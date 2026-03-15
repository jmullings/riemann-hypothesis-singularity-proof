#!/usr/bin/env python3
"""
test_part_03_prime_side_curvature.py
======================================
Unit tests for QED_ASSEMBLY/PART_03_PRIME_SIDE_CURVATURE.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : main() runs and returns bool
    T3 — Functions : key functions exist and are callable
    T4 — Identity  : curvature identity F̄₂ = 2M₁ − 2·cross verified
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "PART_03_PRIME_SIDE_CURVATURE.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestPart03Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: PART_03_PRIME_SIDE_CURVATURE.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestPart03Runtime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")


class TestPart03Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_03_PRIME_SIDE_CURVATURE as mod
        cls.mod = mod

    def test_main_exists_and_returns_bool(self):
        """T3: main() exists and returns bool."""
        self.assertTrue(callable(getattr(self.mod, 'main', None)))
        result = self.mod.main()
        self.assertIsInstance(result, bool)

    def test_main_returns_true(self):
        """T3: main() returns True."""
        self.assertTrue(self.mod.main())

    def test_curvature_identity_exists(self):
        """T3: curvature_identity function exists."""
        self.assertTrue(callable(getattr(self.mod, 'curvature_identity', None)))


class TestPart03Identity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_03_PRIME_SIDE_CURVATURE as mod
        cls.mod = mod

    def test_identity_at_first_zero(self):
        """T4: Curvature identity holds at γ₁ = 14.134725."""
        result = self.mod.curvature_identity(
            T0=14.134725, N=30, H=1.5, sigma=0.5, n_quad=500, tau_max=6.0
        )
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('match', False),
                        f"Identity mismatch: rel_err={result.get('rel_err')}")

    def test_identity_rel_err_small(self):
        """T4: Relative error in identity < 1e-2."""
        result = self.mod.curvature_identity(
            T0=14.134725, N=30, H=1.5, sigma=0.5, n_quad=500, tau_max=6.0
        )
        self.assertLess(abs(result.get('rel_err', 1.0)), 1e-2)

    def test_M1_positive(self):
        """T4: M₁ is positive."""
        result = self.mod.curvature_identity(
            T0=14.134725, N=30, H=1.5, sigma=0.5, n_quad=500, tau_max=6.0
        )
        self.assertGreater(result.get('M1', 0), 0)


if __name__ == '__main__':
    unittest.main()
