#!/usr/bin/env python3
"""
test_part_01_rh_statement.py
==============================
Unit tests for QED_ASSEMBLY/PART_01_RH_STATEMENT.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : main() runs and returns bool
    T3 — Functions : key functions exist and are callable
    T4 — Curvature : curvature_at_zeros returns valid data
    T5 — Statement : RH statement prints without error
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "PART_01_RH_STATEMENT.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestPart01Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: PART_01_RH_STATEMENT.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestPart01Runtime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(
            result.returncode, 0,
            f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}"
        )

    def test_output_contains_pass(self):
        """T2: Script output contains PASS or pass markers."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_ASSEMBLY)
        )
        out = result.stdout.upper()
        self.assertTrue(
            "PASS" in out or "✓" in result.stdout or "TRUE" in out,
            "No PASS/✓ marker found in output."
        )


class TestPart01Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_01_RH_STATEMENT as mod
        cls.mod = mod

    def test_main_exists(self):
        """T3: main() function exists."""
        self.assertTrue(callable(getattr(self.mod, 'main', None)))

    def test_main_returns_bool(self):
        """T3: main() returns a boolean."""
        result = self.mod.main()
        self.assertIsInstance(result, bool)

    def test_main_returns_true(self):
        """T3: main() returns True (all tests pass)."""
        self.assertTrue(self.mod.main())

    def test_print_statement_exists(self):
        """T3: print_statement() function exists."""
        self.assertTrue(callable(getattr(self.mod, 'print_statement', None)))

    def test_curvature_at_zeros_exists(self):
        """T3: curvature_at_zeros() function exists."""
        self.assertTrue(callable(getattr(self.mod, 'curvature_at_zeros', None)))


class TestPart01Curvature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_01_RH_STATEMENT as mod
        cls.mod = mod

    def test_curvature_returns_list(self):
        """T4: curvature_at_zeros() returns a list."""
        result = self.mod.curvature_at_zeros(N=30, n_quad=500, tau_max=6.0)
        self.assertIsInstance(result, list)

    def test_curvature_nonempty(self):
        """T4: curvature_at_zeros() returns non-empty results."""
        result = self.mod.curvature_at_zeros(N=30, n_quad=500, tau_max=6.0)
        self.assertGreater(len(result), 0)

    def test_curvature_all_hold(self):
        """T4: All curvature checks hold at known zeros."""
        result = self.mod.curvature_at_zeros(N=30, n_quad=500, tau_max=6.0)
        for entry in result:
            self.assertTrue(entry.get('holds', False),
                            f"Curvature check failed at γ={entry.get('gamma')}")


if __name__ == '__main__':
    unittest.main()
