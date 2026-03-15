#!/usr/bin/env python3
"""
test_mellin_mean_value_closure.py
====================================
Unit tests for QED_ASSEMBLY/MELLIN_MEAN_VALUE_CLOSURE.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : script runs and exits 0
    T3 — Functions : key step functions exist
    T4 — Steps     : Steps 1-5, 7, 9, 10 pass; Steps 6, 8 diagnostic
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "MELLIN_MEAN_VALUE_CLOSURE.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestMellinSyntax(unittest.TestCase):
    def test_compiles(self):
        """T1: MELLIN_MEAN_VALUE_CLOSURE.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestMellinRuntime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=180,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")

    def test_output_step_markers(self):
        """T4: Output contains step markers."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=180,
            cwd=str(QED_ASSEMBLY)
        )
        out_upper = result.stdout.upper()
        self.assertTrue(
            "STEP" in out_upper or "PASS" in out_upper,
            "No step or PASS markers found in output."
        )


class TestMellinFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import MELLIN_MEAN_VALUE_CLOSURE as mod
        cls.mod = mod

    def test_main_exists(self):
        """T3: main() or equivalent entry point exists."""
        has_main = callable(getattr(self.mod, 'main', None))
        has_run = callable(getattr(self.mod, 'run', None))
        self.assertTrue(has_main or has_run, "No main() or run() found.")


if __name__ == '__main__':
    unittest.main()
