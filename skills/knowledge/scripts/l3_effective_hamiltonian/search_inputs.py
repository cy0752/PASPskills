#!/usr/bin/env python3
"""Deterministic basis-input preparation and gated helper-owned local launches."""
from pathlib import Path
import argparse
import json
import sys
import os
import signal
import subprocess
import time
import re

from prepare_l3 import (FDF, check, positive_int, soc_context, package_hashes,
                        label, logical, mapped_soc, radius_controls, comparable_soc)
from study_contract import (destination, digest, json_bytes, load, number,
                            require, source, write_package)


def immutable(path, data):
    path = Path(path)
    with path.open('xb') as stream:
        stream.write(data)
    path.chmod(0o444)


def execution_evidence(path, seen=()):
    """Verify recorded process attempt, actual input and lineage, not a status label.

    This is an integrity/audit check, not cryptographic attestation against an actor
    able to rewrite an entire evidence tree. External/controller processes without
    this receipt protocol are unsupported for automatic predecessor authorization.
    """
    path = Path(path).resolve()
    require(path not in seen and len(seen) < 64, 'cyclic/overlong predecessor lineage')
    record = load(path)
    require(record.get('schema') == 'basis-execution-v1' and record.get('status') == 'executed',
            'missing wrapper execution receipt (self-attested status is insufficient)')
    run = path.parent
    hashes = record.get('sha256')
    mandatory = {'basis-gate.json', 'basis-effective.input', 'basis-process.json', 'exit.code', 'log.out'}
    if (run / 'local_mode_PM.dat').exists():
        mandatory.add('local_mode_PM.dat')
    require(isinstance(hashes, dict) and mandatory <= set(hashes),
            'incomplete execution evidence hashes')
    for name, expected in record['sha256'].items():
        require(Path(name).name == name, 'invalid execution evidence path')
        require(digest((run / name).read_bytes()) == expected, f'execution evidence hash mismatch: {name}')
    gate = load(run / 'basis-gate.json')
    process = load(run / 'basis-process.json')
    require(process['pid'] > 0 and number(process['ended_epoch']) >= number(process['started_epoch']) and
            number(process['duration_seconds']) >= 0 and process['command'] and
            process['effective_input_sha256'] == gate['effective_input_sha256'] and
            process['gate_sha256'] == record['sha256']['basis-gate.json'] and
            int((run / 'exit.code').read_text()) == process['returncode'], 'invalid process/gate/exit evidence')
    log = (run / 'log.out').read_text(errors='replace')
    require('Property Analysis and Simulation Package for materials (PASP)' in log and
            re.search(r'^\s*PASP start\s*$', log, re.M),
            'process log does not establish an attempted native PASP run')
    require(record['effective_input_sha256'] == gate['effective_input_sha256'] ==
            digest((run / 'basis-effective.input').read_bytes()), 'execution input snapshot mismatch')
    doc = FDF(run / 'PASP.input')
    require(digest(doc.text().encode()) == record['effective_input_sha256'], 'executed effective input changed')
    require(doc.hashes == gate['source_sha256'], 'executed input/include source changed')
    for name, expected in gate['package_sha256'].items():
        require(digest((run / name).read_bytes()) == expected, f'executed package changed: {name}')
    body, _, values = radius_controls(doc)
    require(body == gate.get('body_order') == record.get('body_order'),
            'execution body count differs from actual input/gate')
    require(number(process.get('gate_created_epoch')) <= number(process['started_epoch']) and
            number(process.get('snapshot_created_epoch')) <= number(process['started_epoch']) and
            (run / 'basis-gate.json').stat().st_mtime <= number(process['started_epoch']) and
            (run / 'basis-effective.input').stat().st_mtime <= number(process['started_epoch']),
            'execution gate/snapshot must predate process; post-hoc mirror is not launch evidence')
    require(values[0] == 1 and values[1] == gate['cutoff_bohr'] == record['cutoff_bohr'],
            'predecessor cutoff/input mismatch')
    if gate['status'] in ('reduction_authorized', 'body_radius_comparison_authorized'):
        prior = execution_evidence(gate['predecessor']['receipt'], (*seen, path))
        require((gate['status'] != 'reduction_authorized' or prior['cutoff_bohr'] > record['cutoff_bohr']) and
                digest(Path(gate['predecessor']['receipt']).read_bytes()) == gate['predecessor']['sha256'],
                'predecessor lineage mismatch')
    else:
        require(gate['status'] == 'initial_15_bohr' and record['cutoff_bohr'] == 15 and body == 2,
                'automatic lineage must begin with an executed 15 Bohr pair candidate')
    return record


