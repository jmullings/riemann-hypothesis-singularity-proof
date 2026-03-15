#!/usr/bin/env python3
"""
test_bridge_04_weil_de_bruijn.py
=================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/BRIDGES/BRIDGE_4/EXECUTION/BRIDGE_04_WEIL_DE_BRUIJN.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads (optional TRANSCENDENTAL_BRIDGE_ALIGNMENT warned)
    T3 — Classes present: AnalyticalExtension, ConvergenceResult
    T4 — Instantiation: AnalyticalExtension initializes with expected attributes
    T5 — X_values: geometric progression array is positive and increasing

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
BRIDGE_EXEC = ROOT / 'FORMAL_PROOF_NEW' / 'BRIDGES' / 'BRIDGE_4' / 'EXECUTION'
SCRIPT = BRIDGE_EXEC / 'BRIDGE_04_WEIL_DE_BRUIJN.py'


def _add_paths():
    for p in [str(SHARED), str(BRIDGE_EXEC)]:
        if p not in sys.path:
            sys.path.insert(0, p)


def _load_module():
    """Load with warnings suppressed for optional missing deps."""
    _add_paths()
    import warnings
    import io
    spec = importlib.util.spec_from_file_location('BRIDGE_04_WEIL_DE_BRUIJN', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestBridge04Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: BRIDGE_04_WEIL_DE_BRUIJN.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import
# ---------------------------------------------------------------------------
class TestBridge04Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module imports successfully (optional deps may warn)."""
        self.assertIsNotNone(self.mod)

    def test_expected_classes_present(self):
        """T2: Key classes exported."""
        for name in ('AnalyticalExtension', 'ConvergenceResult'):
            self.assertTrue(hasattr(self.mod, name), f"Missing class: {name}")


# ---------------------------------------------------------------------------
# T3 — ConvergenceResult dataclass
# ---------------------------------------------------------------------------
class TestBridge04ConvergenceResult(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_convergence_result_fields(self):
        """T3: ConvergenceResult dataclass has expected fields."""
        import numpy as np
        CR = self.mod.ConvergenceResult
        # Create a minimal instance
        cr = CR(
            X_values=np.array([50, 100]),
            relative_errors=np.array([0.1, 0.05]),
            lambda_star_values=np.array([100.0, 200.0]),
            x_star_norm_values=np.array([0.3, 0.35]),
            convergence_rate=-0.5,
            asymptotic_bound='O(X^{-0.5})',
            proved_limit_zero=False,
        )
        self.assertEqual(len(cr.X_values), 2)
        self.assertFalse(cr.proved_limit_zero)


# ---------------------------------------------------------------------------
# T4 — AnalyticalExtension instantiation
# ---------------------------------------------------------------------------
class TestBridge04AnalyticalExtension(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        cls.mod = _load_module()

    def test_instantiates_default(self):
        """T4: AnalyticalExtension instantiates with defaults."""
        ae = self.mod.AnalyticalExtension(K_zeros=9, T_range=(100, 200))
        self.assertIsNotNone(ae)

    def test_K_zeros_attribute(self):
        """T4: K_zeros attribute is set correctly."""
        ae = self.mod.AnalyticalExtension(K_zeros=5, T_range=(100, 150))
        self.assertEqual(ae.K_zeros, 5)

    def test_T_range_attribute(self):
        """T4: T_range attribute is set correctly."""
        ae = self.mod.AnalyticalExtension(K_zeros=9, T_range=(100, 300))
        self.assertEqual(ae.T_range, (100, 300))


# ---------------------------------------------------------------------------
# T5 — X_values
# ---------------------------------------------------------------------------
class TestBridge04XValues(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        cls.mod = _load_module()
        cls.ae = cls.mod.AnalyticalExtension(K_zeros=9, T_range=(100, 200))

    def test_x_values_positive(self):
        """T5: X_values are all positive."""
        import numpy as np
        self.assertTrue(np.all(self.ae.X_values > 0))

    def test_x_values_increasing(self):
        """T5: X_values are in ascending order."""
        import numpy as np
        diffs = np.diff(self.ae.X_values)
        self.assertTrue(np.all(diffs > 0))

    def test_x_values_has_entries(self):
        """T5: X_values is non-empty."""
        self.assertGreater(len(self.ae.X_values), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
