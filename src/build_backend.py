import os
from pathlib import Path

from setuptools_scm import get_version

from . import _packing as pack
from ._metadata import Specification


def build_wheel(wheel_directory: str, config_settings=None, metadata_directory=None):
    spec = Specification.from_project_dir()
    spec.version = get_version()
    return os.fspath(pack.build_wheel(spec, Path(wheel_directory)))


def build_editable(wheel_directory: str, config_settings=None, metadata_directory=None):
    spec = Specification.from_project_dir()
    spec.version = get_version()
    return os.fspath(pack.build_editable(spec, Path(wheel_directory)))


def build_sdist(sdist_directory: str, config_settings=None):
    spec = Specification.from_project_dir()
    spec.version = get_version()
    return os.fspath(pack.build_sdist(spec, Path(sdist_directory)))
