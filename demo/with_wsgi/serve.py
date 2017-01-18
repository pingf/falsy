
from demo.with_wsgi.ops.flask import flask_app, PRE_FLASK
from demo.with_wsgi.ops.tornado import tornado_app, PRE_TORNADO
from falsy.falsy import FALSY



f = FALSY(static_path='test', static_dir='demo/with_wsgi/static')\
    .swagger('demo/with_wsgi/spec.yml', ui=True, ui_language='zh-cn', theme='normal')\
    .wsgi(flask_app, PRE_FLASK) \
    .wsgi(tornado_app, PRE_TORNADO)
api = f.api
