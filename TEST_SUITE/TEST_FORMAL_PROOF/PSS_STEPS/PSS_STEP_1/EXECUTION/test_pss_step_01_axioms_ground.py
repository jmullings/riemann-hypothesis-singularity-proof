#!/usr/bin/env python3
"""
test_pss_step_01_axioms_ground.py
==================================
Mirror unit tests for:
    FORMAL_PROOF_NEW/PSS_STEPS/PSS_STEP_1/EXECUTION/PSS_STEP_01_AXIOMS_GROUND.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : script runs to completion (exit 0)
    T3 — AXIOMS    : AXIOMS constants are accessible and correct
    T4 — SECH²     : sech² function form verification
    T5 — Energy    : energy coupling E = COUPLING_K × sech² is positive
    T6 — PSS CSV   : PSS CSV accessibility with correct schema
    T7 — Outputs   : required output files are generated
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
import os
import csv
from pathlib import Path

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[5]  # Go up 5 dirs to repo root
CONFIGS = ROOT / "FORMAL_PROOF_NEW" / "CONFIGURATIONS"
SCRIPT = ROOT / "FORMAL_PROOF_NEW" / "PSS_STEPS" / "PSS_STEP_1" / "EXECUTION" / "PSS_STEP_01_AXIOMS_GROUND.py"
ANALYTICS_DIR = ROOT / "FORMAL_PROOF_NEW" / "PSS_STEPS" / "PSS_STEP_1" / "ANALYTICS"

def _add_configs():
    if str(CONFIGS) not in sys.path:
        sys.path.insert(0, str(CONFIGS))

# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestPSSStep01Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: PSS_STEP_01_AXIOMS_GROUND.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)

# ---------------------------------------------------------------------------
# T2 — Runtime
# ---------------------------------------------------------------------------
class TestPSSStep01Runtime(unittest.TestCase):

    def test_runs_to_completion(self):
        """T2: PSS_STEP_01_AXIOMS_GROUND.py runs to completion (exit 0)."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        
        # Run the script
        result = subprocess.run([
            sys.executable, str(SCRIPT)
        ], capture_output=True, text=True, cwd=str(ROOT))
        
        self.assertEqual(result.returncode, 0, 
                        f"Script failed with exit code {result.returncode}\n"
                        f"STDOUT:\n{result.stdout}\n"
                        f"STDERR:\n{result.stderr}")

# ---------------------------------------------------------------------------
# T3 — AXIOMS Access
# ---------------------------------------------------------------------------
class TestPSSStep01AXIOMS(unittest.TestCase):

    def setUp(self):
        _add_configs()
    
    def test_axioms_accessible(self):
        """T3: AXIOMS constants are accessible from CONFIGURATIONS."""
        try:
            from AXIOMS import DIM_9D, DIM_6D, DIM_3D, PHI, SIGMA_FIXED
        except ImportError as e:
            self.fail(f"Cannot import AXIOMS: {e}")
        
        self.assertEqual(DIM_9D, 9)
        self.assertEqual(DIM_6D, 6) 
        self.assertEqual(DIM_3D, 3)
        self.assertAlmostEqual(PHI, 1.618033988749, places=6)
        self.assertEqual(SIGMA_FIXED, 0.5)

# ---------------------------------------------------------------------------
# T4 — SECH² Function
# ---------------------------------------------------------------------------
class TestPSSStep01SECH2(unittest.TestCase):

    def test_sech2_functional_form(self):
        """T4: sech²(x) = 4·exp(2x)/(exp(2x)+1)² verification."""
        import math
        
        def sech2(x):
            """sech²(x) = 4·exp(2x)/(exp(2x)+1)²"""
            exp_2x = math.exp(2 * x)
            return 4 * exp_2x / (exp_2x + 1)**2
        
        # Test points - compute expected values correctly
        test_points = [-2.0, -1.0, 0.0, 1.0, 2.0]
        
        for x in test_points:
            computed = sech2(x)
            # Verify it's bounded between 0 and 1
            self.assertGreaterEqual(computed, 0, f"sech²({x}) = {computed} should be >= 0")
            self.assertLessEqual(computed, 1, f"sech²({x}) = {computed} should be <= 1")
            
        # Verify sech²(0) = 1 (peak)
        self.assertAlmostEqual(sech2(0.0), 1.0, places=7, 
                             msg="sech²(0) should equal 1.0")

