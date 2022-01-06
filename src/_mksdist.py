import tarfile
from contextlib import contextmanager
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from pathlib import PurePath

from ._metadata import Specification


def sdist_path(sdist_dir: Path, spec: Specification) -> Path:
    return sdist_dir / f"{spec.name}-{spec.version}.tar.gz"


@dataclass
class SdistBuilder:
    _tarfile: tarfile.TarFile
    _spec: Specification
    basename: PurePath

    def add_file(self, name, content: bytes):
        arcname = self.basename / name
        tarinfo = tarfile.TarInfo(name=str(arcname))
        tarinfo.mtime = 0
        tarinfo.size = len(content)
        self._tarfile.addfile(tarinfo, BytesIO(content))

    @classmethod
    @contextmanager
    def for_target(self, target_path: Path, spec: Specification):
        basename = PurePath(f"{spec.name}-{spec.version}")
        with tarfile.open(target_path, "w") as fp:
            builder = SdistBuilder(fp, spec, basename=basename)
            builder.add_file("PKG-INFO", bytes(spec.pyproject_metadata.as_rfc822()))
            yield builder
