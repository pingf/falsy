from falsy.falsy import FALSY

f = FALSY(static_path='test', static_dir='demo/int0/static')
f.begin_api()
f.swagger('demo/int0/spec.yml', ui=True, ui_language='zh-cn', theme='responsive')
f.end_api()
api = f.api
