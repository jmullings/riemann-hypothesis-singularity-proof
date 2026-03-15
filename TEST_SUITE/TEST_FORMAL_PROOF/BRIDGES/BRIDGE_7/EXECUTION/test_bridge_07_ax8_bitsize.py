#!/usr/bin/env python3
"""
test_bridge_07_ax8_bitsize.py
==============================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/BRIDGES/BRIDGE_7/EXECUTION/BRIDGE_07_AX8_BITSIZE.py

This file is the AXIOM 8 Inverse Bitsize Shift bridge.

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads with shared-module path set
    T3 — MacroSectorReconstruction: bitsize statistics are valid
    T4 — MacroSectorReconstruction.build_A_macro: 3×3 PSD diagonal matrix
    T5 — InverseBitsizeShift: instantiation, 6D operator present
    T6 — InverseBitsizeShift.reconstruct_9D: 9×9 matrix, finite, PSD
    T7 — BridgeLift6Dto9D: lift_eigenvalues returns correct structure
    T8 — BridgeLift6Dto9D: lift_trace returns correct structure

Author: auto-generated test mirror
"""

from __future__ import annotations

import sys
import unittest
import py_compile
import importlib.util
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SHARED = ROOT / 'FORMAL_PROOF' / 'Prime-Defined-Operator'
BRIDGE_EXEC = ROOT / 'FORMAL_PROOF_NEW' / 'BRIDGES' / 'BRIDGE_7' / 'EXECUTION'
SCRIPT = BRIDGE_EXEC / 'BRIDGE_07_AX8_BITSIZE.py'


def _add_paths():
    for p in [str(SHARED), str(BRIDGE_EXEC)]:
        if p not in sys.path:
            sys.path.insert(0, p)


