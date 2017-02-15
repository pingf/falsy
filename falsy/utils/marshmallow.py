import functools

from marshmallow import Schema


def argmap2schema(argmap):
    class Meta(object):
        strict = True

    attrs = dict(argmap, Meta=Meta)
    CLS = type(str(''), (Schema,), attrs)
    return CLS()


class MMException(Exception):
    pass


def validate(argmap):
    schema = argmap2schema(argmap)

    def decorator(func):
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            e = schema.validate(kwargs)
            if e:
                raise MMException(str(e))
            return func(*args, **kwargs)

        return decorated

    return decorator


def mm_check(routes, req, **kwargs):
    sig = req.spec['route_signature']
    args = routes.get(sig)
    schema = argmap2schema(args)
    e = schema.validate(kwargs)
    if e:
        raise MMException(str(e))
