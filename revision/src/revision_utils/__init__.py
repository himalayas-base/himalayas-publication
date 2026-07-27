"""Shared helpers for HiMaLAYAS revision analyses."""

from .environment import (
    git_info,
    himalayas_diagnostics,
    package_versions,
    python_info,
)
from .hashing import sha256_file
from .manifest import read_manifest, utc_timestamp, write_manifest
from .paths import find_repo_root, revision_layout
from .reproduction import (
    build_run_copy,
    csv_content_matches,
    csv_row_count,
    execute_notebook,
    has_cell_error,
    image_dimensions,
    load_root_notebook,
    pixel_mean_abs_diff,
    stream_text,
)
from .seeds import DEFAULT_RANDOM_SEED
from .source_verify import (
    activate_pinned_source,
    diff_vendored_against_tag,
    extract_tagged_source,
    repo_has_tag,
)
from .stability import cluster_term_sets, jaccard, match_clusters_by_membership, symmetric_noise

__all__ = [
    "DEFAULT_RANDOM_SEED",
    "find_repo_root",
    "revision_layout",
    "sha256_file",
    "python_info",
    "package_versions",
    "git_info",
    "himalayas_diagnostics",
    "utc_timestamp",
    "write_manifest",
    "read_manifest",
    "repo_has_tag",
    "diff_vendored_against_tag",
    "extract_tagged_source",
    "activate_pinned_source",
    "load_root_notebook",
    "build_run_copy",
    "execute_notebook",
    "stream_text",
    "has_cell_error",
    "image_dimensions",
    "pixel_mean_abs_diff",
    "csv_row_count",
    "csv_content_matches",
    "symmetric_noise",
    "jaccard",
    "match_clusters_by_membership",
    "cluster_term_sets",
]
