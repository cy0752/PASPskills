"""Synthetic basis-input regressions; no PASP or scientific validation."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from prepare_l3 import FDF, check
from search_inputs import prepare, check_launch, launch, execution_evidence
from study_contract import verify
from test_prepare_l3 import BASE, MODE, SPECIAL, restricted_fixture, manual_authority, pin_identity


class SearchInputsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.input = self.root / 'source.input'
        self.input.write_text(BASE + MODE + 'fig.maxk 2\nfig.maxk 6\n'
                              'Invariant.power 2\nInvariant.power 6\n'
                              '%block fig.mdist\n1 3\n%endblock fig.mdist\n'
                              '# preserve explicit seed\nlocal_mode.seed 17\n')
        for name in ('cell.str', 'unit_cell.str'):
            (self.root / name).write_text('synthetic dependency; not a physical cell\n')
        (self.root / 'manual.json').write_text(json.dumps({'mode': 'manual_study', 'soc': 'full',
            'authorization': 'explicit synthetic manual request', 'reason': 'generator format compatibility'}))
        manual_authority(self, self.root, 'full')
        self.spec = {'automatic': False, 'input': 'source.input', 'soc': 'full', 'manual_study': 'manual.json',
                     'files': {name: name for name in ('cell.str', 'unit_cell.str')},
                     'one_body_cutoff_bohr': 1, 'higher_body_cutoffs_bohr': {'3': 7, '4': 5},
                     'candidates': [{'body_order': 4, 'expansion_order': 4,
                                     'two_body_cutoff_bohr': c} for c in (15, 14, 12, 10, 8)]}
        self.manifest = self.root / 'search.json'

    def run_prepare(self, out='out'):
        self.manifest.write_text(json.dumps(self.spec))
        return prepare(self.manifest, self.root / out)

    def test_deterministic_positional_cutoffs_and_shadow_removal(self):
        before = self.input.read_bytes()
        receipt = self.run_prepare()
        self.assertEqual(receipt['request'], self.spec)
        self.assertEqual(receipt, self.run_prepare())
        other = self.run_prepare('other')
        self.assertEqual(receipt, other)
        self.assertEqual(self.input.read_bytes(), before)
        for row, cutoff in zip(receipt['candidates'], (15, 14, 12, 10, 8)):
            path = self.root / 'out' / row['directory'] / 'PASP.input'
            doc = FDF(path)
            self.assertEqual(doc.values('fig.mdist', True), ['1', str(cutoff), '7', '5'])
            self.assertEqual(doc.values('fig.maxk', False), ['4'])
            self.assertEqual(doc.values('Invariant.power', False), ['4'])
            self.assertEqual(path.read_text().count('fig.maxk'), 1)
            self.assertEqual(path.read_text().count('Invariant.power'), 1)
            self.assertIn('local_mode.seed 17', path.read_text())
            self.assertEqual(check(doc, 'full')['mode_count'], 1)
            self.assertEqual(row['status'], 'prepared_not_executed')
            self.assertIsNone(row['qualified_non_pasp_seconds'])
        verify(self.root / 'out', 'search-inputs.json')

    def test_invalid_sequences_leave_no_partial_output(self):
        good = copy.deepcopy(self.spec)
        bad = [[{'body_order': 4, 'expansion_order': 4, 'two_body_cutoff_bohr': 0}],
               [dict(good['candidates'][0], two_body_cutoff_bohr=16)],
               [good['candidates'][0], good['candidates'][0]],
               [dict(good['candidates'][0], higher_body_cutoffs_bohr={'3': 16})],
               [good['candidates'][0], {'body_order': 5, 'expansion_order': 4,
                                      'two_body_cutoff_bohr': 15}],
               [good['candidates'][0], {'body_order': 4, 'expansion_order': 5,
                                      'two_body_cutoff_bohr': 15}], []]
        for candidates in bad:
            with self.subTest(candidates=candidates):
                self.spec = {**good, 'candidates': candidates}
                with self.assertRaises(ValueError):
                    self.run_prepare()
                self.assertFalse((self.root / 'out').exists())

    def test_order_then_body_reduction(self):
        self.spec['candidates'] += [{'body_order': 4, 'expansion_order': p,
                                    'two_body_cutoff_bohr': 8} for p in (3, 2, 1)]
        self.spec['candidates'] += [{'body_order': b, 'expansion_order': 1,
                                    'two_body_cutoff_bohr': 8} for b in (3, 2)]
        receipt = self.run_prepare()
        last = self.root / 'out' / receipt['candidates'][-1]['directory'] / 'PASP.input'
        self.assertEqual(FDF(last).values('fig.mdist', True), ['1', '8'])

    def test_smaller_base_and_early_order_reduction(self):
        self.spec['candidates'] = [dict(body_order=2, expansion_order=p,
                                        two_body_cutoff_bohr=15) for p in (3, 2)]
        receipt = self.run_prepare()
        self.assertEqual(receipt['candidates'][0]['physics']['body_order'], 2)
        self.assertEqual(receipt['candidates'][1]['physics']['expansion_order'], 2)

    def test_staged_policy_on_actual_copied_launch_input(self):
        f = restricted_fixture(self.root)
        mapping = json.loads((self.root / 'mapping.json').read_text())
        mapping.update(selected=[[1, 1, 4], [1, 2, 4], [2, 1, 4]],
                       type_limit=64, order_bound=4,
                       order_rationale=['unsupported complete SOC for R2'] * 3)
        (self.root / 'mapping.json').write_text(json.dumps(mapping))
        f['input'].write_text(f['input'].read_text().replace(SPECIAL,
            '%block local_mode.special_SOC\n3\n1 1 4\n1 2 4\n2 1 4\n%endblock local_mode.special_SOC\n'))
        pin_identity(self.root)
        with self.assertRaisesRegex(ValueError, 'initial SOC stage'):
            check_launch(f['input'], policy_request=f['policy'])

    def test_restricted_generator_writes_verified_targeted_order_two(self):
        f = restricted_fixture(self.root)
        self.spec = {**self.spec, **f['spec'], 'automatic': True, 'input': 'PASP.input',
                     'candidates': [dict(body_order=2, expansion_order=4, two_body_cutoff_bohr=15)]}
        self.spec.pop('manual_study')
        receipt = self.run_prepare()
        row = receipt['candidates'][0]
        actual = self.root / 'out' / row['directory'] / 'PASP.input'
        self.assertEqual(row['soc_policy']['mapping']['selected'], [(1, 1, 2), (1, 2, 2), (2, 1, 2)])
        self.assertIn(SPECIAL, actual.read_text())
        stage = check_launch(actual, policy_request=f['policy'])['soc_policy']['stage']
        self.assertEqual(stage['eligible_total_count'], 3)
        self.assertTrue(stage['availability_exception'])

    def test_ten_nonsequential_native_types_at_actual_launch_gate(self):
        from prepare_l3 import CLUSTER_MARKER
        from study_contract import digest
        f = restricted_fixture(self.root)
        ids = [2, 4, 7, 9, 11, 14, 18, 23, 28, 31, 35]
        log = "Property Analysis and Simulation Package for materials (PASP)\nPASP start\n"
        clusters = [(1, 0, 0, 0)] + [(i + 2, 1, kind, 2) for i, kind in enumerate(ids)]
        for ordinal, body, kind, power in clusters:
            log += CLUSTER_MARKER + f"{ordinal:5d}{body:3d}{kind:3d}{power:5d}{3:5d}{1:5d}{0:5d}\n"
        log += "Total number of different clusters: 12\nPASP is finished gracefully\n"
        (self.root / "map/log.out").write_text(log)
        mapping = json.loads((self.root / "mapping.json").read_text())
        mapping.update(selected=[[1, kind, 2] for kind in ids[:10]], type_limit=10,
                       order_rationale=["synthetic verified quadratic environment"] * 10)
        (self.root / "mapping.json").write_text(json.dumps(mapping))
        block = "%block local_mode.special_SOC\n10\n" + "".join(f"1 {kind} 2\n" for kind in ids[:10]) + "%endblock local_mode.special_SOC\n"
        f["input"].write_text(f["input"].read_text().replace(SPECIAL, block))
        pin_identity(self.root)
        stage = check_launch(f["input"], policy_request=f["policy"])["soc_policy"]["stage"]
        self.assertEqual(stage["selected_rows"], 10)
        self.assertEqual(stage["eligible_single_body_count"], 11)
        self.assertFalse(stage["availability_exception"])
        self.assertEqual(stage["count_evidence"], digest(log.encode()))
        mapping.update(selected=mapping["selected"][:2], type_limit=2,
                       order_rationale=mapping["order_rationale"][:2])
        (self.root / "mapping.json").write_text(json.dumps(mapping))
        pin_identity(self.root)
        with self.assertRaisesRegex(ValueError, "initial SOC stage"):
            check_launch(f["input"], policy_request=f["policy"])

    def test_unsafe_nonfinite_or_incomplete_requests(self):
        good = copy.deepcopy(self.spec)
        for key, value in [('soc', 'restricted'), ('one_body_cutoff_bohr', float('nan')),
                           ('higher_body_cutoffs_bohr', {'3': 7}),
                           ('files', {'cell.str': 'cell.str', '../escape': 'unit_cell.str'}),
                           ('files', {'cell.str': 'cell.str'})]:
            with self.subTest(key=key, value=value):
                self.spec = {**good, key: value}
                with self.assertRaises(ValueError):
                    self.run_prepare()
                self.assertFalse((self.root / 'out').exists())

    def test_physics_and_dependency_hashes_invalidate_reuse(self):
        first = self.run_prepare()
        self.spec['higher_body_cutoffs_bohr']['3'] = 8
        second = self.run_prepare('changed')
        self.assertNotEqual(first['candidates'][0]['configuration_sha256'],
                            second['candidates'][0]['configuration_sha256'])
        (self.root / 'cell.str').write_text('changed cell\n')
        third = self.run_prepare('changed-cell')
        self.assertNotEqual(second['candidates'][0]['configuration_sha256'],
                            third['candidates'][0]['configuration_sha256'])
        with self.assertRaises(ValueError):
            self.run_prepare('out')

    def test_missing_source_and_symlink_destination(self):
        (self.root / 'unit_cell.str').unlink()
        with self.assertRaises(ValueError):
            self.run_prepare()
        self.assertFalse((self.root / 'out').exists())
        (self.root / 'unit_cell.str').write_text('fixture\n')
        (self.root / 'out').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.run_prepare()
        self.assertFalse((self.root / 'search-inputs.json').exists())

    def test_actual_restricted_launch_and_execution_backed_reduction(self):
        f = restricted_fixture(self.root)
        self.assertEqual(check_launch(f['input'], policy_request=f['policy'])['status'], 'initial_15_bohr')
        request = self.root / 'launch.json'
        request.write_text(json.dumps({'input': 'PASP.input', 'policy_request': 'policy.json',
            'command': [sys.executable, '-c',
                'print("Property Analysis and Simulation Package for materials (PASP)\\nPASP start\\nsynthetic native startup")'],
            'timeout_seconds': 5}))
        record = launch(request)
        self.assertEqual(execution_evidence(self.root / 'basis-execution.json'), record)
        # A partial hash map must not turn an unhashed process/log/exit into evidence.
        partial = self.root / 'partial-execution.json'
        for name in record['sha256']:
            hashes = {k: v for k, v in record['sha256'].items() if k != name}
            partial.write_text(json.dumps({**record, 'sha256': hashes}))
            with self.subTest(missing_hash=name), self.assertRaisesRegex(ValueError, 'incomplete execution'):
                execution_evidence(partial)
        (self.root / 'local_mode_PM.dat').write_text('unrecorded native output\n')
        with self.assertRaisesRegex(ValueError, 'incomplete execution'):
            execution_evidence(self.root / 'basis-execution.json')
        (self.root / 'local_mode_PM.dat').unlink()
        low = self.root / 'low'
        low.mkdir()
        for n in ('cell.str', 'unit_cell.str'):
            (low / n).write_bytes((self.root / n).read_bytes())
        low_input = low / 'PASP.input'
        low_input.write_text(f['input'].read_text().replace('1 15', '1 8'))
        # A lower-cutoff mapping must separately be compatible with that candidate.
        (self.root / 'map/PASP.input').write_text(low_input.read_text().replace(SPECIAL, ''))
        pin_identity(self.root)
        with self.assertRaisesRegex(ValueError, '15 Bohr'):
            check_launch(low_input, policy_request=f['policy'])
        ledger = self.root / 'ledger.json'
        row = {'status': 'executed', 'cutoff_bohr': 15, 'receipt': 'basis-execution.json',
               'effective_input_sha256': record['effective_input_sha256'],
               'reduction_reason': 'observed larger-radius attempt; documented synthetic reduction'}
        ledger.write_text(json.dumps([row]))
        self.assertEqual(check_launch(low_input, ledger, policy_request=f['policy'])['status'], 'reduction_authorized')
        for update in ({'effective_input_sha256': 'forged'}, {'cutoff_bohr': 14}, {'receipt': 'missing.json'},
                       {'reduction_reason': ''}):
            ledger.write_text(json.dumps({'attempts': [{**row, **update}]}))
            with self.subTest(update=update), self.assertRaises(ValueError):
                check_launch(low_input, ledger, policy_request=f['policy'])
        (self.root / 'forged.json').write_text(json.dumps({'status': 'executed',
            'effective_input_sha256': record['effective_input_sha256']}))
        ledger.write_text(json.dumps([dict(row, receipt='forged.json')]))
        with self.assertRaisesRegex(ValueError, 'wrapper execution'):
            check_launch(low_input, ledger, policy_request=f['policy'])

    def test_non_pasp_process_cannot_authorize_reduction(self):
        restricted_fixture(self.root)
        request = self.root / 'launch.json'
        request.write_text(json.dumps({'input': 'PASP.input', 'policy_request': 'policy.json',
            'command': [sys.executable, '-c', 'print("launcher failed before PASP started")'],
            'timeout_seconds': 5}))
        with self.assertRaisesRegex(ValueError, 'attempted native PASP'):
            launch(request)
        with self.assertRaisesRegex(ValueError, 'attempted native PASP'):
            execution_evidence(self.root / 'basis-execution.json')

    def test_includes_shadowed_and_missing_soc_never_launch(self):
        f = restricted_fixture(self.root)
        original = f['input'].read_text()
        for text in (original.replace(SPECIAL, ''), original + 'Invariant_SOC F\n',
                     original + '%block fig_mdist\n1 8 6 6\n%endblock fig_mdist\n',
                     original.replace('1 1 2\n1 2 2', '1 1 1\n1 2 2')):
            f['input'].write_text(text)
            with self.subTest(text=text), self.assertRaises(ValueError):
                check_launch(f['input'], policy_request=f['policy'])
        # Included controls are resolved; effective low cutoff cannot be hidden.
        (self.root / 'physics.fdf').write_text(original)
        f['input'].write_text('%include physics.fdf\n')
        self.assertEqual(check_launch(f['input'], policy_request=f['policy'])['cutoff_bohr'], 15)
        f['input'].write_text('%include physics.fdf\n%block fig.mdist\n1 15\n%endblock fig.mdist\n')
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            check_launch(f['input'], policy_request=f['policy'])
        f['input'].write_text(original)
        for policy in ('full', 'off'):
            (self.root / 'policy.json').write_text(json.dumps({**f['spec'], 'soc': policy}))
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                check_launch(f['input'], policy_request=f['policy'])
        with self.assertRaisesRegex(ValueError, 'policy-request'):
            check_launch(f['input'])

    def test_executed_radius_comparisons_with_native_fit_evidence(self):
        from prepare_l3 import radius_comparisons, check_fit
        from study_contract import digest
        from test_method6 import NATIVE
        from test_prepare_l3 import native_log
        comparisons = []
        prior = None
        source_evidence = None
        for i, (body, radius) in enumerate(((2, 6), (3, 6), (3, 9), (4, 9))):
            run = self.root / f'run-{i}'
            run.mkdir()
            text = BASE + MODE + f'fig.maxk {body}\nInvariant.power 4\n%block fig.mdist\n' + ' '.join(map(str, [1, 15] + ([radius] if body >= 3 else []) + ([4] if body == 4 else []))) + '\n%endblock fig.mdist\n'
            f = restricted_fixture(run, text)
            # Source corpus identity is shared, regardless of candidate directory.
            f['spec']['source_outcars'] = [str(self.root / 'OUTCAR-shared')]
            (self.root / 'OUTCAR-shared').write_text('LSORBIT = T\n')
            f['policy'].write_text(json.dumps(f['spec']))
            request = {'input': 'PASP.input', 'policy_request': 'policy.json',
                'command': [sys.executable, '-c', 'from pathlib import Path; Path("local_mode_PM.dat").write_bytes(' + repr(NATIVE) + '); print(' + repr(native_log()) + ')'],
                'timeout_seconds': 5}
            if prior:
                (run / 'ledger.json').write_text(json.dumps([{'status': 'executed', 'cutoff_bohr': 15,
                    'receipt': str(prior), 'effective_input_sha256': json.loads(prior.read_text())['effective_input_sha256'],
                    'reduction_reason': 'synthetic completed comparison'}]))
                request['predecessor_ledger'] = 'ledger.json'
            (run / 'launch.json').write_text(json.dumps(request))
            launch(run / 'launch.json')
            prior = run / 'basis-execution.json'
            source_evidence = json.loads((run / 'basis-gate.json').read_text())['soc_policy']['source_evidence']
            fit = run / 'fit'
            fit.mkdir()
            (fit / 'PASP.input').write_text('Model Fitting_one_order\n')
            for name in ('Fitting_Dataset.txt', 'Fitting_Data_for_prediction.txt'):
                (fit / name).write_text('1 3 -29\n2 4 -27\n')
            (fit / 'Fitting_Set_Lambda.txt').write_text('1 1\n1 2 1.01\n')
            preflight = check_fit(fit / 'PASP.input')
            (fit / 'preflight.json').write_text(json.dumps(preflight))
            (fit / 'LM').write_text('2 1\n2 2\n')
            (fit / 'report').write_text('2\n1 0\n2 2\nB(1)=-35\nB(2)=2\n')
            (fit / 'predictions').write_text('1 -29 -29 0 0\n2 -27 -27 0 0\n')
            (fit / 'log.out').write_text('Nn,Nd: 2 2\nFITTING FINISHED\nPASP is finished gracefully\n')
            (fit / 'exit.code').write_text('0\n')
            manifest = {'basis_file': '../local_mode_PM.dat', 'lm_file': 'LM', 'fit_report': 'report',
                'fit_log': 'log.out', 'fit_exit_code_file': 'exit.code', 'prediction_atol': 1e-10,
                'coefficient_atol': 1e-12, 'datasets': [{'name': n, 'matrix': m, 'predictions': 'predictions'}
                for n, m in [('train', 'Fitting_Dataset.txt'), ('selection', 'Fitting_Data_for_prediction.txt')]]}
            (fit / 'manifest.json').write_text(json.dumps(manifest))
            pin = lambda path: {'path': str(path), 'sha256': digest(path.read_bytes())}
            assessment = {'fit_manifest': pin(fit / 'manifest.json'), 'fit_preflight': pin(fit / 'preflight.json'),
                'basis_sha256': digest(NATIVE), 'feature_count': 2, 'test_used_for_selection': False,
                'train_r2': 1, 'selection_r2': 1, 'train_residual': 0, 'selection_residual': 0,
                'conditioning': 1, 'identifiability': 'synthetic full rank',
                'directional_deficiency': 'synthetic test only', 'controls_comparison': 'synthetic fixed SOC'}
            (fit / 'assessment.json').write_text(json.dumps(assessment))
            comparisons.append({'execution': pin(prior), 'assessment': pin(fit / 'assessment.json')})
        result = radius_comparisons({'radius_body_comparisons': comparisons}, self.root, source_evidence)
        self.assertEqual(len(result), 4)
        # A later targeted order extension can use executed evidence without
        # changing body/radius controls; missing lower-stage evidence still fails.
        from prepare_l3 import staged_soc
        gate = json.loads((run / 'basis-gate.json').read_text())
        mapping = copy.deepcopy(gate['soc_policy']['mapping'])
        mapping.update(stage='extension', order_bound=4, selected=[(1, 1, 2), (1, 2, 2), (2, 1, 4)])
        (self.root / 'operator-evidence').write_text('synthetic selected pair symmetry justification\n')
        evidence = {'radius_body_comparisons': comparisons, 'reason': 'synthetic lower-order deficiency',
            'operator_interpretation': 'synthetic targeted pair order extension',
            'symmetry_evidence': 'synthetic native operator support; no physical acceptance',
            'references': [pin(self.root / 'operator-evidence')], 'predecessor': pin(prior),
            'assessment': pin(fit / 'assessment.json'), 'family': 'advanced', 'lower_stages_exhausted': True}
        (self.root / 'extension.json').write_text(json.dumps(evidence))
        mapping['stage_evidence'] = pin(self.root / 'extension.json')
        self.assertEqual(staged_soc(mapping, self.root / 'mapping.json', None, source_evidence)['stage'], 'extension')
        evidence['lower_stages_exhausted'] = False
        (self.root / 'extension.json').write_text(json.dumps(evidence))
        mapping['stage_evidence'] = pin(self.root / 'extension.json')
        with self.assertRaisesRegex(ValueError, 'lower-order deficiency'):
            staged_soc(mapping, self.root / 'mapping.json', None, source_evidence)
        for subset in (comparisons[:1], comparisons[:2], [comparisons[0], comparisons[1], comparisons[3]]):
            with self.subTest(count=len(subset)), self.assertRaises(ValueError):
                radius_comparisons({'radius_body_comparisons': subset}, self.root, source_evidence)
        assessment['selection_r2'] = 0.5
        (fit / 'assessment.json').write_text(json.dumps(assessment))
        comparisons[-1]['assessment'] = pin(fit / 'assessment.json')
        with self.assertRaisesRegex(ValueError, 'actual native predictions'):
            radius_comparisons({'radius_body_comparisons': comparisons}, self.root, source_evidence)

    def test_native_rewrite_preserves_ids_and_pristine_reconstruction(self):
        from test_fit_handoff import HandoffTest
        fixture = HandoffTest('test_clean_native_completion_passes')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.spec.update(fit_log='fit.log', fit_exit_code_file='fit.exit',
            rewrite_mappings=['Data_Variables_Mapping_(1st Reducing)_2.txt'])
        fixture.write('fit.log', 'Nn,Nd: 2 2\nNEED TO REWRITE DATA\nNn,Nd: 2 1\nFITTING FINISHED\nPASP is finished gracefully\n')
        fixture.write('fit.exit', '0\n')
        mapping = fixture.write('Data_Variables_Mapping_(1st Reducing)_2.txt', '1:2\n')
        self.assertEqual(fixture.check()['datasets']['train']['max_abs_prediction_difference'], 0)
        for text in ('1:0\n', '1:1\n', '2:2\n', ''):
            mapping.write_text(text)
            with self.subTest(mapping=text), self.assertRaises(ValueError):
                fixture.check()
        mapping.write_text('1:2\n')
        fixture.write('predictions', '1 -29 -28 0 0\n2 -27 -27 0 0\n')
        with self.assertRaisesRegex(ValueError, 'round-trip'):
            fixture.check()

    def test_twelve_total_types_with_evidence_is_allowed(self):
        from prepare_l3 import staged_soc
        from study_contract import digest
        rows = [(1, 3, 2)] + [(2, i, 2) for i in range(1, 12)]
        mapping = {'stage': 'initial', 'selected': rows, 'interaction_types': [(b, t) for b, t, _ in rows],
            'type_limit': 12, 'order_bound': 2, 'evidence_sha256': {'basis_log': 'synthetic hash'}}
        (self.root / 'operators.txt').write_text('synthetic equal-range orbit family evidence\n')
        count = {'selected': [list(r) for r in rows], 'reason': 'retain equal-range near pair orbits together',
            'symmetry_evidence': 'synthetic family coverage, not a physical proof',
            'feature_count': 12, 'training_rows': 20,
            'references': [{'path': 'operators.txt', 'sha256': digest((self.root / 'operators.txt').read_bytes())}]}
        (self.root / 'count.json').write_text(json.dumps(count))
        mapping['stage_evidence'] = {'path': 'count.json', 'sha256': digest((self.root / 'count.json').read_bytes())}
        stage = staged_soc(mapping, self.root / 'mapping.json', None, {})
        self.assertEqual(stage['selected_rows'], 12)
        count['feature_count'] = 31
        (self.root / 'count.json').write_text(json.dumps(count))
        mapping['stage_evidence']['sha256'] = digest((self.root / 'count.json').read_bytes())
        with self.assertRaisesRegex(ValueError, '31 > 30'):
            staged_soc(mapping, self.root / 'mapping.json', None, {})

    def test_automatic_radius_plan_and_manual_bypass(self):
        self.input.write_text(BASE.replace('SOC T', 'SOC F') + MODE)
        (self.root / 'OUTCAR.1').write_text('LSORBIT = F\n')
        self.spec.update(soc='off', automatic=True, source_outcars=['OUTCAR.1'],
            candidates=[dict(body_order=b, expansion_order=4, two_body_cutoff_bohr=15,
                higher_body_cutoffs_bohr={'3': r}) for b, r in ((2, 6), (3, 6), (3, 9), (4, 9))])
        self.spec.pop('manual_study')
        result = self.run_prepare()
        self.assertEqual([r['physics']['body_order'] for r in result['candidates']], [2, 3, 3, 4])
        self.assertEqual(result['candidates'][-1]['physics']['cutoffs_bohr'], [1, 15, 9, 5])
        good = copy.deepcopy(self.spec)
        for change in ({'candidates': [dict(body_order=3, expansion_order=4, two_body_cutoff_bohr=15)]},
                       {'higher_body_cutoffs_bohr': {'3': 16, '4': 4}},
                       {'candidates': [dict(body_order=2, expansion_order=4, two_body_cutoff_bohr=14)]},
                       {'automatic': False}, {'manual_study': 'manual.json'}):
            self.spec = {**good, **change}
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.run_prepare('bad')
            self.assertFalse((self.root / 'bad').exists())

    def test_physical_policy_mismatch_and_posthoc_evidence(self):
        from prepare_l3 import soc_context, comparable_soc
        from study_contract import digest
        import os
        f = restricted_fixture(self.root)
        policy = soc_context(FDF(f['input']), f['spec'], self.root)
        changed = copy.deepcopy(policy)
        changed['mapping']['basis_definition_sha256'] = 'changed basis'
        comparable_soc(policy, changed)
        changed['mapping']['policy_identity']['physical_keys'][0] = 'different orbit'
        with self.assertRaisesRegex(ValueError, 'physical SOC'):
            comparable_soc(policy, changed)
        request = self.root / 'launch.json'
        request.write_text(json.dumps({'input': 'PASP.input', 'policy_request': 'policy.json',
            'command': [sys.executable, '-c', 'print("Property Analysis and Simulation Package for materials (PASP)\\nPASP start")'],
            'timeout_seconds': 5}))
        launch(request)
        process = json.loads((self.root / 'basis-process.json').read_text())
        gate = self.root / 'basis-gate.json'
        os.utime(gate, (process['started_epoch'] + 1, process['started_epoch'] + 1))
        with self.assertRaisesRegex(ValueError, 'post-hoc'):
            execution_evidence(self.root / 'basis-execution.json')

    def test_cli_from_other_directory_and_failure(self):
        self.manifest.write_text(json.dumps(self.spec))
        script = Path(__file__).with_name('search_inputs.py')
        cmd = [sys.executable, '-B', str(script), '--manifest', str(self.manifest),
               '--root', str(self.root / 'cli')]
        result = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'prepared_not_executed')
        self.spec['candidates'][0]['expansion_order'] = 5
        self.manifest.write_text(json.dumps(self.spec))
        result = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
