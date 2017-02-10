from webargs import fields
from webargs.falconparser import parser, HTTPError
from falsy.jlog.jlog import JLog

log = JLog().bind()

hello_args = {
    'name': fields.Str(validate=lambda p: len(p) >= 6)#, location='query')
}


def before_get_it(req, resp, name):
    log = JLog().bind()
    try:
        parsed_args = parser.parse(hello_args, req=req)
    except HTTPError as e:
        log.error_trace(str(e.errors))
        raise Exception(e.errors)


def get_it(name):
    log.debug('get it')
    return {
        'get': name
    }


