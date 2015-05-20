import os


def read_specification(root):
    joined = os.path.join(root, 'gumby_elf.ll.json')
    if os.path.exists(joined):
        with open(joined) as fp:
            return GumbyLowlevelSpecification(fp)
    assert 0


class Specification(object):
    def __init__(self, fp):
        self.filename = fp.name
        with fp:
            self.deserialize(fp)

    def deserialize(self, fp):
        raise NotImplementedError('deserialize')




class GumbyLowlevelSpecification(Specification):
    _metadata = None

    def deserialize(self, fp):
        from json import load
        self.data = load(fp)

    @property
    def name(self):
        return self.metadata['Name']


    @property
    def package(self):
        return self.data['package-map'].values()[0]
    @property
    def metadata(self):
        if self._metadata is None:
            metadata_file = self.data['metadata']
            import email
            with open(metadata_file) as fp:
                self._metadata = email.message_from_file(fp)
        return self._metadata


    def get_requires(self):
        return [
            x for x in self.metadata.get_all('requires-dist')
            if ';' not in x
        ]
