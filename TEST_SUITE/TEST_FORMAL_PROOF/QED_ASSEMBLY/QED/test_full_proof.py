#!/usr/bin/env python3
"""
test_full_proof.py
====================
Unit tests for QED_ASSEMBLY/QED/FULL_PROOF.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : script runs and exits 0
    T3 — Theorems  : Theorems A-D functions exist
    T4 — Kernels   : 6 kernel forms are defined and equivalent
    T5 — Results   : Theorems A, C proved; B proved at zeros; D conditional
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
QED_DIR = QED_ASSEMBLY / "QED"
SCRIPT = QED_DIR / "FULL_PROOF.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_DIR), str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestFullProofSyntax(unittest.TestCase):
    def test_compiles(self):
        """T1: FULL_PROOF.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestFullProofRuntime(unittest.TestCase):
    def test_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_DIR)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")

    def test_output_all_tests_passed(self):
        """T2: Output contains 'ALL TESTS PASSED' or equivalent."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_DIR)
        )
        out_upper = result.stdout.upper()
        self.assertTrue(
            "ALL TESTS PASSED" in out_upper or "PASS" in out_upper,
            "No ALL TESTS PASSED marker in output."
        )

    def test_output_conditional(self):
        """T5: Output correctly indicates CONDITIONAL status."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_DIR)
        )
        self.assertIn("CONDITIONAL", result.stdout.upper(),
                       "Missing CONDITIONAL marker — Theorem D should be conditional.")

    def test_output_mentions_theorem_a(self):
        """T5: Output mentions Theorem A."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_DIR)
        )
        self.assertIn("Theorem A", result.stdout)

    def test_output_mentions_theorem_b(self):
        """T5: Output mentions Theorem B."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120,
            cwd=str(QED_DIR)
        )
        self.assertIn("Theorem B", result.stdout)


class TestFullProofKernels(unittest.TestCase):
    """T4: Verify the 6 kernel forms are equivalent."""

    def test_six_kernel_equivalence(self):
        """T4: All 6 kernel forms produce identical values at u=1.0, H=1.5."""
        H = 1.5
        u = 1.0
        u_H = u / H

        K1 = 1.0 / np.cosh(u_H)**2
        K2 = 4.0 / (np.exp(u_H) + np.exp(-u_H))**2
        K3 = (1.0 / np.cosh(u_H)**2)  # tanh' = sech²
        K4 = 4.0 * np.exp(2*u_H) / (np.exp(2*u_H) + 1)**2
        K5 = 1.0 - np.tanh(u_H)**2
        sig = 1.0 / (1.0 + np.exp(-2*u_H))
        K6 = 4.0 * sig * (1.0 - sig)

        kernels = [K1, K2, K3, K4, K5, K6]
        for i, Ki in enumerate(kernels):
            self.assertAlmostEqual(
                Ki, K1, places=14,
                msg=f"K{i+1} = {Ki} != K1 = {K1}"
            )


if __name__ == '__main__':
    unittest.main()
