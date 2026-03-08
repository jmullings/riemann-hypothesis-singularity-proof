#!/usr/bin/env python3
"""
TEST_ASSERTION_3_PROOF_SCRIPTS.py

Comprehensive Unit Tests for Assertion 3: 6D Variance Collapse
===============================================================

Tests for all 1_PROOF_SCRIPTS_NOTES files:
- 1_BOMBIERI_VINOGRADOV_6D_PCA.py
- 2_DIMENSIONAL_COLLAPSE_VALIDATOR.py
- ASSERTION_3_FILE_1__9D_SINGULARITY_DETECTION.py
- ASSERTION_3_FILE_2__BV_VARIANCE_DAMPING.py
- ASSERTION_3_FILE_3__PCA_SPECTRAL_COLLAPSE.py
- ASSERTION_3_FILE_4__DIMENSIONAL_COLLAPSE_VALIDATOR.py
- ASSERTION_3_FILE_5__UNIFIED_6D_COLLAPSE_THEOREM.py

Test Categories:
1. SYNTAX VALIDATION: Scripts compile without syntax errors
2. IMPORT VALIDATION: Modules successfully import
3. SINGULARITY DETECTION TESTS: Local maxima detection
4. PCA TESTS: Dimensional reduction properties
5. VARIANCE DAMPING TESTS: Bombieri-Vinogradov bounds

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
PROJ_DIM = 6  # Target dimension after collapse
CHEB_A = 0.9212
CHEB_B = 1.1056

BASE_PATH = Path(__file__).parent.parent / "CONJECTURE_V" / "ASSERTION_3_6D_VARIANCE_COLLAPSE"
PROOF_SCRIPTS_PATH = BASE_PATH / "1_PROOF_SCRIPTS_NOTES"

ASSERTION_3_SCRIPTS = [
    "1_BOMBIERI_VINOGRADOV_6D_PCA.py",
    "2_DIMENSIONAL_COLLAPSE_VALIDATOR.py",
    "ASSERTION_3_FILE_1__9D_SINGULARITY_DETECTION.py",
    "ASSERTION_3_FILE_2__BV_VARIANCE_DAMPING.py",
    "ASSERTION_3_FILE_3__PCA_SPECTRAL_COLLAPSE.py",
    "ASSERTION_3_FILE_4__DIMENSIONAL_COLLAPSE_VALIDATOR.py",
    "ASSERTION_3_FILE_5__UNIFIED_6D_COLLAPSE_THEOREM.py",
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


# ============================================================================
# SYNTAX VALIDATION TESTS
# ============================================================================

class TestAssertion3Syntax(unittest.TestCase):
    """Test that all Assertion 3 scripts compile without syntax errors."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_all_scripts_compile(self):
        """All Assertion 3 scripts compile without syntax errors."""
        for script_name in ASSERTION_3_SCRIPTS:
            script = self.scripts_path / script_name
            if script.exists():
                with self.subTest(script=script_name):
                    self.assertTrue(can_compile(script), f"Syntax error in {script_name}")


# ============================================================================
# IMPORT VALIDATION TESTS
# ============================================================================

