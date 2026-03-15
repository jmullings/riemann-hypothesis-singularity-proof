#!/usr/bin/env python3
"""
Simplified Test Suite for FORMAL_PROOF_NEW/AI_PHASES
====================================================

Focus on import tests and basic functionality validation.
Updated for current 10-phase structure (PHASE_01 through PHASE_10).
"""

import os
import sys
import unittest
import importlib

# Add AI_PHASES to path
AI_PHASES_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "..", "..", 
    "FORMAL_PROOF_NEW", "AI_PHASES"
))
if AI_PHASES_DIR not in sys.path:
    sys.path.insert(0, AI_PHASES_DIR)

class PhaseTestCase(unittest.TestCase):
    """Base test case for all phases."""
    
    def import_phase(self, module_name):
        """Helper to import a phase module safely."""
        try:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                __import__(module_name)
            return sys.modules[module_name]
        except ImportError as e:
            self.fail(f"Failed to import {module_name}: {e}")
    
    def get_callable_count(self, module):
        """Count callable functions in module (excluding built-ins)."""
        return len([attr for attr in dir(module) 
                   if callable(getattr(module, attr)) and not attr.startswith('_')])


class TestPhase01Foundations(PhaseTestCase):
    def test_import(self):
        p = self.import_phase('PHASE_01_FOUNDATIONS')
        self.assertTrue(hasattr(p, 'G_PHI'))
        self.assertTrue(hasattr(p, 'ALPHA'))
        self.assertGreater(self.get_callable_count(p), 1)

class TestPhase02Bridge(PhaseTestCase):
    def test_import(self):
        p = self.import_phase('PHASE_02_BRIDGE')
        self.assertTrue(hasattr(p, 'NDIM'))
        self.assertGreater(self.get_callable_count(p), 0)

class TestPhase03PrimeGeometry(PhaseTestCase):
    def test_import(self):
        p = self.import_phase('PHASE_03_PRIME_GEOMETRY')
        self.assertTrue(hasattr(p, 'G_PHI'))
        self.assertGreater(self.get_callable_count(p), 0)

class TestPhase04Evidence(PhaseTestCase):
    def test_import(self):
        p = self.import_phase('PHASE_04_EVIDENCE')
        self.assertTrue(hasattr(p, 'BAND_MAP'))
        self.assertGreater(self.get_callable_count(p), 0)

class TestPhase05UniformBound(PhaseTestCase):
    def test_import(self):
        p = self.import_phase('PHASE_05_UNIFORM_BOUND')
        self.assertTrue(hasattr(p, 'NDIM'))
        self.assertGreater(self.get_callable_count(p), 0)

class TestPhase06AnalyticConvexity(PhaseTestCase):
    def test_import(self):
        p = self.import_phase('PHASE_06_ANALYTIC_CONVEXITY')
        self.assertTrue(hasattr(p, 'fourier_formula_F2bar'))
        self.assertTrue(hasattr(p, 'sech2_fourier'))
        self.assertGreater(self.get_callable_count(p), 5)

class TestPhase07MellinSpectral(PhaseTestCase):
    def test_import(self):
        p = self.import_phase('PHASE_07_MELLIN_SPECTRAL')
        self.assertTrue(hasattr(p, 'build_TH_full'))
        self.assertTrue(hasattr(p, 'mellin_symbol_analytic'))
        self.assertGreater(self.get_callable_count(p), 5)

class TestPhase08ContradictionA3(PhaseTestCase):
    def test_import(self):
        p = self.import_phase('PHASE_08_CONTRADICTION_A3')
        self.assertTrue(hasattr(p, 'E_zeta_RS'))
        self.assertGreater(self.get_callable_count(p), 0)

class TestPhase09PhiCurvature(PhaseTestCase):
    def test_import(self):
        p = self.import_phase('PHASE_09_PHI_CURVATURE')
        self.assertTrue(hasattr(p, 'Lambda_H'))
        self.assertTrue(hasattr(p, 'H_STAR'))
        self.assertGreater(self.get_callable_count(p), 5)

class TestPhase10Completion(PhaseTestCase):
    def test_import(self):
        p = self.import_phase('PHASE_10_COMPLETION')
        self.assertTrue(hasattr(p, 'PHI'))
        self.assertTrue(hasattr(p, 'H_STAR'))
        self.assertGreater(self.get_callable_count(p), 1)


if __name__ == '__main__':
    print(f"Running simplified tests for AI_PHASES in: {AI_PHASES_DIR}")
    print(f"Directory exists: {os.path.exists(AI_PHASES_DIR)}")
    if os.path.exists(AI_PHASES_DIR):
        phase_files = [f for f in os.listdir(AI_PHASES_DIR) 
                       if f.startswith('PHASE_') and f.endswith('.py')]
        print(f"Found {len(phase_files)} phase files")
    
    unittest.main(verbosity=2)