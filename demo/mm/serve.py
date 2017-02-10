from falsy.falsy import FALSY

f = FALSY(static_dir='demo/mm/static')
f.swagger('demo/mm/spec.yml', ui=True, ui_language='zh-cn', theme='impress')
api = f.api
