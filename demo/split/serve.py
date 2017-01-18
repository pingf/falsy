from falsy.falsy import FALSY

f = FALSY(static_path='test', static_dir='demo/simple/static')
f.swagger('demo/split/ymls/spec.yml', ui=True, ui_language='zh-cn', theme='responsive')
api = f.api
