import logging

from falsy.jlog import LOG_CONFIG

logging.config.dictConfig(LOG_CONFIG)
if __name__ == '__main__':
    log = logging.getLogger('falsy')
    log.info('haha')
    log.debug('haha')
