import logging

import datetime

import collections

from falsy.jlog.filter import MyFilter



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


class MyFormatter(logging.Formatter):
    converter = datetime.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s



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


# Returns escape codes from format codes
def esc(*x):
    return '\033[' + ';'.join(x) + 'm'


# The initial list of escape codes
escape_codes = {
    'reset': esc('0'),
    'bold': esc('01'),
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
    """Return escape codes from a color sequence."""
    return ''.join(escape_codes[n] for n in sequence.split(',') if n)


def parse_colors(sequence):
    a = ''.join(escape_codes[n] for n in sequence.split(',') if n)
    return a


class JLogColoredFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%',
                 log_colors=None, reset=True):
        if fmt is None:
            fmt = default_formats[style]

        super(self).__init__(fmt, datefmt, style)

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

        message = super(self).format(record)

        if self.reset and not message.endswith(escape_codes['reset']):
            message += escape_codes['reset']

        return message






LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s.%(msecs)03d] - [%(levelname)-8s] - [%(name)-16s] - [%(message)s]',
            'datefmt': '%Y-%m-%d %H:%M:%S %Z%z'
        },
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            # 'format': '[%(asctime)s.%(msecs)03d] - [%(levelname)-8s] - [%(name)-16s] - [%(message)s]',
            'format': '[%(yellow,bg_cyan,bold)s%(asctime)s.%(msecs)03d%(reset)s] - [%(log_color)s%(levelname)-8s%(reset)s] - [%(purple)s%(name)-16s%(reset)s] - \n[%(cyan)s%(message)s%(reset)s]',
            'datefmt': '%Y-%m-%d %H:%M:%S %Z%z',
        },

        'log_colors': {
            'DEBUG': 'white',
            'INFO': 'bold_green',
            'WARNING': 'bold_yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'red,bg_white'
        }
    },
    'filters': {
        'myfilter': {
            '()': MyFilter,
            'param': 'noshow',
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
            'filters': ['myfilter'],
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

# class JLog:
#     def __init__(self, config=LOG_CONFIG):

# if __name__ == '__main__':
