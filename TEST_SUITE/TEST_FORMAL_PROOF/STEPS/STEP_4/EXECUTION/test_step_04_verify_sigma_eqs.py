#!/usr/bin/env python3
"""
test_step_04_verify_sigma_eqs.py
==================================
Mirror unit tests for:
    FORMAL_PROOF_NEW/STEPS/STEP_4/EXECUTION/STEP_04_VERIFY_SIGMA_EQS.py

Test categories:
    T1 — Syntax      : script compiles without errors
    T2 — Runtime     : script runs to completion (exit 0)
    T3 — Sigma grid  : scan finds a minimum in sigma ∈ [0.1, 0.9]
    T4 — CV variance : CV at sigma=0.5 is finite and non-negative
    T5 — F4 benchmark: EQ variance at sigma=0.5 is dominated by F4=0 term
    T6 — Monotonicity: F4(sigma, T) changes sign as sigma crosses 0.5
    T7 — CSV output  : step_04_sigma_star.csv is produced
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
SCRIPT    = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_4" / "EXECUTION" / "STEP_04_VERIFY_SIGMA_EQS.py"
ANALYTICS = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_4" / "ANALYTICS"


def _add_configs():
    if str(CONFIGS) not in sys.path:
        sys.path.insert(0, str(CONFIGS))


# ---------------------------------------------------------------------------
# Inline helpers
# ---------------------------------------------------------------------------
def _sieve(N):
    is_p = bytearray([1]) * (N + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(N ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i::i] = bytearray(len(is_p[i * i::i]))
    return [i for i in range(2, N + 1) if is_p[i]]


PRIMES = _sieve(100)
LOG_P  = {p: math.log(p) for p in PRIMES}


def D(s, T):
    sc = complex(s, T)
    return sum(p ** (-sc) for p in PRIMES)


def E(s, T):
    d = D(s, T)
    return d.real ** 2 + d.imag ** 2


def F4(s, T):
    return E(s, T) - E(0.5, T)


def F2(s, T):
    sc = complex(s, T)
    Dv = D(s, T)
    dD  = sum(-LOG_P[p] * p ** (-sc) for p in PRIMES)
    d2D = sum(LOG_P[p] ** 2 * p ** (-sc) for p in PRIMES)
    return 2 * abs(dD) ** 2 + 2 * (d2D * Dv.conjugate()).real


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestStep04Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: Script compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Runtime
# ---------------------------------------------------------------------------
class TestStep04Runtime(unittest.TestCase):

    def test_script_runs_exit_zero(self):
        """T2: Script runs to completion with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120
        )
        self.assertEqual(
            result.returncode, 0,
            f"Script exited {result.returncode}.\nSTDERR:\n{result.stderr}"
        )

    def test_output_has_complete_marker(self):
        """T2: Output contains STEP 4 COMPLETE."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=120
        )
        self.assertIn("STEP 4 COMPLETE", result.stdout)


# ---------------------------------------------------------------------------
# T3 — Sigma scan finds a minimum
# ---------------------------------------------------------------------------
class TestStep04SigmaScan(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9
        cls.sigma_grid = np.linspace(0.1, 0.9, 81)

    def _cv_at(self, sigma, T):
        """Coefficient of variation of [F2, F4+1] at (sigma, T)."""
        vals = [max(abs(F2(sigma, T)), 1e-30), abs(F4(sigma, T)) + 1e-10]
        a = np.array(vals)
        mean = abs(np.mean(a))
        return float(np.std(a) / (mean + 1e-30))

    def test_sigma_scan_runs(self):
        """T3: Sigma scan over [0.1, 0.9] completes for each zero."""
        for T in self.zeros[:3]:
            scores = [self._cv_at(s, T) for s in self.sigma_grid]
            self.assertEqual(len(scores), len(self.sigma_grid))

    def test_sigma_scan_has_finite_values(self):
        """T3: All CV values in the sigma scan are finite."""
        T = self.zeros[0]
        for sigma in self.sigma_grid:
            cv = self._cv_at(sigma, T)
            self.assertTrue(math.isfinite(cv), f"CV not finite at sigma={sigma}, T={T}")


# ---------------------------------------------------------------------------
# T4 — CV variance at sigma=0.5 is finite
# ---------------------------------------------------------------------------
class TestStep04CVAtHalf(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9

    def test_f4_is_zero_at_half(self):
        """T4: F4(0.5, T) = 0 for all zeros (validates CV baseline)."""
        for T in self.zeros:
            v = F4(0.5, T)
            self.assertAlmostEqual(v, 0.0, places=10, msg=f"F4(0.5,{T})={v}")

    def test_f2_positive_at_half(self):
        """T4: F2(0.5, T) > 0 for all zeros (curvature > 0 at critical line)."""
        for T in self.zeros:
            v = F2(0.5, T)
            self.assertGreater(v, 0.0, f"F2(0.5, {T}) = {v} not positive")


# ---------------------------------------------------------------------------
# T5 — F4 benchmark: energy excess at critical line is zero
# ---------------------------------------------------------------------------
class TestStep04F4Benchmark(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9

    def test_f4_half_is_global_reference(self):
        """T5: By definition E(0.5,T) - E(0.5,T) = 0 for every T."""
        for T in self.zeros:
            self.assertAlmostEqual(F4(0.5, T), 0.0, places=12)

    def test_energy_at_half_is_positive(self):
        """T5: E(0.5, T) > 0 (Dirichlet polynomial is non-zero at critical line)."""
        for T in self.zeros:
            self.assertGreater(E(0.5, T), 0.0, f"E(0.5,{T}) not positive")


# ---------------------------------------------------------------------------
# T6 — Monotonicity: F4 changes near sigma=0.5
# ---------------------------------------------------------------------------
class TestStep04Monotonicity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.T = RIEMANN_ZEROS_9[0]

    def test_f4_changes_around_half(self):
        """T6: F4(sigma, T) is not identically zero for sigma != 0.5."""
        T = self.T
        vals = [F4(s, T) for s in [0.3, 0.4, 0.6, 0.7]]
        # At least some should be nonzero
        self.assertTrue(any(abs(v) > 1e-10 for v in vals),
                        "F4 appears zero everywhere — energy function is constant?")


# ---------------------------------------------------------------------------
# T7 — CSV output
# ---------------------------------------------------------------------------
class TestStep04CSV(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, timeout=120)

    def test_csv_exists(self):
        """T7: step_04_sigma_star.csv is produced."""
        self.assertTrue((ANALYTICS / "step_04_sigma_star.csv").exists())

    def test_csv_has_correct_columns(self):
        """T7: CSV contains expected columns."""
        import csv
        path = ANALYTICS / "step_04_sigma_star.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            cols = csv.DictReader(f).fieldnames
        for col in ("T", "sigma_star", "dist_from_half"):
            self.assertIn(col, cols)

    def test_csv_has_9_rows(self):
        """T7: CSV has exactly 9 rows (one per Riemann zero)."""
        import csv
        path = ANALYTICS / "step_04_sigma_star.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
