from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


DEFAULT_MANIFEST_PATHS = (
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.toml",
    "go.mod",
)

MAX_FILES = 9
MAX_FILE_BYTES = 256_000


@dataclass(frozen=True)
class AcquiredFile:
    path: str
    content: str
    blob_sha: str | None
    source_url: str


def acquire_manifest_files(
    repository: str,
    ref: str,
    *,
    token: str | None = None,
    paths: tuple[str, ...] = DEFAULT_MANIFEST_PATHS,
) -> dict[str, AcquiredFile]:
    """Fetch a bounded set of known manifest paths; never clone the repository."""

    if "/" not in repository:
        raise ValueError("repository must be owner/name")
    if not ref:
        raise ValueError("ref must be version-pinned")

    selected = paths[:MAX_FILES]
    result: dict[str, AcquiredFile] = {}

    for path in selected:
        encoded_path = urllib.parse.quote(path, safe="/")
        encoded_ref = urllib.parse.quote(ref, safe="")
        url = (
            "https://api.github.com/repos/"
            + repository
            + "/contents/"
            + encoded_path
            + "?ref="
            + encoded_ref
        )
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "agent-underwriting-network/0.3",
                **({"Authorization": "Bearer " + token} if token else {}),
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise

        if payload.get("type") != "file":
            continue

        if int(payload.get("size") or 0) > MAX_FILE_BYTES:
            continue

        encoded = payload.get("content")
        if not encoded:
            continue

        raw = base64.b64decode(encoded, validate=False)
        if len(raw) > MAX_FILE_BYTES:
            continue

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue

        result[path] = AcquiredFile(
            path=path,
            content=text,
            blob_sha=payload.get("sha"),
            source_url=payload.get("html_url") or url,
        )

    return result
