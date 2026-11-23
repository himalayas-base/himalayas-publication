# Yeast CC and MF tutorial mappings

`go_cc_name_to_orfs.json` and `go_mf_name_to_orfs.json` map GO term names to sorted, unique systematic yeast ORFs, matching the existing BP JSON format. They are bundled inputs; tutorial execution needs no downloads.

Sources: the Gene Ontology Consortium's fixed **2024-11-03 archive**, using SGD annotations for *Saccharomyces cerevisiae* S288C (taxon 559292):

- [SGD GAF](https://release.geneontology.org/2024-11-03/annotations/sgd.gaf.gz). Header: GOC generation `2024-11-04T21:28`; embedded SGD source date `20241028`.
- [GO basic ontology](https://release.geneontology.org/2024-11-03/ontology/go-basic.obo). Header: `data-version: releases/2024-10-27`.
- [GAF 2.2 field definitions](https://geneontology.org/docs/go-annotation-file-gaf-format-2.2/).

Retrieved 23 November 2026. The archive label and file-header dates are recorded separately; they are not assumed identical. This archived snapshot was chosen for reproducibility, not as a claim to the latest annotations. The original BP reference mapping is unchanged; its upstream release/preparation is not reconstructed here. Category coverage and preparation therefore differ, and this example does not compare annotation quality or category performance.

Preparation (one-based GAF columns):

1. Keep database `SGD` (column 1), first taxon `taxon:559292` (13), and aspect `C` or `F` (9). Exclude relations containing `NOT` (4) and evidence `ND` (7); retain all other evidence codes, including IEA. Ignore annotation extensions (16) and product-form IDs (17).
2. Match a systematic ORF in symbol (3) or pipe-separated synonyms (11) using `Y[A-P][LR][0-9]{3}[CW](-[A-Z])?` or mitochondrial `Q[0-9]{4}`. Require exactly one unique match; skip missing/ambiguous cases. Never substitute common gene symbols. Assert each SGD ID resolves consistently.
3. Resolve GO IDs, including alternate IDs, against non-obsolete ontology terms. Require the matching CC/MF namespace; omit unknown/obsolete terms and the category roots (`GO:0005575`, `GO:0003674`). Use the ontology's primary term name as the JSON key; assert names are unique within each category.
4. Retain the term directly present in each accepted GAF row; do **not** propagate to ancestors or add memberships from extension fields. Deduplicate memberships and sort terms and ORFs. No upstream term-size cutoff or matrix restriction is applied. In the tutorial, `Annotations` intersects with the same 1,053 matrix genes and applies the same minimum of 2 and no maximum used for BP.

Of 81,390 CC/MF rows, 2,507 were excluded for NOT/ND and 3,099 for missing/ambiguous ORFs; 41,531 CC and 34,253 MF rows remained before deduplication. No additional rows were lost to database, taxon or ontology checks. Outputs:

| Mapping | Terms | Unique ORFs | Memberships | ORFs matching matrix |
| --- | ---: | ---: | ---: | ---: |
| CC | 776 | 5,535 | 20,598 | 948 |
| MF | 2,170 | 4,604 | 18,726 | 801 |

SHA256 checksums:

```text
sgd.gaf.gz  88e7ddbd756ce12b614cebe4cd5b19232d81e6d85e9a4c085be092aaefd7705c
go-basic.obo  385331279bd6d44666a6959a9a1719d9b3600c7801313d33745f043934d1912f
go_cc_name_to_orfs.json  536308f16874ad3ff9be3c1d2be39be9e021ef165f73b0e98fb17cfbc2bc1be2
go_mf_name_to_orfs.json  715dca6cf8645d2992e4c3161c5c99afab94a060bcddda451934c75a9c41f526
```
