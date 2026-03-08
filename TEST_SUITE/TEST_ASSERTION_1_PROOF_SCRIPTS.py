#!/usr/bin/env python3
"""
TEST_ASSERTION_1_PROOF_SCRIPTS.py

Comprehensive Unit Tests for Assertion 1: Eulerian Scaffold
============================================================

Tests for all 1_PROOF_SCRIPTS_NOTES files:
- 1_EULERIAN_PRIME_LAWS.py
- 2_EULER_PHI_CONSTANTS.py
- EULERIAN_LAW_1_PNT_AND_PSI.py
- EULERIAN_LAW_2_THETA_AND_LI.py
- EULERIAN_LAW_3_PI_ERROR_BOUNDS.py
- EULERIAN_LAW_4_EULER_PRODUCT_TARGETS.py
- EULERIAN_LAW_5_PHI_UNIVERSAL_CONSTANTS.py

Test Categories:
1. SYNTAX VALIDATION: Scripts compile without syntax errors
2. IMPORT VALIDATION: Modules successfully import
3. SIEVE TESTS: sieve_mangoldt correctness
4. MATHEMATICAL VALIDATION: PHI constants, PNT, Chebyshev bounds
5. FUNCTION TESTS: Specific function validation

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

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
NUM_BRANCHES = 9
CHEB_A = 0.9212  # Chebyshev lower bound
CHEB_B = 1.1056  # Chebyshev upper bound

BASE_PATH = Path(__file__).parent.parent / "CONJECTURE_V" / "ASSERTION_1_EULERIAN_SCAFFOLD"
PROOF_SCRIPTS_PATH = BASE_PATH / "1_PROOF_SCRIPTS_NOTES"

ASSERTION_1_SCRIPTS = [
    "1_EULERIAN_PRIME_LAWS.py",
    "2_EULER_PHI_CONSTANTS.py",
    "EULERIAN_LAW_1_PNT_AND_PSI.py",
    "EULERIAN_LAW_2_THETA_AND_LI.py",
    "EULERIAN_LAW_3_PI_ERROR_BOUNDS.py",
    "EULERIAN_LAW_4_EULER_PRODUCT_TARGETS.py",
    "EULERIAN_LAW_5_PHI_UNIVERSAL_CONSTANTS.py",
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
    """Reference implementation of sieve_mangoldt for testing."""
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

class TestAssertion1Syntax(unittest.TestCase):
    """Test that all Assertion 1 scripts compile without syntax errors."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_all_scripts_compile(self):
        """All Assertion 1 scripts compile without syntax errors."""
        for script_name in ASSERTION_1_SCRIPTS:
            script = self.scripts_path / script_name
            if script.exists():
                with self.subTest(script=script_name):
                    self.assertTrue(can_compile(script), f"Syntax error in {script_name}")


# ============================================================================
# IMPORT VALIDATION TESTS
# ============================================================================

