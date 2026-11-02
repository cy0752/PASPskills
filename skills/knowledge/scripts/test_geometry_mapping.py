"""Regression tests for endpoint-orbit and periodic-image auditing."""
import unittest

import numpy as np
import spglib

import geometry_mapping as gm


LATTICE = [[4.0, 0, 0], [0, 4.0, 0], [0, 0, 4.0]]
SITES = [{"frac": [0, 0, 0], "species": "Fe"},
         {"frac": [0.25, 0, 0], "species": "Fe"},
         {"frac": [0, 0.25, 0], "species": "Fe"},
         {"frac": [0.25, 0.25, 0], "species": "Fe"}]


def pair(a, b, image_b=(0, 0, 0)):
    return [
        {"site": a, "frac": SITES[a]["frac"], "species": "Fe", "image": [0, 0, 0]},
        {"site": b, "frac": SITES[b]["frac"], "species": "Fe", "image": list(image_b)},
    ]


class GeometryMapping(unittest.TestCase):
    def test_swapped_equal_vector_rows_under_actual_space_group(self):
        # Chemical decorations remove the translation/reflection connecting
        # these equal-vector Fe bonds. Derive the full group from geometry,
        # rather than assuming that a supplied subset proves distinctness.
        lattice = np.array([[4., 0, 0], [.3, 4.7, 0], [.6, .8, 5.2]])
        frac = np.array([s["frac"] for s in SITES] + [[.137, .219, .317], [.421, .623, .853]])
        symmetry = spglib.get_symmetry((lattice, frac, [26] * 4 + [8] * 2), symprec=1e-5)
        self.assertIsNotNone(symmetry)
        ops = [{"rotation": r.T.tolist(), "translation": t.tolist()}
               for r, t in zip(symmetry["rotations"], symmetry["translations"])]
        source = [pair(0, 1), pair(2, 3)]
        self.assertTrue(np.allclose((frac[1] - frac[0]) @ lattice,
                                    (frac[3] - frac[2]) @ lattice))
        expected = [gm.orbit_signature(p, ops) for p in source]
        self.assertNotEqual(expected[0], expected[1])
        self.assertNotEqual(expected, [gm.orbit_signature(p, ops) for p in reversed(source)])
        # Exchanging endpoint order or adding a class label cannot invent a
        # different orbit for identical geometry.
        decorated = [dict(e, class_id="arbitrary") for e in reversed(source[0])]
        self.assertEqual(expected[0], gm.orbit_signature(decorated, ops))

    def test_equal_distance_pairs_have_distinct_geometry_signatures(self):
        # Both bonds are 1 Angstrom, but their endpoint locations are distinct.
        first = pair(0, 1)
        second = pair(2, 3)
        operations = [
            {"rotation": [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "translation": [0, 0, 0]},
            {"rotation": [[-1, 0, 0], [0, 1, 0], [0, 0, 1]],
             "translation": [0.25, 0, 0]},
        ]
        self.assertNotEqual(gm.orbit_signature(first, operations),
                            gm.orbit_signature(second, operations))
        groups = gm.orbit_groups([first, second], operations)
        self.assertEqual(sorted(len(v) for v in groups.values()), [1, 1])

    def test_relative_image_is_preserved_in_long_bond(self):
        source = pair(0, 1, (1, 0, 0))
        payload = {"source_lattice": LATTICE, "source_sites": SITES, "pairs": [source],
                   "final": {"lattice": LATTICE, "sites": SITES}}
        result = gm.audit(payload)
        self.assertEqual(result["pairs"][0]["source"][1]["image"], [1, 0, 0])
        self.assertEqual(result["pairs"][0]["final"][1]["final_image"], [1, 0, 0])
        self.assertGreater(result["pairs"][0]["final"][1]["cartesian"][0], 4.0)
        self.assertEqual(result["pairs"][0]["source_bond_cartesian"], [5.0, 0.0, 0.0])
        self.assertEqual(result["pairs"][0]["final_bond_cartesian"], [5.0, 0.0, 0.0])
        self.assertEqual(result["pairs"][0]["bond_residual_angstrom"], 0.0)

    def test_mismatched_final_lattice_is_rejected_at_strict_tolerance(self):
        source = pair(0, 1)
        final = {"lattice": [[4.0002414, 0, 0], [0, 4, 0], [0, 0, 4]], "sites": SITES}
        with self.assertRaisesRegex(gm.GeometryError, "residual"):
            gm.audit({"source_lattice": LATTICE, "source_sites": SITES, "pairs": [source],
                      "final": final, "tolerance_angstrom": 1e-5})

    def test_supercell_to_primitive_keeps_integer_image_in_pair_mapping(self):
        # A 2x source supercell has two translationally equivalent sites.  The
        # second source site must map to image 1 of the one-site primitive;
        # reducing it to a minimum image would change the 4 Angstrom bond.
        source_lattice = [[8.0, 0, 0], [0, 4, 0], [0, 0, 4]]
        source_sites = [{"frac": [0, 0, 0], "species": "Fe"},
                        {"frac": [0.5, 0, 0], "species": "Fe"}]
        source_pair = [
            {"site": 0, "frac": [0, 0, 0], "species": "Fe", "image": [0, 0, 0]},
            {"site": 1, "frac": [0.5, 0, 0], "species": "Fe", "image": [0, 0, 0]},
        ]
        result = gm.audit({"source_lattice": source_lattice, "source_sites": source_sites,
                           "pairs": [source_pair],
                           "final": {"lattice": LATTICE, "sites": [{"frac": [0, 0, 0], "species": "Fe"}]}})
        row = result["pairs"][0]
        self.assertEqual(row["final"][1]["final_image"], [1, 0, 0])
        self.assertEqual(row["source_bond_cartesian"], [4.0, 0.0, 0.0])
        self.assertEqual(row["final_bond_cartesian"], [4.0, 0.0, 0.0])
        self.assertEqual(row["bond_residual_angstrom"], 0.0)

    def test_pair_mapping_rejects_collapsed_relative_image(self):
        source = pair(0, 1, (1, 0, 0))
        # The final site is displaced enough that even the correct integer
        # image cannot reproduce the source long bond.
        final = {"lattice": LATTICE,
                 "sites": [{"frac": [0, 0, 0], "species": "Fe"},
                           {"frac": [0.30, 0, 0], "species": "Fe"}]}
        with self.assertRaisesRegex(gm.GeometryError, "residual"):
            gm.audit({"source_lattice": LATTICE, "source_sites": SITES,
                      "pairs": [source], "final": final, "tolerance_angstrom": 1e-5})

    def test_species_and_site_identity_are_checked(self):
        bad = pair(0, 1)
        bad[1]["species"] = "O"
        with self.assertRaisesRegex(gm.GeometryError, "species"):
            gm.audit({"source_lattice": LATTICE, "source_sites": SITES, "pairs": [bad]})

    def test_endpoint_coordinate_must_match_claimed_source_site(self):
        bad = pair(0, 1)
        bad[1]["frac"] = SITES[3]["frac"]
        with self.assertRaisesRegex(gm.GeometryError, "claimed source site"):
            gm.audit({"source_lattice": LATTICE, "source_sites": SITES, "pairs": [bad]})

    def test_image_must_be_exact_integer_triplet(self):
        bad = pair(0, 1)
        bad[1]["image"] = [0.5, 0, 0]
        with self.assertRaisesRegex(gm.GeometryError, "malformed frac/image"):
            gm.audit({"source_lattice": LATTICE, "source_sites": SITES, "pairs": [bad]})

    def test_two_final_sites_within_tolerance_are_ambiguous(self):
        near_duplicate = {"frac": [0.250001, 0, 0], "species": "Fe"}
        final = {"lattice": LATTICE, "sites": SITES + [near_duplicate]}
        with self.assertRaisesRegex(gm.GeometryError, "not unique"):
            gm.audit({"source_lattice": LATTICE, "source_sites": SITES,
                      "pairs": [pair(0, 1)], "final": final})


if __name__ == "__main__":
    unittest.main()
