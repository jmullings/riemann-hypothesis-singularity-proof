#!/usr/bin/env python3
"""
test_sigma_02_strict_convexity_away.py
========================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/SIGMAS/SIGMA_2/EXECUTION/EQ2_STRICT_CONVEXITY_AWAY.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads and key symbols are present
    T3 — StrictCurvatureResult: fields and semantic correctness
    T4 — StrictCurvatureEngine.evaluate: single-point EQ2 check
    T5 — run_eq2_strict_convexity_demo: full validation summary
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
SCRIPT = ROOT / 'FORMAL_PROOF_NEW' / 'SIGMAS' / 'SIGMA_2' / 'EXECUTION' / 'EQ2_STRICT_CONVEXITY_AWAY.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('EQ2_STRICT_CONVEXITY_AWAY', SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules['EQ2_STRICT_CONVEXITY_AWAY'] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestSigma02Syntax(unittest.TestCase):

    def test_script_exists(self):
        """T1: Script file is present."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")

    def test_compiles_without_errors(self):
        """T1: EQ2_STRICT_CONVEXITY_AWAY.py compiles cleanly."""
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import and symbols
# ---------------------------------------------------------------------------
class TestSigma02Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module loads without ImportError."""
        self.assertIsNotNone(self.mod)

    def test_key_classes_present(self):
        """T2: Key classes exported by EQ2."""
        for name in ('EQ2GlobalConvexityEngine', 'EQ2ValidationSummary',
                     'StrictCurvatureEngine', 'StrictCurvatureResult',
                     'BVSpectralGapEngine', 'BVSpectralGapResult'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")

    def test_key_functions_present(self):
        """T2: Main demo function exported."""
        self.assertTrue(hasattr(self.mod, 'run_eq2_strict_convexity_demo'))
        self.assertTrue(hasattr(self.mod, 'run_bv_spectral_gap_demo'))


# ---------------------------------------------------------------------------
# T3 — StrictCurvatureResult fields
# ---------------------------------------------------------------------------
class TestSigma02StrictCurvatureResult(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        cls.engine = cls.mod.StrictCurvatureEngine(pa=pa)

    def test_evaluate_returns_correct_type(self):
        """T3: evaluate() returns StrictCurvatureResult."""
        result = self.engine.evaluate(sigma=0.5, T=14.134, h=0.1)
        self.assertIsInstance(result, self.mod.StrictCurvatureResult)

    def test_result_fields_present(self):
        """T3: StrictCurvatureResult has all expected fields."""
        result = self.engine.evaluate(sigma=0.5, T=14.134, h=0.1)
        for field in ('sigma', 'T', 'h', 'energy', 'fd_curvature', 'c_fd',
                      'c_lower_bound', 'cs_lower_bound', 'd_sigma_slope',
                      'd2_analytic', 'passes_strict', 'passes_cs'):
            self.assertTrue(hasattr(result, field), f"Missing field: {field}")

    def test_energy_nonnegative(self):
        """T3: energy = |D|^2 >= 0."""
        result = self.engine.evaluate(sigma=0.5, T=14.134, h=0.1)
        self.assertGreaterEqual(result.energy, 0.0)

    def test_c_lower_bound_nonnegative(self):
        """T3: EQ2.3 mean lower bound c >= 0."""
        result = self.engine.evaluate(sigma=0.5, T=14.134, h=0.1)
        self.assertGreaterEqual(result.c_lower_bound, 0.0)


# ---------------------------------------------------------------------------
# T4 — passes_strict at sigma=1/2
# ---------------------------------------------------------------------------
class TestSigma02PassesStrict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        cls.engine = cls.mod.StrictCurvatureEngine(pa=pa)

    def test_passes_strict_at_critical_line(self):
        """T4: fd_curvature >= 0 at sigma=0.5, T=14.134."""
        result = self.engine.evaluate(sigma=0.5, T=14.134, h=0.1)
        self.assertTrue(result.passes_strict,
                        f"passes_strict failed: fd_curvature={result.fd_curvature}")

    def test_passes_cs_at_critical_line(self):
        """T4: EQ2.2 Cauchy-Schwarz bound d2 >= (dE/ds)^2 / (2E)."""
        result = self.engine.evaluate(sigma=0.5, T=14.134, h=0.1)
        self.assertTrue(result.passes_cs,
                        f"passes_cs failed: d2={result.d2_analytic}, cs_bound={result.cs_lower_bound}")

    def test_passes_strict_multiple_T(self):
        """T4: passes_strict at sigma=0.5 for T in [10, 14.134, 21.022, 50]."""
        for T in [10.0, 14.134, 21.022, 50.0]:
            result = self.engine.evaluate(sigma=0.5, T=T, h=0.05)
            self.assertTrue(result.passes_strict,
                            f"passes_strict failed at T={T}")


# ---------------------------------------------------------------------------
# T5 — run_eq2_strict_convexity_demo
# ---------------------------------------------------------------------------
class TestSigma02ValidationDemo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.summary = cls.mod.run_eq2_strict_convexity_demo(
            T_values=[10.0, 14.134, 21.022, 50.0],
            h_values=[0.05, 0.10],
            X=50,
            export_csv=False,
        )

    def test_summary_type(self):
        """T5: Returns EQ2ValidationSummary."""
        self.assertIsInstance(self.summary, self.mod.EQ2ValidationSummary)

    def test_total_checks_positive(self):
        """T5: total_checks > 0."""
        self.assertGreater(self.summary.total_checks, 0)

    def test_all_strict_pass(self):
        """T5: strict_fails == 0."""
        self.assertEqual(self.summary.strict_fails, 0,
                         f"{self.summary.strict_fails} strict failures")

    def test_all_cs_pass(self):
        """T5: cs_fails == 0."""
        self.assertEqual(self.summary.cs_fails, 0,
                         f"{self.summary.cs_fails} Cauchy-Schwarz failures")

    def test_min_c_fd_nonnegative(self):
        """T5: min c_fd = fd_curvature/h^2 >= 0."""
        self.assertGreaterEqual(self.summary.min_c_fd, 0.0)

    def test_legacy_aliases(self):
        """T5: Legacy .passes/.fails aliases equal strict counts."""
        self.assertEqual(self.summary.passes, self.summary.strict_passes)
        self.assertEqual(self.summary.fails,  self.summary.strict_fails)


if __name__ == '__main__':
    unittest.main()
