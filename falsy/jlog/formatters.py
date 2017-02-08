import logging

import collections

from falsy.termcc.termcc import fore, back, style, reset, rastyle, rred, ritalic, reverse, rafore, raback


class ColoredRecord(object):
    class __dict(collections.defaultdict):
        def __missing__(self, name):
            try:
                return parse_colors(name)
            except Exception:
                raise KeyError("{} is not a valid record attribute "
                               "or color sequence".format(name))

    def __init__(self, record):
        self.__dict__ = self.__dict()
        self.__dict__.update(record.__dict__)
        self.__record = record

    def __getattr__(self, name):
        return getattr(self.__record, name)


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
    'underlined': style('underlined'),
    'blink': style('blink'),
    'reverse': style('reverse'),
    'hidden': style('hidden'),

    'reset': reset(),
    'rstyle': rastyle(),
    'rafore': rafore(),
    'raback': raback(),
}


def get_color_code(e):
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
    a = ''.join(get_color_code(e) for e in sequence.split(',') if e)
    return a


class JLogColoredFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%',
                 log_colors=None, reset=True):
        if fmt is None:
            default_formats = {
                '%': '%(log_color)s%(levelname)s:%(name)s:%(message)s',
                '{': '{log_color}{levelname}:{name}:{message}',
                '$': '${log_color}${levelname}:${name}:${message}'
            }
            fmt = default_formats[style]

        super().__init__(fmt, datefmt, style)
        default_log_colors = {
            'DEBUG': 'white',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }

        self.log_colors = (
            log_colors if log_colors is not None else default_log_colors)
        self.reset = reset

    def color(self, log_colors, level_name):
        return parse_colors(log_colors.get(level_name, ""))

    def format(self, record):
        record = ColoredRecord(record)
        record.log_color = self.color(self.log_colors, record.levelname)

        message = super().format(record)

        if self.reset and not message.endswith(codes['reset']):
            message += codes['reset']

        return message
