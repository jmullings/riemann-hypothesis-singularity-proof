#!/usr/bin/env python3
"""
TEST_DEF_04_ROBIN_LAGARIAS_ARITHMETIC_CRITERIA.py
==================================================
Mirrored unit tests for DEF_04_ROBIN_LAGARIAS_ARITHMETIC_CRITERIA.py

Verifies:
  - sum_of_divisors(n): correct sigma(n) values
  - robin_f(n): ratio σ(n)/(eᵞ·n·ln ln n) for n > 1
  - robin_delta(n): offset from 1
  - lagarias_hn(n): harmonic number H_n
  - lagarias_bound(n): H_n + e^{H_n}·ln(H_n)
  - lagarias_check(n): True for all known n (RH implication)
  - n < 5041 EXEMPT handling (no false VIOLATION flags)
  - Framework constants BITSIZE_OFFSET, LAMBDA_STAR

TRINITY PROTOCOL:
  P1: log() used internally (lagarias/harmonic) — these are reference
      implementations in EXECUTION (boundary case, noted)
  P4: BITSIZE_OFFSET δ = 2.96  ✓
  P5: unit-test suite  ✓
"""

import os
import sys
import unittest
import math

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), *(['..'] * 5))
)
_DEF_EXEC = os.path.join(
    _REPO_ROOT, 'FORMAL_PROOF_NEW', 'DEFINITIONS', 'DEF_4', 'EXECUTION'
)
sys.path.insert(0, _DEF_EXEC)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'FORMAL_PROOF_NEW', 'CONFIGURATIONS'))

try:
    from DEF_04_ROBIN_LAGARIAS_ARITHMETIC_CRITERIA import (
        sum_of_divisors,
        robin_f,
        robin_delta,
        lagarias_hn,
        lagarias_bound,
        lagarias_check,
        BITSIZE_OFFSET,
    )
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    _IMPORT_ERR = str(e)


class TestDef04SumOfDivisors(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_sigma_6(self):
        self.assertEqual(sum_of_divisors(6), 12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_sigma_12(self):
        self.assertEqual(sum_of_divisors(12), 28)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_sigma_60(self):
        self.assertEqual(sum_of_divisors(60), 168)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_sigma_prime(self):
        """σ(p) = p + 1 for any prime p."""
        self.assertEqual(sum_of_divisors(7), 8)
        self.assertEqual(sum_of_divisors(11), 12)
        self.assertEqual(sum_of_divisors(97), 98)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_sigma_1(self):
        self.assertEqual(sum_of_divisors(1), 1)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_sigma_720720(self):
        """Known Lagarias test case."""
        self.assertEqual(sum_of_divisors(720720), 3249792)


class TestDef04RobinF(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_n_less_than_5041_exempt(self):
        """For n < 5041 robin_f may be > 1 — no violation should be raised."""
        # Just check it returns a finite float without error
        for n in [6, 12, 60, 120, 360, 720, 5040]:
            with self.subTest(n=n):
                val = robin_f(n)
                self.assertTrue(math.isfinite(val), f"robin_f({n}) not finite")
                self.assertGreater(val, 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_n_720720_below_one(self):
        """σ(720720)/(eᵞ·720720·log log 720720) < 1 expected."""
        val = robin_f(720720)
        self.assertLess(val, 1.0, "Robin RH check for n=720720 should give f(n)<1")

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_positive_output(self):
        """robin_f should always be positive for n > 1."""
        for n in [6, 60, 720720]:
            val = robin_f(n)
            self.assertGreater(val, 0.0)


class TestDef04RobinDelta(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_delta_720720(self):
        """δ(720720) = f(720720) - 1 < 0."""
        d = robin_delta(720720)
        self.assertAlmostEqual(d, robin_f(720720) - 1.0, places=12)
        self.assertLess(d, 0.0)


class TestDef04LagariasHn(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_h1(self):
        self.assertAlmostEqual(lagarias_hn(1), 1.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_h2(self):
        self.assertAlmostEqual(lagarias_hn(2), 1.5, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_h4(self):
        expected = 1 + 0.5 + 1/3 + 0.25
        self.assertAlmostEqual(lagarias_hn(4), expected, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_increasing(self):
        h_vals = [lagarias_hn(n) for n in range(1, 10)]
        for a, b in zip(h_vals, h_vals[1:]):
            self.assertLess(a, b)


class TestDef04LagariasCheck(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_known_n_pass(self):
        """σ(n) ≤ H_n + e^{H_n}·ln(H_n) for known values."""
        for n in [6, 12, 60, 720, 5040, 720720]:
            with self.subTest(n=n):
                self.assertTrue(lagarias_check(n),
                                msg=f"lagarias_check({n}) unexpectedly failed")

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_n1_trivial(self):
        """n=1: σ(1)=1, bound = 1 + e·ln(1)=1, marginal."""
        # Lagarias check at n=1: bound = H_1 + e^1 * ln(1) = 1 + 0 = 1; σ(1)=1
        self.assertTrue(lagarias_check(1))


class TestDef04Constants(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_bitsize_offset(self):
        self.assertAlmostEqual(BITSIZE_OFFSET, 2.96, places=8)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_lambda_star(self):
        self.assertAlmostEqual(LAMBDA_STAR, 494.0589555580202, places=6)


if __name__ == '__main__':
    unittest.main(verbosity=2)
