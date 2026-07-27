"""Repo-root and output-directory resolution shared across revision notebooks."""

from __future__ import annotations

from pathlib import Path

REQUIRED_MARKERS = ("himalayas_src", "data", ".git", "revision")


def find_repo_root(start: Path | str | None = None) -> Path:
    """Walk upward from `start` (default: current working directory) until a
    directory containing all `REQUIRED_MARKERS` is found. This lets notebooks
    resolve the repo root regardless of whether Jupyter's working directory is
    the notebook's own folder or the repo root itself.
    """
    current = Path(start if start is not None else Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if all((candidate / marker).exists() for marker in REQUIRED_MARKERS):
            return candidate
    raise RuntimeError(
        f"Could not locate himalayas-publication repo root above {current} "
        f"(expected to find: {', '.join(REQUIRED_MARKERS)})"
    )


def revision_layout(repo_root: Path) -> dict[str, Path]:
    """Return the standard revision/ subdirectory layout given a resolved repo root."""
    revision_dir = repo_root / "revision"
    outputs_dir = revision_dir / "outputs"
    return {
        "repo_root": repo_root,
        "data_dir": repo_root / "data",
        "revision_dir": revision_dir,
        "outputs_dir": outputs_dir,
        "manifests_dir": outputs_dir / "manifests",
        "tables_dir": outputs_dir / "tables",
        "figures_dir": outputs_dir / "figures",
        "logs_dir": outputs_dir / "logs",
        "executed_notebooks_dir": outputs_dir / "executed_notebooks",
        "scratch_dir": revision_dir / "scratch",
    }
