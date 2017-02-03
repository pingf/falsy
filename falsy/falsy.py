import json
import os
import falcon
import yaml
from falsy.jlog.jlog import JLog
from falsy.loader.yaml import Loader
from falsy.swagger_proxy.middleware import SwaggerUIStaticMiddleware, CommonStaticMiddleware, CommonWSGIMiddleware
from falsy.swagger_proxy.swagger_server import SwaggerServer
from falsy.termcc.termcc import lgreen, bold, reset, wrap, italic


class FALSY:
    def __init__(self, falcon_api=None,
                 static_path='static', static_dir='static', high_log=None):
        self.log = JLog(hightable=high_log).setup()
        self.log.info(wrap(bold())+'falsy init')

        self.api = self.falcon_api = falcon_api or falcon.API()
        self.static_path = static_path.strip('/')
        self.static_dir = static_dir if os.path.isdir(static_dir) else '.'

        self.api = CommonStaticMiddleware(self.falcon_api, static_dir=self.static_dir,
                                          url_prefix=self.static_path, log=self.log)
        self.log.info('common static middleware loaded\n\t\t\turl_prefix(static_path):%s, static_dir:%s'%(self.static_path, self.static_dir))

    def wsgi(self, app, url_prefix='/wsgi'):
        self.api = CommonWSGIMiddleware(self.api, app, url_prefix=url_prefix, log=self.log)
        self.log.info('common wsgi middleware loaded\n\t\t\turl_prefix:%s'%(self.static_path))
        return self


    def swagger(self, filename, ui=False, new_file=None, ui_language='en', theme='normal', errors=None):
        server = SwaggerServer(errors=errors, log=self.log)
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
            self.log.info('swagger file generated(from yaml file)\n\t\t\tnew_path:%s'%(new_path))
        else:
            new_file = new_file or swagger_file
            new_path = self.static_dir + '/' + new_file
            with open(filename, 'r') as fr:
                config = fr.read()
                server.load_specs(config)
                with open(new_path, 'w') as fw:
                    config = self.remove_error_info(config)
                    json.dump(config, fw, sort_keys=True, indent=4)
            self.log.info('swagger file generated(from json file)\n\t\t\tnew_path:%s'%(new_path))
        path = server.basePath
        path = path.lstrip('/') if path else 'v0'
        self.falcon_api.add_sink(server, '/'+path)
        self.log.info('swagger server sinked\n\t\t\t%s'%(wrap(lgreen())+'path:'+path+wrap(reset())))
        if ui:
            self.api = SwaggerUIStaticMiddleware(self.api, swagger_file=self.static_path + '/' + new_file,
                                                 url_prefix=path, language=ui_language, theme=theme)
            self.log.info('swagger ui static middleware loaded\n\t\t\turl_prefix(static_path):%s'%(self.static_path))
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
