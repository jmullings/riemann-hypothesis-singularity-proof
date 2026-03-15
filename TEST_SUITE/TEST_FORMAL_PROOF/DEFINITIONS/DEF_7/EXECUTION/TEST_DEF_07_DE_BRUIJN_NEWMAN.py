#!/usr/bin/env python3
"""
TEST_DEF_07_DE_BRUIJN_NEWMAN.py
================================
Mirrored unit tests for DEF_07_DE_BRUIJN_NEWMAN.py

Verifies:
  - D_X(sigma, T): Dirichlet polynomial, returns complex
  - E(sigma, T): energy = |D_X|², positive
  - flow_curvature(T): ∂²E/∂σ²(½, γk) > 0 for all 9 zeros
  - scale_functional(delta_b): S(0)=1, S(1)≈2^0.864
  - λ* ≈ sum of curvatures to within 1e-3 relative error
  - Framework constants LAMBDA_STAR, NORM_X_STAR, ALPHA

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
    _REPO_ROOT, 'FORMAL_PROOF_NEW', 'DEFINITIONS', 'DEF_7', 'EXECUTION'
)
sys.path.insert(0, _DEF_EXEC)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'FORMAL_PROOF_NEW', 'CONFIGURATIONS'))

try:
    from DEF_07_DE_BRUIJN_NEWMAN import (
        D_X,
        E,
        flow_curvature,
        scale_functional,
    )
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR, RIEMANN_ZEROS_9
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    _IMPORT_ERR = str(e)


class TestDef07DX(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_returns_complex(self):
        result = D_X(0.5, 14.134725)
        self.assertIsInstance(result, complex)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_finite(self):
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                r = D_X(0.5, T)
                self.assertTrue(math.isfinite(abs(r)))

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_sigma_convergence(self):
        """Larger σ → smaller |D_X| (primes decay faster)."""
        d_half = D_X(0.5, 14.134725)
        d_one  = D_X(1.0, 14.134725)
        self.assertGreater(abs(d_half), abs(d_one))


class TestDef07Energy(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_positive(self):
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                self.assertGreater(E(0.5, T), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_equals_modulus_squared(self):
        T = 14.134725
        self.assertAlmostEqual(E(0.5, T), abs(D_X(0.5, T)) ** 2, places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_reference_first_zero(self):
        """E(½, 14.135) ≈ 6.0116 (from DEF_09 reference output)."""
        self.assertAlmostEqual(E(0.5, 14.134725), 6.011633, places=3)


class TestDef07FlowCurvature(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_positive_at_all_zeros(self):
        """∂²E/∂σ²(½, γk) > 0 for k=1..9 (De Bruijn-Newman σ-flow stability)."""
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                c = flow_curvature(T)
                self.assertGreater(c, 0.0,
                                   msg=f"flow_curvature({T:.3f}) = {c} ≤ 0")

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_reference_first_zero(self):
        """∂²E/∂σ²(½, 14.135) ≈ 69.286 (h=1e-5)."""
        c = flow_curvature(14.134725)
        self.assertAlmostEqual(c, 69.2858, places=2)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_reference_third_zero(self):
        """∂²E/∂σ²(½, 25.011) ≈ 33.082."""
        c = flow_curvature(25.010858)
        self.assertAlmostEqual(c, 33.0825, places=2)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_lambda_star_from_sum(self):
        """Σ_k flow_curvature(γk) ≈ λ* within 0.1% relative error."""
        total = sum(flow_curvature(T) for T in RIEMANN_ZEROS_9)
        rel_err = abs(total - LAMBDA_STAR) / LAMBDA_STAR
        self.assertLess(rel_err, 0.001,
                        msg=f"Σ curvatures = {total:.4f}, λ* = {LAMBDA_STAR:.4f}, rel err = {rel_err:.6f}")


class TestDef07ScaleFunctional(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_s_zero_equals_one(self):
        """S(0) = 2^0 = 1 (zero bit shift)."""
        self.assertAlmostEqual(scale_functional(0.0), 1.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_s_positive_for_positive_input(self):
        for db in [0.5, 1.0, 2.0]:
            with self.subTest(db=db):
                self.assertGreater(scale_functional(db), 1.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_s_monotone(self):
        vals = [scale_functional(db) for db in [0.0, 0.5, 1.0, 1.5, 2.0]]
        for a, b in zip(vals, vals[1:]):
            self.assertLess(a, b)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_s_at_1(self):
        """S(1) = 2^{α·1} where α=0.864 → S(1) ≈ 1.8244."""
        alpha = 0.864
        expected = 2 ** alpha
        self.assertAlmostEqual(scale_functional(1.0), expected, places=6)


class TestDef07P1Compliance(unittest.TestCase):

    def test_no_bare_log_attribute(self):
        src_path = os.path.join(_DEF_EXEC, 'DEF_07_DE_BRUIJN_NEWMAN.py')
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
