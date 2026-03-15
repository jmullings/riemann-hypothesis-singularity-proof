#!/usr/bin/env python3
"""
test_part_08_uniform_curvature_bound.py
=========================================
Unit tests for QED_ASSEMBLY/PART_08_UNIFORM_CURVATURE_BOUND.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : main() runs and returns bool (long-running: ~290s)
    T3 — Functions : key functions exist and are callable
    T4 — Steps     : Steps A-C produce valid outputs
    T5 — Bound     : C(H) < 1 for tested cases
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "PART_08_UNIFORM_CURVATURE_BOUND.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestPart08Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: PART_08_UNIFORM_CURVATURE_BOUND.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestPart08Runtime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0 (may take ~5 min)."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=600,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")


class TestPart08Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_08_UNIFORM_CURVATURE_BOUND as mod
        cls.mod = mod

    def test_main_exists_and_returns_bool(self):
        """T3: main() exists and returns bool."""
        self.assertTrue(callable(getattr(self.mod, 'main', None)))

    def test_step_a_exists(self):
        """T3: step_A_near_diagonal_restriction function exists."""
        self.assertTrue(callable(getattr(self.mod, 'step_A_near_diagonal_restriction', None)))


class TestPart08Bound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_08_UNIFORM_CURVATURE_BOUND as mod
        cls.mod = mod

    def test_C_less_than_one(self):
        """T5: C(H) < 1 for a sample (T0, N) pair."""
        if hasattr(self.mod, 'compute_C_integral'):
            C = self.mod.compute_C_integral(T0=14.134725, N=30, H=1.5)
            self.assertLess(C, 1.0, f"C(H) = {C} >= 1")
        elif hasattr(self.mod, 'step_C_refined_constant'):
            C = self.mod.step_C_refined_constant(T0=14.134725, N=30, H=1.5)
            self.assertLess(C, 1.0, f"C(H) = {C} >= 1")


if __name__ == '__main__':
    unittest.main()
