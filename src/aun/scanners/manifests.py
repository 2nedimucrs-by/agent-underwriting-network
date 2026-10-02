from __future__ import annotations

import json
import re
import tomllib
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class DependencySignal:
    ecosystem: str
    name: str
    declared_version: str | None
    source_path: str


def _clean_requirement(line: str) -> tuple[str, str | None] | None:
    value = line.strip()
    if not value or value.startswith("#") or value.startswith("-"):
        return None
    value = value.split(";", 1)[0].strip()
    match = re.match(r"^([A-Za-z0-9_.-]+)\s*([<>=!~].+)?$", value)
    if not match:
        return None
    return match.group(1), (match.group(2) or None)


def extract_dependencies(files: Mapping[str, str]) -> list[DependencySignal]:
    signals: list[DependencySignal] = []

    for path, content in files.items():
        lower = path.lower()

        if lower.endswith("requirements.txt"):
            for line in content.splitlines():
                parsed = _clean_requirement(line)
                if parsed:
                    name, version = parsed
                    signals.append(
                        DependencySignal("python", name, version, path)
                    )

        elif lower.endswith("package.json"):
            try:
                payload = json.loads(content)
            except json.JSONDecodeError:
                continue
            for section in ("dependencies", "devDependencies", "peerDependencies"):
                for name, version in (payload.get(section) or {}).items():
                    signals.append(
                        DependencySignal("npm", name, str(version), path)
                    )

        elif lower.endswith("pyproject.toml"):
            try:
                payload = tomllib.loads(content)
            except tomllib.TOMLDecodeError:
                continue

            project = payload.get("project") or {}
            for requirement in project.get("dependencies") or []:
                parsed = _clean_requirement(str(requirement))
                if parsed:
                    name, version = parsed
                    signals.append(
                        DependencySignal("python", name, version, path)
                    )

    unique: dict[tuple[str, str, str], DependencySignal] = {}
    for signal in signals:
        key = (signal.ecosystem, signal.name.lower(), signal.source_path)
        unique[key] = signal
    return sorted(
        unique.values(),
        key=lambda item: (item.ecosystem, item.name.lower(), item.source_path),
    )
