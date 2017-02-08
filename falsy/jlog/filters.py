import logging

from falsy.termcc.termcc import magenta, rmagenta, cc


class TraceFilter(logging.Filter):
    def filter(self, record):
        if 'trace' not in dir(record):
            record.trace = ''
        else:
            record.trace = '\n\t' + record.trace
        return True


class HighlightFilter(logging.Filter):
    def __init__(self, highlights=None):
        self.highlights = highlights

    def filter(self, record):
        record.high = ''
        if self.highlights is None:
            return True
        for e in self.highlights:
            if e in record.msg:
                record.high = '\n\t' + \
                              magenta() + 'highlight' + rmagenta() + ': ' + \
                              record.msg.replace(e, cc(e, fore='yellow', back='red'))
        return True

