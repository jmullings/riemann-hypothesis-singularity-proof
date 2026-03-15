#!/usr/bin/env python3
"""
test_part_02_pss_sech2_framework.py
=====================================
Unit tests for QED_ASSEMBLY/PART_02_PSS_SECH2_FRAMEWORK.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : main() runs and returns bool
    T3 — Functions : key functions exist and are callable
    T4 — Kernel    : Lambda_H and w_hat_H produce valid outputs
    T5 — Fourier   : Fourier properties verified
    T6 — PSD       : kernel PSD property holds
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "PART_02_PSS_SECH2_FRAMEWORK.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestPart02Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: PART_02_PSS_SECH2_FRAMEWORK.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestPart02Runtime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")


class TestPart02Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_02_PSS_SECH2_FRAMEWORK as mod
        cls.mod = mod

    def test_main_exists_and_returns_bool(self):
        """T3: main() exists and returns bool."""
        self.assertTrue(callable(getattr(self.mod, 'main', None)))
        result = self.mod.main()
        self.assertIsInstance(result, bool)

    def test_main_returns_true(self):
        """T3: main() returns True (all checks pass)."""
        self.assertTrue(self.mod.main())

    def test_lambda_h_exists(self):
        """T3: Lambda_H function exists."""
        self.assertTrue(callable(getattr(self.mod, 'Lambda_H', None)))

    def test_w_hat_h_exists(self):
        """T3: w_hat_H function exists."""
        self.assertTrue(callable(getattr(self.mod, 'w_hat_H', None)))

    def test_build_bn_exists(self):
        """T3: build_bn function exists."""
        self.assertTrue(callable(getattr(self.mod, 'build_bn', None)))


class TestPart02Kernel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_02_PSS_SECH2_FRAMEWORK as mod
        cls.mod = mod

    def test_lambda_h_positive(self):
        """T4: Lambda_H(tau) > 0 for small tau."""
        val = self.mod.Lambda_H(0.0)
        self.assertGreater(val, 0.0)

    def test_lambda_h_symmetric(self):
        """T4: Lambda_H(tau) = Lambda_H(-tau) (even function)."""
        for tau in [0.5, 1.0, 2.0]:
            self.assertAlmostEqual(
                self.mod.Lambda_H(tau), self.mod.Lambda_H(-tau), places=12
            )

    def test_lambda_h_decays(self):
        """T4: Lambda_H decays for large |tau|."""
        self.assertGreater(self.mod.Lambda_H(0.0), self.mod.Lambda_H(5.0))

    def test_w_hat_h_at_zero(self):
        """T4: w_hat_H(0) = 2H = 3.0 for H=1.5."""
        val = self.mod.w_hat_H(0.0, H=1.5)
        self.assertAlmostEqual(val, 3.0, places=6)

    def test_w_hat_h_nonnegative(self):
        """T5: w_hat_H(omega) >= 0 for all omega (PSD kernel)."""
        for omega in np.linspace(0, 10, 50):
            val = self.mod.w_hat_H(omega, H=1.5)
            self.assertGreaterEqual(val, -1e-12,
                                    f"w_hat_H({omega}) = {val} < 0")


class TestPart02Dirichlet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_02_PSS_SECH2_FRAMEWORK as mod
        cls.mod = mod

    def test_build_bn_shape(self):
        """T6: build_bn returns array of length N."""
        bn = self.mod.build_bn(14.134725, 0.5, 30)
        self.assertEqual(len(bn), 30)

    def test_build_bn_finite(self):
        """T6: build_bn returns finite values."""
        bn = self.mod.build_bn(14.134725, 0.5, 30)
        self.assertTrue(np.all(np.isfinite(bn)))


if __name__ == '__main__':
    unittest.main()
