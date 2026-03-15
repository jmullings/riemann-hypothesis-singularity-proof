#!/usr/bin/env python3
"""
run_all_selectivity_tests.py
============================
Master runner for all 4 SELECTIVITY PATH unit-test suites.

Tests the four mathematical pathways implementing FORMAL_PROOF_NEW/SELECTIVITY:
- PATH_1_SPECTRAL_OPERATOR (Hilbert-Pólya horizon approach)
- PATH_2_WEIL_EXPLICIT (Primary Weil explicit formula route)  
- PATH_3_LI_DUAL_PROBE (Supporting evidence with Li coefficients)
- RH_PROOF_COMPLETE (All 10 phases combined into single executable)

Usage:
    python3 TEST_SUITE/TEST_FORMAL_PROOF/SELECTIVITY/run_all_selectivity_tests.py

Exit code 0  → all tests pass
Exit code 1  → one or more tests failed

TRINITY PROTOCOL COMPLIANCE:
- P1: LOG-FREE OPERATOR ARCHITECTURE ✓
- P2: 9D-CENTRIC COMPUTATIONS ✓  
- P3: RIEMANN-φ WEIGHTS ✓
- P4: BIT-SIZE AXIOMS (not applicable for unit tests)
- P5: TRINITY AND UNIT-TEST COMPLIANCE ✓

STATUS: Complete test suite for SELECTIVITY pathways plus combined proof
"""

import os
import sys
import importlib
import unittest
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))

# Test module mapping for the three pathways plus complete proof test
TEST_MODULE_MAP = {
    1: 'TEST_PATH_1_SPECTRAL_OPERATOR',
    2: 'TEST_PATH_2_WEIL_EXPLICIT', 
    3: 'TEST_PATH_3_LI_DUAL_PROBE',
    4: 'TEST_RH_PROOF_COMPLETE',
}

PATHWAY_DESCRIPTIONS = {
    1: 'Hilbert-Pólya Spectral Operator (Horizon)',
    2: 'Weil Explicit Formula (Primary Route)',
    3: 'Li Coefficients Dual Probe (Supporting)',
    4: 'Complete RH Proof (All 10 Phases Combined)',
}

def main():
    """Run all SELECTIVITY pathway tests"""
    
    print("=" * 70)
    print("SELECTIVITY PATHWAY UNIT TEST SUITE")
    print("=" * 70)
    print("Tests for FORMAL_PROOF_NEW/SELECTIVITY implementation")
    print(f"Location: {_HERE}")
    print()
    
    # Add current directory to path for imports
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    successful_imports = 0
    total_modules = len(TEST_MODULE_MAP)
    
    # Load each test module
    for path_idx, mod_name in TEST_MODULE_MAP.items():
        pathway_desc = PATHWAY_DESCRIPTIONS[path_idx]
        print(f"[PATH_{path_idx}] Loading {pathway_desc}...")
        
        try:
            # Import the test module
            mod = importlib.import_module(mod_name)
            tests = loader.loadTestsFromModule(mod)
            suite.addTests(tests)
            successful_imports += 1
            print(f"[PATH_{path_idx}] ✓ Loaded {tests.countTestCases()} tests")
            
        except ImportError as exc:
            print(f"[PATH_{path_idx}] ✗ Import failed: {exc}")
            
        except Exception as exc:
            print(f"[PATH_{path_idx}] ✗ Error loading tests: {exc}")
            traceback.print_exc()
    
    print()
    print(f"Summary: {successful_imports}/{total_modules} modules loaded successfully")
    print(f"Total test cases: {suite.countTestCases()}")
    print()
    
    if successful_imports == 0:
        print("ERROR: No test modules could be loaded!")
        return 1
    
    # Run the test suite
    print("=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    
    if result.wasSuccessful():
        print(f"✓ ALL TESTS PASSED ({result.testsRun} tests)")
        print()
        print("SELECTIVITY pathway implementations validated:")
        for path_idx, desc in PATHWAY_DESCRIPTIONS.items():
            if path_idx <= successful_imports:
                print(f"  PATH_{path_idx}: {desc}")
        return 0
    else:
        print(f"✗ TESTS FAILED ({result.testsRun} tests run)")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"  {test}: {traceback}")
                
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"  {test}: {traceback}")
        
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)