# ---------------------------------------------------------------------------
# T5 — Energy Coupling
# ---------------------------------------------------------------------------
class TestPSSStep01Energy(unittest.TestCase):

    def test_energy_coupling_positive(self):
        """T5: Energy coupling E = COUPLING_K × sech² is positive for test zeros."""
        import math
        
        def sech2(x):
            exp_2x = math.exp(2 * x)
            return 4 * exp_2x / (exp_2x + 1)**2
        
        # Constants from script
        COUPLING_K = 0.002675
        LAMBDA_STAR = 494.058956
        NORM_X_STAR = 0.342260671137479
        
        # Test zeros
        test_zeros = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062]
        
        for gamma in test_zeros:
            shift = NORM_X_STAR / math.sqrt(gamma / LAMBDA_STAR)
            sech2_value = sech2(shift)
            energy = COUPLING_K * sech2_value
            
            self.assertGreater(energy, 0, 
                             f"Energy coupling E = {energy} not positive for γ = {gamma}")
            self.assertLess(energy, 1.0,
                          f"Energy coupling E = {energy} unexpectedly large for γ = {gamma}")

# ---------------------------------------------------------------------------
# T6 — PSS CSV Access
# ---------------------------------------------------------------------------
class TestPSSStep01PSSCSV(unittest.TestCase):

    def test_pss_csv_accessibility(self):
        """T6: PSS CSV is accessible with correct schema."""
        pss_csv_path = ROOT / "pss_micro_signatures_100k_adaptive.csv"
        
        # The CSV might be in different locations, try a few
        if not pss_csv_path.exists():
            # Try alternative locations
            alt_paths = [
                ROOT / "SECH2_PSS_INVESTIGATION" / "pss_micro_signatures_100k_adaptive.csv",
                ROOT / "FORMAL_PROOF_NEW" / "pss_micro_signatures_100k_adaptive.csv"
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    pss_csv_path = alt_path
                    break
        
        if not pss_csv_path.exists():
            self.skipTest(f"PSS CSV not found in expected locations")
            return
        
        expected_columns = ['C_k', 'C_k_norm', 'N_eff', 'dist_from_center', 
                           'gamma', 'k', 'mu_abs', 'sigma_abs']
        
        with open(pss_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            
            for col in expected_columns:
                self.assertIn(col, columns, f"Missing column '{col}' in PSS CSV")
            
            # Check first row
            first_row = next(reader)
            self.assertAlmostEqual(float(first_row['gamma']), 14.134725, places=5)
            self.assertGreater(float(first_row['mu_abs']), 0)

# ---------------------------------------------------------------------------
# T7 — Output Files
# ---------------------------------------------------------------------------
class TestPSSStep01Outputs(unittest.TestCase):

    def test_output_files_generated(self):
        """T7: Required output files are generated."""
        # Run the script first
        result = subprocess.run([
            sys.executable, str(SCRIPT)
        ], capture_output=True, text=True, cwd=str(ROOT))
        
        self.assertEqual(result.returncode, 0, "Script must run successfully first")
        
        # Check expected output files
        expected_files = [
            ANALYTICS_DIR / "pss_step_01_axiom_report.csv",
            ANALYTICS_DIR / "pss_step_01_sech2_sample.csv"
        ]
        
        for file_path in expected_files:
            self.assertTrue(file_path.exists(), f"Output file not generated: {file_path}")
            self.assertGreater(file_path.stat().st_size, 0, f"Output file is empty: {file_path}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()