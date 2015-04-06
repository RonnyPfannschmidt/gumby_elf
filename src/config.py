import json
class Specification(object):
    def __init__(self, fp):
        self.filename = fp.name
        self.data = json.load(fp)['python package']
