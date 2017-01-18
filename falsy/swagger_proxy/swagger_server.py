import pprint

import falcon
import json
import logging

from falsy.dynamic_import import get_function_from_name
from falsy.swagger_proxy.operator_loader import OperatorLoader
from falsy.swagger_proxy.spec_loader import SpecLoader

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class SwaggerServer:
    def __init__(self, errors=None):
        self.default_content_type = 'application/json'
        self.specs = {}  # Meta()
        self.custom_error_map = errors

    def __call__(self, req, resp, **kwargs):
        # log.info(dir(req))
        log.info(req.remote_addr)
        self.req = req
        self.resp = resp
        self.process()

    def load_specs(self, swagger_spec):
        self.specs = SpecLoader().load_specs(swagger_spec)
        self.basePath = self.specs['basePath']

    def process(self):
        if self.process_preflight_request(): return  # it would be good if we could just force a response return
        try:
            self.dispatch()
        except Exception as e:
            error_type = type(e)
            error_map = {
                falcon.errors.HTTPNotFound: lambda req, resp, e: self.http_not_found_handler(e),
                falcon.errors.HTTPMissingParam: lambda req, resp, e: self.http_missing_param_handler(e),
                falcon.errors.HTTPInvalidParam: lambda req, resp, e: self.http_invalid_param_handler(e),
            }
            if self.custom_error_map:
                error_map.update(self.custom_error_map)

            error_func = error_map.get(error_type)
            if error_func:
                error_func(self.req, self.resp, e)
            else:
                self.default_error_handler(e)

    def default_error_handler(self, e):
        self.resp.body = json.dumps({'error': str(e)})
        self.resp.status = falcon.HTTP_500
        self.resp.content_type = 'application/json'

    def http_not_found_handler(self, e):
        self.resp.body = e.title
        self.resp.status = e.status
        self.resp.content_type = 'application/json'

    def http_missing_param_handler(self, e):
        self.resp.body = json.dumps({'error': e.title + ':' + ' '.join([p for p in e.args])})
        self.resp.status = e.status
        self.resp.content_type = 'application/json'

    def http_invalid_param_handler(self, e):
        self.resp.body = json.dumps({'error': e.title + ':' + ' '.join([p for p in e.args])})
        self.resp.status = e.status
        self.resp.content_type = 'application/json'

    def process_preflight_request(self):
        if self.req.method == 'OPTIONS':
            log.info("Got an OPTIONS request: ".format(self.req.relative_uri))
            self.resp.set_header('Access-Control-Allow-Origin', '*')
            self.resp.set_header('Access-Control-Allow-Credentials', 'true')
            self.resp.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
            self.resp.set_header('Access-Control-Allow-Headers',
                                 'Authorization, X-Auth-Token, Keep-Alive, Users-Agent, X-Requested-With, If-Modified-Since, Cache-Control, Content-Type')
            self.resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days

            response_body = '\n'

            response_body += 'All Swagger operations:\n\n'
            response_body += 'nothing here\n\n'

            self.resp.body = response_body
            self.resp.status = falcon.HTTP_200
            return True

    def dispatch(self):
        op_loader = OperatorLoader()
        base_before, base_after, base_excp = op_loader.load_base(self.specs)
        try:
            if base_before:
                base_before(req=self.req, resp=self.resp)
            for uri_regex, spec in self.specs.items():
                try:
                    route_signature = '/' + self.req.method.lower() + self.req.relative_uri
                    if route_signature.find('?') > 0:
                        route_signature = route_signature[:route_signature.find('?')]
                    if type(uri_regex) == str:
                        continue
                    match = uri_regex.match(route_signature)
                    if match:
                        handler, params, before, after, excp, mode = op_loader.load(req=self.req, spec=spec,
                                                                                    matched_uri=match)
                        handler_return = None
                        try:
                            if before:
                                before(req=self.req, resp=self.resp, **params)
                            if mode == 'raw':
                                handler_return = handler(req=self.req, resp=self.resp)
                            elif mode == 'more':
                                handler_return = handler(req=self.req, resp=self.resp, **params)
                            else:
                                handler_return = handler(**params)
                            self.process_response(handler_return, mode)
                            if after:
                                after(req=self.req, resp=self.resp, response=handler_return, **params)
                        except Exception as e:
                            if excp is None:
                                raise e
                            if excp is not None:
                                excp(req=self.req, resp=self.resp, error=e)
                        return
                except AttributeError as e:
                    print(e, 'catched')
            if base_after:
                base_after(req=self.req, resp=self.resp)
        except Exception as e:
            if base_excp is None:
                raise e
            if base_excp is not None:
                base_excp(req=self.req, resp=self.resp, error=e)
        log.info("Request URL does not match any route signature: {}".format(route_signature))
        raise falcon.HTTPNotFound()

    def process_response(self, handler_return, mode='normal'):
        if mode == 'raw':
            return
        content_type = 'text/plain'
        if handler_return is None:
            # when exceptions happend
            content_type = 'application/json'
            http_code = falcon.HTTP_500
        if type(handler_return) == tuple:
            data = handler_return[0]
            http_code = handler_return[1]
            if len(handler_return) > 2:
                content_type = handler_return[2]
            else:
                if type(data) == dict or type(data) == list:
                    content_type = 'application/json'
                # else:
                #     content_type = 'text/plain'
        else:
            data = handler_return
            http_code = falcon.HTTP_200
            if type(data) == dict or type(data) == list:
                content_type = 'application/json'
            # else:
            #     content_type = 'text/plain'
        if self.resp.body:
            try:
                pre_body = json.loads(self.resp.body)
            except Exception as e:
                pre_body = self.resp.body
            if type(pre_body) == dict:
                if 'json' in content_type:
                    pre_body.update(data)
                    self.resp.body = json.dumps(pre_body)
                else:
                    self.resp.body = json.dumps(pre_body) + data
            else:
                self.resp.body = pre_body + json.dumps(data) if 'json' in content_type else json.dumps(pre_body) + data
        else:
            self.resp.body = json.dumps(data) if 'json' in content_type else data
        self.resp.content_type = content_type
        self.resp.status = http_code
