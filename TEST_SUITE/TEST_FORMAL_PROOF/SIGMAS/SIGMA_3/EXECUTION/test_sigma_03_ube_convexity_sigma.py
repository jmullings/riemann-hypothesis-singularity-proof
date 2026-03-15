#!/usr/bin/env python3
"""
test_sigma_03_ube_convexity_sigma.py
======================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/SIGMAS/SIGMA_3/EXECUTION/EQ3_UBE_CONVEXITY_SIGMA.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads and key symbols are present
    T3 — UBEIdentityResult: EQ3.1 exact identity d2sigma + d2T = 4|D_sigma|^2
    T4 — UBEConvexityEngine: identity scan and curvature scan
    T5 — run_eq3_demo: full validation summary is passing
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
SCRIPT = ROOT / 'FORMAL_PROOF_NEW' / 'SIGMAS' / 'SIGMA_3' / 'EXECUTION' / 'EQ3_UBE_CONVEXITY_SIGMA.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('EQ3_UBE_CONVEXITY_SIGMA', SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules['EQ3_UBE_CONVEXITY_SIGMA'] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestSigma03Syntax(unittest.TestCase):

    def test_script_exists(self):
        """T1: Script file is present."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")

    def test_compiles_without_errors(self):
        """T1: EQ3_UBE_CONVEXITY_SIGMA.py compiles cleanly."""
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import and symbols
# ---------------------------------------------------------------------------
class TestSigma03Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module loads without ImportError."""
        self.assertIsNotNone(self.mod)

    def test_key_classes_present(self):
        """T2: Key classes exported by EQ3."""
        for name in ('UBECurvatureEngine', 'UBE6DEngine', 'UBEIdentityResult',
                     'UBEConvexityResult', 'UBEConvexityEngine',
                     'EQ3ValidationSummary'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")

    def test_key_functions_present(self):
        """T2: Main demo functions exported."""
        self.assertTrue(hasattr(self.mod, 'run_eq3_demo'))
        self.assertTrue(hasattr(self.mod, 'run_6d_ube_demo'))


# ---------------------------------------------------------------------------
# T3 — EQ3.1 identity: d2sigma + d2T = 4|D_sigma|^2
# ---------------------------------------------------------------------------
class TestSigma03UBEIdentity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa         = cls.mod.PrimeArithmetic(X=50)
        engine     = cls.mod.UBECurvatureEngine(pa=pa)
        cls.checker = cls.mod.UBEConvexityEngine(ube_engine=engine)

    def test_check_identity_returns_correct_type(self):
        """T3: check_identity returns UBEIdentityResult."""
        result = self.checker.check_identity(sigma=0.5, T=14.134)
        self.assertIsInstance(result, self.mod.UBEIdentityResult)

    def test_identity_result_fields(self):
        """T3: UBEIdentityResult has necessary fields."""
        result = self.checker.check_identity(sigma=0.5, T=14.134)
        for field in ('sigma', 'T', 'd2_sigma', 'd2_T', 'ube_sum',
                      'ube_analytic', 'residual', 'passes_identity', 'ube_nonneg'):
            self.assertTrue(hasattr(result, field), f"Missing field: {field}")

    def test_ube_analytic_nonneg(self):
        """T3: 4|D_sigma|^2 >= 0 (trivial since it is a squared norm)."""
        result = self.checker.check_identity(sigma=0.5, T=14.134)
        self.assertTrue(result.ube_nonneg,
                        f"4|D_sigma|^2 < 0: ube_analytic={result.ube_analytic}")

    def test_identity_residual_small(self):
        """T3: |d2sigma + d2T - 4|D_sigma|^2| < 1e-6 (machine precision)."""
        result = self.checker.check_identity(sigma=0.5, T=14.134)
        self.assertLess(abs(result.residual), 1e-6,
                        f"Identity residual too large: {result.residual}")

    def test_passes_identity_flag(self):
        """T3: passes_identity == True at sigma=0.5, T=14.134."""
        result = self.checker.check_identity(sigma=0.5, T=14.134)
        self.assertTrue(result.passes_identity)


# ---------------------------------------------------------------------------
# T4 — identity_scan and scan_grid
# ---------------------------------------------------------------------------
class TestSigma03Engines(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa         = cls.mod.PrimeArithmetic(X=50)
        engine     = cls.mod.UBECurvatureEngine(pa=pa)
        cls.checker = cls.mod.UBEConvexityEngine(ube_engine=engine)

    def test_identity_scan_all_pass(self):
        """T4: All identity checks pass across a small (sigma, T) grid."""
        results = self.checker.identity_scan([0.4, 0.5, 0.6], [10.0, 14.134, 50.0])
        failures = [r for r in results if not r.passes_identity]
        self.assertEqual(len(failures), 0,
                         f"{len(failures)} identity failures detected")

    def test_scan_grid_curvature_nonneg(self):
        """T4: UBE curvature C_sigma + C_T >= 0 at all tested points."""
        results = self.checker.scan_grid(
            [0.4, 0.5, 0.6], [10.0, 14.134, 50.0], [0.05]
        )
        failures = [r for r in results if not r.passes]
        self.assertEqual(len(failures), 0,
                         f"{len(failures)} UBE curvature failures detected")


# ---------------------------------------------------------------------------
# T5 — run_eq3_demo
# ---------------------------------------------------------------------------
class TestSigma03ValidationDemo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.summary = cls.mod.run_eq3_demo(
            sigma_values=[0.4, 0.5, 0.6],
            T_values=[10.0, 14.134, 21.022, 50.0],
            h_values=[0.05, 0.10],
            X=50,
            export_csv=False,
        )

    def test_summary_type(self):
        """T5: Returns EQ3ValidationSummary."""
        self.assertIsInstance(self.summary, self.mod.EQ3ValidationSummary)

    def test_total_checks_positive(self):
        """T5: total_checks > 0."""
        self.assertGreater(self.summary.total_checks, 0)

    def test_no_identity_failures(self):
        """T5: identity_fails == 0 (EQ3.1 exact identity holds everywhere)."""
        self.assertEqual(self.summary.identity_fails, 0,
                         f"{self.summary.identity_fails} identity failures")

    def test_min_ube_analytic_nonneg(self):
        """T5: min 4|D_sigma|^2 >= 0 across all tested points."""
        self.assertGreaterEqual(self.summary.min_ube_analytic, 0.0,
                                f"min_ube_analytic = {self.summary.min_ube_analytic}")

    def test_min_curvature_nonneg(self):
        """T5: min UBE curvature >= 0."""
        self.assertGreaterEqual(self.summary.min_curvature, 0.0,
                                f"min_curvature = {self.summary.min_curvature}")

    def test_identity_residuals_small(self):
        """T5: max identity residual < 1e-5."""
        self.assertLess(self.summary.max_residual, 1e-5,
                        f"max_residual = {self.summary.max_residual}")


if __name__ == '__main__':
    unittest.main()
