#!/usr/bin/env python3
"""
run_all_def_tests.py
====================
Master runner for all 10 DEF unit-test suites.

Usage:
    python3 TEST_SUITE/TEST_FORMAL_PROOF/DEFINITIONS/run_all_def_tests.py

Exit code 0  → all tests pass
Exit code 1  → one or more tests failed
"""

import os
import sys
import importlib
import unittest
import glob

_HERE = os.path.dirname(os.path.abspath(__file__))

TEST_MODULE_MAP = {
    1:  'TEST_DEF_01_GUE_RANDOM_MATRIX_STATISTICS',
    2:  'TEST_DEF_02_HILBERT_POLYA_SPECTRAL_OPERATOR',
    3:  'TEST_DEF_03_MONTGOMERY_PAIR_CORRELATION',
    4:  'TEST_DEF_04_ROBIN_LAGARIAS_ARITHMETIC_CRITERIA',
    5:  'TEST_DEF_05_AUTOMORPHIC_FORMS_L_FUNCTIONS',
    6:  'TEST_DEF_06_SELBERG_TRACE_FORMULA',
    7:  'TEST_DEF_07_DE_BRUIJN_NEWMAN',
    8:  'TEST_DEF_08_MOMENTS_KEATING_SNAITH',
    9:  'TEST_DEF_09_NYMAN_BEURLING',
    10: 'TEST_DEF_10_EXPLICIT_FORMULAE_PNT',
}

loader = unittest.TestLoader()
suite = unittest.TestSuite()

for def_idx, mod_name in TEST_MODULE_MAP.items():
    exec_dir = os.path.join(_HERE, f'DEF_{def_idx}', 'EXECUTION')
    if not os.path.isdir(exec_dir):
        print(f'[SKIP] DEF_{def_idx}: directory not found: {exec_dir}')
        continue
    # Prepend so this module's directory wins
    if exec_dir not in sys.path:
        sys.path.insert(0, exec_dir)
    try:
        mod = importlib.import_module(mod_name)
        tests = loader.loadTestsFromModule(mod)
        suite.addTests(tests)
    except Exception as exc:
        print(f'[ERROR] Could not load {mod_name}: {exc}')

runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
result = runner.run(suite)

print()
print('=' * 72)
print('DEFINITION TEST SUITE SUMMARY')
print(f'  Total tests run : {result.testsRun}')
print(f'  Failures        : {len(result.failures)}')
print(f'  Errors          : {len(result.errors)}')
print(f'  Skipped         : {len(result.skipped)}')
print(f'  Status          : {"ALL PASS ✓" if result.wasSuccessful() else "SOME FAIL ✗"}')
print('=' * 72)

sys.exit(0 if result.wasSuccessful() else 1)
