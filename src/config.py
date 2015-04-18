import json


class Specification(object):
    def __init__(self, fp):
        self.filename = fp.name
        self.data = json.load(fp)['python package']

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)
