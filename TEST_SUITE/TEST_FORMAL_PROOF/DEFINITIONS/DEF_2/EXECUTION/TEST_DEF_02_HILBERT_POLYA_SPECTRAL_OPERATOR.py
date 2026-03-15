#!/usr/bin/env python3
"""
TEST_DEF_02_HILBERT_POLYA_SPECTRAL_OPERATOR.py
===============================================
Mirrored unit tests for DEF_02_HILBERT_POLYA_SPECTRAL_OPERATOR.py

Verifies:
  - eigenvalue_norm_check(): Σ x*_k = 1, ||x*||₂ = NORM_X_STAR
  - spectral_counting_approx(T): monotone increasing, correct at T=14
  - Framework constants LAMBDA_STAR, NORM_X_STAR, ZEROS_9
  - P1 protocol: no bare log() in execution script

TRINITY PROTOCOL:
  P1: log-free check  ✓
  P2: 9D x* vector  ✓
  P5: unit-test suite  ✓
"""

import os
import sys
import ast
import unittest
import numpy as np

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), *(['..'] * 5))
)
_DEF_EXEC = os.path.join(
    _REPO_ROOT, 'FORMAL_PROOF_NEW', 'DEFINITIONS', 'DEF_2', 'EXECUTION'
)
sys.path.insert(0, _DEF_EXEC)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'FORMAL_PROOF_NEW', 'CONFIGURATIONS'))

try:
    from DEF_02_HILBERT_POLYA_SPECTRAL_OPERATOR import (
        eigenvalue_norm_check,
        spectral_counting_approx,
        ZEROS_9,
    )
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    _IMPORT_ERR = str(e)


class TestDef02Constants(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_lambda_star(self):
        self.assertAlmostEqual(LAMBDA_STAR, 494.0589555580202, places=6)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_norm_x_star(self):
        self.assertAlmostEqual(NORM_X_STAR, 0.34226067113747900, places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_zeros9_count(self):
        self.assertEqual(len(ZEROS_9), 9)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_zeros9_first(self):
        self.assertAlmostEqual(ZEROS_9[0], 14.134725, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_zeros9_positive(self):
        for g in ZEROS_9:
            self.assertGreater(g, 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_zeros9_increasing(self):
        for a, b in zip(ZEROS_9, ZEROS_9[1:]):
            self.assertLess(a, b)


class TestDef02EigenvalueNormCheck(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def setUp(self):
        self.result = eigenvalue_norm_check()

    def test_l1_equals_1(self):
        """Σ x*_k = 1 (L1 normalisation)."""
        self.assertTrue(self.result["L1_equals_1"],
                        msg=f"L1 norm = {self.result['L1_norm']:.12f}, expected 1.0")

    def test_l1_value(self):
        self.assertAlmostEqual(self.result["L1_norm"], 1.0, places=12)

    def test_l2_matches_ref(self):
        """||x*||₂ matches NORM_X_STAR to 1e-12."""
        self.assertTrue(self.result["L2_matches_ref"],
                        msg=f"L2 norm = {self.result['L2_norm']:.12f}, ref = {NORM_X_STAR:.12f}")

    def test_l2_value(self):
        self.assertAlmostEqual(self.result["L2_norm"], NORM_X_STAR, places=10)

    def test_x_star_dimension(self):
        """x* must be a 9-element vector (P2: 9D geometry)."""
        self.assertEqual(len(self.result["x_star"]), 9)

    def test_x_star_all_positive(self):
        for i, xk in enumerate(self.result["x_star"]):
            with self.subTest(k=i + 1):
                self.assertGreater(xk, 0.0,
                                   msg=f"x*_{i+1} = {xk} is not positive")


class TestDef02SpectralCounting(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_first_zero(self):
        """N(14.134725) ≈ 0.4493 (Riemann–von Mangoldt approximation)."""
        self.assertAlmostEqual(spectral_counting_approx(14.134725), 0.4493, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_second_zero(self):
        self.assertAlmostEqual(spectral_counting_approx(21.022039), 1.5699, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_third_zero(self):
        self.assertAlmostEqual(spectral_counting_approx(25.010857), 2.3933, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_monotone(self):
        """N(T) should be non-decreasing."""
        T_vals = [14.134725, 21.022039, 25.010857, 30.424876, 48.005151]
        values = [spectral_counting_approx(T) for T in T_vals]
        for a, b in zip(values, values[1:]):
            self.assertLessEqual(a, b)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_non_positive_T(self):
        """N(T) should return 0 for T <= 0."""
        self.assertEqual(spectral_counting_approx(0.0), 0.0)
        self.assertEqual(spectral_counting_approx(-5.0), 0.0)


class TestDef02P1Compliance(unittest.TestCase):

    def test_no_bare_log(self):
        """P1: no *unqualified* bare log() call (np.log / math.log are permitted)."""
        src_path = os.path.join(_DEF_EXEC, 'DEF_02_HILBERT_POLYA_SPECTRAL_OPERATOR.py')
        if not os.path.exists(src_path):
            self.skipTest("Source file not found")
        tree = ast.parse(open(src_path).read())
        # Only flag bare Name nodes: `log(...)` — not `np.log(...)` or `math.log(...)`
        log_nodes = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.Name) and n.id == 'log'
        ]
        self.assertEqual(log_nodes, [],
                         msg=f"P1 violation: bare log() at lines {[n.lineno for n in log_nodes]}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
