#!/usr/bin/env python3
"""
test_sigma_01_global_convexity_xi.py
======================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/SIGMAS/SIGMA_1/EXECUTION/EQ1_GLOBAL_CONVEXITY_XI.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads and key symbols are present
    T3 — EQ1ConvexityCheck dataclass: correct fields and semantics
    T4 — EQ1GlobalConvexityEngine.check_single: single-point convexity check
    T5 — run_eq1_sigma_selectivity_demo: full validation summary is passing
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
SCRIPT = ROOT / 'FORMAL_PROOF_NEW' / 'SIGMAS' / 'SIGMA_1' / 'EXECUTION' / 'EQ1_GLOBAL_CONVEXITY_XI.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('EQ1_GLOBAL_CONVEXITY_XI', SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules['EQ1_GLOBAL_CONVEXITY_XI'] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestSigma01Syntax(unittest.TestCase):

    def test_script_exists(self):
        """T1: Script file is present."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")

    def test_compiles_without_errors(self):
        """T1: EQ1_GLOBAL_CONVEXITY_XI.py compiles cleanly."""
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import and symbols
# ---------------------------------------------------------------------------
class TestSigma01Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module loads without ImportError."""
        self.assertIsNotNone(self.mod)

    def test_key_classes_present(self):
        """T2: Key classes exported by EQ1."""
        for name in ('EQ1GlobalConvexityEngine', 'EQ1ValidationSummary',
                     'EQ1ConvexityCheck', 'EulerianStateFactory',
                     'SigmaSelectivityLemma'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")

    def test_key_functions_present(self):
        """T2: Main demo function exported."""
        self.assertTrue(hasattr(self.mod, 'run_eq1_sigma_selectivity_demo'))
        self.assertTrue(hasattr(self.mod, 'run_sigma_profile'))


# ---------------------------------------------------------------------------
# T3 — EQ1ConvexityCheck dataclass
# ---------------------------------------------------------------------------
class TestSigma01ConvexityCheck(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_check_single_returns_correct_type(self):
        """T3: check_single returns an EQ1ConvexityCheck with expected fields."""
        mod     = self.mod
        factory = mod.EulerianStateFactory(X=50)
        lemma   = mod.SigmaSelectivityLemma(state_factory=factory)
        engine  = mod.EQ1GlobalConvexityEngine(lemma=lemma)

        result = engine.check_single(T=14.134, h=0.05, sigma=0.5)
        self.assertIsInstance(result, mod.EQ1ConvexityCheck)
        for field in ('T', 'h', 'sigma', 'energy_at_sigma', 'curvature_energy',
                      'd2_analytic', 'passes_fd', 'passes_analytic',
                      'cauchy_schwarz_margin'):
            self.assertTrue(hasattr(result, field), f"Missing field: {field}")

    def test_energy_is_nonnegative(self):
        """T3: E(sigma, T) = |D|^2 >= 0."""
        mod     = self.mod
        factory = mod.EulerianStateFactory(X=50)
        lemma   = mod.SigmaSelectivityLemma(state_factory=factory)
        engine  = mod.EQ1GlobalConvexityEngine(lemma=lemma)

        result = engine.check_single(T=14.134, h=0.05, sigma=0.5)
        self.assertGreaterEqual(result.energy_at_sigma, 0.0)

    def test_passes_fd_at_critical_line(self):
        """T3: Finite-difference curvature >= 0 at sigma=1/2, T=14.134."""
        mod     = self.mod
        factory = mod.EulerianStateFactory(X=50)
        lemma   = mod.SigmaSelectivityLemma(state_factory=factory)
        engine  = mod.EQ1GlobalConvexityEngine(lemma=lemma)

        result = engine.check_single(T=14.134, h=0.05, sigma=0.5)
        self.assertTrue(result.passes_fd, "check_single fd failed at sigma=0.5, T=14.134")

    def test_passes_analytic_at_critical_line(self):
        """T3: Analytic d2E/dsigma^2 >= 0 at sigma=1/2."""
        mod     = self.mod
        factory = mod.EulerianStateFactory(X=50)
        lemma   = mod.SigmaSelectivityLemma(state_factory=factory)
        engine  = mod.EQ1GlobalConvexityEngine(lemma=lemma)

        result = engine.check_single(T=14.134, h=0.05, sigma=0.5)
        self.assertTrue(result.passes_analytic,
                        f"analytic d2E < 0 at sigma=0.5: d2={result.d2_analytic}")


# ---------------------------------------------------------------------------
# T4 — scan_grid
# ---------------------------------------------------------------------------
class TestSigma01ScanGrid(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        factory = cls.mod.EulerianStateFactory(X=50)
        lemma   = cls.mod.SigmaSelectivityLemma(state_factory=factory)
        cls.engine = cls.mod.EQ1GlobalConvexityEngine(lemma=lemma)

    def test_scan_grid_nonempty(self):
        """T4: scan_grid returns non-empty list for valid inputs."""
        results = self.engine.scan_grid(
            T_values=[14.134, 50.0],
            h_values=[0.05, 0.10],
            sigma=0.5,
        )
        self.assertGreater(len(results), 0)

    def test_scan_grid_all_fd_pass(self):
        """T4: All checks in scan_grid pass finite-difference test."""
        results = self.engine.scan_grid(
            T_values=[14.134, 21.022, 50.0],
            h_values=[0.05, 0.10],
            sigma=0.5,
        )
        failures = [r for r in results if not r.passes_fd]
        self.assertEqual(len(failures), 0,
                         f"{len(failures)} fd failures in scan_grid")

    def test_scan_grid_all_analytic_pass(self):
        """T4: All checks pass the analytic d2E test."""
        results = self.engine.scan_grid(
            T_values=[14.134, 21.022, 50.0],
            h_values=[0.05, 0.10],
            sigma=0.5,
        )
        failures = [r for r in results if not r.passes_analytic]
        self.assertEqual(len(failures), 0,
                         f"{len(failures)} analytic failures in scan_grid")


# ---------------------------------------------------------------------------
# T5 — run_eq1_sigma_selectivity_demo (full validation)
# ---------------------------------------------------------------------------
class TestSigma01ValidationDemo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.summary = cls.mod.run_eq1_sigma_selectivity_demo(
            T_values=[10.0, 14.134, 21.022, 50.0],
            h_values=[0.05, 0.10],
            X=50,
            export_csv=False,
        )

    def test_summary_type(self):
        """T5: run_eq1_sigma_selectivity_demo returns EQ1ValidationSummary."""
        self.assertIsInstance(self.summary, self.mod.EQ1ValidationSummary)

    def test_total_checks_positive(self):
        """T5: total_checks > 0."""
        self.assertGreater(self.summary.total_checks, 0)

    def test_all_fd_pass(self):
        """T5: All fd checks pass (fd_fails == 0)."""
        self.assertEqual(self.summary.fd_fails, 0,
                         f"{self.summary.fd_fails} fd failures in demo")

    def test_all_analytic_pass(self):
        """T5: All analytic checks pass (analytic_fails == 0)."""
        self.assertEqual(self.summary.analytic_fails, 0,
                         f"{self.summary.analytic_fails} analytic failures in demo")

    def test_min_curvature_nonnegative(self):
        """T5: min_curvature >= 0 (no negative second differences)."""
        self.assertGreaterEqual(self.summary.min_curvature, 0.0,
                                f"min_curvature = {self.summary.min_curvature}")

    def test_min_d2_analytic_nonnegative(self):
        """T5: min_d2_analytic >= 0 (pointwise convexity proved)."""
        self.assertGreaterEqual(self.summary.min_d2_analytic, 0.0,
                                f"min_d2_analytic = {self.summary.min_d2_analytic}")

    def test_legacy_aliases(self):
        """T5: Legacy .passes/.fails aliases equal fd counts."""
        self.assertEqual(self.summary.passes, self.summary.fd_passes)
        self.assertEqual(self.summary.fails,  self.summary.fd_fails)


if __name__ == '__main__':
    unittest.main()