def _load_module():
    _add_paths()
    spec = importlib.util.spec_from_file_location('BRIDGE_07_AX8_BITSIZE', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestBridge07Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: BRIDGE_07_AX8_BITSIZE.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import
# ---------------------------------------------------------------------------
class TestBridge07Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module imports successfully."""
        self.assertIsNotNone(self.mod)

    def test_expected_symbols(self):
        """T2: Key symbols exported."""
        for name in ('MacroSectorReconstruction', 'InverseBitsizeShift',
                     'BridgeLift6Dto9D', 'AXIOM_8_STATEMENT'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")

    def test_axiom_8_statement_is_string(self):
        """T2: AXIOM_8_STATEMENT is a non-empty string."""
        s = self.mod.AXIOM_8_STATEMENT
        self.assertIsInstance(s, str)
        self.assertGreater(len(s), 50)


# ---------------------------------------------------------------------------
# T3 — MacroSectorReconstruction statistics
# ---------------------------------------------------------------------------
class TestBridge07MacroSector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.macro = cls.mod.MacroSectorReconstruction(T=100.0, N_max=50)

    def test_mean_b_positive(self):
        """T3: mean_b (average bitsize) > 0."""
        self.assertGreater(self.macro.mean_b, 0.0)

    def test_var_b_nonnegative(self):
        """T3: var_b (bitsize variance) ≥ 0."""
        self.assertGreaterEqual(self.macro.var_b, 0.0)

    def test_max_b_gte_mean_b(self):
        """T3: max_b ≥ mean_b."""
        self.assertGreaterEqual(self.macro.max_b, self.macro.mean_b)

    def test_expected_b_positive(self):
        """T3: expected_b = log2(T) > 0 for T > 2."""
        self.assertGreater(self.macro.expected_b, 0.0)

    def test_energy_positive(self):
        """T3: macro energy > 0."""
        self.assertGreater(self.macro.energy, 0.0)


# ---------------------------------------------------------------------------
# T4 — build_A_macro
# ---------------------------------------------------------------------------
class TestBridge07BuildAMacro(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.macro = cls.mod.MacroSectorReconstruction(T=100.0, N_max=50)
        cls.A_macro = cls.macro.build_A_macro()

    def test_shape_3x3(self):
        """T4: A_macro has shape (3, 3)."""
        self.assertEqual(self.A_macro.shape, (3, 3))

    def test_diagonal_structure(self):
        """T4: A_macro is diagonal (off-diagonal entries are zero)."""
        off_diag = self.A_macro - np.diag(np.diag(self.A_macro))
        np.testing.assert_array_equal(off_diag, np.zeros((3, 3)))

    def test_diagonal_nonnegative(self):
        """T4: Diagonal entries are non-negative (A_macro ≥ 0)."""
        diag = np.diag(self.A_macro)
        self.assertTrue(np.all(diag >= 0))

    def test_all_finite(self):
        """T4: All entries are finite."""
        self.assertTrue(np.all(np.isfinite(self.A_macro)))


# ---------------------------------------------------------------------------
# T5 — InverseBitsizeShift instantiation
# ---------------------------------------------------------------------------
class TestBridge07InverseBitsizeShift(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        cls.mod = _load_module()
        cls.shift = cls.mod.InverseBitsizeShift(T_range=(100, 150), num_samples=5)

    def test_instantiates(self):
        """T5: InverseBitsizeShift instantiates without error."""
        self.assertIsNotNone(self.shift)

    def test_S_T_positive(self):
        """T5: S(T) (bitsize scale) > 0."""
        self.assertGreater(self.shift.get_S_T(), 0.0)

    def test_A_tilde_shape(self):
        """T5: Ã (normalized 6D operator) has shape (6, 6)."""
        A_tilde = self.shift.get_A_tilde()
        self.assertEqual(A_tilde.shape, (6, 6))

    def test_A_tilde_symmetric(self):
        """T5: Ã is symmetric."""
        A_tilde = self.shift.get_A_tilde()
        np.testing.assert_allclose(A_tilde, A_tilde.T, atol=1e-12)


# ---------------------------------------------------------------------------
# T6 — reconstruct_9D
# ---------------------------------------------------------------------------
class TestBridge07Reconstruct9D(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        cls.mod = _load_module()
        cls.shift = cls.mod.InverseBitsizeShift(T_range=(100, 150), num_samples=5)
        cls.A_9D = cls.shift.reconstruct_9D(T=120.0)

    def test_shape_9x9(self):
        """T6: Reconstructed 9D operator has shape (9, 9)."""
        self.assertEqual(self.A_9D.shape, (9, 9))

    def test_all_finite(self):
        """T6: All entries of reconstructed 9D operator are finite."""
        self.assertTrue(np.all(np.isfinite(self.A_9D)))

    def test_micro_block_is_symmetric(self):
        """T6: 6×6 micro block is symmetric."""
        micro = self.A_9D[:6, :6]
        np.testing.assert_allclose(micro, micro.T, atol=1e-12)

    def test_macro_block_is_diagonal(self):
        """T6: 3×3 macro block is diagonal."""
        macro = self.A_9D[6:, 6:]
        off_diag = macro - np.diag(np.diag(macro))
        np.testing.assert_array_equal(off_diag, np.zeros((3, 3)))

    def test_cross_blocks_are_zero(self):
        """T6: Off-diagonal cross blocks are zero (direct sum structure)."""
        np.testing.assert_array_equal(self.A_9D[:6, 6:], np.zeros((6, 3)))
        np.testing.assert_array_equal(self.A_9D[6:, :6], np.zeros((3, 6)))


# ---------------------------------------------------------------------------
# T7 — BridgeLift6Dto9D.lift_eigenvalues
# ---------------------------------------------------------------------------
class TestBridge07LiftEigenvalues(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        cls.mod = _load_module()
        shift = cls.mod.InverseBitsizeShift(T_range=(100, 150), num_samples=5)
        cls.lift = cls.mod.BridgeLift6Dto9D(shift)
        # Use dummy 6D eigenvalues
        cls.eigs_6D = np.array([0.5, 0.3, 0.2, 0.1, 0.05, 0.02])

    def test_lift_returns_dict(self):
        """T7: lift_eigenvalues returns a dict."""
        result = self.lift.lift_eigenvalues(self.eigs_6D)
        self.assertIsInstance(result, dict)

    def test_lift_has_expected_keys(self):
        """T7: Result has expected keys."""
        result = self.lift.lift_eigenvalues(self.eigs_6D)
        for key in ('6D_eigenvalues', '9D_micro_eigenvalues',
                    '9D_macro_eigenvalues', '9D_full_eigenvalues', 'S_T'):
            self.assertIn(key, result, f"Missing key: {key}")

    def test_9D_full_has_9_eigenvalues(self):
        """T7: Full 9D eigenvalue array has 9 entries (6 micro + 3 macro)."""
        result = self.lift.lift_eigenvalues(self.eigs_6D)
        self.assertEqual(len(result['9D_full_eigenvalues']), 9)

    def test_S_T_positive(self):
        """T7: S_T in result is positive."""
        result = self.lift.lift_eigenvalues(self.eigs_6D)
        self.assertGreater(result['S_T'], 0.0)


# ---------------------------------------------------------------------------
# T8 — BridgeLift6Dto9D.lift_trace
# ---------------------------------------------------------------------------
class TestBridge07LiftTrace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_paths()
        cls.mod = _load_module()
        shift = cls.mod.InverseBitsizeShift(T_range=(100, 150), num_samples=5)
        cls.lift = cls.mod.BridgeLift6Dto9D(shift)

    def test_lift_trace_returns_dict(self):
        """T8: lift_trace returns a dict."""
        result = self.lift.lift_trace(trace_6D=1.0, power=1)
        self.assertIsInstance(result, dict)

    def test_lift_trace_keys_present(self):
        """T8: Result contains expected keys."""
        result = self.lift.lift_trace(trace_6D=1.0, power=1)
        for key in ('trace_6D', 'trace_9D_micro', 'trace_9D_macro',
                    'trace_9D_total', 'power'):
            self.assertIn(key, result, f"Missing key: {key}")

    def test_trace_micro_scales_by_S_T(self):
        """T8: 9D micro trace = S_T^power × trace_6D."""
        import math
        result = self.lift.lift_trace(trace_6D=1.0, power=1)
        S_T = result['S_T_power']
        self.assertAlmostEqual(result['trace_9D_micro'], S_T * 1.0, places=10)

    def test_trace_9D_total_finite(self):
        """T8: Total 9D trace is finite."""
        import math
        result = self.lift.lift_trace(trace_6D=1.0, power=2)
        self.assertTrue(math.isfinite(result['trace_9D_total']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
