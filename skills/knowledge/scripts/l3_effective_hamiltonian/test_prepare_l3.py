"""Synthetic preparation regressions; no PASP execution or scientific acceptance."""
import json
import os
from unittest.mock import patch
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import prepare_l3 as prep
import study_contract as contract


MODE = '%block local_mode.mode_definition\n2\n1\n1 spin\n1\n0 0 0 1 0 0\n%endblock local_mode.mode_definition\n'
BASE = ('Model Invariant\nnumber_of_species 2\n'
        '%block Z_values\n24 8\n%endblock Z_values\n'
        '%block Spin_values\n1 0\n%endblock Spin_values\nInvariant.SOC T\n')


class PrepareTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.input = self.write('PASP.input', BASE + MODE)
        self.write('manual.json', {'mode': 'manual_study', 'soc': 'full', 'authorization': 'explicit synthetic manual request', 'reason': 'format compatibility study'})
        self.spec = {'soc': 'full', 'automatic': False, 'manual_study': 'manual.json', 'representatives': [{'species': 1, 'position_angstrom': [0, 0, 0]}]}
        self.request = self.write('request.json', self.spec)
        manual_authority(self, self.root, 'full')

    def write(self, name, value):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value if isinstance(value, str) else json.dumps(value))
        return p

    def run_spin(self):
        self.write('request.json', self.spec)
        return prep.prepare_spin(self.input, self.request, self.root / 'out')

    def test_generate_roundtrip_preserves_source_and_unrelated_records(self):
        unrelated = ('# retain comment\nInvariant.power 6\nInvariant.power 2 # shadow\n'
                     '%block SuperCell\n1 0 0\n0 1 0\n0 0 1\n%endblock SuperCell\n')
        self.input.write_text(BASE + MODE + unrelated)
        before = self.input.read_bytes()
        result = self.run_spin()
        self.assertEqual(result['mode_count'], 3)
        self.assertEqual(self.input.read_bytes(), before)
        out = self.root / 'out/PASP.input'
        self.assertIn(unrelated, out.read_text())
        self.assertEqual(prep.check(prep.FDF(out), 'full')['mode_count'], 3)
        self.assertEqual(prep.FDF(out).values('Invariant.power', False), ['6'])

    def test_include_first_match_aliases_and_explicit_soc_replacement(self):
        self.write('sub/parts.fdf', BASE.replace('Invariant.SOC T', 'INVARIANT-SOC F') + MODE +
                   '%include extra.fdf\n%block local-mode.special_SOC\n1\n1 1 2\n%endblock local-mode.special_SOC\n')
        # Nested include names resolve against the runtime CWD, not the including file.
        self.write('extra.fdf', '# extra retained\n')
        self.input.write_text('%include sub/parts.fdf\nInvariant_SOC T\n' + MODE)
        self.assertEqual(prep.FDF(self.input).values('Invariant.SOC', False), ['F'])
        self.run_spin()
        out = self.root / 'out/PASP.input'
        text = out.read_text()
        self.assertEqual(text.count('%block local_mode.mode_definition'), 1)
        self.assertEqual(text.count('Invariant.SOC'), 1)
        self.assertNotIn('special_SOC', text)
        self.assertIn('# extra retained', text)
        self.assertNotIn('%include', text)

    def test_fortran_numbers_and_cli_failure(self):
        self.input.write_text(BASE + MODE.replace('0 0 0 1 0 0', '0D0 0 0 1d0 0 0'))
        self.assertEqual(prep.check(prep.FDF(self.input), 'full')['mode_count'], 1)
        self.spec['soc'] = 'restricted'
        self.write('request.json', self.spec)
        proc = subprocess.run([sys.executable, '-B', str(Path(prep.__file__).resolve()), 'spin',
                               '--input', str(self.input), '--request', str(self.request),
                               '--root', str(self.root / 'out')], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('mapping', proc.stderr)
        self.assertFalse((self.root / 'out').exists())

    def test_off_policy(self):
        self.spec['soc'] = 'off'
        self.write('manual.json', {'mode': 'manual_study', 'soc': 'off', 'authorization': 'explicit synthetic manual request', 'reason': 'off study'})
        manual_authority(self, self.root, 'off')
        self.run_spin()
        self.assertFalse(prep.logical(prep.FDF(self.root / 'out/PASP.input').values('Invariant.SOC', False)))

    def test_automatic_source_policy_and_mapping(self):
        fixture = restricted_fixture(self.root)
        self.input = fixture['input']
        self.spec = {**fixture['spec'], 'representatives': [{'species': 1, 'position_angstrom': [0, 0, 0]}]}
        # Mapping modes must match the generated xyz representatives.
        self.input.write_text(BASE + xyz_modes() + PHYSICS)
        (self.root / 'map/PASP.input').write_text(self.input.read_text())
        pin_identity(self.root)
        result = self.run_spin()
        self.assertEqual(result['selected_special_SOC'], [(1, 1, 2), (1, 2, 2), (2, 1, 2)])
        self.assertEqual(result['soc_policy']['source_evidence']['observed'], 'full')
        self.assertIn('3\n1 1 2\n1 2 2\n2 1 2', (self.root / 'out/PASP.input').read_text())

    def test_automatic_full_off_and_unrecorded_manual_rejected(self):
        f = restricted_fixture(self.root)
        for policy in ('full', 'off'):
            spec = {**f['spec'], 'soc': policy}
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                prep.soc_context(prep.FDF(f['input']), spec, self.root)
        with self.assertRaisesRegex(ValueError, 'recorded manual'):
            prep.soc_context(prep.FDF(f['input']), {**f['spec'], 'automatic': False}, self.root)
        for text in ('LNONCOLLINEAR = T\n', 'LSORBIT = T\nLSORBIT = F\n', 'LSORBIT = F\n'):
            (self.root / 'OUTCAR.1').write_text(text)
            with self.subTest(text=text), self.assertRaises(ValueError):
                prep.soc_context(prep.FDF(f['input']), f['spec'], self.root)

    def test_source_off_stays_off_and_mixed_corpus_fails(self):
        f = restricted_fixture(self.root)
        (self.root / 'OUTCAR.2').write_text('LSORBIT = F\nLNONCOLLINEAR = T\n')
        with self.assertRaisesRegex(ValueError, 'mixed LSORBIT'):
            prep.soc_context(prep.FDF(f['input']),
                {**f['spec'], 'source_outcars': ['OUTCAR.1', 'OUTCAR.2']}, self.root)
        (self.root / 'OUTCAR.1').write_text('LSORBIT = F\nLNONCOLLINEAR = T\n')
        f['input'].write_text(f['input'].read_text().replace(SPECIAL, '').replace('SOC T', 'SOC F'))
        result = prep.soc_context(prep.FDF(f['input']), {**f['spec'], 'soc': 'off'}, self.root)
        self.assertEqual(result['soc'], 'off')
        self.assertEqual(result['special_SOC'], [])
        self.assertEqual(result['source_evidence']['observed'], 'off')
        with self.assertRaisesRegex(ValueError, 'source LSORBIT'):
            prep.soc_context(prep.FDF(f['input']), {**f['spec'], 'soc': 'full'}, self.root)

    def test_native_fixed_width_three_digit_type_and_partial_final_table(self):
        def row(index, body, kind):
            return prep.CLUSTER_MARKER + f'{index:5d}{body:3d}{kind:3d}{1:5d}{3:5d}{3:5d}{0:5d}\n'
        log = row(1, 0, 0) + row(2, 4, 100) + 'Total number of different clusters: 2\n'
        self.assertEqual(prep.native_types(log), [(4, 100)])
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            prep.native_types(log + row(1, 0, 0))

    def test_initial_policy_targets_ten_rows_when_available(self):
        mapping = {'stage': 'initial', 'type_limit': 10, 'order_bound': 2,
                   'selected': [(1, i, 2) for i in range(1, 11)],
                   'interaction_types': [(1, i) for i in range(1, 11)],
                   'evidence_sha256': {'basis_log': 'synthetic hash'}}
        self.assertEqual(prep.staged_soc(mapping, self.root / 'mapping.json', None, {})['selected_rows'], 10)
        mapping['type_limit'] = 9
        mapping['selected'] = mapping['selected'][:-1]
        with self.assertRaisesRegex(ValueError, 'count deviation'):
            prep.staged_soc(mapping, self.root / 'mapping.json', None, {})

    def test_mapping_wrong_basis_ids_orders_and_partial_log_rejected(self):
        f = restricted_fixture(self.root)
        good = json.loads((self.root / 'mapping.json').read_text())
        for update in ({'selected': [[2, 99, 1]]}, {'order_bound': 5},
                       {'selected': [[1, 1, 3]], 'order_bound': 2}, {'order_rationale': []}):
            self.write('mapping.json', {**good, **update})
            with self.subTest(update=update), self.assertRaises(ValueError):
                prep.soc_context(prep.FDF(f['input']), f['spec'], self.root)
        self.write('mapping.json', good)
        old = self.root / 'map/PASP.input'
        old.write_text(old.read_text().replace('15', '14'))
        with self.assertRaisesRegex(ValueError, 'basis definitions'):
            prep.soc_context(prep.FDF(f['input']), f['spec'], self.root)
        old.write_text(f['input'].read_text().replace(SPECIAL, '').replace('SOC T', 'SOC F'))
        with self.assertRaisesRegex(ValueError, 'SOC=F'):
            prep.soc_context(prep.FDF(f['input']), f['spec'], self.root)
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            prep.native_types(native_log().replace('clusters: 4', 'clusters: 5'))
        with self.assertRaisesRegex(ValueError, 'missing'):
            prep.native_types('PASP is finished gracefully')

    def test_evidence_backed_symmetry_exception_and_hash_mismatch(self):
        f = restricted_fixture(self.root)
        operator_ref = self.write('operators.txt', 'synthetic symmetry/operator evidence\n')
        evidence = {
            'reason': 'Second-order single-ion term is forbidden by the declared site symmetry.',
            'operator_interpretation': 'Only the lowest symmetry-allowed single-ion anisotropy term is selected.',
            'symmetry_evidence': 'The referenced invariant analysis excludes quadratic anisotropy.',
            'references': [{'path': 'operators.txt', 'sha256': contract.digest(operator_ref.read_bytes())}],
            'second_order_forbidden_or_absent': True,
            'lowest_allowed_tuples': [[1, 1, 4], [1, 2, 4]],
        }
        stage_path = self.write('stage.json', evidence)
        mapping = json.loads((self.root / 'mapping.json').read_text())
        mapping.update(stage='symmetry_exception', selected=[[1, 1, 4], [1, 2, 4]], order_bound=4,
                       order_rationale=['synthetic symmetry exception'] * 2,
                       stage_evidence={'path': 'stage.json',
                                       'sha256': contract.digest(stage_path.read_bytes())})
        self.write('mapping.json', mapping)
        f['input'].write_text(f['input'].read_text().replace(SPECIAL, SPECIAL.replace('1 1 2', '1 1 4').replace('1 2 2', '1 2 4')))
        pin_identity(self.root)
        with self.assertRaisesRegex(ValueError, 'executed bounded radius/body'):
            prep.soc_context(prep.FDF(f['input']), f['spec'], self.root)
        operator_ref.write_text('changed after evidence was pinned\n')
        with self.assertRaisesRegex(ValueError, 'stage evidence hash mismatch'):
            prep.soc_context(prep.FDF(f['input']), f['spec'], self.root)

    def test_bad_mode_layouts(self):
        variants = [MODE.replace('\n2\n', '\n'), MODE.replace('\n1\n1 spin', '\n1\n\n1 spin'),
                    MODE.replace('0 0 0 1 0 0', '0 0 0 nan 0 0'),
                    MODE.replace('1 spin', '2 spin'), MODE.replace('0 0 0 1 0 0', '0 0 0 0 0 0'),
                    MODE.replace('\n1\n1 spin', '\n2\n1 spin'), MODE.replace('1 spin\n1', '1 spin\n2')]
        for bad in variants:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.input.write_text(BASE + bad)
                prep.check(prep.FDF(self.input), 'full')

    def test_separator_missing_or_extra(self):
        self.run_spin()
        good = (self.root / 'out/PASP.input').read_text()
        for bad in (good.replace('\n\n1 spin', '\n1 spin', 1),
                    good.replace('\n\n1 spin', '\n\n\n1 spin', 1)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.input.write_text(bad)
                prep.check(prep.FDF(self.input), 'full')

    def test_bad_requests_no_output(self):
        for edit in ({'soc': 'restricted'}, {'representatives': []},
                     {'representatives': [{'species': 2, 'position_angstrom': [0, 0, 0]}]},
                     {'representatives': [{'species': True, 'position_angstrom': [0, 0, 0]}]},
                     {'representatives': [{'species': 1, 'position_angstrom': [0, 0]}]},
                     {'representatives': self.spec['representatives'] * 2}, {'typo': 1}):
            with self.subTest(edit=edit), self.assertRaises(ValueError):
                request = self.write('bad.json', {**self.spec, **edit})
                prep.prepare_spin(self.input, request, self.root / 'out')
            self.assertFalse((self.root / 'out').exists())

    def test_species_and_soc_conflicts(self):
        for text in (BASE.replace('24 8', '24'), BASE.replace('1 0', '1 nan'),
                     BASE.replace('number_of_species 2', 'number_of_species 1.5'),
                     BASE.replace('Invariant.SOC T', 'Invariant.SOC F'),
                     BASE + '%block local_mode.special_SOC\n1\n1 1 2\n%endblock local_mode.special_SOC\n'):
            self.input.write_text(text + MODE)
            with self.subTest(text=text), self.assertRaises(ValueError):
                prep.check(prep.FDF(self.input), 'full')

    def test_unsupported_or_broken_fdf(self):
        for text in ('%include PASP.input\n', '%include absent\n', 'Spin_values < vals\n',
                     '%block Spin_values < vals\n', '%include "file name"\n',
                     '%block x\n1\n%endblock y\n', '%block x\n1\n', '%dump foo\n'):
            self.input.write_text(text)
            with self.subTest(text=text), self.assertRaises((ValueError, OSError)):
                prep.FDF(self.input)

    def test_cli_other_cwd_and_conflicting_output(self):
        script = Path(prep.__file__).resolve()
        proc = subprocess.run([sys.executable, '-B', str(script), 'spin', '--input', str(self.input),
                               '--request', str(self.request), '--root', str(self.root / 'cli')],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.run_spin()
        self.spec['soc'] = 'off'
        with self.assertRaises(ValueError):
            self.run_spin()


class FitDataTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Create a real contract receipt using synthetic indexed encoder records.
        self.write('Energy.dat', '4 -3\n9 -2\n20 -5\n13 -4\n')
        self.split = self.write('split.json', {'method': 'explicit', 'seed': None,
                               'splits': {'train': [4, 13], 'selection': [20], 'test': [9]}})
        self.write('basis', 'synthetic basis\n')
        spec = {'energy_file': 'Energy.dat', 'energy_header': 'none', 'split_file': 'split.json',
                'energy_divisor': 1, 'basis_file': 'basis', 'samples': []}
        for sid in (4, 9, 20, 13):
            self.write(f'{sid}.feat', f'2 #npara\n1 {sid}\n2 1\n')
            self.write(f'{sid}.log', 'synthetic: PASP is finished gracefully\n')
            self.write(f'{sid}.exit', '0\n')
            spec['samples'].append({'id': sid, 'features': f'{sid}.feat', 'basis_file': 'basis',
                                    'log': f'{sid}.log', 'exit_code_file': f'{sid}.exit'})
        manifest = self.write('convert.json', spec)
        contract.convert(manifest, self.root / 'conversion')
        self.receipt = self.root / 'conversion/conversion.json'
        self.pin = contract.digest(self.receipt.read_bytes())
        self.lambdas = self.write('lambdas.json', [1.2, 1.01, 1.05])

    def write(self, name, value):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value if isinstance(value, str) else json.dumps(value))
        return p

    def stage(self):
        return prep.fit_data(self.receipt, self.split, self.pin, self.lambdas, self.root / 'fit')

    def test_full_staging_no_test_open_or_copy_and_width(self):
        # Test contents need not be opened for staging; the full conversion already checked coverage.
        self.assertFalse((self.root / 'conversion/test.txt').exists())
        r = self.stage()
        self.assertEqual(r['counts'], {'train': 2, 'selection': 1, 'test': 1})
        out = self.root / 'fit'
        self.assertEqual((out / 'Fitting_Dataset.txt').read_bytes(), (self.root / 'conversion/train.txt').read_bytes())
        self.assertEqual(json.loads((out / 'Fitting_Data_for_prediction.txt.ids.json').read_text()), [20])
        self.assertEqual((out / 'Fitting_Set_Lambda.txt').read_text().splitlines()[1].split()[:2], ['1', '2'])
        self.assertFalse(any('test' in p.name for p in out.iterdir()))

    def test_candidate_width_gate_runs_before_staging(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['feature_count'] = 1857
        self.receipt.write_text(json.dumps(receipt))
        self.pin = contract.digest(self.receipt.read_bytes())
        with self.assertRaisesRegex(ValueError, '1857 > 3'):
            self.stage()
        self.assertFalse((self.root / 'fit').exists())

    def wide_conversion(self):
        train_ids = list(range(1, 701))
        split = {'method': 'explicit', 'seed': None,
                 'splits': {'train': train_ids, 'selection': [701], 'test': [702]}}
        self.write('split.json', split)
        receipt = json.loads(self.receipt.read_text())
        receipt.update(feature_count=740, samples=[str(i) for i in range(1, 703)],
                       splits=split['splits'], split_sha256=contract.digest(self.split.read_bytes()))
        row = ' '.join(['1'] * 740 + ['-3']) + '\n'
        for name, ids in [('train', train_ids), ('selection', [701])]:
            self.write(f'conversion/{name}.txt', row * len(ids))
            self.write(f'conversion/{name}.ids.json', ids)
            for suffix in ('.txt', '.ids.json'):
                filename = name + suffix
                receipt['sha256'][filename] = contract.digest((self.root / 'conversion' / filename).read_bytes())
        self.receipt.write_text(json.dumps(receipt))
        self.pin = contract.digest(self.receipt.read_bytes())

    def test_740_feature_basis_uses_150_cap_on_every_round(self):
        self.wide_conversion()
        result = self.stage()
        rows = (self.root / 'fit/Fitting_Set_Lambda.txt').read_text().splitlines()[1:]
        self.assertEqual(result['candidate_feature_count'], 740)
        self.assertEqual(result['candidate_feature_limit'], 1050)
        self.assertEqual(result['retained_parameter_limit'], 150)
        self.assertTrue(all(int(row.split()[1]) == 150 for row in rows))
        self.write('fit/PASP.input', 'Model Fitting_one_order\n')
        checked = prep.check_fit(self.root / 'fit/PASP.input')
        self.assertEqual(checked['round_parameter_caps'], [150, 150, 150])

    def test_actual_fit_preflight_rejects_oversized_cap_after_edit(self):
        self.wide_conversion()
        self.stage()
        self.write('fit/PASP.input', 'Model Fitting_one_order\n')
        self.write('fit/Fitting_Set_Lambda.txt', '1 1\n1 740 1.01\n')
        with self.assertRaisesRegex(ValueError, '740 > 150'):
            prep.check_fit(self.root / 'fit/PASP.input')

    def test_actual_fit_preflight_rejects_bad_lambda_in_any_round(self):
        self.stage()
        self.write('fit/PASP.input', 'Model Fitting_one_order\n')
        for factor in ('0.98', '1.0', 'nan', 'inf'):
            self.write('fit/Fitting_Set_Lambda.txt', f'2 1\n1 2 1.02\n2 2 {factor}\n')
            with self.subTest(factor=factor), self.assertRaises(ValueError):
                prep.check_fit(self.root / 'fit/PASP.input')

    def test_actual_fit_preflight_checks_model_matrices_and_schedule_shape(self):
        self.stage()
        self.write('fit/PASP.input', 'Model Fitting_one_order\n')
        checked = prep.check_fit(self.root / 'fit/PASP.input')
        self.assertEqual(checked['round_parameter_caps'], [2, 2, 2])
        for name, bad in [('PASP.input', 'Model Invariant\n'),
                          ('Fitting_Dataset.txt', ''),
                          ('Fitting_Data_for_prediction.txt', '1 -3\n'),
                          ('Fitting_Set_Lambda.txt', '2 1\n1 2 1.01\n'),
                          ('Fitting_Set_Lambda.txt', '1 2\n1 2 1.01\n'),
                          ('Fitting_Set_Lambda.txt', '1 1\n2 2 1.01\n')]:
            path = self.root / 'fit' / name
            original = path.read_bytes()
            path.write_text(bad)
            with self.subTest(name=name, bad=bad), self.assertRaises(ValueError):
                prep.check_fit(self.root / 'fit/PASP.input')
            path.write_bytes(original)

    def test_check_fit_cli(self):
        self.stage()
        self.write('fit/PASP.input', 'Model Fitting_one_order\n')
        proc = subprocess.run([sys.executable, '-B', str(Path(prep.__file__).resolve()),
                               'check-fit', '--input', str(self.root / 'fit/PASP.input')],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['round_parameter_caps'], [2, 2, 2])

    def test_hash_pins_and_source_mutation(self):
        for name in ('conversion/conversion.json', 'split.json', 'conversion/train.txt', 'conversion/selection.ids.json'):
            p = self.root / name
            original = p.read_bytes()
            p.write_bytes(original + b'\n')
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.stage()
            self.assertFalse((self.root / 'fit').exists())
            p.write_bytes(original)

    def test_finite_width_and_count_even_with_matching_digest(self):
        p = self.root / 'conversion/train.txt'
        for bad in ('1 nan -3\n13 1 -4\n', '1 -3\n13 -4\n', '1 1 -3\n'):
            p.write_text(bad)
            receipt = json.loads(self.receipt.read_text())
            receipt['sha256']['train.txt'] = contract.digest(p.read_bytes())
            self.receipt.write_text(json.dumps(receipt))
            self.pin = contract.digest(self.receipt.read_bytes())
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.stage()

    def test_row_map_mismatch_with_matching_digest(self):
        p = self.root / 'conversion/train.ids.json'
        p.write_text('[13, 4]')
        receipt = json.loads(self.receipt.read_text())
        receipt['sha256']['train.ids.json'] = contract.digest(p.read_bytes())
        self.receipt.write_text(json.dumps(receipt))
        self.pin = contract.digest(self.receipt.read_bytes())
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse((self.root / 'fit').exists())

    def test_invalid_lambda_and_existing_directory(self):
        for values in ([], [0], [-1], [0.98], [1], [1.01, 1], [True], ['nan'], ['inf'], {'lambda': 1}):
            self.write('lambdas.json', values)
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.stage()
        self.write('lambdas.json', [1.01])
        (self.root / 'fit').mkdir()
        with self.assertRaises(ValueError):
            self.stage()

    def test_cli_fit(self):
        proc = subprocess.run([sys.executable, '-B', str(Path(prep.__file__).resolve()), 'fit-data',
                               '--conversion', str(self.receipt), '--split', str(self.split),
                               '--receipt-sha256', self.pin, '--lambdas', str(self.lambdas),
                               '--root', str(self.root / 'fit')], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)




PHYSICS = 'fig.maxk 2\nInvariant.power 4\n%block fig.mdist\n1 15\n%endblock fig.mdist\n'
SPECIAL = '%block local_mode.special_SOC\n3\n1 1 2\n1 2 2\n2 1 2\n%endblock local_mode.special_SOC\n'


def xyz_modes():
    rows = ['1 spin\n1\n0 0 0 ' + ' '.join(str(int(i == j)) for i in range(3)) for j in range(3)]
    return '%block local_mode.mode_definition\n2\n3\n' + '\n\n'.join(rows) + '\n%endblock local_mode.mode_definition\n'


def native_log():
    rows = [(1, 0, 1, 0, 3, 0, 0), (2, 1, 1, 2, 3, 1, 0),
            (3, 1, 2, 2, 3, 1, 0), (4, 2, 1, 2, 3, 2, 0)]
    return 'Property Analysis and Simulation Package for materials (PASP)\nPASP start\nTotal number of different clusters: 4\n' + ''.join(
        prep.CLUSTER_MARKER + f'{a:5d}{b:3d}{c:3d}{d:5d}{e:5d}{f:5d}{g:5d}\n'
        for a, b, c, d, e, f, g in rows) + 'Total number of local modes (excluding strain): 3\nPASP is finished gracefully.\n'


def restricted_fixture(root, input_text=None):
    root = Path(root)
    old = root / 'map'
    old.mkdir(exist_ok=True)
    text = input_text or BASE + MODE + PHYSICS
    (old / 'PASP.input').write_text(text.replace(SPECIAL, ''))
    (old / 'log.out').write_text(native_log())
    (old / 'exit.code').write_text('0\n')
    for n in ('cell.str', 'unit_cell.str'):
        (root / n).write_text('synthetic cell; no native scientific validity\n')
        (old / n).write_bytes((root / n).read_bytes())
    (root / 'OUTCAR.1').write_text('LSORBIT = T\n')
    mapping = {'basis_input': 'map/PASP.input', 'basis_log': 'map/log.out',
               'basis_exit_code_file': 'map/exit.code', 'files': {n: n for n in ('cell.str', 'unit_cell.str')},
               'selected': [[1, 1, 2], [1, 2, 2], [2, 1, 2]], 'type_limit': 3, 'order_bound': 2,
               'order_rationale': ['synthetic low-order test for first native type', 'synthetic bounded second native type', 'synthetic near-range pair']}
    (root / 'mapping.json').write_text(json.dumps(mapping))
    path = root / 'PASP.input'
    path.write_text(text + SPECIAL)
    spec = {'soc': 'restricted', 'soc_mapping': 'mapping.json',
            'source_outcars': ['OUTCAR.1'], 'files': mapping['files']}
    (root / 'policy.json').write_text(json.dumps(spec))
    pin_identity(root)
    return {'input': path, 'spec': spec, 'policy': root / 'policy.json'}


def manual_authority(test, root, soc):
    authority = Path(test.tmp.name).parent / (Path(test.tmp.name).name + '-' + soc + '-authority.json')
    authority.write_text(json.dumps({'mode': 'explicit_user_manual', 'soc': soc,
        'study_root': str(root), 'authorization': 'explicit synthetic manual request'}))
    authority.chmod(0o444)
    test.addCleanup(lambda: authority.unlink(missing_ok=True))
    env = patch.dict(os.environ, {'PASP_MANUAL_AUTHORITY': str(authority)})
    env.start()
    test.addCleanup(env.stop)


def pin_identity(root):
    mapping_path = root / 'mapping.json'
    mapping = json.loads(mapping_path.read_text())
    doc = prep.FDF(root / 'map/PASP.input')
    definition = prep.basis_definition(doc, prep.package_hashes(doc, mapping, root))
    identity = {'selected': mapping['selected'], 'basis_definition_sha256': definition,
        'basis_log_sha256': contract.digest((root / 'map/log.out').read_bytes()),
        'physical_keys': [f'synthetic orbit {b}:{t}' for b, t, _ in mapping['selected']],
        'references': [{'path': 'map/log.out', 'sha256': contract.digest((root / 'map/log.out').read_bytes())}]}
    path = root / 'identity.json'
    path.write_text(json.dumps(identity))
    mapping['policy_identity'] = {'path': 'identity.json', 'sha256': contract.digest(path.read_bytes())}
    mapping_path.write_text(json.dumps(mapping))


if __name__ == '__main__':
    unittest.main()
