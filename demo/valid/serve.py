from falsy.falsy import FALSY

f = FALSY(static_path='test', static_dir='demo/valid/static')
f.swagger('demo/valid/spec.yml', ui=True, ui_language='zh-cn', theme='material')
api = f.api
