import logging
import logging.config

import traceback

import collections

from falsy.jlog.filters import TraceFilter, HighlightFilter
from falsy.jlog.formatters import JLogColoredFormatter
from falsy.termcc.termcc import blue, yellow, cyan, red, bold, magenta
import sys


class JLog:
    def __init__(self, name='falsy'):
        self.logger = None
        self.logname = name

    def setup(self, config=None):
        if config is not None:
            highlights = config.get('highlights')
            logfile = config.get('logfile', 'falsy.log')
            file_level = config.get('file_level', 'DEBUG')
            console_level = config.get('console_level', 'DEBUG')
            handlers = config.get('handlers', ['file', 'console'])
            extra_loggers = config.get('extra_loggers')
        else:
            highlights = None
            logfile = 'falsy.log'
            file_level = console_level = 'DEBUG'
            handlers = ['file', 'console']
            extra_loggers = None
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'file': {
                    'fmt': '%(asctime)s.%(msecs)03d %(levelname)-8s %(name)-8s %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S %Z%z'
                },
                'console': {
                    '()': JLogColoredFormatter,
                    'fmt': '%(99)s%(process)s-%(thread)s%(reset)s %(yellow)s%(asctime)s.%(msecs)03d%(reset)s %(cyan)s%(name)-8s%(reset)s'
                           '%(log_color)s%(message)s%(reset)s%(trace)s%(high)s',
                    'datefmt': '%m%d %H:%M:%S',
                    'log_colors': {
                        'DEBUG': 'blue',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red',
                    }
                },

            },
            'filters': {
                'trace_filter': {
                    '()': TraceFilter,
                },
                'highlight_filter': {
                    '()': HighlightFilter,
                    'highlights': highlights
                }
            },
            'handlers': {
                'file': {
                    'level': file_level,
                    'filters': None,
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'filename': logfile,
                    'formatter': 'file'
                },
                'console': {
                    'level': console_level,
                    'filters': ['trace_filter', 'highlight_filter'],
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                    'formatter': 'console'
                },
            },
            'loggers': {
                self.logname: {
                    'handlers': handlers,
                    'level': 'DEBUG',
                    'propagate': False,
                },
            }
        }
        if extra_loggers:
            config['loggers'].update(extra_loggers)
        logging.config.dictConfig(config)
        return self

    def bind(self):
        self.logger = logging.getLogger(self.logname)
        return self

    def bind2(self, logname):
        self.logger = logging.getLogger(logname)
        return self

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
                blue() + filename, yellow() + str(s.lineno),
                '|' + '-' * (i * 4) + cyan() + s.name + ':' + red() + s.line)
            lines.append(line)
        lines = '\n\t'.join(lines)
        kwargs['extra'] = {
            'trace': magenta() + str(exc_type) + ' ' + bold() + magenta() + str(exc_value) + '\n\t' + lines}
