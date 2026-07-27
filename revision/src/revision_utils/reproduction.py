"""Execute isolated copies of the submitted root notebooks under a controlled
HiMaLAYAS import path, without ever modifying the root .ipynb files on disk.

The root notebooks each define `PNG_DIR = Path("png") / "<name>"` in one early
cell and write every figure relative to it; patching that single assignment
redirects all downstream `.save(...)` calls without touching any other cell.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Optional

import nbformat
from nbclient.client import NotebookClient

PNG_DIR_PATTERN = re.compile(r'PNG_DIR\s*=\s*Path\(\s*["\']png["\']\s*\)\s*/\s*["\'][\w\-]+["\']')

# Variable names every root notebook binds after its clustering+enrichment cell.
EXPORT_TARGETS = ("results", "results_sig", "cluster_labels")


def load_root_notebook(path: Path) -> nbformat.NotebookNode:
    """Read-only load of a submitted root notebook. Never writes back to `path`."""
    return nbformat.read(path, as_version=4)


def build_run_copy(
    nb: nbformat.NotebookNode,
    *,
    figure_dir: Path,
    export_dir: Path,
    sys_path_prepend: Optional[Path] = None,
) -> nbformat.NotebookNode:
    """Return an in-memory copy of `nb` prepared for isolated execution:
    a bootstrap cell inserted first (pins sys.path if `sys_path_prepend` is
    given, forces a headless matplotlib backend), the PNG_DIR cell rewritten
    to `figure_dir`, and an export cell appended that writes
    results/results_sig/cluster_labels to CSV under `export_dir`.
    """
    run_nb = copy.deepcopy(nb)

    bootstrap_lines = []
    if sys_path_prepend is not None:
        bootstrap_lines += ["import sys", f"sys.path.insert(0, {str(sys_path_prepend)!r})"]
    bootstrap_lines += ["import matplotlib", "matplotlib.use('Agg')"]
    run_nb.cells.insert(0, nbformat.v4.new_code_cell("\n".join(bootstrap_lines)))

    patched = 0
    for cell in run_nb.cells:
        if cell.cell_type != "code":
            continue
        if PNG_DIR_PATTERN.search(cell.source):
            cell.source = PNG_DIR_PATTERN.sub(f"PNG_DIR = Path({str(figure_dir)!r})", cell.source)
            patched += 1
    if patched == 0:
        raise RuntimeError("Could not find a PNG_DIR assignment cell to patch")

    export_lines = [
        "from pathlib import Path as _Path",
        f"_export_dir = _Path({str(export_dir)!r})",
        "_export_dir.mkdir(parents=True, exist_ok=True)",
    ]
    for name in EXPORT_TARGETS:
        export_lines.append(
            f"{name}.to_csv(_export_dir / '{name}.csv', index=False) "
            f"if hasattr({name}, 'to_csv') else "
            f"{name}.df.to_csv(_export_dir / '{name}.csv', index=False)"
        )
    export_lines.append("print(f'Comparison export written to {_export_dir}')")
    run_nb.cells.append(nbformat.v4.new_code_cell("\n".join(export_lines)))
    return run_nb


def execute_notebook(nb: nbformat.NotebookNode, *, cwd: Path, timeout: int = 900):
    """Execute `nb` in place via nbclient with the kernel CWD set to `cwd`.
    Returns (executed_nb, error_str_or_None); never raises."""
    client = NotebookClient(nb, timeout=timeout, resources={"metadata": {"path": str(cwd)}})
    try:
        client.execute()
        return nb, None
    except Exception as exc:  # noqa: BLE001 -- surfaced to caller, not swallowed
        return nb, f"{type(exc).__name__}: {exc}"


def stream_text(nb: nbformat.NotebookNode) -> str:
    """Concatenate all stdout/stderr stream output across a notebook's cells."""
    chunks = []
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "stream":
                chunks.append("".join(out.get("text", [])))
    return "\n".join(chunks)


def has_cell_error(nb: nbformat.NotebookNode) -> bool:
    return any(
        out.get("output_type") == "error"
        for cell in nb.cells
        if cell.cell_type == "code"
        for out in cell.get("outputs", [])
    )


def image_dimensions(path: Path) -> Optional[tuple]:
    import matplotlib.image as mpimg

    if not Path(path).exists():
        return None
    arr = mpimg.imread(path)
    return (int(arr.shape[0]), int(arr.shape[1]))


def pixel_mean_abs_diff(path_a: Path, path_b: Path) -> Optional[float]:
    import matplotlib.image as mpimg
    import numpy as np

    if not (Path(path_a).exists() and Path(path_b).exists()):
        return None
    a = mpimg.imread(path_a)
    b = mpimg.imread(path_b)
    if a.shape != b.shape:
        return None
    return float(np.abs(a.astype(float) - b.astype(float)).mean())


def csv_row_count(path: Path) -> Optional[int]:
    import pandas as pd

    if not Path(path).exists():
        return None
    return len(pd.read_csv(path))


def csv_content_matches(path_a: Path, path_b: Path) -> Optional[bool]:
    import pandas as pd

    if not (Path(path_a).exists() and Path(path_b).exists()):
        return None
    return pd.read_csv(path_a).equals(pd.read_csv(path_b))
