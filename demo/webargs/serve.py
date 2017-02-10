from falsy.falsy import FALSY

f = FALSY(static_dir='demo/webargs/static',high_log=['init'])
f.swagger('demo/webargs/spec.yml', ui=True, ui_language='zh-cn', theme='impress')
api = f.api
