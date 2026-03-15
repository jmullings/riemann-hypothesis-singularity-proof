#!/usr/bin/env python3
"""
Test Suite for AI_PHASES Scripts
=================================

Real unit tests for all phase scripts in FORMAL_PROOF_NEW/AI_PHASES/
Tests import, basic functionality, and key exports.
Updated for current 10-phase structure (PHASE_01 through PHASE_10).
"""

import unittest
import sys
import os
import io
import contextlib
from typing import Any, Dict

# Add AI_PHASES to path
AI_PHASES_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "..", "..", 
    "FORMAL_PROOF_NEW", "AI_PHASES"
))
if AI_PHASES_DIR not in sys.path:
    sys.path.insert(0, AI_PHASES_DIR)


class PhaseTestCase(unittest.TestCase):
    """Base test case for phase scripts."""
    
    def assert_module_importable(self, module_name: str) -> Any:
        """Test that a module can be imported without error."""
        try:
            module = __import__(module_name)
            self.assertIsNotNone(module, f"Module {module_name} imported as None")
            return module
        except Exception as e:
            self.fail(f"Failed to import {module_name}: {e}")
    
    def capture_output(self, func):
        """Capture stdout/stderr from a function."""
        stdout_cap = io.StringIO()
        stderr_cap = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_cap), \
                 contextlib.redirect_stderr(stderr_cap):
                result = func()
            return result, stdout_cap.getvalue(), stderr_cap.getvalue()
        except Exception as e:
            return None, stdout_cap.getvalue(), str(e)


class TestPhase01Foundations(PhaseTestCase):
    """Test PHASE_01_FOUNDATIONS.py - Foundation constants and metrics."""
    
    def test_import_and_constants(self):
        """Test basic import and key constants."""
        p = self.assert_module_importable("PHASE_01_FOUNDATIONS")
        
        # Check key constants exist
        self.assertTrue(hasattr(p, 'ALPHA'))
        self.assertTrue(hasattr(p, 'BETA'))
        self.assertTrue(hasattr(p, 'G_PHI'))
        self.assertTrue(hasattr(p, 'BITSIZE'))
        
        # Check G_PHI is a matrix
        self.assertEqual(p.G_PHI.shape, (9, 9))
    
    def test_key_functions(self):
        """Test key functions exist and are callable."""
        p = self.assert_module_importable("PHASE_01_FOUNDATIONS")
        self.assertTrue(callable(getattr(p, 'E_S_energy', None)))
        self.assertTrue(callable(getattr(p, 'F2_S_curvature', None)))
        self.assertTrue(callable(getattr(p, 'D_complex', None)))


class TestPhase02Bridge(PhaseTestCase):
    """Test PHASE_02_BRIDGE.py - Bridge computations."""
    
    def test_import_and_constants(self):
        """Test import and key constants."""
        p = self.assert_module_importable("PHASE_02_BRIDGE")
        
        self.assertTrue(hasattr(p, 'NDIM'))
        self.assertTrue(hasattr(p, 'ZEROS_30'))
        self.assertTrue(hasattr(p, 'ZEROS_9'))
        self.assertEqual(len(p.ZEROS_9), 9)
    
    def test_key_functions(self):
        """Test key functions exist."""
        p = self.assert_module_importable("PHASE_02_BRIDGE")
        self.assertTrue(callable(getattr(p, 'E_S', None)))
        self.assertTrue(callable(getattr(p, 'F2_S', None)))
        self.assertTrue(callable(getattr(p, 'S_N', None)))


class TestPhase03PrimeGeometry(PhaseTestCase):
    """Test PHASE_03_PRIME_GEOMETRY.py - Prime geometry."""
    
    def test_import_and_constants(self):
        """Test import and key constants."""
        p = self.assert_module_importable("PHASE_03_PRIME_GEOMETRY")
        
        self.assertTrue(hasattr(p, 'ALPHA'))
        self.assertTrue(hasattr(p, 'ALPHA_SECH'))
        self.assertTrue(hasattr(p, 'G_PHI'))
    
    def test_key_functions(self):
        """Test key functions exist."""
        p = self.assert_module_importable("PHASE_03_PRIME_GEOMETRY")
        self.assertTrue(callable(getattr(p, 'F2_curvature', None)))
        self.assertTrue(callable(getattr(p, 'bitsize_curvature_normalised', None)))


class TestPhase04Evidence(PhaseTestCase):
    """Test PHASE_04_EVIDENCE.py - Evidence and classification."""
    
    def test_import_and_constants(self):
        """Test import and key constants."""
        p = self.assert_module_importable("PHASE_04_EVIDENCE")
        
        self.assertTrue(hasattr(p, 'BANDS_PRESENT'))
        self.assertTrue(hasattr(p, 'BAND_MAP'))
    
    def test_key_functions(self):
        """Test key functions exist."""
        p = self.assert_module_importable("PHASE_04_EVIDENCE")
        self.assertTrue(callable(getattr(p, 'classify_result', None)))
        self.assertTrue(callable(getattr(p, 'F2_band', None)))


