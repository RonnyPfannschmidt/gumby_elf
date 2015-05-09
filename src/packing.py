import os.path

import zipfile
import pkgutil
import hashlib
import base64

from .metadata import EntryPoints, WheelInfo
from .mkwheel import (
    WheelBuilder,
    wheel_name,
    finalize_whl_metadata,
    write_src_to_whl,
)

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


def develop_version(version):
    spec_char = '.' if '+' in version else '+'
    return version + spec_char + "gumby.develop"




def build_wheel(spec, distdir):
    target_filename = wheel_name(distdir, spec, version=spec.version)
    bld = WheelBuilder(target_filename)
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
    target_filename = wheel_name(dist, spec, version=version)
    bld = WheelBuilder(target_filename)
    bld.add_file(
        name=spec.package + '.py',
        data=bootstraper(spec),
    )
    finalize_whl_metadata(bld, spec, version=version)
    return target_filename
