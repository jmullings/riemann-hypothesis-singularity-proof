#!/usr/bin/env python3
"""
test_part_05_montgomery_vaughan.py
====================================
Unit tests for QED_ASSEMBLY/PART_05_MONTGOMERY_VAUGHAN.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : main() runs and returns bool
    T3 — Functions : key functions exist and are callable
    T4 — Spacing   : MV spacing estimates verified
    T5 — Decay     : off-diagonal exponential decay holds
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "PART_05_MONTGOMERY_VAUGHAN.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestPart05Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: PART_05_MONTGOMERY_VAUGHAN.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestPart05Runtime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")


class TestPart05Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_05_MONTGOMERY_VAUGHAN as mod
        cls.mod = mod

    def test_main_exists_and_returns_bool(self):
        """T3: main() exists and returns bool."""
        self.assertTrue(callable(getattr(self.mod, 'main', None)))
        result = self.mod.main()
        self.assertIsInstance(result, bool)

    def test_main_returns_true(self):
        """T3: main() returns True."""
        self.assertTrue(self.mod.main())

    def test_verify_spacing_exists(self):
        """T3: verify_spacing function exists."""
        self.assertTrue(callable(getattr(self.mod, 'verify_spacing', None)))

    def test_verify_mv_upper_bound_exists(self):
        """T3: verify_mv_upper_bound function exists."""
        self.assertTrue(callable(getattr(self.mod, 'verify_mv_upper_bound', None)))

    def test_verify_offdiag_decay_exists(self):
        """T3: verify_offdiag_decay function exists."""
        self.assertTrue(callable(getattr(self.mod, 'verify_offdiag_decay', None)))


class TestPart05MV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_05_MONTGOMERY_VAUGHAN as mod
        cls.mod = mod

    def test_spacing_verified(self):
        """T4: MV spacing estimates hold."""
        self.assertTrue(self.mod.verify_spacing())

    def test_offdiag_decay(self):
        """T5: Off-diagonal exponential decay holds."""
        self.assertTrue(self.mod.verify_offdiag_decay())


if __name__ == '__main__':
    unittest.main()
