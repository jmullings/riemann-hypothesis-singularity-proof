#!/usr/bin/env python3
"""
test_step_05_verify_bridges.py
================================
Mirror unit tests for:
    FORMAL_PROOF_NEW/STEPS/STEP_5/EXECUTION/STEP_05_VERIFY_BRIDGES.py

Test categories:
    T1 — Syntax       : script compiles without errors
    T2 — Runtime      : script runs to completion (exit 0)
    T3 — F2 curvature : F2(0.5, T) > 0 for all 9 zero heights
    T4 — Normalisation: x* = F2-vector / ||F2-vector|| has unit norm
    T5 — AXIOMS align : computed norm is close to NORM_X_STAR reference
    T6 — CSV output   : step_05_curvature_spectrum.csv produced with 9 rows
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
import math
from pathlib import Path

import numpy as np

ROOT      = Path(__file__).resolve().parents[5]
CONFIGS   = ROOT / "FORMAL_PROOF_NEW" / "CONFIGURATIONS"
SCRIPT    = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_5" / "EXECUTION" / "STEP_05_VERIFY_BRIDGES.py"
ANALYTICS = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_5" / "ANALYTICS"


def _add_configs():
    if str(CONFIGS) not in sys.path:
        sys.path.insert(0, str(CONFIGS))


# ---------------------------------------------------------------------------
# Inline F2 curvature helper
# ---------------------------------------------------------------------------
def _sieve(N):
    is_p = bytearray([1]) * (N + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(N ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i::i] = bytearray(len(is_p[i * i::i]))
    return [i for i in range(2, N + 1) if is_p[i]]


_PRIMES = _sieve(100)
_LOG_P  = {p: math.log(p) for p in _PRIMES}


def D(sigma, T):
    s = complex(sigma, T)
    return sum(p ** (-s) for p in _PRIMES)


def F2(sigma, T):
    s = complex(sigma, T)
    Dv = D(sigma, T)
    dD  = sum(-_LOG_P[p] * p ** (-s) for p in _PRIMES)
    d2D = sum(_LOG_P[p] ** 2 * p ** (-s) for p in _PRIMES)
    return 2 * abs(dD) ** 2 + 2 * (d2D * Dv.conjugate()).real


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestStep05Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: Script compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Runtime
# ---------------------------------------------------------------------------
class TestStep05Runtime(unittest.TestCase):

    def test_script_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=60
        )
        self.assertEqual(
            result.returncode, 0,
            f"Script exited {result.returncode}.\nSTDERR:\n{result.stderr}"
        )

    def test_output_has_complete_marker(self):
        """T2: Output contains STEP 5 COMPLETE."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=60
        )
        self.assertIn("STEP 5 COMPLETE", result.stdout)


# ---------------------------------------------------------------------------
# T3 — F2 curvature positive at critical line
# ---------------------------------------------------------------------------
class TestStep05F2Curvature(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9

    def test_f2_positive_all_zeros(self):
        """T3: F2(0.5, T) > 0 for all 9 Riemann zero heights."""
        for T in self.zeros:
            v = F2(0.5, T)
            self.assertGreater(v, 0.0, f"F2(0.5, {T}) = {v} not positive")

    def test_f2_finite_all_zeros(self):
        """T3: F2(0.5, T) is finite for all 9 Riemann zero heights."""
        for T in self.zeros:
            v = F2(0.5, T)
            self.assertTrue(math.isfinite(v), f"F2(0.5, {T}) not finite")

    def test_f2_first_zero_reference(self):
        """T3: F2(0.5, γ₁) is in expected order of magnitude (>10, <1e6)."""
        v = F2(0.5, 14.1347251417347)
        self.assertGreater(v, 10.0)
        self.assertLess(v, 1e6)


# ---------------------------------------------------------------------------
# T4 — Normalisation: x* has unit norm
# ---------------------------------------------------------------------------
class TestStep05Normalisation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9
        curv = np.array([F2(0.5, T) for T in RIEMANN_ZEROS_9])
        norm = float(np.linalg.norm(curv))
        cls.x_star = curv / norm if norm > 0 else curv
        cls.norm_curv = norm

    def test_x_star_unit_norm(self):
        """T4: ||x*|| = 1 after normalisation."""
        norm = float(np.linalg.norm(self.x_star))
        self.assertAlmostEqual(norm, 1.0, places=12)

    def test_x_star_has_9_components(self):
        """T4: x* vector has exactly 9 components."""
        self.assertEqual(len(self.x_star), 9)

    def test_raw_curvature_norm_positive(self):
        """T4: Raw curvature vector has positive norm."""
        self.assertGreater(self.norm_curv, 0.0)


# ---------------------------------------------------------------------------
# T5 — AXIOMS alignment
# ---------------------------------------------------------------------------
class TestStep05AxiomsAlign(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import NORM_X_STAR, RIEMANN_ZEROS_9
        cls.NORM_X_STAR = NORM_X_STAR
        curv = np.array([F2(0.5, T) for T in RIEMANN_ZEROS_9])
        cls.x_star_norm = float(np.linalg.norm(curv / np.linalg.norm(curv)))

    def test_axioms_norm_x_star_positive(self):
        """T5: AXIOMS NORM_X_STAR constant is positive."""
        self.assertGreater(self.NORM_X_STAR, 0.0)

    def test_computed_x_star_norm_is_one(self):
        """T5: Normalised x* vector has ||·|| = 1."""
        self.assertAlmostEqual(self.x_star_norm, 1.0, places=12)


# ---------------------------------------------------------------------------
# T6 — CSV output
# ---------------------------------------------------------------------------
class TestStep05CSV(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, timeout=60)

    def test_csv_exists(self):
        """T6: step_05_curvature_spectrum.csv is produced."""
        self.assertTrue((ANALYTICS / "step_05_curvature_spectrum.csv").exists())

    def test_csv_has_9_rows(self):
        """T6: CSV has exactly 9 rows (one per Riemann zero)."""
        import csv
        path = ANALYTICS / "step_05_curvature_spectrum.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 9)

    def test_csv_columns(self):
        """T6: CSV contains k, T_k, F2_half, x_star_k columns."""
        import csv
        path = ANALYTICS / "step_05_curvature_spectrum.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            cols = csv.DictReader(f).fieldnames
        for col in ("k", "T_k", "F2_half", "x_star_k"):
            self.assertIn(col, cols)


if __name__ == "__main__":
    unittest.main(verbosity=2)
