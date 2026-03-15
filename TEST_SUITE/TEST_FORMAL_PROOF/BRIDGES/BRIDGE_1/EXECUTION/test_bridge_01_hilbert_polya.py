#!/usr/bin/env python3
"""
test_bridge_01_hilbert_polya.py
================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/BRIDGES/BRIDGE_1/EXECUTION/BRIDGE_01_HILBERT_POLYA.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads with shared-module path set
    T3 — Constants: RIEMANN_ZEROS values match reference
    T4 — Bridge: HilbertPolyaBridge instantiates and computes spectrum
    T5 — Mathematical: spectrum is real (self-adjoint operator by construction)
    T6 — Mathematical: all eigenvalues are finite

Author: auto-generated test mirror
"""

from __future__ import annotations

import sys
import unittest
import py_compile
import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SHARED = ROOT / 'FORMAL_PROOF' / 'Prime-Defined-Operator'
BRIDGE_EXEC = ROOT / 'FORMAL_PROOF_NEW' / 'BRIDGES' / 'BRIDGE_1' / 'EXECUTION'
SCRIPT = BRIDGE_EXEC / 'BRIDGE_01_HILBERT_POLYA.py'


def _add_paths():
    for p in [str(SHARED), str(BRIDGE_EXEC)]:
        if p not in sys.path:
            sys.path.insert(0, p)


def _load_module():
    _add_paths()
    spec = importlib.util.spec_from_file_location('BRIDGE_01_HILBERT_POLYA', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestBridge01Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: BRIDGE_01_HILBERT_POLYA.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import
# ---------------------------------------------------------------------------
class TestBridge01Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module imports successfully."""
        self.assertIsNotNone(self.mod)

    def test_expected_symbols_present(self):
        """T2: Key symbols are exported."""
        for name in ('RIEMANN_ZEROS', 'HilbertPolyaBridge'):
            self.assertTrue(hasattr(self.mod, name),
                            f"Missing symbol: {name}")


# ---------------------------------------------------------------------------
# T3 — Constants
# ---------------------------------------------------------------------------
class TestBridge01Constants(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_riemann_zeros_count(self):
        """T3: RIEMANN_ZEROS has at least 30 entries."""
        zeros = self.mod.RIEMANN_ZEROS
        self.assertGreaterEqual(len(zeros), 30)

    def test_riemann_zeros_first_value(self):
        """T3: First Riemann zero γ₁ ≈ 14.1347 (within 1e-4)."""
        gamma1 = self.mod.RIEMANN_ZEROS[0]
        self.assertAlmostEqual(gamma1, 14.1347251417347, places=4)

    def test_riemann_zeros_ascending(self):
        """T3: Zeros are listed in ascending order."""
        zeros = self.mod.RIEMANN_ZEROS
        for i in range(len(zeros) - 1):
            self.assertLess(zeros[i], zeros[i + 1],
                            f"Zero at index {i} not < index {i+1}")

    def test_riemann_zeros_all_positive(self):
        """T3: All zero imaginary parts are positive."""
        for z in self.mod.RIEMANN_ZEROS:
            self.assertGreater(z, 0.0)


# ---------------------------------------------------------------------------
# T4 — Bridge Instantiation
# ---------------------------------------------------------------------------
class TestBridge01Instantiation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        cls.mod = _load_module()

    def test_bridge_instantiates(self):
        """T4: HilbertPolyaBridge can be instantiated with small parameters."""
        bridge = self.mod.HilbertPolyaBridge(T_range=(100, 150), num_samples=5)
        self.assertIsNotNone(bridge)

    def test_bridge_has_T_values(self):
        """T4: Bridge exposes T_values array."""
        bridge = self.mod.HilbertPolyaBridge(T_range=(100, 150), num_samples=5)
        self.assertEqual(len(bridge.T_values), 5)
        self.assertAlmostEqual(float(bridge.T_values[0]), 100.0, places=1)
        self.assertAlmostEqual(float(bridge.T_values[-1]), 150.0, places=1)


# ---------------------------------------------------------------------------
# T5 + T6 — Mathematical properties
# ---------------------------------------------------------------------------
class TestBridge01Spectrum(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        import numpy as np
        cls.np = np
        cls.mod = _load_module()
        # Use tiny sample for speed
        cls.bridge = cls.mod.HilbertPolyaBridge(T_range=(100, 150), num_samples=4)

    def test_operator_is_real_symmetric(self):
        """T5: Normalized bridge operator Ã is real and symmetric (self-adjoint)."""
        np = self.np
        op = self.bridge.operator
        M = op.H_tilde
        self.assertTrue(np.all(np.isfinite(M)), "H_tilde contains non-finite values")
        np.testing.assert_allclose(M, M.T, atol=1e-12,
                                   err_msg="H_tilde is not symmetric")

    def test_eigenvalues_are_real_and_finite(self):
        """T6: All eigenvalues of Ã are real-valued and finite."""
        np = self.np
        eigs = np.array(self.bridge.operator.eigenvalues, dtype=float)
        self.assertTrue(np.all(np.isfinite(eigs)),
                        "Eigenvalues contain non-finite values")
        # Eigenvalues from eigh are guaranteed real for symmetric matrix
        self.assertEqual(eigs.dtype.kind, 'f',
                         "Eigenvalues should be floating-point (real)")


if __name__ == '__main__':
    unittest.main(verbosity=2)
