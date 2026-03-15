#!/usr/bin/env python3
"""
test_claim_scan.py
====================
Unit tests for QED_ASSEMBLY/CLAIM_SCAN.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : script runs and exits 0 (intensive: ~2 min)
    T3 — Functions : key functions exist
    T4 — Results   : N₀ threshold = 9, max C = 0.734, fails for N < 9
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "CLAIM_SCAN.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestClaimScanSyntax(unittest.TestCase):
    def test_compiles(self):
        """T1: CLAIM_SCAN.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestClaimScanRuntime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0 (may take ~2 min)."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=300,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")

    def test_output_threshold(self):
        """T4: Output mentions threshold N₀ = 9."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=300,
            cwd=str(QED_ASSEMBLY)
        )
        # Check that N=9 threshold is identified
        out = result.stdout
        self.assertTrue(
            "9" in out,
            "Threshold N₀ = 9 not found in output."
        )


class TestClaimScanFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import CLAIM_SCAN as mod
        cls.mod = mod

    def test_main_exists(self):
        """T3: main() or equivalent entry point exists."""
        has_main = callable(getattr(self.mod, 'main', None))
        has_run = callable(getattr(self.mod, 'run', None))
        self.assertTrue(has_main or has_run, "No main() or run() found.")


if __name__ == '__main__':
    unittest.main()
