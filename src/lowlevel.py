import os
import distutils
import hashlib
from setuptools_scm import get_version
SITE_PACKAGES = distutils.sysconfig_get_python_lib()

BOOTSTRAP_TEMPLATE="""
import os
__path__ = [{srcfolder!r}]
__file__ = os.path.join({srcfolder!r}, '__init__.py')
del os
execfile(__file__)
"""

import base64


def record_hash(data):
    return 'sha1=' + base64.urlsafe_b64encode(hashlib.sha1(data).digest())


class FileBundle(object):
    def __init__(self):
        self.needed_folders = set()
        self.files = {}
        self.finalized = False


    def add_file(self, name, data):
        assert not self.finalized
        dirname = os.path.dirname(name)
        if dirname:
            self.needed_folders.add(dirname)
        self.files[name] = data

    def finalize(self, record_filename):
        record_entries = [
            (name, record_hash(data))
            for name, data in sorted(self.files.items())
        ]
        record_entries.append((record_filename, ''))
        self.files[record_filename] = '\n'.join(
            ','.join(x) for x in record_entries)
        self.finalized = True

    def to_filesystem(self):
        for folder in sorted(self.needed_folders):
            # will autouse abs if folder is abspath
            folder = os.path.join(SITE_PACKAGES, folder)
            if not os.path.isdir(folder):
                os.makedirs(folder)

        for name, data in sorted(self.files.items()):
            # will autouse abspath if name is abs
            path = os.path.join(SITE_PACKAGES, name)
            with open(path, 'w') as fp:
                fp.write(data)


def metadata_11(spec):
    #XXX: better pathhandling
    #XXX: incomplete
    version = get_version()
    result = [
        'Name: $(name)\n' % spec.data,
        'Version: ' + version + '\n',
    ]
    return ''.join(result)


def bootstraper(spec):
    fn = os.path.abspath(spec.filename)
    srcdir = os.path.join(os.path.dirname(fn), 'src')
    return BOOTSTRAP_TEMPLATE.format(srcfolder=srcdir)



def install_develop_data(spec):
    bundle = FileBundle()

    distinfo_folder = '%(name)s-develop.dist-info' % spec.data
    bundle.add_file(os.path.join(distinfo_folder, 'REQUESTED'), '')

    bundle.add_file(
        os.path.join(distinfo_folder, 'METADATA'),
        metadata_11(spec),
    )
    bundle.add_file(os.path.join(distinfo_folder, 'INSTALLER'), 'gumby elf')
    bundle.add_file(spec.data['package'] + '.py', bootstraper(spec))
    bundle.finalize(os.path.join(distinfo_folder, 'RECORD'))
    bundle.to_filesystem()
