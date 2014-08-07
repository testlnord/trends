""" Source exceptions and errors """
__author__ = 'user'


class SourceException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


class UnknownTechnology(SourceException):
    def __init__(self, tech=None):
        if tech is None:
            super().__init__("Unknown technology" + tech)
        else:
            super().__init__("Unknown technology")

if __name__ == "__main__":
    pass