"""Manifest read/write helpers so every revision notebook shares one JSON convention."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_manifest(data: dict, path: Path | str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)
        fh.write("\n")
    return path


def read_manifest(path: Path | str) -> dict:
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)
