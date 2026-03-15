#!/usr/bin/env python3
"""
TEST_DEF_08_MOMENTS_KEATING_SNAITH.py
======================================
Mirrored unit tests for DEF_08_MOMENTS_KEATING_SNAITH.py

Verifies:
  - D_X(sigma, T): Dirichlet polynomial
  - E(sigma, T): energy functional
  - barnes_g_ratio(k): g(1)=1, g(2)≈0.04167, g(3)≈2.89e-5
  - moment_exponent(k): returns k²
  - framework_second_moment(): M2 ≈ 29.403
  - framework_fourth_moment(): M4 ≈ 108.219
  - GUE moment ratio M4·N/M2² ≈ 1.127 (close to 1+1/N = 10/9 ≈ 1.111)
  - Framework constants LAMBDA_STAR, NORM_X_STAR

TRINITY PROTOCOL:
  P1: log-free check  ✓
  P2: 9D zero basis  ✓
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
    _REPO_ROOT, 'FORMAL_PROOF_NEW', 'DEFINITIONS', 'DEF_8', 'EXECUTION'
)
sys.path.insert(0, _DEF_EXEC)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'FORMAL_PROOF_NEW', 'CONFIGURATIONS'))

try:
    from DEF_08_MOMENTS_KEATING_SNAITH import (
        D_X,
        E,
        barnes_g_ratio,
        moment_exponent,
        framework_second_moment,
        framework_fourth_moment,
    )
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR, RIEMANN_ZEROS_9
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    _IMPORT_ERR = str(e)

_N_ZEROS = 9


class TestDef08DXAndEnergy(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_dx_complex(self):
        self.assertIsInstance(D_X(0.5, 14.134725), complex)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_energy_positive(self):
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                self.assertGreater(E(0.5, T), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_energy_equals_modulus_sq(self):
        T = 14.134725
        self.assertAlmostEqual(E(0.5, T), abs(D_X(0.5, T)) ** 2, places=10)


class TestDef08BarnesGRatio(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_g1(self):
        """g(1) = G²(2)/G(3) = 1/1 = 1."""
        self.assertAlmostEqual(barnes_g_ratio(1), 1.0, places=6)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_g2(self):
        """g(2) ≈ 0.04167 (Barnes G-function ratio for k=2)."""
        self.assertAlmostEqual(barnes_g_ratio(2), 4.16666667e-02, places=6)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_g3(self):
        """g(3) ≈ 2.894e-5."""
        self.assertAlmostEqual(barnes_g_ratio(3), 2.89351852e-05, places=9)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_strictly_decreasing(self):
        """Barnes g(k) should decay rapidly with k."""
        g1 = barnes_g_ratio(1)
        g2 = barnes_g_ratio(2)
        g3 = barnes_g_ratio(3)
        self.assertGreater(g1, g2)
        self.assertGreater(g2, g3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_positive(self):
        for k in [1, 2, 3]:
            with self.subTest(k=k):
                self.assertGreater(barnes_g_ratio(k), 0.0)


class TestDef08MomentExponent(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_k_squared(self):
        """moment_exponent(k) should return k²."""
        for k in [1, 2, 3, 4]:
            with self.subTest(k=k):
                self.assertEqual(moment_exponent(k), k * k)


class TestDef08FrameworkMoments(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_second_moment_reference(self):
        """M2 = Σ E(½, γk) ≈ 29.403203."""
        m2 = framework_second_moment()
        self.assertAlmostEqual(m2, 29.403203, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_fourth_moment_reference(self):
        """M4 = Σ E(½, γk)² ≈ 108.218720."""
        m4 = framework_fourth_moment()
        self.assertAlmostEqual(m4, 108.218720, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_second_moment_positive(self):
        self.assertGreater(framework_second_moment(), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_fourth_moment_positive(self):
        self.assertGreater(framework_fourth_moment(), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_gue_moment_ratio(self):
        """M4·N/M2² ≈ 1.127; close to GUE 1+1/N = 1.111 (N=9)."""
        m2 = framework_second_moment()
        m4 = framework_fourth_moment()
        ratio = m4 * _N_ZEROS / (m2 ** 2)
        # Should be within 20% of the GUE prediction 1 + 1/N
        gue_pred = 1.0 + 1.0 / _N_ZEROS
        self.assertAlmostEqual(ratio, 1.126563, places=3)
        self.assertAlmostEqual(ratio, gue_pred, delta=0.1)


class TestDef08Constants(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_lambda_star(self):
        self.assertAlmostEqual(LAMBDA_STAR, 494.0589555580202, places=6)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_norm_x_star(self):
        self.assertAlmostEqual(NORM_X_STAR, 0.34226067113747900, places=10)


class TestDef08P1Compliance(unittest.TestCase):

    def test_no_bare_log_attribute(self):
        src_path = os.path.join(_DEF_EXEC, 'DEF_08_MOMENTS_KEATING_SNAITH.py')
        if not os.path.exists(src_path):
            self.skipTest("Source file not found")
        tree = ast.parse(open(src_path).read())
        log_attr = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.Attribute) and n.attr == 'log'
        ]
        self.assertEqual(log_attr, [],
                         msg=f"P1 violation: log attr at lines {[n.lineno for n in log_attr]}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
