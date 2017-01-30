import logging

import sys
import traceback

from falsy.termcc.termcc import blue, yellow, cyan, red, bold, magenta, red_, green


class TraceFilter(logging.Filter):
    def filter(self, record):
        if 'trace' not in dir(record):
            record.trace = ''
        else:
            record.trace = '\n\t\t' + record.trace
        return True


class HighlightFilter(logging.Filter):
    def __init__(self, hightable=None):
        self.table = hightable

    def filter(self, record):
        record.high = ''
        if self.table is None:
            return True
        for e in self.table:
            if e in record.msg:
                record.high = '\n\t\t'+magenta('highlight')+': ' +record.msg.replace(e, red_(yellow(e)))
        return True


class JLog:
    def __init__(self, hightable=None):
        self.hightable = hightable
        self.config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s.%(msecs)03d %(levelname)-8s %(name)-8s %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S %Z%z'
                },
                'colored': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': '%(yellow)s%(asctime)s.%(msecs)03d%(reset)s %(cyan)s%(name)-8s%(reset)s '
                              '%(log_color)s%(message)s%(reset)s%(trace)s%(high)s',
                    'datefmt': '%m%d %H:%M:%S',
                    'log_colors': {
                        'DEBUG': 'blue',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'bold_red',
                    }
                },

            },
            'filters': {
                'trace_filter': {
                    '()': TraceFilter,
                },
                'highlight_filter': {
                    '()': HighlightFilter,
                    'hightable': self.hightable
                }
            },
            'handlers': {
                'rotate_file': {
                    'level': 'INFO',
                    'filters': None,
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'filename': 'falsy.log',
                    'formatter': 'standard'
                },
                'console': {
                    'level': 'DEBUG',
                    'filters': ['trace_filter', 'highlight_filter'],
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                    'formatter': 'colored'
                },
            },
            'loggers': {
                'falsy': {
                    'handlers': ['rotate_file', 'console'],
                    'level': 'DEBUG',
                    'propagate': False,
                },
            }
        }

    def setup(self):
        logging.config.dictConfig(self.config)
        self.logger = logging.getLogger('falsy')
        return self

    def get_falsy(self):
        return self.logger

    def debug(self, msg, *args, **kwargs):
        return self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        return self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        return self.logger.critical(msg, *args, **kwargs)

    def warning_trace(self, msg, *args, **kwargs):
        self.trace(kwargs)
        return self.logger.critical(msg, *args, **kwargs)

    def critical_trace(self, msg, *args, **kwargs):
        self.trace(kwargs)
        return self.logger.critical(msg, *args, **kwargs)

    def error_trace(self, msg, *args, **kwargs):
        self.trace(kwargs)
        return self.logger.error(msg, *args, **kwargs)

    def trace(self, kwargs):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        stack = traceback.extract_tb(exc_traceback)
        lines = []
        for i, s in enumerate(stack):
            filename = s.filename
            l = len(filename)
            shortfile = kwargs.get('shortfile', 40)
            if l > shortfile:
                filename = filename[filename.find('/', l - shortfile):]
            line = '%-40s:%-4s %s' % (
                blue(filename), yellow(str(s.lineno)), '|' + '-' * (i * 4) + cyan(s.name) + ':' + red(s.line))
            lines.append(line)
        lines = '\n\t\t'.join(lines)
        kwargs['extra'] = {'trace': magenta(str(exc_type)) + ' ' + bold(magenta(str(exc_value))) + '\n\t\t' + lines}

    def remap(self, tp, arg):
        if self.hightable:
            m = self.hightable.get(tp)
            if m:
                return m.get(arg, arg)
        return arg