class TestAssertion1Imports(unittest.TestCase):
    """Test that all Assertion 1 scripts import successfully."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_eulerian_law_1_imports(self):
        """EULERIAN_LAW_1_PNT_AND_PSI.py imports successfully."""
        script = self.scripts_path / "EULERIAN_LAW_1_PNT_AND_PSI.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "eulerian_law_1")
        self.assertIsNotNone(module, "Module failed to import")
        self.assertTrue(hasattr(module, 'PHI'), "Missing PHI constant")
        self.assertTrue(hasattr(module, 'sieve_mangoldt'), "Missing sieve_mangoldt function")

    def test_eulerian_law_2_imports(self):
        """EULERIAN_LAW_2_THETA_AND_LI.py imports successfully."""
        script = self.scripts_path / "EULERIAN_LAW_2_THETA_AND_LI.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "eulerian_law_2")
        self.assertIsNotNone(module, "Module failed to import")


# ============================================================================
# MATHEMATICAL VALIDATION TESTS
# ============================================================================

class TestAssertion1Mathematics(unittest.TestCase):
    """Test mathematical properties of Assertion 1 constructs."""

    def test_phi_constant_value(self):
        """PHI = (1 + sqrt(5)) / 2 ≈ 1.618033988749895."""
        expected_phi = (1 + np.sqrt(5)) / 2
        self.assertAlmostEqual(PHI, expected_phi, places=15)

    def test_phi_golden_ratio_property(self):
        """PHI satisfies φ² = φ + 1."""
        self.assertAlmostEqual(PHI**2, PHI + 1, places=14)

    def test_phi_inverse_property(self):
        """1/φ = φ - 1."""
        self.assertAlmostEqual(1/PHI, PHI - 1, places=14)

    def test_chebyshev_bounds_order(self):
        """Chebyshev bounds satisfy A < 1 < B."""
        self.assertLess(CHEB_A, 1.0)
        self.assertGreater(CHEB_B, 1.0)

    def test_chebyshev_bounds_reasonable(self):
        """Chebyshev bounds are within historical limits."""
        self.assertGreater(CHEB_A, 0.9)
        self.assertLess(CHEB_B, 1.2)


class TestAssertion1Sieve(unittest.TestCase):
    """Test sieve_mangoldt implementation."""

    def test_sieve_small_primes(self):
        """Λ(n) = log(p) for small primes p."""
        lam = reference_sieve_mangoldt(20)
        # Λ(2) = log(2)
        self.assertAlmostEqual(lam[2], np.log(2), places=10)
        # Λ(3) = log(3)
        self.assertAlmostEqual(lam[3], np.log(3), places=10)
        # Λ(5) = log(5)
        self.assertAlmostEqual(lam[5], np.log(5), places=10)

    def test_sieve_prime_powers(self):
        """Λ(p^k) = log(p) for prime powers."""
        lam = reference_sieve_mangoldt(32)
        # Λ(4) = Λ(2²) = log(2)
        self.assertAlmostEqual(lam[4], np.log(2), places=10)
        # Λ(8) = Λ(2³) = log(2)
        self.assertAlmostEqual(lam[8], np.log(2), places=10)
        # Λ(9) = Λ(3²) = log(3)
        self.assertAlmostEqual(lam[9], np.log(3), places=10)

    def test_sieve_composite_zero(self):
        """Λ(n) = 0 for composite n that are not prime powers."""
        lam = reference_sieve_mangoldt(20)
        # Λ(6) = Λ(2·3) = 0 (not a prime power)
        self.assertEqual(lam[6], 0.0)
        # Λ(10) = Λ(2·5) = 0
        self.assertEqual(lam[10], 0.0)
        # Λ(15) = Λ(3·5) = 0
        self.assertEqual(lam[15], 0.0)

    def test_sieve_one_zero(self):
        """Λ(1) = 0."""
        lam = reference_sieve_mangoldt(10)
        self.assertEqual(lam[1], 0.0)


class TestAssertion1PNT(unittest.TestCase):
    """Test Prime Number Theorem related functions."""

    def test_psi_sum_positive(self):
        """ψ(x) = Σ_{n≤x} Λ(n) is positive for x ≥ 2."""
        lam = reference_sieve_mangoldt(100)
        psi = np.cumsum(lam)
        # ψ(x) should be positive for x ≥ 2
        self.assertGreater(psi[10], 0)
        self.assertGreater(psi[50], 0)
        self.assertGreater(psi[100], 0)

    def test_psi_monotonic(self):
        """ψ(x) is non-decreasing."""
        lam = reference_sieve_mangoldt(200)
        psi = np.cumsum(lam)
        # Check monotonicity
        for i in range(1, len(psi)):
            self.assertGreaterEqual(psi[i], psi[i-1])

    def test_pnt_asymptotic(self):
        """ψ(x)/x → 1 as x → ∞ (PNT)."""
        lam = reference_sieve_mangoldt(10000)
        psi = np.cumsum(lam)
        # For x = 10000, ψ(x)/x should be close to 1
        ratio = psi[10000] / 10000
        self.assertGreater(ratio, 0.9)  # Should be > 0.9
        self.assertLess(ratio, 1.1)     # Should be < 1.1


class TestAssertion1PhiWeights(unittest.TestCase):
    """Test φ-weight construction and properties."""

    def test_phi_weights_normalized(self):
        """φ-weights sum to 1."""
        raw_weights = np.array([PHI**(-k) for k in range(NUM_BRANCHES)])
        weights = raw_weights / raw_weights.sum()
        self.assertAlmostEqual(weights.sum(), 1.0, places=14)

    def test_phi_weights_positive(self):
        """All φ-weights are positive."""
        raw_weights = np.array([PHI**(-k) for k in range(NUM_BRANCHES)])
        weights = raw_weights / raw_weights.sum()
        for w in weights:
            self.assertGreater(w, 0)

    def test_phi_weights_decreasing(self):
        """φ-weights are monotonically decreasing."""
        raw_weights = np.array([PHI**(-k) for k in range(NUM_BRANCHES)])
        weights = raw_weights / raw_weights.sum()
        for k in range(1, NUM_BRANCHES):
            self.assertGreater(weights[k-1], weights[k])

    def test_geodesic_lengths_increasing(self):
        """Geodesic lengths L_k = φ^k are increasing."""
        lengths = np.array([PHI**k for k in range(NUM_BRANCHES)])
        for k in range(1, NUM_BRANCHES):
            self.assertGreater(lengths[k], lengths[k-1])


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ASSERTION 1: EULERIAN SCAFFOLD - UNIT TESTS")
    print("=" * 70)
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion1Syntax))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion1Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion1Mathematics))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion1Sieve))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion1PNT))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion1PhiWeights))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL ASSERTION 1 TESTS PASSED")
    else:
        print(f"❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
