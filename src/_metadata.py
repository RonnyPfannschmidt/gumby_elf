from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomli
from packaging.version import Version
from pep621 import StandardMetadata


@dataclass
class Specification:
    source_file: Path
    toml_data: dict[str, Any]
    pyproject_metadata: StandardMetadata

    @property
    def name(self) -> str:
        return self.pyproject_metadata.name

    @property
    def package(self) -> str:
        return self.toml_data["tool"]["gumby_elf"]["package-name"]

    @property
    def version(self) -> Version:
        return self.pyproject_metadata.version

    @version.setter
    def version(self, new_value: Version | str) -> Version:
        if not isinstance(new_value, Version):
            new_value = Version(new_value)
        self.pyproject_metadata.version = new_value
        if "version" in self.pyproject_metadata.dynamic:
            self.pyproject_metadata.dynamic.remove("version")

    @classmethod
    def from_project_dir(
        cls, source_file: Path = Path("pyproject.toml")
    ) -> Specification:
        toml_data = tomli.loads(source_file.read_text())
        return Specification(
            source_file=source_file,
            toml_data=toml_data,
            pyproject_metadata=StandardMetadata.from_pyproject(toml_data),
        )


def get_wheel_info(
    wheel_version: str = "1.0",
    tags: tuple[str, ...] = ("py3-none-any",),
    root_purelib: bool = True,
) -> bytes:

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
