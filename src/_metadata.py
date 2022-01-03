from pathlib import Path
from typing import Any, Sequence, Dict
from dataclasses import dataclass

from pep621 import StandardMetadata
import tomli


@dataclass
class Specification:
    source_file: Path
    toml_data: Dict["str", Any]
    pyproject_metadata: StandardMetadata

    @property
    def name(self):
        return self.pyproject_metadata.name

    @property
    def package(self):
        return self.toml_data["tool"]["gumby_elf"]["package-name"]

    @classmethod
    def from_project_dir(cls):
        source_file = Path("pyproject.toml")
        toml_data = tomli.loads(source_file.read_text())
        return Specification(
            source_file=source_file,
            toml_data=toml_data,
            pyproject_metadata=StandardMetadata.from_pyproject(toml_data),
        )


def get_wheel_info(
    wheel_version: str = "1.0",
    tags: Sequence[str] = (b"py3-none-any"),
    root_purelib: bool = True,
) -> str:

    return "\n".join(
        [
            f"Wheel-Version: {wheel_version}",
            "Generator: gumby_elf pre alpha",
            f"Root-Is-Purelib: {'true' if root_purelib else 'false'}",
            *(f"Tag: {tag}" for tag in tags),
        ]
    ).encode("utf-8")


def entrypoints_from_spec(spec: Specification):
    return entrypoints_txt(spec.pyproject_metadata)


def entrypoints_txt(metadata) -> bytes:
    data = metadata.entrypoints.copy()
    data.update(
        {
            "console_scripts": metadata.scripts,
            "gui_scripts": metadata.gui_scripts,
        }
    )

    def entries():
        for entrypoint, items in data.items():
            if not items:
                continue
            yield f"[{entrypoint}]\n"
            for name, target in items.items():
                yield f"{name} = {target}\n"
            yield "\n"

    return "".join(entries()).encode()
