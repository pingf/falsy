import json

from falsy.falsy import FALSY


class CustomException(Exception):
    pass


def handle_custom(req, resp, e):
    resp.body = json.dumps({'error': 'custom error catched'})
    resp.content_type = 'application/json'


f = FALSY(static_path='test', static_dir='demo/catch/static')
f.begin_api(errors= {CustomException: handle_custom})
f.swagger('demo/catch/spec.yml', ui=True, theme='responsive')
f.end_api()
api = f.api
