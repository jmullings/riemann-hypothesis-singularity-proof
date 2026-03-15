#!/usr/bin/env python3
"""
TEST_DEF_01_GUE_RANDOM_MATRIX_STATISTICS.py
============================================
Mirrored unit tests for DEF_01_GUE_RANDOM_MATRIX_STATISTICS.py

Verifies:
  - GUE spacing density P_GUE(s)
  - GUE pair correlation R2(x)
  - Framework constants LAMBDA_STAR, NORM_X_STAR, GUE_EQ9_THRESHOLD
  - P1 protocol: no bare log() in the execution script

TRINITY PROTOCOL:
  P1: log-free operator check  ✓
  P2: 9D constants sourced from AXIOMS  ✓
  P3: Riemann-φ weights (not applicable to GUE statistics)
  P5: unit-test suite  ✓
"""

import os
import sys
import math
import ast
import unittest

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__),
                 *(['..'] * 5))
)
_DEF_EXEC = os.path.join(
    _REPO_ROOT,
    'FORMAL_PROOF_NEW', 'DEFINITIONS', 'DEF_1', 'EXECUTION'
)
sys.path.insert(0, _DEF_EXEC)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'FORMAL_PROOF_NEW', 'CONFIGURATIONS'))

try:
    from DEF_01_GUE_RANDOM_MATRIX_STATISTICS import (
        gue_spacing_density,
        gue_pair_correlation,
        GUE_EQ9_THRESHOLD,
        BITSIZE_OFFSET,
        ALPHA,
    )
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    _IMPORT_ERR = str(e)


class TestDef01Constants(unittest.TestCase):
    """Framework constants loaded correctly."""

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_lambda_star(self):
        self.assertAlmostEqual(LAMBDA_STAR, 494.0589555580202, places=6, msg="LAMBDA_STAR mismatch")

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_norm_x_star(self):
        self.assertAlmostEqual(NORM_X_STAR, 0.34226067113747900, places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_threshold_sign(self):
        """EQ9 threshold must be negative (energy repulsion)."""
        self.assertLess(GUE_EQ9_THRESHOLD, 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_threshold_value(self):
        self.assertAlmostEqual(GUE_EQ9_THRESHOLD, -(NORM_X_STAR ** 2) / 10, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_bitsize_offset(self):
        self.assertAlmostEqual(BITSIZE_OFFSET, 2.96, places=8)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_alpha(self):
        self.assertAlmostEqual(ALPHA, 0.864, places=8)


class TestDef01GUESpacingDensity(unittest.TestCase):
    """GUE Wigner surmise P_GUE(s)."""

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_zero_at_s0(self):
        self.assertAlmostEqual(gue_spacing_density(0.0), 0.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_level_repulsion_near_zero(self):
        """P_GUE(0.1) should be very small (quadratic level repulsion)."""
        self.assertLess(gue_spacing_density(0.1), 0.1)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_peak_near_one(self):
        """P_GUE peaks around s ≈ 1.0."""
        p1 = gue_spacing_density(1.0)
        self.assertAlmostEqual(p1, 0.907589, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_half(self):
        self.assertAlmostEqual(gue_spacing_density(0.5), 0.589590, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_decay_at_large_s(self):
        """P_GUE must decay for large spacings."""
        self.assertLess(gue_spacing_density(3.0), gue_spacing_density(1.0))

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_non_negative(self):
        for s in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
            with self.subTest(s=s):
                self.assertGreaterEqual(gue_spacing_density(s), 0.0)


class TestDef01PairCorrelation(unittest.TestCase):
    """GUE pair correlation R2(x)."""

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_level_repulsion_at_zero(self):
        self.assertAlmostEqual(gue_pair_correlation(0.0), 0.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_unity_at_one(self):
        """R2(1) should equal exactly 1 (sin(π)/π = 0)."""
        self.assertAlmostEqual(gue_pair_correlation(1.0), 1.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_unity_at_two(self):
        self.assertAlmostEqual(gue_pair_correlation(2.0), 1.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_half(self):
        self.assertAlmostEqual(gue_pair_correlation(0.5), 0.594715, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_quarter(self):
        self.assertAlmostEqual(gue_pair_correlation(0.25), 0.189431, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_range_0_to_1(self):
        for x in [0.1, 0.3, 0.5, 0.7, 0.9]:
            with self.subTest(x=x):
                v = gue_pair_correlation(x)
                self.assertGreaterEqual(v, 0.0)
                self.assertLessEqual(v, 1.00001)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_symmetry(self):
        """R2 should be symmetric: R2(x) = R2(-x)."""
        for x in [0.3, 0.7, 1.5]:
            with self.subTest(x=x):
                self.assertAlmostEqual(
                    gue_pair_correlation(x),
                    gue_pair_correlation(-x),
                    places=12
                )


class TestDef01P1Compliance(unittest.TestCase):
    """Protocol P1: no bare log() call in the execution script."""

    def test_no_bare_log_in_source(self):
        src_path = os.path.join(_DEF_EXEC, 'DEF_01_GUE_RANDOM_MATRIX_STATISTICS.py')
        if not os.path.exists(src_path):
            self.skipTest("Source file not found")
        tree = ast.parse(open(src_path).read())
        log_nodes = [
            n for n in ast.walk(tree)
            if (isinstance(n, ast.Attribute) and n.attr == 'log')
            or (isinstance(n, ast.Name) and n.id == 'log')
        ]
        self.assertEqual(log_nodes, [],
                         msg=f"P1 violation: log() found at lines {[n.lineno for n in log_nodes]}")


class TestDef01ImportSuccess(unittest.TestCase):
    """Smoke test: module must import without error."""

    def test_import(self):
        if not IMPORT_OK:
            self.fail(f"DEF_01 import failed: {_IMPORT_ERR}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
