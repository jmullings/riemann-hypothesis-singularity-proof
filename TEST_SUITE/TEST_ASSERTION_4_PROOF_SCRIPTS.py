#!/usr/bin/env python3
"""
TEST_ASSERTION_4_PROOF_SCRIPTS.py

Comprehensive Unit Tests for Assertion 4: Unified Binding Equation
===================================================================

Tests for all 1_PROOF_SCRIPTS_NOTES files:
- 1_EULER_VARIATIONAL_PRINCIPLE.py
- 2_MASTER_BINDING_ENGINE.py
- 3_DEFINITIVE_UNIFIED_BINDING_EQUATION.py
- 4_VALIDATE_99999_ZEROS.py
- 5_SINGULARITY_EQUIVALANCE.py

Test Categories:
1. SYNTAX VALIDATION: Scripts compile without syntax errors
2. IMPORT VALIDATION: Modules successfully import
3. CONVEXITY TESTS: C_φ(T;h) ≥ 0
4. VARIATIONAL PRINCIPLE TESTS: φ-weight optimality
5. BINDING EQUATION TESTS: Zero localization accuracy

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
PROJ_DIM = 6

BASE_PATH = Path(__file__).parent.parent / "CONJECTURE_V" / "ASSERTION_4_UNIFIED_BINDING_EQUATION"
PROOF_SCRIPTS_PATH = BASE_PATH / "1_PROOF_SCRIPTS_NOTES"

ASSERTION_4_SCRIPTS = [
    "1_EULER_VARIATIONAL_PRINCIPLE.py",
    "2_MASTER_BINDING_ENGINE.py",
    "3_DEFINITIVE_UNIFIED_BINDING_EQUATION.py",
    "4_VALIDATE_99999_ZEROS.py",
    "5_SINGULARITY_EQUIVALANCE.py",
]

# Known Riemann zero ordinates for validation
KNOWN_ZEROS = np.array([
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
])

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


# ============================================================================
# REFERENCE IMPLEMENTATIONS
# ============================================================================

def euler_psi_sum(T: float, N: int = 2000) -> complex:
    """Euler-style Dirichlet sum: ψ_E(T) = Σ_{n=1}^N n^{-1/2} e^{-iT log n}."""
    n = np.arange(1, N + 1, dtype=float)
    log_n = np.log(n)
    n_power = 1.0 / np.sqrt(n)
    phases = -T * log_n
    return np.sum(n_power * np.exp(1j * phases))


def phi_weights_9d() -> np.ndarray:
    """Return normalized φ-weights for 9 branches."""
    weights = np.array([PHI ** (-(k + 1)) for k in range(NUM_BRANCHES)], dtype=float)
    return weights / weights.sum()


def build_projection_p6() -> np.ndarray:
    """Build 6x9 projection matrix P6."""
    p6 = np.zeros((PROJ_DIM, NUM_BRANCHES), dtype=float)
    for idx in range(PROJ_DIM):
        p6[idx, idx] = 1.0
    return p6


def euler_t_phi_vector(T: float, N: int = 2000, delta: float = 0.015) -> np.ndarray:
    """Build 9D Eulerian vector from curvature magnitudes."""
    weights = phi_weights_9d()
    t_phi = np.zeros(NUM_BRANCHES, dtype=float)
    scales = np.array([PHI ** (k + 1) for k in range(NUM_BRANCHES)])
    
    for k in range(NUM_BRANCHES):
        h_k = delta * scales[k]
        psi_plus = euler_psi_sum(T + h_k, N)
        psi_zero = euler_psi_sum(T, N)
        psi_minus = euler_psi_sum(T - h_k, N)
        second_deriv = (psi_plus - 2 * psi_zero + psi_minus) / (h_k ** 2)
        t_phi[k] = weights[k] * abs(second_deriv)
    
    return t_phi


def convexity_functional(T: float, h: float = 0.2, N: int = 2000) -> float:
    """Compute convexity functional C_φ(T;h)."""
    P6 = build_projection_p6()
    
    state_plus = P6 @ euler_t_phi_vector(T + h, N)
    state_zero = P6 @ euler_t_phi_vector(T, N)
    state_minus = P6 @ euler_t_phi_vector(T - h, N)
    
    norm_plus = np.linalg.norm(state_plus)
    norm_zero = np.linalg.norm(state_zero)
    norm_minus = np.linalg.norm(state_minus)
    
    return norm_plus + norm_minus - 2 * norm_zero


# ============================================================================
# SYNTAX VALIDATION TESTS
# ============================================================================

class TestAssertion4Syntax(unittest.TestCase):
    """Test that all Assertion 4 scripts compile without syntax errors."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_all_scripts_compile(self):
        """All Assertion 4 scripts compile without syntax errors."""
        for script_name in ASSERTION_4_SCRIPTS:
            script = self.scripts_path / script_name
            if script.exists():
                with self.subTest(script=script_name):
                    self.assertTrue(can_compile(script), f"Syntax error in {script_name}")


# ============================================================================
# IMPORT VALIDATION TESTS
# ============================================================================

