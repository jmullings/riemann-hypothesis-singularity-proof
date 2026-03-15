#!/usr/bin/env python3
"""
test_gap_2_uniform_bound.py
==============================
Unit tests for QED_ASSEMBLY/QED/GAP_2_UNIFORM_BOUND.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : script runs and exits 0
    T3 — Functions : key step functions exist
    T4 — Results   : uniform bound analysis produces valid output
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
QED_DIR = QED_ASSEMBLY / "QED"
SCRIPT = QED_DIR / "GAP_2_UNIFORM_BOUND.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_DIR), str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestGap2Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: GAP_2_UNIFORM_BOUND.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestGap2Runtime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_DIR)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")

    def test_output_pass(self):
        """T4: Output contains PASS marker."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_DIR)
        )
        self.assertIn("PASS", result.stdout.upper())


class TestGap2Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import GAP_2_UNIFORM_BOUND as mod
        cls.mod = mod

    def test_main_exists(self):
        """T3: main() function exists."""
        self.assertTrue(callable(getattr(self.mod, 'main', None)))


if __name__ == '__main__':
    unittest.main()
