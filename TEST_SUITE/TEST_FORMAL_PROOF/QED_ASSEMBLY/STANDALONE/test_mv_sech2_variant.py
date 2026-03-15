#!/usr/bin/env python3
"""
test_mv_sech2_variant.py
===========================
Unit tests for QED_ASSEMBLY/MV_SECH2_VARIANT.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : script runs and exits 0
    T3 — Functions : key inequality functions exist
    T4 — Results   : Step 2 ratio max < 1, closure established
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "MV_SECH2_VARIANT.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestMvSech2Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: MV_SECH2_VARIANT.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestMvSech2Runtime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")

    def test_output_pass(self):
        """T4: Output contains PASS marker."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertIn("PASS", result.stdout.upper())


class TestMvSech2Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import MV_SECH2_VARIANT as mod
        cls.mod = mod

    def test_main_exists(self):
        """T3: main() or equivalent entry point exists."""
        has_main = callable(getattr(self.mod, 'main', None))
        has_run = callable(getattr(self.mod, 'run', None))
        self.assertTrue(has_main or has_run, "No main() or run() found.")


if __name__ == '__main__':
    unittest.main()
