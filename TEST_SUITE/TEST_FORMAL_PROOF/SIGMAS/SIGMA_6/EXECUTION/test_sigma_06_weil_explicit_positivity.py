#!/usr/bin/env python3
"""
test_sigma_06_weil_explicit_positivity.py
==========================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/SIGMAS/SIGMA_6/EXECUTION/EQ6_WEIL_EXPLICIT_POSITIVITY.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads and key symbols are present
    T3 — EulerianWeilEngine: weil_value(), curvature()
    T4 — Test functions: gaussian_fn, cosine_bump_fn
    T5 — Proposition runners EQ6.1 – EQ6.7 all pass
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
SCRIPT = ROOT / 'FORMAL_PROOF_NEW' / 'SIGMAS' / 'SIGMA_6' / 'EXECUTION' / 'EQ6_WEIL_EXPLICIT_POSITIVITY.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('EQ6_WEIL_EXPLICIT_POSITIVITY', SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules['EQ6_WEIL_EXPLICIT_POSITIVITY'] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestSigma06Syntax(unittest.TestCase):

    def test_script_exists(self):
        """T1: Script file is present."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")

    def test_compiles_without_errors(self):
        """T1: EQ6_WEIL_EXPLICIT_POSITIVITY.py compiles cleanly."""
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import and symbols
# ---------------------------------------------------------------------------
class TestSigma06Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module loads without ImportError."""
        self.assertIsNotNone(self.mod)

    def test_key_classes_present(self):
        """T2: Key classes exported by EQ6."""
        for name in ('EulerianWeilEngine', 'WeilResult', 'SensitivityResult',
                     'EQ6ValidationSummary', 'PrimeSideEnergyModel'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")

    def test_key_functions_present(self):
        """T2: Proposition runners and test-function builders exported."""
        for name in ('run_eq6_1', 'run_eq6_2', 'run_eq6_3',
                     'run_eq6_4', 'run_eq6_5', 'run_eq6_6', 'run_eq6_7',
                     'gaussian_fn', 'cosine_bump_fn'):
            self.assertTrue(hasattr(self.mod, name), f"Missing function: {name}")


# ---------------------------------------------------------------------------
# T3 — EulerianWeilEngine
# ---------------------------------------------------------------------------
class TestSigma06WeilEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        em      = cls.mod.PrimeSideEnergyModel(pa)
        cls.em  = em
        cls.we  = cls.mod.EulerianWeilEngine(em)

    def test_curvature_nonneg_at_half(self):
        """T3: C(sigma=0.5, T=14.134; delta=0.05) >= 0."""
        c = self.we.curvature(sigma=0.5, T=14.134, delta=0.05)
        self.assertGreaterEqual(c, 0.0, f"curvature = {c}")

    def test_weil_value_nonneg_gaussian(self):
        """T3: W_E(gaussian(alpha=4), sigma=0.5, T=14.134) >= 0."""
        g = self.mod.gaussian_fn(4.0)
        val = self.we.weil_value(g, sigma=0.5, T=14.134)
        self.assertGreaterEqual(val, 0.0, f"weil_value = {val}")

    def test_weil_value_nonneg_cosine(self):
        """T3: W_E(cosine_bump(L=0.15), sigma=0.5, T=14.134) >= 0."""
        g = self.mod.cosine_bump_fn(0.15)
        val = self.we.weil_value(g, sigma=0.5, T=14.134)
        self.assertGreaterEqual(val, 0.0, f"weil_value = {val}")

    def test_evaluate_grid_returns_weil_results(self):
        """T3: evaluate_grid returns a list of WeilResult dataclasses."""
        g       = self.mod.gaussian_fn(4.0)
        results = self.we.evaluate_grid(g, "gaussian", 4.0, [0.5], [14.134])
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertIsInstance(r, self.mod.WeilResult)
            self.assertGreaterEqual(r.weil_value, 0.0)


# ---------------------------------------------------------------------------
# T4 — gaussian_fn and cosine_bump_fn
# ---------------------------------------------------------------------------
class TestSigma06TestFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_gaussian_fn_nonneg(self):
        """T4: gaussian_fn(alpha)(x) >= 0 for all real x."""
        g = self.mod.gaussian_fn(4.0)
        for x in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            self.assertGreaterEqual(g(x), 0.0, f"gaussian < 0 at x={x}")

    def test_gaussian_fn_peak_at_zero(self):
        """T4: gaussian_fn peaks at x=0."""
        g = self.mod.gaussian_fn(4.0)
        self.assertAlmostEqual(g(0.0), 1.0, places=10)

    def test_cosine_bump_nonneg(self):
        """T4: cosine_bump_fn(L)(x) >= 0 for all x."""
        g = self.mod.cosine_bump_fn(0.15)
        for x in [-0.2, -0.1, 0.0, 0.1, 0.2]:
            self.assertGreaterEqual(g(x), 0.0, f"cosine_bump < 0 at x={x}")

    def test_cosine_bump_zero_outside_support(self):
        """T4: cosine_bump_fn(L)(x) == 0 for |x| > L."""
        L = 0.15
        g = self.mod.cosine_bump_fn(L)
        self.assertEqual(g(0.2), 0.0)
        self.assertEqual(g(-0.2), 0.0)

    def test_cosine_bump_peak_at_zero(self):
        """T4: cosine_bump_fn peaks at x=0 with value 1.0."""
        g = self.mod.cosine_bump_fn(0.15)
        self.assertAlmostEqual(g(0.0), 1.0, places=10)


# ---------------------------------------------------------------------------
# T5 — Proposition runners EQ6.1 – EQ6.7
# ---------------------------------------------------------------------------
class TestSigma06PropositionRunners(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        em      = cls.mod.PrimeSideEnergyModel(pa)
        cls.em  = em
        cls.we  = cls.mod.EulerianWeilEngine(em)

    def test_eq6_1_energy_nonneg(self):
        """T5: EQ6.1 — E(sigma,T) >= 0 at all test points."""
        passed, total = self.mod.run_eq6_1(self.em)
        self.assertEqual(passed, total, f"EQ6.1: {passed}/{total}")

    def test_eq6_2_curvature_nonneg(self):
        """T5: EQ6.2 — C(sigma,T;delta) >= 0 at all test points."""
        passed, total = self.mod.run_eq6_2(self.we)
        self.assertEqual(passed, total, f"EQ6.2: {passed}/{total}")

    def test_eq6_3_weil_nonneg(self):
        """T5: EQ6.3 — W_E(g,sigma,T) >= 0 for both function families."""
        passed, total, min_w = self.mod.run_eq6_3(self.we)
        self.assertEqual(passed, total, f"EQ6.3: {passed}/{total}")
        self.assertGreaterEqual(min_w, 0.0, f"EQ6.3 min_weil = {min_w}")

    def test_eq6_4_gaussian_strictly_positive(self):
        """T5: EQ6.4 — W_E(gaussian) strictly > 0."""
        passed, total = self.mod.run_eq6_4(self.we)
        self.assertEqual(passed, total, f"EQ6.4: {passed}/{total}")

    def test_eq6_5_cosine_strictly_positive(self):
        """T5: EQ6.5 — W_E(cosine-bump) strictly > 0."""
        passed, total = self.mod.run_eq6_5(self.we)
        self.assertEqual(passed, total, f"EQ6.5: {passed}/{total}")

    def test_eq6_6_riemann_zeros(self):
        """T5: EQ6.6 — W_E > 0 at 8 Riemann zero heights."""
        passed, total = self.mod.run_eq6_6(self.we)
        self.assertEqual(passed, total, f"EQ6.6: {passed}/{total}")

    def test_eq6_7_sensitivity_monotone(self):
        """T5: EQ6.7 — W_E decreases as g narrows."""
        passed, total = self.mod.run_eq6_7(self.we)
        self.assertEqual(passed, total, f"EQ6.7: {passed}/{total}")


if __name__ == '__main__':
    unittest.main()
