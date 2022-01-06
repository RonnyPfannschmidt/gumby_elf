from __future__ import annotations

from base64 import urlsafe_b64encode
from contextlib import closing
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from pathlib import PurePath
from typing import Generator
from typing import NamedTuple
from zipfile import ZipFile

from ._metadata import entrypoints_from_spec
from ._metadata import get_wheel_info
from ._metadata import Specification


WHEEL_FMT = "{spec.name}-{spec.version}-py3-none-any.whl"
DISTINFO_FMT = "{spec.name}-{spec.version}.dist-info"


def wheel_name(dist: Path, spec) -> Path:
    filename = WHEEL_FMT.format(spec=spec)
    return dist.joinpath(filename)


def record_hash(data: bytes) -> str:
    digest = sha1(data).digest()
    return "sha1=" + urlsafe_b64encode(digest).decode("ascii")


class Record(NamedTuple):
    path: PurePath
    hash: str | None

    def as_record(self):
        return f"{self.path}, {self.hash or ''}"


@dataclass
class WheelBuilder:
    _archive: ZipFile
    _record: list[Record]

    @classmethod
    @contextmanager
    def for_target(
        cls, target: Path, spec: Specification
    ) -> Generator[WheelBuilder, None, None]:

        with closing(ZipFile(target, "w")) as archive:
            record: list[Record] = []
            bld = WheelBuilder(archive, record)
            yield bld

            _finalize_whl_metadata(bld, spec)
            record.clear()

    def add_file(self, name: PurePath, data: bytes):
        self._record.append(Record(name, record_hash(data)))
        self._archive.writestr(str(name), data)


def _finalize_whl_metadata(builder, spec: Specification):
    distinfo = Path(DISTINFO_FMT.format(spec=spec))
    builder.add_file(
        distinfo / "METADATA",
        bytes(spec.pyproject_metadata.as_rfc822()),
    )
    builder.add_file(
        distinfo / "entry_points.txt",
        entrypoints_from_spec(spec),
    )
    builder.add_file(
        distinfo / "WHEEL",
        get_wheel_info(),
    )

    record = builder._record
    record_filename = distinfo / "RECORD"
    record.append(Record(record_filename, None))

    builder._archive.writestr(
        str(record_filename), "\n".join(x.as_record() for x in record).encode("utf-8")
    )
    record.clear()


def write_src_to_whl(builder, spec):
    src = Path("src")
    items = sorted(src.glob("**/*"))

    package = PurePath(spec.package)
    print(items)

    for item in items:
        if not item.is_file():
            continue
        if item.suffix in (".pyc", ".pyo"):
            continue

        target = package.joinpath(item.relative_to(src))

        builder.add_file(
            name=target,
            data=item.read_bytes(),
        )
