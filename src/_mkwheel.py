from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import List, NamedTuple, Optional
from zipfile import ZIP_LZMA, ZipFile
from base64 import urlsafe_b64encode
from hashlib import sha1

from ._metadata import get_wheel_info, Specification, entrypoints_from_spec


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
    hash: Optional[str]

    def as_record(self):
        return f"{self.path}, {self.hash or ''}"



@dataclass
class WheelBuilder(object):
    _archive: ZipFile
    _record: List[Record] 


    @classmethod
    @contextmanager
    def for_target(cls, target: Path, spec: Specification):
        
        with closing(ZipFile(target, "w", compression=ZIP_LZMA)) as archive:
            record = []
            bld = WheelBuilder(archive, record)
            yield bld

            _finalize_whl_metadata(bld, spec)
            record.clear()

        


    def add_file(self, name: PurePath, data: bytes):
        self._record.append(Record(name, record_hash(data)))
        self._archive.writestr(str(name), data)

    


def _finalize_whl_metadata(builder, spec):
    distinfo = Path(DISTINFO_FMT.format(spec=spec))
    spec.pyproject_metadata.version = spec.version
    spec.pyproject_metadata.dynamic.remove("version")
    builder.add_file(
        distinfo / "METADATA",
        bytes(spec.pyproject_metadata.as_rfc822()),
    )
    builder.add_file(
        distinfo /"entry_points.txt",
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
    for folder, dirs, files in walk("src"):

        targetfolder = spec.package + folder[3:]

        for file_name in files:
            if file_name[-4:] in (".pyc", ".pyo"):
                continue
            with open(path.join(folder, file_name)) as fp:
                content = fp.read()
            builder.add_file(
                name=path.join(targetfolder, file_name),
                data=content,
            )
