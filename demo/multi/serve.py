from falsy.falsy import FALSY

f = FALSY(static_path='test', static_dir='demo/multi/static')
f.swagger('demo/multi/spec1.yml', ui=True, ui_language='zh-cn', theme='normal')
f.swagger('demo/multi/spec2.yml', ui=True, ui_language='zh-cn', theme='normal')
api = f.api
