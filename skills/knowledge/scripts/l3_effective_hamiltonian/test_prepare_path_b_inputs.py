"""Synthetic OUTCAR regressions; no PASP calculation or material defaults."""
import json
from pathlib import Path
import tempfile
import unittest

import prepare_path_b_inputs as pb


def outcar(energy='-1.25D+01', species='Fe', moment='0.4'):
    header = f'VRHFIN ={species}:\n ions per type = 1\n'
    lattice = (' direct lattice vectors reciprocal lattice vectors\n'
               '2 0 0 1 0 0\n1 3 0 0 1 0\n0.5 0.25 4 0 0 1\n')
    step = (' POSITION TOTAL-FORCE\n ------\n0.1 0.2 0.3 0 0 0\n'
            ' free energy TOTEN = -20 eV\n')
    final = ' POSITION TOTAL-FORCE\n ------\n1.25 1.625 2 0 0 0\n'
    for axis, value in zip('xyz', [moment, '0.0', '0.3']):
        final += f' magnetization ({axis})\n # of ion s p d tot\n -----\n 1 0 0 0 {value}\n tot 0\n'
    return header + lattice + step + final + f' free energy TOTEN = {energy} eV\n'


class PathBTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.raw = self.root / 'raw'
        self.raw.mkdir()

    def sample(self, name, text=None):
        p = self.raw / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(outcar() if text is None else text)
        return p

    def generate(self, *extra):
        dest = self.root / 'prepared'
        pb.main([str(self.raw), '--output-dir', str(dest), *extra])
        return dest

    def test_prefix_suffix_and_nonconsecutive_ids(self):
        self.sample('OUTCAR.19')
        self.sample('4.OUTCAR')
        self.sample('8/OUTCAR')
        dest = self.generate('--normalize-magmoms', '--coordinate-mode', 'Direct')
        receipt = json.loads((dest / 'manifest.json').read_text())
        self.assertEqual([s['id'] for s in receipt['samples']], [4, 8, 19])
        self.assertEqual(receipt['sample_count'], 3)
        self.assertFalse((dest / 'OUTCAR').exists())
        pos = (dest / '19/distortion.pos').read_text().splitlines()
        self.assertEqual(pos[7], 'Direct')
        for got, want in zip(map(float, pos[8].split()), [0.25, 0.5, 0.5]):
            self.assertAlmostEqual(got, want)
        self.assertEqual((dest / '19/distortion.MAGMOM').read_text().split(), ['0.8000000000', '0.0000000000', '0.6000000000'])
        self.assertEqual(receipt['samples'][2]['energy_ev'], -12.5)
        ledger = json.loads((dest / '19/source_identity.json').read_text())
        self.assertEqual(ledger['original_id'], 19)
        self.assertEqual((dest / '19' / ledger['outcar']).resolve(), (self.raw / 'OUTCAR.19').resolve())

    def test_single_prefix_and_legacy_symbolic_id(self):
        for name, sid in [('OUTCAR.17', '17'), ('sample.OUTCAR', 'sample')]:
            p = self.sample(name)
            self.assertEqual(pb.discover_outcars(p), [(sid, p)])

    def test_explicit_prefix_pattern_keeps_ids(self):
        self.sample('OUTCAR.2')
        self.sample('OUTCAR.9')
        self.assertEqual([s for s, _ in pb.discover_outcars(self.raw, 'OUTCAR.*')], ['2', '9'])

    def test_duplicates_and_missing_directories_fail(self):
        self.sample('OUTCAR.1')
        self.sample('01.OUTCAR')
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            self.generate()
        (self.raw / '01.OUTCAR').unlink()
        (self.raw / '2').mkdir()
        with self.assertRaisesRegex(ValueError, 'missing numbered'):
            self.generate()
        self.assertFalse((self.root / 'prepared').exists())

    def test_source_alias_under_different_ids_fails(self):
        p = self.sample('1.OUTCAR')
        (self.raw / '2.OUTCAR').symlink_to(p)
        with self.assertRaisesRegex(ValueError, 'source reused'):
            self.generate()

    def test_later_species_mismatch_leaves_no_package(self):
        self.sample('OUTCAR.1')
        self.sample('OUTCAR.2', outcar(species='Co'))
        with self.assertRaisesRegex(ValueError, 'species/order/count'):
            self.generate()
        self.assertFalse((self.root / 'prepared').exists())

    def test_truncated_final_magnetization_rejects_earlier_complete_state(self):
        self.sample('1.OUTCAR', outcar() + ' magnetization (x)\n # of ion s p d tot\n 1 0 0 0 2\n')
        with self.assertRaisesRegex(ValueError, 'incomplete final'):
            self.generate()
        self.assertFalse((self.root / 'prepared').exists())

    def test_partial_axes_and_nonfinite_moments(self):
        self.sample('1.OUTCAR', outcar().replace('magnetization (z)', 'missing axis'))
        with self.assertRaisesRegex(ValueError, 'partial'):
            self.generate()
        self.sample('1.OUTCAR', outcar(moment='NaN'))
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            self.generate()

    def test_invalid_numeric_geometry_and_energy(self):
        for old, new in [('2 0 0 1 0 0', 'NaN 0 0 1 0 0'),
                         ('0.5 0.25 4 0 0 1', '0 0 0 0 0 1'),
                         ('1.25 1.625 2 0 0 0', '1.25 1.625'),
                         ('-1.25D+01', 'Inf')]:
            with self.subTest(new=new):
                self.sample('1.OUTCAR', outcar().replace(old, new))
                with self.assertRaises(ValueError):
                    self.generate()
                self.assertFalse((self.root / 'prepared').exists())

    def test_new_directory_and_legacy_energy_header(self):
        self.sample('1.OUTCAR')
        dest = self.generate('--primitive-cells', '2')
        self.assertEqual((dest / 'Energy.dat').read_text().splitlines(), ['2', '1 -12.5'])
        with self.assertRaisesRegex(ValueError, 'new output'):
            self.generate()

    def test_invalid_count_reference_and_output_path(self):
        self.sample('1.OUTCAR')
        with self.assertRaisesRegex(ValueError, 'positive'):
            self.generate('--primitive-cells', '0')
        ref = self.root / 'POSCAR'
        ref.write_text('test\n1\n1 0 0\n0 1 0\n0 0 1\nCo\n1\n')
        with self.assertRaisesRegex(ValueError, 'species/order/count'):
            self.generate('--poscar-reference', str(ref))
        with self.assertRaises(ValueError):
            self.generate('--primitive-cells', '1', '--energy-out', '../escape')
        self.assertFalse((self.root / 'escape').exists())


if __name__ == '__main__':
    unittest.main()
