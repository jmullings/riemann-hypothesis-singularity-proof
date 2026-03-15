#!/usr/bin/env python3
"""
test_part_04_classical_backbone.py
====================================
Unit tests for QED_ASSEMBLY/PART_04_CLASSICAL_BACKBONE.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : main() runs and returns bool
    T3 — Functions : key functions exist and are callable
    T4 — Classical : RS bridge, Dirichlet approx, zero counting verified
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "PART_04_CLASSICAL_BACKBONE.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestPart04Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: PART_04_CLASSICAL_BACKBONE.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestPart04Runtime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")


class TestPart04Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_04_CLASSICAL_BACKBONE as mod
        cls.mod = mod

    def test_main_exists_and_returns_bool(self):
        """T3: main() exists and returns bool."""
        self.assertTrue(callable(getattr(self.mod, 'main', None)))
        result = self.mod.main()
        self.assertIsInstance(result, bool)

    def test_main_returns_true(self):
        """T3: main() returns True."""
        self.assertTrue(self.mod.main())

    def test_verify_rs_bridge_exists(self):
        """T3: verify_rs_bridge function exists."""
        self.assertTrue(callable(getattr(self.mod, 'verify_rs_bridge', None)))

    def test_verify_dirichlet_approx_exists(self):
        """T3: verify_dirichlet_approx function exists."""
        self.assertTrue(callable(getattr(self.mod, 'verify_dirichlet_approx', None)))

    def test_verify_zero_counting_exists(self):
        """T3: verify_zero_counting function exists."""
        self.assertTrue(callable(getattr(self.mod, 'verify_zero_counting', None)))


class TestPart04Classical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_04_CLASSICAL_BACKBONE as mod
        cls.mod = mod

    def test_rs_bridge(self):
        """T4: RS bridge verification passes."""
        self.assertTrue(self.mod.verify_rs_bridge())

    def test_dirichlet_approx(self):
        """T4: Dirichlet approximation verification passes."""
        self.assertTrue(self.mod.verify_dirichlet_approx())

    def test_zero_counting(self):
        """T4: Zero counting formula verification passes."""
        self.assertTrue(self.mod.verify_zero_counting())


if __name__ == '__main__':
    unittest.main()
