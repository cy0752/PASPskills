#!/usr/bin/env python3
"""Render checked Cartesian cells/species/modes from established geometry facts.

Does not discover symmetry or choose a primitive, species, spin scale or orbit.
Optional reference_cell and relation are checked before publication. No PASP run.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

from prepare_l3 import FDF, check
from structure_mapping import _det, _inverse, _norm, _row_matrix, check as check_mapping
from study_contract import digest, json_bytes, load, number, require, write_package


def vector(value, name):
    require(isinstance(value, list) and len(value) == 3, f'{name} needs three values')
    return [number(x) for x in value]


def cell(value, species, tolerance):
    lattice = value['lattice_angstrom']
    require(isinstance(lattice, list) and len(lattice) == 3, 'lattice needs three rows')
    lattice = [vector(row, 'lattice row') for row in lattice]
    require(_det(lattice) > 1e-14, 'lattice must be nonsingular and right-handed')
    inverse = _inverse(lattice)
    require(isinstance(value['sites'], list) and value['sites'], 'sites must be non-empty')
    sites, fractional = [], []
    for site in value['sites']:
        require(set(site) == {'position_angstrom', 'species_id', 'element'}, 'invalid site fields')
        sid = site['species_id']
        require(type(sid) is int and 1 <= sid <= len(species), 'site species_id out of range')
        require(site['element'] == species[sid - 1]['element'], 'site element/species_id mismatch')
        position = vector(site['position_angstrom'], 'site position')
        frac = _row_matrix(position, inverse)
        for old in fractional:
            delta = [a - b - round(a - b) for a, b in zip(frac, old)]
            require(_norm(_row_matrix(delta, lattice)) > tolerance, 'duplicate periodic site')
        fractional.append(frac)
        sites.append(dict(site, position_angstrom=position))
    require({s['species_id'] for s in sites} == set(range(1, len(species) + 1)),
            'every declared species needs a site')
    return lattice, sites, fractional


def render_cell(lattice, sites, species_count, unit=False):
    count_key = 'unit_cell.na' if unit else 'NumberOfAtoms'
    lattice_key = 'unit_cell_in_Ang' if unit else 'LatticeVectors'
    sites_key = 'Atoms_in_unit_cell_Ang' if unit else 'AtomicCoordinatesAndAtomicSpecies'
    lines = [f'{count_key} {len(sites)}']
    if not unit:
        lines += [f'number_of_species {species_count}', 'LatticeConstant 1 Ang',
                  'AtomicCoordinatesFormat NotScaledCartesianAng']
    lines += [f'%block {lattice_key}']
    lines += [' '.join(f'{v:.16g}' for v in row) for row in lattice]
    lines += [f'%endblock {lattice_key}', f'%block {sites_key}']
    for index, site in enumerate(sites, 1):
        xyz = ' '.join(f'{v:.16g}' for v in site['position_angstrom'])
        lines.append(f"{xyz} {site['species_id']} {site['element']} {index}")
    lines += [f'%endblock {sites_key}', '']
    return '\n'.join(lines)


def build(manifest, output):
    manifest, root = Path(manifest).resolve(), Path(output).absolute()
    require(not root.exists(), 'use a new output directory; preserve previous attempts')
    spec = load(manifest)
    required = {'lattice_angstrom', 'sites', 'species', 'spin_values', 'representatives', 'tolerance_angstrom'}
    require(required <= set(spec) <= required | {'reference_cell', 'relation'}, 'invalid manifest fields')
    require(('reference_cell' in spec) == ('relation' in spec), 'reference_cell requires relation and vice versa')
    tolerance = number(spec['tolerance_angstrom'])
    require(tolerance > 0, 'positive coordinate tolerance required')
    species = spec['species']
    require(isinstance(species, list) and species and all(isinstance(s, dict) and
            set(s) == {'element', 'z_value'} and isinstance(s['element'], str) and
            re.fullmatch(r'[A-Z][a-z]?', s['element']) and type(s['z_value']) is int and
            1 <= s['z_value'] <= 118 for s in species), 'invalid element/Z_values species records')
    require(len({s['element'] for s in species}) == len(species), 'duplicate species element')
    require(isinstance(spec['spin_values'], list) and len(spec['spin_values']) == len(species),
            'Spin_values/species count differs')
    spins = [number(v) for v in spec['spin_values']]
    require(all(v >= 0 for v in spins), 'Spin_values must be nonnegative')
    lattice, sites, frac = cell(spec, species, tolerance)
    ref_lattice, ref_sites, ref_frac = cell(spec.get('reference_cell', spec), species, tolerance)
    relation = spec.get('relation', [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    mapping = check_mapping({'primitive': {'lattice': ref_lattice, 'sites': [
                {'species': s['element'], 'frac': f} for s, f in zip(ref_sites, ref_frac)]},
            'configuration': {'lattice': lattice, 'sites': [
                {'species': s['element'], 'frac': f} for s, f in zip(sites, frac)]},
            'relation': relation, 'tolerance_angstrom': tolerance})
    reps = spec['representatives']
    require(isinstance(reps, list) and reps, 'representatives must be non-empty')
    modes, matched = [], []
    inverse = _inverse(ref_lattice)
    for rep in reps:
        require(isinstance(rep, dict) and set(rep) == {'species_id', 'position_angstrom'},
                'invalid representative fields')
        sid = rep['species_id']
        require(type(sid) is int and 1 <= sid <= len(spins) and spins[sid - 1] > 0,
                'representative species must be active in Spin_values')
        position = vector(rep['position_angstrom'], 'representative position')
        f = _row_matrix(position, inverse)
        matches = []
        for index, (s, g) in enumerate(zip(ref_sites, ref_frac)):
            delta = [a - b - round(a - b) for a, b in zip(f, g)]
            if s['species_id'] == sid and _norm(_row_matrix(delta, ref_lattice)) <= tolerance:
                matches.append(index)
        require(len(matches) == 1 and matches[0] not in matched, 'representative missing/duplicate in reference cell')
        matched += matches
        for axis in range(3):
            values = position + [int(axis == component) for component in range(3)]
            modes.append(f'1 spin\n{sid}\n' + ' '.join(f'{x:.16g}' for x in values))
    modes_text = '%block local_mode.mode_definition\n2\n' + str(len(modes)) + '\n'
    modes_text += '\n\n'.join(modes) + '\n%endblock local_mode.mode_definition\n'
    species_text = '%block Z_values\n' + ' '.join(str(s['z_value']) for s in species) + '\n%endblock Z_values\n'
    species_text += '%block Spin_values\n' + ' '.join(f'{s:.16g}' for s in spins) + '\n%endblock Spin_values\n'
    files = {'cell.str': render_cell(lattice, sites, len(species)).encode(),
             'unit_cell.str': render_cell(ref_lattice, ref_sites, len(species), unit=True).encode(),
             'mode_definition.fdf': (species_text + modes_text).encode()}
    # Re-read generated FDF in memory before publication; no read of source code.
    doc = FDF.__new__(FDF)
    doc.cwd, doc.hashes = root, {}
    generated = 'Model Invariant\nInvariant.SOC F\n' + ''.join(v.decode() for v in files.values())
    doc.entries = doc.parse(generated, Path('<generated>'), ())
    checked = check(doc, 'off')  # shape-only validation; this does not choose or authorize SOC.
    receipt = {'schema': 'l3-geometry-package-v1', 'manifest_sha256': digest(manifest.read_bytes()),
               'site_count': len(sites), 'reference_site_count': len(ref_sites),
               'species_count': len(species), 'mode_count': checked['mode_count'],
               'spin_values': spins, 'representative_reference_indices': matched, 'mapping': mapping,
               'scope': 'Cartesian file rendering, cell relation/site correspondence and single-atom mode shape',
               'not_covered': ['symmetry equivalence/representative completeness', 'element/Z chemistry',
                               'SOC restriction/operator choice', 'energy convention', 'native executable outputs'],
               'usage': 'include cell.str, unit_cell.str and mode_definition.fdf; choose/gate physics separately; relation is not PASP SuperCell'}
    return write_package(root, files, 'geometry-package.json', receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json_bytes(build(args.manifest, args.output)).decode(), end='')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        raise SystemExit(f'error: {exc}')
