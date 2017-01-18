from falsy.falsy import FALSY

f = FALSY(static_path='test', static_dir='demo/cookie/static')
f.swagger('demo/cookie/spec.yml', ui=True, ui_language='zh-cn', theme='normal')
api = f.api
