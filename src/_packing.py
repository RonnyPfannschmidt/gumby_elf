import os.path

import pkgutil

from ._mkwheel import (
    WheelBuilder,
    wheel_name,
    write_src_to_whl,
)


def develop_version(version):
    spec_char = "." if "+" in version else "+"
    return version + spec_char + "gumby.develop"


def build_wheel(spec, distdir):
    target_filename = wheel_name(distdir, spec, version=spec.version)
    with WheelBuilder.for_target(target_filename, spec) as bld:
        write_src_to_whl(bld, spec)
    return target_filename


def bootstraper(spec):
    fn = os.path.abspath(spec.source_file)
    srcdir = os.path.join(os.path.dirname(fn), "src")
    template = pkgutil.get_data(__name__, "bootstrap_template.py.txt")
    template = template.decode("utf-8")
    return template.format(srcfolder=srcdir).encode("utf-8")


def build_editable(spec, distdir):
    spec.version = develop_version(spec.version)
    target_filename = wheel_name(distdir, spec, )
    with WheelBuilder.for_target(target_filename, spec) as bld:
        bld.add_file(
            name=spec.package + ".py",
            data=bootstraper(spec),
        )
    return target_filename
