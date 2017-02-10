from marshmallow import Schema


class Meta(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def bind(self, name, func):
        setattr(self.__class__, name, func)


def args2schema(args, raise_error=False):
    class SchemaMeta(object):
        strict = raise_error

    attrs = dict(args, Meta=SchemaMeta)
    cls = type(str(''), (Schema,), attrs)
    return cls()
