from falsy.falsy import FALSY

f = FALSY(static_dir='demo/mm2/static')
f.swagger('demo/mm2/spec.yml', ui=True, ui_language='zh-cn', theme='impress')
api = f.api
