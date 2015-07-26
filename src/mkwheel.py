from os import path, walk
from zipfile import ZipFile
from base64 import urlsafe_b64encode
from hashlib import sha1

from .metadata import WheelInfo


WHEEL_FMT = '{spec.name}-{version}-py27.py3-none-any.whl'
DISTINFO_FMT = '{spec.name}-{version}.dist-info'


def wheel_name(dist, spec, version):
    filename = WHEEL_FMT.format(spec=spec, version=version)
    return path.join(dist, filename)


def record_hash(data):
    digest = sha1(data).digest()
    return 'sha1=' + urlsafe_b64encode(digest).decode('ascii')


def entrypoints_11(spec):
    with open(spec.data['entry-points'], 'rb') as fp:
        return fp.read()


class WheelBuilder(object):
    def __init__(self, target):
        self.archive = ZipFile(target, 'w')
        self.record = []

    def add_file(self, name, data):
        assert getattr(self, 'record', None) is not None
        self.record.append((name, record_hash(data)))
        self.archive.writestr(name, data)

    def finalize(self, record_filename):
        self.record.append((record_filename, ''))
        self.archive.writestr(record_filename, '\n'.join(
            ','.join(x) for x in self.record))
        del self.record
        self.archive.close()


def finalize_whl_metadata(builder, spec, version):
    distinfo_folder = DISTINFO_FMT.format(
        spec=spec,
        version=version)

    builder.add_file(
        path.join(distinfo_folder, 'METADATA'),
        metadata_11(spec, version),
    )
    builder.add_file(
        path.join(distinfo_folder, 'entry_points.txt'),
        entrypoints_11(spec),
    )
    builder.add_file(
        path.join(distinfo_folder, 'WHEEL'),
        WheelInfo.default().to_bytes(),
    )
    builder.finalize(path.join(distinfo_folder, 'RECORD'))


def write_src_to_whl(builder, spec):
    for folder, dirs, files in walk('src'):

        targetfolder = spec.package + folder[3:]

        for file_name in files:
            if file_name[-4:] in ('.pyc', '.pyo'):
                continue
            with open(path.join(folder, file_name)) as fp:
                content = fp.read()
            builder.add_file(
                name=path.join(targetfolder, file_name),
                data=content,
            )


def metadata_11(spec, version):
    # XXX: better pathhandling
    # XXX: incomplete
    assert spec.metadata
    from email.generator import Generator
    spec.metadata['Version'] = version

    from six import StringIO
    io = StringIO()
    Generator(io).flatten(spec.metadata)
    return io.getvalue().encode('utf-8')
