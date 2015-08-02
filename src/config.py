import os
from .core import manager

def read_specification(root):
    return manager.hook.read_specification(root=root)


class Specification(object):
    def __init__(self, fp):
        self.filename = fp.name
        with fp:
            self.deserialize(fp)

    def deserialize(self, fp):
        raise NotImplementedError('deserialize')
