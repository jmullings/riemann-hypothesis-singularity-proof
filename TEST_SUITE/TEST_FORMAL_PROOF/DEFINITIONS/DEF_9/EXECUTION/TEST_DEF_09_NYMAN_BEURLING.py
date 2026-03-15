#!/usr/bin/env python3
"""
TEST_DEF_09_NYMAN_BEURLING.py
==============================
Mirrored unit tests for DEF_09_NYMAN_BEURLING.py

Verifies:
  - rho_fractional(x): fractional part {x}
  - nyman_basis_vector(theta, x_values): list of floats in [0,1]
  - D_X(sigma, T): Dirichlet polynomial
  - E(sigma, T): energy = |D_X|² > 0
  - projected_norm_N_phi(T): N_φ(T) = E(½,T) > 0 at zero heights
  - N_φ reference values at all 9 zeros
  - Framework constants LAMBDA_STAR, NORM_X_STAR

TRINITY PROTOCOL:
  P1: log-free check  ✓
  P2: 9D zero basis  ✓
  P9: DEF_09 convexity test is σ-direction (not T-direction)  ✓
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
    _REPO_ROOT, 'FORMAL_PROOF_NEW', 'DEFINITIONS', 'DEF_9', 'EXECUTION'
)
sys.path.insert(0, _DEF_EXEC)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'FORMAL_PROOF_NEW', 'CONFIGURATIONS'))

try:
    from DEF_09_NYMAN_BEURLING import (
        rho_fractional,
        nyman_basis_vector,
        D_X,
        E,
        projected_norm_N_phi,
        convexity_C_phi,
    )
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR, RIEMANN_ZEROS_9
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    _IMPORT_ERR = str(e)

# Reference N_φ values from DEF_09 runtime output
_N_PHI_REF = {
    14.134725: 6.011633,
    21.022040: 3.448835,
    25.010858: 1.967686,
    30.424876: 3.467582,
    32.935062: 2.881760,
    37.586178: 2.003109,
    40.918719: 3.011545,
    43.327073: 2.581229,
    48.005151: 4.029824,
}


class TestDef09RhoFractional(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_half(self):
        self.assertAlmostEqual(rho_fractional(1.5), 0.5, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_0p7(self):
        self.assertAlmostEqual(rho_fractional(2.7), 0.7, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_pi(self):
        import math as m
        self.assertAlmostEqual(rho_fractional(m.pi), m.pi - 3, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_integer_zero(self):
        """ρ(integer) = 0."""
        self.assertAlmostEqual(rho_fractional(4.0), 0.0, places=12)
        self.assertAlmostEqual(rho_fractional(1.0), 0.0, places=12)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_range_0_to_1(self):
        for x in [1.1, 2.3, 5.7, 100.99]:
            v = rho_fractional(x)
            with self.subTest(x=x):
                self.assertGreaterEqual(v, 0.0)
                self.assertLess(v, 1.0)


class TestDef09NymanBasisVector(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_returns_list(self):
        result = nyman_basis_vector(0.5, [1.0, 2.0, 3.0])
        self.assertIsInstance(result, list)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_length_matches_x_values(self):
        x_values = [1.0, 2.0, 3.0, 4.0]
        result = nyman_basis_vector(0.5, x_values)
        self.assertEqual(len(result), len(x_values))

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_range_0_to_1(self):
        for v in nyman_basis_vector(0.3, [1.0, 1.5, 2.7, 4.0]):
            self.assertGreaterEqual(v, 0.0)
            self.assertLess(v, 1.0 + 1e-10)


class TestDef09DXAndEnergy(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_dx_complex(self):
        self.assertIsInstance(D_X(0.5, 14.134725), complex)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_energy_positive(self):
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                self.assertGreater(E(0.5, T), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_energy_eq_modulus_sq(self):
        T = 14.134725
        self.assertAlmostEqual(E(0.5, T), abs(D_X(0.5, T)) ** 2, places=10)


class TestDef09ProjectedNormNPhi(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_equals_energy(self):
        """N_φ(T) = E(½, T) by definition."""
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                self.assertAlmostEqual(projected_norm_N_phi(T), E(0.5, T), places=10)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_positive(self):
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                self.assertGreater(projected_norm_N_phi(T), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_reference_values(self):
        for T, ref in _N_PHI_REF.items():
            with self.subTest(T=T):
                val = projected_norm_N_phi(T)
                self.assertAlmostEqual(val, ref, places=3,
                                       msg=f"N_φ({T:.3f}) = {val:.6f}, ref = {ref:.6f}")


class TestDef09ConvexityC_phi(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_returns_finite(self):
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                c = convexity_C_phi(T)
                self.assertTrue(math.isfinite(c),
                                msg=f"convexity_C_phi({T:.3f}) not finite")

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_sigma_direction_positive(self):
        """σ-direction convexity at zero heights must be ≥ 0."""
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                c = convexity_C_phi(T)
                self.assertGreaterEqual(c, 0.0,
                                        msg=f"C_φ({T:.3f}) = {c:.6f} < 0")


class TestDef09Constants(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_lambda_star(self):
        self.assertAlmostEqual(LAMBDA_STAR, 494.0589555580202, places=6)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_norm_x_star(self):
        self.assertAlmostEqual(NORM_X_STAR, 0.34226067113747900, places=10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
