#!/usr/bin/env python3
"""
test_bridge_06_explicit_formula.py
====================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/BRIDGES/BRIDGE_6/EXECUTION/BRIDGE_06_EXPLICIT_FORMULA.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads (self-contained)
    T3 — sieve_mangoldt_ef: von Mangoldt values for small N
    T4 — compute_psi: Chebyshev ψ(x) non-negative, accumulates correctly
    T5 — chebyshev_band_ok: sanity bound 0.9212·x ≤ ψ(x) ≤ 1.1056·x
    T6 — smeared_prime_sum: finite, converges as N grows
    T7 — scaling_test: S_prime(T) converges as N grows
    T8 — ExplicitFormulaBridge: instantiation and prime-side evaluation

Author: auto-generated test mirror
"""

from __future__ import annotations

import sys
import unittest
import py_compile
import importlib.util
from pathlib import Path
import math

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SHARED = ROOT / 'FORMAL_PROOF' / 'Prime-Defined-Operator'
BRIDGE_EXEC = ROOT / 'FORMAL_PROOF_NEW' / 'BRIDGES' / 'BRIDGE_6' / 'EXECUTION'
SCRIPT = BRIDGE_EXEC / 'BRIDGE_06_EXPLICIT_FORMULA.py'


def _load_module():
    for p in [str(SHARED), str(BRIDGE_EXEC)]:
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location('BRIDGE_06_EXPLICIT_FORMULA', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestBridge06Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: BRIDGE_06_EXPLICIT_FORMULA.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import
# ---------------------------------------------------------------------------
class TestBridge06Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module imports successfully."""
        self.assertIsNotNone(self.mod)

    def test_expected_symbols(self):
        """T2: Key symbols exported."""
        for name in ('sieve_mangoldt_ef', 'compute_psi', 'smeared_prime_sum',
                     'chebyshev_band_ok', 'ExplicitFormulaBridge'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")


# ---------------------------------------------------------------------------
# T3 — sieve_mangoldt_ef
# ---------------------------------------------------------------------------
class TestBridge06SieveMangoldt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt_ef(20)

    def test_length(self):
        """T3: Array length is N+1."""
        self.assertEqual(len(self.lam), 21)

    def test_prime_values(self):
        """T3: Λ(p) = log(p) for primes p = 2, 3, 5, 7."""
        for p in (2, 3, 5, 7):
            self.assertAlmostEqual(float(self.lam[p]), math.log(p), places=10)

    def test_prime_power_values(self):
        """T3: Λ(4) = log(2), Λ(8) = log(2), Λ(9) = log(3)."""
        self.assertAlmostEqual(float(self.lam[4]), math.log(2), places=10)
        self.assertAlmostEqual(float(self.lam[8]), math.log(2), places=10)
        self.assertAlmostEqual(float(self.lam[9]), math.log(3), places=10)

    def test_composite_is_zero(self):
        """T3: Λ(6) = Λ(10) = Λ(15) = 0 (composites with 2+ distinct primes)."""
        for n in (6, 10, 15):
            self.assertAlmostEqual(float(self.lam[n]), 0.0, places=12)

    def test_nonnegative(self):
        """T3: All Λ(n) ≥ 0."""
        self.assertTrue(np.all(self.lam >= 0))


# ---------------------------------------------------------------------------
# T4 — compute_psi
# ---------------------------------------------------------------------------
class TestBridge06ComputePsi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt_ef(3000)

    def test_psi_nonnegative(self):
        """T4: ψ(x) ≥ 0 for x ≥ 2."""
        for x in [10, 50, 100, 500]:
            val = self.mod.compute_psi(float(x), self.lam)
            self.assertGreaterEqual(val, 0.0)

    def test_psi_nondecreasing(self):
        """T4: ψ(x) is non-decreasing (it's a partial sum of non-negative terms)."""
        xs = [10, 20, 30, 50, 100]
        psi_vals = [self.mod.compute_psi(float(x), self.lam) for x in xs]
        for i in range(len(psi_vals) - 1):
            self.assertLessEqual(psi_vals[i], psi_vals[i + 1],
                                 f"ψ not non-decreasing at x={xs[i]}")

    def test_psi_at_2(self):
        """T4: ψ(2) = log(2)."""
        val = self.mod.compute_psi(2.0, self.lam)
        self.assertAlmostEqual(val, math.log(2), places=10)


# ---------------------------------------------------------------------------
# T5 — chebyshev_band_ok
# ---------------------------------------------------------------------------
class TestBridge06ChebyshevBand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt_ef(3000)

    def test_chebyshev_holds_for_moderate_x(self):
        """T5: Chebyshev band 0.9212·x ≤ ψ(x) ≤ 1.1056·x holds for x=100..1000."""
        for x in [100, 200, 500, 1000]:
            result = self.mod.chebyshev_band_ok(float(x), self.lam)
            self.assertTrue(result, f"Chebyshev band failed at x={x}")

    def test_returns_bool(self):
        """T5: chebyshev_band_ok returns a boolean."""
        result = self.mod.chebyshev_band_ok(500.0, self.lam)
        self.assertIsInstance(result, bool)


# ---------------------------------------------------------------------------
# T6 — smeared_prime_sum
# ---------------------------------------------------------------------------
class TestBridge06SmearedSum(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt_ef(3000)

    def test_finite_value(self):
        """T6: smeared_prime_sum returns finite value."""
        for T in [3.0, 4.0, 5.0]:
            val = self.mod.smeared_prime_sum(T, self.lam, sigma=1.0)
            self.assertTrue(math.isfinite(val), f"Non-finite at T={T}")

    def test_positive_at_moderate_T(self):
        """T6: S_prime(T) > 0 for T in range with prime support."""
        val = self.mod.smeared_prime_sum(5.0, self.lam, sigma=1.0)
        self.assertGreater(val, 0.0)

    def test_sigma_values_are_finite_positive(self):
        """T6: smeared_prime_sum returns finite positive values across sigma range."""
        for sigma in (0.5, 1.0, 2.0):
            val = self.mod.smeared_prime_sum(5.0, self.lam, sigma=sigma)
            self.assertTrue(math.isfinite(val), f"Non-finite at sigma={sigma}")
            self.assertGreater(val, 0.0, f"Non-positive at sigma={sigma}")


# ---------------------------------------------------------------------------
# T7 — scaling_test
# ---------------------------------------------------------------------------
class TestBridge06ScalingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_scaling_returns_dict(self):
        """T7: scaling_test returns a dict with N keys."""
        result = self.mod.scaling_test(T=5.0, sigma=1.0,
                                       N_values=(100, 300, 500))
        self.assertIsInstance(result, dict)
        self.assertEqual(set(result.keys()), {100, 300, 500})

    def test_scaling_values_finite(self):
        """T7: All scaling_test values are finite."""
        result = self.mod.scaling_test(T=5.0, sigma=1.0,
                                       N_values=(100, 300, 500))
        for N, val in result.items():
            self.assertTrue(math.isfinite(val), f"Non-finite at N={N}")

    def test_scaling_convergence(self):
        """T7: S_prime converges as N increases (last change < 10%)."""
        result = self.mod.scaling_test(T=5.0, sigma=1.0,
                                       N_values=(500, 1000, 2000, 3000))
        vals = list(result.values())
        last = vals[-1]
        second_last = vals[-2]
        if abs(last) > 1e-30:
            rel_change = abs(last - second_last) / abs(last)
            self.assertLess(rel_change, 0.10,
                            f"S_prime not converging: rel_change = {rel_change:.2%}")


# ---------------------------------------------------------------------------
# T8 — ExplicitFormulaBridge
# ---------------------------------------------------------------------------
class TestBridge06ExplicitFormulaBridge(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_bridge_instantiates(self):
        """T8: ExplicitFormulaBridge instantiates with small parameters."""
        bridge = self.mod.ExplicitFormulaBridge(
            T_range=(3.0, 6.0), num_points=10, sigma=1.0
        )
        self.assertIsNotNone(bridge)

    def test_bridge_prime_side_runs(self):
        """T8: run_prime_side() returns numpy array of correct length."""
        bridge = self.mod.ExplicitFormulaBridge(
            T_range=(3.0, 6.0), num_points=8, sigma=1.0
        )
        S_prime = bridge.run_prime_side()
        self.assertIsInstance(S_prime, np.ndarray)
        self.assertEqual(len(S_prime), 8)

    def test_bridge_ef1_sanity(self):
        """T8: EF1 Chebyshev sanity check returns pass_rate ∈ [0, 1]."""
        bridge = self.mod.ExplicitFormulaBridge(
            T_range=(5.0, 7.0), num_points=10, sigma=1.0
        )
        result = bridge.run_ef1_sanity()
        self.assertIn('pass_rate', result)
        rate = result['pass_rate']
        self.assertGreaterEqual(rate, 0.0)
        self.assertLessEqual(rate, 1.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
