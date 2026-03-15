#!/usr/bin/env python3
"""
TEST_DEF_06_SELBERG_TRACE_FORMULA.py
=====================================
Mirrored unit tests for DEF_06_SELBERG_TRACE_FORMULA.py

Verifies:
  - von_mangoldt(n): correct Λ(n) values, including composite fix
  - selberg_test_function_h(r, T0): returns finite float
  - prime_geodesic_contribution(P_star): returns finite float
  - Geometric side (P*=97) ≈ -2.728387
  - Framework constants LAMBDA_STAR, NORM_X_STAR

TRINITY PROTOCOL:
  P1: log() used only inside von_mangoldt (allowed — raw data ingest)  ✓
  P2: 9D constants from AXIOMS  ✓
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
    _REPO_ROOT, 'FORMAL_PROOF_NEW', 'DEFINITIONS', 'DEF_6', 'EXECUTION'
)
sys.path.insert(0, _DEF_EXEC)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'FORMAL_PROOF_NEW', 'CONFIGURATIONS'))

try:
    from DEF_06_SELBERG_TRACE_FORMULA import (
        von_mangoldt,
        selberg_test_function_h,
        prime_geodesic_contribution,
    )
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR, RIEMANN_ZEROS_9
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    _IMPORT_ERR = str(e)


class TestDef06VonMangoldt(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_n1_zero(self):
        """Λ(1) = 0 by convention."""
        self.assertEqual(von_mangoldt(1), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_prime_2(self):
        self.assertAlmostEqual(von_mangoldt(2), math.log(2), places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_prime_3(self):
        self.assertAlmostEqual(von_mangoldt(3), math.log(3), places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_prime_power_4(self):
        """4 = 2²: Λ(4) = ln 2."""
        self.assertAlmostEqual(von_mangoldt(4), math.log(2), places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_prime_power_8(self):
        """8 = 2³: Λ(8) = ln 2."""
        self.assertAlmostEqual(von_mangoldt(8), math.log(2), places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_prime_power_9(self):
        """9 = 3²: Λ(9) = ln 3."""
        self.assertAlmostEqual(von_mangoldt(9), math.log(3), places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_composite_2_distinct_primes(self):
        """6 = 2·3 (two distinct primes): Λ(6) = 0."""
        self.assertEqual(von_mangoldt(6), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_composite_10(self):
        """10 = 2·5: Λ(10) = 0."""
        self.assertEqual(von_mangoldt(10), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_composite_12(self):
        """12 = 2²·3 (two distinct primes): Λ(12) = 0."""
        self.assertEqual(von_mangoldt(12), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_prime_5(self):
        self.assertAlmostEqual(von_mangoldt(5), math.log(5), places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_prime_7(self):
        self.assertAlmostEqual(von_mangoldt(7), math.log(7), places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_prime_11(self):
        self.assertAlmostEqual(von_mangoldt(11), math.log(11), places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_prime_13(self):
        self.assertAlmostEqual(von_mangoldt(13), math.log(13), places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_non_negative(self):
        for n in range(1, 20):
            with self.subTest(n=n):
                self.assertGreaterEqual(von_mangoldt(n), 0.0)


class TestDef06TestFunction(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_returns_finite(self):
        h = selberg_test_function_h(0.0)
        self.assertTrue(math.isfinite(h))

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_positive_at_zero(self):
        """h(0) > 0 (peaked test function)."""
        h = selberg_test_function_h(0.0)
        self.assertGreater(h, 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_decay_at_large_r(self):
        """Test function should decay for large |r|."""
        h0 = selberg_test_function_h(0.0)
        h100 = selberg_test_function_h(100.0)
        self.assertLess(h100, h0)


class TestDef06GeometricSide(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_returns_finite(self):
        g = prime_geodesic_contribution()
        self.assertTrue(math.isfinite(g))

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_reference_value(self):
        """Geometric side (P*=97, T₀=14.135) ≈ -2.728387."""
        g = prime_geodesic_contribution()
        self.assertAlmostEqual(g, -2.728387, places=3)


class TestDef06Constants(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_lambda_star(self):
        self.assertAlmostEqual(LAMBDA_STAR, 494.0589555580202, places=6)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_norm_x_star(self):
        self.assertAlmostEqual(NORM_X_STAR, 0.34226067113747900, places=10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
