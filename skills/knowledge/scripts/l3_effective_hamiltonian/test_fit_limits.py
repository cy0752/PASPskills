"""Regression tests for the pre-fit candidate and retained-term gates."""
import unittest

from fit_limits import check_candidate_width, check_retained_count


class FitLimitTests(unittest.TestCase):
    def test_700_points_1857_candidates_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "1857 > 1050"):
            check_candidate_width(1857, 700)

    def test_700_points_1050_candidates_are_allowed(self):
        result = check_candidate_width(1050, 700)
        self.assertEqual(result["candidate_feature_limit"], 1050)

    def test_retained_terms_use_150_cap_and_data_limit(self):
        self.assertEqual(check_retained_count(150, 700)["retained_limit"], 150)
        with self.assertRaisesRegex(ValueError, "151 > 150"):
            check_retained_count(151, 700)
        with self.assertRaisesRegex(ValueError, "101 > 100"):
            check_retained_count(101, 67)


if __name__ == "__main__":
    unittest.main()
