
from ._metadata import Specification
from . import _packing as pack

from setuptools_scm import get_version

from pathlib import Path

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    spec = Specification.from_project_dir()
    spec.version = get_version()
    return pack.build_wheel(spec, Path(wheel_directory))
    
def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    spec = Specification.from_project_dir()
    spec.version = get_version()
    return pack.build_editable(spec, Path(wheel_directory))

def build_sdist(sdist_directory, config_settings=None):
    ...