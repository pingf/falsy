from falsy.jlog.jlog import JLog

log = JLog().bind()


def get_it():
    log.debug('get it')
    return {
        'hello': 'jesse'
    }
