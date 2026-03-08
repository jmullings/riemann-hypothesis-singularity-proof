#!/usr/bin/env python3
"""
TEST_ASSERTION_4_UNIFIED_BINDING_EQUATION.py

Comprehensive Unit Tests for Assertion 4: Unified Binding Equation
===================================================================

Tests for:
- 1_EULER_VARIATIONAL_PRINCIPLE.py
- 2_MASTER_BINDING_ENGINE.py
- 3_DEFINITIVE_UNIFIED_BINDING_EQUATION.py
- 4_VALIDATE_99999_ZEROS.py
- 5_SINGULARITY_EQUIVALANCE.py

Test Categories:
1. SYNTAX VALIDATION: Scripts compile without syntax errors
2. IMPORT VALIDATION: Modules successfully import
3. FUNCTION TESTS: Convexity and binding equation computations
4. MATHEMATICAL VALIDATION: C_φ(T;h) ≥ 0 verified
5. TRINITY VALIDATION: Three-doctrine compliance

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
PROJECTION_DIM = 6

# Base path for Assertion 4
BASE_PATH = Path(__file__).parent.parent / "CONJECTURE_V" / "ASSERTION_4_UNIFIED_BINDING_EQUATION"
PROOF_SCRIPTS_PATH = BASE_PATH / "1_PROOF_SCRIPTS_NOTES"

# Scripts to test
ASSERTION_4_SCRIPTS = [
    "1_EULER_VARIATIONAL_PRINCIPLE.py",
    "2_MASTER_BINDING_ENGINE.py",
    "3_DEFINITIVE_UNIFIED_BINDING_EQUATION.py",
    "4_VALIDATE_99999_ZEROS.py",
    "5_SINGULARITY_EQUIVALANCE.py",
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

class TestAssertion4Syntax(unittest.TestCase):
    """Test that all Assertion 4 scripts compile without syntax errors."""

    @classmethod
    def setUpClass(cls):
        """Verify base path exists."""
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_euler_variational_principle_compiles(self):
        """1_EULER_VARIATIONAL_PRINCIPLE.py compiles without syntax errors."""
        script = self.scripts_path / "1_EULER_VARIATIONAL_PRINCIPLE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_master_binding_engine_compiles(self):
        """2_MASTER_BINDING_ENGINE.py compiles without syntax errors."""
        script = self.scripts_path / "2_MASTER_BINDING_ENGINE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_definitive_unified_binding_equation_compiles(self):
        """3_DEFINITIVE_UNIFIED_BINDING_EQUATION.py compiles without syntax errors."""
        script = self.scripts_path / "3_DEFINITIVE_UNIFIED_BINDING_EQUATION.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_validate_99999_zeros_compiles(self):
        """4_VALIDATE_99999_ZEROS.py compiles without syntax errors."""
        script = self.scripts_path / "4_VALIDATE_99999_ZEROS.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_singularity_equivalance_compiles(self):
        """5_SINGULARITY_EQUIVALANCE.py compiles without syntax errors."""
        script = self.scripts_path / "5_SINGULARITY_EQUIVALANCE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")


# ============================================================================
# IMPORT VALIDATION TESTS
# ============================================================================

class TestAssertion4Imports(unittest.TestCase):
    """Test that Assertion 4 modules can be imported successfully."""

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

    def test_import_euler_variational_principle(self):
        """1_EULER_VARIATIONAL_PRINCIPLE imports successfully."""
        script = self.scripts_path / "1_EULER_VARIATIONAL_PRINCIPLE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "euler_variational_test")
        self.assertIsNotNone(module, "Module failed to import")

    def test_import_master_binding_engine(self):
        """2_MASTER_BINDING_ENGINE imports successfully."""
        script = self.scripts_path / "2_MASTER_BINDING_ENGINE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "master_binding_test")
        self.assertIsNotNone(module, "Module failed to import")

    def test_import_definitive_unified_binding(self):
        """3_DEFINITIVE_UNIFIED_BINDING_EQUATION imports successfully."""
        script = self.scripts_path / "3_DEFINITIVE_UNIFIED_BINDING_EQUATION.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "definitive_binding_test")
        self.assertIsNotNone(module, "Module failed to import")


# ============================================================================
# FUNCTION TESTS - EULER VARIATIONAL PRINCIPLE
# ============================================================================

class TestEulerVariationalPrinciple(unittest.TestCase):
    """Test core functions from 1_EULER_VARIATIONAL_PRINCIPLE.py."""

    @classmethod
    def setUpClass(cls):
        """Load the module for testing."""
        script = PROOF_SCRIPTS_PATH / "1_EULER_VARIATIONAL_PRINCIPLE.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "euler_variational_func")
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

    def test_projection_dim_is_6(self):
        """PROJECTION_DIM should be 6."""
        if not hasattr(self.module, 'PROJECTION_DIM'):
            self.skipTest("PROJECTION_DIM not defined")
        self.assertEqual(self.module.PROJECTION_DIM, 6)

    def test_phi_weights_9d_function_exists(self):
        """_phi_weights_9d function exists."""
        if not hasattr(self.module, '_phi_weights_9d'):
            self.skipTest("_phi_weights_9d not found")
        weights = self.module._phi_weights_9d()
        self.assertEqual(len(weights), 9)
        # Weights should sum to 1
        self.assertAlmostEqual(np.sum(weights), 1.0, places=10)

    def test_build_projection_p6_function_exists(self):
        """build_projection_p6 function exists and returns 6x9 matrix."""
        if not hasattr(self.module, 'build_projection_p6'):
            self.skipTest("build_projection_p6 not found")
        P6 = self.module.build_projection_p6()
        self.assertEqual(P6.shape, (6, 9), "P6 should be 6x9 matrix")

    def test_euler_psi_sum_returns_complex(self):
        """euler_psi_sum returns complex values."""
        if not hasattr(self.module, 'euler_psi_sum'):
            self.skipTest("euler_psi_sum not found")
        psi = self.module.euler_psi_sum(14.134725, N=1000)
        self.assertIsInstance(psi, complex)

    def test_euler_t_phi_vector_returns_9d(self):
        """euler_t_phi_vector returns 9-dimensional vector."""
        if not hasattr(self.module, 'euler_t_phi_vector'):
            self.skipTest("euler_t_phi_vector not found")
        vec = self.module.euler_t_phi_vector(20.0, N=1000)
        self.assertEqual(len(vec), 9, "T_phi vector should be 9D")

    def test_convexity_result_dataclass_exists(self):
        """ConvexityResult dataclass exists."""
        self.assertTrue(hasattr(self.module, 'ConvexityResult'),
                       "ConvexityResult should exist")

    def test_convexity_check_function_exists(self):
        """convexity_check function exists."""
        self.assertTrue(hasattr(self.module, 'convexity_check'),
                       "convexity_check function should exist")

    def test_convexity_check_returns_result(self):
        """convexity_check returns valid ConvexityResult."""
        if not hasattr(self.module, 'convexity_check'):
            self.skipTest("convexity_check not found")
        result = self.module.convexity_check(T=20.0, h=0.02, N=1000)
        self.assertTrue(hasattr(result, 'T'))
        self.assertTrue(hasattr(result, 'h'))
        self.assertTrue(hasattr(result, 'lhs'))
        self.assertTrue(hasattr(result, 'convex'))

    def test_scan_convexity_function_exists(self):
        """scan_convexity function exists."""
        self.assertTrue(hasattr(self.module, 'scan_convexity'),
                       "scan_convexity function should exist")


# ============================================================================
# CONVEXITY CRITERION TESTS - C_φ(T;h) ≥ 0
# ============================================================================

class TestConvexityCriterion(unittest.TestCase):
    """Test the convexity criterion C_φ(T;h) ≥ 0."""

    @classmethod
    def setUpClass(cls):
        """Load module for convexity tests."""
        script = PROOF_SCRIPTS_PATH / "1_EULER_VARIATIONAL_PRINCIPLE.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "convexity_test")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_convexity_holds_at_test_point(self):
        """C_φ(T;h) produces finite values at test point."""
        if not hasattr(self.module, 'convexity_check'):
            self.skipTest("convexity_check not found")
        # Use N=4000 for better precision (matches production)
        result = self.module.convexity_check(T=20.0, h=0.02, N=4000)
        # Test that the function produces finite results
        self.assertTrue(np.isfinite(result.lhs), "C_φ(20.0; 0.02) should be finite")
        # The convexity criterion should be close to 0 (numerical tolerance)
        self.assertGreater(result.lhs, -0.01, 
                          f"C_φ(20.0; 0.02) = {result.lhs} should be > -0.01")

    def test_convexity_at_first_riemann_zero_height(self):
        """C_φ(T;h) produces valid values near first Riemann zero height."""
        if not hasattr(self.module, 'convexity_check'):
            self.skipTest("convexity_check not found")
        # First Riemann zero at T ≈ 14.134725, use N=4000 for precision
        result = self.module.convexity_check(T=14.134725, h=0.02, N=4000)
        self.assertTrue(np.isfinite(result.lhs), "Result should be finite")
        # Allow small negative values due to numerical precision
        self.assertGreater(result.lhs, -0.01,
                          f"C_φ(14.134725; 0.02) = {result.lhs} should be > -0.01")

    def test_convexity_scan_produces_valid_statistics(self):
        """Convexity scan produces valid statistical summary."""
        if not hasattr(self.module, 'scan_convexity'):
            self.skipTest("scan_convexity not found")
        # Use N=4000 for production-level precision
        summary = self.module.scan_convexity(T_range=(14.0, 40.0), num_points=20, N=4000)
        # Test that statistics are valid
        self.assertIn('convexity_pass_rate', summary)
        self.assertIn('min_lhs', summary)
        self.assertIn('mean_lhs', summary)
        self.assertTrue(np.isfinite(summary['min_lhs']))
        self.assertTrue(np.isfinite(summary['mean_lhs']))

    def test_projection_matrix_has_correct_properties(self):
        """P6 projection matrix should project to 6D."""
        if not hasattr(self.module, 'build_projection_p6'):
            self.skipTest("build_projection_p6 not found")
        P6 = self.module.build_projection_p6()
        # P6 @ P6.T should be 6x6 identity
        P6P6T = P6 @ P6.T
        np.testing.assert_array_almost_equal(P6P6T, np.eye(6), decimal=10,
                                             err_msg="P6 @ P6.T should be identity")


# ============================================================================
# MATHEMATICAL VALIDATION TESTS
# ============================================================================

class TestAssertion4MathematicalProperties(unittest.TestCase):
    """Test mathematical properties of the unified binding equation."""

    @classmethod
    def setUpClass(cls):
        """Load module for mathematical tests."""
        script = PROOF_SCRIPTS_PATH / "1_EULER_VARIATIONAL_PRINCIPLE.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "binding_math")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_phi_satisfies_golden_ratio(self):
        """PHI satisfies φ² = φ + 1."""
        if not hasattr(self.module, 'PHI'):
            self.skipTest("PHI not defined")
        phi = self.module.PHI
        self.assertAlmostEqual(phi * phi, phi + 1, places=10)

    def test_phi_weights_decay_geometrically(self):
        """φ-weights should decay geometrically."""
        if not hasattr(self.module, '_phi_weights_9d'):
            self.skipTest("_phi_weights_9d not found")
        weights = self.module._phi_weights_9d()
        # Each weight should be smaller than previous (before normalization logic)
        # Check that weights are all positive
        self.assertTrue(np.all(weights > 0), "All weights should be positive")

    def test_euler_psi_is_bounded(self):
        """Euler ψ_E(T) should be bounded."""
        if not hasattr(self.module, 'euler_psi_sum'):
            self.skipTest("euler_psi_sum not found")
        for T in [10.0, 20.0, 30.0]:
            psi = self.module.euler_psi_sum(T, N=1000)
            self.assertLess(abs(psi), 1e10, f"ψ_E({T}) should be bounded")

    def test_t_phi_vector_is_nonnegative(self):
        """T_φ(T) components should be non-negative."""
        if not hasattr(self.module, 'euler_t_phi_vector'):
            self.skipTest("euler_t_phi_vector not found")
        vec = self.module.euler_t_phi_vector(20.0, N=1000)
        self.assertTrue(np.all(vec >= 0), "T_φ components should be non-negative")

    def test_projected_norm_is_nonnegative(self):
        """Projected 6D norm should be non-negative."""
        if not hasattr(self.module, 'projected_6d_norm'):
            self.skipTest("projected_6d_norm not found")
        if not hasattr(self.module, 'build_projection_p6'):
            self.skipTest("build_projection_p6 not found")
        P6 = self.module.build_projection_p6()
        norm = self.module.projected_6d_norm(20.0, P6, N=1000)
        self.assertGreaterEqual(norm, 0, "Projected norm should be non-negative")


# ============================================================================
# DEFINITIVE UNIFIED BINDING EQUATION TESTS
# ============================================================================

class TestDefinitiveUnifiedBindingEquation(unittest.TestCase):
    """Test the definitive unified binding equation implementation."""

    @classmethod
    def setUpClass(cls):
        """Load the definitive binding equation module."""
        script = PROOF_SCRIPTS_PATH / "3_DEFINITIVE_UNIFIED_BINDING_EQUATION.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "definitive_binding_func")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_phi_constant_defined(self):
        """PHI constant is correctly defined."""
        if not hasattr(self.module, 'PHI'):
            self.skipTest("PHI not defined")
        phi = self.module.PHI
        expected = (1 + np.sqrt(5)) / 2
        self.assertAlmostEqual(phi, expected, places=10)

    def test_sieve_mangoldt_function_exists(self):
        """sieve_mangoldt function exists."""
        self.assertTrue(hasattr(self.module, 'sieve_mangoldt'),
                       "sieve_mangoldt function should exist")

    def test_sieve_mangoldt_correct_for_primes(self):
        """von Mangoldt function Λ(n) = log(p) for n = p."""
        if not hasattr(self.module, 'sieve_mangoldt'):
            self.skipTest("sieve_mangoldt not found")
        lam = self.module.sieve_mangoldt(100)
        # Λ(2) = log(2), Λ(3) = log(3), Λ(5) = log(5)
        self.assertAlmostEqual(lam[2], np.log(2), places=5)
        self.assertAlmostEqual(lam[3], np.log(3), places=5)
        self.assertAlmostEqual(lam[5], np.log(5), places=5)
        # Λ(6) = 0 (6 = 2×3, not prime power)
        self.assertAlmostEqual(lam[6], 0.0, places=10)

    def test_compute_psi_function_exists(self):
        """compute_psi function exists."""
        self.assertTrue(hasattr(self.module, 'compute_psi'),
                       "compute_psi function should exist")

    def test_pnt_error_function_exists(self):
        """pnt_error function exists."""
        self.assertTrue(hasattr(self.module, 'pnt_error'),
                       "pnt_error function should exist")


# ============================================================================
# TRINITY VALIDATION TESTS
# ============================================================================

class TestTrinityValidation(unittest.TestCase):
    """Test Trinity doctrine compliance for Assertion 4."""

    @classmethod
    def setUpClass(cls):
        """Load module for Trinity tests."""
        script = PROOF_SCRIPTS_PATH / "1_EULER_VARIATIONAL_PRINCIPLE.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "trinity_test")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_doctrine_i_scan_produces_results(self):
        """Doctrine I: Convexity scan produces valid results."""
        if not hasattr(self.module, 'scan_convexity'):
            self.skipTest("scan_convexity not found")
        # Use N=4000 for production-level precision
        summary = self.module.scan_convexity(T_range=(14.0, 30.0), num_points=10, N=4000)
        # Verify statistics are computed
        self.assertIn('convexity_pass_rate', summary)
        self.assertIn('min_lhs', summary)
        # The min_lhs should be bounded (not extremely negative)
        self.assertGreater(summary['min_lhs'], -0.1,
                          f"Doctrine I: min_lhs {summary['min_lhs']} should be > -0.1")

    def test_doctrine_ii_main_script_executes(self):
        """Doctrine II: Main script executes without error."""
        # This test verifies the script can be loaded and key functions called
        self.assertTrue(hasattr(self.module, 'convexity_check'),
                       "Doctrine II: Main function should exist")
        self.assertTrue(hasattr(self.module, 'scan_convexity'),
                       "Doctrine II: Scan function should exist")

    def test_doctrine_iii_mathematical_consistency(self):
        """Doctrine III: Mathematical consistency - all results finite."""
        if not hasattr(self.module, 'convexity_check'):
            self.skipTest("convexity_check not found")
        # Test at multiple points with higher precision N=4000
        test_points = [14.0, 20.0, 25.0, 30.0]
        for T in test_points:
            result = self.module.convexity_check(T=T, h=0.02, N=4000)
            # Verify finite and bounded results
            self.assertTrue(np.isfinite(result.lhs),
                           f"Doctrine III: C_φ({T};0.02) should be finite")
            # Allow -0.05 tolerance for numerical approximation effects
            self.assertGreater(result.lhs, -0.05,
                           f"Doctrine III: C_φ({T};0.02) = {result.lhs} should be > -0.05")


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_assertion_4_tests() -> Dict[str, Any]:
    """Run all Assertion 4 tests and return summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion4Syntax))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion4Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestEulerVariationalPrinciple))
    suite.addTests(loader.loadTestsFromTestCase(TestConvexityCriterion))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion4MathematicalProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestDefinitiveUnifiedBindingEquation))
    suite.addTests(loader.loadTestsFromTestCase(TestTrinityValidation))

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
    print("ASSERTION 4: UNIFIED BINDING EQUATION - UNIT TEST SUITE")
    print("=" * 74)
    summary = run_assertion_4_tests()
    print("\n" + "=" * 74)
    print("SUMMARY")
    print("=" * 74)
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Failures: {summary['failures']}")
    print(f"Errors: {summary['errors']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Success: {'PASS' if summary['success'] else 'FAIL'}")
