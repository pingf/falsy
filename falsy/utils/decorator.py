import time
from contextlib import ContextDecorator

from falsy.jlog.jlog import JLog
from falsy.loader import func


class suppress_exceptions(ContextDecorator):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __enter__(self):
        return self

    def __exit__(self, e_type, e_value, e_trace):
        on_error = self.__dict__.get('on_error')
        if on_error:
            propagate = func.load(on_error)(e_type, e_value, e_trace)
            if propagate in [True, False]:
                return propagate

        for supp in self.__dict__.get('suppress_list', []):
            if isinstance(e_value, supp):
                return True
        return False


class log_runtime(ContextDecorator):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.log = JLog().bind()

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, typ, val, traceback):
        # Note: typ, val and traceback will only be not None
        # If an exception occured
        self.log.info("{}: {}".format(self.__dict__.get('label', 'default'), time.time() - self.start_time))
        return False
