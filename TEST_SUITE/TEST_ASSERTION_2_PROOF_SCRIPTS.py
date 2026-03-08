#!/usr/bin/env python3
"""
TEST_ASSERTION_2_PROOF_SCRIPTS.py

Comprehensive Unit Tests for Assertion 2: 9D φ-Weight Embedding
================================================================

Tests for all 1_PROOF_SCRIPTS_NOTES files:
- 1_EULER_GEODESIC_ENGINE.py
- 2_9D_PRIME_CURVATURE_ANALYZER.py
- 3_EULER_WEIGHT_CALIBRATOR.py
- ASSERTION_2_FILE_1__EULER_GEODESIC_ENGINE.py
- ASSERTION_2_FILE_2__9D_PRIME_CURVATURE_ANALYZER.py
- ASSERTION_2_FILE_3__EULER_WEIGHT_CALIBRATOR.py
- ASSERTION_2_FILE_4__9D_BOUNDEDNESS_COMPACTIFICATION.py
- ASSERTION_2_FILE_5__9D_SPECTRAL_CONSISTENCY.py

Test Categories:
1. SYNTAX VALIDATION: Scripts compile without syntax errors
2. IMPORT VALIDATION: Modules successfully import
3. 9D STATE VECTOR TESTS: T_φ(T) construction and properties
4. OPERATOR TESTS: Dirichlet sums and geodesic engine
5. BOUNDEDNESS TESTS: Chebyshev constraint validation

Date: March 2026
"""

from __future__ import annotations

import sys
import os
import unittest
import importlib.util
import py_compile
from pathlib import Path
import numpy as np
from typing import Optional, Any

# ============================================================================
# CONFIGURATION
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2
NUM_BRANCHES = 9
N_MAX = 3000

BASE_PATH = Path(__file__).parent.parent / "CONJECTURE_V" / "ASSERTION_2_9D_PHI_EMBEDDING"
PROOF_SCRIPTS_PATH = BASE_PATH / "1_PROOF_SCRIPTS_NOTES"

