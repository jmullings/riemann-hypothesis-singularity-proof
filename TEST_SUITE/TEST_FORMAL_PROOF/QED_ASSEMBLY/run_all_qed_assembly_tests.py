#!/usr/bin/env python3
"""
run_all_qed_assembly_tests.py
================================
Discovers and runs all unit tests for QED_ASSEMBLY scripts.

Usage:
    python3 run_all_qed_assembly_tests.py              # all tests
    python3 run_all_qed_assembly_tests.py --fast        # syntax + function tests only (skip runtime)
    python3 run_all_qed_assembly_tests.py --parts-only  # PART tests only
    python3 run_all_qed_assembly_tests.py --qed-only    # QED/ tests only
"""

from __future__ import annotations

import sys
import unittest
import argparse
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Run QED_ASSEMBLY unit tests")
    parser.add_argument('--fast', action='store_true',
                        help='Skip long-running runtime tests')
    parser.add_argument('--parts-only', action='store_true',
                        help='Run only PART tests')
    parser.add_argument('--qed-only', action='store_true',
                        help='Run only QED/ tests')
    parser.add_argument('--standalone-only', action='store_true',
                        help='Run only standalone script tests')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    args = parser.parse_args()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    dirs = []
    if args.parts_only:
        dirs = [TEST_DIR / "PARTS"]
    elif args.qed_only:
        dirs = [TEST_DIR / "QED"]
    elif args.standalone_only:
        dirs = [TEST_DIR / "STANDALONE"]
    else:
        dirs = [TEST_DIR / "PARTS", TEST_DIR / "QED", TEST_DIR / "STANDALONE"]

    for d in dirs:
        if d.exists():
            discovered = loader.discover(
                str(d), pattern="test_*.py", top_level_dir=str(TEST_DIR)
            )
            suite.addTests(discovered)

    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
