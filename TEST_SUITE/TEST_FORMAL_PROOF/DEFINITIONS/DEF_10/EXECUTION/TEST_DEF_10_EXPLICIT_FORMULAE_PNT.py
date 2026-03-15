#!/usr/bin/env python3
"""
TEST_DEF_10_EXPLICIT_FORMULAE_PNT.py
=====================================
Mirrored unit tests for DEF_10_EXPLICIT_FORMULAE_PNT.py

Verifies:
  - von_mangoldt_psi_X(sigma, T): weighted Ψ_X, returns complex
  - D_X(sigma, T): Dirichlet polynomial
  - E(sigma, T): energy functional
  - N_T_formula(T): Riemann-von Mangoldt counting function
  - explicit_formula_sigma_bound(T, C): σ-upper bound > ½
  - σ-bounds at all 9 zeros match reference output
  - σ-bound > ½ for every zero (σ-selectivity)
  - Framework constants LAMBDA_STAR, NORM_X_STAR

TRINITY PROTOCOL:
  P1: log() used only in N_T_formula and sigma_bound (reference implementations)
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
    _REPO_ROOT, 'FORMAL_PROOF_NEW', 'DEFINITIONS', 'DEF_10', 'EXECUTION'
)
sys.path.insert(0, _DEF_EXEC)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'FORMAL_PROOF_NEW', 'CONFIGURATIONS'))

try:
    from DEF_10_EXPLICIT_FORMULAE_PNT import (
        von_mangoldt_psi_X,
        D_X,
        E,
        N_T_formula,
        explicit_formula_sigma_bound,
    )
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR, RIEMANN_ZEROS_9
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    _IMPORT_ERR = str(e)

# Reference σ-bounds from DEF_10 runtime output
_SIGMA_BOUND_REF = {
    14.134725: 0.877553,
    21.022040: 0.828346,
    25.010858: 0.810626,
    30.424876: 0.792803,
    32.935062: 0.786161,
    37.586178: 0.775738,
    40.918719: 0.769426,
}


class TestDef10VonMangoldtPsiX(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_returns_complex(self):
        result = von_mangoldt_psi_X(0.5, 14.134725)
        self.assertIsInstance(result, complex)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_finite(self):
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                r = von_mangoldt_psi_X(0.5, T)
                self.assertTrue(math.isfinite(abs(r)))

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_magnitude_first_zero(self):
        """Reference: |Ψ_X(½+14.135i)| ≈ 3.901 (von Mangoldt augmented)."""
        r = von_mangoldt_psi_X(0.5, 14.134725)
        self.assertAlmostEqual(abs(r), 3.90114, places=3)


class TestDef10DXAndEnergy(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_dx_complex(self):
        self.assertIsInstance(D_X(0.5, 14.134725), complex)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_magnitude_first_zero(self):
        """Reference: |D_X(½+14.135i)| ≈ 2.45186."""
        r = D_X(0.5, 14.134725)
        self.assertAlmostEqual(abs(r), 2.45186, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_energy_positive(self):
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                self.assertGreater(E(0.5, T), 0.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_energy_eq_modulus_sq(self):
        T = 14.134725
        self.assertAlmostEqual(E(0.5, T), abs(D_X(0.5, T)) ** 2, places=10)


class TestDef10NTFormula(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_first_zero(self):
        """N(14.134725) ≈ 0.4493 (Riemann–von Mangoldt)."""
        self.assertAlmostEqual(N_T_formula(14.134725), 0.4493, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_second_zero(self):
        self.assertAlmostEqual(N_T_formula(21.022040), 1.5699, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_at_third_zero(self):
        self.assertAlmostEqual(N_T_formula(25.010858), 2.3933, places=3)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_monotone_increasing(self):
        vals = [N_T_formula(T) for T in sorted(RIEMANN_ZEROS_9)]
        for a, b in zip(vals, vals[1:]):
            self.assertLessEqual(a, b)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_positive_for_large_T(self):
        self.assertGreater(N_T_formula(100.0), 0.0)


class TestDef10SigmaBound(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_above_half(self):
        """EQ8 σ-bound must be strictly > ½ for all zero heights."""
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                bound = explicit_formula_sigma_bound(T)
                self.assertGreater(bound, 0.5,
                                   msg=f"σ_bound({T:.3f}) = {bound:.6f} ≤ 0.5")

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_below_one(self):
        """σ-bound should be < 1 for small T."""
        for T in RIEMANN_ZEROS_9:
            with self.subTest(T=T):
                self.assertLess(explicit_formula_sigma_bound(T), 1.0)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_decreasing_in_T(self):
        """σ-bound = ½ + 1/log(T) decreases as T increases."""
        bounds = [explicit_formula_sigma_bound(T) for T in sorted(RIEMANN_ZEROS_9)]
        for a, b in zip(bounds, bounds[1:]):
            self.assertGreater(a, b)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_reference_values(self):
        for T, ref in _SIGMA_BOUND_REF.items():
            with self.subTest(T=T):
                val = explicit_formula_sigma_bound(T)
                self.assertAlmostEqual(val, ref, places=5,
                                       msg=f"σ_bound({T:.3f}) = {val:.6f}, ref = {ref:.6f}")

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_half_formula(self):
        """σ_bound(T) = ½ + C/log(T) with C=1."""
        for T in RIEMANN_ZEROS_9:
            expected = 0.5 + 1.0 / math.log(T)
            with self.subTest(T=T):
                self.assertAlmostEqual(
                    explicit_formula_sigma_bound(T, C=1.0), expected, places=12
                )


class TestDef10Constants(unittest.TestCase):

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_lambda_star(self):
        self.assertAlmostEqual(LAMBDA_STAR, 494.0589555580202, places=6)

    @unittest.skipUnless(IMPORT_OK, "import failed")
    def test_norm_x_star(self):
        self.assertAlmostEqual(NORM_X_STAR, 0.34226067113747900, places=10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
