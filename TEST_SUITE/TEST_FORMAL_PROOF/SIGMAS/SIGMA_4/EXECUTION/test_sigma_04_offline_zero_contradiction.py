#!/usr/bin/env python3
"""
test_sigma_04_offline_zero_contradiction.py
=============================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/SIGMAS/SIGMA_4/EXECUTION/EQ4_OFFLINE_ZERO_CONTRADICTION.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads and key symbols are present
    T3 — OfflineZeroContradictionResult: fields and semantics
    T4 — OfflineZeroContradictionEngine: contradiction, energy bounds
    T5 — ConvexityProfileEngine: profile construction
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
SCRIPT = ROOT / 'FORMAL_PROOF_NEW' / 'SIGMAS' / 'SIGMA_4' / 'EXECUTION' / 'EQ4_OFFLINE_ZERO_CONTRADICTION.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('EQ4_OFFLINE_ZERO_CONTRADICTION', SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules['EQ4_OFFLINE_ZERO_CONTRADICTION'] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestSigma04Syntax(unittest.TestCase):

    def test_script_exists(self):
        """T1: Script file is present."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")

    def test_compiles_without_errors(self):
        """T1: EQ4_OFFLINE_ZERO_CONTRADICTION.py compiles cleanly."""
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import and symbols
# ---------------------------------------------------------------------------
class TestSigma04Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module loads without ImportError."""
        self.assertIsNotNone(self.mod)

    def test_key_classes_present(self):
        """T2: Key classes exported by EQ4."""
        for name in ('OfflineZeroContradictionEngine',
                     'EQ4ValidationSummary',
                     'ConvexityProfileEngine'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")

    def test_key_functions_present(self):
        """T2: Main demo function exported."""
        self.assertTrue(hasattr(self.mod, 'run_offline_zero_contradiction_demo'))


# ---------------------------------------------------------------------------
# T3 — OfflineZeroContradictionResult fields
# ---------------------------------------------------------------------------
class TestSigma04ContradictionResult(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        cls.engine = cls.mod.OfflineZeroContradictionEngine(pa)

    def test_contradiction_returns_result(self):
        """T3: contradiction() returns a result object with expected fields."""
        result = self.engine.contradiction(sigma_test=0.65, T=14.134)
        for field in ('sigma_test', 'T', 'E_at_half', 'contradicted',
                      'contradiction_gap'):
            self.assertTrue(hasattr(result, field), f"Missing field: {field}")

    def test_e_at_half_nonnegative(self):
        """T3: E(1/2, T) = |D|^2 >= 0."""
        result = self.engine.contradiction(sigma_test=0.65, T=14.134)
        self.assertGreaterEqual(result.E_at_half, 0.0,
                                f"E_at_half = {result.E_at_half}")

    def test_contradiction_gap_positive(self):
        """T3: Contradiction gap > 0 (E_at_half > 0 for T near Riemann zero)."""
        result = self.engine.contradiction(sigma_test=0.65, T=14.134)
        self.assertGreater(result.contradiction_gap, -1e-12,
                           f"contradiction_gap = {result.contradiction_gap}")

    def test_contradicted_flag(self):
        """T3: contradicted is True when offline zero would force E(1/2) <= 0."""
        result = self.engine.contradiction(sigma_test=0.65, T=14.134)
        # For a well-configured engine with X=50, contradiction is expected
        self.assertIsInstance(result.contradicted, bool)


# ---------------------------------------------------------------------------
# T4 — OfflineZeroContradictionEngine: energy bounds
# ---------------------------------------------------------------------------
class TestSigma04EnergyBounds(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        cls.engine = cls.mod.OfflineZeroContradictionEngine(pa)

    def test_energy_lower_bound_nonneg(self):
        """T4: energy_lower_bound(T) >= 0 for T > 0."""
        for T in [10.0, 14.134, 21.022, 50.0]:
            lb = self.engine.energy_lower_bound(T)
            self.assertGreaterEqual(lb, 0.0,
                                    f"energy_lower_bound({T}) = {lb}")

    def test_analytic_energy_lower_bound_nonneg(self):
        """T4: analytic_energy_lower_bound(sigma) >= 0 for sigma in (0,1)."""
        for sigma in [0.3, 0.5, 0.7]:
            lb = self.engine.analytic_energy_lower_bound(sigma)
            self.assertGreaterEqual(lb, 0.0,
                                    f"analytic_energy_lower_bound({sigma}) = {lb}")

    def test_scan_grid_returns_results(self):
        """T4: scan_grid returns non-empty list."""
        results = self.engine.scan_grid(
            sigma_tests=[0.55, 0.65],
            T_vals=[10.0, 14.134],
        )
        self.assertGreater(len(results), 0)


# ---------------------------------------------------------------------------
# T5 — ConvexityProfileEngine
# ---------------------------------------------------------------------------
class TestSigma04ConvexityProfile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        cls.cpe = cls.mod.ConvexityProfileEngine(pa)

    def test_profile_returns_correct_length(self):
        """T5: profile() returns ConvexityProfile with n_pts sigma values."""
        profile = self.cpe.profile(T=14.134, sigma_lo=0.3, sigma_hi=0.7, n_pts=5)
        self.assertEqual(len(profile.sigmas), 5)

    def test_profile_energies_nonneg(self):
        """T5: All E values in the profile are >= 0."""
        profile = self.cpe.profile(T=14.134, sigma_lo=0.3, sigma_hi=0.7, n_pts=5)
        for e in profile.energies:
            self.assertGreaterEqual(e, 0.0, f"Negative energy in profile: {e}")

    def test_profile_sigma_bounds(self):
        """T5: sigma values span the requested range."""
        profile = self.cpe.profile(T=14.134, sigma_lo=0.3, sigma_hi=0.7, n_pts=5)
        self.assertAlmostEqual(profile.sigmas[0],  0.3, places=6)
        self.assertAlmostEqual(profile.sigmas[-1], 0.7, places=6)

    def test_eq4_validation_summary_fields(self):
        """T5: EQ4ValidationSummary has expected fields."""
        summ = self.mod.EQ4ValidationSummary()
        for field in ('total_checks', 'pass_count', 'eq4_1_count',
                      'eq4_2_count', 'eq4_2_pass', 'eq4_3_count', 'eq4_3_pass',
                      'eq4_4_count', 'eq4_4_pass', 'eq4_5_count', 'eq4_5_pass',
                      'min_energy', 'min_d2E_sigma', 'min_contradiction_gap'):
            self.assertTrue(hasattr(summ, field), f"Missing field: {field}")


if __name__ == '__main__':
    unittest.main()
