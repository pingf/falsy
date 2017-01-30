import logging
import traceback

import sys
from falsy.jlog import LOG_CONFIG
from falsy.jlog.jlog import JLog

# logging.config.dictConfig(LOG_CONFIG)
from falsy.termcc.termcc import blue, yellow, red, cyan, bold


def print_format_table():
    """
    prints table of formatted text format options
    """
    for style in range(8):
        for fg in range(30, 38):
            s1 = ''
            for bg in range(40, 48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
            print(s1)
        print('\n')


def test():
    raise Exception('haha')

def test1():
    test()
    # raise Exception('haha')

if __name__ == '__main__':
    # log = logging.getLogger('falsy')
    log = JLog().setup()
    log.debug('hehe')
    log.info('hehe')
    log.error('noshow')
    log.critical('hehe')
    try:
        test1()
    except Exception as e:
        log.error_trace('error trace')
        log.critical_trace('critical trace')
        # exc_type, exc_value, exc_traceback = sys.exc_info()
        #
        # stack = traceback.extract_stack()
        # stack = traceback.extract_tb(exc_traceback)
        # lines = []
        # for i,s in enumerate(stack):
        #     print(dir(s))
        #     print(s.locals)
        #     filename = s.filename
        #     l = len(filename)
        #     if l > 40:
        #         filename = filename[filename.find('/', l - 40):]
        #     line = '%-40s:%-4s %s'%( blue(filename), yellow(str(s.lineno)), '>>>>'*(i+1)+cyan(s.name)+':'+red(s.line))
        #     lines.append(line)
            # print(s.lineno, s.name, s.line, filename)
        # lines = '\n\t\t'.join(lines)
        # print(lines)
        # a, b, c = sys.exc_info()
        # print(a)
        # print(b)
        # print(dir(c))
        # print(c.tb_frame)
        # print(sys.exec_info())

        # log.critical('info', extra={'detail':'\t\t'.join(stack)})
        # log.critical('info', extra={'detail': lines + '\n\t\t' + bold(red(str(exc_type))) + ' ' + bold(red(str(exc_value)))})
        # log.debug({1:2})


        # print_format_table()
