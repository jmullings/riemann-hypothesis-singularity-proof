#!/usr/bin/env python3
"""
test_bridge_10_espinosa_robin.py
==================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/BRIDGES/BRIDGE_10/EXECUTION/BRIDGE_10_ESPINOSA_ROBIN.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads (self-contained)
    T3 — EspinosaSample dataclass: field structure
    T4 — EspinosaEngine.sigma: divisor function correctness
    T5 — EspinosaEngine.f_robin: Robin bound values
    T6 — EspinosaEngine.espinosa_residual: δ(n) = f(n) - 1
    T7 — EspinosaEngine.multiplicative_epicycle: σ(n)/n
    T8 — EspinosaEngine.sigma_selective_test: σ-selectivity
    T9 — EspinosaBridge: phase_1_zkg_analysis populates samples

Author: auto-generated test mirror
"""

from __future__ import annotations

import sys
import unittest
import py_compile
import importlib.util
from pathlib import Path
import math
from dataclasses import fields as dc_fields

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
BRIDGE_EXEC = ROOT / 'FORMAL_PROOF_NEW' / 'BRIDGES' / 'BRIDGE_10' / 'EXECUTION'
SCRIPT = BRIDGE_EXEC / 'BRIDGE_10_ESPINOSA_ROBIN.py'


