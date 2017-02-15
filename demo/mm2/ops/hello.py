import json

from marshmallow import fields

from falsy.utils.marshmallow import validate



argmap = {
    'name': fields.Str(required=False),
}


@validate(argmap)
def get_it(**kwargs):
    return {
        'get': kwargs.get('name')
    }


def post_it(name):
    return {
        'post': name
    }
