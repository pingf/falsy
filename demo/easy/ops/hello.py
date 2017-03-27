import falcon
import requests

from falsy.jlog.jlog import JLog

log = JLog().bind()

def get_it(name):
    log.debug('get it')
    return {
        'get': name
    }


