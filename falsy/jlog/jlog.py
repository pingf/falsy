import logging

import sys
import traceback

import collections
from colorlog import ColoredFormatter
from falsy.termcc.termcc import blue, yellow, cyan, red, bold, magenta, red_, green, color, reset, TERMCC_BOLD, \
     back, TERMCC_DIM, style, rstyle, ritalic, rred, rastyle, wrap


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
    'CRITICAL': 'bold_red',
}




codes = {
    'black': color('black'),
    'red': color('red'),
    'green': color('green'),
    'yellow': color('yellow'),
    'blue': color('blue'),
    'magenta': color('magenta'),
    'cyan': color('cyan'),
    'lgray': color('lightgray'),
    'gray': color('darkgray'),
    'lred': color('lightred'),
    'lgreen': color('lightgreen'),
    'lyellow': color('lightyellow'),
    'lblue': color('lightblue'),
    'lmagenta': color('lightmagenta'),
    'lcyan': color('lightcyan'),
    'white': color('white'),


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



def parse_colors(sequence):
    # a = ''.join(escape_codes[n] for n in sequence.split(',') if n)
    a = wrap(''.join(codes[n] for n in sequence.split(',') if n))
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

        if self.reset and not message.endswith(wrap(codes['reset'])):
            message += wrap(codes['reset'])

        return message


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
                    # '()': 'colorlog.ColoredFormatter',
                    '()': JLogColoredFormatter,
                    'fmt': '%(yellow)s%(asctime)s.%(msecs)03d%(reset)s %(cyan)s%(name)-8s%(reset)s'
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
