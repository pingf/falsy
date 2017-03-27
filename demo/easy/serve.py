from falsy.falsy import FALSY

f = FALSY(static_path='test', static_dir='demo/easy/static',log_config={'highlights':['falsy']})
f.swagger('demo/easy/spec.yml', ui=True, ui_language='zh-cn', theme='impress')
api = f.api
