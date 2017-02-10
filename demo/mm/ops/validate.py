from marshmallow import fields

from falsy.utils.meta import args2schema

route_args = {
    '/get/v1/hello': {
        'name': fields.Str(validate=lambda p: len(p) >= 6)
    },
    '/post/v1/hello': {
        'name': fields.Str(validate=lambda p: len(p) >= 4)
    }
}


def mmcheck(req, resp, **kwargs):
    args = route_args.get(req.spec['route_signature'])
    schema = args2schema(args)
    data, errors = schema.load(kwargs)
    if errors:
        raise Exception(errors)
