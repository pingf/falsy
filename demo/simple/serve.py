from falsy.falsy import FALSY

f = FALSY(static_path='test', static_dir='demo/simple/static',high_log=[])
f.swagger('demo/simple/spec.yml', ui=True, ui_language='zh-cn', theme='material')
api = f.api
