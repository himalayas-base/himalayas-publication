"""File hashing helpers for input-data provenance tracking."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path | str, chunk_size: int = 1 << 20) -> str:
    """Return the hex-encoded SHA-256 digest of a file's contents."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