def check_launch(input_path, predecessor_ledger=None, receipt=None, policy_request=None):
    """Mandatory gate on the SAME actual run, including copied/manual inputs."""
    doc = FDF(Path(input_path).resolve())
    require(policy_request, 'basis launch needs --policy-request; raw automatic launches unsupported')
    policy_request = Path(policy_request).resolve()
    spec = load(policy_request)
    files = package_hashes(doc, spec, policy_request.parent)
    for name, expected in files.items():
        require(digest((doc.cwd / name).read_bytes()) == expected, f'actual launch dependency mismatch: {name}')
    policy = soc_context(doc, spec, policy_request.parent, files)
    body = positive_int(doc.values('fig.maxk', False)[0])
    power = positive_int(doc.values('Invariant.power', False)[0])
    if policy['manual_study'] is None:
        body = positive_int(doc.values('fig.maxk', False)[0])
        power = positive_int(doc.values('Invariant.power', False)[0])
        require(body <= 4 and power <= 4,
                'automatic body/order beyond four is unsupported by this bounded route; preserve evidence and stop')
    for key in ('local_mode.cal_para_method', 'local_mode.read_interaction'):
        values_control = [e for e in doc.entries if e.key == label(key)]
        require(len(values_control) <= 1, f'duplicate/shadowed basis control: {key}')
    if any(e.key == 'localmodecalparamethod' for e in doc.entries):
        require(doc.values('local_mode.cal_para_method', False) == ['1'], 'automatic basis launch requires method 1')
    if any(e.key == 'localmodereadinteraction' for e in doc.entries):
        require(not logical(doc.values('local_mode.read_interaction', False)),
                'fresh automatic basis must not read an old native interaction file')
    entries = [e for e in doc.entries if e.key == 'figmdist']
    require(len(entries) == 1, 'effective input must contain exactly one fig.mdist declaration')
    require(entries[0].block, 'fig.mdist must be a block')
    values = [number(v) for v in doc.values('fig.mdist', True)]
    require(len(values) >= 2 and values[0] == 1, 'fig.mdist must start with enabling flag 1 and a two-body cutoff')
    cutoff = values[1]
    require(cutoff > 0, 'positive two-body cutoff required')
    prior = None
    if policy['manual_study']:
        status = 'manual_study'
    elif cutoff == 15 and body == 2 and not predecessor_ledger:
        status = 'initial_15_bohr'
    else:
        require(cutoff <= 15 and predecessor_ledger,
                'first automatic basis input must use 15 Bohr pairs; successors need executed predecessor')
        predecessor_ledger = Path(predecessor_ledger).resolve()
        ledger = load(predecessor_ledger)
        attempts = ledger if isinstance(ledger, list) else ledger.get('attempts')
        require(isinstance(attempts, list), 'predecessor ledger must contain attempts')
        # Every verified chain starts at 15. A same-pair-radius body successor
        # may use its immediate predecessor after an earlier pair reduction.
        candidates = [r for r in attempts if r.get('status') == 'executed']
        require(candidates, 'successor needs executed lineage from the larger-radius 15 Bohr pair start')
        for row in reversed(candidates):
            path = source(predecessor_ledger.parent, row.get('receipt', ''))
            evidence = execution_evidence(path)
            require(evidence['effective_input_sha256'] == row.get('effective_input_sha256') and
                    evidence['cutoff_bohr'] == row['cutoff_bohr'], 'predecessor receipt hash/cutoff does not match ledger')
            old_policy = load(path.parent / 'basis-gate.json')['soc_policy']
            if policy.get('stage', {}).get('stage') == 'initial' or policy['soc'] == 'off':
                comparable_soc(old_policy, policy)
            old_body, old_power, old_radii = radius_controls(FDF(path.parent / 'PASP.input'))
            if policy.get('stage', {}).get('stage') == 'initial' or policy['soc'] == 'off':
                require(power == old_power and body <= old_body + 1,
                        'keep expansion fixed; progressively add three then four bodies')
                if body > old_body:
                    require(all(r < 15 for r in values[old_body:body]),
                            'three/four-body starts must be smaller than 15 Bohr')
                changes = int(body != old_body) + sum(a != b for a, b in zip(values[1:body], old_radii[1:old_body]))
                require(changes <= 1 or isinstance(row.get('confounders'), str) and row['confounders'].strip(),
                        'multiple body/radius changes need declared confounders')
            require(isinstance(row.get('reduction_reason'), str) and row['reduction_reason'].strip(),
                    'document actual larger-radius outcome and reason for reduction')
            prior = {'receipt': str(path), 'sha256': digest(path.read_bytes()), 'reason': row['reduction_reason']}
            break
        status = 'reduction_authorized' if cutoff < evidence['cutoff_bohr'] else 'body_radius_comparison_authorized'
    result = {'status': status, 'cutoff_bohr': cutoff, 'body_order': body, 'predecessor': prior,
              'effective_input_sha256': digest(doc.text().encode()),
              'resolved_fig_mdist': values, 'source_sha256': doc.hashes,
              'package_sha256': files, 'soc_policy': policy,
              'policy_request_sha256': digest(policy_request.read_bytes())}
    if receipt:
        immutable(receipt, json_bytes(result))
    return result


