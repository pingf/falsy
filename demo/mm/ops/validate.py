from marshmallow import fields

from falsy.utils.marshmallow import mm_check

route_args = {
    '/get/v1/hello': {
        'name': fields.Str(required=False),
    },
    '/post/v1/hello': {
        'name': fields.Str(validate=lambda p: len(p) >= 4)
    }
}


def mmcheck(req, resp, **kwargs):
    mm_check(route_args, req, **kwargs)