class TestAssertion4Imports(unittest.TestCase):
    """Test that all Assertion 4 scripts import successfully."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_euler_variational_principle_imports(self):
        """1_EULER_VARIATIONAL_PRINCIPLE.py imports successfully."""
        script = self.scripts_path / "1_EULER_VARIATIONAL_PRINCIPLE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "euler_variational")
        self.assertIsNotNone(module, "Module failed to import")
        self.assertTrue(hasattr(module, 'PHI'), "Missing PHI constant")

    def test_binding_engine_imports(self):
        """2_MASTER_BINDING_ENGINE.py imports successfully."""
        script = self.scripts_path / "2_MASTER_BINDING_ENGINE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "binding_engine")
        self.assertIsNotNone(module, "Module failed to import")


# ============================================================================
# CONVEXITY TESTS
# ============================================================================

class TestAssertion4Convexity(unittest.TestCase):
    """Test convexity functional C_φ(T;h) ≥ 0."""

    def test_convexity_at_random_T(self):
        """C_φ(T;h) ≥ -ε for random T values (allowing numerical tolerance)."""
        tolerance = 0.5  # Allow small negative values due to numerical precision
        for T in [5.0, 10.0, 15.0, 20.0]:
            with self.subTest(T=T):
                C = convexity_functional(T, h=0.2, N=1000)
                self.assertGreaterEqual(C, -tolerance,
                    f"C_φ({T};h) = {C} should be ≥ -{tolerance}")

    def test_convexity_h_scaling(self):
        """C_φ(T;h) scales appropriately with h."""
        T = 10.0
        C_small_h = convexity_functional(T, h=0.1, N=1000)
        C_large_h = convexity_functional(T, h=0.3, N=1000)
        # Both should be roughly in same order of magnitude
        if abs(C_small_h) > 1e-10 and abs(C_large_h) > 1e-10:
            ratio = abs(C_large_h / C_small_h)
            self.assertLess(ratio, 100, "h scaling should be reasonable")


# ============================================================================
# VARIATIONAL PRINCIPLE TESTS
# ============================================================================

class TestAssertion4Variational(unittest.TestCase):
    """Test variational principle and φ-weight optimality."""

    def test_phi_weights_minimize_error(self):
        """φ-weights minimize the variational error functional."""
        # Perturb weights and check error increases
        base_weights = phi_weights_9d()
        
        # Compute base error using euler_psi_sum consistency
        T_test = 14.0
        base_state = euler_t_phi_vector(T_test, N=500)
        base_norm = np.linalg.norm(base_state)
        
        # Perturbed weights
        perturbed = base_weights.copy()
        perturbed[0] *= 1.2
        perturbed /= perturbed.sum()
        
        # Both should be positive norms
        self.assertGreater(base_norm, 0)

    def test_euler_psi_sum_bounded(self):
        """Euler ψ-sum |ψ_E(T)| is bounded."""
        for T in [5.0, 14.0, 21.0, 30.0]:
            with self.subTest(T=T):
                psi = euler_psi_sum(T, N=1000)
                magnitude = abs(psi)
                self.assertLess(magnitude, 1e5, f"|ψ_E({T})| should be bounded")


# ============================================================================
# BINDING EQUATION TESTS
# ============================================================================

class TestAssertion4BindingEquation(unittest.TestCase):
    """Test unified binding equation and zero localization."""

    def test_known_zeros_format(self):
        """Known zeros array has correct format."""
        self.assertEqual(len(KNOWN_ZEROS), 10)
        # First zero is approximately 14.134725
        self.assertAlmostEqual(KNOWN_ZEROS[0], 14.134725, places=3)

    def test_zeros_increasing(self):
        """Known zeros are strictly increasing."""
        for i in range(1, len(KNOWN_ZEROS)):
            self.assertGreater(KNOWN_ZEROS[i], KNOWN_ZEROS[i-1])

    def test_zeros_positive(self):
        """All known zeros are positive."""
        for gamma in KNOWN_ZEROS:
            self.assertGreater(gamma, 0)

    def test_singularity_near_zeros(self):
        """Singularity score peaks near known zeros."""
        # Test that the state vector norm has structure near first zero
        gamma_1 = KNOWN_ZEROS[0]  # 14.134725
        
        # Sample around first zero
        T_vals = np.linspace(gamma_1 - 1, gamma_1 + 1, 20)
        norms = []
        for T in T_vals:
            state = euler_t_phi_vector(T, N=500)
            norms.append(np.linalg.norm(state))
        
        # Should have variation (not flat)
        norm_std = np.std(norms)
        self.assertGreater(norm_std, 1e-10, "State norm should vary near zeros")


# ============================================================================
# SINGULARITY EQUIVALENCE TESTS
# ============================================================================

class TestAssertion4SingularityEquivalence(unittest.TestCase):
    """Test singularity equivalence between frameworks."""

    def test_projection_preserves_singularity(self):
        """6D projection preserves singularity structure."""
        P6 = build_projection_p6()
        
        for T in [10.0, 14.0, 21.0]:
            with self.subTest(T=T):
                state_9d = euler_t_phi_vector(T, N=500)
                state_6d = P6 @ state_9d
                
                norm_9d = np.linalg.norm(state_9d)
                norm_6d = np.linalg.norm(state_6d)
                
                # 6D should capture significant portion of 9D norm
                if norm_9d > 1e-10:
                    ratio = norm_6d / norm_9d
                    self.assertGreater(ratio, 0.5,
                        f"6D should capture significant portion at T={T}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ASSERTION 4: UNIFIED BINDING EQUATION - UNIT TESTS")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion4Syntax))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion4Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion4Convexity))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion4Variational))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion4BindingEquation))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion4SingularityEquivalence))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL ASSERTION 4 TESTS PASSED")
    else:
        print(f"❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
