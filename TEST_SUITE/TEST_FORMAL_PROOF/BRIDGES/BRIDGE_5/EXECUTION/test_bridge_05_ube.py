#!/usr/bin/env python3
"""
test_bridge_05_ube.py
=====================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/BRIDGES/BRIDGE_5/EXECUTION/BRIDGE_05_UBE.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads (self-contained)
    T3 — sieve_mangoldt: known values for small N
    T4 — build_P6_static: correct shape and structure
    T5 — T_phi_9D: output shape, finite values, T-range sensitivity
    T6 — N_phi: positive finite norm
    T7 — C_phi: convexity (UBE) ≥ 0 for T away from zeros
    T8 — UnifiedBindingEquationBridge: instantiation and Phase 1 run

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
BRIDGE_EXEC = ROOT / 'FORMAL_PROOF_NEW' / 'BRIDGES' / 'BRIDGE_5' / 'EXECUTION'
SCRIPT = BRIDGE_EXEC / 'BRIDGE_05_UBE.py'


def _load_module():
    p = str(BRIDGE_EXEC)
    if p not in sys.path:
        sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location('BRIDGE_05_UBE', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestBridge05Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: BRIDGE_05_UBE.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import
# ---------------------------------------------------------------------------
class TestBridge05Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module imports successfully."""
        self.assertIsNotNone(self.mod)

    def test_expected_symbols(self):
        """T2: Key symbols exported."""
        for name in ('sieve_mangoldt', 'T_phi_9D', 'N_phi', 'C_phi',
                     'build_P6_static', 'UnifiedBindingEquationBridge',
                     'PHI', 'NUM_BRANCHES', 'PROJECTION_DIM'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")

    def test_phi_golden_ratio(self):
        """T2: PHI constant equals golden ratio."""
        self.assertAlmostEqual(self.mod.PHI, (1 + np.sqrt(5)) / 2, places=12)

    def test_num_branches_9(self):
        """T2: NUM_BRANCHES = 9 (9D architecture)."""
        self.assertEqual(self.mod.NUM_BRANCHES, 9)

    def test_projection_dim_6(self):
        """T2: PROJECTION_DIM = 6 (6D projection)."""
        self.assertEqual(self.mod.PROJECTION_DIM, 6)


# ---------------------------------------------------------------------------
# T3 — sieve_mangoldt
# ---------------------------------------------------------------------------
class TestBridge05SieveMangoldt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt(20)

    def test_shape(self):
        """T3: sieve_mangoldt(N) returns array of length N+1."""
        self.assertEqual(len(self.lam), 21)

    def test_composite_is_zero(self):
        """T3: Λ(6) = 0 (composite, 2 distinct primes)."""
        self.assertAlmostEqual(float(self.lam[6]), 0.0, places=12)

    def test_prime_is_log_p(self):
        """T3: Λ(2) = log(2), Λ(3) = log(3), Λ(5) = log(5)."""
        import math
        self.assertAlmostEqual(float(self.lam[2]), math.log(2), places=10)
        self.assertAlmostEqual(float(self.lam[3]), math.log(3), places=10)
        self.assertAlmostEqual(float(self.lam[5]), math.log(5), places=10)

    def test_prime_power_is_log_p(self):
        """T3: Λ(4) = Λ(2²) = log(2), Λ(8) = log(2), Λ(9) = log(3)."""
        import math
        self.assertAlmostEqual(float(self.lam[4]), math.log(2), places=10)
        self.assertAlmostEqual(float(self.lam[8]), math.log(2), places=10)
        self.assertAlmostEqual(float(self.lam[9]), math.log(3), places=10)

    def test_nonnegative(self):
        """T3: All Λ(n) ≥ 0."""
        self.assertTrue(np.all(self.lam >= 0))


# ---------------------------------------------------------------------------
# T4 — build_P6_static
# ---------------------------------------------------------------------------
class TestBridge05P6Matrix(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.P6 = cls.mod.build_P6_static()

    def test_shape(self):
        """T4: P6 has shape (6, 9)."""
        self.assertEqual(self.P6.shape, (6, 9))

    def test_identity_block(self):
        """T4: First 6×6 block of P6 is the identity."""
        np.testing.assert_array_equal(self.P6[:, :6], np.eye(6))

    def test_zero_trailing_columns(self):
        """T4: Columns 6, 7, 8 of P6 are zero (B-V suppression)."""
        np.testing.assert_array_equal(self.P6[:, 6:], np.zeros((6, 3)))


# ---------------------------------------------------------------------------
# T5 — T_phi_9D
# ---------------------------------------------------------------------------
class TestBridge05TPhi9D(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt(3000)

    def test_output_shape(self):
        """T5: T_phi_9D returns array of shape (9,)."""
        vec = self.mod.T_phi_9D(4.0, self.lam)
        self.assertEqual(vec.shape, (9,))

    def test_output_finite(self):
        """T5: T_phi_9D output contains no NaN or Inf."""
        for T in [3.0, 4.0, 5.0]:
            vec = self.mod.T_phi_9D(T, self.lam)
            self.assertTrue(np.all(np.isfinite(vec)),
                            f"Non-finite value at T={T}")

    def test_output_nonzero_for_valid_T(self):
        """T5: T_phi_9D is non-zero for T values with primes ≤ e^T."""
        vec = self.mod.T_phi_9D(5.0, self.lam)
        self.assertGreater(np.linalg.norm(vec), 1e-15)


# ---------------------------------------------------------------------------
# T6 — N_phi
# ---------------------------------------------------------------------------
class TestBridge05NPhi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt(3000)
        cls.P6 = cls.mod.build_P6_static()

    def test_nphi_positive(self):
        """T6: N_phi(T) > 0 for T with prime weight support."""
        for T in [3.5, 4.0, 4.5, 5.0]:
            val = self.mod.N_phi(T, self.lam, self.P6)
            self.assertGreater(val, 0.0, f"N_phi({T}) not positive")

    def test_nphi_finite(self):
        """T6: N_phi is finite for valid T."""
        val = self.mod.N_phi(4.0, self.lam, self.P6)
        self.assertTrue(np.isfinite(val))


# ---------------------------------------------------------------------------
# T7 — C_phi (UBE convexity)
# ---------------------------------------------------------------------------
class TestBridge05CPhi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt(3000)
        cls.P6 = cls.mod.build_P6_static()

    def test_cphi_finite(self):
        """T7: C_phi(T, h) is finite."""
        val = self.mod.C_phi(4.5, 0.1, self.lam, self.P6)
        self.assertTrue(np.isfinite(val))

    def test_cphi_symmetric_h(self):
        """T7: C_phi is symmetric in h (same value for +h and -h by definition)."""
        # C_phi(T; h) = N(T+h) + N(T-h) - 2N(T) should be same for +h and -h
        v1 = self.mod.C_phi(5.0, 0.1, self.lam, self.P6)
        v2 = self.mod.C_phi(5.0, -0.1, self.lam, self.P6)
        self.assertAlmostEqual(v1, v2, places=10)


# ---------------------------------------------------------------------------
# T8 — UnifiedBindingEquationBridge
# ---------------------------------------------------------------------------
class TestBridge05UBEBridge(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_bridge_instantiates(self):
        """T8: UnifiedBindingEquationBridge instantiates."""
        bridge = self.mod.UnifiedBindingEquationBridge(
            T_range=(14.0, 35.0), num_points=30, h=0.05, n_zeros=5
        )
        self.assertIsNotNone(bridge)

    def test_bridge_phase1_runs(self):
        """T8: Phase 1 ZKZ analysis populates internal state (returns None)."""
        bridge = self.mod.UnifiedBindingEquationBridge(
            T_range=(14.0, 35.0), num_points=30, h=0.05, n_zeros=5
        )
        result = bridge.run_phase1()
        # run_phase1 returns None but sets private attributes
        self.assertIsNone(result)
        self.assertIsNotNone(bridge._N_phi_vals)
        self.assertIsNotNone(bridge._candidates)

    def test_bridge_nphi_array_correct_size(self):
        """T8: N_phi array has correct length after Phase 1."""
        bridge = self.mod.UnifiedBindingEquationBridge(
            T_range=(14.0, 35.0), num_points=30, h=0.05, n_zeros=5
        )
        bridge.run_phase1()
        self.assertEqual(len(bridge._N_phi_vals), 30)
        self.assertIsInstance(bridge._N_phi_vals, np.ndarray)

    def test_bridge_nphi_all_finite(self):
        """T8: All N_phi values are finite after Phase 1."""
        bridge = self.mod.UnifiedBindingEquationBridge(
            T_range=(14.0, 35.0), num_points=30, h=0.05, n_zeros=5
        )
        bridge.run_phase1()
        self.assertTrue(np.all(np.isfinite(bridge._N_phi_vals)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
