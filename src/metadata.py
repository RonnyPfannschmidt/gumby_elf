from collections import namedtuple

class EntryPoint(namedtuple('EntryPoint', 'name entry extras')):

    def __str__(self):
        return "{self.name} = {self.entry} {self.extras}".format(self=self)


class EntryPoints(object):


    def __init__(self):
        self.listings = {}

    @classmethod
    def from_spec_dict(cls, data):
        self = cls()
        data = data.get('entrypoints', data)
        for name, mapping in data.items():
            items = self.listings[name] = []
            for entry_name, entry_str in mapping.items():
                items.append(EntryPoint(
                    name=entry_name,
                    entry=entry_str,
                    extras='',
                ))
        return self

    def to_11_metadata(self):
        res = []
        for name, listing in self.listings.items():
            res.append('[{}]'.format(name))
            for item in listing:
                res.append(str(item).strip())
        return '\n'.join(res)
