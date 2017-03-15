import json
import os
import falcon
import yaml
from falsy.jlog.jlog import JLog
from falsy.loader.yaml import Loader
from falsy.swagger_proxy.middleware import SwaggerUIStaticMiddleware, CommonStaticMiddleware, CommonWSGIMiddleware
from falsy.swagger_proxy.swagger_server import SwaggerServer
from falsy.termcc.termcc import lgreen, bold, reset, italic, cc, red, rgreen, rlgreen, reverse, rreverse, rred


class FALSY:
    def __init__(self, falcon_api=None,
                 static_path='static', static_dir='static', log_config=None):
        if log_config is None:
            self.log = JLog().setup().bind()
        else:
            self.log = JLog().setup(config=log_config).bind()
        self.log.info(cc('falsy init', fore=77, styles=['italic', 'underlined', 'reverse']))

        self.api = self.falcon_api = falcon_api or falcon.API()
        self.static_path = static_path.strip('/')
        self.static_dir = static_dir if os.path.isdir(static_dir) else '.'

        self.api = CommonStaticMiddleware(self.falcon_api, static_dir=self.static_dir,
                                          url_prefix=self.static_path)
        self.log.info('common static middleware loaded\n\t{}'.format(
            'url_prefix(static_path):' + reverse() + self.static_path + rreverse() +
            ', static_dir:' + reverse() + self.static_dir + rreverse()))

    def wsgi(self, app, url_prefix='/wsgi'):
        self.api = CommonWSGIMiddleware(self.api, app, url_prefix=url_prefix)
        self.log.info('common wsgi middleware loaded\n\t{}'.format('url_prefix:' + self.static_path))
        return self

    def swagger(self, filename, ui=True, new_file=None, ui_language='en', theme='normal', errors=None, cors_origin=None, api_url=None):
        server = SwaggerServer(errors=errors, cors_origin=cors_origin)
        self.log.info('swagger server init')

        swagger_file = filename.replace('/', '_')
        if swagger_file.endswith('yml') or swagger_file.endswith('yaml'):
            new_file = new_file or swagger_file
            new_file = new_file.replace('.yaml', '.json')
            new_file = new_file.replace('.yml', '.json')
            new_path = self.static_dir + '/' + new_file
            with open(filename, 'r') as f:
                config = yaml.load(f, Loader)
                server.load_specs(config)
                with open(new_path, 'w') as fw:
                    config = self.remove_error_info(config)
                    json.dump(config, fw, sort_keys=True, indent=4)
            self.log.info('swagger file generated(from yaml file)\n\t{}'.format(
                'new_path:' + reverse() + new_path + rreverse()))
        else:
            new_file = new_file or swagger_file
            new_path = self.static_dir + '/' + new_file
            with open(filename, 'r') as fr:
                config = fr.read()
                server.load_specs(config)
                with open(new_path, 'w') as fw:
                    config = json.loads(self.remove_error_info(config))
                    json.dump(config, fw, sort_keys=True, indent=4)
            self.log.info('swagger file generated(from json file)\n\t{}'.format(
                'new_path:' + reverse() + new_path + rreverse()))
        path = server.basePath
        path = path.lstrip('/') if path else 'v0'
        self.falcon_api.add_sink(server, '/' + path)
        self.log.info('swagger server sinked\n\t{}'.format('path:' + reverse() + path + rreverse()))
        if ui:
            self.api = SwaggerUIStaticMiddleware(self.api, swagger_file=self.static_path + '/' + new_file,
                                                 url_prefix=path, language=ui_language, theme=theme, api_url=api_url)
            self.log.info('swagger ui static middleware loaded\n\t{}'.format(
                'url_prefix(static_path):' + reverse() + self.static_path) + rreverse())
        return self

    # deprecated
    def begin_api(self, api_prefix=None, errors=None):
        pass

    # deprecated
    def end_api(self):
        pass

    def remove_error_info(self, d):
        if not isinstance(d, (dict, list)):
            return d
        if isinstance(d, list):
            return [self.remove_error_info(v) for v in d]
        return {k: self.remove_error_info(v) for k, v in d.items()
                if k not in {'validationId', 'beforeId', 'afterId', 'exceptionId', 'operationId', 'finalId', 'operationMode'}}
