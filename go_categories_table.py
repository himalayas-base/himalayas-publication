"""Generate the yeast GO-category comparison table without rerunning figure workflows."""

import hashlib
from html import escape
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

import matplotlib
import numpy as np
import pandas as pd
import scipy

import himalayas
from himalayas import Analysis, Annotations, Matrix


REFERENCE_CONFIG = dict(
    linkage_method="ward",
    linkage_metric="euclidean",
    linkage_threshold=16,
    optimal_ordering=True,
    min_cluster_size=30,
)
MIN_OVERLAP = 2
QVAL_CUTOFF = 0.05


def sha256(path):
    """Return a file's SHA256 checksum."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Run separate category analyses and export the selected terms and run metadata."""
    root = Path(__file__).resolve().parent
    inputs = {
        "BP": root / "data/go_bp_name_to_orfs.json",
        "CC": root / "data/go_categories/go_cc_name_to_orfs.json",
        "MF": root / "data/go_categories/go_mf_name_to_orfs.json",
    }
    matrix_path = root / "data/gi_pcc_sampled.tsv"
    matrix = Matrix(pd.read_csv(matrix_path, sep="\t", index_col=0))
    reference_memberships = None
    rows = []
    summary = {}
    for category, path in inputs.items():
        mapping = json.loads(path.read_text(encoding="utf-8"))
        annotations = Annotations(mapping, matrix, min_term_size=2, max_term_size=None)
        results = (
            Analysis(matrix, annotations)
            .cluster(**REFERENCE_CONFIG)
            .enrich(min_overlap=MIN_OVERLAP)
            .finalize(fdr_scope="global")
            .results
        )
        memberships = results.clusters.label_to_cluster
        if reference_memberships is None:
            reference_memberships = dict(memberships)
        elif memberships != reference_memberships:
            raise ValueError(f"{category} cluster memberships differ from BP")
        significant = results.df[results.df["qval"] <= QVAL_CUTOFF]
        top = (
            significant.sort_values(["qval", "pval", "term"])
            .drop_duplicates("cluster")
            .set_index("cluster")
        )
        for cid in results.clusters.unique_clusters:
            row = {
                "cluster": int(cid),
                "category": category,
                "term": None,
                "n": int(results.clusters.cluster_sizes[int(cid)]),
                "k": None,
                "K": None,
                "N": len(matrix.labels),
                "pval": None,
                "qval": None,
                "status": "no_significant_term",
            }
            if cid in top.index:
                selected = top.loc[cid]
                row.update({"term": selected["term"], "status": "significant"})
                for column in ["k", "K"]:
                    row[column] = int(selected[column])
                for column in ["pval", "qval"]:
                    row[column] = float(selected[column])
            rows.append(row)
        summary[category] = {
            "tested_pairs": len(results.df),
            "significant_pairs": len(significant),
            "retained_terms": len(annotations.terms),
        }

    table = pd.DataFrame(rows)
    output = root / "tables/go_categories"
    output.mkdir(parents=True, exist_ok=True)
    tsv_path = output / "go_categories.tsv"
    table.to_csv(tsv_path, sep="\t", index=False, na_rep="NA", float_format="%.17g")
    # Full term names and q-values stay together, with wrapping for long labels.
    html_rows = []
    for cid in sorted(table["cluster"].unique()):
        cells = [f'<th scope="row">{cid}</th>']
        for category in inputs:
            selected = table[(table["cluster"] == cid) & (table["category"] == category)].iloc[0]
            if selected["status"] == "significant":
                text = (
                    escape(selected["term"])
                    + f'<br><span class="q">q={selected["qval"]:.2e}</span>'
                )
            else:
                text = "No significant term"
            cells.append(f"<td>{text}</td>")
        html_rows.append("<tr>" + "".join(cells) + "</tr>")
    html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Yeast GO category annotations</title>
<style>
body {font-family: sans-serif; color: #222; margin: 2rem auto; padding: 0 1rem; max-width: 1100px;}
h1 {font-size: 1.5rem;} table {width: 100%; border-collapse: collapse; table-layout: fixed;}
th, td {padding: .75rem; border-bottom: 1px solid #ddd; text-align: left; vertical-align: top; overflow-wrap: anywhere;}
th:first-child {width: 4rem;} .q {font-size: .9em; color: #444; white-space: nowrap;}
</style></head><body><h1>Yeast GO category annotations</h1>
<p>Top significant term per cluster and category (q &le; 0.05). BH correction is applied separately within each category.</p>
<table><thead><tr><th scope="col">Cluster</th><th scope="col">BP</th><th scope="col">CC</th><th scope="col">MF</th></tr></thead><tbody>
'''+ "\n".join(html_rows) + "\n</tbody></table></body></html>\n"
    html_path = output / "go_categories.html"
    html_path.write_text(html, encoding="utf-8")

    source = Path(himalayas.__file__).resolve().parent
    distribution = importlib.metadata.distribution("himalayas")
    origin = distribution.read_text("direct_url.json")
    metadata = {
        "parameters": {
            "clustering": REFERENCE_CONFIG,
            "background": "matrix row labels",
            "min_overlap": MIN_OVERLAP,
            "min_term_size": 2,
            "max_term_size": None,
            "fdr_scope": "global within each category separately",
            "qval_cutoff": QVAL_CUTOFF,
            "top_term_order": ["qval", "pval", "term"],
        },
        "environment": {
            "python": platform.python_version(),
            "executable": sys.executable,
            "himalayas": himalayas.__version__,
            "package_path": str(source),
            "install_origin": json.loads(origin) if origin else None,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "package_source_sha256": {
            str(path.relative_to(source)): sha256(path) for path in sorted(source.rglob("*.py"))
        },
        "inputs_sha256": {
            str(path.relative_to(root)): sha256(path)
            for path in [matrix_path, *inputs.values(),
                         root / "data/go_categories/go_cc_mf_provenance.md",
                         root / "data/go_categories/prepare_mappings.py"]
        },
        "generator_sha256": sha256(Path(__file__)),
        "category_summary": summary,
        "cluster_memberships": {
            str(cid): sorted(
                label for label, cluster in reference_memberships.items() if cluster == cid
            )
            for cid in sorted(set(reference_memberships.values()))
        },
        "outputs_sha256": {path.name: sha256(path) for path in [tsv_path, html_path]},
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))
    print(
        f"Saved {len(table)} entries for {len(metadata['cluster_memberships'])} clusters to {output}"
    )


if __name__ == "__main__":
    main()
