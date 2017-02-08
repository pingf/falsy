import logging
import traceback

import sys
from falsy.jlog import LOG_CONFIG
from falsy.jlog.jlog import JLog

# logging.config.dictConfig(LOG_CONFIG)
from falsy.termcc.termcc import blue, yellow, red, cyan, bold


# def print_format_table():
#     """
#     prints table of formatted text format options
#     """
#     for style in range(8):
#         for fg in range(30, 38):
#             s1 = ''
#             for bg in range(40, 48):
#                 format = ';'.join([str(style), str(fg), str(bg)])
#                 s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
#             print(s1)
#         print('\n')


def test():
    raise Exception('haha')

def test1():
    test()
    # raise Exception('haha')

if __name__ == '__main__':
    log = JLog().setup().bind()
    log.debug('hehe')
    log.info('hehe')
    log.error('noshow')
    log.critical('hehe')
    try:
        test1()
    except Exception as e:
        log.error_trace('error trace')
        log.critical_trace('critical trace')
