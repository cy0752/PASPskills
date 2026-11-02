"""Synthetic process/contract tests, never a PASP scientific validation."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import method6 as m6
import prepare_path_b_inputs as pb
import study_contract as sc
from test_prepare_path_b_inputs import outcar

INPUT = '''Model Invariant
number_of_species 1
%block Z_values
26
%endblock Z_values
%block Spin_values
2
%endblock Spin_values
Invariant.SOC F
%block local_mode.mode_definition
2
1
1 spin
1
0 0 0 1 0 0
%endblock local_mode.mode_definition
Invariant.power 4
%include controls.fdf
local_mode.cal_para_method 99
local_mode.read_interaction T
'''
NATIVE = b'''synthetic native format
1 1 2 1 1 1 F #ipara,ipara_gb,power,n,nmode,im_read,lonebody
2 2 2 1 1 1 F #ipara,ipara_gb,power,n,nmode,im_read,lonebody
'''
GOOD_LOG = 'Total number of local modes (excluding strain): 3\nPASP is finished gracefully.\n'
FAKE = '''from pathlib import Path
import sys,time
mode=sys.argv[1]
if mode=='timeout': time.sleep(10)
if mode=='basis': Path('local_mode_PM.dat').write_bytes(Path('local_mode_PM.dat').read_bytes()+b'changed polynomial\\n')
if mode=='input': Path('distortion.MAGMOM').write_text('0 0 1\\n')
if mode=='fdf': Path('PASP.input').write_text('Model Invariant\\n')
if mode=='dependency': Path('auxiliary.dat').write_text('changed\\n')
feature='2 #npara\\n1 1.0D+00\\n2 2.0\\n'
if mode=='zero': feature='0 #npara\\n'
if mode=='width': feature='1 #npara\\n1 1.0\\n'
if mode=='nan': feature='2 #npara\\n1 NaN\\n2 2.0\\n'
if mode=='indices': feature='2 #npara\\n2 1.0\\n1 2.0\\n'
Path('distortion.ene_symbol').write_text(feature)
if mode!='no_marker': print('PASP is finished gracefully.')
print('Total number of local modes (excluding strain):',0 if mode=='modes' else 3)
if mode=='error': print('forrtl: severe (174): SIGSEGV')
if mode=='warning': print('WARNING: synthetic unresolved diagnostic')
if mode=='exit': sys.exit(7)
'''


class Method6Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run = self.root / 'successful-run'
        self.run.mkdir()
        (self.run / 'PASP.input').write_text(INPUT)
        (self.run / 'controls.fdf').write_text('local_mode.cal_para_method 1\nlocal_mode.read_interaction F\n')
        (self.run / m6.PM).write_bytes(NATIVE)
        (self.run / 'log.out').write_text(GOOD_LOG)
        (self.run / 'exit.code').write_text('0\n')
        (self.root / 'manual.json').write_text(json.dumps({'mode': 'manual_study', 'soc': 'off',
            'authorization': 'explicit synthetic manual request', 'reason': 'encoding format compatibility'}))
        from test_prepare_l3 import manual_authority
        manual_authority(self, self.root, 'off')
        self.prep = self.root / 'prepare.json'
        self.prep.write_text(json.dumps({'basis_input': 'successful-run/PASP.input',
            'basis_file': 'successful-run/local_mode_PM.dat', 'basis_log': 'successful-run/log.out',
            'basis_exit_code_file': 'successful-run/exit.code', 'soc': 'off', 'policy': 'reuse', 'automatic': False, 'manual_study': 'manual.json'}))
        self.template = self.root / 'template'
        self.raw = self.root / 'raw'
        self.raw.mkdir()
        for sid in (4, 8, 19):
            (self.raw / f'OUTCAR.{sid}').write_text(outcar())
        self.inventory = self.root / 'path-b'
        with contextlib.redirect_stdout(io.StringIO()):
            pb.main([str(self.raw), '--output-dir', str(self.inventory)])
        self.fake = self.root / 'fake.py'
        self.fake.write_text(FAKE)

    def prepare(self, policy='reuse'):
        data = json.loads(self.prep.read_text())
        data['policy'] = policy
        self.prep.write_text(json.dumps(data))
        return m6.prepare(self.prep, self.template)

    def request(self, mode='good', **updates):
        data = {'template': 'template', 'inventory': 'path-b/manifest.json', 'ids': [19, 4, 8],
                'root': 'batch-' + mode, 'command': [sys.executable, str(self.fake), mode],
                'timeout_seconds': 5, 'jobs': 2}
        data.update(updates)
        path = self.root / ('batch-request-' + mode + '.json')
        path.write_text(json.dumps(data))
        return path

    def test_preserved_basis_and_effective_include_controls(self):
        before = (self.run / 'PASP.input').read_bytes()
        receipt = self.prepare()
        text = (self.template / 'PASP.input').read_text()
        self.assertNotIn('%include', text)
        self.assertEqual(text.count('local_mode.cal_para_method'), 1)
        self.assertIn('local_mode.cal_para_method 6', text)
        self.assertIn('Invariant.power 4', text)
        self.assertIn('local_mode.nstr_random 1', text)
        self.assertEqual((self.template / m6.PM).read_bytes(), NATIVE)
        self.assertEqual(receipt['feature_count'], 2)
        self.assertEqual((self.run / 'PASP.input').read_bytes(), before)

    def test_wrong_draft_mode_native_basis_and_run_outcomes_fail(self):
        original = (self.run / 'PASP.input').read_text()
        (self.run / 'PASP.input').write_text(original.replace('2\n1\n1 spin', '1\n1 spin'))
        with self.assertRaisesRegex(ValueError, 'method line'):
            self.prepare()
        (self.run / 'PASP.input').write_text(original)
        (self.run / m6.PM).write_bytes(original.encode())
        with self.assertRaisesRegex(ValueError, 'native basis'):
            self.prepare()
        (self.run / m6.PM).write_bytes(NATIVE)
        for log in [GOOD_LOG.replace(': 3', ': 0'), GOOD_LOG + 'forrtl: severe (174)\n', 'license invalid\n']:
            (self.run / 'log.out').write_text(log)
            with self.assertRaises(ValueError):
                self.prepare()
        self.assertFalse(self.template.exists())

    def test_rebuild_explicit_and_not_automatic(self):
        self.prepare('rebuild')
        self.assertIn('local_mode.read_interaction F', (self.template / 'PASP.input').read_text())
        bad = m6.batch(self.request('basis'))
        self.assertFalse(bad['complete'])
        self.assertIn('native basis changed', bad['results'][0]['reason'])
        self.assertEqual([r['status'] for r in bad['results']], ['failed', 'not_run', 'not_run'])

    def test_complete_batch_provenance_and_conversion(self):
        self.prepare()
        result = m6.batch(self.request())
        self.assertTrue(result['complete'])
        root = self.root / 'batch-good'
        for sid in [19, 4, 8]:
            enc = sc.load(root / str(sid) / 'encoding_identity.json')
            pre = sc.load(root / str(sid) / 'pre-run.json')
            for role in ('structure', 'magnetic_state', 'basis'):
                self.assertEqual(enc['sha256'][role], pre['sha256'][role])
        (root / 'Energy.dat').write_text('4 -12.5\n8 -12.5\n19 -12.5\n')
        (root / 'split.json').write_text(json.dumps({'splits': {'train': [4], 'selection': [8], 'test': [19]}}))
        spec = {'samples': result['samples'], 'energy_file': 'Energy.dat', 'energy_header': 'none',
                'split_file': 'split.json', 'basis_file': '19/local_mode_PM.dat', 'energy_divisor': 1,
                'require_source_identity': True, 'source_energy_atol': 1e-8}
        (root / 'conversion-request.json').write_text(json.dumps(spec))
        receipt = sc.convert(root / 'conversion-request.json', root / 'converted')
        self.assertTrue(receipt['source_identity_checked'])
        self.assertEqual(receipt['feature_count'], 2)

    def test_failed_probe_stops_every_other_id_and_keeps_failure(self):
        self.prepare()
        for mode in ['exit', 'error', 'no_marker', 'modes', 'zero', 'width', 'nan', 'indices', 'input', 'fdf', 'warning']:
            with self.subTest(mode=mode):
                result = m6.batch(self.request(mode))
                self.assertFalse(result['complete'])
                self.assertEqual([r['status'] for r in result['results']], ['failed', 'not_run', 'not_run'])
                run = self.root / ('batch-' + mode) / '19'
                self.assertTrue((run / 'log.out').exists())
                self.assertTrue((run / 'exit.code').exists())
                self.assertFalse((run / 'encoding_identity.json').exists())

    def test_timeout_and_missing_launcher_preserve_failed_result(self):
        self.prepare()
        result = m6.batch(self.request('timeout', timeout_seconds=0.1))
        self.assertFalse(result['complete'])
        self.assertEqual((self.root / 'batch-timeout/19/exit.code').read_text().strip(), '124')
        result = m6.batch(self.request('missing', command=[str(self.root / 'absent-launcher')]))
        self.assertFalse(result['complete'])
        self.assertIn('No such file', result['results'][0]['reason'])

    def test_full_coverage_duplicates_and_request_types(self):
        self.prepare()
        for updates in [{'ids': [19]}, {'ids': [19, 19, 4, 8]}, {'jobs': True}, {'jobs': 0},
                        {'command': 'bash launcher'}, {'timeout_seconds': 0}]:
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                m6.batch(self.request(**updates))
        self.assertFalse((self.root / 'batch-good').exists())

    def test_controller_stage_and_collect_never_launch(self):
        self.prepare()
        request = self.request()
        data = json.loads(request.read_text())
        for key in ('command', 'jobs', 'timeout_seconds'):
            del data[key]
        request.write_text(json.dumps(data))
        root, samples, receipt, spec = m6.stage(request)
        self.assertEqual(len(samples), 3)
        self.assertTrue(all(not (run / 'log.out').exists() for _, run, _ in samples))
        incomplete = m6.collect(root)
        self.assertFalse(incomplete['complete'])
        self.assertEqual(incomplete['runtime_owner'], 'controller')
        # Synthetic returned outputs test collection; these are not PASP evidence.
        for sid, run, _ in samples:
            (run / 'log.out').write_text(GOOD_LOG)
            (run / 'exit.code').write_text('0\n')
            (run / 'distortion.ene_symbol').write_text('2 #npara\n1 1.0\n2 2.0\n')
        collected = m6.collect(root)
        self.assertTrue(collected['complete'])
        self.assertEqual(len(collected['samples']), 3)

    def test_changed_source_and_template_fail_before_staging(self):
        self.prepare()
        path = self.inventory / '4/distortion.MAGMOM'
        path.write_text('0 0 1\n')
        with self.assertRaisesRegex(ValueError, 'package changed'):
            m6.batch(self.request())
        self.assertFalse((self.root / 'batch-good').exists())
        (self.template / 'PASP.input').write_text(INPUT)
        with self.assertRaisesRegex(ValueError, 'template changed'):
            m6.batch(self.request())

    def test_dependency_preserved_and_runtime_change_blocks_batch(self):
        dependency = self.root / 'auxiliary.dat'
        dependency.write_text('established input\n')
        data = json.loads(self.prep.read_text())
        data['dependencies'] = {'auxiliary.dat': 'auxiliary.dat'}
        self.prep.write_text(json.dumps(data))
        self.prepare()
        result = m6.batch(self.request('dependency'))
        self.assertFalse(result['complete'])
        self.assertIn('dependency changed', result['results'][0]['reason'])
        self.assertEqual([r['status'] for r in result['results']], ['failed', 'not_run', 'not_run'])
        self.assertEqual(dependency.read_text(), 'established input\n')

    def test_wrapper_cli_from_other_directory_and_new_root_guard(self):
        self.prepare()
        request = self.request()
        wrapper = Path(m6.__file__).with_name('run_method6_batch.sh')
        done = subprocess.run(['bash', str(wrapper), '--request', str(request)], cwd='/tmp',
                              env={'PATH': __import__('os').environ['PATH'], 'PYTHONDONTWRITEBYTECODE': '1'},
                              text=True, capture_output=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(json.loads(done.stdout)['complete'])
        with self.assertRaisesRegex(ValueError, 'new batch root'):
            m6.batch(request)



class RestrictedPipelineTests(unittest.TestCase):
    setUp = Method6Tests.setUp
    prepare = Method6Tests.prepare
    request = Method6Tests.request
    # Reuse fixture setup, but only run the additional pipeline tests here.
    def test_restricted_same_run_launch_encoding_and_identity(self):
        from test_prepare_l3 import restricted_fixture, BASE, MODE, PHYSICS, SPECIAL, native_log
        from search_inputs import launch, check_launch
        from prepare_l3 import FDF
        # Give the basis policy the complete future encoding source corpus.
        f = restricted_fixture(self.root, BASE + MODE + PHYSICS)
        spec = f['spec']
        for sid in (4, 8, 19):
            path = self.raw / f'OUTCAR.{sid}'
            path.write_text(outcar().replace('LSORBIT = F', 'LSORBIT = T') + '\nLSORBIT = T\n')
        # Refresh the source-aware inventory after changing its synthetic sources.
        import shutil
        shutil.rmtree(self.inventory)
        with contextlib.redirect_stdout(io.StringIO()):
            pb.main([str(self.raw), '--output-dir', str(self.inventory)])
        spec['source_outcars'] = [f'raw/OUTCAR.{sid}' for sid in (4, 8, 19)]
        f['policy'].write_text(json.dumps(spec))
        fake_basis = self.root / 'fake-basis.py'
        fake_basis.write_text('from pathlib import Path\n' +
            'text=Path("PASP.input").read_text()\nassert "Invariant.SOC T" in text\n' +
            'assert ' + repr(SPECIAL) + ' in text\n' +
            'Path("local_mode_PM.dat").write_bytes(' + repr(NATIVE) + ')\n' +
            'print(' + repr(native_log()) + ')\n')
        request = self.root / 'basis-launch.json'
        request.write_text(json.dumps({'input': 'PASP.input', 'policy_request': 'policy.json',
            'command': [sys.executable, str(fake_basis)], 'timeout_seconds': 5}))
        launched = launch(request)
        data = {**spec, 'basis_input': 'PASP.input', 'basis_file': 'local_mode_PM.dat',
                'basis_log': 'log.out', 'basis_exit_code_file': 'exit.code', 'policy': 'reuse',
                'basis_execution_receipt': 'basis-execution.json', 'dependencies': spec['files']}
        self.prep.write_text(json.dumps(data))
        # Actual basis/encoding policy drift must fail before producing a template.
        changed = dict(data, soc='full')
        self.prep.write_text(json.dumps(changed))
        with self.assertRaisesRegex(ValueError, 'requires restricted'):
            self.prepare()
        self.prep.write_text(json.dumps(data))
        receipt = self.prepare()
        self.assertEqual(receipt['special_SOC'], [(1, 1, 2), (1, 2, 2), (2, 1, 2)])
        self.assertEqual(receipt['basis_execution_receipt'], launched)
        self.assertIn(SPECIAL, (self.template / 'PASP.input').read_text())
        # A changed source-corpus declaration invalidates staging even with matching dimensions.
        inventory = self.inventory / 'manifest.json'
        receipt_copy = dict(receipt)
        receipt_copy['soc_policy'] = {**receipt['soc_policy'], 'source_evidence': {**receipt['soc_policy']['source_evidence'], 'sources': []}}
        with self.assertRaisesRegex(ValueError, 'source corpus'):
            m6.stage_samples(inventory, [4, 8, 19], self.root / 'wrong-corpus',
                             m6.checked_template(self.template)[1], receipt_copy)
        result = m6.batch(self.request())
        self.assertTrue(result['complete'], result['results'])
        for sid in (4, 8, 19):
            identity = sc.load(self.root / 'batch-good' / str(sid) / 'encoding_identity.json')
            self.assertEqual(identity['soc_policy_sha256'], receipt['soc_policy_sha256'])
        self.assertEqual(identity['special_SOC'], [[1, 1, 2], [1, 2, 2], [2, 1, 2]])
        # Template omission blocks staging, rather than dropping SOC only in encoding.
        template_input = self.template / 'PASP.input'
        template_input.write_text(template_input.read_text().replace(SPECIAL, ''))
        with self.assertRaisesRegex(ValueError, 'template changed'):
            m6.batch(self.request('changed-template'))

    def test_automatic_encoding_rejects_optional_full_and_missing_execution(self):
        from test_prepare_l3 import restricted_fixture
        f = restricted_fixture(self.root)
        data = {**f['spec'], 'basis_input': 'PASP.input', 'basis_file': 'local_mode_PM.dat',
                'basis_log': 'log.out', 'basis_exit_code_file': 'exit.code', 'policy': 'reuse'}
        (self.root / 'local_mode_PM.dat').write_bytes(NATIVE)
        (self.root / 'log.out').write_text(GOOD_LOG)
        (self.root / 'exit.code').write_text('0')
        self.prep.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'execution receipt'):
            self.prepare()
        data['soc'] = 'full'
        self.prep.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'requires restricted'):
            self.prepare()


if __name__ == '__main__':
    unittest.main()
