import os


def read_specification(root):
    print root, os.listdir(root)
    joined = os.path.join(root, 'gumby_elf.ll.ini')
    if os.path.exists(joined):
        with open(joined) as fp:
            return GumbyLowlevelIniSpecification(fp)
    assert 0


class Specification(object):
    def __init__(self, fp):
        self.filename = fp.name
        with fp:
            self.deserialize(fp)

    def deserialize(self, fp):
        raise NotImplementedError('deserialize')



class PackageJSonSpecification(Specification):
    def deserialize(self, fp):
        self.data = json.load(fp)['python package']

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)


class GumbyLowlevelIniSpecification(Specification):
    _metadata = None
    def deserialize(self, fp):
        try:
            from configparser import ConfigParser
        except ImportError:
            from ConfigParser import ConfigParser
        self.parser = ConfigParser()
        self.parser.readfp(fp)

    @property
    def name(self):
        return self.metadata['Name']


    @property
    def package(self):
        return self.parser.get('gumby_elf', 'package')

    @property
    def metadata(self):
        if self._metadata is None:
            metadata_file = self.parser.get("gumby_elf", 'metadata_base')
            import email
            with open(metadata_file) as fp:
                self._metadata = email.message_from_file(fp)
        return self._metadata


    def get_requires(self):
        return [
            x for x in self.metadata.get_all('requires-dist')
            if ';' not in x
        ]
