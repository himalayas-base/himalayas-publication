"""Generic stability-comparison helpers shared by robustness/sensitivity/null
notebooks (10, 11, 20, 21): symmetric noise generation and gene-membership-based
cluster matching across independently computed clusterings.
"""

from __future__ import annotations

import numpy as np


def symmetric_noise(shape: tuple, scale: float, rng: np.random.Generator) -> np.ndarray:
    """Return an (n, n) symmetric noise matrix with per-entry std ~= `scale`.

    Two independent N(0,1) matrices are averaged and rescaled by 1/sqrt(2) so the
    symmetrized result keeps unit variance before applying `scale`, then mirrored
    so noise[i, j] == noise[j, i] -- perturbation does not introduce new asymmetry
    beyond whatever the input matrix already has.
    """
    raw = rng.normal(0.0, 1.0, size=shape)
    return scale * (raw + raw.T) / np.sqrt(2.0)


def jaccard(a: set, b: set) -> float:
    """Jaccard similarity of two sets; defined as 1.0 when both are empty."""
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def match_clusters_by_membership(
    reference_cluster_to_labels: dict,
    other_cluster_to_labels: dict,
) -> dict:
    """For each reference cluster id, find the `other` clustering's cluster id with
    maximum gene-membership Jaccard overlap. Cluster ids are not assumed to be
    comparable across independent clusterings -- only gene membership is.

    Returns {ref_cluster_id: {"matched_cluster_id": ..., "membership_jaccard": ...}}.
    """
    matches = {}
    for ref_cid, ref_genes in reference_cluster_to_labels.items():
        ref_set = set(ref_genes)
        best_cid, best_jaccard = None, -1.0
        for other_cid, other_genes in other_cluster_to_labels.items():
            j = jaccard(ref_set, set(other_genes))
            if j > best_jaccard:
                best_cid, best_jaccard = other_cid, j
        matches[ref_cid] = {"matched_cluster_id": best_cid, "membership_jaccard": best_jaccard}
    return matches


def cluster_term_sets(results_sig_df) -> dict:
    """cluster_id -> set of significant term names, from a HiMaLAYAS `results_sig.df`
    (a pandas DataFrame with "cluster" and "term" columns). Returns {} for an empty
    frame rather than raising, since a noise/threshold sweep can legitimately produce
    zero significant rows at an extreme setting.
    """
    if results_sig_df.empty:
        return {}
    return {int(cid): set(sub["term"]) for cid, sub in results_sig_df.groupby("cluster")}
