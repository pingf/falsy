import functools
import importlib

func_map = {}


def load(function_name):
    if not function_name:
        return None

    if function_name in func_map.keys():
        return func_map[function_name]

    module_name, attr_path = function_name.rsplit('.', 1)
    module = None
    last_import_error = None

    while not module:

        try:
            module = importlib.import_module(module_name)
        except ImportError as import_error:
            last_import_error = import_error
            if '.' in module_name:
                module_name, attr_path1 = module_name.rsplit('.', 1)
                attr_path = '{0}.{1}'.format(attr_path1, attr_path)
            else:
                raise
    try:
        function = deep_getattr(module, attr_path)
    except AttributeError:
        if last_import_error:
            raise last_import_error
        else:
            raise
    func_map[str(function_name)] = function
    return function


def deep_getattr(obj, attr):
    return functools.reduce(getattr, attr.split('.'), obj)
