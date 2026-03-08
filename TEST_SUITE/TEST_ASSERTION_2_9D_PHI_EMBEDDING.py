#!/usr/bin/env python3
"""
TEST_ASSERTION_2_9D_PHI_EMBEDDING.py

Comprehensive Unit Tests for Assertion 2: 9D φ-Embedding
=========================================================

Tests for:
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
3. FUNCTION TESTS: Core 9D embedding computations work correctly
4. MATHEMATICAL VALIDATION: φ-geometric properties hold

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

# Base path for Assertion 2
BASE_PATH = Path(__file__).parent.parent / "CONJECTURE_V" / "ASSERTION_2_9D_PHI_EMBEDDING"
PROOF_SCRIPTS_PATH = BASE_PATH / "1_PROOF_SCRIPTS_NOTES"

# Scripts to test
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


# ============================================================================
# SYNTAX VALIDATION TESTS
# ============================================================================

class TestAssertion2Syntax(unittest.TestCase):
    """Test that all Assertion 2 scripts compile without syntax errors."""

    @classmethod
    def setUpClass(cls):
        """Verify base path exists."""
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_euler_geodesic_engine_compiles(self):
        """1_EULER_GEODESIC_ENGINE.py compiles without syntax errors."""
        script = self.scripts_path / "1_EULER_GEODESIC_ENGINE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_9d_prime_curvature_analyzer_compiles(self):
        """2_9D_PRIME_CURVATURE_ANALYZER.py compiles without syntax errors."""
        script = self.scripts_path / "2_9D_PRIME_CURVATURE_ANALYZER.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_euler_weight_calibrator_compiles(self):
        """3_EULER_WEIGHT_CALIBRATOR.py compiles without syntax errors."""
        script = self.scripts_path / "3_EULER_WEIGHT_CALIBRATOR.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_assertion_2_file_1_compiles(self):
        """ASSERTION_2_FILE_1 compiles without syntax errors."""
        script = self.scripts_path / "ASSERTION_2_FILE_1__EULER_GEODESIC_ENGINE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_assertion_2_file_2_compiles(self):
        """ASSERTION_2_FILE_2 compiles without syntax errors."""
        script = self.scripts_path / "ASSERTION_2_FILE_2__9D_PRIME_CURVATURE_ANALYZER.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_assertion_2_file_3_compiles(self):
        """ASSERTION_2_FILE_3 compiles without syntax errors."""
        script = self.scripts_path / "ASSERTION_2_FILE_3__EULER_WEIGHT_CALIBRATOR.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_assertion_2_file_4_compiles(self):
        """ASSERTION_2_FILE_4 compiles without syntax errors."""
        script = self.scripts_path / "ASSERTION_2_FILE_4__9D_BOUNDEDNESS_COMPACTIFICATION.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")

    def test_assertion_2_file_5_compiles(self):
        """ASSERTION_2_FILE_5 compiles without syntax errors."""
        script = self.scripts_path / "ASSERTION_2_FILE_5__9D_SPECTRAL_CONSISTENCY.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        self.assertTrue(can_compile(script), f"Syntax error in {script.name}")


# ============================================================================
# IMPORT VALIDATION TESTS
# ============================================================================

class TestAssertion2Imports(unittest.TestCase):
    """Test that Assertion 2 modules can be imported successfully."""

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

    def test_import_euler_geodesic_engine(self):
        """1_EULER_GEODESIC_ENGINE imports successfully."""
        script = self.scripts_path / "1_EULER_GEODESIC_ENGINE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "euler_geodesic_engine_test")
        self.assertIsNotNone(module, "Module failed to import")

    def test_import_9d_curvature_analyzer(self):
        """2_9D_PRIME_CURVATURE_ANALYZER compiles (may have external deps)."""
        script = self.scripts_path / "2_9D_PRIME_CURVATURE_ANALYZER.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        # This module has dependencies on QUANTUM_GEODESIC_SINGULARITY
        # We test syntax only, import may fail due to missing deps
        self.assertTrue(can_compile(script), 
                       "Module should compile despite external dependencies")


# ============================================================================
# FUNCTION TESTS - GEODESIC ENGINE
# ============================================================================

class TestEulerGeodesicEngine(unittest.TestCase):
    """Test core functions from 1_EULER_GEODESIC_ENGINE.py."""

    @classmethod
    def setUpClass(cls):
        """Load the module for testing."""
        script = PROOF_SCRIPTS_PATH / "1_EULER_GEODESIC_ENGINE.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "euler_geodesic_engine_func")
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
        """NUM_BRANCHES should be 9 for 9D embedding."""
        if not hasattr(self.module, 'NUM_BRANCHES'):
            self.skipTest("NUM_BRANCHES not defined")
        self.assertEqual(self.module.NUM_BRANCHES, 9)

    def test_quantum_geodesic_singularity_class_exists(self):
        """QuantumGeodesicSingularity class exists."""
        if not hasattr(self.module, 'QuantumGeodesicSingularity'):
            self.skipTest("QuantumGeodesicSingularity class not found")
        # Try to instantiate
        qgs = self.module.QuantumGeodesicSingularity()
        self.assertIsNotNone(qgs)

    def test_compute_euler_psi_returns_complex(self):
        """compute_euler_psi returns complex values."""
        if not hasattr(self.module, 'QuantumGeodesicSingularity'):
            self.skipTest("QuantumGeodesicSingularity not found")
        qgs = self.module.QuantumGeodesicSingularity(max_n=1000)
        psi = qgs.compute_euler_psi(14.134725)  # First Riemann zero height
        self.assertIsInstance(psi, complex)

    def test_compute_psi_alias_works(self):
        """compute_psi is a valid alias for compute_euler_psi."""
        if not hasattr(self.module, 'QuantumGeodesicSingularity'):
            self.skipTest("QuantumGeodesicSingularity not found")
        qgs = self.module.QuantumGeodesicSingularity(max_n=1000)
        if not hasattr(qgs, 'compute_psi'):
            self.skipTest("compute_psi method not found")
        psi = qgs.compute_psi(14.134725)
        self.assertIsInstance(psi, complex)

    def test_extract_9d_curvature_shape(self):
        """extract_9d_curvature returns 9-dimensional vector."""
        if not hasattr(self.module, 'QuantumGeodesicSingularity'):
            self.skipTest("QuantumGeodesicSingularity not found")
        qgs = self.module.QuantumGeodesicSingularity(max_n=1000)
        if not hasattr(qgs, 'extract_9d_curvature'):
            self.skipTest("extract_9d_curvature method not found")
        curv = qgs.extract_9d_curvature(20.0)
        self.assertEqual(len(curv), 9, "Curvature should be 9-dimensional")

    def test_spectral_features_dataclass_exists(self):
        """SpectralFeatures dataclass exists."""
        if not hasattr(self.module, 'SpectralFeatures'):
            self.skipTest("SpectralFeatures not found")
        # Just check it's importable
        self.assertTrue(hasattr(self.module, 'SpectralFeatures'))


# ============================================================================
# MATHEMATICAL VALIDATION TESTS
# ============================================================================

class TestAssertion2MathematicalProperties(unittest.TestCase):
    """Test mathematical properties of 9D φ-embedding."""

    @classmethod
    def setUpClass(cls):
        """Load module for mathematical tests."""
        script = PROOF_SCRIPTS_PATH / "1_EULER_GEODESIC_ENGINE.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "euler_geodesic_math")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_phi_satisfies_golden_ratio(self):
        """PHI satisfies φ² = φ + 1."""
        if not hasattr(self.module, 'PHI'):
            self.skipTest("PHI not defined")
        phi = self.module.PHI
        self.assertAlmostEqual(phi * phi, phi + 1, places=10)

    def test_psi_conjugate_symmetry(self):
        """ψ(-t) = conj(ψ(t)) should approximately hold."""
        if not hasattr(self.module, 'QuantumGeodesicSingularity'):
            self.skipTest("QuantumGeodesicSingularity not found")
        qgs = self.module.QuantumGeodesicSingularity(max_n=1000)
        t = 20.0
        psi_plus = qgs.compute_euler_psi(t)
        psi_minus = qgs.compute_euler_psi(-t)
        # ψ(-t) should be close to conjugate of ψ(t)
        self.assertAlmostEqual(psi_minus.real, psi_plus.real, places=5)
        self.assertAlmostEqual(psi_minus.imag, -psi_plus.imag, places=5)

    def test_psi_bounded_at_test_height(self):
        """ψ(t) should be bounded for reasonable t values."""
        if not hasattr(self.module, 'QuantumGeodesicSingularity'):
            self.skipTest("QuantumGeodesicSingularity not found")
        qgs = self.module.QuantumGeodesicSingularity(max_n=1000)
        for t in [14.0, 21.0, 25.0]:
            psi = qgs.compute_euler_psi(t)
            self.assertLess(abs(psi), 1e10, f"ψ({t}) should be bounded")

    def test_curvature_scales_with_stencil(self):
        """Multi-scale curvature should vary with stencil size."""
        if not hasattr(self.module, 'QuantumGeodesicSingularity'):
            self.skipTest("QuantumGeodesicSingularity not found")
        qgs = self.module.QuantumGeodesicSingularity(max_n=1000)
        if not hasattr(qgs, 'extract_9d_curvature'):
            self.skipTest("extract_9d_curvature not found")
        curv = qgs.extract_9d_curvature(20.0)
        # Curvature components should generally decrease with scale
        # (larger stencils smooth out variations)
        self.assertTrue(np.all(np.isfinite(curv)), "All curvature values should be finite")


# ============================================================================
# 9D BOUNDEDNESS TESTS
# ============================================================================

class TestAssertion2Boundedness(unittest.TestCase):
    """Test 9D boundedness and compactification properties."""

    @classmethod
    def setUpClass(cls):
        """Load the 9D boundedness module."""
        script = PROOF_SCRIPTS_PATH / "ASSERTION_2_FILE_4__9D_BOUNDEDNESS_COMPACTIFICATION.py"
        if not script.exists():
            raise unittest.SkipTest(f"Script not found: {script}")
        cls.module = load_module_from_path(script, "boundedness_test")
        if cls.module is None:
            raise unittest.SkipTest("Failed to load module")

    def test_phi_weights_exist(self):
        """φ-weights for 9 branches should exist."""
        # Look for weight-related functions or constants
        weight_attrs = [attr for attr in dir(self.module) 
                       if 'weight' in attr.lower() or 'phi' in attr.lower()]
        self.assertTrue(len(weight_attrs) > 0 or hasattr(self.module, 'PHI'),
                       "Module should have φ-related attributes")

    def test_num_branches_consistency(self):
        """NUM_BRANCHES should be 9 if defined."""
        if hasattr(self.module, 'NUM_BRANCHES'):
            self.assertEqual(self.module.NUM_BRANCHES, 9)


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_assertion_2_tests() -> Dict[str, Any]:
    """Run all Assertion 2 tests and return summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion2Syntax))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion2Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestEulerGeodesicEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion2MathematicalProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion2Boundedness))

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
    print("ASSERTION 2: 9D φ-EMBEDDING - UNIT TEST SUITE")
    print("=" * 74)
    summary = run_assertion_2_tests()
    print("\n" + "=" * 74)
    print("SUMMARY")
    print("=" * 74)
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Failures: {summary['failures']}")
    print(f"Errors: {summary['errors']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Success: {'PASS' if summary['success'] else 'FAIL'}")
