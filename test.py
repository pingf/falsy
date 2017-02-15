import functools

from marshmallow import fields
from webargs import argmap2schema

from marshmallow import Schema
class NameSchema(Schema):
    name = fields.Str(required=True)

def argmap2schema(argmap, instance=False, **kwargs):
    class Meta(object):
        strict = True
    attrs = dict(argmap, Meta=Meta)
    # print(attrs, type(attrs))
    cls = type('sch', (Schema,), argmap)
    # cls = type()
    # print('!!!!!!')
    # print(cls.__dict__)
    # print(NameSchema.__dict__)
    return NameSchema
    # return cls if not instance else cls(**kwargs)

def validate(argmap):
    schema = argmap2schema(argmap, instance=True)()
    schema = NameSchema()
    def decorator(func):
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            # print(kwargs)
            schema.validate(kwargs)
            return func(*args, **kwargs)
        return decorated
    return decorator

@validate({
    's': fields.Str(required=True),
})
def add(s):
    print(s)
    return s

# add(s=None)



class Name2Schema(Schema):
    a = fields.Str(required=False)

s = Name2Schema()
e = s.validate({})
print(e)



def aaa(a, b):
    req ={b:,a:None}
