"""Verify a vendored HiMaLAYAS source copy against a specific git tag in the
upstream package repository, and extract a pristine copy of that tag.

All operations against the upstream repo are read-only (`git show`, `git
ls-tree`, `git archive`); nothing here ever checks out or mutates its working
tree. This exists because a version *string* (e.g. `__version__ = "0.0.15"`)
is not proof that a vendored copy matches what was actually tagged/released --
see `diff_vendored_against_tag`.
"""

from __future__ import annotations

import io
import subprocess
import tarfile
from pathlib import Path


def _run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def repo_has_tag(repo: Path, tag: str) -> bool:
    try:
        out = _run_git(repo, "tag", "-l", tag)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return out.strip() == tag


def tagged_file_list(repo: Path, tag: str, subpath: str) -> list[str]:
    out = _run_git(repo, "ls-tree", "-r", "--name-only", tag, "--", subpath)
    return sorted(line for line in out.splitlines() if line)


def tagged_file_text(repo: Path, tag: str, file_path: str) -> str:
    return _run_git(repo, "show", f"{tag}:{file_path}")


def diff_vendored_against_tag(
    repo: Path,
    tag: str,
    vendored_root: Path,
    tag_subpath: str = "src/himalayas",
    vendored_subpath: str = "himalayas",
) -> dict:
    """Compare every file under `vendored_root/vendored_subpath` against the
    same relative path at `tag` in `repo`, byte-for-byte."""
    tagged_files = tagged_file_list(repo, tag, tag_subpath)
    rel_files = [f[len(tag_subpath) + 1 :] for f in tagged_files]

    per_file = []
    for rel in rel_files:
        vendored_path = vendored_root / vendored_subpath / rel
        tag_text = tagged_file_text(repo, tag, f"{tag_subpath}/{rel}")
        vendored_exists = vendored_path.exists()
        vendored_text = vendored_path.read_text() if vendored_exists else None
        per_file.append(
            {
                "path": rel,
                "vendored_exists": vendored_exists,
                "matches_tag": vendored_exists and vendored_text == tag_text,
            }
        )

    mismatched = [r["path"] for r in per_file if not r["matches_tag"]]
    return {
        "tag": tag,
        "tag_subpath": tag_subpath,
        "vendored_root": str(vendored_root),
        "files_compared": len(per_file),
        "mismatched_files": mismatched,
        "matches_tag_exactly": len(mismatched) == 0,
        "per_file": per_file,
    }


def extract_tagged_source(repo: Path, tag: str, dest_dir: Path, subpath: str = "src") -> Path:
    """Extract `subpath` at `tag` from `repo` into `dest_dir` via `git archive`
    (read-only against `repo`; writes only under `dest_dir`). Returns the path
    to prepend to `sys.path` to import the resulting package."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["git", "-C", str(repo), "archive", tag, subpath],
        capture_output=True,
        check=True,
    )
    with tarfile.open(fileobj=io.BytesIO(proc.stdout)) as tar:
        tar.extractall(dest_dir, filter="data")
    return dest_dir / subpath


def activate_pinned_source(repo_root: Path, dest_dir: Path, tag: str = "v0.0.15") -> dict:
    """Extract the verified `tag` source from the sibling HiMaLAYAS dev repo (located
    via the active editable install) and activate it for THIS kernel: prepend it to
    `sys.path` and force a fresh `import himalayas` bound to that path, discarding any
    `himalayas.*` modules already cached in `sys.modules` from a different location.

    This is the pattern `01_reproduce_submitted_figures.ipynb` established: the active
    editable install may be an unreleased dev version, so any notebook computing results
    that will be reported as "the submitted baseline" must run under the verified tag,
    not whatever happens to be importable by default.

    Returns a diagnostics dict recording exactly what was activated, suitable for
    inclusion in the calling notebook's manifest. Raises RuntimeError if no sibling repo
    with `tag` can be found -- callers should treat that as a BLOCKED condition, not
    silently fall back to the active install.
    """
    import sys

    from .environment import himalayas_diagnostics

    diag_before = himalayas_diagnostics(repo_root)
    sibling_repo = diag_before["editable_project_location"]
    if sibling_repo is None:
        raise RuntimeError(
            "No editable HiMaLAYAS install detected in the active kernel; cannot locate "
            f"a sibling dev repo to extract tag {tag!r} from. Cannot activate a verified "
            "pinned source on this machine."
        )
    sibling_repo = Path(sibling_repo)
    if not repo_has_tag(sibling_repo, tag):
        raise RuntimeError(f"Sibling repo {sibling_repo} does not have tag {tag!r}.")

    pinned_src_dir = extract_tagged_source(sibling_repo, tag, dest_dir, subpath="src")

    if str(pinned_src_dir) not in sys.path:
        sys.path.insert(0, str(pinned_src_dir))
    # Discard any himalayas.* modules already cached from a different sys.path entry
    # (e.g. himalayas_diagnostics() above imports himalayas as a side effect) so the
    # re-import below is forced to resolve via the freshly inserted path.
    for mod_name in list(sys.modules):
        if mod_name == "himalayas" or mod_name.startswith("himalayas."):
            del sys.modules[mod_name]
    import himalayas as _himalayas

    activated_version = _himalayas.__version__
    return {
        "requested_tag": tag,
        "sibling_repo": str(sibling_repo),
        "pinned_src_dir": str(pinned_src_dir),
        "activated_version": activated_version,
        "activated_file": str(Path(_himalayas.__file__).resolve()),
        "matches_requested_tag": activated_version == tag.lstrip("v"),
    }
