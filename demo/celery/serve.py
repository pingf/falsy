from falsy.falsy import FALSY

f = FALSY(static_path='test', static_dir='demo/celery/static',log_config={'highlights':['falsy']})
f.swagger('demo/celery/spec.yml', ui=True, ui_language='zh-cn', theme='impress', cors_origin='*')
api = f.api
