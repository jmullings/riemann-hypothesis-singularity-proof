#!/usr/bin/env python3
"""
test_bridge_02_li.py
====================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/BRIDGES/BRIDGE_2/EXECUTION/BRIDGE_02_LI.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads with shared-module path set
    T3 — Constants: CLASSICAL_LI values are all positive and match reference
    T4 — Bridge: LiCoefficientBridge instantiates, traces are finite
    T5 — Mathematical: trace Tr(Ã^n) finite for n=1..5
    T6 — Mathematical: Classical Li ratios λₙ/λ₁ are positive and monotone

Author: auto-generated test mirror
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
ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SHARED = ROOT / 'FORMAL_PROOF' / 'Prime-Defined-Operator'
BRIDGE_EXEC = ROOT / 'FORMAL_PROOF_NEW' / 'BRIDGES' / 'BRIDGE_2' / 'EXECUTION'
SCRIPT = BRIDGE_EXEC / 'BRIDGE_02_LI.py'


def _add_paths():
    for p in [str(SHARED), str(BRIDGE_EXEC)]:
        if p not in sys.path:
            sys.path.insert(0, p)


def _load_module():
    _add_paths()
    spec = importlib.util.spec_from_file_location('BRIDGE_02_LI', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestBridge02Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: BRIDGE_02_LI.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import
# ---------------------------------------------------------------------------
class TestBridge02Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module imports successfully."""
        self.assertIsNotNone(self.mod)

    def test_expected_symbols_present(self):
        """T2: Key symbols exported."""
        for name in ('CLASSICAL_LI', 'CLASSICAL_LI_ACCURATE', 'LiCoefficientBridge'):
            self.assertTrue(hasattr(self.mod, name), f"Missing symbol: {name}")


# ---------------------------------------------------------------------------
# T3 — Constants: CLASSICAL_LI
# ---------------------------------------------------------------------------
class TestBridge02ClassicalLi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.cli = cls.mod.CLASSICAL_LI

    def test_li_coefficients_count(self):
        """T3: CLASSICAL_LI has entries for n = 1..20."""
        self.assertEqual(len(self.cli), 20)

    def test_all_li_positive(self):
        """T3: All classical Li coefficients λₙ > 0 (RH consistent)."""
        for n, val in self.cli.items():
            self.assertGreater(val, 0.0,
                               f"λ_{n} = {val} is not positive")

    def test_li_lambda1_reference(self):
        """T3: λ₁ ≈ 0.023095708966121 (Bombieri-Lagarias reference)."""
        self.assertAlmostEqual(self.cli[1], 0.023095708966121, places=10)

    def test_li_lambda2_reference(self):
        """T3: λ₂ ≈ 0.092345735228047."""
        self.assertAlmostEqual(self.cli[2], 0.092345735228047, places=10)

    def test_li_monotone_increasing(self):
        """T3: λₙ is strictly increasing for n = 1..20."""
        vals = [self.cli[n] for n in range(1, 21)]
        for i in range(len(vals) - 1):
            self.assertLess(vals[i], vals[i + 1],
                            f"λ_{i+1} >= λ_{i+2}: not monotone")

    def test_classical_li_accurate_alias(self):
        """T3: CLASSICAL_LI_ACCURATE is identical to CLASSICAL_LI."""
        self.assertDictEqual(self.mod.CLASSICAL_LI_ACCURATE, self.mod.CLASSICAL_LI)


# ---------------------------------------------------------------------------
# T4 — Bridge instantiation
# ---------------------------------------------------------------------------
class TestBridge02Instantiation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        cls.mod = _load_module()

    def test_bridge_instantiates(self):
        """T4: LiCoefficientBridge instantiates with small parameters."""
        bridge = self.mod.LiCoefficientBridge(T_range=(100, 150), num_samples=5)
        self.assertIsNotNone(bridge)

    def test_bridge_has_S_T(self):
        """T4: Bridge exposes S_T (bitsize normalization) > 0."""
        bridge = self.mod.LiCoefficientBridge(T_range=(100, 150), num_samples=5)
        self.assertGreater(bridge.S_T, 0.0)


# ---------------------------------------------------------------------------
# T5 — Trace computation
# ---------------------------------------------------------------------------
class TestBridge02Traces(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        import numpy as np
        cls.np = np
        cls.mod = _load_module()
        cls.bridge = cls.mod.LiCoefficientBridge(T_range=(100, 150), num_samples=5)

    def test_eulerian_traces_finite(self):
        """T5: Tr(Ã^n) is finite for n = 1..5."""
        import math
        traces = self.bridge.compute_eulerian_traces(n_max=5)
        self.assertEqual(len(traces), 5)
        for n, tr in traces.items():
            self.assertFalse(math.isnan(tr), f"Tr(Ã^{n}) is NaN")
            self.assertFalse(math.isinf(tr), f"Tr(Ã^{n}) is Inf")

    def test_trace_1_is_real(self):
        """T5: Tr(Ã^1) is a real number."""
        traces = self.bridge.compute_eulerian_traces(n_max=1)
        self.assertIsInstance(float(traces[1]), float)


# ---------------------------------------------------------------------------
# T6 — Classical Li ratios
# ---------------------------------------------------------------------------
class TestBridge02ClassicalRatios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.bridge = cls.mod.LiCoefficientBridge(T_range=(100, 150), num_samples=5)

    def test_classical_ratios_positive(self):
        """T6: All classical Li ratios λₙ/λ₁ > 0."""
        ratios = self.bridge.compute_classical_ratios(n_max=10)
        for key, val in ratios.items():
            self.assertGreater(val, 0.0, f"Ratio {key} = {val} not positive")

    def test_classical_ratio_n1_is_1(self):
        """T6: λ₁/λ₁ = 1.0."""
        ratios = self.bridge.compute_classical_ratios(n_max=5)
        self.assertAlmostEqual(ratios[(1, 1)], 1.0, places=12)

    def test_classical_ratios_increasing(self):
        """T6: Ratios λₙ/λ₁ increase with n (Li coefficients grow)."""
        ratios = self.bridge.compute_classical_ratios(n_max=10)
        vals = [ratios[(n, 1)] for n in range(1, 11)]
        for i in range(len(vals) - 1):
            self.assertLess(vals[i], vals[i + 1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
