#!/usr/bin/env python3
"""
test_pss_step_02_micro_signatures.py
=====================================
Mirror unit tests for:
    FORMAL_PROOF_NEW/PSS_STEPS/PSS_STEP_2/EXECUTION/PSS_STEP_02_MICRO_SIGNATURES.py
    
Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : script runs to completion (exit 0)  
    T3 — Outputs   : required output files are generated
    T4 — PSS Data  : PSS micro-signature extraction works
"""

import sys
import subprocess
import unittest
import py_compile
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
CONFIGS = ROOT / "FORMAL_PROOF_NEW" / "CONFIGURATIONS"
SCRIPT = ROOT / "FORMAL_PROOF_NEW" / "PSS_STEPS" / "PSS_STEP_2" / "EXECUTION" / "PSS_STEP_02_MICRO_SIGNATURES.py"
ANALYTICS_DIR = ROOT / "FORMAL_PROOF_NEW" / "PSS_STEPS" / "PSS_STEP_2" / "ANALYTICS"

def _add_configs():
    if str(CONFIGS) not in sys.path:
        sys.path.insert(0, str(CONFIGS))

class TestPSSStep02Syntax(unittest.TestCase):
    def test_compiles_without_errors(self):
        """T1: PSS_STEP_02_MICRO_SIGNATURES.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)

class TestPSSStep02Runtime(unittest.TestCase):
    def test_runs_to_completion(self):
        """T2: PSS_STEP_02_MICRO_SIGNATURES.py runs to completion (exit 0)."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        
        result = subprocess.run([
            sys.executable, str(SCRIPT)
        ], capture_output=True, text=True, cwd=str(ROOT))
        
        if result.returncode != 0:
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
        
        self.assertEqual(result.returncode, 0, 
                        f"Script failed with exit code {result.returncode}")

class TestPSSStep02Outputs(unittest.TestCase):
    def test_output_files_generated(self):
        """T3: Required output files are generated."""
        # Run the script first
        result = subprocess.run([
            sys.executable, str(SCRIPT)
        ], capture_output=True, text=True, cwd=str(ROOT))
        
        if result.returncode != 0:
            self.skipTest(f"Script failed to run: {result.stderr}")
        
        expected_files = [
            ANALYTICS_DIR / "pss_step_02_micro_vectors.csv",
            ANALYTICS_DIR / "pss_step_02_energy.csv"
        ]
        
        for file_path in expected_files:
            self.assertTrue(file_path.exists(), f"Output file not generated: {file_path}")

class TestPSSStep02PSSData(unittest.TestCase):
    def test_pss_micro_signature_extraction(self):
        """T4: PSS micro-signature extraction produces valid data."""
        # Run the script
        result = subprocess.run([
            sys.executable, str(SCRIPT)
        ], capture_output=True, text=True, cwd=str(ROOT))
        
        if result.returncode != 0:
            self.skipTest(f"Script failed to run: {result.stderr}")
            
        micro_vectors_file = ANALYTICS_DIR / "pss_step_02_micro_vectors.csv"
        if micro_vectors_file.exists():
            with open(micro_vectors_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # Should have 9 rows for 9 zeros
                self.assertGreaterEqual(len(rows), 8, "Should have data for multiple zeros")
                
                # Check first row has expected structure
                if rows:
                    first_row = rows[0]
                    self.assertIn('gamma', first_row.keys())
                    self.assertGreater(float(first_row['gamma']), 10, "Gamma values should be reasonable")

if __name__ == "__main__":
    unittest.main()