def launch(request):
    """Helper-owned local argv wrapper. Controller-owned runtime uses check-launch
    as a handoff gate, but cannot claim this execution protocol without receipts.
    """
    request = Path(request).resolve()
    spec = load(request)
    require(set(spec) <= {'input', 'policy_request', 'predecessor_ledger', 'command', 'timeout_seconds'} and
            {'input', 'policy_request', 'command', 'timeout_seconds'} <= set(spec), 'invalid launch request')
    path = source(request.parent, spec['input'])
    run = path.parent
    require(path.name == 'PASP.input', 'launcher consumes actual PASP.input')
    require(not (run / 'local_mode_PM.dat').exists(), 'fresh basis launch must not inherit a cached native PM')
    command = spec['command']
    require(isinstance(command, list) and command and all(isinstance(x, str) and x for x in command),
            'launcher requires argv, never shell text')
    timeout = number(spec['timeout_seconds'])
    require(timeout > 0, 'positive bounded timeout required')
    for name in ('basis-gate.json', 'basis-effective.input', 'basis-process.json', 'basis-execution.json', 'log.out', 'exit.code'):
        require(not (run / name).exists(), f'preserve old run; launch artifact already exists: {name}')
    policy = source(request.parent, spec['policy_request'])
    ledger = source(request.parent, spec['predecessor_ledger']) if spec.get('predecessor_ledger') else None
    gate = check_launch(path, ledger, run / 'basis-gate.json', policy)
    immutable(run / 'basis-effective.input', FDF(path).text().encode())
    # Close the preparation/launch gap before spawning the process.
    require(check_launch(path, ledger, policy_request=policy) == gate, 'actual input/policy changed before execution')
    start, tick = time.time(), time.monotonic()
    with (run / 'log.out').open('xb') as out:
        process = subprocess.Popen(command, cwd=run, stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            code = 124
            out.write(b'\nRUNNER TIMEOUT: outputs are not accepted.\n')
    immutable(run / 'exit.code', (str(code) + '\n').encode())
    immutable(run / 'basis-process.json', json_bytes({'pid': process.pid, 'command': command,
        'started_epoch': start, 'ended_epoch': time.time(), 'duration_seconds': time.monotonic() - tick,
        'returncode': code, 'effective_input_sha256': gate['effective_input_sha256'],
        'gate_created_epoch': (run / 'basis-gate.json').stat().st_mtime,
        'snapshot_created_epoch': (run / 'basis-effective.input').stat().st_mtime,
        'gate_sha256': digest((run / 'basis-gate.json').read_bytes()),
        'scope': 'observed launcher process interval, not direct PASP timing qualification'}))
    names = ['basis-gate.json', 'basis-effective.input', 'basis-process.json', 'exit.code', 'log.out']
    if (run / 'local_mode_PM.dat').exists():
        names.append('local_mode_PM.dat')
    record = {'schema': 'basis-execution-v1', 'status': 'executed', 'cutoff_bohr': gate['cutoff_bohr'],
              'body_order': gate['body_order'],
              'effective_input_sha256': gate['effective_input_sha256'],
              'sha256': {n: digest((run / n).read_bytes()) for n in names}}
    immutable(run / 'basis-execution.json', json_bytes(record))
    # Manual studies have separate authorization, not automatic predecessor lineage.
    if gate['status'] != 'manual_study':
        execution_evidence(run / 'basis-execution.json')
    require(code == 0, f'launcher exit {code}; preserve attempted-run evidence, do not accept outputs')
    return record


def prepare(manifest, root):
    manifest = Path(manifest).resolve()
    spec = load(manifest)
    required = {'input', 'soc', 'files', 'higher_body_cutoffs_bohr',
                'one_body_cutoff_bohr', 'candidates'}
    require(required <= set(spec), 'missing request fields')
    require(spec['soc'] in ('full', 'off', 'restricted'), 'unsupported SOC policy')
    input_path = source(manifest.parent, spec['input'])
    doc = FDF(input_path)
    # Policy is revalidated per generated physical candidate, not just the template.
    require(isinstance(spec['files'], dict), 'files must map package names to sources')
    require({'cell.str', 'unit_cell.str'} <= set(spec['files']), 'cell files required')
    files = {}
    for name, src in spec['files'].items():
        destination(Path(root), name)  # Validate names without creating output.
        require(Path(name).parent == Path('.') and name not in
                ('PASP.input', 'search-inputs.json', 'local_mode_PM.dat') and
                not name.endswith('.ene_symbol'), 'only flat declared input dependencies allowed')
        files[name] = source(manifest.parent, src).read_bytes()
        require(bool(files[name].strip()), 'empty declared input dependency')
    one = number(spec['one_body_cutoff_bohr'])
    require(one > 0, 'positive one-body cutoff required')
    higher = spec['higher_body_cutoffs_bohr']
    require(isinstance(higher, dict) and set(higher) == {'3', '4'},
            'declare three/four-body cutoffs explicitly')
    higher = {k: number(v) for k, v in higher.items()}
    require(all(0 < v <= 15 for v in higher.values()), 'higher-body cutoffs must be positive and at most 15 Bohr')
    candidates = spec['candidates']
    require(isinstance(candidates, list) and 0 < len(candidates) <= (12 if spec.get('automatic', True) else 64),
            'bounded nonempty candidate list required')
    outputs, rows, seen, previous = {}, [], set(), None
    previous_policy = None
    for ordinal, config in enumerate(candidates):
        require(isinstance(config, dict) and
                {'body_order', 'expansion_order', 'two_body_cutoff_bohr'} <= set(config) <=
                {'body_order', 'expansion_order', 'two_body_cutoff_bohr', 'soc_mapping', 'higher_body_cutoffs_bohr', 'confounders'}, 'invalid candidate fields')
        body = positive_int(config['body_order'])
        power = positive_int(config['expansion_order'])
        cutoff = number(config['two_body_cutoff_bohr'])
        require(2 <= body <= 4 and 1 <= power <= 4, 'automatic body/order bounds exceeded')
        require(0 < cutoff <= 15, 'two-body cutoff must be positive and at most 15 Bohr')
        candidate_higher = {**higher, **config.get('higher_body_cutoffs_bohr', {})}
        require(set(candidate_higher) == {'3', '4'}, 'unsupported higher-body cutoff key')
        candidate_higher = {k: number(v) for k, v in candidate_higher.items()}
        require(all(0 < v <= 15 for v in candidate_higher.values()), 'higher-body radius maximum is 15 Bohr')
        distances = [one, cutoff] + [candidate_higher[str(k)] for k in range(3, body + 1)]
        mapping_name = config.get('soc_mapping', spec.get('soc_mapping'))
        key = (body, power, tuple(distances), mapping_name)
        require(key not in seen, 'duplicate candidate')
        seen.add(key)
        if spec.get('automatic', True):
            require(one == 1, 'fig.mdist first value is enabling flag 1, not a one-body radius')
            if previous is None:
                require(body == 2 and cutoff == 15, 'begin automatic search with 15 Bohr pairs')
            else:
                pb, pp, pd, pm = previous
                require(power == pp and body <= pb + 1, 'keep expansion fixed; progressively add three then four bodies')
                changes = int(body != pb) + sum(a != b for a, b in zip(distances[1:], pd[1:]))
                require(changes <= 1 or isinstance(config.get('confounders'), str) and config['confounders'].strip(),
                        'multiple body/radius changes need declared confounders')
                if body > pb:
                    require(all(r < 15 for r in distances[pb:body]), 'higher-body starts must be smaller than 15 Bohr')
        previous = key
        candidate = FDF(input_path)
        candidate.replace('fig.maxk', f'fig.maxk {body}\n')
        candidate.replace('Invariant.power', f'Invariant.power {power}\n')
        candidate.replace('fig.mdist', '%block fig.mdist\n' +
                          ' '.join(f'{v:.16g}' for v in distances) + '\n%endblock fig.mdist\n')
        raw = candidate.text().encode()
        resolved = FDF.__new__(FDF)
        resolved.cwd, resolved.hashes = candidate.cwd, candidate.hashes
        resolved.entries = resolved.parse(candidate.text(), Path('<generated>'), ())
        candidate_spec = dict(spec)
        if mapping_name is not None:
            candidate_spec['soc_mapping'] = mapping_name
        if spec['soc'] == 'restricted':
            require(candidate_spec.get('soc_mapping'), 'restricted candidate requires compatible SOC mapping')
            mapping = mapped_soc(resolved, source(manifest.parent, candidate_spec['soc_mapping']),
                                 {k: digest(v) for k, v in files.items()})
            candidate.replace('local_mode.special_SOC', '%block local_mode.special_SOC\n' +
                              str(len(mapping['selected'])) + '\n' +
                              ''.join(' '.join(map(str, row)) + '\n' for row in mapping['selected']) +
                              '%endblock local_mode.special_SOC\n')
            resolved.entries = resolved.parse(candidate.text(), Path('<generated>'), ())
            raw = candidate.text().encode()
        context = soc_context(resolved, candidate_spec, manifest.parent,
                              {k: digest(v) for k, v in files.items()})
        if previous_policy is not None and context['manual_study'] is None:
            comparable_soc(previous_policy, context)
        previous_policy = context
        gate = {'status': 'prepared_not_executed_requires_actual_launch_gate',
                'cutoff_bohr': cutoff, 'effective_input_sha256': digest(raw)}
        physics = {'body_order': body, 'expansion_order': power,
                   'cutoffs_bohr': distances, 'soc': spec['soc'],
                   'special_SOC': context['special_SOC'], 'soc_policy_sha256': context['policy_sha256']}
        identity = digest(json_bytes({'physics': physics, 'input_sha256': digest(raw),
                                     'files': {k: digest(v) for k, v in files.items()}}))
        name = f'{ordinal + 1:02d}-{identity[:12]}'
        outputs[f'{name}/PASP.input'] = raw
        outputs.update({f'{name}/{k}': v for k, v in files.items()})
        rows.append({'directory': name, 'physics': physics, 'cutoff_gate': gate,
                     'soc_policy': context,
                     'configuration_sha256': identity,
                     'predecessor': rows[-1]['configuration_sha256'] if rows else None,
                     'status': 'prepared_not_executed', 'feature_count': None,
                     'parameter_count': None, 'conditioning': None, 'train_r2': None,
                     'selection_r2': None, 'qualified_non_pasp_seconds': None,
                     'skip_term_mapping': None, 'failure_reason': None,
                     'cache_decision': 'fresh basis and full re-encoding required'})
    receipt = {'scope': 'bounded candidate order, FDF replacement, dependency bytes and hashes only',
               'request': spec,
               'manifest_sha256': digest(manifest.read_bytes()), 'source_sha256': doc.hashes,
               'soc_policy': context, 'candidates': rows,
               'execution_requirements': [
                   'Evaluate predecessor before running the next candidate; record actual results.',
                   'Fresh native basis and full encoding on every physics change.',
                   'Full train+selection dependency check and current native skip mapping.',
                   'Full original width gate, check-fit before EVERY fit, native fit_handoff.',
                   'Freeze model before test; complete consumer-root publish and verify.'],
               'not_covered': ['physical suitability', 'general FDF dependencies',
                               'native execution', 'accuracy', 'safe cache reuse', 'scientific acceptance'],
               'launch_gate': 'check_launch must run on the actual resolved input before every basis PASP launch; lower cutoffs require an executed predecessor receipt'}
    return write_package(Path(root).resolve(), outputs, 'search-inputs.json', receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--launch-request', type=Path)
    parser.add_argument('--policy-request', type=Path)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--check-launch-input', type=Path)
    parser.add_argument('--predecessor-ledger', type=Path)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    try:
        if args.launch_request:
            result = launch(args.launch_request)
        elif args.check_launch_input:
            result = check_launch(args.check_launch_input, args.predecessor_ledger, args.receipt, args.policy_request)
        else:
            require(args.manifest and args.root, '--manifest and --root are required for preparation')
            result = prepare(args.manifest, args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}), file=sys.stderr)
        return 1
    if args.check_launch_input or args.launch_request:
        print(json.dumps(result, indent=2, allow_nan=False))
    else:
        print(json.dumps({'status': 'prepared_not_executed', 'count': len(result['candidates'])}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
