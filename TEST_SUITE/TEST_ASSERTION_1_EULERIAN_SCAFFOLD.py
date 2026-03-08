#!/usr/bin/env python3
"""
TEST_ASSERTION_1_EULERIAN_SCAFFOLD.py

Comprehensive Unit Tests for Assertion 1: Eulerian Scaffold
============================================================

Tests for:
- 1_EULERIAN_PRIME_LAWS.py
- 2_EULER_PHI_CONSTANTS.py
- EULERIAN_LAW_1_PNT_AND_PSI.py
- EULERIAN_LAW_2_THETA_AND_LI.py
- EULERIAN_LAW_3_PI_ERROR_BOUNDS.py
- EULERIAN_LAW_4_EULER_PRODUCT_TARGETS.py
- EULERIAN_LAW_5_PHI_UNIVERSAL_CONSTANTS.py

Test Categories:
1. SYNTAX VALIDATION: Scripts compile without errors
2. IMPORT VALIDATION: Modules can be imported
3. FUNCTION TESTS: Core computations produce valid results
4. MATHEMATICAL VALIDATION: Results satisfy mathematical properties

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
from typing import Optional, Dict, Any

# ============================================================================
# CONFIGURATION
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio

# Base path for Assertion 1
BASE_PATH = Path(__file__).parent.parent / "CONJECTURE_V" / "ASSERTION_1_EULERIAN_SCAFFOLD"
PROOF_SCRIPTS_PATH = BASE_PATH / "1_PROOF_SCRIPTS_NOTES"

# Scripts to test
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


# ============================================================================
# SYNTAX VALIDATION TESTS
# ============================================================================

class TestAssertion1Syntax(unittest.TestCase):
    """Test that all Assertion 1 scripts compile without syntax errors."""

    @classmethod
    def setUpClass(cls):
        """Verify base path exists."""
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_1_eulerian_prime_laws_compiles(self):
        """1_EULERIAN_PRIME_LAWS.py compiles without syntax errors."""
        script = self.scripts_path / "1_EULERIAN_PRIME_LAWS.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_2_euler_phi_constants_compiles(self):
        """2_EULER_PHI_CONSTANTS.py compiles without syntax errors."""
        script = self.scripts_path / "2_EULER_PHI_CONSTANTS.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_eulerian_law_1_compiles(self):
        """EULERIAN_LAW_1_PNT_AND_PSI.py compiles without syntax errors."""
        script = self.scripts_path / "EULERIAN_LAW_1_PNT_AND_PSI.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_eulerian_law_2_compiles(self):
        """EULERIAN_LAW_2_THETA_AND_LI.py compiles without syntax errors."""
        script = self.scripts_path / "EULERIAN_LAW_2_THETA_AND_LI.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_eulerian_law_3_compiles(self):
        """EULERIAN_LAW_3_PI_ERROR_BOUNDS.py compiles without syntax errors."""
        script = self.scripts_path / "EULERIAN_LAW_3_PI_ERROR_BOUNDS.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_eulerian_law_4_compiles(self):
        """EULERIAN_LAW_4_EULER_PRODUCT_TARGETS.py compiles without syntax errors."""
        script = self.scripts_path / "EULERIAN_LAW_4_EULER_PRODUCT_TARGETS.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_eulerian_law_5_compiles(self):
        """EULERIAN_LAW_5_PHI_UNIVERSAL_CONSTANTS.py compiles without syntax errors."""
        script = self.scripts_path / "EULERIAN_LAW_5_PHI_UNIVERSAL_CONSTANTS.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")


# ============================================================================
# IMPORT VALIDATION TESTS
# ============================================================================

class TestAssertion1Imports(unittest.TestCase):
    """Test that Assertion 1 modules can be imported successfully."""

    @classmethod
    def setUpClass(cls):
        """Set up import path."""
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if cls.scripts_path.exists():
            sys.path.insert(0, str(cls.scripts_path))

    @classmethod
    def tearDownClass(cls):
        """Clean up import path."""
        if str(cls.scripts_path) in sys.path:
            sys.path.remove(str(cls.scripts_path))

    def test_import_eulerian_prime_laws(self):
        """1_EULERIAN_PRIME_LAWS imports successfully."""
        script = self.scripts_path / "1_EULERIAN_PRIME_LAWS.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "eulerian_prime_laws_test")
        self.assertIsNotNone(module, "Module failed to import")

    def test_import_euler_phi_constants(self):
        """2_EULER_PHI_CONSTANTS imports successfully."""
        script = self.scripts_path / "2_EULER_PHI_CONSTANTS.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "euler_phi_constants_test")
        self.assertIsNotNone(module, "Module failed to import")


# ============================================================================
# FUNCTION TESTS - PRIME LAWS
# ============================================================================

class TestEulerianPrimeLaws(unittest.TestCase):
    """Test core functions from 1_EULERIAN_PRIME_LAWS.py."""

    @classmethod
    def setUpClass(cls):
        """Load the module for testing."""
        script = PROOF_SCRIPTS_PATH / "1_EULERIAN_PRIME_LAWS.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "eulerian_prime_laws_func")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_phi_constant_defined(self):
        """PHI constant is correctly defined as golden ratio."""
        if not hasattr(self.module, 'PHI'):
            self.skipTest("PHI constant not found")
        phi = self.module.PHI
        expected = (1 + np.sqrt(5)) / 2
        self.assertAlmostEqual(phi, expected, places=10,
                               msg="PHI should equal golden ratio")

    def test_prime_generator_exists(self):
        """PrimeGenerator class exists and is instantiable."""
        if not hasattr(self.module, 'PrimeGenerator'):
            self.skipTest("PrimeGenerator class not found")
        generator = self.module.PrimeGenerator()
        self.assertIsNotNone(generator)

    def test_prime_generator_produces_primes(self):
        """PrimeGenerator produces correct first few primes."""
        if not hasattr(self.module, 'PrimeGenerator'):
            self.skipTest("PrimeGenerator class not found")
        generator = self.module.PrimeGenerator()
        primes = generator.get_primes(30)
        expected = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
        np.testing.assert_array_equal(primes, expected,
                                      err_msg="First 10 primes incorrect")

    def test_prime_count_function(self):
        """Prime counting function π(x) returns correct values."""
        if not hasattr(self.module, 'PrimeGenerator'):
            self.skipTest("PrimeGenerator class not found")
        generator = self.module.PrimeGenerator()
        # π(10) = 4 (primes: 2, 3, 5, 7)
        self.assertEqual(generator.prime_count(10), 4)
        # π(100) = 25
        self.assertEqual(generator.prime_count(100), 25)

    def test_prime_function_enum_exists(self):
        """PrimeFunction enumeration exists."""
        if not hasattr(self.module, 'PrimeFunction'):
            self.skipTest("PrimeFunction enum not found")
        self.assertTrue(hasattr(self.module.PrimeFunction, 'PI_FUNCTION'))
        self.assertTrue(hasattr(self.module.PrimeFunction, 'PSI_FUNCTION'))
        self.assertTrue(hasattr(self.module.PrimeFunction, 'THETA_FUNCTION'))

    def test_error_type_enum_exists(self):
        """ErrorType enumeration exists."""
        if not hasattr(self.module, 'ErrorType'):
            self.skipTest("ErrorType enum not found")
        self.assertTrue(hasattr(self.module.ErrorType, 'CLASSICAL'))
        self.assertTrue(hasattr(self.module.ErrorType, 'RH_SHARP'))


# ============================================================================
# MATHEMATICAL VALIDATION TESTS
# ============================================================================

class TestEulerianMathematicalProperties(unittest.TestCase):
    """Test mathematical properties of Eulerian scaffold functions."""

    @classmethod
    def setUpClass(cls):
        """Load module for mathematical tests."""
        script = PROOF_SCRIPTS_PATH / "1_EULERIAN_PRIME_LAWS.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "eulerian_prime_laws_math")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_phi_is_golden_ratio(self):
        """PHI satisfies the golden ratio equation φ² = φ + 1."""
        if not hasattr(self.module, 'PHI'):
            self.skipTest("PHI not defined")
        phi = self.module.PHI
        # φ² ≈ φ + 1
        self.assertAlmostEqual(phi * phi, phi + 1, places=10)

    def test_prime_sieve_correctness(self):
        """Prime sieve produces correct counts up to known limits."""
        if not hasattr(self.module, 'PrimeGenerator'):
            self.skipTest("PrimeGenerator not found")
        generator = self.module.PrimeGenerator()
        
        # Known prime counts: π(n) for n = 10, 100, 1000
        test_cases = [
            (10, 4),
            (100, 25),
            (1000, 168),
        ]
        for n, expected_count in test_cases:
            actual = generator.prime_count(n)
            self.assertEqual(actual, expected_count,
                           f"π({n}) should be {expected_count}, got {actual}")

    def test_euler_gamma_constant(self):
        """Euler-Mascheroni constant is correctly defined."""
        if not hasattr(self.module, 'EULER_GAMMA'):
            self.skipTest("EULER_GAMMA not defined")
        gamma = self.module.EULER_GAMMA
        # γ ≈ 0.5772156649...
        self.assertAlmostEqual(gamma, 0.5772156649015329, places=10)


# ============================================================================
# PHI CONSTANTS TESTS
# ============================================================================

class TestEulerPhiConstants(unittest.TestCase):
    """Test functions from 2_EULER_PHI_CONSTANTS.py."""

    @classmethod
    def setUpClass(cls):
        """Load the module."""
        script = PROOF_SCRIPTS_PATH / "2_EULER_PHI_CONSTANTS.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "euler_phi_constants_func")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_phi_weights_normalized(self):
        """φ-weights should sum to 1 (normalized)."""
        if hasattr(self.module, '_phi_weights') or hasattr(self.module, 'phi_weights'):
            weights_func = getattr(self.module, '_phi_weights', 
                                   getattr(self.module, 'phi_weights', None))
            if weights_func and callable(weights_func):
                weights = weights_func()
                self.assertAlmostEqual(np.sum(weights), 1.0, places=10,
                                      msg="φ-weights should sum to 1")
        else:
            self.skipTest("Weight function not found")

    def test_num_branches_is_9(self):
        """NUM_BRANCHES should be 9."""
        if hasattr(self.module, 'NUM_BRANCHES'):
            self.assertEqual(self.module.NUM_BRANCHES, 9,
                           "NUM_BRANCHES should be 9")
        else:
            self.skipTest("NUM_BRANCHES not defined")


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_assertion_1_tests() -> Dict[str, Any]:
    """Run all Assertion 1 tests and return summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion1Syntax))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion1Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestEulerianPrimeLaws))
    suite.addTests(loader.loadTestsFromTestCase(TestEulerianMathematicalProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestEulerPhiConstants))

    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success": result.wasSuccessful()
    }


if __name__ == "__main__":
    print("=" * 74)
    print("ASSERTION 1: EULERIAN SCAFFOLD - UNIT TEST SUITE")
    print("=" * 74)
    summary = run_assertion_1_tests()
    print("\n" + "=" * 74)
    print("SUMMARY")
    print("=" * 74)
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Failures: {summary['failures']}")
    print(f"Errors: {summary['errors']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Success: {'PASS' if summary['success'] else 'FAIL'}")
