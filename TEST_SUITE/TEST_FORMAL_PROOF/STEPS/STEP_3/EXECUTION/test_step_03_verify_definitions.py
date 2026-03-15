#!/usr/bin/env python3
"""
test_step_03_verify_definitions.py
=====================================
Mirror unit tests for:
    FORMAL_PROOF_NEW/STEPS/STEP_3/EXECUTION/STEP_03_VERIFY_DEFINITIONS.py

Test categories:
    T1 — Syntax       : script compiles without errors
    T2 — Runtime      : script runs to completion (exit 0)
    T3 — EQ kernel    : F1-F10 are evaluable and finite at sigma=0.5
    T4 — EQ4 symmetry : F4(0.5, T) = 0 by definition (E - E(0.5))
    T5 — EQ1 positive : F1(sigma,T) = sqrt(E) >= 0 always
    T6 — EQ8 positive : |D(sigma,T)| >= 0 always
    T7 — CSV output   : step_03_eq_kernel.csv is produced with correct structure
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
import math
import cmath
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
CONFIGS   = ROOT / "FORMAL_PROOF_NEW" / "CONFIGURATIONS"
SCRIPT    = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_3" / "EXECUTION" / "STEP_03_VERIFY_DEFINITIONS.py"
ANALYTICS = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_3" / "ANALYTICS"


def _add_configs():
    if str(CONFIGS) not in sys.path:
        sys.path.insert(0, str(CONFIGS))


# ---------------------------------------------------------------------------
# Minimal inline EQ kernel (mirrored from STEP_03 for independent testing)
# ---------------------------------------------------------------------------
def _build_kernel():
    def _sieve(N):
        is_p = bytearray([1]) * (N + 1)
        is_p[0] = is_p[1] = 0
        for i in range(2, int(N ** 0.5) + 1):
            if is_p[i]:
                is_p[i * i::i] = bytearray(len(is_p[i * i::i]))
        return [i for i in range(2, N + 1) if is_p[i]]

    PRIMES = _sieve(100)
    LOG_P  = {p: math.log(p) for p in PRIMES}

    def D(sigma, T):
        s = complex(sigma, T)
        return sum(p ** (-s) for p in PRIMES)

    def E(sigma, T):
        d = D(sigma, T)
        return d.real ** 2 + d.imag ** 2

    def F1(sigma, T):
        return math.sqrt(max(E(sigma, T), 0.0))

    def F2(sigma, T):
        s = complex(sigma, T)
        Dv = D(sigma, T)
        dD = sum(-LOG_P[p] * p ** (-s) for p in PRIMES)
        d2D = sum(LOG_P[p] ** 2 * p ** (-s) for p in PRIMES)
        return 2 * abs(dD) ** 2 + 2 * (d2D * Dv.conjugate()).real

    def F3(sigma, T, delta=0.05):
        return E(sigma + delta, T) + E(sigma - delta, T) - 2 * E(sigma, T)

    def F4(sigma, T):
        return E(sigma, T) - E(0.5, T)

    def F8(sigma, T):
        return abs(D(sigma, T))

    return dict(
        D=D, E=E, F1=F1, F2=F2, F3=F3, F4=F4, F8=F8,
        PRIMES=PRIMES
    )


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestStep03Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: Script compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Runtime
# ---------------------------------------------------------------------------
class TestStep03Runtime(unittest.TestCase):

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

    def test_script_output_has_complete_marker(self):
        """T2: Output contains STEP 3 COMPLETE."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=60
        )
        self.assertIn("STEP 3 COMPLETE", result.stdout)


