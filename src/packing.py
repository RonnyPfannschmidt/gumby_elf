import os.path

import zipfile
import pkgutil
import hashlib
import base64

from .metadata import EntryPoints, WheelInfo


WHEEL_FMT = '{spec.name}-{version}-py27.py3-none-any.whl'
DISTINFO_FMT = '{spec.name}-{version}.dist-info'


def metadata_11(spec, version):
    # XXX: better pathhandling
    # XXX: incomplete
    assert spec.metadata
    from email.generator import Generator
    spec.metadata['Version'] = version
    from io import BytesIO
    io = BytesIO()
    Generator(io).flatten(spec.metadata)
    return io.getvalue()


def entrypoints_11(spec):
    with open(spec.parser.get('gumby_elf', 'entry_points')) as fp:
        return fp.read()


def record_hash(data):
    return 'sha1=' + base64.urlsafe_b64encode(hashlib.sha1(data).digest())


class WheelBuilder(object):
    def __init__(self, dist, target):
        self.archive = zipfile.ZipFile(
            os.path.join(dist, target), 'w')
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


def develop_version(version):
    spec_char = '.' if '+' in version else '+'
    return version + spec_char + "gumby.develop"


def finalize_whl_metadata(builder, spec, version):
    distinfo_folder = DISTINFO_FMT.format(
        spec=spec,
        version=version)

    builder.add_file(
        os.path.join(distinfo_folder, 'METADATA'),
        metadata_11(spec, version),
    )
    builder.add_file(
        os.path.join(distinfo_folder, 'entry_points.txt'),
        entrypoints_11(spec),
    )
    builder.add_file(
        os.path.join(distinfo_folder, 'WHEEL'),
        str(WheelInfo.default()),
    )
    builder.finalize(os.path.join(distinfo_folder, 'RECORD'))


def build_wheel(spec, distdir):
    target_filename = WHEEL_FMT.format(spec=spec, version=spec.version)
    bld = WheelBuilder(distdir, target_filename)
    write_src_to_whl(bld, spec)
    finalize_whl_metadata(bld, spec, version=spec.version)
    return target_filename


def bootstraper(spec):
    fn = os.path.abspath(spec.filename)
    srcdir = os.path.join(os.path.dirname(fn), 'src')
    template = pkgutil.get_data(__name__, 'bootstrap_template.py.txt')
    return template.format(srcfolder=srcdir)


def build_develop_wheel(spec, distdir):
    version = develop_version(spec.version)
    target_filename = WHEEL_FMT.format( spec=spec, version=version)
    bld = WheelBuilder(distdir, target_filename)
    bld.add_file(
        name=spec.package + '.py',
        data=bootstraper(spec),
    )
    finalize_whl_metadata(bld, spec, version=version)
    return target_filename