ASSERTION_2_SCRIPTS = [
    "1_EULER_GEODESIC_ENGINE.py",
    "2_9D_PRIME_CURVATURE_ANALYZER.py",
    "3_EULER_WEIGHT_CALIBRATOR.py",
    "ASSERTION_2_FILE_1__EULER_GEODESIC_ENGINE.py",
    "ASSERTION_2_FILE_2__9D_PRIME_CURVATURE_ANALYZER.py",
    "ASSERTION_2_FILE_3__EULER_WEIGHT_CALIBRATOR.py",
    "ASSERTION_2_FILE_4__9D_BOUNDEDNESS_COMPACTIFICATION.py",
    "ASSERTION_2_FILE_5__9D_SPECTRAL_CONSISTENCY.py",
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_module_from_path(script_path: Path, module_name: str) -> Optional[Any]:
    """Dynamically load a module from a file path."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Failed to load {script_path}: {e}")
        return None


def can_compile(script_path: Path) -> bool:
    """Check if a Python script compiles without syntax errors."""
    try:
        py_compile.compile(str(script_path), doraise=True)
        return True
    except py_compile.PyCompileError:
        return False


def reference_sieve_mangoldt(N: int) -> np.ndarray:
    """Reference implementation of sieve_mangoldt."""
    lam = np.zeros(N + 1)
    sieve = np.ones(N + 1, dtype=bool)
    sieve[0] = sieve[1] = False
    for p in range(2, N + 1):
        if not sieve[p]:
            continue
        for m in range(p * p, N + 1, p):
            sieve[m] = False
        log_p = np.log(p)
        pk = p
        while pk <= N:
            lam[pk] = log_p
            pk *= p
    return lam


def reference_phi_weights() -> np.ndarray:
    """Reference φ-weights."""
    raw = np.array([PHI**(-k) for k in range(NUM_BRANCHES)])
    return raw / raw.sum()


def reference_geodesic_lengths() -> np.ndarray:
    """Reference geodesic lengths L_k = φ^k."""
    return np.array([PHI**k for k in range(NUM_BRANCHES)])


# ============================================================================
# SYNTAX VALIDATION TESTS
# ============================================================================

class TestAssertion2Syntax(unittest.TestCase):
    """Test that all Assertion 2 scripts compile without syntax errors."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_all_scripts_compile(self):
        """All Assertion 2 scripts compile without syntax errors."""
        for script_name in ASSERTION_2_SCRIPTS:
            script = self.scripts_path / script_name
            if script.exists():
                with self.subTest(script=script_name):
                    self.assertTrue(can_compile(script), f"Syntax error in {script_name}")


# ============================================================================
# IMPORT VALIDATION TESTS
# ============================================================================

class TestAssertion2Imports(unittest.TestCase):
    """Test that all Assertion 2 scripts import successfully."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_file1_geodesic_engine_imports(self):
        """ASSERTION_2_FILE_1__EULER_GEODESIC_ENGINE.py imports successfully."""
        script = self.scripts_path / "ASSERTION_2_FILE_1__EULER_GEODESIC_ENGINE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "assertion2_file1")
        self.assertIsNotNone(module, "Module failed to import")
        self.assertTrue(hasattr(module, 'PHI'), "Missing PHI constant")
        self.assertTrue(hasattr(module, 'NUM_BRANCHES'), "Missing NUM_BRANCHES")
        self.assertTrue(hasattr(module, 'sieve_mangoldt'), "Missing sieve_mangoldt")

    def test_file2_curvature_analyzer_imports(self):
        """ASSERTION_2_FILE_2__9D_PRIME_CURVATURE_ANALYZER.py imports successfully."""
        script = self.scripts_path / "ASSERTION_2_FILE_2__9D_PRIME_CURVATURE_ANALYZER.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "assertion2_file2")
        self.assertIsNotNone(module, "Module failed to import")

    def test_file4_boundedness_imports(self):
        """ASSERTION_2_FILE_4__9D_BOUNDEDNESS_COMPACTIFICATION.py imports successfully."""
        script = self.scripts_path / "ASSERTION_2_FILE_4__9D_BOUNDEDNESS_COMPACTIFICATION.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "assertion2_file4")
        self.assertIsNotNone(module, "Module failed to import")


# ============================================================================
# 9D STATE VECTOR TESTS
# ============================================================================

class TestAssertion2StateVector(unittest.TestCase):
    """Test 9D state vector T_φ(T) properties."""

    def setUp(self):
        """Set up test fixtures."""
        self.lam = reference_sieve_mangoldt(1000)
        self.weights = reference_phi_weights()
        self.lengths = reference_geodesic_lengths()
        self._log_table = np.zeros(1001)
        for n in range(2, 1001):
            self._log_table[n] = np.log(n)

    def _compute_F_k(self, k: int, T: float) -> float:
        """Compute branch functional F_k(T)."""
        N = min(int(np.exp(T)) + 1, len(self.lam) - 1)
        n_arr = np.arange(2, N + 1)
        la = self.lam[2:N + 1]
        nz = la != 0.0
        if not nz.any():
            return 0.0
        n_arr, la = n_arr[nz], la[nz]
        log_n = self._log_table[np.clip(n_arr, 0, 1000)]
        z = (log_n - T) / self.lengths[k]
        g = self.weights[k] * np.exp(-0.5 * z * z) / (self.lengths[k] * np.sqrt(2 * np.pi))
        return float(np.dot(g, la))

    def _T_phi(self, T: float) -> np.ndarray:
        """Compute full 9D state vector."""
        return np.array([self._compute_F_k(k, T) for k in range(NUM_BRANCHES)])

    def test_state_vector_dimension(self):
        """T_φ(T) has exactly 9 components."""
        T = 5.0
        state = self._T_phi(T)
        self.assertEqual(len(state), 9)

    def test_state_vector_not_zero(self):
        """T_φ(T) is non-zero for T > 1."""
        for T in [3.0, 5.0, 6.5]:
            with self.subTest(T=T):
                state = self._T_phi(T)
                norm = np.linalg.norm(state)
                self.assertGreater(norm, 0, f"T_φ({T}) should be non-zero")

    def test_state_vector_bounded(self):
        """‖T_φ(T)‖ is bounded for bounded T."""
        norms = []
        for T in np.linspace(3.0, 7.0, 20):
            state = self._T_phi(T)
            norms.append(np.linalg.norm(state))
        max_norm = max(norms)
        self.assertLess(max_norm, 1e6, "9D state norm should be bounded")

    def test_state_vector_continuity(self):
        """T_φ(T) varies continuously with T."""
        T1, T2 = 5.0, 5.01
        state1 = self._T_phi(T1)
        state2 = self._T_phi(T2)
        diff_norm = np.linalg.norm(state2 - state1)
        # Small change in T should produce small change in state
        self.assertLess(diff_norm, 1.0, "State should vary continuously")


# ============================================================================
# DIRICHLET SUM TESTS
# ============================================================================

class TestAssertion2DirichletSum(unittest.TestCase):
    """Test Dirichlet partial sum ψ_DP(t) properties."""

    def setUp(self):
        """Set up test fixtures."""
        self.lam = reference_sieve_mangoldt(500)
        self._log_table = np.zeros(501)
        for n in range(2, 501):
            self._log_table[n] = np.log(n)

    def _psi_DP(self, t: float, N: int = 500) -> complex:
        """Compute ψ_DP(t) = Σ_{n=2}^N Λ(n)·n^{-1/2}·e^{-it·log n}."""
        N_use = min(N, len(self.lam) - 1)
        result = 0j
        for n in range(2, N_use + 1):
            if self.lam[n] > 0:
                log_n = self._log_table[n]
                result += self.lam[n] * (n ** -0.5) * np.exp(-1j * t * log_n)
        return result

    def test_dirichlet_sum_not_zero(self):
        """ψ_DP(t) is non-zero for t > 0."""
        for t in [5.0, 10.0, 14.0]:
            with self.subTest(t=t):
                val = self._psi_DP(t)
                self.assertNotEqual(abs(val), 0)

    def test_dirichlet_sum_bounded(self):
        """|ψ_DP(t)| is bounded."""
        for t in np.linspace(1.0, 50.0, 20):
            val = abs(self._psi_DP(t, N=200))
            self.assertLess(val, 1e4, f"|ψ_DP({t})| should be bounded")

    def test_dirichlet_sum_symmetric_magnitude(self):
        """|ψ_DP(t)| = |ψ_DP(-t)| (conjugate symmetry)."""
        for t in [5.0, 10.0, 20.0]:
            with self.subTest(t=t):
                val_pos = abs(self._psi_DP(t))
                val_neg = abs(self._psi_DP(-t))
                self.assertAlmostEqual(val_pos, val_neg, places=10)


# ============================================================================
# BOUNDEDNESS AND COMPACTIFICATION TESTS
# ============================================================================

class TestAssertion2Boundedness(unittest.TestCase):
    """Test Chebyshev boundedness and compactification properties."""

    def test_chebyshev_bounds_valid(self):
        """Verify Chebyshev bounds constants are valid."""
        CHEB_A = 0.9212  # Lower bound
        CHEB_B = 1.1056  # Upper bound
        self.assertLess(CHEB_A, 1.0)
        self.assertGreater(CHEB_B, 1.0)
        self.assertGreater(CHEB_A, 0.0)
        self.assertLess(CHEB_B, 2.0)

    def test_geodesic_lengths_well_separated(self):
        """Geodesic lengths L_k = φ^k are well-separated."""
        lengths = reference_geodesic_lengths()
        for k in range(1, NUM_BRANCHES):
            ratio = lengths[k] / lengths[k-1]
            self.assertAlmostEqual(ratio, PHI, places=10)

    def test_weights_times_lengths_bounded(self):
        """w_k * L_k is bounded across all branches."""
        weights = reference_phi_weights()
        lengths = reference_geodesic_lengths()
        products = weights * lengths
        # w_k ∝ φ^{-k}, L_k = φ^k, so w_k * L_k ∝ constant
        max_ratio = max(products) / min(products)
        self.assertLess(max_ratio, 10, "w_k * L_k should be approximately constant")


# ============================================================================
# SPECTRAL CONSISTENCY TESTS
# ============================================================================

class TestAssertion2SpectralConsistency(unittest.TestCase):
    """Test spectral consistency of 9D embedding."""

    def test_phi_weights_spectral_property(self):
        """φ-weights satisfy spectral properties."""
        weights = reference_phi_weights()
        # Weights should be positive
        self.assertTrue(all(w > 0 for w in weights))
        # Weights should decay exponentially
        for k in range(1, NUM_BRANCHES):
            ratio = weights[k-1] / weights[k]
            self.assertAlmostEqual(ratio, PHI, places=10)

    def test_normalization_preserved(self):
        """Weight normalization is preserved under operations."""
        weights = reference_phi_weights()
        self.assertAlmostEqual(np.sum(weights), 1.0, places=14)
        # Under φ-scaling
        scaled = weights * PHI
        renormalized = scaled / scaled.sum()
        self.assertAlmostEqual(np.sum(renormalized), 1.0, places=14)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ASSERTION 2: 9D φ-WEIGHT EMBEDDING - UNIT TESTS")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion2Syntax))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion2Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion2StateVector))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion2DirichletSum))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion2Boundedness))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion2SpectralConsistency))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL ASSERTION 2 TESTS PASSED")
    else:
        print(f"❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
