import pprint

import falcon
import json
import logging


from falcon.routing import compile_uri_template

from falsy.loader.func import load

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class SpecLoader:
    def __init__(self, log=None):
        self.specs = {}
        self.log = log

    def load_specs(self, swagger_spec):
        self.log.info("load swagger specs")
        try:
            swagger_spec = json.loads(swagger_spec) if type(swagger_spec) == str else swagger_spec
        except:
            self.log.error_trace("Unable to parse the Swagger spec JSON document.")
            raise Exception("Unable to parse the Swagger spec JSON document.")
        try:
            self.specs['basePath'] = swagger_spec.get('basePath')
            self.specs['consumes'] = swagger_spec.get('consumes')
            self.specs['produces'] = swagger_spec.get('produces')
            self.specs['beforeId'] = self.load_handler(swagger_spec.get('beforeId'))
            self.specs['afterId'] = self.load_handler(swagger_spec.get('afterId'))
            self.specs['exceptionId'] = self.load_handler(swagger_spec.get('exceptionId'))
            self.specs['finalId'] = self.load_handler(swagger_spec.get('finalId'))
            for path, path_content in swagger_spec['paths'].items():
                self.load_paths(path, path_content, swagger_spec)
        except:
            raise Exception("Unable to build routing table from provided Swagger spec.")
        # pprint.pprint(self.specs)
        return self.specs

    def load_paths(self, path, path_content, swagger_spec):
        for method, method_content in path_content.items():
            self.load_methods(method, method_content, path, swagger_spec)

    def load_methods(self, method, method_content, path, swagger_spec):
        uri_fields, uri_regex = compile_uri_template(
            '/' + method.lower() + swagger_spec['basePath'] + path)
        self.specs[uri_regex] = {'uri_fields': uri_fields}
        for attribute, attribute_content in method_content.items():
            if attribute in ['beforeId', 'afterId', 'operationId', 'validationId', 'exceptionId', 'finalId']:
                attribute_content = self.load_handler(attribute_content)
            self.load_attributes(attribute, attribute_content, swagger_spec, uri_regex)
            self.specs[uri_regex]['path'] = path

    def load_attributes(self, attribute, attribute_content, swagger_spec, uri_regex):
        self.specs[uri_regex][attribute] = attribute_content
        if attribute == 'parameters':
            for i, param in enumerate(attribute_content):
                if param.get('in') == 'body':
                    schema = param.get('schema')
                    ref = schema.get('$ref')
                    if ref:
                        self.specs[uri_regex]['schema'] = swagger_spec['definitions'][
                            ref[ref.rfind('/') + 1:]]
                    else:
                        self.specs[uri_regex]['schema'] = schema

                self.specs[uri_regex][attribute][i]['validationId'] = self.load_handler(param.get('validationId'))

    def load_handler(self, name):
        if name is None:
            return None
        return load(name)
