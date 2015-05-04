import os
import hashlib
import base64
import subprocess
import pkgutil

import zipfile

from .metadata import EntryPoints, WheelInfo



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


def install_extra_requires(spec, requested_extras):
    extras = spec.get('dependenciesExtra', {})
    required = []
    for extra in requested_extras:
        required.extend(extras[extra])
    return subprocess.call(['pip', 'install', '-q'] + required)

