#!/usr/bin/env python3
"""Bounded spin method-6 preparation/batching. Standard library; see README.md.

The caller supplies the successful basis run, complete inventory and authorized
launcher argv. This module does not choose physics, fit, or submit to a scheduler.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys

from prepare_l3 import FDF, check, label, logical, one, soc_context, package_hashes
from study_contract import (digest, features, identifier, json_bytes, load, number,
                            require, source, write_package)

PM = 'local_mode_PM.dat'
CONTROLS = ('local_mode.cal_para_method', 'local_mode.read_interaction', 'local_mode.nstr_random')
FAILURE = re.compile(r'forrtl:|SIGSEGV|SIGABRT|BAD TERMINATION|MPI_ABORT|'
                     r'^\s*(?:ERROR\b|FATAL\b)|\bNaN\b|NEED TO REWRITE DATA|'
                     r'license.*(?:fail|error|invalid)', re.I | re.M)
MODE_COUNT = re.compile(r'Total number of local modes \(excluding strain\):\s*(\d+)', re.I)


def native_width(raw):
    ids = [int(m.group(1)) for m in re.finditer(
        r'^\s*\d+\s+(\d+)\s+.*#ipara,ipara_gb,power,n,nmode,im_read,lonebody\s*$',
        raw.decode(), re.M | re.I)]
    require(ids and sorted(ids) == list(range(1, len(ids) + 1)),
            'native basis needs unique contiguous ipara_gb IDs; FDF text is not a basis')
    return len(ids)


def runtime_check(log, exit_code):
    require(exit_code == 0, f'PASP/launcher exit {exit_code}')
    require('PASP is finished gracefully' in log, 'missing PASP completion marker')
    require(not FAILURE.search(log), 'runtime failure diagnostic; inspect the full log')
    modes = [int(m.group(1)) for m in MODE_COUNT.finditer(log)]
    require(modes and all(m > 0 for m in modes), 'missing/zero actual local modes')
    return {'expanded_mode_count': modes[-1],
            'warnings': [{'line': i, 'text': s} for i, s in enumerate(log.splitlines(), 1)
                         if re.search(r'\bwarning\b', s, re.I)]}


def prepare(request, root):
    request, root = Path(request).resolve(), Path(root).resolve()
    require(not root.exists(), 'use a new template directory; preserve earlier attempts')
    spec = load(request)
    required = {'basis_input', 'basis_file', 'basis_log', 'basis_exit_code_file', 'soc', 'policy'}
    require(required <= set(spec) <= required | {'dependencies', 'interaction_types', 'source_outcars',
                                                'automatic', 'basis_gate_receipt', 'basis_execution_receipt', 'files', 'soc_mapping', 'manual_study'}, 'unsupported preparation request fields')
    require(spec['soc'] in ('full', 'off', 'restricted') and spec['policy'] in ('reuse', 'rebuild'),
            'explicit SOC policy and reuse/rebuild policy required')
    paths = {k: source(request.parent, spec[k]) for k in required - {'soc', 'policy'}}
    require(all(p.parent == paths['basis_input'].parent for p in paths.values()),
            'basis input, native PM, log and exit evidence must belong to the same successful run')
    require(paths['basis_file'].name == PM, 'basis_file must be native local_mode_PM.dat')
    doc = FDF(paths['basis_input'])
    context = soc_context(doc, spec, request.parent)
    policy_rows = context['special_SOC']
    soc_evidence = context['source_evidence']
    gate_receipt = None
    execution = None
    if context['manual_study'] is None:
        from search_inputs import execution_evidence, check_launch
        require(spec.get('basis_execution_receipt'), 'automatic encoding requires same-run basis execution receipt')
        execution_path = source(request.parent, spec['basis_execution_receipt'])
        require(execution_path.parent == paths['basis_input'].parent, 'execution receipt is from another basis run')
        execution = execution_evidence(execution_path)
        gate_receipt = load(execution_path.parent / 'basis-gate.json')
        require(gate_receipt['soc_policy']['policy_sha256'] == context['policy_sha256'],
                'basis launch/encoding SOC policy mismatch')
        require(execution['sha256'].get(PM) == digest(paths['basis_file'].read_bytes()),
                'basis artifact missing or different from actual execution receipt')
        files_hash = package_hashes(doc, spec, request.parent)
        require(set(spec.get('dependencies', {})) == set(files_hash),
                'encoding must package exactly the declared basis dependencies')
        for name, dependency in spec['dependencies'].items():
            require(digest(source(request.parent, dependency).read_bytes()) == files_hash[name],
                    f'encoding dependency differs from basis: {name}')
    require(not any(e.key == label('local_mode.poscar_files') for e in doc.entries),
            'poscar_files route unsupported by the per-sample spin runner')
    observed = runtime_check(paths['basis_log'].read_text(), int(paths['basis_exit_code_file'].read_text().strip()))
    raw_basis = paths['basis_file'].read_bytes()
    width = native_width(raw_basis)
    replaced = {k: [e.origin for e in doc.entries if e.key == label(k)] for k in CONTROLS}
    doc.replace(CONTROLS[0], CONTROLS[0] + ' 6\n')
    doc.replace(CONTROLS[1], CONTROLS[1] + (' T\n' if spec['policy'] == 'reuse' else ' F\n'))
    doc.replace(CONTROLS[2], CONTROLS[2] + ' 1\n')
    files = {'PASP.input': doc.text().encode(), PM: raw_basis}
    for name, path in spec.get('dependencies', {}).items():
        require(name not in files and name != 'method6-preparation.json', 'dependency name collision')
        require(Path(name).name not in {'distortion.pos', 'distortion.MAGMOM', 'distortion.ene_symbol',
                                       'pre-run.json', 'encoding_identity.json', 'source_identity.json',
                                       'log.out', 'exit.code', 'result.json'}, 'reserved runtime dependency name')
        files[name] = source(request.parent, path).read_bytes()
    return write_package(root, files, 'method6-preparation.json', {
        'scope': 'single-atom spin FDF controls, native basis identity and runtime mode/feature gates',
        'policy': spec['policy'], 'soc': spec['soc'], 'special_SOC': policy_rows or [],
        'interaction_type_mapping': context['mapping']['interaction_types'] if context['mapping'] else None, 'feature_count': width,
        'soc_evidence': soc_evidence, 'soc_policy': context,
        'soc_policy_sha256': context['policy_sha256'], 'basis_execution_receipt': execution,
        'basis_gate_receipt': gate_receipt,
        'basis_sha256': digest(raw_basis), 'source_sha256': doc.hashes,
        'runtime_evidence_sha256': {k: digest(p.read_bytes()) for k, p in paths.items()},
        'replaced_declarations': replaced, 'basis_observation': observed,
        'unresolved': ['structure/primitive/site mapping', 'physical basis suitability',
                       'warnings require contextual review', 'installed executable equivalence',
                       'other keyword-controlled dependencies']})


def checked_template(path):
    path = Path(path).resolve()
    receipt = load(path / 'method6-preparation.json')
    policy = dict(receipt['soc_policy'])
    pinned = policy.pop('policy_sha256')
    require(pinned == receipt['soc_policy_sha256'] == digest(json_bytes(policy)),
            'template SOC provenance identity changed')
    files = {}
    for name, expected in receipt['sha256'].items():
        raw = source(path, name).read_bytes()
        require(digest(raw) == expected, f'template changed: {name}')
        files[name] = raw
    doc = FDF(path / 'PASP.input')
    check(doc, receipt['soc'], receipt.get('special_SOC') or None,
          receipt.get('interaction_type_mapping'), 'T' if receipt['soc'] == 'restricted' else None)
    require(one(doc.values(CONTROLS[0], False), CONTROLS[0]) == '6', 'not method 6')
    require(logical(doc.values(CONTROLS[1], False)) == (receipt['policy'] == 'reuse'), 'reuse policy changed')
    require(one(doc.values(CONTROLS[2], False), CONTROLS[2]) == '1', 'nstr_random changed')
    require(native_width(files[PM]) == receipt['feature_count'], 'native feature width changed')
    require(digest(files[PM]) == receipt['basis_sha256'], 'native basis changed')
    return receipt, files


def stage_samples(inventory, ids, root, template_files, preparation=None):
    inventory = Path(inventory).resolve()
    receipt = load(inventory)
    rows = {identifier(s['id']): s for s in receipt['samples']}
    require(len(rows) == len(receipt['samples']), 'duplicate inventory IDs')
    require(set(ids) == set(rows), 'batch must cover the complete inventoried ID set')
    packages = []
    # Validate every source before staging; capture the inputs before execution.
    for sid in ids:
        row = rows[sid]
        ledger_path = source(inventory.parent, row['source_identity'])
        require(digest(ledger_path.read_bytes()) == receipt['sha256'][row['source_identity']], 'source ledger changed')
        ledger = load(ledger_path)
        require(identifier(ledger['original_id']) == sid, 'source ID mismatch')
        outcar = source(ledger_path.parent, ledger['outcar'])
        require(digest(outcar.read_bytes()) == ledger['outcar_sha256'], 'source OUTCAR changed')
        used, canonical = {}, {}
        for role, filename in [('structure', 'distortion.pos'), ('magnetic_state', 'distortion.MAGMOM')]:
            p = source(ledger_path.parent, ledger[role])
            canonical[role] = str(p)
            raw = p.read_bytes()
            require(digest(raw) == receipt['sha256'][os.path.relpath(p, inventory.parent)], 'final-state package changed')
            used[filename] = raw
        packages.append((sid, outcar, canonical, used))
    if preparation and preparation['soc_policy']['manual_study'] is None:
        observed = {(str(outcar), digest(outcar.read_bytes())) for _, outcar, _, _ in packages}
        expected = {(str(Path(row['path']).resolve()), row['sha256']) for row in
                    preparation['soc_policy']['source_evidence']['sources']}
        require(observed == expected, 'encoding source corpus differs from basis LSORBIT evidence')
    root.mkdir(parents=True, exist_ok=False)
    samples = []
    for sid, outcar, canonical, used in packages:
        run = root / str(sid)
        run.mkdir()
        for name, raw in {**template_files, **used}.items():
            p = run / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        pre = {role: digest((run / name).read_bytes()) for role, name in
               [('structure', 'distortion.pos'), ('magnetic_state', 'distortion.MAGMOM'), ('basis', PM)]}
        if preparation:
            pre['soc_policy'] = preparation['soc_policy_sha256']
        (run / 'source_identity.json').write_bytes(json_bytes({'original_id': sid, 'outcar': str(outcar), **canonical}))
        (run / 'pre-run.json').write_bytes(json_bytes({'original_id': sid, 'sha256': pre}))
        samples.append((sid, run, pre))
    return samples


def check_result(item, receipt):
    sid, run, pre = item
    row = {'id': sid, 'status': 'failed', 'reason': ''}
    try:
        code = int((run / 'exit.code').read_text().strip())
        observed = runtime_check((run / 'log.out').read_text(errors='replace'), code)
        require(observed['expanded_mode_count'] == receipt['basis_observation']['expanded_mode_count'],
                'actual expanded mode count differs from the successful basis run')
        require(digest((run / PM).read_bytes()) == receipt['basis_sha256'],
                'native basis changed; equal parameter counts do not prove identity')
        for role, name in [('structure', 'distortion.pos'), ('magnetic_state', 'distortion.MAGMOM')]:
            require(digest((run / name).read_bytes()) == pre[role], 'encoding input changed during execution')
        require(digest((run / 'PASP.input').read_bytes()) == receipt['sha256']['PASP.input'],
                'effective encoding input changed during execution')
        for name, expected in receipt['sha256'].items():
            if name not in {'PASP.input', PM}:
                require(digest((run / name).read_bytes()) == expected,
                        f'encoding dependency changed during execution: {name}')
        require(len(features(run / 'distortion.ene_symbol')) == receipt['feature_count'],
                'feature width differs from native basis')
        row['observation'] = observed
        require(not observed['warnings'], 'runtime warnings need contextual review before acceptance')
        require(pre.get('soc_policy') == receipt['soc_policy_sha256'], 'encoding SOC policy identity mismatch')
        encoding = {'original_id': sid, 'soc_policy_sha256': receipt['soc_policy_sha256'],
                    'special_SOC': receipt['special_SOC'], 'structure': 'distortion.pos', 'magnetic_state': 'distortion.MAGMOM',
                    'sha256': {**pre, 'features': digest((run / 'distortion.ene_symbol').read_bytes())}}
        (run / 'encoding_identity.json').write_bytes(json_bytes(encoding))
        row['status'] = 'ok'
    except (OSError, ValueError, TypeError, KeyError) as exc:
        row['reason'] = str(exc)
    (run / 'result.json').write_bytes(json_bytes(row))
    return row


def run_one(item, command, timeout, receipt):
    sid, run, pre = item
    try:
        for name, expected in receipt['sha256'].items():
            require(digest((run / name).read_bytes()) == expected, f'pre-execution template changed: {name}')
        require(pre.get('soc_policy') == receipt['soc_policy_sha256'], 'pre-execution SOC identity mismatch')
        with (run / 'log.out').open('wb') as out:
            try:
                process = subprocess.Popen(command, cwd=run, stdout=out, stderr=subprocess.STDOUT,
                                           start_new_session=True)
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                code = 124
                # The supplied launcher may have a PASP child. Stop its entire
                # process group so a timed-out run cannot continue changing files.
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                out.write(b'\nRUNNER TIMEOUT: outputs are not accepted.\n')
        (run / 'exit.code').write_text(str(code) + '\n')
        return check_result(item, receipt)
    except (OSError, ValueError) as exc:
        row = {'id': sid, 'status': 'failed', 'reason': f'launcher did not start: {exc}'}
        (run / 'result.json').write_bytes(json_bytes(row))
        return row


def stage(request, helper_run=False):
    request = Path(request).resolve()
    spec = load(request)
    required = {'template', 'inventory', 'ids', 'root'}
    if helper_run:
        required |= {'command', 'timeout_seconds', 'jobs'}
    require(set(spec) == required, 'stage/batch request fields must be explicit')
    require(isinstance(spec['ids'], list) and spec['ids'], 'nonempty explicit IDs required')
    ids = [identifier(s) for s in spec['ids']]
    require(len(ids) == len(set(ids)), 'duplicate batch IDs')
    if helper_run:
        require(isinstance(spec['jobs'], int) and not isinstance(spec['jobs'], bool) and spec['jobs'] > 0,
                'jobs must be a positive integer')
        command = spec['command']
        require(isinstance(command, list) and command and all(isinstance(s, str) and s for s in command),
                'command must be an argv list, never shell text')
        require(number(spec['timeout_seconds']) > 0, 'positive explicit timeout required')
    template = Path(spec['template'])
    template = (request.parent / template).resolve() if not template.is_absolute() else template.resolve()
    require(template.is_dir(), f'missing template directory: {template}')
    inventory = source(request.parent, spec['inventory'])
    root = Path(spec['root'])
    root = (request.parent / root).resolve() if not root.is_absolute() else root.resolve()
    require(not root.exists(), 'use a new batch root; preserve failed/partial attempts')
    receipt, files = checked_template(template)
    samples = stage_samples(inventory, ids, root, files, receipt)
    (root / 'batch-plan.json').write_bytes(json_bytes({
        'runtime_owner': 'helper' if helper_run else 'controller', 'request': spec,
        'preparation': receipt, 'template_sha256': digest((template / 'method6-preparation.json').read_bytes()),
        'inventory_sha256': digest(inventory.read_bytes())}))
    return root, samples, receipt, spec


def summarize(root, rows, ids):
    plan = load(root / 'batch-plan.json')
    result = {'scope': 'mechanical encoding evidence; not scientific acceptance',
              **plan, 'results': rows, 'complete': all(r['status'] == 'ok' for r in rows),
              'samples': [{'id': sid, 'original_id': sid, 'features': f'{sid}/distortion.ene_symbol',
                           'basis_file': f'{sid}/{PM}', 'log': f'{sid}/log.out', 'exit_code_file': f'{sid}/exit.code',
                           'source_identity': f'{sid}/source_identity.json',
                           'encoding_identity': f'{sid}/encoding_identity.json'} for sid in ids]}
    (root / 'batch.json').write_bytes(json_bytes(result))
    (root / 'status.tsv').write_text('sample_id\tstatus\n' + ''.join(f"{r['id']}\t{r['status']}\n" for r in rows))
    return result


def collect(root):
    root = Path(root).resolve()
    plan = load(root / 'batch-plan.json')
    ids = plan['request']['ids']
    rows = []
    for sid in ids:
        run = root / str(sid)
        pre = load(run / 'pre-run.json')
        require(pre['original_id'] == sid, 'pre-run ID changed')
        rows.append(check_result((sid, run, pre['sha256']), plan['preparation']))
    return summarize(root, rows, ids)


def batch(request):
    root, samples, receipt, spec = stage(request, helper_run=True)
    ids, command, timeout = spec['ids'], spec['command'], number(spec['timeout_seconds'])
    rows = [run_one(samples[0], command, timeout, receipt)]
    if rows[0]['status'] == 'ok':
        with ThreadPoolExecutor(max_workers=min(spec['jobs'], len(samples))) as pool:
            rows.extend(pool.map(lambda item: run_one(item, command, timeout, receipt), samples[1:]))
    else:
        rows.extend({'id': sid, 'status': 'not_run', 'reason': 'first-sample probe failed; no automatic retry'}
                    for sid in ids[1:])
    return summarize(root, rows, ids)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    q = sub.add_parser('prepare')
    q.add_argument('--request', type=Path, required=True)
    q.add_argument('--root', type=Path, required=True)
    for action in ('stage', 'batch'):
        q = sub.add_parser(action)
        q.add_argument('--request', type=Path, required=True)
    q = sub.add_parser('collect')
    q.add_argument('--root', type=Path, required=True)
    args = p.parse_args()
    if args.action == 'prepare':
        result = prepare(args.request, args.root)
    elif args.action == 'stage':
        root, samples, receipt, spec = stage(args.request)
        result = {'status': 'staged', 'root': str(root), 'sample_count': len(samples), 'runtime_owner': 'controller'}
    elif args.action == 'collect':
        result = collect(args.root)
    else:
        result = batch(args.request)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result.get('complete', True) else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        sys.exit(1)
