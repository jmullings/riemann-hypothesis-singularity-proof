#!/usr/bin/env python3
"""
test_sigma_10_finite_euler_product_filter.py
==============================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/SIGMAS/SIGMA_10/EXECUTION/EQ10_FINITE_EULER_PRODUCT_FILTER.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads and key symbols are present
    T3 — PrimeEulerEngine: R_p, R_p_lower, R_p_upper, log_euler
    T4 — Triangle inequality bounds and T-bound semantics
    T5 — All EQ10 proposition runners pass (EQ10.1 – EQ10.7)
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
SCRIPT = ROOT / 'FORMAL_PROOF_NEW' / 'SIGMAS' / 'SIGMA_10' / 'EXECUTION' / 'EQ10_FINITE_EULER_PRODUCT_FILTER.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('EQ10_FINITE_EULER_PRODUCT_FILTER', SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules['EQ10_FINITE_EULER_PRODUCT_FILTER'] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestSigma10Syntax(unittest.TestCase):

    def test_script_exists(self):
        """T1: Script file is present."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")

    def test_compiles_without_errors(self):
        """T1: EQ10_FINITE_EULER_PRODUCT_FILTER.py compiles cleanly."""
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import and symbols
# ---------------------------------------------------------------------------
class TestSigma10Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module loads without ImportError."""
        self.assertIsNotNone(self.mod)

    def test_key_classes_present(self):
        """T2: PrimeEulerEngine exported."""
        self.assertTrue(hasattr(self.mod, 'PrimeEulerEngine'), "Missing: PrimeEulerEngine")

    def test_key_functions_present(self):
        """T2: All prove_eq10_N functions and PROOFS list exported."""
        for name in ('prove_eq10_1', 'prove_eq10_2', 'prove_eq10_3',
                     'prove_eq10_4', 'prove_eq10_5', 'prove_eq10_6',
                     'prove_eq10_7', 'prove_eq10_A',
                     'AnalyticLogZDerivativeEngine', 'PROOFS'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")


# ---------------------------------------------------------------------------
# T3 — PrimeEulerEngine methods
# ---------------------------------------------------------------------------
class TestSigma10EulerEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        cls.ee  = cls.mod.PrimeEulerEngine(pa)
        cls.EPS = 1e-12

    def test_R_p_positive(self):
        """T3: R_p(p, sigma, T) > 0 for p=2, sigma=0.5, T=14.134."""
        Rp = self.ee.R_p(2, 0.5, 14.134)
        self.assertGreater(Rp, self.EPS, f"R_p = {Rp}")

    def test_R_p_lower_positive(self):
        """T3: (1 - p^{-sigma})^2 > 0 for p=2, sigma=0.5."""
        lb = self.ee.R_p_lower(2, 0.5)
        self.assertGreater(lb, self.EPS, f"R_p_lower = {lb}")

    def test_R_p_upper_greater_than_lower(self):
        """T3: (1+p^{-s})^2 >= R_p >= (1-p^{-s})^2 (sandwich bounds)."""
        for p in [2, 3, 5]:
            for T in [10.0, 14.134, 50.0]:
                Rp = self.ee.R_p(p, 0.5, T)
                lb = self.ee.R_p_lower(p, 0.5)
                ub = self.ee.R_p_upper(p, 0.5)
                self.assertGreaterEqual(Rp, lb - self.EPS,
                                        f"R_p({p}) < lower bound at T={T}")
                self.assertLessEqual(Rp, ub + self.EPS,
                                     f"R_p({p}) > upper bound at T={T}")

    def test_log_euler_T_bound(self):
        """T3: log Z(sigma, T) <= log Z(sigma, 0) for all T (EQ10.4)."""
        for sigma in [0.3, 0.5, 0.7]:
            z0 = self.ee.log_euler_at_zero(sigma)
            for T in [10.0, 14.134, 50.0]:
                zt = self.ee.log_euler(sigma, T)
                self.assertLessEqual(zt, z0 + self.EPS,
                                     f"log Z(sigma={sigma}, T={T}) > log Z(sigma,0)")

    def test_curvature_nonneg(self):
        """T3: C0(sigma=0.5, T) >= 0 for T in [10, 14.134, 50]."""
        for T in [10.0, 14.134, 50.0]:
            c = self.ee.curvature(0.5, T)
            self.assertGreaterEqual(c, 0.0, f"curvature < 0 at T={T}: {c}")


# ---------------------------------------------------------------------------
# T4 — log Z strictly decreasing in sigma
# ---------------------------------------------------------------------------
class TestSigma10LogEulerMonotone(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        cls.ee  = cls.mod.PrimeEulerEngine(pa)

    def test_log_euler_at_zero_decreasing(self):
        """T4: log Z(0.3, 0) > log Z(0.5, 0) > log Z(0.7, 0) (EQ10.5)."""
        z30 = self.ee.log_euler_at_zero(0.3)
        z50 = self.ee.log_euler_at_zero(0.5)
        z70 = self.ee.log_euler_at_zero(0.7)
        self.assertGreater(z30, z50, f"log Z(0.3) <= log Z(0.5)")
        self.assertGreater(z50, z70, f"log Z(0.5) <= log Z(0.7)")


# ---------------------------------------------------------------------------
# T5 — All EQ10 proposition runners
# ---------------------------------------------------------------------------
class TestSigma10PropositionRunners(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_eq10_1_lower_bound_positive(self):
        """T5: EQ10.1 — (1-p^{-sigma})^2 > 0 for all probe primes."""
        passed, total = self.mod.prove_eq10_1()
        self.assertEqual(passed, total, f"EQ10.1: {passed}/{total}")

    def test_eq10_2_rp_lower_bound(self):
        """T5: EQ10.2 — R_p >= (1-p^{-sigma})^2 (reverse triangle ineq)."""
        passed, total = self.mod.prove_eq10_2()
        self.assertEqual(passed, total, f"EQ10.2: {passed}/{total}")

    def test_eq10_3_rp_upper_bound(self):
        """T5: EQ10.3 — R_p <= (1+p^{-sigma})^2 (triangle inequality)."""
        passed, total = self.mod.prove_eq10_3()
        self.assertEqual(passed, total, f"EQ10.3: {passed}/{total}")

    def test_eq10_4_T_bound(self):
        """T5: EQ10.4 — log Z(sigma,T) <= log Z(sigma,0) for all T."""
        passed, total = self.mod.prove_eq10_4()
        self.assertEqual(passed, total, f"EQ10.4: {passed}/{total}")

    def test_eq10_5_log_euler_strictly_dec(self):
        """T5: EQ10.5 — log Z(sigma,0) strictly decreasing in sigma."""
        passed, total = self.mod.prove_eq10_5()
        self.assertEqual(passed, total, f"EQ10.5: {passed}/{total}")

    def test_eq10_6_c0_positive(self):
        """T5: EQ10.6 — C0(sigma=0.5, T) > 0 (sigma-selectivity barrier)."""
        passed, total = self.mod.prove_eq10_6()
        self.assertEqual(passed, total, f"EQ10.6: {passed}/{total}")

    def test_eq10_7_riemann_zero_bounds(self):
        """T5: EQ10.7 — Euler bounds hold at 8 Riemann zero heights."""
        passed, total = self.mod.prove_eq10_7()
        self.assertEqual(passed, total, f"EQ10.7: {passed}/{total}")

    def test_proofs_list_complete(self):
        """T5: PROOFS list contains all 8 proposition entries (7 numeric + EQ10.A analytic)."""
        self.assertEqual(len(self.mod.PROOFS), 8)

    def test_eq10_A_analytic_log_z_monotone(self):
        """T5: prove_eq10_A — analytic d/dsigma[log Z(sigma,0)] < 0."""
        passed, total = self.mod.prove_eq10_A()
        self.assertGreater(total, 0)
        self.assertEqual(passed, total, f"EQ10.A analytic log-Z: {passed}/{total}")


if __name__ == '__main__':
    unittest.main()
