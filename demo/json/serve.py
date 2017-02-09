from falsy.falsy import FALSY

f = FALSY(static_path='test', static_dir='demo/json/static')
f.swagger('demo/json/spec.json', ui=True, ui_language='zh-cn', theme='impress')
api = f.api
