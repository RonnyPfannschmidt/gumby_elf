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


class WheelInfo(object):
    def __init__(self, wheel_version, tags, root_purelib):
        self.wheel_version = wheel_version
        self.tags = tags
        self.root_purelib = root_purelib

    @classmethod
    def default(cls):
        return cls(
            wheel_version='1.0',
            tags=[
                'py27-none-any',
                'py3-none-any',
            ],
            root_purelib=True,
        )

    def __str__(self):
        res = [
            'Wheel-Version: {wv}'.format(wv=self.wheel_version),
            'Generator: gumby_elf pre alpha',
            'Root-Is-Purelib: {rp}'.format(
                rp='true' if self.root_purelib else 'false'),
        ]
        for tag in self.tags:
            res.append(
                'Tag: {tag}'.format(tag=tag)
            )
        return '\n'.join(res)

    def to_bytes(self):
        data = str(self)
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        return data
