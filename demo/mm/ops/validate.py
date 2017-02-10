from marshmallow import fields

from falsy.utils.meta import args2schema

route_args = {
    '/get/v1/hello': {
        'name': fields.Str(validate=lambda p: len(p) >= 6, required=True),
    },
    '/post/v1/hello': {
        'name': fields.Str(validate=lambda p: len(p) >= 4)
    }
}


def mmcheck(req, resp, **kwargs):
    sig = req.spec['route_signature']
    args = route_args.get(sig)
    schema = args2schema(args, raise_error=False)
    data, errors = schema.load(kwargs)
    if errors:
        raise Exception(errors)
