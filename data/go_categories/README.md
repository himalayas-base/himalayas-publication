# GO category table inputs

The CC and MF JSON files and `go_cc_mf_provenance.md` are exact copies of the accepted inputs in the sibling documentation repository. Their source headers, filters, identifiers and checksums are unchanged. The table uses the existing `data/gi_pcc_sampled.tsv` and `data/go_bp_name_to_orfs.json`; the historical BP mapping is preserved.

The accepted comparison is the final section, **Annotate the same clusters with other GO categories**, in the [basic quickstart](../../../himalayas-docs/notebooks/quickstart.ipynb#Annotate-the-same-clusters-with-other-GO-categories) in the sibling development checkout. This relative link requires that checkout; the accepted additions are not yet hosted on the public branch.

`prepare_mappings.py` is the exact deterministic preparation script archived with the accepted tutorial. Table generation uses the bundled JSON files and requires no downloads. To reproduce preparation separately, download the fixed archive inputs and run from the publication repository root:

```bash
mkdir -p /tmp/himalayas-go-source /tmp/himalayas-go-prepared
curl -fL https://release.geneontology.org/2024-11-03/ontology/go-basic.obo -o /tmp/himalayas-go-source/go-basic.obo
curl -fL https://release.geneontology.org/2024-11-03/annotations/sgd.gaf.gz -o /tmp/himalayas-go-source/sgd.gaf.gz
python data/go_categories/prepare_mappings.py /tmp/himalayas-go-source /tmp/himalayas-go-prepared
```

Compare the reported input/output SHA256 values with `go_cc_mf_provenance.md`. The source GAF/ontology are reproducible archive downloads rather than additional bundled datasets. BP and CC/MF have different historical preparation and coverage; the table provides complementary annotations, not a category-performance comparison.
