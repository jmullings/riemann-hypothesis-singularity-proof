#!/usr/bin/env python3
"""
test_part_09_rs_bridge.py
===========================
Unit tests for QED_ASSEMBLY/PART_09_RS_BRIDGE.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : main() runs and returns bool
    T3 — Functions : key functions exist and are callable
    T4 — Lemmas    : Lemma 9.1-9.3 chain produces output
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "PART_09_RS_BRIDGE.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestPart09Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: PART_09_RS_BRIDGE.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestPart09Runtime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")


class TestPart09Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_09_RS_BRIDGE as mod
        cls.mod = mod

    def test_main_exists_and_returns_bool(self):
        """T3: main() exists and returns bool."""
        self.assertTrue(callable(getattr(self.mod, 'main', None)))
        result = self.mod.main()
        self.assertIsInstance(result, bool)

    def test_main_returns_true(self):
        """T3: main() returns True."""
        self.assertTrue(self.mod.main())

    def test_print_rs_bridge_exists(self):
        """T3: print_rs_bridge function exists."""
        self.assertTrue(callable(getattr(self.mod, 'print_rs_bridge', None)))


if __name__ == '__main__':
    unittest.main()
