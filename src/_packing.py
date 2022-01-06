import os.path
import pkgutil
from pathlib import Path

from ._metadata import Specification
from ._mksdist import sdist_path
from ._mksdist import SdistBuilder
from ._mkwheel import wheel_name
from ._mkwheel import WheelBuilder
from ._mkwheel import write_src_to_whl


def build_wheel(spec: Specification, distdir: Path):
    target_filename = wheel_name(distdir, spec)
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
    target_filename = wheel_name(
        distdir,
        spec,
    )
    with WheelBuilder.for_target(target_filename, spec) as bld:
        bld.add_file(
            name=spec.package + ".py",
            data=bootstraper(spec),
        )
    return target_filename


def build_sdist(spec: Specification, sdist_dir: Path) -> Path:
    target = sdist_path(sdist_dir, spec)
    with SdistBuilder.for_target(target, spec) as sdist:
        # todo: better config

        from setuptools_scm.integration import find_files

        for name in find_files(""):
            with open(name, "rb") as fp:
                sdist.add_file(name, fp.read())
    return target
