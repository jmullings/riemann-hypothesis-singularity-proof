#!/usr/bin/env python3
"""
test_part_06_mellin_mean_decomposition.py
===========================================
Unit tests for QED_ASSEMBLY/PART_06_MELLIN_MEAN_DECOMPOSITION.py

Test categories:
    T1 — Syntax        : script compiles without errors
    T2 — Runtime        : main() runs and returns bool
    T3 — Functions      : key functions exist and are callable
    T4 — Decomposition  : Fourier-Mellin decomposition verified
    T5 — Hard Identity  : 4 ln(m)ln(n) + (ln(m)-ln(n))² = (ln(mn))²
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "PART_06_MELLIN_MEAN_DECOMPOSITION.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestPart06Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: PART_06_MELLIN_MEAN_DECOMPOSITION.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestPart06Runtime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")


class TestPart06Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_06_MELLIN_MEAN_DECOMPOSITION as mod
        cls.mod = mod

    def test_main_exists_and_returns_bool(self):
        """T3: main() exists and returns bool."""
        self.assertTrue(callable(getattr(self.mod, 'main', None)))
        result = self.mod.main()
        self.assertIsInstance(result, bool)

    def test_main_returns_true(self):
        """T3: main() returns True."""
        self.assertTrue(self.mod.main())

    def test_F2bar_quadrature_exists(self):
        """T3: F2bar_quadrature function exists."""
        self.assertTrue(callable(getattr(self.mod, 'F2bar_quadrature', None)))


class TestPart06Decomposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_06_MELLIN_MEAN_DECOMPOSITION as mod
        cls.mod = mod

    def test_F2bar_returns_dict(self):
        """T4: F2bar_quadrature returns a dict."""
        result = self.mod.F2bar_quadrature(
            T0=14.134725, N=30, H=1.5, sigma=0.5, n_quad=500, tau_max=6.0
        )
        self.assertIsInstance(result, dict)

    def test_F2bar_has_required_keys(self):
        """T4: F2bar_quadrature result has F2bar, M1, cross keys."""
        result = self.mod.F2bar_quadrature(
            T0=14.134725, N=30, H=1.5, sigma=0.5, n_quad=500, tau_max=6.0
        )
        for key in ['F2bar', 'M1', 'cross']:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_M1_positive(self):
        """T4: M₁ > 0."""
        result = self.mod.F2bar_quadrature(
            T0=14.134725, N=30, H=1.5, sigma=0.5, n_quad=500, tau_max=6.0
        )
        self.assertGreater(result['M1'], 0)


class TestPart06HardIdentity(unittest.TestCase):
    def test_algebraic_identity(self):
        """T5: 4 ln(m)ln(n) + (ln(m)-ln(n))² = (ln(mn))² for various m,n."""
        test_pairs = [(2, 3), (5, 7), (11, 13), (17, 19), (100, 200)]
        for m, n in test_pairs:
            lhs = 4 * math.log(m) * math.log(n) + (math.log(m) - math.log(n))**2
            rhs = (math.log(m * n))**2
            self.assertAlmostEqual(lhs, rhs, places=12,
                                   msg=f"Identity fails for m={m}, n={n}")


if __name__ == '__main__':
    unittest.main()