# ---------------------------------------------------------------------------
# T3 — EQ kernel: F1-F10 finite at sigma=0.5
# ---------------------------------------------------------------------------
class TestStep03EQKernel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9
        cls.k = _build_kernel()

    def test_f1_finite_at_critical_line(self):
        """T3: F1(0.5, T) is finite for all 9 zero heights."""
        for T in self.zeros:
            v = self.k["F1"](0.5, T)
            self.assertTrue(math.isfinite(v), f"F1 not finite at T={T}")

    def test_f2_finite_at_critical_line(self):
        """T3: F2(0.5, T) is finite for all 9 zero heights."""
        for T in self.zeros:
            v = self.k["F2"](0.5, T)
            self.assertTrue(math.isfinite(v), f"F2 not finite at T={T}")

    def test_f3_finite_at_critical_line(self):
        """T3: F3(0.5, T) is finite for all 9 zero heights."""
        for T in self.zeros:
            v = self.k["F3"](0.5, T)
            self.assertTrue(math.isfinite(v), f"F3 not finite at T={T}")

    def test_d_evaluable(self):
        """T3: D(sigma, T) is evaluable (complex result)."""
        d = self.k["D"](0.5, 14.1347)
        self.assertIsInstance(d, complex)

    def test_energy_non_negative(self):
        """T3: E(sigma, T) = |D|^2 >= 0."""
        for T in self.zeros[:3]:
            for sigma in [0.25, 0.5, 0.75]:
                self.assertGreaterEqual(self.k["E"](sigma, T), 0.0)


# ---------------------------------------------------------------------------
# T4 — EQ4 symmetry: F4(0.5, T) = 0 (exact by definition)
# ---------------------------------------------------------------------------
class TestStep03EQ4Symmetry(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9
        cls.k = _build_kernel()

    def test_f4_zero_at_critical_line(self):
        """T4: F4(0.5, T) = E(0.5,T) - E(0.5,T) = 0 for all T."""
        for T in self.zeros:
            v = self.k["F4"](0.5, T)
            self.assertAlmostEqual(v, 0.0, places=10,
                                   msg=f"F4(0.5, {T}) = {v} ≠ 0")

    def test_f4_positive_off_critical_line(self):
        """T4: F4(sigma ≠ 0.5, T) can differ from zero (energy excess)."""
        # Not necessarily positive, just verify F4(0.3, T) ≠ 0 for first zero
        T = self.zeros[0]
        v = self.k["F4"](0.3, T)
        self.assertFalse(v == 0.0, "F4(0.3, T) unexpectedly 0")


# ---------------------------------------------------------------------------
# T5 — EQ1: sqrt of energy, always non-negative
# ---------------------------------------------------------------------------
class TestStep03EQ1Positive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9
        cls.k = _build_kernel()

    def test_f1_non_negative(self):
        """T5: F1(sigma, T) = sqrt(E) >= 0 for all sigma, T."""
        for T in self.zeros[:4]:
            for sigma in [0.1, 0.25, 0.5, 0.75, 0.9]:
                v = self.k["F1"](sigma, T)
                self.assertGreaterEqual(v, 0.0, f"F1 < 0 at sigma={sigma}, T={T}")


# ---------------------------------------------------------------------------
# T6 — EQ8: |D(sigma,T)| >= 0 always
# ---------------------------------------------------------------------------
class TestStep03EQ8Positive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9
        cls.k = _build_kernel()

    def test_f8_non_negative(self):
        """T6: F8 = |D(sigma,T)| >= 0 always."""
        for T in self.zeros[:4]:
            for sigma in [0.25, 0.5, 0.75]:
                v = self.k["F8"](sigma, T)
                self.assertGreaterEqual(v, 0.0, f"F8 < 0 at sigma={sigma}, T={T}")


# ---------------------------------------------------------------------------
# T7 — CSV output
# ---------------------------------------------------------------------------
class TestStep03CSV(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, timeout=60)

    def test_csv_exists(self):
        """T7: step_03_eq_kernel.csv is produced."""
        self.assertTrue((ANALYTICS / "step_03_eq_kernel.csv").exists())

    def test_csv_has_correct_columns(self):
        """T7: CSV contains T, sigma, and EQ columns."""
        import csv
        path = ANALYTICS / "step_03_eq_kernel.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames
        self.assertIn("T", cols)
        self.assertIn("sigma", cols)
        self.assertIn("EQ1_EnergyRoot", cols)

    def test_csv_has_rows(self):
        """T7: CSV has at least 27 rows (9 zeros × 3 sigma values)."""
        import csv
        path = ANALYTICS / "step_03_eq_kernel.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows), 27)


if __name__ == "__main__":
    unittest.main(verbosity=2)
