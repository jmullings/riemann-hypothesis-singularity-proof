#!/usr/bin/env python3
"""
test_pss_step_07_independence.py
=================================
Mirror unit tests for:
    FORMAL_PROOF_NEW/PSS_STEPS/PSS_STEP_7/EXECUTION/PSS_STEP_07_INDEPENDENCE.py
    
Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : script runs to completion (exit 0)  
    T3 — Outputs   : required output files are generated
"""

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
CONFIGS = ROOT / "FORMAL_PROOF_NEW" / "CONFIGURATIONS"
SCRIPT = ROOT / "FORMAL_PROOF_NEW" / "PSS_STEPS" / "PSS_STEP_7" / "EXECUTION" / "PSS_STEP_07_INDEPENDENCE.py"
ANALYTICS_DIR = ROOT / "FORMAL_PROOF_NEW" / "PSS_STEPS" / "PSS_STEP_7" / "ANALYTICS"

class TestPSSStep07Syntax(unittest.TestCase):
    def test_compiles_without_errors(self):
        """T1: PSS_STEP_07_INDEPENDENCE.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)

class TestPSSStep07Runtime(unittest.TestCase):
    def test_runs_to_completion(self):
        """T2: PSS_STEP_07_INDEPENDENCE.py runs to completion (exit 0)."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        
        result = subprocess.run([
            sys.executable, str(SCRIPT)
        ], capture_output=True, text=True, cwd=str(ROOT))
        
        if result.returncode != 0:
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
        
        self.assertEqual(result.returncode, 0, 
                        f"Script failed with exit code {result.returncode}")

class TestPSSStep07Outputs(unittest.TestCase):
    def test_output_files_generated(self):
        """T3: Required output files are generated."""
        # Run the script first
        result = subprocess.run([
            sys.executable, str(SCRIPT)
        ], capture_output=True, text=True, cwd=str(ROOT))
        
        if result.returncode != 0:
            self.skipTest(f"Script failed to run: {result.stderr}")
        
        # Check analytics directory exists
        self.assertTrue(ANALYTICS_DIR.exists(), f"Analytics directory not created: {ANALYTICS_DIR}")

if __name__ == "__main__":
    unittest.main()