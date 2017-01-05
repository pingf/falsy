import json
import os
import pprint

import falcon
import shutil

import yaml
from falsy.loader.yaml import Loader
from falsy.swagger_proxy.middleware import SwaggerUIStaticMiddleware, CommonStaticMiddleware
from falsy.swagger_proxy.swagger_server import SwaggerServer


class FALSY:
    def __init__(self, falcon_api=None,
                 static_path='static', static_dir=None):
        self.api = self.falcon_api = falcon_api or falcon.API()
        self.static_path = static_path.strip('/')
        self.server = None
        self.api_prefix = r'/'
        if static_dir:
            self.static_dir = static_dir if os.path.isdir(static_dir) else '.'
            self.api = CommonStaticMiddleware(self.api, static_dir=self.static_dir,
                                              url_prefix=self.static_path)

    def begin_api(self, api_prefix=None, errors=None):
        self.api_prefix = api_prefix or self.api_prefix
        self.server = SwaggerServer(errors=errors)

    def swagger(self, filename, ui=False, new_file=None, ui_language='en', theme='normal'):
        swagger_file = filename.split('/')[-1] if filename.find('/') > 0 else filename
        if swagger_file.endswith('yml') or swagger_file.endswith('yaml'):
            new_file = new_file or swagger_file
            new_file = new_file.replace('.yaml', '.json')
            new_file = new_file.replace('.yml', '.json')
            new_path = self.static_dir + '/' + new_file
            with open(filename, 'r') as f:
                config = yaml.load(f, Loader)
                self.server.load_specs(config)
                with open(new_path, 'w') as fw:
                    config = self.remove_error_info(config)
                    json.dump(config, fw, sort_keys=True, indent=4)
        else:
            new_file = new_file or swagger_file
            new_path = self.static_dir + '/' + new_file
            with open(filename, 'r') as fr:
                config = fr.read()
                self.server.load_specs(config)
                with open(new_path, 'w') as fw:
                    config = self.remove_error_info(config)
                    json.dump(config, fw, sort_keys=True, indent=4)
        if ui:
            path = self.server.basePath
            if path:
                path=path.lstrip('/')
            else:
                path='v0'
            self.api = SwaggerUIStaticMiddleware(self.api, swagger_file=self.static_path + '/' + new_file,
                                                 url_prefix=path, language = ui_language, theme=theme)

    def end_api(self):
        self.falcon_api.add_sink(self.server, self.api_prefix)



    def remove_error_info(self, d):
        if not isinstance(d, (dict, list)):
            return d
        if isinstance(d, list):
            return [self.remove_error_info(v) for v in d]
        return {k: self.remove_error_info(v) for k, v in d.items()
                if k not in {'validationId', 'beforeId', 'afterId'}}
