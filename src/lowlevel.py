import os
import sys
import stat
import hashlib
import base64
import subprocess

import zipfile

from setuptools_scm import get_version

WHEEL_FMT = './dist/{spec[name]}-{version}-py27.py3-none-any.whl'
BOOTSTRAP_TEMPLATE = """
# development script generated by gumby elf
import os
__path__ = [{srcfolder!r}]
__file__ = os.path.join({srcfolder!r}, '__init__.py')
del os
with open(__file__) as fp:
    __code = compile(fp.read(), __file__, 'exec')
    exec(__code, globals(), globals())
"""
WHEEL_DEFAULT_META = """\
Wheel-Version: 1.0
Generator: gumby_elf
Root-Is-Purelib: true
Tag: py27-none-any
Tag: py3-none-any
Build: 1
"""

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


def metadata_11(spec):
    #XXX: better pathhandling
    #XXX: incomplete
    version = get_version()
    result = [
        'Name: $(name)\n' % spec.data,
        'Version: ' + version + '\n',
    ]
    return ''.join(result)

def entrypoints_11(spec):
    entrypoints = spec.get('entrypoints', {})
    res = ""
    for name, items in entrypoints.items():
        items = ['{0} = {1}'.format(*item) for item in items.items()]
        res += '[' + name + ']\n' + '\n'.join(items) + '\n'
    return res




def bootstraper(spec):
    fn = os.path.abspath(spec.filename)
    srcdir = os.path.join(os.path.dirname(fn), 'src')
    return BOOTSTRAP_TEMPLATE.format(srcfolder=srcdir)

def install_extra_requires(spec, requested_extras):
    extras = spec.get('dependenciesExtra', {})
    required = []
    for extra in requested_extras:
        required.extend(extras[extra])
    return subprocess.call(['pip', 'install', '-q'] + required)

def install_develop_data(spec):
    if not os.path.isdir('dist'):
        os.mkdir('dist')
    if '+' in spec.version:
        version = spec.version + ".gumby.develop"
    else:
        version = spec.version + "+gumby.develop"
    wheel_filename = WHEEL_FMT.format(spec=spec, version=version)

    bundle = WheelBundler(wheel_filename)
    bundle.add_file(
        spec.data['package'] + '.py',
        bootstraper(spec))

    distinfo_folder = '{spec[name]}-{spec.version}.dist-info'.format(spec=spec)

    bundle.add_file(
        os.path.join(distinfo_folder, 'METADATA'),
        metadata_11(spec),
    )
    bundle.add_file(
        os.path.join(distinfo_folder, 'entry_points.txt'),
        entrypoints_11(spec),
    )
    bundle.add_file(
        os.path.join(distinfo_folder, 'WHEEL'),
        WHEEL_DEFAULT_META,
    )
    bundle.finalize(os.path.join(distinfo_folder, 'RECORD'))
    return subprocess.call(
        ['pip', 'install', '-q', '-U', wheel_filename])