class TestPhase05UniformBound(PhaseTestCase):
    """Test PHASE_05_UNIFORM_BOUND.py - Uniform bound analysis."""
    
    def test_import_and_constants(self):
        """Test import and key constants."""
        p = self.assert_module_importable("PHASE_05_UNIFORM_BOUND")
        
        self.assertTrue(hasattr(p, 'NDIM'))
        self.assertTrue(hasattr(p, 'ZEROS_30'))
    
    def test_key_functions(self):
        """Test key functions exist."""
        p = self.assert_module_importable("PHASE_05_UNIFORM_BOUND")
        self.assertTrue(callable(getattr(p, 'averaged_F2', None)))
        self.assertTrue(callable(getattr(p, 'run_phase_05', None)))


class TestPhase06AnalyticConvexity(PhaseTestCase):
    """Test PHASE_06_ANALYTIC_CONVEXITY.py - Analytic convexity."""
    
    def test_import_and_functions(self):
        """Test import and analytic convexity functions."""
        p = self.assert_module_importable("PHASE_06_ANALYTIC_CONVEXITY")
        
        self.assertTrue(callable(getattr(p, 'sech2_fourier', None)))
        self.assertTrue(callable(getattr(p, 'mv_diagonal', None)))
        self.assertTrue(callable(getattr(p, 'fourier_formula_F2bar', None)))
        self.assertTrue(callable(getattr(p, 'run_phase_06', None)))
        
        # Test basic function
        sf = p.sech2_fourier(1.0, 1.5)
        self.assertIsInstance(sf, float)
        self.assertGreater(sf, 0)


class TestPhase07MellinSpectral(PhaseTestCase):
    """Test PHASE_07_MELLIN_SPECTRAL.py - Mellin spectral analysis."""
    
    def test_import_and_functions(self):
        """Test import and Mellin spectral functions."""
        p = self.assert_module_importable("PHASE_07_MELLIN_SPECTRAL")
        
        self.assertTrue(callable(getattr(p, 'sech2_fourier', None)))
        self.assertTrue(callable(getattr(p, 'mellin_symbol_analytic', None)))
        self.assertTrue(callable(getattr(p, 'build_TH_full', None)))
        self.assertTrue(callable(getattr(p, 'run_phase_07', None)))
        
        # Test function
        msa = p.mellin_symbol_analytic(0.5, 1.5)
        self.assertIsInstance(msa, float)


class TestPhase08ContradictionA3(PhaseTestCase):
    """Test PHASE_08_CONTRADICTION_A3.py - A3 contradiction."""
    
    def test_import_and_functions(self):
        """Test import and A3 functions."""
        p = self.assert_module_importable("PHASE_08_CONTRADICTION_A3")
        
        self.assertTrue(callable(getattr(p, 'E_zeta_RS', None)))
        self.assertTrue(callable(getattr(p, 'absolute_value_bound', None)))
        self.assertTrue(callable(getattr(p, 'averaged_energy', None)))


class TestPhase09PhiCurvature(PhaseTestCase):
    """Test PHASE_09_PHI_CURVATURE.py - φ-Curvature theorem."""
    
    def test_import_and_functions(self):
        """Test import and φ-curvature functions."""
        p = self.assert_module_importable("PHASE_09_PHI_CURVATURE")
        
        self.assertTrue(hasattr(p, 'H_STAR'))
        self.assertTrue(callable(getattr(p, 'Lambda_H', None)))
        self.assertTrue(callable(getattr(p, 'Lambda_H_pp', None)))
        self.assertTrue(callable(getattr(p, 'build_TH_full', None)))
        
        # Test core function
        lh = p.Lambda_H(0.5)
        self.assertIsInstance(lh, float)
        self.assertGreater(lh, 0)


class TestPhase10Completion(PhaseTestCase):
    """Test PHASE_10_COMPLETION.py - Completion theorem."""
    
    def test_import_and_constants(self):
        """Test import and key constants."""
        p = self.assert_module_importable("PHASE_10_COMPLETION")
        
        self.assertTrue(hasattr(p, 'PHI'))
        self.assertTrue(hasattr(p, 'H_STAR'))
        self.assertTrue(hasattr(p, 'NDIM'))
        self.assertTrue(hasattr(p, 'G_PHI'))
    
    def test_key_functions(self):
        """Test key functions exist."""
        p = self.assert_module_importable("PHASE_10_COMPLETION")
        self.assertTrue(callable(getattr(p, 'E_S_energy', None)))
        self.assertTrue(callable(getattr(p, 'F2_S_curvature', None)))
        self.assertTrue(callable(getattr(p, 'averaged_F2', None)))


class TestPhaseIntegration(PhaseTestCase):
    """Integration tests across multiple phases."""
    
    def test_phase_dependencies(self):
        """Test that phases with dependencies import correctly."""
        # Phase 02 depends on Phase 01
        p1 = __import__("PHASE_01_FOUNDATIONS")
        p2 = __import__("PHASE_02_BRIDGE")
        
        # Both should have ZEROS_9
        self.assertTrue(hasattr(p2, 'ZEROS_9'))
        self.assertEqual(len(p2.ZEROS_9), 9)
        
        # Phase 09 should have H_STAR
        p9 = __import__("PHASE_09_PHI_CURVATURE")
        self.assertTrue(hasattr(p9, 'H_STAR'))
        
        # Phase 10 should have constants from earlier phases
        p10 = __import__("PHASE_10_COMPLETION")
        self.assertTrue(hasattr(p10, 'H_STAR'))
        self.assertTrue(hasattr(p10, 'PHI'))


if __name__ == '__main__':
    # Configure test output
    unittest.main(verbosity=2, buffer=True)