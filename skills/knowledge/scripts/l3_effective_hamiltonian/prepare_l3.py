#!/usr/bin/env python3
"""Bounded L3 input preparation; standard library, no calculations. See README.md."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
import json
import math
import os

from study_contract import (require, number, identifier, digest, load,
                            write_package, split_ids, source, json_bytes, records)
from fit_limits import check_candidate_width, check_retained_count, limits


def label(text):
    return re.sub(r'[_.-]', '', text).lower()


def tokens(line):
    return re.split(r'[#!;]', line, maxsplit=1)[0].split()


@dataclass
class Entry:
    key: str
    block: bool
    raw: str
    body: list[str]
    origin: str


class FDF:
    """Ordinary includes only, relative to PASP working directory, first match wins.

    Reject redirects/quoted tokens rather than approximating the full FDF reader.
    Preserve raw records (including blank mode separators) when flattening includes.
    """
    def __init__(self, path):
        self.cwd = Path(path).resolve().parent
        self.hashes = {}
        self.entries = self.read(Path(path).resolve(), ())

    def read(self, path, stack):
        require(path not in stack and len(stack) < 32, 'include cycle/depth limit')
        data = path.read_bytes()
        self.hashes[str(path)] = digest(data)
        return self.parse(data.decode("utf-8"), path, stack)

    def parse(self, text, path, stack):
        lines = [line + "\n" for line in text.splitlines()]
        result, i = [], 0
        while i < len(lines):
            start = i
            t = tokens(lines[i])
            origin = f'{path}:{i + 1}'
            if not t:
                result.append(Entry('', False, lines[i], [], origin))
                i += 1
                continue
            require(not any(c in ' '.join(t) for c in '<>\'"'),
                    f'unsupported redirect/quoted syntax: {origin}')
            if t[0].lower() == '%include':
                require(len(t) == 2, f'invalid include: {origin}')
                result.extend(self.read((self.cwd / t[1]).resolve(), (*stack, path)))
                i += 1
                continue
            block = t[0].lower() == '%block'
            require(not t[0].startswith('%') or block, f'unsupported directive: {origin}')
            if block:
                require(len(t) == 2, f'invalid block header: {origin}')
                key = label(t[1])
                i += 1
                body = []
                while i < len(lines):
                    row = tokens(lines[i])
                    if row and row[0].lower() == '%endblock':
                        require(len(row) == 2 and label(row[1]) == key,
                                f'mismatched block end: {origin}')
                        break
                    require(not row or not row[0].startswith('%'),
                            f'nested directive in block: {origin}')
                    require(not any(c in ' '.join(row) for c in '<>\'"'),
                            f'unsupported block syntax: {origin}')
                    body.append(lines[i].rstrip('\r\n'))
                    i += 1
                require(i < len(lines), f'unclosed block: {origin}')
            else:
                key, body = label(t[0]), [' '.join(t[1:])]
            raw = ''.join(lines[start:i + 1])
            if not raw.endswith('\n'):
                raw += '\n'
            result.append(Entry(key, block, raw, body, origin))
            i += 1
        return result

    def get(self, key, block):
        entry = next((e for e in self.entries if e.key == label(key)), None)
        require(entry is not None, f'missing {key}')
        require(entry.block == block, f'wrong scalar/block type: {entry.origin}')
        return entry

    def values(self, key, block):
        return [v for row in self.get(key, block).body for v in tokens(row)]

    def replace(self, key, raw):
        # Replace first and remove shadow copies; never append an ineffective override.
        matches = [i for i, e in enumerate(self.entries) if e.key == label(key)]
        at = matches[0] if matches else len(self.entries)
        replacement = Entry(label(key), raw.startswith('%block'), raw, [], 'generated')
        self.entries = [e for i, e in enumerate(self.entries) if i not in matches]
        if raw:
            self.entries.insert(at, replacement)

    def text(self):
        return ''.join(e.raw for e in self.entries)


def positive_int(text):
    require(re.fullmatch(r'\+?[0-9]+', str(text)) is not None, f'not a positive integer: {text}')
    n = int(text)
    require(n > 0, 'count must be positive')
    return n


def one(values, name):
    require(len(values) == 1, f'{name} needs one value')
    return values[0]


def logical(values):
    value = one(values, 'logical').lower()
    require(value in ('t', 'true', '.true.', 'yes', 'f', 'false', '.false.', 'no'),
            'unsupported logical spelling')
    return value in ('t', 'true', '.true.', 'yes')


def species(doc):
    n = positive_int(one(doc.values('number_of_species', False), 'number_of_species'))
    spins = [number(v) for v in doc.values('Spin_values', True)]
    z = [positive_int(v) for v in doc.values('Z_values', True)]
    require(len(spins) == len(z) == n, 'species / Spin_values / Z_values counts differ')
    require(all(v >= 0 for v in spins), 'negative Spin_values')
    require(all(v <= 118 for v in z), 'unsupported Z_values')
    return spins


def _lsorbit_evidence(paths, expected=None):
    """Require explicit, consistent LSORBIT declarations in source OUTCARs."""
    if not paths:
        require(False, 'unsupported SOC route without source OUTCAR LSORBIT evidence')
    observed = []
    for path in paths:
        raw = Path(path).read_text(errors='replace')
        hits = re.findall(r'(?im)^\s*LSORBIT\s*=\s*([TF])\b', raw)
        require(hits, f'missing LSORBIT evidence: {path}')
        require(len(set(hits)) == 1, f'inconsistent LSORBIT declarations: {path}')
        observed.append(hits[0] == 'T')
    require(len(set(observed)) == 1, 'mixed LSORBIT evidence across source OUTCARs')
    actual = 'full' if observed[0] else 'off'
    require(expected is None or actual == expected,
            f'LSORBIT={"T" if observed[0] else "F"} conflicts with requested SOC={expected}')
    return {'expected': expected, 'observed': actual,
            'sources': [{'path': str(Path(p)), 'sha256': digest(Path(p).read_bytes())} for p in paths]}


# Basis geometry/order identity excludes only the documented runtime controls and
# restriction itself. SOC must separately be T in the mapping's executed input.
RUNTIME_CONTROLS = {label(k) for k in ('local_mode.cal_para_method',
    'local_mode.read_interaction', 'local_mode.nstr_random', 'local_mode.seed',
    'local_mode.special_SOC')}
CLUSTER_MARKER = 'Interaction,ik,inf,nint_para,nmode_all,nmode_cluster,nint_para_lamp: '


def basis_definition(doc, files):
    effective = {}
    for e in doc.entries:
        if e.key and e.key not in RUNTIME_CONTROLS and e.key not in effective:
            effective[e.key] = {'block': e.block, 'rows': [tokens(row) for row in e.body]}
    return digest(json_bytes({'effective': effective, 'files': files}))


def package_hashes(doc, spec, base):
    paths = spec.get('files')
    require(isinstance(paths, dict) and {'cell.str', 'unit_cell.str'} <= set(paths),
            'declare actual cell.str, unit_cell.str and every active package dependency in files')
    result = {}
    for name, path in paths.items():
        require(Path(name).name == name and name not in ('PASP.input', 'local_mode_PM.dat'),
                'only flat input dependencies supported')
        result[name] = digest(source(base, path).read_bytes())
    return result


def native_types(log):
    """PASP print_lm_interaction: I5,2I3,4I5; parse widths, not species/columns.

    Fixed widths matter when ik=4 and inf>=100 have no intervening whitespace.
    The complete final table, including the zero-body record, must be captured.
    """
    rows = []
    for line in log.splitlines():
        if CLUSTER_MARKER not in line:
            continue
        data = line.split(CLUSTER_MARKER, 1)[1]
        require(len(data) >= 31, 'unsupported/truncated native interaction table')
        ends = (0, 5, 8, 11, 16, 21, 26, 31)
        row = tuple(int(data[ends[i]:ends[i + 1]]) for i in range(7))
        if row[0] == 1:
            rows = []  # Last complete table wins; partial tables fail below.
        rows.append(row)
    require(rows and [r[0] for r in rows] == list(range(1, len(rows) + 1)),
            'missing/non-contiguous current native interaction enumeration')
    totals = re.findall(r'Total number of different clusters:\s*(\d+)', log)
    require(totals and int(totals[-1]) == len(rows), 'incomplete native interaction table')
    types = [(r[1], r[2]) for r in rows if r[1] > 0 and r[3] > 0]
    require(types and len(types) == len(set(types)), 'missing/duplicate eligible native types')
    return types


def mapped_soc(doc, mapping_path, current_files):
    """Use a previously verified compatible SOC=T run; never launch to get IDs."""
    mapping_path = Path(mapping_path).resolve()
    m = load(mapping_path)
    required = {'basis_input', 'basis_log', 'basis_exit_code_file', 'files',
                'selected', 'order_rationale', 'type_limit', 'order_bound'}
    optional = {'stage', 'stage_evidence', 'cap_convention', 'policy_identity'}
    require(required <= set(m) <= required | optional, 'unsupported SOC mapping evidence fields')
    paths = {k: source(mapping_path.parent, m[k]) for k in
             ('basis_input', 'basis_log', 'basis_exit_code_file')}
    require(len({p.parent for p in paths.values()}) == 1,
            'SOC mapping input/log/exit must be from the same verified run')
    old = FDF(paths['basis_input'])
    require(logical(old.values('Invariant.SOC', False)), 'SOC=F enumeration is not an SOC=T mapping')
    old_files = package_hashes(old, m, mapping_path.parent)
    for name, expected in old_files.items():
        require(digest((old.cwd / name).read_bytes()) == expected,
                f'mapping dependency does not match actual verified run: {name}')
    definition = basis_definition(doc, current_files)
    require(definition == basis_definition(old, old_files),
            'unsupported SOC mapping: basis definitions/dependency hashes differ; obtain compatible verified evidence')
    log = paths['basis_log'].read_text()
    require(paths['basis_exit_code_file'].read_text().strip() == '0' and
            'PASP is finished gracefully' in log and
            not re.search(r'forrtl:|SIGSEGV|SIGABRT|MPI_ABORT|NEED TO REWRITE DATA|^\s*(ERROR|FATAL)\b', log, re.I | re.M),
            'SOC mapping run has no verified native completion')
    types = native_types(log)
    limit, bound = positive_int(m['type_limit']), positive_int(m['order_bound'])
    power = positive_int(one(doc.values('Invariant.power', False), 'Invariant.power'))
    require(bound <= power, 'maximum SOC order bound exceeds current expansion order')
    require(isinstance(m['selected'], list) and m['selected'], 'nonempty selected SOC tuples required')
    selected = []
    for row in m['selected']:
        require(isinstance(row, list) and len(row) == 3, 'selected needs body/type/maximum_order')
        selected.append(tuple(positive_int(v) for v in row))
    ids = [(b, t) for b, t, _ in selected]
    require(len(selected) <= limit and len(set(ids)) == len(ids) and
            all(pair in types for pair in ids) and
            ids == [pair for pair in types if pair in ids],
            'select unique eligible actual types in native cluster ordering; never guess IDs')
    require(all(order <= bound for _, _, order in selected), 'selected maximum SOC order exceeds declared bound')
    require(isinstance(m['order_rationale'], list) and len(m['order_rationale']) == len(selected) and
            all(isinstance(s, str) and s.strip() for s in m['order_rationale']),
            'declare reference/current-basis justification for every selected maximum SOC order')
    cap_convention = m.get('cap_convention', 'selected_rows')
    require(cap_convention == 'selected_rows', 'SOC cap convention must count actual selected rows/types')
    refs = Path(__file__).resolve().parents[2] / 'reference/params'
    identity = None
    if m.get('policy_identity'):
        identity_path = pinned_stage_file(mapping_path.parent, m['policy_identity'])
        identity = load(identity_path)
        require(identity.get('selected') == [list(row) for row in selected] and
                identity.get('basis_definition_sha256') == definition and
                identity.get('basis_log_sha256') == digest(paths['basis_log'].read_bytes()),
                'physical identity must pin current native tuples, basis definition and log')
        keys = identity.get('physical_keys')
        require(isinstance(keys, list) and len(keys) == len(selected) and
                all(isinstance(k, str) and k.strip() for k in keys) and len(set(keys)) == len(keys),
                'physical policy needs unique environment/orbit identities, not copied indices')
        require(identity.get('references'), 'physical identity needs mapping/operator references')
        for ref in identity['references']:
            pinned_stage_file(identity_path.parent, ref)
    return {'selected': selected, 'interaction_types': types, 'basis_definition_sha256': definition,
            'policy_identity': identity,
            'mapping_sha256': digest(mapping_path.read_bytes()),
            'evidence_sha256': {k: digest(p.read_bytes()) for k, p in paths.items()},
            'reference_sha256': {k: digest((refs / (k + '.md')).read_bytes()) for k in
                                 ('Invariant.SOC', 'local_mode.special_SOC')},
            'type_limit': limit, 'order_bound': bound, 'order_rationale': m['order_rationale'],
            'stage': m.get('stage', 'initial'), 'cap_convention': cap_convention,
            'actual_count': len(selected), 'stage_evidence': m.get('stage_evidence'),
            'ordering': 'native print_lm_interaction cluster order, nonzero body and parameter count',
            'omitted_types': 'non-SOC path; no appended zero rows',
            'unresolved': 'order rationale and native restricted outputs require scientific review'}


def pinned_stage_file(base, ref):
    require(isinstance(ref, dict) and set(ref) == {'path', 'sha256'},
            'stage evidence needs path and sha256')
    path = source(base, ref['path'])
    require(digest(path.read_bytes()) == ref['sha256'], 'SOC stage evidence hash mismatch')
    return path


def radius_controls(doc):
    for key in ('fig.maxk', 'Invariant.power', 'fig.mdist'):
        require(sum(e.key == label(key) for e in doc.entries) == 1,
                f'effective input must contain exactly one {key} declaration')
    body = positive_int(one(doc.values('fig.maxk', False), 'fig.maxk'))
    power = positive_int(one(doc.values('Invariant.power', False), 'Invariant.power'))
    radii = [number(v) for v in doc.values('fig.mdist', True)]
    require(2 <= body <= 4 and power <= 4, 'automatic body/order bounds exceeded')
    require(body <= len(radii) <= 4 and radii[0] == 1 and all(0 < r <= 15 for r in radii[1:]),
            'fig.mdist needs flag 1 and two/three/four radii at most 15 Bohr')
    return body, power, radii


def comparable_soc(old, new):
    require(old['soc'] == new['soc'] and old['source_evidence'] == new['source_evidence'] and
            old['manual_study'] is None and new['manual_study'] is None,
            'comparison source/SOC provenance mismatch')
    if old['soc'] == 'off':
        return
    a, b = old['mapping'], new['mapping']
    if a['basis_definition_sha256'] == b['basis_definition_sha256']:
        require(old['special_SOC'] == new['special_SOC'], 'radius comparison changed SOC orders/types')
    else:
        require(a.get('policy_identity') and b.get('policy_identity'),
                'changed basis requires verified physical policy identities and native remapping; pin before first launch')
        left = dict(zip(a['policy_identity']['physical_keys'], (r[2] for r in a['selected'])))
        right = dict(zip(b['policy_identity']['physical_keys'], (r[2] for r in b['selected'])))
        require(left == right, 'radius comparison changed physical SOC selection/order')


def radius_comparisons(evidence, base, source_evidence):
    """Hash-bound executed bases, actual fit preflight and pristine reconstruction."""
    from search_inputs import execution_evidence
    from fit_handoff import check as handoff
    comparisons = evidence.get('radius_body_comparisons')
    require(isinstance(comparisons, list) and 2 <= len(comparisons) <= 12,
            'higher SOC requires executed bounded radius/body comparisons')
    bodies, configs, policies, results = set(), set(), [], []
    for row in comparisons:
        path = pinned_stage_file(base, row['execution'])
        run = execution_evidence(path)
        require(run['sha256'].get('local_mode_PM.dat') and
                (path.parent / 'exit.code').read_text().strip() == '0' and
                'PASP is finished gracefully' in (path.parent / 'log.out').read_text(),
                'SOC comparison basis did not complete')
        policy = load(path.parent / 'basis-gate.json')['soc_policy']
        require(policy['source_evidence'] == source_evidence and policy['manual_study'] is None and
                policy['stage']['stage'] == 'initial' and all(r[2] == 2 for r in policy['special_SOC']),
                'radius comparisons require same source and low-order initial SOC')
        if policies:
            comparable_soc(policies[0], policy)
        policies.append(policy)
        body, power, radii = radius_controls(FDF(path.parent / 'PASP.input'))
        bodies.add(body)
        configs.add((body, tuple(radii[1:body])))
        assessment_path = pinned_stage_file(base, row['assessment'])
        assessment = load(assessment_path)
        manifest = pinned_stage_file(assessment_path.parent, assessment['fit_manifest'])
        checked, _ = handoff(manifest)
        require(assessment.get('basis_sha256') == run['sha256']['local_mode_PM.dat'] ==
                checked['sources']['basis_file']['sha256'] and
                assessment.get('feature_count') == checked['feature_count'] and
                assessment.get('test_used_for_selection') is False and
                {'fit_log', 'fit_exit_code_file'} <= checked['sources'].keys(),
                'comparison assessment basis/test/native fit provenance mismatch')
        preflight_path = pinned_stage_file(assessment_path.parent, assessment['fit_preflight'])
        preflight = load(preflight_path)
        fit_dir = Path(checked['sources']['fit_log']['path']).parent
        actual = check_fit(fit_dir / 'PASP.input', {
            'Fitting_Dataset.txt': checked['sources']['train_matrix']['path'],
            'Fitting_Data_for_prediction.txt': checked['sources']['selection_matrix']['path']})
        require(preflight == actual and actual['candidate_feature_count'] == checked['feature_count'],
                'comparison needs unchanged actual settings and pristine pre-fit matrices')
        metrics = {}
        for name in ('train', 'selection'):
            rows = records(Path(checked['sources'][name + '_predictions']['path']))
            target, estimate = [number(r[1]) for r in rows], [number(r[2]) for r in rows]
            mean = math.fsum(target) / len(target)
            sse = math.fsum((a - b) ** 2 for a, b in zip(target, estimate))
            sst = math.fsum((v - mean) ** 2 for v in target)
            require(sst > 0, 'constant target comparison has undefined R2')
            metrics[name] = {'r2': 1 - sse / sst, 'rmse': math.sqrt(sse / len(target))}
            require(math.isclose(number(assessment[name + '_r2']), metrics[name]['r2'], abs_tol=1e-10) and
                    math.isclose(number(assessment[name + '_residual']), metrics[name]['rmse'], abs_tol=1e-10),
                    'declared residual/R2 differs from actual native predictions')
        require(number(assessment['conditioning']) >= 0, 'nonnegative conditioning required')
        for key in ('identifiability', 'directional_deficiency', 'controls_comparison'):
            require(isinstance(assessment.get(key), str) and assessment[key].strip(), f'assessment needs {key}')
        results.append({'body': body, 'radii': radii, 'metrics': metrics,
                        'assessment_sha256': digest(assessment_path.read_bytes())})
    require((2, (15.0,)) in configs, 'SOC comparisons need executed 15 Bohr pair baseline')
    pruned = evidence.get('pruned_controls', [])
    require(isinstance(pruned, list), 'pruned_controls must be a list')
    justified, radius_pruned = set(), False
    for row in pruned:
        require(row.get('category') in ('width', 'symmetry', 'mapping', 'runtime') and
                isinstance(row.get('reason'), str) and row['reason'].strip() and row.get('references'),
                'pruned branch needs concrete width/symmetry/mapping/runtime evidence')
        for ref in row['references']:
            pinned_stage_file(base, ref)
        if row['category'] in ('width', 'runtime'):
            path = pinned_stage_file(base, row['execution'])
            run = execution_evidence(path)
            require(run['body_order'] == row['body'], 'pruning body mismatch')
            comparable_soc(policies[0], load(path.parent / 'basis-gate.json')['soc_policy'])
            if row['category'] == 'width':
                from method6 import native_width
                require(native_width((path.parent / 'local_mode_PM.dat').read_bytes()) >
                        1.5 * checked['datasets']['train']['count'], 'width pruning needs oversized full basis')
            else:
                require((path.parent / 'exit.code').read_text().strip() != '0' or
                        'PASP is finished gracefully' not in (path.parent / 'log.out').read_text(),
                        'runtime pruning needs failed/incomplete actual attempt')
        justified.add(positive_int(row['body']))
        radius_pruned |= row.get('radius_comparison_infeasible') is True
    require({2, 3, 4} <= bodies | justified and bodies & {3, 4},
            'SOC escalation needs representative multi-body runs or evidenced infeasible branches')
    require(any(len({r for b, r in configs if b == body}) > 1 for body in bodies) or radius_pruned,
            'one radius tuple is not a bounded radius comparison')
    return results


def staged_soc(mapping, mapping_path, manual, source_evidence):
    """Enforce automatic stages at the shared basis/encoding policy boundary.

    Evidence integrity is executable; physical operator/symmetry interpretation
    remains an independent review duty. Never launch unrestricted SOC for IDs.
    """
    if manual is not None:
        return {'stage': 'manual_study', 'authorization_sha256': manual['sha256']}
    rows = mapping['selected']
    stage = mapping['stage']
    eligible = [pair for pair in mapping['interaction_types'] if pair[0] in (1, 2)]
    target = min(10, len(eligible))
    require(stage in ('initial', 'symmetry_exception', 'extension'), 'unsupported automatic SOC stage')
    if stage == 'initial':
        require(target > 0, 'initial SOC stage has no eligible single/pair types')
        require(all(b in (1, 2) and order == 2 for b, _, order in rows) and mapping['order_bound'] == 2,
                'initial SOC stage requires real single/pair types at maximum SOC order two')
        count = None
        if len(rows) != target or mapping['type_limit'] != len(rows):
            require(mapping.get('stage_evidence'), 'initial SOC stage count deviation needs pinned evidence')
            path = pinned_stage_file(Path(mapping_path).resolve().parent, mapping['stage_evidence'])
            count = load(path)
            require(mapping['type_limit'] == len(rows) <= len(eligible) and
                    count.get('selected') == [list(r) for r in rows] and count.get('references'),
                    'initial SOC stage count evidence selection mismatch')
            for key in ('reason', 'symmetry_evidence'):
                require(isinstance(count.get(key), str) and count[key].strip(), f'count evidence needs {key}')
            check_candidate_width(positive_int(count['feature_count']), positive_int(count['training_rows']))
            for ref in count['references']:
                pinned_stage_file(path.parent, ref)
        if {b for b, _ in eligible} == {1, 2}:
            require({b for b, _, _ in rows} == {1, 2} or count is not None,
                    'initial SOC stage must cover available single-body and pair families')
        return {'stage': stage, 'evidence': None,
                'initial_target': 10, 'eligible_single_body_count': sum(b == 1 for b, _ in eligible),
                'eligible_total_count': len(eligible), 'count_exception': count,
                'selected_rows': len(rows), 'availability_exception': len(eligible) < 10,
                'count_evidence': mapping['evidence_sha256']['basis_log']}
    base = Path(mapping_path).resolve().parent
    evidence_path = pinned_stage_file(base, mapping['stage_evidence'])
    evidence = load(evidence_path)
    for key in ('reason', 'operator_interpretation', 'symmetry_evidence'):
        require(isinstance(evidence.get(key), str) and evidence[key].strip(),
                f'SOC stage evidence needs {key}')
    refs = evidence.get('references')
    require(isinstance(refs, list) and refs, 'SOC stage evidence needs operator/symmetry source references')
    for ref in refs:
        pinned_stage_file(evidence_path.parent, ref)
    comparisons = radius_comparisons(evidence, evidence_path.parent, source_evidence)
    if stage == 'symmetry_exception':
        require(len(rows) <= len(eligible) and all(order <= 4 for _, _, order in rows),
                'symmetry exception remains targeted and bounded')
        require(evidence.get('second_order_forbidden_or_absent') is True and
                evidence.get('lowest_allowed_tuples') == [list(row) for row in rows],
                'symmetry exception must document the lowest allowed meaningful operators')
    else:
        from search_inputs import execution_evidence
        previous_path = pinned_stage_file(evidence_path.parent, evidence.get('predecessor'))
        previous = execution_evidence(previous_path)
        gate = load(previous_path.parent / 'basis-gate.json')
        require('local_mode_PM.dat' in previous['sha256'] and
                (previous_path.parent / 'exit.code').read_text().strip() == '0' and
                'PASP is finished gracefully' in (previous_path.parent / 'log.out').read_text(),
                'SOC extension requires a completed reduced predecessor basis')
        old = gate['soc_policy']
        require(old['soc'] == 'restricted' and old['source_evidence'] == source_evidence and
                old['manual_study'] is None and old.get('stage', {}).get('stage') in
                ('initial', 'symmetry_exception', 'extension'), 'SOC predecessor source/stage mismatch')
        require(old['mapping']['basis_definition_sha256'] == mapping['basis_definition_sha256'],
                'SOC extension must hold body/radii/modes/expansion fixed after radius comparison')
        old_rows = {tuple(row[:2]): row[2] for row in old['special_SOC']}
        new_rows = {tuple(row[:2]): row[2] for row in rows}
        require(all(new_rows.get(key, -1) >= value for key, value in old_rows.items()),
                'SOC extension must retain the evaluated lower-stage operators')
        changed = [(b, t, order) for (b, t), order in new_rows.items()
                   if old_rows.get((b, t)) != order]
        require(changed, 'SOC extension must change a physical family')
        family = evidence.get('family')
        require(family in ('pair_bilinear', 'single_fourth', 'advanced'), 'declare one SOC extension family')
        if family == 'pair_bilinear':
            require(all(b == 2 and order <= 2 for b, _, order in changed),
                    'pair_bilinear extension permits only eligible two-body order-two additions')
        elif family == 'single_fourth':
            require(all(b == 1 and order <= 4 for b, _, order in changed),
                    'single_fourth extension permits only targeted single-body additions')
        else:
            require(evidence.get('lower_stages_exhausted') is True and
                    all(order <= 4 for _, _, order in changed),
                    'advanced SOC requires demonstrated lower-order deficiency and targeted orders at most four')
        require(mapping['type_limit'] <= 10 or
                isinstance(evidence.get('cap_extension_reason'), str) and evidence['cap_extension_reason'].strip(),
                'do not inflate the SOC type cap without physical/train-selection evidence')
        assessment_path = pinned_stage_file(evidence_path.parent, evidence.get('assessment'))
        assessment = load(assessment_path)
        require(any(r['assessment_sha256'] == digest(assessment_path.read_bytes()) for r in comparisons),
                'SOC predecessor assessment must be an executed reconstructed radius comparison')
        require(assessment.get('basis_sha256') == previous['sha256']['local_mode_PM.dat'],
                'SOC comparison assessment is from another basis')
        for key in ('feature_count',):
            positive_int(assessment[key])
        for key in ('train_r2', 'selection_r2', 'train_residual', 'selection_residual', 'conditioning'):
            number(assessment[key])
        for key in ('identifiability', 'directional_deficiency', 'controls_comparison'):
            require(isinstance(assessment.get(key), str) and assessment[key].strip(),
                    f'SOC comparison assessment needs {key}; pooled R2 alone is insufficient')
        require(assessment.get('test_used_for_selection') is False,
                'SOC extension evidence must use train/selection, not test outcomes')
        current_definition = mapping['basis_definition_sha256']
        require(old['mapping']['basis_definition_sha256'] == current_definition or
                isinstance(assessment.get('confounders'), str) and assessment['confounders'].strip(),
                'declare controls changed during SOC comparison')
    return {'stage': stage, 'evidence': evidence, 'radius_body_comparisons': comparisons,
            'evidence_sha256': digest(evidence_path.read_bytes())}


def soc_context(doc, spec, base, files=None):
    """Mandatory automatic policy; manual studies require a separate authorization."""
    require(spec.get('soc') in ('full', 'off', 'restricted'), 'explicit SOC policy required')
    manual = None
    if spec.get('manual_study'):
        path = source(base, spec['manual_study'])
        manual = load(path)
        require(manual.get('mode') == 'manual_study' and manual.get('soc') == spec['soc'] and
                isinstance(manual.get('authorization'), str) and manual['authorization'].strip() and
                isinstance(manual.get('reason'), str) and manual['reason'].strip(),
                'manual study needs explicit user authorization, SOC policy and reason')
        manual = {**manual, 'sha256': digest(path.read_bytes())}
        require(spec.get('automatic') is False,
                'manual-study authorization cannot be used by an automatic search route')
        authority_name = os.environ.get('PASP_MANUAL_AUTHORITY')
        require(authority_name, 'self-authored manual authorization is unsupported; missing external user authority')
        authority_path = Path(authority_name).absolute()
        require(not any(p.is_symlink() for p in (authority_path, *authority_path.parents)) and
                authority_path.is_file() and not authority_path.stat().st_mode & 0o222,
                'manual authority must be a regular read-only externally supplied file')
        authority = load(authority_path)
        study_root = Path(authority['study_root']).resolve()
        require(not authority_path.is_relative_to(study_root) and doc.cwd.is_relative_to(study_root) and
                authority.get('mode') == 'explicit_user_manual' and authority.get('soc') == spec['soc'] and
                authority.get('authorization') == manual['authorization'],
                'manual authority does not support this study/user decision')
        manual['authority_sha256'] = digest(authority_path.read_bytes())
    require(spec.get('automatic', True) is True or manual is not None,
            'automatic=false is not a recorded manual-study exception')
    outcars = [source(base, p) for p in spec.get('source_outcars', [])]
    evidence = _lsorbit_evidence(outcars) if outcars or manual is None else None
    if evidence:
        expected = 'off' if spec['soc'] == 'off' else 'full'
        require(evidence['observed'] == expected, 'source LSORBIT conflicts with effective SOC physics')
        if manual is None and expected == 'full':
            require(spec['soc'] == 'restricted', 'automatic source-SOC-on exploration requires restricted SOC; full/off rejected')
    if manual is None:
        radius_controls(doc)
    mapping = None
    if spec['soc'] == 'restricted':
        require(spec.get('soc_mapping'), 'unsupported restricted SOC without verified current-basis mapping evidence')
        files = package_hashes(doc, spec, base) if files is None else files
        mapping = mapped_soc(doc, source(base, spec['soc_mapping']), files)
        if manual is None:
            require(mapping['policy_identity'],
                    'automatic restricted SOC needs physical policy identity pinned before first launch')
    stage = staged_soc(mapping, source(base, spec['soc_mapping']), manual, evidence) if mapping else None
    checked = check(doc, spec['soc'], mapping['selected'] if mapping else None,
                    mapping['interaction_types'] if mapping else None,
                    ('F' if evidence['observed'] == 'off' else 'T') if evidence else None)
    result = {'soc': spec['soc'], 'special_SOC': checked['special_SOC'],
              'source_evidence': evidence, 'mapping': mapping, 'manual_study': manual, 'stage': stage}
    result['policy_sha256'] = digest(json_bytes(result))
    return result


def _special_rows(doc):
    entries = [e for e in doc.entries if e.key == label('local_mode.special_SOC')]
    require(len(entries) <= 1, 'duplicate local_mode.special_SOC declarations')
    if not entries:
        return []
    entry = entries[0]
    rows = [tokens(row) for row in entry.body if tokens(row)]
    require(rows and len(rows[0]) == 1, 'special_SOC row count is missing')
    count = positive_int(rows[0][0])
    require(len(rows) == count + 1, 'special_SOC row count does not match rows written')
    result = []
    for row in rows[1:]:
        require(len(row) == 3, 'special_SOC rows need body, interaction type, maximum order')
        body, interaction = map(positive_int, row[:2])
        require(re.fullmatch(r'\+?[0-9]+', row[2]) is not None, 'maximum SOC order must be a nonnegative integer')
        maximum = int(row[2])
        result.append((body, interaction, maximum))
    return result


def check(doc, soc, special_rows=None, interaction_types=None, lsorbit=None):
    require(doc.values('Model', False) == ['Invariant'], 'only Model Invariant supported')
    for key in ('Invariant.SOC', 'local_mode.special_SOC'):
        require(sum(e.key == label(key) for e in doc.entries) <= 1, f'duplicate/shadowed {key}')
    spins = species(doc)
    effective_soc = 'full' if soc == 'restricted' else soc
    require(logical(doc.values('Invariant.SOC', False)) == (effective_soc == 'full'), 'SOC policy mismatch')
    actual_rows = _special_rows(doc)
    if soc == 'restricted':
        require(actual_rows, 'restricted SOC requires local_mode.special_SOC')
        if special_rows is not None:
            require(actual_rows == [tuple(map(int, row)) for row in special_rows],
                    'special_SOC rows differ from requested policy')
        require(interaction_types, 'restricted SOC requires current-basis interaction type mapping')
        available = {(int(row[0]), int(row[1])) for row in interaction_types}
        require(all((body, interaction) in available for body, interaction, _ in actual_rows),
                'special_SOC references an interaction type absent from the current SOC basis')
        require(lsorbit in (None, 'T'), 'restricted SOC requires LSORBIT=T')
    else:
        require(not actual_rows, 'special_SOC is only valid with restricted SOC policy')
        if lsorbit is not None:
            require(lsorbit == ('T' if soc == 'full' else 'F'), 'LSORBIT conflicts with SOC policy')
    body = doc.get('local_mode.mode_definition', True).body
    require(len(body) >= 2 and tokens(body[0]) == ['2'], 'mode method line must be 2')
    n = positive_int(one(tokens(body[1]), 'mode count'))
    at = 2
    for mode in range(n):
        require(at + 2 < len(body) and tokens(body[at]) == ['1', 'spin'],
                'only single-atom spin modes supported; mode header missing/misaligned')
        sid = positive_int(one(tokens(body[at + 1]), 'mode species'))
        require(sid <= len(spins) and spins[sid - 1] > 0, 'mode species inactive/out of range')
        row = [number(v) for v in tokens(body[at + 2])]
        require(len(row) == 6 and any(v != 0 for v in row[3:]), 'mode needs xyz and nonzero direction')
        at += 3
        if mode < n - 1:
            require(at < len(body) and not body[at].strip(), 'exactly one blank mode separator required')
            at += 1
    require(at == len(body), 'mode count/extra records mismatch')
    return {'scope': 'spin format and declared SOC shape only; not basis launch authorization',
            'mode_count': n, 'species_count': len(spins), 'soc': soc,
            'special_SOC': actual_rows,
            'source_sha256': doc.hashes}


def prepare_spin(path, request, root):
    doc = FDF(path)
    spec = load(request)
    allowed = {'soc', 'representatives', 'source_outcars', 'soc_mapping', 'files', 'manual_study', 'automatic'}
    require(set(spec) <= allowed and {'soc', 'representatives'} <= set(spec), 'invalid spin request fields')
    require(spec['soc'] in ('full', 'off', 'restricted'), 'unsupported SOC policy')
    spins = species(doc)
    reps = spec['representatives']
    require(isinstance(reps, list) and reps, 'nonempty representatives required')
    modes, seen = [], set()
    for rep in reps:
        require(set(rep) == {'species', 'position_angstrom'}, 'invalid representative fields')
        sid = identifier(rep['species'])
        xyz = rep['position_angstrom']
        require(isinstance(xyz, list) and len(xyz) == 3, 'position_angstrom needs three Cartesian values')
        xyz = [number(v) for v in xyz]
        require(1 <= sid <= len(spins) and spins[sid - 1] > 0, 'representative species inactive/out of range')
        key = (sid, *xyz)
        require(key not in seen, 'duplicate representative')
        seen.add(key)
        for axis in range(3):
            values = xyz + [int(j == axis) for j in range(3)]
            modes.append(f'1 spin\n{sid}\n' + ' '.join(f'{v:.16g}' for v in values))
    block = '%block local_mode.mode_definition\n2\n' + str(len(modes)) + '\n'
    block += '\n\n'.join(modes) + '\n%endblock local_mode.mode_definition\n'
    changes = {key: [e.origin for e in doc.entries if e.key == label(key)]
               for key in ('local_mode.mode_definition', 'Invariant.SOC', 'local_mode.special_SOC')}
    doc.replace('local_mode.mode_definition', block)
    doc.replace('Invariant.SOC', 'Invariant.SOC ' + ('F' if spec['soc'] == 'off' else 'T') + '\n')
    # Reparse generated records before deriving the mapping identity.
    generated = FDF.__new__(FDF)
    generated.cwd, generated.hashes = doc.cwd, doc.hashes
    generated.entries = generated.parse(doc.text(), Path('<generated>'), ())
    rows = []
    if spec['soc'] == 'restricted':
        require(spec.get('soc_mapping'), 'restricted preparation requires verified SOC mapping')
        mapping = mapped_soc(generated, source(Path(request).resolve().parent, spec['soc_mapping']),
                             package_hashes(generated, spec, Path(request).resolve().parent))
        rows = mapping['selected']
        doc.replace('local_mode.special_SOC', '%block local_mode.special_SOC\n' + str(len(rows)) + '\n' +
                    ''.join(' '.join(map(str, row)) + '\n' for row in rows) +
                    '%endblock local_mode.special_SOC\n')
    else:
        doc.replace('local_mode.special_SOC', '')
    raw = doc.text()
    # Reparse in memory; deployed skill directories may be read-only.
    checked = FDF.__new__(FDF)
    checked.cwd, checked.hashes = doc.cwd, doc.hashes
    checked.entries = checked.parse(raw, Path('<generated>'), ())
    context = soc_context(checked, spec, Path(request).resolve().parent)
    receipt = check(checked, spec['soc'], rows or None,
                    context['mapping']['interaction_types'] if context['mapping'] else None)
    receipt.update(source_sha256=doc.hashes, replaced_declarations=changes,
                   request_sha256=digest(Path(request).read_bytes()),
                   soc_policy=context,
                   selected_special_SOC=rows,
                   unresolved=['site symmetry/coordinates', 'primitive/atom mapping',
                               'basis suitability and runtime output'])
    return write_package(Path(root).resolve(), {'PASP.input': raw.encode()}, 'spin-preparation.json', receipt)


def fit_data(conversion, split, receipt_hash, lambdas, root):
    root = Path(root).resolve()
    require(not root.exists(), 'fit-data requires a new output directory; preserve existing attempts')
    conversion = Path(conversion).resolve()
    data = conversion.read_bytes()
    require(digest(data) == receipt_hash, 'conversion receipt changed since checkpoint')
    receipt = load(conversion)
    split = Path(split).resolve()
    require(digest(split.read_bytes()) == receipt['split_sha256'], 'frozen split changed')
    expected = [int(sid) for sid in receipt['samples']]
    splits = split_ids(split, expected)
    require(splits == receipt['splits'], 'split receipt mismatch')
    width = positive_int(receipt['feature_count'])
    fitting_point_count = len(splits['train'])
    size_gate = check_candidate_width(width, fitting_point_count)
    schedule = load(lambdas)
    require(isinstance(schedule, list) and schedule, 'explicit nonempty lambda list required')
    schedule = [number(v) for v in schedule]
    require(all(v > 1 for v in schedule),
            'automatic-search lambda factors must be greater than 1')
    retained_limit = min(width, limits(fitting_point_count)['retained_limit'])
    files = {}
    for name, target in [('train', 'Fitting_Dataset.txt'), ('selection', 'Fitting_Data_for_prediction.txt')]:
        for suffix in ('.txt', '.ids.json'):
            filename = name + suffix
            raw = (conversion.parent / filename).read_bytes()
            require(digest(raw) == receipt['sha256'][filename], f'converted artifact changed: {filename}')
            if suffix == '.ids.json':
                require(json.loads(raw) == splits[name], f'row map mismatch: {name}')
                files[target + '.ids.json'] = raw
            else:
                rows = raw.decode().splitlines()
                require(len(rows) == len(splits[name]), f'row count mismatch: {name}')
                for row in rows:
                    values = [number(v) for v in row.split()]
                    require(len(values) == width + 1, f'feature/target width mismatch: {name}')
                files[target] = raw
    files['Fitting_Set_Lambda.txt'] = (f'{len(schedule)} 1\n' + ''.join(
        f'{i} {retained_limit} {v:.16E}\n' for i, v in enumerate(schedule, 1))).encode()
    result = {'scope': 'train/selection staging and explicit lambda schedule; candidate-width pre-fit gate',
              'conversion_sha256': receipt_hash, 'split_sha256': receipt['split_sha256'],
              'basis_sha256': receipt['basis_sha256'], 'feature_count': width,
              'candidate_feature_count': width,
              'fitting_data_point_count': fitting_point_count,
              'candidate_feature_limit': size_gate['candidate_feature_limit'],
              'candidate_width_gate': 'passed',
              'retained_parameter_limit': retained_limit,
              'lambda_semantics': 'successive multiplicative search-threshold factors, each greater than 1',
              'lambdas': schedule, 'counts': {k: len(v) for k, v in splits.items()},
              'required_model': 'Fitting_one_order',
              'unresolved': ['real cell.str and PASP.input', 'positional fitting settings and active dependencies',
                             'prior test access/history', 'variable/coefficients mapping', 'actual PASP results']}
    return write_package(root, files, 'fit-data.json', result)


def check_fit(input_path, pristine_matrices=None):
    """Preflight actual files; internal post-fit replay may supply hash-pinned pristine matrices."""
    input_path = Path(input_path).resolve()
    root = input_path.parent
    doc = FDF(input_path)
    require(doc.values('Model', False) == ['Fitting_one_order'],
            'automatic fit preflight requires Model Fitting_one_order')
    sources = {str(p): digest(Path(p).read_bytes()) for p in doc.hashes}
    counts, width = {}, None
    for name in ('Fitting_Dataset.txt', 'Fitting_Data_for_prediction.txt'):
        path = Path(pristine_matrices[name]) if pristine_matrices else root / name
        raw = path.read_bytes()
        rows = [row.split() for row in raw.decode().splitlines() if row.strip()]
        require(bool(rows), f'empty fitting matrix: {name}')
        if width is None:
            width = len(rows[0]) - 1
        for row in rows:
            require(len(row) == width + 1, f'feature/target width mismatch: {name}')
            for value in row:
                number(value)
        counts[name] = len(rows)
        sources[name] = digest(raw)
    size_gate = check_candidate_width(width, counts['Fitting_Dataset.txt'])
    path = root / 'Fitting_Set_Lambda.txt'
    raw = path.read_bytes()
    rows = [tokens(line) for line in raw.decode().splitlines() if tokens(line)]
    require(bool(rows) and len(rows[0]) >= 2, 'missing lambda count/start round')
    count, start = positive_int(rows[0][0]), positive_int(rows[0][1])
    require(len(rows) == count + 1 and start <= count, 'lambda count/start round mismatch')
    schedule, caps = [], []
    for index, row in enumerate(rows[1:], 1):
        require(len(row) >= 3 and positive_int(row[0]) == index, 'invalid lambda row numbering')
        cap = positive_int(row[1])
        check_retained_count(cap, counts['Fitting_Dataset.txt'])
        require(cap <= width, 'retained-parameter cap exceeds candidate width')
        factor = number(row[2])
        require(factor > 1, 'automatic-search lambda factors must be greater than 1')
        caps.append(cap)
        schedule.append(factor)
    sources[path.name] = digest(raw)
    return {'scope': 'actual automatic-search matrices, parameter caps and lambda factors; not dependency or scientific validation',
            'candidate_width_gate': 'passed', 'candidate_feature_count': width,
            'candidate_feature_limit': size_gate['candidate_feature_limit'],
            'fitting_data_point_count': counts['Fitting_Dataset.txt'],
            'retained_parameter_limit': min(width, size_gate['retained_limit']),
            'round_parameter_caps': caps, 'lambdas': schedule,
            'lambda_semantics': 'successive multiplicative search-threshold factors, each greater than 1',
            'sha256': sources}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('spin', 'check-spin'):
        p = sub.add_parser(name)
        p.add_argument('--input', type=Path, required=True)
        if name == 'spin':
            p.add_argument('--request', type=Path, required=True)
            p.add_argument('--root', type=Path, required=True)
        else:
            p.add_argument('--soc', choices=('full', 'off'))
            p.add_argument('--request', type=Path)
    p = sub.add_parser('fit-data')
    p.add_argument('--conversion', type=Path, required=True)
    p.add_argument('--split', type=Path, required=True)
    p.add_argument('--receipt-sha256', required=True)
    p.add_argument('--lambdas', type=Path, required=True)
    p.add_argument('--root', type=Path, required=True)
    p = sub.add_parser('check-fit')
    p.add_argument('--input', type=Path, required=True)
    a = parser.parse_args()
    if a.command == 'spin':
        result = prepare_spin(a.input, a.request, a.root)
    elif a.command == 'check-spin':
        if a.request:
            result = soc_context(FDF(a.input), load(a.request), a.request.resolve().parent)
        else:
            require(a.soc, 'check-spin needs --request (policy) or --soc (shape only)')
            result = check(FDF(a.input), a.soc)
    elif a.command == 'check-fit':
        result = check_fit(a.input)
    else:
        result = fit_data(a.conversion, a.split, a.receipt_sha256, a.lambdas, a.root)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError, IndexError, OverflowError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        sys.exit(1)
