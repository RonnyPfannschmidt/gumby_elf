import os
import hashlib
import base64
import subprocess
import pkgutil

import zipfile

from .metadata import EntryPoints, WheelInfo

WHEEL_FMT = './dist/{spec[name]}-{version}-py27.py3-none-any.whl'
DISTINFO_FMT = '{spec[name]}-{version}.dist-info'


def record_hash(data):
    return 'sha1=' + base64.urlsafe_b64encode(hashlib.sha1(data).digest())


class WheelBundler(object):
    def __init__(self, path):
        self.archive = zipfile.ZipFile(path, 'w')
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


def metadata_11(spec, version):
    # XXX: better pathhandling
    # XXX: incomplete
    result = [
        'Name: $(name)\n' % spec.data,
        'Version: ' + version + '\n',
    ]
    return ''.join(result)


def entrypoints_11(spec):
    ep = EntryPoints.from_spec_dict(spec)
    return ep.to_11_metadata()


def bootstraper(spec):
    fn = os.path.abspath(spec.filename)
    srcdir = os.path.join(os.path.dirname(fn), 'src')
    template = pkgutil.get_data(__name__, 'bootstrap_template.py.txt')
    return template.format(srcfolder=srcdir)


def install_extra_requires(spec, requested_extras):
    extras = spec.get('dependenciesExtra', {})
    required = []
    for extra in requested_extras:
        required.extend(extras[extra])
    return subprocess.call(['pip', 'install', '-q'] + required)


def install_develop_data(spec):
    if not os.path.isdir('dist'):
        os.mkdir('dist')
    spec_char = '.' if '+' in spec.version else '+'
    version = spec.version + spec_char + ".gumby.develop"
    wheel_filename = WHEEL_FMT.format(spec=spec, version=version)

    bundle = WheelBundler(wheel_filename)
    bundle.add_file(
        spec.data['package'] + '.py',
        bootstraper(spec))

    distinfo_folder = DISTINFO_FMT.format(
        spec=spec,
        version=version)

    bundle.add_file(
        os.path.join(distinfo_folder, 'METADATA'),
        metadata_11(spec, version),
    )
    bundle.add_file(
        os.path.join(distinfo_folder, 'entry_points.txt'),
        entrypoints_11(spec),
    )
    bundle.add_file(
        os.path.join(distinfo_folder, 'WHEEL'),
        str(WheelInfo.default()),
    )
    bundle.finalize(os.path.join(distinfo_folder, 'RECORD'))
    return subprocess.call(
        ['pip', 'install', '-q', '-U', wheel_filename])
