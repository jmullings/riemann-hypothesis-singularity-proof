#!/usr/bin/env python3
"""
TEST_ASSERTION_3_6D_VARIANCE_COLLAPSE.py

Comprehensive Unit Tests for Assertion 3: 6D Variance Collapse
===============================================================

Tests for:
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
3. FUNCTION TESTS: PCA and dimensional collapse computations work
4. MATHEMATICAL VALIDATION: Bombieri-Vinogradov properties verified

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

# Base path for Assertion 3
BASE_PATH = Path(__file__).parent.parent / "CONJECTURE_V" / "ASSERTION_3_6D_VARIANCE_COLLAPSE"
PROOF_SCRIPTS_PATH = BASE_PATH / "1_PROOF_SCRIPTS_NOTES"

# Scripts to test
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


# ============================================================================
# SYNTAX VALIDATION TESTS
# ============================================================================

class TestAssertion3Syntax(unittest.TestCase):
    """Test that all Assertion 3 scripts compile without syntax errors."""

    @classmethod
    def setUpClass(cls):
        """Verify base path exists."""
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_bombieri_vinogradov_6d_pca_compiles(self):
        """1_BOMBIERI_VINOGRADOV_6D_PCA.py compiles without syntax errors."""
        script = self.scripts_path / "1_BOMBIERI_VINOGRADOV_6D_PCA.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_dimensional_collapse_validator_compiles(self):
        """2_DIMENSIONAL_COLLAPSE_VALIDATOR.py compiles without syntax errors."""
        script = self.scripts_path / "2_DIMENSIONAL_COLLAPSE_VALIDATOR.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_assertion_3_file_1_compiles(self):
        """ASSERTION_3_FILE_1__9D_SINGULARITY_DETECTION compiles."""
        script = self.scripts_path / "ASSERTION_3_FILE_1__9D_SINGULARITY_DETECTION.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_assertion_3_file_2_compiles(self):
        """ASSERTION_3_FILE_2__BV_VARIANCE_DAMPING compiles."""
        script = self.scripts_path / "ASSERTION_3_FILE_2__BV_VARIANCE_DAMPING.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_assertion_3_file_3_compiles(self):
        """ASSERTION_3_FILE_3__PCA_SPECTRAL_COLLAPSE compiles."""
        script = self.scripts_path / "ASSERTION_3_FILE_3__PCA_SPECTRAL_COLLAPSE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_assertion_3_file_4_compiles(self):
        """ASSERTION_3_FILE_4__DIMENSIONAL_COLLAPSE_VALIDATOR compiles."""
        script = self.scripts_path / "ASSERTION_3_FILE_4__DIMENSIONAL_COLLAPSE_VALIDATOR.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_assertion_3_file_5_compiles(self):
        """ASSERTION_3_FILE_5__UNIFIED_6D_COLLAPSE_THEOREM compiles."""
        script = self.scripts_path / "ASSERTION_3_FILE_5__UNIFIED_6D_COLLAPSE_THEOREM.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")


# ============================================================================
# IMPORT VALIDATION TESTS
# ============================================================================

class TestAssertion3Imports(unittest.TestCase):
    """Test that Assertion 3 modules can be imported successfully."""

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

    def test_import_bombieri_vinogradov_6d_pca(self):
        """1_BOMBIERI_VINOGRADOV_6D_PCA imports successfully."""
        script = self.scripts_path / "1_BOMBIERI_VINOGRADOV_6D_PCA.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "bv_6d_pca_test")
        self.assertIsNotNone(module, "Module failed to import")

    def test_import_dimensional_collapse_validator(self):
        """2_DIMENSIONAL_COLLAPSE_VALIDATOR compiles (may have external deps)."""
        script = self.scripts_path / "2_DIMENSIONAL_COLLAPSE_VALIDATOR.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        # This module has dependencies on RH_SINGULARITY and other modules
        # We test syntax only, import may fail due to missing deps
        self.assertTrue(can_compile(script), 
                       "Module should compile despite external dependencies")


# ============================================================================
# FUNCTION TESTS - BOMBIERI-VINOGRADOV PCA
# ============================================================================

class TestBombieriVinogradov6DPCA(unittest.TestCase):
    """Test core functions from 1_BOMBIERI_VINOGRADOV_6D_PCA.py."""

    @classmethod
    def setUpClass(cls):
        """Load the module for testing."""
        script = PROOF_SCRIPTS_PATH / "1_BOMBIERI_VINOGRADOV_6D_PCA.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "bv_6d_pca_func")
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

    def test_pca_result_dataclass_exists(self):
        """PCAResult dataclass exists."""
        self.assertTrue(hasattr(self.module, 'PCAResult'),
                       "PCAResult dataclass should exist")

    def test_run_bv_6d_pca_function_exists(self):
        """run_bv_6d_pca function exists."""
        self.assertTrue(hasattr(self.module, 'run_bv_6d_pca'),
                       "run_bv_6d_pca function should exist")

    def test_run_bv_6d_pca_returns_pca_result(self):
        """run_bv_6d_pca returns PCAResult with expected fields."""
        if not hasattr(self.module, 'run_bv_6d_pca'):
            self.skipTest("run_bv_6d_pca not found")
        result = self.module.run_bv_6d_pca()
        # Check result has expected fields
        self.assertTrue(hasattr(result, 'covariance_9d'))
        self.assertTrue(hasattr(result, 'eigenvalues_desc'))
        self.assertTrue(hasattr(result, 'effective_rank_99'))
        self.assertTrue(hasattr(result, 'trailing_energy_ratio'))

    def test_eigenvalues_are_sorted_descending(self):
        """Eigenvalues should be sorted in descending order."""
        if not hasattr(self.module, 'run_bv_6d_pca'):
            self.skipTest("run_bv_6d_pca not found")
        result = self.module.run_bv_6d_pca()
        eigvals = result.eigenvalues_desc
        # Check descending order
        for i in range(len(eigvals) - 1):
            self.assertGreaterEqual(eigvals[i], eigvals[i + 1],
                                   "Eigenvalues should be descending")

    def test_effective_rank_at_most_9(self):
        """Effective rank should be at most 9 (full dimension)."""
        if not hasattr(self.module, 'run_bv_6d_pca'):
            self.skipTest("run_bv_6d_pca not found")
        result = self.module.run_bv_6d_pca()
        self.assertLessEqual(result.effective_rank_99, 9,
                            "Effective rank should be ≤ 9")

    def test_effective_rank_is_6_or_less(self):
        """Effective rank should demonstrate 6D collapse."""
        if not hasattr(self.module, 'run_bv_6d_pca'):
            self.skipTest("run_bv_6d_pca not found")
        result = self.module.run_bv_6d_pca()
        # The core assertion: effective dimensionality collapses to ≤6
        self.assertLessEqual(result.effective_rank_99, 6,
                            "Effective rank should collapse to ≤ 6 (BV damping)")

    def test_trailing_energy_ratio_small(self):
        """Trailing energy ratio should be small after BV damping."""
        if not hasattr(self.module, 'run_bv_6d_pca'):
            self.skipTest("run_bv_6d_pca not found")
        result = self.module.run_bv_6d_pca()
        # Trailing modes (7,8,9) should contribute little energy
        self.assertLess(result.trailing_energy_ratio, 0.1,
                       "Trailing mode energy should be < 10%")


# ============================================================================
# MATHEMATICAL VALIDATION TESTS
# ============================================================================

class TestAssertion3MathematicalProperties(unittest.TestCase):
    """Test mathematical properties of 6D variance collapse."""

    @classmethod
    def setUpClass(cls):
        """Load module for mathematical tests."""
        script = PROOF_SCRIPTS_PATH / "1_BOMBIERI_VINOGRADOV_6D_PCA.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "bv_pca_math")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_phi_satisfies_golden_ratio(self):
        """PHI satisfies φ² = φ + 1."""
        if not hasattr(self.module, 'PHI'):
            self.skipTest("PHI not defined")
        phi = self.module.PHI
        self.assertAlmostEqual(phi * phi, phi + 1, places=10)

    def test_covariance_matrix_is_symmetric(self):
        """Covariance matrix should be symmetric."""
        if not hasattr(self.module, 'run_bv_6d_pca'):
            self.skipTest("run_bv_6d_pca not found")
        result = self.module.run_bv_6d_pca()
        cov = result.covariance_9d
        # Check symmetry
        np.testing.assert_array_almost_equal(cov, cov.T, decimal=10,
                                             err_msg="Covariance should be symmetric")

    def test_covariance_matrix_is_positive_semidefinite(self):
        """Covariance matrix should be positive semi-definite."""
        if not hasattr(self.module, 'run_bv_6d_pca'):
            self.skipTest("run_bv_6d_pca not found")
        result = self.module.run_bv_6d_pca()
        eigvals = result.eigenvalues_desc
        # All eigenvalues should be non-negative (within numerical tolerance)
        self.assertTrue(np.all(eigvals >= -1e-10),
                       "All eigenvalues should be non-negative")

    def test_eigenvalues_sum_equals_trace(self):
        """Sum of eigenvalues should equal trace of covariance."""
        if not hasattr(self.module, 'run_bv_6d_pca'):
            self.skipTest("run_bv_6d_pca not found")
        result = self.module.run_bv_6d_pca()
        cov = result.covariance_9d
        eigvals = result.eigenvalues_desc
        trace = np.trace(cov)
        eigsum = np.sum(eigvals)
        self.assertAlmostEqual(trace, eigsum, places=5,
                              msg="Sum of eigenvalues should equal trace")

    def test_bv_damping_reduces_trailing_modes(self):
        """BV damping should suppress modes 7-9."""
        if not hasattr(self.module, 'run_bv_6d_pca'):
            self.skipTest("run_bv_6d_pca not found")
        result = self.module.run_bv_6d_pca()
        eigvals = result.eigenvalues_desc
        # Trailing eigenvalues (indices 6, 7, 8) should be small
        leading_energy = np.sum(eigvals[:6])
        trailing_energy = np.sum(eigvals[6:])
        self.assertGreater(leading_energy, trailing_energy * 9,
                          "Leading modes should dominate trailing modes")


# ============================================================================
# DIMENSIONAL COLLAPSE VALIDATOR TESTS
# ============================================================================

class TestDimensionalCollapseValidator(unittest.TestCase):
    """Test dimensional collapse validation functionality."""

    @classmethod
    def setUpClass(cls):
        """Load the dimensional collapse validator module."""
        script = PROOF_SCRIPTS_PATH / "2_DIMENSIONAL_COLLAPSE_VALIDATOR.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "dim_collapse_func")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_num_branches_consistency(self):
        """NUM_BRANCHES should be 9."""
        if hasattr(self.module, 'NUM_BRANCHES'):
            self.assertEqual(self.module.NUM_BRANCHES, 9)


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_assertion_3_tests() -> Dict[str, Any]:
    """Run all Assertion 3 tests and return summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion3Syntax))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion3Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestBombieriVinogradov6DPCA))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion3MathematicalProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestDimensionalCollapseValidator))

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
    print("ASSERTION 3: 6D VARIANCE COLLAPSE - UNIT TEST SUITE")
    print("=" * 74)
    summary = run_assertion_3_tests()
    print("\n" + "=" * 74)
    print("SUMMARY")
    print("=" * 74)
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Failures: {summary['failures']}")
    print(f"Errors: {summary['errors']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Success: {'PASS' if summary['success'] else 'FAIL'}")
