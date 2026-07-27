"""Random seed policy shared across revision notebooks.

Submitted baseline analyses (root `fig_1`/`supp_fig_1`/`supp_fig_2` notebooks)
use Ward/Euclidean hierarchical clustering with `optimal_ordering=True`, which
is deterministic and takes no random seed. Revision notebooks that introduce
randomness (noise perturbation, permutation nulls, cluster-label
randomization) must seed every stochastic step from `DEFAULT_RANDOM_SEED`
unless a notebook-specific seed is documented in that notebook's own header,
and must record the seed actually used in that notebook's manifest.
"""

DEFAULT_RANDOM_SEED = 0
