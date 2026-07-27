"""Interpreter, dependency, git, and HiMaLAYAS source/version identification.

The critical job of this module is `himalayas_diagnostics`: it identifies which
HiMaLAYAS source tree and version the running kernel actually imports, since
that may differ from both the version pinned in this repo's README and the
vendored reference copy under `himalayas_src/`.
"""

from __future__ import annotations

import json
import platform
import re
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname


def python_info() -> dict:
    return {
        "version": sys.version,
        "version_info": list(sys.version_info),
        "executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
    }


def package_versions(names: list[str]) -> dict[str, str]:
    """Look up installed distribution versions by name; missing packages are
    reported rather than raising, since notebooks may check optional deps."""
    versions = {}
    for name in names:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "not installed"
    return versions


def git_info(repo_path: Path | str) -> dict:
    """Best-effort git identity for a repo path: branch, commit, describe, and
    dirty-file list. Returns {"is_git_repo": False} if `repo_path` isn't a git
    work tree or git is unavailable."""
    repo_path = Path(repo_path)

    def _run(*args: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), *args],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    if _run("rev-parse", "--is-inside-work-tree") != "true":
        return {"is_git_repo": False}

    dirty_files = _run("status", "--porcelain") or ""
    return {
        "is_git_repo": True,
        "branch": _run("rev-parse", "--abbrev-ref", "HEAD"),
        "commit": _run("rev-parse", "HEAD"),
        "describe": _run("describe", "--tags", "--always"),
        "is_dirty": bool(dirty_files),
        "dirty_files": dirty_files.splitlines() if dirty_files else [],
    }


def _file_url_to_path(url: str) -> Path | None:
    if not url.startswith("file://"):
        return None
    parsed = urlparse(url)
    return Path(url2pathname(parsed.path))


def _vendored_version(repo_root: Path) -> str | None:
    init_path = repo_root / "himalayas_src" / "himalayas" / "__init__.py"
    if not init_path.exists():
        return None
    match = re.search(r"__version__\s*=\s*[\"']([^\"']+)[\"']", init_path.read_text())
    return match.group(1) if match else None


def _pinned_version(repo_root: Path) -> str | None:
    readme_path = repo_root / "README.md"
    if not readme_path.exists():
        return None
    match = re.search(r"himalayas==([0-9][\w.\-]*)", readme_path.read_text())
    return match.group(1) if match else None


def himalayas_diagnostics(repo_root: Path) -> dict:
    """Identify the HiMaLAYAS source actually imported by this kernel, and
    reconcile it against the vendored copy and the README-pinned version."""
    import himalayas  # local import: this module has no hard dependency on it

    dist = metadata.distribution("himalayas")
    direct_url_raw = dist.read_text("direct_url.json")
    direct_url = json.loads(direct_url_raw) if direct_url_raw else {}
    is_editable = bool(direct_url.get("dir_info", {}).get("editable"))
    editable_location = (
        _file_url_to_path(direct_url["url"]) if is_editable and "url" in direct_url else None
    )

    info = {
        "imported_version": himalayas.__version__,
        "imported_file": str(Path(himalayas.__file__).resolve()),
        "is_editable_install": is_editable,
        "editable_project_location": str(editable_location) if editable_location else None,
        "editable_git": git_info(editable_location) if editable_location else None,
        "vendored_copy_path": str(repo_root / "himalayas_src" / "himalayas" / "__init__.py"),
        "vendored_copy_version": _vendored_version(repo_root),
        "readme_pinned_version": _pinned_version(repo_root),
    }
    info["matches_readme_pinned_version"] = (
        info["imported_version"] == info["readme_pinned_version"]
    )
    return info
