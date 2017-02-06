import logging

import sys
import traceback

import collections
from colorlog import ColoredFormatter
from falsy.termcc.termcc import blue, yellow, cyan, red, bold, magenta, red_, green, fore, reset, \
    back, style, rstyle, ritalic, rred, rastyle, reverse


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
                record.high = '\n\t\t' + magenta('highlight') + ': ' + record.msg.replace(e, red_(yellow(e)))
        return True


# from colorlog import ColoredFormatter

default_formats = {
    '%': '%(log_color)s%(levelname)s:%(name)s:%(message)s',
    '{': '{log_color}{levelname}:{name}:{message}',
    '$': '${log_color}${levelname}:${name}:${message}'
}
import sys

default_log_colors = {
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}

codes = {
    'black': fore('black'),
    'red': fore('red'),
    'green': fore('green'),
    'yellow': fore('yellow'),
    'blue': fore('blue'),
    'magenta': fore('magenta'),
    'cyan': fore('cyan'),
    'lgray': fore('lightgray'),
    'gray': fore('darkgray'),
    'lred': fore('lightred'),
    'lgreen': fore('lightgreen'),
    'lyellow': fore('lightyellow'),
    'lblue': fore('lightblue'),
    'lmagenta': fore('lightmagenta'),
    'lcyan': fore('lightcyan'),
    'white': fore('white'),

    'black_': back('black'),
    'red_': back('red'),
    'green_': back('green'),
    'yellow_': back('yellow'),
    'blue_': back('blue'),
    'magenta_': back('magenta'),
    'cyan_': back('cyan'),
    'lgray_': back('lightgray'),
    'gray_': back('darkgray'),
    'lred_': back('lightred'),
    'lgreen_': back('lightgreen'),
    'lyellow_': back('lightyellow'),
    'lblue_': back('lightblue'),
    'lmagenta_': back('lightmagenta'),
    'lcyan_': back('lightcyan'),
    'white_': back('white'),

    'bold': style('bold'),
    'dim': style('dim'),
    'italic': style('italic'),
    'reverse': style('reverse'),
    'reset': reset(),
    'rstyle': rastyle(),
    'rred': rred(),
    'ritalic': ritalic(),
    'reverse': reverse()
}

# The color names
COLORS = [
    'black',
    'red',
    'green',
    'yellow',
    'blue',
    'purple',
    'cyan',
    'white'
]


def get_code(e):
    if '0' <= e[0] <= '9':
        if len(e) > 1:
            if e[-1] == '_':
                return back(int(e[:-1]))
            else:
                return fore(int(e))
        else:
            return fore(e)
    return codes[e]


def parse_colors(sequence):
    # a = ''.join(escape_codes[n] for n in sequence.split(',') if n)
    a = ''.join(get_code(e) for e in sequence.split(',') if e)
    return a


class ColoredRecord(object):
    class __dict(collections.defaultdict):
        def __missing__(self, name):
            try:
                return parse_colors(name)
            except Exception:
                raise KeyError("{} is not a valid record attribute "
                               "or color sequence".format(name))

    def __init__(self, record):
        # Replace the internal dict with one that can handle missing keys
        self.__dict__ = self.__dict()
        self.__dict__.update(record.__dict__)

        self.__record = record

    def __getattr__(self, name):
        return getattr(self.__record, name)


class JLogColoredFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%',
                 log_colors=None, reset=True):
        if fmt is None:
            fmt = default_formats[style]

        super().__init__(fmt, datefmt, style)

        self.log_colors = (
            log_colors if log_colors is not None else default_log_colors)
        self.reset = reset

    def color(self, log_colors, level_name):
        """Return escape codes from a ``log_colors`` dict."""
        return parse_colors(log_colors.get(level_name, ""))

    def format(self, record):
        """Format a message from a record object."""
        record = ColoredRecord(record)
        record.log_color = self.color(self.log_colors, record.levelname)

        message = super().format(record)

        if self.reset and not message.endswith(codes['reset']):
            message += codes['reset']

        return message


class JLog:
    def __init__(self):
        self.logger = None

    def setup(self, hightable=None):
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s.%(msecs)03d %(levelname)-8s %(name)-8s %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S %Z%z'
                },
                'colored': {
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
                    'hightable': hightable
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
        logging.config.dictConfig(config)
        return self

    def bind(self, name='falsy'):
        self.logger = logging.getLogger(name)
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
                blue()+filename, yellow()+str(s.lineno), '|' + '-' * (i * 4) + cyan()+s.name + ':' + red()+s.line)
            lines.append(line)
        lines = '\n\t'.join(lines)
        kwargs['extra'] = {'trace': magenta()+str(exc_type) + ' ' + bold()+magenta()+str(exc_value) + '\n\t' + lines}

