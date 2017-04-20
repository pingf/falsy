import logging
import mimetypes
import os

import falcon
from jinja2 import Template

from falsy.jlog.jlog import JLog

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class CommonWSGIMiddleware(object):
    def __init__(self, falcon_api, app, url_prefix='wsgi'):
        self.falcon_api = falcon_api
        self.app = app
        self.url_prefix = url_prefix.lstrip('/')
        self.log = JLog().bind()

    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']
        if path_info and path_info.startswith('/' + self.url_prefix):
            return self.app(environ, start_response)
        return self.falcon_api(environ, start_response)


class CommonStaticMiddleware(object):
    def __init__(self, app, static_dir='dist', url_prefix='static'):
        self.app = app
        self.static_dir = static_dir
        self.url_prefix = url_prefix.lstrip('/')
        self.path_dir = os.path.abspath(static_dir)
        self.log = JLog().bind()

    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']
        resource_path = self.resolve_resouce(path_info, self.url_prefix)
        if path_info and path_info.startswith('/' + self.url_prefix):

            path = os.path.abspath(
                os.path.join(
                    self.path_dir,
                    resource_path
                )
            )
            if not os.path.exists(path):
                status = '404 FAIL'
                headers = [('Content-type', 'text/plain')]
                start_response(status, headers)
                info = '404 not found: ' + path_info
                return [info.encode('utf-8')]
            filetype = mimetypes.guess_type(path, strict=True)[0]
            if not filetype:
                filetype = 'text/plain'
            resp = []
            resp.append(('Access-Control-Allow-Origin', '*'))
            resp.append(('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS'))
            resp.append(('Access-Control-Allow-Headers',
                         'Authorization, X-Auth-Token, Keep-Alive, Users-Agent, X-Requested-With, If-Modified-Since, Cache-Control, Content-Type'))
            resp.append(('Access-Control-Allow-Credentials', 'true'))
            resp.append(('Access-Control-Max-Age', '1728000'))
            resp.append(('Content-type', filetype))
            start_response("200 OK", resp)

            return environ['wsgi.file_wrapper'](open(path, 'rb'), 409600)
        return self.app(environ, start_response)

    def resolve_resouce(self, uri, prefix):
        if uri in ['/' + prefix + '/', '/' + prefix]:
            return 'index.html'
        if uri.startswith('/' + prefix + '/'):
            id = len('/' + prefix + '/')
        else:
            id = 0
        return uri[id:].lstrip('/')


class SwaggerUIStaticMiddleware(object):
    def __init__(self, app, swagger_file='swagger.json', url_prefix='v1', language='en', theme='normal', api_url=None):
        self.app = app
        if theme == 'material' or theme == 'angular':
            self.static_dir = 'vendors/dist_material'
        elif theme == 'responsive' or theme == 'impress':
            self.static_dir = 'vendors/dist_impress'
        elif theme == 'normal' or theme == 'swagger':
            self.static_dir = 'vendors/dist_normal'
        elif theme == 'bootstrap':
            self.static_dir = 'vendors/dist_bootstrap'
        else:
            self.static_dir = 'vendors/dist_impress'
        self.url_prefix = url_prefix.lstrip('/')
        self.path_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                self.static_dir,
            )
        )
        self.swagger_file = swagger_file.strip('/')
        self.language = language
        if type(api_url) == str:
            self.api_url = api_url.rstrip('/') if api_url.endswith('/') else api_url
        else:
            self.api_url = None

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO')
        if path_info and path_info.startswith('/' + self.url_prefix + '/ui/'):
            resource_path = self.resolve_resouce(path_info, self.url_prefix)
            path = os.path.abspath(
                os.path.join(
                    self.path_dir,
                    resource_path
                )
            )
            if not os.path.exists(path):
                headers = [('Content-type', 'text/plain')]
                start_response('404 FAIL', headers)
                info = '404 not found: ' + path_info
                return [info.encode('utf-8')]
            if resource_path == 'index.html':
                with open(path, 'r') as f:
                    content = f.read()
                    template = Template(content)
                    if self.api_url:
                        rendered = template.render({'api_url': self.api_url + '/' + self.swagger_file,
                                                    'language': self.language})
                    else:
                        rendered = template.render({'api_url': environ['wsgi.url_scheme'] + '://' + environ[
                            'SERVER_NAME'] + ':' + environ['SERVER_PORT'] + '/' + self.swagger_file,
                                                    'language': self.language})
                resp = [('Content-type', 'text/html')]
                start_response("200 OK", resp)
                return [rendered.encode('utf-8')]

            filetype = mimetypes.guess_type(path, strict=True)[0]
            if not filetype:
                filetype = 'text/plain'
            resp = [('Content-type', filetype)]
            start_response("200 OK", resp)
            return environ['wsgi.file_wrapper'](open(path, 'rb'), 409600)
        return self.app(environ, start_response)

    def resolve_resouce(self, uri, prefix):
        if uri in ['/' + prefix + '/ui', '/' + prefix + '/ui/']:
            return 'index.html'
        if uri.startswith('/' + prefix + '/ui/'):
            id = len('/' + prefix + '/ui/')
        elif uri.startswith('/' + prefix + '/'):
            id = len('/' + prefix + '/')
        else:
            id = 0
        return uri[id:].lstrip('/')
