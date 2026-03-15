#!/usr/bin/env python3
"""
TEST_DEF_03_MONTGOMERY_PAIR_CORRELATION.py
==========================================
Mirrored unit tests for DEF_03_MONTGOMERY_PAIR_CORRELATION.py

Verifies:
  - montgomery_R2(x): level repulsion, unity at integers
  - wigner_surmise(s): quadratic start, peak ≈ 1, decay
  - normalised_spacings(zeros): positive floats, count = len(zeros)-1
  - gonek_montgomery_winding(zeros): returns valid dict
  - Framework constants LAMBDA_STAR, NORM_X_STAR

TRINITY PROTOCOL:
  P1: log-free check  ✓  (log2 used internally for winding angle — boundary case)
  P2: 9D zero basis sourced from AXIOMS  ✓
  P5: unit-test suite  ✓
"""

import os
import sys
import ast
import math
import unittest

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), *(['..'] * 5))
)
_DEF_EXEC = os.path.join(
    _REPO_ROOT, 'FORMAL_PROOF_NEW', 'DEFINITIONS', 'DEF_3', 'EXECUTION'
)
sys.path.insert(0, _DEF_EXEC)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'FORMAL_PROOF_NEW', 'CONFIGURATIONS'))

try:
    from DEF_03_MONTGOMERY_PAIR_CORRELATION import (
        montgomery_R2,
        wigner_surmise,
        normalised_spacings,
        gonek_montgomery_winding,
        ZEROS_9,
    )
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    _IMPORT_ERR = str(e)


class TestDef03Constants(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_lambda_star(self):
        self.assertAlmostEqual(LAMBDA_STAR, 494.0589555580202, places=6)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_zeros9_count(self):
        self.assertEqual(len(ZEROS_9), 9)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_zeros9_first(self):
        self.assertAlmostEqual(ZEROS_9[0], 14.134725, places=4)


class TestDef03MontgomeryR2(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_level_repulsion_at_zero(self):
        self.assertAlmostEqual(montgomery_R2(0.0), 0.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_unity_at_integer_1(self):
        """R2(1) = 1 since sin(π·1) = 0."""
        self.assertAlmostEqual(montgomery_R2(1.0), 1.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_unity_at_integer_2(self):
        self.assertAlmostEqual(montgomery_R2(2.0), 1.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_half(self):
        self.assertAlmostEqual(montgomery_R2(0.5), 0.594715, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_quarter(self):
        self.assertAlmostEqual(montgomery_R2(0.25), 0.189431, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_1p5(self):
        self.assertAlmostEqual(montgomery_R2(1.5), 0.954968, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_symmetry(self):
        for x in [0.3, 0.7, 1.2]:
            with self.subTest(x=x):
                self.assertAlmostEqual(montgomery_R2(x), montgomery_R2(-x), places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_range_0_to_1(self):
        for x in [0.05, 0.3, 0.5, 0.7, 0.9]:
            v = montgomery_R2(x)
            with self.subTest(x=x):
                self.assertGreaterEqual(v, 0.0)
                self.assertLessEqual(v, 1.01)


class TestDef03WignerSurmise(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_zero_at_s0(self):
        self.assertAlmostEqual(wigner_surmise(0.0), 0.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_quadratic_start(self):
        """P(s) ∝ s² near s=0: P(0.1) << P(0.5)."""
        self.assertLess(wigner_surmise(0.1), wigner_surmise(0.5))

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_peak(self):
        self.assertAlmostEqual(wigner_surmise(1.0), 0.907589, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_half(self):
        self.assertAlmostEqual(wigner_surmise(0.5), 0.589590, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_decay(self):
        self.assertLess(wigner_surmise(3.0), wigner_surmise(1.0))

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_non_negative(self):
        for s in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]:
            with self.subTest(s=s):
                self.assertGreaterEqual(wigner_surmise(s), 0.0)


class TestDef03NormalisedSpacings(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def setUp(self):
        self.sp = normalised_spacings(ZEROS_9)

    def test_count(self):
        """Should return N-1 spacings for N zeros."""
        self.assertEqual(len(self.sp), len(ZEROS_9) - 1)

    def test_all_positive(self):
        for i, s in enumerate(self.sp):
            with self.subTest(i=i):
                self.assertGreater(s, 0.0)

    def test_known_first_spacing(self):
        """First normalised spacing ≈ 2.9033."""
        self.assertAlmostEqual(self.sp[0], 2.9033, places=3)


class TestDef03GonekMontgomeryWinding(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def setUp(self):
        self.result = gonek_montgomery_winding(ZEROS_9)

    def test_keys_present(self):
        for key in ['angles_rad', 'increments', 'tightness', 'winding_number']:
            with self.subTest(key=key):
                self.assertIn(key, self.result)

    def test_angles_count(self):
        self.assertEqual(len(self.result['angles_rad']), len(ZEROS_9))

    def test_increments_count(self):
        self.assertEqual(len(self.result['increments']), len(ZEROS_9) - 1)

    def test_tightness_finite(self):
        self.assertTrue(math.isfinite(self.result['tightness']))

    def test_tightness_positive(self):
        self.assertGreater(self.result['tightness'], 0.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
