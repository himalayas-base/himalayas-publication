"""Prepare name-to-ORF CC/MF mappings from the fixed GO archive inputs."""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

source = Path(sys.argv[1])
output = Path(sys.argv[2])
output.mkdir(parents=True, exist_ok=True)
terms = {}
for block in (source / 'go-basic.obo').read_text().split('\n[Term]\n')[1:]:
    fields = collections.defaultdict(list)
    for line in block.split('\n\n', 1)[0].splitlines():
        if ': ' in line:
            key, value = line.split(': ', 1)
            fields[key].append(value)
    if 'id' not in fields or 'name' not in fields or fields.get('is_obsolete') == ['true']:
        continue
    term = {'id': fields['id'][0], 'name': fields['name'][0], 'namespace': fields['namespace'][0]}
    for go_id in [term['id'], *fields.get('alt_id', [])]:
        assert go_id not in terms
        terms[go_id] = term

mappings = {'C': collections.defaultdict(set), 'F': collections.defaultdict(set)}
stats = collections.Counter()
orf_pattern = re.compile(r'(?:Y[A-P][LR][0-9]{3}[CW](?:-[A-Z])?|Q[0-9]{4})')
roots = {'GO:0005575', 'GO:0003674'}
namespaces = {'C': 'cellular_component', 'F': 'molecular_function'}
id_to_orf = {}
with gzip.open(source / 'sgd.gaf.gz', 'rt') as handle:
    for line in handle:
        if line.startswith('!'):
            continue
        row = line.rstrip('\n').split('\t')
        assert len(row) == 17
        if row[8] not in mappings:
            continue
        stats['CC_MF_rows'] += 1
        if row[0] != 'SGD' or row[12].split('|')[0] != 'taxon:559292':
            stats['wrong_database_or_taxon'] += 1
            continue
        if 'NOT' in row[3].split('|') or row[6] == 'ND':
            stats['negative_or_no_data'] += 1
            continue
        term = terms.get(row[4])
        if term is None or term['id'] in roots:
            stats['obsolete_unknown_or_root'] += 1
            continue
        assert term['namespace'] == namespaces[row[8]]
        # Use systematic ORFs only; never substitute a common gene symbol.
        identifiers = {value for value in [row[2], *row[10].split('|')]
                       if orf_pattern.fullmatch(value)}
        if len(identifiers) != 1:
            stats['missing_or_ambiguous_ORF'] += 1
            continue
        orf = identifiers.pop()
        assert id_to_orf.setdefault(row[1], orf) == orf
        mappings[row[8]][term['id']].add(orf)
        stats['retained_rows_' + row[8]] += 1

report = {'source_sha256': {}, 'filter_counts': dict(stats), 'outputs': {}}
for name in ['go-basic.obo', 'sgd.gaf.gz']:
    report['source_sha256'][name] = hashlib.sha256((source / name).read_bytes()).hexdigest()
for aspect, mapping in mappings.items():
    names = [terms[go_id]['name'] for go_id in mapping]
    assert len(names) == len(set(names)), 'Distinct GO IDs share a name'
    result = dict(sorted((terms[go_id]['name'], sorted(orfs)) for go_id, orfs in mapping.items()))
    name = f'go_{"cc" if aspect == "C" else "mf"}_name_to_orfs.json'
    path = output / name
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    report['outputs'][name] = {
        'terms': len(result), 'unique_orfs': len(set().union(*mapping.values())),
        'memberships': sum(map(len, result.values())),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    }
print(json.dumps(report, indent=2))
