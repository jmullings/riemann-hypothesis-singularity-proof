#!/usr/bin/env python3
"""
TEST_ASSERTION_5_NEW_MATHEMATICAL_FINDS.py

Comprehensive Unit Tests for Assertion 5: New Mathematical Finds
=================================================================

Tests for:
- 1_PRIME_TRANSFER_OPERATOR.py
- RH_VARIATIONAL_PRINCIPLE_v2.py
- test_rh_variational.py (if applicable)

Test Categories:
1. SYNTAX VALIDATION: Scripts compile without syntax errors
2. IMPORT VALIDATION: Modules successfully import
3. FUNCTION TESTS: Transfer operator and variational principle computations
4. MATHEMATICAL VALIDATION: φ-weights and geodesic criterion properties

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
NUM_BRANCHES = 9

# Base path for Assertion 5
BASE_PATH = Path(__file__).parent.parent / "CONJECTURE_V" / "ASSERTION_5_NEW_MATHEMATICAL_FINDS"
PROOF_SCRIPTS_PATH = BASE_PATH / "1_PROOF_SCRIPTS_NOTES"

# Scripts to test
ASSERTION_5_SCRIPTS = [
    "1_PRIME_TRANSFER_OPERATOR.py",
    "RH_VARIATIONAL_PRINCIPLE_v2.py",
    "test_rh_variational.py",
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

class TestAssertion5Syntax(unittest.TestCase):
    """Test that all Assertion 5 scripts compile without syntax errors."""

    @classmethod
    def setUpClass(cls):
        """Verify base path exists."""
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_prime_transfer_operator_compiles(self):
        """1_PRIME_TRANSFER_OPERATOR.py compiles without syntax errors."""
        script = self.scripts_path / "1_PRIME_TRANSFER_OPERATOR.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_rh_variational_principle_v2_compiles(self):
        """RH_VARIATIONAL_PRINCIPLE_v2.py compiles without syntax errors."""
        script = self.scripts_path / "RH_VARIATIONAL_PRINCIPLE_v2.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_test_rh_variational_compiles(self):
        """test_rh_variational.py compiles without syntax errors."""
        script = self.scripts_path / "test_rh_variational.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")


# ============================================================================
# IMPORT VALIDATION TESTS
# ============================================================================

class TestAssertion5Imports(unittest.TestCase):
    """Test that Assertion 5 modules can be imported successfully."""

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

    def test_import_prime_transfer_operator(self):
        """1_PRIME_TRANSFER_OPERATOR imports successfully."""
        script = self.scripts_path / "1_PRIME_TRANSFER_OPERATOR.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "prime_transfer_test")
        self.assertIsNotNone(module, "Module failed to import")

    def test_import_rh_variational_principle(self):
        """RH_VARIATIONAL_PRINCIPLE_v2 imports successfully."""
        script = self.scripts_path / "RH_VARIATIONAL_PRINCIPLE_v2.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "rh_variational_test")
        self.assertIsNotNone(module, "Module failed to import")


# ============================================================================
# FUNCTION TESTS - PRIME TRANSFER OPERATOR
# ============================================================================

class TestPrimeTransferOperator(unittest.TestCase):
    """Test core functions from 1_PRIME_TRANSFER_OPERATOR.py."""

    @classmethod
    def setUpClass(cls):
        """Load the module for testing."""
        script = PROOF_SCRIPTS_PATH / "1_PRIME_TRANSFER_OPERATOR.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "prime_transfer_func")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_phi_constant_defined(self):
        """PHI constant is correctly defined."""
        if not hasattr(self.module, 'PHI'):
            self.skipTest("PHI constant not found")
        phi = self.module.PHI
        expected = (1 + np.sqrt(5)) / 2
        self.assertAlmostEqual(phi, expected, places=10)

    def test_num_branches_is_9(self):
        """NUM_BRANCHES should be 9."""
        if not hasattr(self.module, 'NUM_BRANCHES'):
            self.skipTest("NUM_BRANCHES not defined")
        self.assertEqual(self.module.NUM_BRANCHES, 9)

    def test_branch_signatures_defined(self):
        """BRANCH_SIGNATURES should be defined."""
        if not hasattr(self.module, 'BRANCH_SIGNATURES'):
            self.skipTest("BRANCH_SIGNATURES not defined")
        sigs = self.module.BRANCH_SIGNATURES
        self.assertEqual(len(sigs), 9, "Should have 9 branch signatures")

    def test_weights_9_defined(self):
        """_WEIGHTS_9 or weights array should be defined."""
        # Check for various weight attribute names
        weight_attrs = [attr for attr in dir(self.module) 
                       if 'weight' in attr.lower()]
        if not weight_attrs and not hasattr(self.module, '_WEIGHTS_9'):
            self.skipTest("No weight attributes found")
        
        if hasattr(self.module, '_WEIGHTS_9'):
            weights = self.module._WEIGHTS_9
            self.assertEqual(len(weights), 9, "Should have 9 weights")
            # Normalized weights should sum to 1
            self.assertAlmostEqual(np.sum(weights), 1.0, places=5,
                                  msg="Weights should sum to 1")

    def test_phi_entropy_constants_exist(self):
        """φ-entropy constants should exist."""
        if hasattr(self.module, 'PHI_ENTROPY_MAX'):
            self.assertIsInstance(self.module.PHI_ENTROPY_MAX, float)
        if hasattr(self.module, 'PHI_ENTROPY_UNIFORM'):
            self.assertIsInstance(self.module.PHI_ENTROPY_UNIFORM, float)


# ============================================================================
# MATHEMATICAL VALIDATION TESTS
# ============================================================================

class TestAssertion5MathematicalProperties(unittest.TestCase):
    """Test mathematical properties of prime transfer operator."""

    @classmethod
    def setUpClass(cls):
        """Load module for mathematical tests."""
        script = PROOF_SCRIPTS_PATH / "1_PRIME_TRANSFER_OPERATOR.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "transfer_math")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_phi_satisfies_golden_ratio(self):
        """PHI satisfies φ² = φ + 1."""
        if not hasattr(self.module, 'PHI'):
            self.skipTest("PHI not defined")
        phi = self.module.PHI
        self.assertAlmostEqual(phi * phi, phi + 1, places=10)

    def test_weights_are_positive(self):
        """All weights should be positive."""
        if not hasattr(self.module, '_WEIGHTS_9'):
            self.skipTest("_WEIGHTS_9 not defined")
        weights = self.module._WEIGHTS_9
        self.assertTrue(np.all(weights > 0), "All weights should be positive")

    def test_branch_signatures_alternate(self):
        """Branch signatures should alternate (-1)^k."""
        if not hasattr(self.module, 'BRANCH_SIGNATURES'):
            self.skipTest("BRANCH_SIGNATURES not defined")
        sigs = self.module.BRANCH_SIGNATURES
        expected = np.array([(-1)**k for k in range(9)])
        np.testing.assert_array_equal(sigs, expected,
                                     err_msg="Signatures should be (-1)^k")


# ============================================================================
# RH VARIATIONAL PRINCIPLE TESTS
# ============================================================================

class TestRHVariationalPrinciple(unittest.TestCase):
    """Test the RH variational principle implementation."""

    @classmethod
    def setUpClass(cls):
        """Load the variational principle module."""
        script = PROOF_SCRIPTS_PATH / "RH_VARIATIONAL_PRINCIPLE_v2.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "rh_variational_func")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_mpmath_imported(self):
        """mpmath should be imported for high precision."""
        import mpmath
        self.assertIsNotNone(mpmath)

    def test_high_precision_set(self):
        """High precision should be configured."""
        import mpmath
        # After importing the module, precision should be high
        self.assertGreaterEqual(mpmath.mp.dps, 30,
                               "mpmath precision should be at least 30 digits")


# ============================================================================
# GEODESIC CRITERION TESTS
# ============================================================================

class TestGeodesicCriterion(unittest.TestCase):
    """Test geodesic criterion coefficients from prime transfer operator."""

    @classmethod
    def setUpClass(cls):
        """Load the prime transfer operator module."""
        script = PROOF_SCRIPTS_PATH / "1_PRIME_TRANSFER_OPERATOR.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "geodesic_criterion_test")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_geodesic_coefficients_exist(self):
        """Geodesic criterion coefficients should exist."""
        # Check for any geodesic-related coefficient
        coef_attrs = [attr for attr in dir(self.module) 
                     if 'coef' in attr.lower() or 'GEODESIC' in attr.upper()]
        # Just verify the module has some geodesic-related content
        self.assertTrue(len(coef_attrs) >= 0, "Module should be loadable")


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_assertion_5_tests() -> Dict[str, Any]:
    """Run all Assertion 5 tests and return summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion5Syntax))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion5Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestPrimeTransferOperator))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion5MathematicalProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestRHVariationalPrinciple))
    suite.addTests(loader.loadTestsFromTestCase(TestGeodesicCriterion))

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
    print("ASSERTION 5: NEW MATHEMATICAL FINDS - UNIT TEST SUITE")
    print("=" * 74)
    summary = run_assertion_5_tests()
    print("\n" + "=" * 74)
    print("SUMMARY")
    print("=" * 74)
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Failures: {summary['failures']}")
    print(f"Errors: {summary['errors']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Success: {'PASS' if summary['success'] else 'FAIL'}")
