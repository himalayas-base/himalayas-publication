# HiMaLAYAS Publication

![Python](https://img.shields.io/badge/python-3.8%2B-yellow)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](LICENSE)

> [!CAUTION]
> This repository is designed to work with `himalayas==0.0.7`. To ensure compatibility with these notebooks, please run:
>
> ```bash
> pip install himalayas==0.0.7
> ```

This repository contains publication datasets and workflows presented in **HiMaLAYAS: enrichment-based annotation of hierarchically clustered matrices**. HiMaLAYAS is a general framework that treats dendrogram-defined clusters as statistical units, evaluates annotation enrichment, and maps significant terms onto matrix regions.
The publication workflows include both biological and non-biological applications.

For a full description of HiMaLAYAS and its applications, see:
<br>
Horecka, I., and Röst, H. (2026)
<br>
_HiMaLAYAS: enrichment-based annotation of hierarchically clustered matrices_
<br>
_bioRxiv_. https://doi.org/10.1101/2026.xx.xx.xxxxxx
<br>
Under review at _Bioinformatics_.

## Documentation and Tutorial

- **Docs:** [himalayas-base.github.io/himalayas-docs](https://himalayas-base.github.io/himalayas-docs)
- **Tutorial Notebook Repository:** [github.com/himalayas-base/himalayas-docs](https://github.com/himalayas-base/himalayas-docs)
- **Core Package Repository:** [github.com/himalayas-base/himalayas](https://github.com/himalayas-base/himalayas)

## Repository Structure

This repository is organized around three publication notebooks and their supporting
data and figure exports.

### Notebooks

- `fig_1.ipynb`: Figure 1 workflow for a yeast GI profile similarity matrix (`data/yeast/gi_pcc_sampled.tsv`)
- `supp_fig_1.ipynb`: Supplementary Figure S1 workflow for a yeast GI score matrix (`data/yeast/gi_score_sampled.tsv`) with zoomed cluster panels
- `supp_fig_2.ipynb`: Supplementary Figure S2 workflow for a world recipe matrix (`data/interdisciplinary/WorldWideDishes_2024_June.xlsx`)

### Data

- `data/yeast/go_bp_name_to_orfs.json`: GO BP term-to-ORF mapping (1,095 terms)
- `data/yeast/gi_pcc_sampled.tsv`: sampled yeast GI profile similarity matrix (1053 x 1053)
- `data/yeast/gi_score_sampled.tsv`: sampled yeast GI score matrix (1142 x 1142)
- `data/yeast/yeast_essential_orfs.txt`: essential ORF labels used for row annotations
- `data/interdisciplinary/WorldWideDishes_2024_June.xlsx`: interdisciplinary recipe dataset used in Supplementary Figure S2

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
pip install "himalayas==0.0.7" jupyter numpy pandas scipy matplotlib openpyxl
```

### Step 4: Launch Jupyter

```bash
jupyter notebook
```

Open the notebook you want to run (`fig_1.ipynb`, `supp_fig_1.ipynb`, or `supp_fig_2.ipynb`).

## Figure Reproduction Guide

### Figure 1 (`fig_1.ipynb`)

- Input: yeast GI profile similarity matrix + GO BP annotations
- Analysis: hierarchical clustering (`ward`/`euclidean`), enrichment, Benjamini-Hochberg correction
- Significance filter: `qval <= 0.05`

### Supplementary Figure S1 (`supp_fig_1.ipynb`)

- Input: yeast GI score matrix + GO BP annotations + essential ORF labels
- Analysis: depth-dependent clustered enrichment with supplementary zoom views
- Significance filter: `qval <= 0.05`

### Supplementary Figure S2 (`supp_fig_2.ipynb`)

- Input: world recipe matrix derived from `WorldWideDishes_2024_June.xlsx`
- Analysis: token-cleaned ingredient matrix + country-level enrichment mapping
- Significance filter: `qval <= 0.05`

## Citation

### Primary citation

Horecka, I., and Röst, H. (2026)
<br>
_HiMaLAYAS: enrichment-based annotation of hierarchically clustered matrices_
<br>
_bioRxiv_. https://doi.org/10.1101/2026.xx.xx.xxxxxx
<br>
Under review at _Bioinformatics_.

### Software archive

HiMaLAYAS software for the manuscript.
<br>
Zenodo. https://doi.org/10.5281/zenodo.xxxxxxxx

## License

This repository is distributed under the [BSD 3-Clause License](LICENSE).
