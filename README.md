# HiMaLAYAS Publication

![Python](https://img.shields.io/badge/python-3.8%2B-yellow)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](LICENSE)

> [!CAUTION]
> This repository is designed to work with `himalayas==0.0.16`. To ensure compatibility with these notebooks, please run:
>
> ```bash
> pip install himalayas==0.0.16
> ```

This repository contains publication datasets and workflows presented in **HiMaLAYAS: enrichment-based annotation and visualization of hierarchically clustered matrices**. HiMaLAYAS treats dendrogram-defined clusters as statistical units, tests categorical annotations for enrichment, controls multiple testing, and renders significant annotations alongside clusters.
The publication workflows include the yeast genetic interaction profile similarity matrix application, robustness and null analyses, related-tool comparison, and a non-biological country-sector input-output matrix example.

For a full description of HiMaLAYAS and its applications, see:
<br>
Horecka, I., and Röst, H. (2026)
<br>
_HiMaLAYAS: enrichment-based annotation and visualization of hierarchically clustered matrices_
<br>
_bioRxiv_. [https://www.biorxiv.org/content/10.64898/2026.02.11.705303v3](https://www.biorxiv.org/content/10.64898/2026.02.11.705303v3)
<br>
Submitted to _Bioinformatics Advances_.

## Documentation and Tutorials

- **Docs:** [himalayas-base.github.io/himalayas-docs](https://himalayas-base.github.io/himalayas-docs)
- **Tutorial Notebook Repository:** [github.com/himalayas-base/himalayas-docs](https://github.com/himalayas-base/himalayas-docs)
- **Core Package Repository:** [github.com/himalayas-base/himalayas](https://github.com/himalayas-base/himalayas)

## Repository Structure

This repository is organized around six publication notebooks and their supporting
data and figure exports.

### Notebooks

- `fig_1.ipynb`: Figure 1 - HiMaLAYAS workflow and yeast genetic interaction profile similarity matrix application (`data/gi_pcc_sampled.tsv`)
- `fig_2.ipynb`: Figure 2 - robustness and null analysis of GO Biological Process annotations in the yeast genetic interaction profile similarity matrix (`data/gi_pcc_sampled.tsv`)
- `supp_fig_1.ipynb`: Supplementary Figure S1 - annotated matrix and condensed hierarchy views of the full yeast matrix and cluster 3 zoom, with post hoc row data tracks for essentiality and single-mutant fitness (`data/gi_pcc_sampled.tsv`)
- `supp_fig_2.ipynb`: Supplementary Figure S2 - matrix-perturbation robustness of the seven headline Gene Ontology Biological Process annotations from the Fig. 1B parent-level reference analysis (`data/gi_pcc_sampled.tsv`)
- `supp_fig_3.ipynb`: Supplementary Figure S3 - related-tool capability comparison from a curated capability table; no external dataset and no competing tool is run
- `supp_fig_4.ipynb`: Supplementary Figure S4 - WIOD non-biological country-sector input-output matrix portability example (downloaded at runtime)

### Data

- `data/go_bp_name_to_orfs.json`: GO BP term-to-ORF mapping (1,095 terms)
- `data/gi_pcc_sampled.tsv`: sampled yeast genetic interaction profile similarity matrix (1053 x 1053)
- `data/yeast_essential_orfs.txt`: essential ORF labels used for the Supplementary Figure S1 row rail
- `data/strain_ids_and_single_mutant_fitness.csv`: Costanzo et al. (2016) single-mutant fitness used for the Supplementary Figure S1 row rail

Supplementary Figure S4 downloads the WIOD 2016 release archive (`WIOTS_in_R.zip`, ~642 MB) at runtime into `scratch/supp_fig_4/`. It is not stored in this repository.

## Installation

To run the publication notebooks locally:

### Step 1: Clone This Repository

```bash
git clone https://github.com/himalayas-base/himalayas-publication.git
cd himalayas-publication
```

### Step 2: Create and Activate a Virtual Environment

- **Windows**

```cmd
python -m venv himalayas-env
himalayas-env\Scripts\activate
```

- **macOS/Linux**

```bash
python3 -m venv himalayas-env
source himalayas-env/bin/activate
```

### Step 3: Install Notebook Dependencies

```bash
python -m pip install --upgrade pip
pip install "himalayas==0.0.16" jupyter numpy pandas scipy matplotlib pyreadr
```

### Step 4: Launch Jupyter

```bash
jupyter notebook
```

Open the notebook you want to run (`fig_1.ipynb`, `fig_2.ipynb`, or `supp_fig_1.ipynb` through `supp_fig_4.ipynb`).

## Figure Reproduction Guide

### Figure 1 (`fig_1.ipynb`)

- Input: yeast genetic interaction profile similarity matrix + GO BP annotations
- Analysis: workflow schematic plus hierarchical clustering (`ward`/`euclidean`, `linkage_threshold=16`, `min_cluster_size=30`), enrichment, global Benjamini-Hochberg correction, and cluster 3 zoom
- Significance filter: `qval <= 0.05`

### Figure 2 (`fig_2.ipynb`)

- Input: yeast genetic interaction profile similarity matrix + GO BP annotations
- Analysis: dendrogram distance-threshold and minimum-cluster-size sweeps, plus same-size random clusters with annotations fixed and annotation-label permutations with clusters fixed
- Significance filter: `qval <= 0.05`

### Supplementary Figure S1 (`supp_fig_1.ipynb`)

- Input: yeast genetic interaction profile similarity matrix + GO BP annotations + essential ORF labels + single-mutant fitness
- Analysis: the Figure 1 reference clustering and cluster 3 zoom, rendered as annotated matrix and condensed hierarchy views with post hoc row data tracks for essentiality and log2 fitness
- Significance filter: `qval <= 0.05`

### Supplementary Figure S2 (`supp_fig_2.ipynb`)

- Input: yeast genetic interaction profile similarity matrix + GO BP annotations
- Analysis: matrix perturbation with symmetric zero-mean Gaussian noise, reclustering, enrichment testing, and recovery summaries for the seven headline GO BP annotations from the Fig. 1B parent-level reference analysis
- Significance filter: `qval <= 0.05`

### Supplementary Figure S3 (`supp_fig_3.ipynb`)

- Input: curated capability table (no external dataset)
- Analysis: qualitative capability comparison against related tools and workflows; no competing tool is installed, run, timed, or scored
- Significance filter: not applicable

### Supplementary Figure S4 (`supp_fig_4.ipynb`)

- Input: WIOD 2016 release, 2014 country-sector input-output table (downloaded at runtime)
- Analysis: log1p-scaled intermediate-flow matrix, clustered with `linkage_threshold="auto"` and `min_cluster_size=20`, annotated with native WIOD country metadata
- Significance filter: `qval <= 0.05`

## Citation

### Primary citation

Horecka, I., and Röst, H. (2026)
<br>
_HiMaLAYAS: enrichment-based annotation and visualization of hierarchically clustered matrices_
<br>
_bioRxiv_. [https://www.biorxiv.org/content/10.64898/2026.02.11.705303v3](https://www.biorxiv.org/content/10.64898/2026.02.11.705303v3)
<br>
Submitted to _Bioinformatics Advances_.

### Software archive

HiMaLAYAS software archive.
<br>
Zenodo. [https://doi.org/10.5281/zenodo.18610373](https://doi.org/10.5281/zenodo.18610373)

## License

This repository is distributed under the [BSD 3-Clause License](LICENSE).
