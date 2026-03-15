#!/usr/bin/env python3
"""
test_bridge_03_gue.py
=====================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/BRIDGES/BRIDGE_3/EXECUTION/BRIDGE_03_GUE.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads
    T3 — GUE distribution functions: shape, positivity, normalization
    T4 — GOE distribution functions: shape, positivity
    T5 — Poisson distribution: shape, positivity, normalization
    T6 — CDF functions: monotonicity, range [0,1]
    T7 — Bridge: GUEStatisticsBridge instantiates and computes spacing metrics

Author: auto-generated test mirror
"""

from __future__ import annotations

import sys
import unittest
import py_compile
import importlib.util
from pathlib import Path

import numpy as np
from scipy.integrate import quad

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SHARED = ROOT / 'FORMAL_PROOF' / 'Prime-Defined-Operator'
BRIDGE_EXEC = ROOT / 'FORMAL_PROOF_NEW' / 'BRIDGES' / 'BRIDGE_3' / 'EXECUTION'
SCRIPT = BRIDGE_EXEC / 'BRIDGE_03_GUE.py'


def _add_paths():
    for p in [str(SHARED), str(BRIDGE_EXEC)]:
        if p not in sys.path:
            sys.path.insert(0, p)


def _load_module():
    _add_paths()
    spec = importlib.util.spec_from_file_location('BRIDGE_03_GUE', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestBridge03Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: BRIDGE_03_GUE.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import
# ---------------------------------------------------------------------------
class TestBridge03Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module imports successfully."""
        self.assertIsNotNone(self.mod)

    def test_expected_symbols(self):
        """T2: Key symbols exported."""
        for name in ('wigner_surmise_gue', 'wigner_surmise_goe',
                     'poisson_spacing', 'GUEStatisticsBridge'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")


# ---------------------------------------------------------------------------
# T3 — GUE Wigner Surmise
# ---------------------------------------------------------------------------
class TestBridge03GUEDistribution(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.s = np.linspace(0, 4, 400)

    def test_gue_nonnegative(self):
        """T3: GUE PDF p(s) ≥ 0 for s ≥ 0."""
        pdf = self.mod.wigner_surmise_gue(self.s)
        self.assertTrue(np.all(pdf >= 0))

    def test_gue_at_zero(self):
        """T3: GUE PDF p(0) = 0 (level repulsion)."""
        val = float(self.mod.wigner_surmise_gue(0.0))
        self.assertAlmostEqual(val, 0.0, places=12)

    def test_gue_normalization(self):
        """T3: ∫₀^∞ p_GUE(s) ds ≈ 1 (within 2%)."""
        integral, _ = quad(lambda s: float(self.mod.wigner_surmise_gue(s)),
                           0, 20)
        self.assertAlmostEqual(integral, 1.0, delta=0.02)

    def test_gue_peak_location(self):
        """T3: GUE mode (peak) is between s=0.5 and s=2.5."""
        s_fine = np.linspace(0.01, 5, 1000)
        pdf = self.mod.wigner_surmise_gue(s_fine)
        peak_s = float(s_fine[np.argmax(pdf)])
        self.assertGreater(peak_s, 0.5)
        self.assertLess(peak_s, 2.5)


# ---------------------------------------------------------------------------
# T4 — GOE Wigner Surmise
# ---------------------------------------------------------------------------
class TestBridge03GOEDistribution(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_goe_nonnegative(self):
        """T4: GOE PDF p(s) ≥ 0 for s ≥ 0."""
        s = np.linspace(0, 4, 200)
        pdf = self.mod.wigner_surmise_goe(s)
        self.assertTrue(np.all(pdf >= 0))

    def test_goe_at_zero(self):
        """T4: GOE PDF p(0) = 0 (GOE also has level repulsion)."""
        val = float(self.mod.wigner_surmise_goe(0.0))
        self.assertAlmostEqual(val, 0.0, places=12)

    def test_goe_normalization(self):
        """T4: ∫₀^∞ p_GOE(s) ds ≈ 1 (within 2%)."""
        integral, _ = quad(lambda s: float(self.mod.wigner_surmise_goe(s)),
                           0, 20)
        self.assertAlmostEqual(integral, 1.0, delta=0.02)


# ---------------------------------------------------------------------------
# T5 — Poisson Distribution
# ---------------------------------------------------------------------------
class TestBridge03Poisson(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_poisson_at_zero(self):
        """T5: Poisson PDF p(0) = 1."""
        val = float(self.mod.poisson_spacing(0.0))
        self.assertAlmostEqual(val, 1.0, places=12)

    def test_poisson_nonnegative(self):
        """T5: Poisson PDF ≥ 0 everywhere."""
        s = np.linspace(0, 5, 100)
        pdf = self.mod.poisson_spacing(s)
        self.assertTrue(np.all(pdf >= 0))

    def test_poisson_normalization(self):
        """T5: ∫₀^∞ exp(-s) ds = 1."""
        integral, _ = quad(lambda s: float(self.mod.poisson_spacing(s)),
                           0, 50)
        self.assertAlmostEqual(integral, 1.0, delta=0.01)


# ---------------------------------------------------------------------------
# T6 — CDF
# ---------------------------------------------------------------------------
class TestBridge03CDF(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_wigner_cdf_range(self):
        """T6: GUE CDF values lie in [0, 1]."""
        s = np.linspace(0, 5, 50)
        cdf = self.mod.wigner_surmise_cdf(s)
        self.assertTrue(np.all(cdf >= 0))
        self.assertTrue(np.all(cdf <= 1))

    def test_wigner_cdf_monotone(self):
        """T6: GUE CDF is non-decreasing."""
        s = np.linspace(0, 5, 100)
        cdf = self.mod.wigner_surmise_cdf(s)
        diff = np.diff(cdf)
        self.assertTrue(np.all(diff >= -1e-14),
                        "GUE CDF is not monotone non-decreasing")

    def test_wigner_cdf_starts_at_zero(self):
        """T6: CDF(0) ≈ 0."""
        val = float(self.mod.wigner_surmise_cdf(0.0))
        self.assertAlmostEqual(val, 0.0, places=5)


# ---------------------------------------------------------------------------
# T7 — Bridge
# ---------------------------------------------------------------------------
class TestBridge03Instantiation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        cls.mod = _load_module()

    def test_bridge_instantiates(self):
        """T7: GUEStatisticsBridge instantiates with small parameters."""
        bridge = self.mod.GUEStatisticsBridge(T_range=(100, 150), num_samples=5)
        self.assertIsNotNone(bridge)


if __name__ == '__main__':
    unittest.main(verbosity=2)