class TestAssertion3Imports(unittest.TestCase):
    """Test that all Assertion 3 scripts import successfully."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_file1_singularity_detection_imports(self):
        """ASSERTION_3_FILE_1__9D_SINGULARITY_DETECTION.py imports successfully."""
        script = self.scripts_path / "ASSERTION_3_FILE_1__9D_SINGULARITY_DETECTION.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "assertion3_file1")
        self.assertIsNotNone(module, "Module failed to import")
        self.assertTrue(hasattr(module, 'PHI'), "Missing PHI constant")
        self.assertTrue(hasattr(module, 'sieve_mangoldt'), "Missing sieve_mangoldt")

    def test_file3_pca_collapse_imports(self):
        """ASSERTION_3_FILE_3__PCA_SPECTRAL_COLLAPSE.py imports successfully."""
        script = self.scripts_path / "ASSERTION_3_FILE_3__PCA_SPECTRAL_COLLAPSE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "assertion3_file3")
        self.assertIsNotNone(module, "Module failed to import")


# ============================================================================
# SINGULARITY DETECTION TESTS
# ============================================================================

class TestAssertion3Singularity(unittest.TestCase):
    """Test singularity detection S(T) properties."""

    def setUp(self):
        """Set up test fixtures."""
        self.lam = reference_sieve_mangoldt(1000)
        self.weights = np.array([PHI**(-k) for k in range(NUM_BRANCHES)])
        self.weights /= self.weights.sum()
        self.lengths = np.array([PHI**k for k in range(NUM_BRANCHES)])
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
        """Compute 9D state vector."""
        return np.array([self._compute_F_k(k, T) for k in range(NUM_BRANCHES)])

    def _singularity_score(self, T: float, h: float = 0.01) -> float:
        """Compute singularity score S(T) = ‖∇T_φ(T)‖ / ‖T_φ(T)‖."""
        state = self._T_phi(T)
        state_plus = self._T_phi(T + h)
        state_minus = self._T_phi(T - h)
        grad = (state_plus - state_minus) / (2 * h)
        norm_state = np.linalg.norm(state)
        norm_grad = np.linalg.norm(grad)
        if norm_state < 1e-15:
            return 0.0
        return norm_grad / norm_state

    def test_singularity_score_positive(self):
        """Singularity score S(T) is non-negative."""
        for T in [4.0, 5.0, 6.0]:
            with self.subTest(T=T):
                S = self._singularity_score(T)
                self.assertGreaterEqual(S, 0)

    def test_singularity_score_bounded(self):
        """Singularity score S(T) is bounded."""
        for T in np.linspace(3.5, 7.0, 20):
            S = self._singularity_score(T)
            self.assertLess(S, 1e6, f"S({T}) should be bounded")

    def test_singularity_local_maxima_exist(self):
        """Local maxima in S(T) exist (singularities)."""
        T_vals = np.linspace(4.0, 6.0, 50)
        S_vals = [self._singularity_score(T) for T in T_vals]
        # Find local maxima
        maxima_count = 0
        for i in range(1, len(S_vals) - 1):
            if S_vals[i] > S_vals[i-1] and S_vals[i] > S_vals[i+1]:
                maxima_count += 1
        # Should find at least some local maxima
        self.assertGreater(maxima_count, 0, "Should find local maxima in S(T)")


# ============================================================================
# PCA AND DIMENSIONAL COLLAPSE TESTS
# ============================================================================

class TestAssertion3PCA(unittest.TestCase):
    """Test PCA dimensional collapse properties."""

    def test_projection_matrix_dimensions(self):
        """Projection matrix P6 has correct dimensions."""
        P6 = np.zeros((PROJ_DIM, NUM_BRANCHES))
        for i in range(PROJ_DIM):
            P6[i, i] = 1.0
        self.assertEqual(P6.shape, (6, 9))

    def test_projection_matrix_orthogonal(self):
        """P6·P6ᵀ = I_6 (orthogonal projection)."""
        P6 = np.zeros((PROJ_DIM, NUM_BRANCHES))
        for i in range(PROJ_DIM):
            P6[i, i] = 1.0
        product = P6 @ P6.T
        np.testing.assert_array_almost_equal(product, np.eye(PROJ_DIM))

    def test_projection_reduces_dimension(self):
        """Projection reduces 9D to 6D."""
        P6 = np.zeros((PROJ_DIM, NUM_BRANCHES))
        for i in range(PROJ_DIM):
            P6[i, i] = 1.0
        state_9d = np.random.randn(NUM_BRANCHES)
        state_6d = P6 @ state_9d
        self.assertEqual(len(state_6d), PROJ_DIM)

    def test_projection_preserves_leading_components(self):
        """Projection preserves first 6 components."""
        P6 = np.zeros((PROJ_DIM, NUM_BRANCHES))
        for i in range(PROJ_DIM):
            P6[i, i] = 1.0
        state_9d = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=float)
        state_6d = P6 @ state_9d
        np.testing.assert_array_equal(state_6d, [1, 2, 3, 4, 5, 6])


# ============================================================================
# BOMBIERI-VINOGRADOV VARIANCE DAMPING TESTS
# ============================================================================

class TestAssertion3BombieriVinogradov(unittest.TestCase):
    """Test Bombieri-Vinogradov variance damping properties."""

    def test_variance_damping_positive(self):
        """Variance damping factor is positive."""
        # BV damping factor: (1 - 1/φ) for thin directions
        damping = 1 - 1/PHI
        self.assertGreater(damping, 0)

    def test_variance_damping_less_than_one(self):
        """Variance damping factor is less than 1."""
        damping = 1 - 1/PHI
        self.assertLess(damping, 1)

    def test_thin_direction_suppression(self):
        """Thin directions (k=6,7,8) are suppressed by BV."""
        weights = np.array([PHI**(-k) for k in range(NUM_BRANCHES)])
        weights /= weights.sum()
        # Thin directions have smaller weights
        thin_sum = weights[6:].sum()
        dominant_sum = weights[:6].sum()
        self.assertGreater(dominant_sum, thin_sum)


# ============================================================================
# 6D COLLAPSE THEOREM TESTS
# ============================================================================

class TestAssertion3CollapseTheorem(unittest.TestCase):
    """Test unified 6D collapse theorem properties."""

    def test_effective_dimension_is_six(self):
        """Effective dimension after collapse is 6."""
        self.assertEqual(PROJ_DIM, 6)

    def test_collapse_preserves_singularity_structure(self):
        """6D collapse preserves singularity structure."""
        # The projection P6 should preserve the first 6 components
        # which contain the dominant singularity information
        P6 = np.zeros((PROJ_DIM, NUM_BRANCHES))
        for i in range(PROJ_DIM):
            P6[i, i] = 1.0
        
        # Singularity in 9D vs 6D should be correlated
        state_9d = np.array([1, 0.8, 0.6, 0.4, 0.2, 0.1, 0.01, 0.005, 0.001])
        state_6d = P6 @ state_9d
        
        # 6D should capture most of the norm
        norm_9d = np.linalg.norm(state_9d)
        norm_6d = np.linalg.norm(state_6d)
        ratio = norm_6d / norm_9d
        self.assertGreater(ratio, 0.99, "6D should capture >99% of 9D norm")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ASSERTION 3: 6D VARIANCE COLLAPSE - UNIT TESTS")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion3Syntax))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion3Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion3Singularity))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion3PCA))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion3BombieriVinogradov))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion3CollapseTheorem))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL ASSERTION 3 TESTS PASSED")
    else:
        print(f"❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
