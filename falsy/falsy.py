import json
import os
# import pprint

import falcon
# import shutil

import yaml
from falsy.jlog.jlog import JLog
from falsy.loader.yaml import Loader
from falsy.swagger_proxy.middleware import SwaggerUIStaticMiddleware, CommonStaticMiddleware, CommonWSGIMiddleware
from falsy.swagger_proxy.swagger_server import SwaggerServer


class FALSY:
    def __init__(self, falcon_api=None,
                 static_path='static', static_dir='static'):
        self.log = JLog(hightable=['swagger']).setup()
        self.log.info('swagger')

        self.api = self.falcon_api = falcon_api or falcon.API()
        self.static_path = static_path.strip('/')
        self.static_dir = static_dir if os.path.isdir(static_dir) else '.'

        self.api = CommonStaticMiddleware(self.falcon_api, static_dir=self.static_dir,
                                          url_prefix=self.static_path, log=self.log)

    def wsgi(self, app, url_prefix='/wsgi'):
        self.api = CommonWSGIMiddleware(self.api, app, url_prefix=url_prefix, log=self.log)
        return self


    def swagger(self, filename, ui=False, new_file=None, ui_language='en', theme='normal', errors=None):
        server = SwaggerServer(errors=errors, log=self.log)

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
        else:
            new_file = new_file or swagger_file
            new_path = self.static_dir + '/' + new_file
            with open(filename, 'r') as fr:
                config = fr.read()
                server.load_specs(config)
                with open(new_path, 'w') as fw:
                    config = self.remove_error_info(config)
                    json.dump(config, fw, sort_keys=True, indent=4)
        path = server.basePath
        path = path.lstrip('/') if path else 'v0'
        self.falcon_api.add_sink(server, '/'+path)
        if ui:
            self.api = SwaggerUIStaticMiddleware(self.api, swagger_file=self.static_path + '/' + new_file,
                                                 url_prefix=path, language=ui_language, theme=theme)
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
                if k not in {'validationId', 'beforeId', 'afterId', 'exceptionId', 'operationId', 'operationMode'}}
