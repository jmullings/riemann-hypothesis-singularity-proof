#!/usr/bin/env python3
"""
test_bridge_08_nyman_beurling.py
==================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/BRIDGES/BRIDGE_8/EXECUTION/BRIDGE_08_NYMAN_BEURLING.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads (self-contained)
    T3 — sieve_mangoldt_nm: von Mangoldt values are correct
    T4 — sieve_mobius: Möbius function values are correct
    T5 — ArithmeticWeights factory: all weight methods return valid arrays
    T6 — T_phi_9D_weighted: output shape and finiteness
    T7 — C_phi_weighted: convexity values are finite
    T8 — ArithmeticNullModelsBridge: instantiation and weight suite

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
BRIDGE_EXEC = ROOT / 'FORMAL_PROOF_NEW' / 'BRIDGES' / 'BRIDGE_8' / 'EXECUTION'
SCRIPT = BRIDGE_EXEC / 'BRIDGE_08_NYMAN_BEURLING.py'


def _load_module():
    p = str(BRIDGE_EXEC)
    if p not in sys.path:
        sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location('BRIDGE_08_NYMAN_BEURLING', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestBridge08Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: BRIDGE_08_NYMAN_BEURLING.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import
# ---------------------------------------------------------------------------
class TestBridge08Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module imports successfully."""
        self.assertIsNotNone(self.mod)

    def test_expected_symbols(self):
        """T2: Key symbols exported."""
        for name in ('sieve_mangoldt_nm', 'sieve_mobius', 'T_phi_9D_weighted',
                     'C_phi_weighted', 'ArithmeticWeights',
                     'ArithmeticNullModelsBridge'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")

    def test_architecture_constants(self):
        """T2: NUM_BRANCHES=9, PROJECTION_DIM=6."""
        self.assertEqual(self.mod.NUM_BRANCHES, 9)
        self.assertEqual(self.mod.PROJECTION_DIM, 6)


# ---------------------------------------------------------------------------
# T3 — sieve_mangoldt_nm
# ---------------------------------------------------------------------------
class TestBridge08SieveMangoldt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt_nm(20)

    def test_length(self):
        """T3: Array length N+1."""
        self.assertEqual(len(self.lam), 21)

    def test_prime_values(self):
        """T3: Λ(p) = log(p) for primes."""
        for p in (2, 3, 5, 7):
            self.assertAlmostEqual(float(self.lam[p]), math.log(p), places=10)

    def test_composite_zero(self):
        """T3: Λ(6) = 0."""
        self.assertAlmostEqual(float(self.lam[6]), 0.0, places=12)

    def test_prime_power(self):
        """T3: Λ(4) = log(2) (prime power)."""
        self.assertAlmostEqual(float(self.lam[4]), math.log(2), places=10)


# ---------------------------------------------------------------------------
# T4 — sieve_mobius
# ---------------------------------------------------------------------------
class TestBridge08SieveMobius(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.mu = cls.mod.sieve_mobius(20)

    def test_length(self):
        """T4: Array length N+1."""
        self.assertEqual(len(self.mu), 21)

    def test_mu_1(self):
        """T4: μ(1) = 1."""
        self.assertEqual(int(self.mu[1]), 1)

    def test_mu_prime(self):
        """T4: μ(p) = -1 for primes p."""
        for p in (2, 3, 5, 7, 11, 13):
            self.assertEqual(int(self.mu[p]), -1, f"μ({p}) should be -1")

    def test_mu_squarefree_product(self):
        """T4: μ(6) = μ(2·3) = 1 (product of 2 distinct primes)."""
        self.assertEqual(int(self.mu[6]), 1)

    def test_mu_prime_square(self):
        """T4: μ(4) = μ(2²) = 0 (has squared factor)."""
        self.assertEqual(int(self.mu[4]), 0)
        self.assertEqual(int(self.mu[9]), 0)

    def test_mu_values_in_minus1_0_1(self):
        """T4: μ(n) ∈ {-1, 0, 1} for all n."""
        for val in self.mu:
            self.assertIn(int(val), (-1, 0, 1))


# ---------------------------------------------------------------------------
# T5 — ArithmeticWeights
# ---------------------------------------------------------------------------
class TestBridge08ArithmeticWeights(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.N = 100
        cls.AW = cls.mod.ArithmeticWeights

    def test_von_mangoldt_nonnegative(self):
        """T5: von_mangoldt weights ≥ 0."""
        w = self.AW.von_mangoldt(self.N)
        self.assertTrue(np.all(w >= 0))

    def test_mobius_abs_binary(self):
        """T5: mobius_abs weights ∈ {0, 1}."""
        w = self.AW.mobius_abs(self.N)
        self.assertTrue(np.all((w == 0) | (w == 1)))

    def test_mobius_signed_in_range(self):
        """T5: mobius_signed weights ∈ {-1, 0, 1}."""
        w = self.AW.mobius_signed(self.N).astype(int)
        self.assertTrue(np.all((w == -1) | (w == 0) | (w == 1)))

    def test_euler_smooth_positive(self):
        """T5: euler_smooth weights w(n) = 1/√n > 0."""
        w = self.AW.euler_smooth(self.N)
        self.assertTrue(np.all(w[1:] > 0))

    def test_shuffled_mangoldt_same_sum(self):
        """T5: shuffled_mangoldt has same sum as von_mangoldt."""
        w_orig = self.AW.von_mangoldt(self.N)
        w_shuf = self.AW.shuffled_mangoldt(self.N, seed=0)
        self.assertAlmostEqual(float(np.sum(w_orig)), float(np.sum(w_shuf)), places=10)


# ---------------------------------------------------------------------------
# T6 — T_phi_9D_weighted
# ---------------------------------------------------------------------------
class TestBridge08TPhiWeighted(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt_nm(3000)

    def test_shape(self):
        """T6: T_phi_9D_weighted returns shape (9,)."""
        vec = self.mod.T_phi_9D_weighted(4.0, self.lam)
        self.assertEqual(vec.shape, (9,))

    def test_finite(self):
        """T6: All entries finite."""
        for T in [3.0, 4.0, 5.0]:
            vec = self.mod.T_phi_9D_weighted(T, self.lam)
            self.assertTrue(np.all(np.isfinite(vec)))

    def test_nonzero(self):
        """T6: Vector non-zero for T values with prime support."""
        vec = self.mod.T_phi_9D_weighted(5.0, self.lam)
        self.assertGreater(np.linalg.norm(vec), 1e-15)


# ---------------------------------------------------------------------------
# T7 — C_phi_weighted
# ---------------------------------------------------------------------------
class TestBridge08CPhiWeighted(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.lam = cls.mod.sieve_mangoldt_nm(3000)
        cls.P6 = cls.mod.build_P6_static_nm()

    def test_finite(self):
        """T7: C_phi_weighted returns finite value."""
        val = self.mod.C_phi_weighted(4.5, 0.1, self.lam, self.P6)
        self.assertTrue(math.isfinite(val))

    def test_symmetric_h(self):
        """T7: C_phi_weighted is symmetric under h → -h."""
        v1 = self.mod.C_phi_weighted(4.5, 0.1, self.lam, self.P6)
        v2 = self.mod.C_phi_weighted(4.5, -0.1, self.lam, self.P6)
        self.assertAlmostEqual(v1, v2, places=10)


# ---------------------------------------------------------------------------
# T8 — ArithmeticNullModelsBridge
# ---------------------------------------------------------------------------
class TestBridge08NullModelsBridge(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_bridge_instantiates(self):
        """T8: ArithmeticNullModelsBridge instantiates."""
        bridge = self.mod.ArithmeticNullModelsBridge(
            T_range=(14.0, 50.0), num_points=20, h=0.05, N=300
        )
        self.assertIsNotNone(bridge)

    def test_bridge_build_weight_suite(self):
        """T8: build_weight_suite returns a non-empty dict of (weights, desc, is_arith) tuples."""
        bridge = self.mod.ArithmeticNullModelsBridge(
            T_range=(14.0, 30.0), num_points=10, h=0.05, N=200
        )
        suite = bridge.build_weight_suite()
        self.assertIsInstance(suite, dict)
        self.assertGreater(len(suite), 0)
        # Each value is a 3-tuple: (weights, description, is_arithmetic)
        for name, entry in suite.items():
            self.assertEqual(len(entry), 3)
            weights, desc, is_arith = entry
            self.assertIsNotNone(weights)
            self.assertIsInstance(desc, str)
            self.assertIsInstance(is_arith, bool)

    def test_weight_suite_has_mangoldt(self):
        """T8: Weight suite includes the von Mangoldt weight keyed as 'Λ(n)'."""
        bridge = self.mod.ArithmeticNullModelsBridge(
            T_range=(14.0, 30.0), num_points=10, h=0.05, N=200
        )
        suite = bridge.build_weight_suite()
        # von Mangoldt key is 'Λ(n)'
        self.assertIn('Λ(n)', suite)


if __name__ == '__main__':
    unittest.main(verbosity=2)
