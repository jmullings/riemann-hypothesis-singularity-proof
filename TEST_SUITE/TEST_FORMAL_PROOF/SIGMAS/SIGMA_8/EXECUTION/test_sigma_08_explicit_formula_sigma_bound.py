#!/usr/bin/env python3
"""
test_sigma_08_explicit_formula_sigma_bound.py
===============================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/SIGMAS/SIGMA_8/EXECUTION/EQ8_EXPLICIT_FORMULA_SIGMA_BOUND.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads and key symbols are present
    T3 — PrimeExplicitPoly: psi, energy_root, curvature methods
    T4 — |Psi| <= B bound (EQ8.2) and B > 0 (EQ8.1) spot checks
    T5 — All EQ8 proposition runners pass (EQ8.1 – EQ8.7)
"""

from __future__ import annotations

import sys
import math
import unittest
import py_compile
import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT   = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SCRIPT = ROOT / 'FORMAL_PROOF_NEW' / 'SIGMAS' / 'SIGMA_8' / 'EXECUTION' / 'EQ8_EXPLICIT_FORMULA_SIGMA_BOUND.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('EQ8_EXPLICIT_FORMULA_SIGMA_BOUND', SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules['EQ8_EXPLICIT_FORMULA_SIGMA_BOUND'] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestSigma08Syntax(unittest.TestCase):

    def test_script_exists(self):
        """T1: Script file is present."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")

    def test_compiles_without_errors(self):
        """T1: EQ8_EXPLICIT_FORMULA_SIGMA_BOUND.py compiles cleanly."""
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import and symbols
# ---------------------------------------------------------------------------
class TestSigma08Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module loads without ImportError."""
        self.assertIsNotNone(self.mod)

    def test_key_classes_present(self):
        """T2: PrimeExplicitPoly class exported."""
        self.assertTrue(hasattr(self.mod, 'PrimeExplicitPoly'), "Missing: PrimeExplicitPoly")

    def test_key_functions_present(self):
        """T2: All prove_eq8_N functions plus PROOFS list exported."""
        for name in ('prove_eq8_1', 'prove_eq8_2', 'prove_eq8_3',
                     'prove_eq8_4', 'prove_eq8_5', 'prove_eq8_6',
                     'prove_eq8_7', 'prove_eq8_A', 'prove_eq8_B', 'PROOFS'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")


# ---------------------------------------------------------------------------
# T3 — PrimeExplicitPoly methods
# ---------------------------------------------------------------------------
class TestSigma08PrimeExplicitPoly(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        cls.pe  = cls.mod.PrimeExplicitPoly(pa)

    def test_energy_nonneg(self):
        """T3: energy(sigma, T) = |D|^2 >= 0."""
        self.assertGreaterEqual(self.pe.energy(0.5, 14.134), 0.0)

    def test_energy_root_positive(self):
        """T3: energy_root(sigma, T) = sqrt(E) > 0."""
        b = self.pe.energy_root(0.5, 14.134)
        self.assertGreater(b, 0.0, f"energy_root = {b}")

    def test_psi_bounded_by_energy_root(self):
        """T3: |Psi| <= B from |Re(D)| <= |D| (EQ8.2)."""
        for sigma in [0.3, 0.5, 0.7]:
            for T in [10.0, 14.134, 50.0]:
                psi = abs(self.pe.psi(sigma, T))
                b   = self.pe.energy_root(sigma, T)
                self.assertLessEqual(psi, b + 1e-12,
                                     f"|Psi|={psi} > B={b} at sigma={sigma}, T={T}")

    def test_curvature_nonneg(self):
        """T3: C0(sigma, T) = second finite diff of E >= 0."""
        c = self.pe.curvature(0.5, 14.134)
        self.assertGreaterEqual(c, 0.0, f"curvature = {c}")


# ---------------------------------------------------------------------------
# T4 — Monotone sigma behaviour
# ---------------------------------------------------------------------------
class TestSigma08MonotoneSigma(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        cls.pe  = cls.mod.PrimeExplicitPoly(pa)

    def test_energy_root_decreasing_in_sigma(self):
        """T4: B(0.3, T) > B(0.5, T) > B(0.7, T) at T=14.134."""
        T = 14.134
        b30 = self.pe.energy_root(0.3, T)
        b50 = self.pe.energy_root(0.5, T)
        b70 = self.pe.energy_root(0.7, T)
        self.assertGreater(b30, b50, f"B(0.3) <= B(0.5): {b30} <= {b50}")
        self.assertGreater(b50, b70, f"B(0.5) <= B(0.7): {b50} <= {b70}")


# ---------------------------------------------------------------------------
# T5 — All EQ8 proposition runners
# ---------------------------------------------------------------------------
class TestSigma08PropositionRunners(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_eq8_1_b_positive(self):
        """T5: EQ8.1 — B(sigma, T) > 0 at all test points."""
        passed, total = self.mod.prove_eq8_1()
        self.assertEqual(passed, total, f"EQ8.1: {passed}/{total}")

    def test_eq8_2_psi_bounded(self):
        """T5: EQ8.2 — |Psi| <= B at all test points."""
        passed, total = self.mod.prove_eq8_2()
        self.assertEqual(passed, total, f"EQ8.2: {passed}/{total}")

    def test_eq8_3_b_strictly_decreasing(self):
        """T5: EQ8.3 — B strictly decreasing in sigma on T_MAIN grid."""
        passed, total = self.mod.prove_eq8_3()
        self.assertEqual(passed, total, f"EQ8.3: {passed}/{total}")

    def test_eq8_4_c0_positive(self):
        """T5: EQ8.4 — C0(sigma, T) > 0 (convexity) at all test points."""
        passed, total = self.mod.prove_eq8_4()
        self.assertEqual(passed, total, f"EQ8.4: {passed}/{total}")

    def test_eq8_5_half_vs_06_at_zeros(self):
        """T5: EQ8.5 — E(0.5, T) > E(0.6, T) at first 5 Riemann zeros."""
        passed, total = self.mod.prove_eq8_5()
        self.assertEqual(passed, total, f"EQ8.5: {passed}/{total}")

    def test_eq8_6_off_critical_direction(self):
        """T5: EQ8.6 — Off-critical energy direction consistent."""
        passed, total = self.mod.prove_eq8_6()
        self.assertEqual(passed, total, f"EQ8.6: {passed}/{total}")

    def test_eq8_7_riemann_zero_bound(self):
        """T5: EQ8.7 — |Psi(0.5,T)| <= B(0.5,T) at 8 Riemann zeros."""
        passed, total = self.mod.prove_eq8_7()
        self.assertEqual(passed, total, f"EQ8.7: {passed}/{total}")

    def test_proofs_list_complete(self):
        """T5: PROOFS list contains all 9 proposition entries (7 numeric + 2 analytic Layer A)."""
        self.assertEqual(len(self.mod.PROOFS), 9)

    def test_eq8_A_diagonal_monotonicity(self):
        """T5: prove_eq8_A — dE_diag/dsigma < 0 analytically proved."""
        passed, total = self.mod.prove_eq8_A()
        self.assertGreater(total, 0)
        self.assertEqual(passed, total, f"EQ8.A diagonal: {passed}/{total}")

    def test_eq8_B_t_average_monotonicity(self):
        """T5: prove_eq8_B — T-average dE/dsigma < 0 by Weyl."""
        passed, total = self.mod.prove_eq8_B()
        self.assertGreater(total, 0)
        self.assertEqual(passed, total, f"EQ8.B T-avg: {passed}/{total}")


if __name__ == '__main__':
    unittest.main()
