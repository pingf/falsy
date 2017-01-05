import os
# import pprint

import yaml


class LoaderMeta(type):

    def __new__(metacls, __name__, __bases__, __dict__):
        """Add include constructer to class."""

        # register the include constructor on the class
        cls = super().__new__(metacls, __name__, __bases__, __dict__)
        cls.add_constructor('!include', cls.construct_include)
        cls.add_constructor('include!', cls.construct_include)

        return cls


class Loader(yaml.Loader, metaclass=LoaderMeta):
    """YAML Loader with `!include` constructor."""

    def __init__(self, stream):
        """Initialise Loader."""

        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream)

    def construct_include(self, node):
        """Include file referenced at node."""

        filename = os.path.abspath(os.path.join(
            self._root, self.construct_scalar(node)
        ))
        filename = os.path.join(self._root, self.construct_scalar(node))

        extension = os.path.splitext(filename)[1].lstrip('.')

        with open(filename, 'r') as f:
            if extension in ('yaml', 'yml'):
                return yaml.load(f, Loader)
            else:
                return ''.join(f.readlines())


def load(filename):
    with open(filename, 'r') as f:
        data = yaml.load(f, Loader)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(data)
    return data
