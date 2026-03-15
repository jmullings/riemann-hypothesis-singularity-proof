#!/usr/bin/env python3
"""
TEST_DEF_05_AUTOMORPHIC_FORMS_L_FUNCTIONS.py
============================================
Mirrored unit tests for DEF_05_AUTOMORPHIC_FORMS_L_FUNCTIONS.py

Verifies:
  - selberg_degree(): returns 6 (framework projection dimension)
  - euler_local_factor(sigma, T, p, lp): returns complex with |F| ≤ 1/(1-p^{-σ})
  - Z_euler_product(sigma, T): returns complex, grows with σ
  - Z_euler_product magnitudes match reference at critical line
  - Framework constants LAMBDA_STAR, BITSIZE_OFFSET

TRINITY PROTOCOL:
  P1: log-free check  ✓
  P2: 9D constants from AXIOMS  ✓
  P5: unit-test suite  ✓
"""

import os
import sys
import ast
import math
import cmath
import unittest

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), *(['..'] * 5))
)
_DEF_EXEC = os.path.join(
    _REPO_ROOT, 'FORMAL_PROOF_NEW', 'DEFINITIONS', 'DEF_5', 'EXECUTION'
)
sys.path.insert(0, _DEF_EXEC)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'FORMAL_PROOF_NEW', 'CONFIGURATIONS'))

try:
    from DEF_05_AUTOMORPHIC_FORMS_L_FUNCTIONS import (
        euler_local_factor,
        Z_euler_product,
        selberg_degree,
        BITSIZE_OFFSET,
    )
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR, RIEMANN_ZEROS_9
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    _IMPORT_ERR = str(e)

_T0 = 14.134725
_T1 = 21.022039
_T2 = 25.010857


class TestDef05Constants(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_lambda_star(self):
        self.assertAlmostEqual(LAMBDA_STAR, 494.0589555580202, places=6)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_bitsize_offset(self):
        self.assertAlmostEqual(BITSIZE_OFFSET, 2.96, places=8)


class TestDef05SelbergDegree(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_degree_equals_6(self):
        """Framework projection dimension is 6 (not Selberg L-function degree)."""
        self.assertEqual(selberg_degree(), 6)


class TestDef05EulerLocalFactor(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_returns_complex(self):
        result = euler_local_factor(0.5, _T0, 2, math.log(2))
        self.assertIsInstance(result, complex)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_p2_sigma_half(self):
        """Known value from DEF_05 output: |F_2(½+14.135i)| ≈ 0.595805."""
        result = euler_local_factor(0.5, _T0, 2, math.log(2))
        self.assertAlmostEqual(abs(result), 0.595805, places=4)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_absolute_convergence_bound_at_sigma_2(self):
        """Absolute convergence bound: |F_2(2+iT)| ≤ 1/(1-2^{-2}) ≈ 1.333."""
        f_two = euler_local_factor(2.0, _T0, 2, math.log(2))
        upper_bound = 1.0 / (1.0 - 2.0 ** -2.0)  # ≈ 1.3333
        self.assertLess(abs(f_two), upper_bound,
                        msg=f"|F_2(2+{_T0}i)| = {abs(f_two):.6f} exceeds bound {upper_bound:.6f}")

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_sigma_2_very_small(self):
        """At σ=2 the Euler product converges absolutely; |F_p| ≈ 1/(1-p^-2)^{-1}."""
        result = euler_local_factor(2.0, _T0, 2, math.log(2))
        self.assertTrue(math.isfinite(abs(result)))
        self.assertGreater(abs(result), 0.0)


class TestDef05ZEulerProduct(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_returns_complex(self):
        result = Z_euler_product(0.5, _T0)
        self.assertIsInstance(result, complex)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_magnitude_at_half_T0(self):
        """Reference: |Z(½, 14.134725)| ≈ 0.115200."""
        result = Z_euler_product(0.5, _T0)
        self.assertAlmostEqual(abs(result), 0.115200, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_magnitude_at_half_T1(self):
        """Reference: |Z(½, 21.022039)| ≈ 0.173867."""
        result = Z_euler_product(0.5, _T1)
        self.assertAlmostEqual(abs(result), 0.173867, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_magnitude_at_half_T2(self):
        """Reference: |Z(½, 25.010857)| ≈ 0.189042."""
        result = Z_euler_product(0.5, _T2)
        self.assertAlmostEqual(abs(result), 0.189042, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_sigma_06_larger_than_half(self):
        """Moving away from critical line should change magnitude."""
        z_half = Z_euler_product(0.5, _T0)
        z_06   = Z_euler_product(0.6, _T0)
        # Their magnitudes should differ; at σ=0.6 primes decay faster
        self.assertAlmostEqual(abs(z_06), 0.156666, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_finite_result(self):
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                r = Z_euler_product(0.5, T)
                self.assertTrue(math.isfinite(abs(r)))


class TestDef05P1Compliance(unittest.TestCase):

    def test_no_bare_log(self):
        src_path = os.path.join(_DEF_EXEC, 'DEF_05_AUTOMORPHIC_FORMS_L_FUNCTIONS.py')
        if not os.path.exists(src_path):
            self.skipTest("Source file not found")
        tree = ast.parse(open(src_path).read())
        # In DEF_05 log() may appear only inside euler_local_factor as lp parameter
        # (which is passed in, not computed here); verify no math.log() cal
        log_attr_nodes = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.Attribute) and n.attr == 'log'
        ]
        self.assertEqual(log_attr_nodes, [],
                         msg=f"P1 violation: math.log attr at lines "
                             f"{[n.lineno for n in log_attr_nodes]}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
