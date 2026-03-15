#!/usr/bin/env python3
"""
test_sigma_05_li_positivity_eulerian.py
=========================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/SIGMAS/SIGMA_5/EXECUTION/EQ5_LI_POSITIVITY_EULERIAN.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads and key symbols are present
    T3 — FDCurvatureEngine: curvature() and taylor_consistency()
    T4 — EulerianLiEngine: li_value() positivity
    T5 — Proposition runners EQ5.1 – EQ5.5 all pass
"""

from __future__ import annotations

import sys
import unittest
import py_compile
import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT   = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SCRIPT = ROOT / 'FORMAL_PROOF_NEW' / 'SIGMAS' / 'SIGMA_5' / 'EXECUTION' / 'EQ5_LI_POSITIVITY_EULERIAN.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('EQ5_LI_POSITIVITY_EULERIAN', SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules['EQ5_LI_POSITIVITY_EULERIAN'] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestSigma05Syntax(unittest.TestCase):

    def test_script_exists(self):
        """T1: Script file is present."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")

    def test_compiles_without_errors(self):
        """T1: EQ5_LI_POSITIVITY_EULERIAN.py compiles cleanly."""
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import and symbols
# ---------------------------------------------------------------------------
class TestSigma05Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module loads without ImportError."""
        self.assertIsNotNone(self.mod)

    def test_key_classes_present(self):
        """T2: Key classes exported by EQ5."""
        for name in ('PrimeSideEnergyModel', 'FDCurvatureEngine',
                     'EulerianLiEngine', 'EQ5ValidationSummary',
                     'CurvatureResult', 'LiResult', 'TaylorConsistencyResult'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")

    def test_key_functions_present(self):
        """T2: Proposition runners and main runner exported."""
        for name in ('run_eq5_1', 'run_eq5_2', 'run_eq5_3',
                     'run_eq5_4', 'run_eq5_5', 'run_eq5'):
            self.assertTrue(hasattr(self.mod, name), f"Missing function: {name}")


# ---------------------------------------------------------------------------
# T3 — FDCurvatureEngine
# ---------------------------------------------------------------------------
class TestSigma05FDCurvatureEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        em      = cls.mod.PrimeSideEnergyModel(pa)
        cls.fd  = cls.mod.FDCurvatureEngine(em)

    def test_curvature_returns_correct_type(self):
        """T3: curvature() returns CurvatureResult."""
        result = self.fd.curvature(sigma=0.5, T=14.134, delta=0.05)
        self.assertIsInstance(result, self.mod.CurvatureResult)

    def test_curvature_positive_at_critical_line(self):
        """T3: C(0.5, T; 0.05) >= 0 for T in [10, 14.134, 50]."""
        for T in [10.0, 14.134, 50.0]:
            result = self.fd.curvature(sigma=0.5, T=T, delta=0.05)
            self.assertTrue(result.positive,
                            f"curvature < 0 at T={T}: {result.curvature}")

    def test_curvature_energy_nonneg(self):
        """T3: E_center = |D|^2 >= 0."""
        result = self.fd.curvature(sigma=0.5, T=14.134, delta=0.05)
        self.assertGreaterEqual(result.E_center, 0.0)

    def test_taylor_consistency_within_tolerance(self):
        """T3: C/delta^2 ~ d2E/dsigma^2 within 5% (Taylor EQ5.5)."""
        result = self.fd.taylor_consistency(sigma=0.5, T=14.134, delta=0.01)
        self.assertIsInstance(result, self.mod.TaylorConsistencyResult)
        self.assertTrue(result.consistent,
                        f"Taylor error {result.relative_error:.2%} exceeds tolerance")


# ---------------------------------------------------------------------------
# T4 — EulerianLiEngine
# ---------------------------------------------------------------------------
class TestSigma05EulerianLiEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        em      = cls.mod.PrimeSideEnergyModel(pa)
        fd      = cls.mod.FDCurvatureEngine(em)
        cls.li  = cls.mod.EulerianLiEngine(fd)

    def test_li_value_nonneg_at_half(self):
        """T4: Lambda_n(sigma=0.5, T=14.134) >= 0 for n=1,2,3."""
        for n in [1, 2, 3]:
            val = self.li.li_value(n=n, sigma=0.5, T=14.134, delta=0.05)
            self.assertGreaterEqual(val, 0.0,
                                    f"li_value(n={n}) = {val} < 0")

    def test_li_value_strictly_positive_at_riemann_zero(self):
        """T4: Lambda_1(sigma=0.5, T=14.1347) strictly > 0."""
        val = self.li.li_value(n=1, sigma=0.5, T=14.1347, delta=0.05)
        self.assertGreater(val, 0.0, f"li_value not strictly positive: {val}")

    def test_evaluate_returns_list_of_li_results(self):
        """T4: evaluate() returns a list of LiResult objects."""
        results = self.li.evaluate(
            n_vals=[1, 2],
            sigma_vals=[0.5],
            T_vals=[14.134, 50.0],
            delta=0.05,
        )
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertIsInstance(r, self.mod.LiResult)


# ---------------------------------------------------------------------------
# T5 — Proposition runners EQ5.1 – EQ5.5
# ---------------------------------------------------------------------------
class TestSigma05PropositionRunners(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        em      = cls.mod.PrimeSideEnergyModel(pa)
        fd      = cls.mod.FDCurvatureEngine(em)
        cls.em  = em
        cls.fd  = fd
        cls.li  = cls.mod.EulerianLiEngine(fd)

    def test_eq5_1_d2E_positive(self):
        """T5: EQ5.1 — all ∂²E/∂σ² > 0 checks pass."""
        passed, total, _ = self.mod.run_eq5_1(self.em)
        self.assertEqual(passed, total,
                         f"EQ5.1: {passed}/{total} passed")

    def test_eq5_2_curvature_nonneg(self):
        """T5: EQ5.2 — all C(σ,T;δ) >= 0 checks pass."""
        passed, total, _ = self.mod.run_eq5_2(self.fd)
        self.assertEqual(passed, total,
                         f"EQ5.2: {passed}/{total} passed")

    def test_eq5_3_li_nonneg(self):
        """T5: EQ5.3 — all Λ_n(T) >= 0 checks pass."""
        passed, total, _ = self.mod.run_eq5_3(self.li)
        self.assertEqual(passed, total,
                         f"EQ5.3: {passed}/{total} passed")

    def test_eq5_4_li_strictly_positive(self):
        """T5: EQ5.4 — Λ_n strictly > 0 at Riemann zero heights."""
        passed, total, _ = self.mod.run_eq5_4(self.li)
        self.assertEqual(passed, total,
                         f"EQ5.4: {passed}/{total} passed")

    def test_eq5_5_taylor_consistency(self):
        """T5: EQ5.5 — Taylor FD consistency within 5% tolerance."""
        passed, total, _ = self.mod.run_eq5_5(self.fd)
        self.assertEqual(passed, total,
                         f"EQ5.5: {passed}/{total} passed")


if __name__ == '__main__':
    unittest.main()