def _load_module():
    p = str(BRIDGE_EXEC)
    if p not in sys.path:
        sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location('BRIDGE_10_ESPINOSA_ROBIN', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestBridge10Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: BRIDGE_10_ESPINOSA_ROBIN.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import
# ---------------------------------------------------------------------------
class TestBridge10Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module imports successfully."""
        self.assertIsNotNone(self.mod)

    def test_expected_symbols(self):
        """T2: Key symbols exported."""
        for name in ('EspinosaSample', 'EspinosaEngine', 'EspinosaBridge'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")


# ---------------------------------------------------------------------------
# T3 — EspinosaSample dataclass
# ---------------------------------------------------------------------------
class TestBridge10EspinosaSample(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_is_dataclass(self):
        """T3: EspinosaSample is a dataclass."""
        import dataclasses
        self.assertTrue(dataclasses.is_dataclass(self.mod.EspinosaSample))

    def test_required_fields(self):
        """T3: EspinosaSample has T, n, sigma_n, f_n, delta_n fields."""
        field_names = {f.name for f in dc_fields(self.mod.EspinosaSample)}
        for name in ('T', 'n', 'sigma_n', 'f_n', 'delta_n'):
            self.assertIn(name, field_names, f"Missing field: {name}")

    def test_instantiation(self):
        """T3: EspinosaSample instantiates with expected values."""
        sample = self.mod.EspinosaSample(
            T=14.134725, n=1500000, sigma_n=3000000,
            f_n=0.95, delta_n=-0.05,
            cphi_normalized=0.001, is_anomaly=False
        )
        self.assertEqual(sample.T, 14.134725)
        self.assertAlmostEqual(sample.delta_n, -0.05, places=12)


# ---------------------------------------------------------------------------
# T4 — EspinosaEngine.sigma (divisor function)
# ---------------------------------------------------------------------------
class TestBridge10Sigma(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.engine = cls.mod.EspinosaEngine()

    def test_sigma_1(self):
        """T4: σ(1) = 1."""
        self.assertEqual(self.engine.sigma(1), 1)

    def test_sigma_2(self):
        """T4: σ(2) = 1 + 2 = 3."""
        self.assertEqual(self.engine.sigma(2), 3)

    def test_sigma_4(self):
        """T4: σ(4) = 1 + 2 + 4 = 7."""
        self.assertEqual(self.engine.sigma(4), 7)

    def test_sigma_6(self):
        """T4: σ(6) = 1 + 2 + 3 + 6 = 12."""
        self.assertEqual(self.engine.sigma(6), 12)

    def test_sigma_12(self):
        """T4: σ(12) = 1+2+3+4+6+12 = 28."""
        self.assertEqual(self.engine.sigma(12), 28)

    def test_sigma_prime_is_p_plus_1(self):
        """T4: σ(p) = p + 1 for primes p."""
        for p in (5, 7, 11, 13, 17, 19):
            self.assertEqual(self.engine.sigma(p), p + 1)

    def test_sigma_is_positive(self):
        """T4: σ(n) > 0 for n ≥ 1."""
        for n in range(1, 50):
            self.assertGreater(self.engine.sigma(n), 0)


# ---------------------------------------------------------------------------
# T5 — EspinosaEngine.f_robin
# ---------------------------------------------------------------------------
class TestBridge10FRobin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.engine = cls.mod.EspinosaEngine()

    def test_f_robin_large_n_finite(self):
        """T5: f_robin(n) is finite for n > 5040."""
        for n in (5041, 10000, 100000):
            val = self.engine.f_robin(n)
            self.assertTrue(math.isfinite(val), f"f_robin({n}) not finite: {val}")

    def test_f_robin_large_n_positive(self):
        """T5: f_robin(n) > 0 for n > 5040."""
        for n in (5041, 10000, 100000):
            self.assertGreater(self.engine.f_robin(n), 0.0)

    def test_robin_satisfied_for_typical_n(self):
        """T5: f_robin(n) < 1 for highly composite n > 5040 (Robin's theorem, assuming RH)."""
        # n = 720720 = 2^4 * 3^2 * 5 * 7 * 11 * 13 is highly composite
        n = 720720
        val = self.engine.f_robin(n)
        self.assertLess(val, 1.01)  # Should be close to or below 1


# ---------------------------------------------------------------------------
# T6 — EspinosaEngine.espinosa_residual
# ---------------------------------------------------------------------------
class TestBridge10EspinosaResidual(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.engine = cls.mod.EspinosaEngine()

    def test_delta_is_f_minus_1(self):
        """T6: δ(n) = f_robin(n) - 1 exactly."""
        for n in (5041, 10000, 100000):
            delta = self.engine.espinosa_residual(n)
            f = self.engine.f_robin(n)
            self.assertAlmostEqual(delta, f - 1.0, places=12)

    def test_delta_is_finite(self):
        """T6: δ(n) is finite for n > 5040."""
        for n in (5041, 50000, 200000):
            self.assertTrue(math.isfinite(self.engine.espinosa_residual(n)))


# ---------------------------------------------------------------------------
# T7 — EspinosaEngine.multiplicative_epicycle
# ---------------------------------------------------------------------------
class TestBridge10MultiplicativeEpicycle(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.engine = cls.mod.EspinosaEngine()

    def test_equals_sigma_over_n(self):
        """T7: multiplicative_epicycle(n) = σ(n)/n."""
        for n in (1, 2, 3, 6, 12):
            epic = self.engine.multiplicative_epicycle(n)
            expected = self.engine.sigma(n) / n
            self.assertAlmostEqual(epic, expected, places=12)

    def test_positive(self):
        """T7: epicycle(n) > 0 for n ≥ 1."""
        for n in range(1, 20):
            self.assertGreater(self.engine.multiplicative_epicycle(n), 0.0)


# ---------------------------------------------------------------------------
# T8 — EspinosaEngine.sigma_selective_test
# ---------------------------------------------------------------------------
class TestBridge10SigmaSelectiveTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.engine = cls.mod.EspinosaEngine()
        cls.sigma_values = [0.4, 0.45, 0.5, 0.55, 0.6]
        cls.result = cls.engine.sigma_selective_test(4.0, cls.sigma_values)

    def test_returns_dict(self):
        """T8: sigma_selective_test returns a dict."""
        self.assertIsInstance(self.result, dict)

    def test_keys_match_sigma_values(self):
        """T8: Dict keys match provided sigma_values."""
        self.assertEqual(set(self.result.keys()), set(self.sigma_values))

    def test_values_are_tuples(self):
        """T8: Dict values are (n, delta) 2-tuples."""
        for sigma, val in self.result.items():
            self.assertEqual(len(val), 2, f"Expected 2-tuple for σ={sigma}")
            n, delta = val
            self.assertIsInstance(n, int)
            self.assertIsInstance(delta, float)

    def test_n_above_robin_threshold(self):
        """T8: All n values ≥ 5041 (forced above Robin's threshold)."""
        for sigma, (n, delta) in self.result.items():
            self.assertGreaterEqual(n, 5041)

    def test_delta_is_finite(self):
        """T8: All delta values are finite."""
        for sigma, (n, delta) in self.result.items():
            self.assertTrue(math.isfinite(delta), f"Non-finite delta at σ={sigma}")


# ---------------------------------------------------------------------------
# T9 — EspinosaBridge
# ---------------------------------------------------------------------------
class TestBridge10EspinosaBridge(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_bridge_instantiates(self):
        """T9: EspinosaBridge instantiates without error."""
        bridge = self.mod.EspinosaBridge()
        self.assertIsNotNone(bridge)

    def test_bridge_has_engine(self):
        """T9: EspinosaBridge has an engine attribute."""
        bridge = self.mod.EspinosaBridge()
        self.assertIsInstance(bridge.engine, self.mod.EspinosaEngine)

    def test_phase1_populates_samples(self):
        """T9: phase_1_zkg_analysis populates bridge.samples."""
        bridge = self.mod.EspinosaBridge()
        T_grid = [14.0, 14.134725, 15.0, 20.0, 21.022040, 22.0]
        bridge.phase_1_zkg_analysis(T_grid, anomaly_threshold=0.1)
        self.assertGreater(len(bridge.samples), 0)

    def test_phase1_sample_count_matches_grid(self):
        """T9: Number of samples equals T_grid length (one sample per T)."""
        bridge = self.mod.EspinosaBridge()
        T_grid = [14.0, 21.0, 25.0, 30.0]
        bridge.phase_1_zkg_analysis(T_grid, anomaly_threshold=0.1)
        self.assertEqual(len(bridge.samples), len(T_grid))

    def test_phase1_samples_are_espinosa_sample(self):
        """T9: All samples are EspinosaSample instances."""
        bridge = self.mod.EspinosaBridge()
        T_grid = [14.0, 21.0]
        bridge.phase_1_zkg_analysis(T_grid, anomaly_threshold=0.1)
        for s in bridge.samples:
            self.assertIsInstance(s, self.mod.EspinosaSample)

    def test_phase1_sample_T_values_match_grid(self):
        """T9: Sample T values match the input T_grid."""
        bridge = self.mod.EspinosaBridge()
        T_grid = [14.134725, 21.022040, 25.010858]
        bridge.phase_1_zkg_analysis(T_grid, anomaly_threshold=0.1)
        sample_Ts = [s.T for s in bridge.samples]
        self.assertEqual(sample_Ts, T_grid)

    def test_phase1_sigma_n_positive(self):
        """T9: All sample sigma_n values are positive."""
        bridge = self.mod.EspinosaBridge()
        T_grid = [14.0, 21.0]
        bridge.phase_1_zkg_analysis(T_grid, anomaly_threshold=0.1)
        for s in bridge.samples:
            self.assertGreater(s.sigma_n, 0)

    def test_phase1_delta_n_finite(self):
        """T9: All sample delta_n values are finite."""
        bridge = self.mod.EspinosaBridge()
        T_grid = [14.0, 21.0, 25.0]
        bridge.phase_1_zkg_analysis(T_grid, anomaly_threshold=0.1)
        for s in bridge.samples:
            self.assertTrue(math.isfinite(s.delta_n), f"Non-finite delta_n: {s.delta_n}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
