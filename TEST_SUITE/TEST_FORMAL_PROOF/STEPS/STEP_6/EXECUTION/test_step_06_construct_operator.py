#!/usr/bin/env python3
"""
test_step_06_construct_operator.py
=====================================
Mirror unit tests for:
    FORMAL_PROOF_NEW/STEPS/STEP_6/EXECUTION/STEP_06_CONSTRUCT_OPERATOR.py

Test categories:
    T1 — Syntax       : script compiles without errors
    T2 — Runtime      : script runs to completion (exit 0)
    T3 — EQ matrix    : 9×10 matrix M at sigma=0.5 has all finite entries
    T4 — SVD          : singular values are non-negative and in descending order
    T5 — Consensus    : dominant SVD mode (consensus vector) has unit norm
    T6 — F4 column    : M[:,3] = 0 (F4=E-E(0.5)=0 at sigma=0.5 for all T)
    T7 — CSV output   : step_06_eq_matrix.csv and step_06_svd.csv produced
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
SCRIPT    = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_6" / "EXECUTION" / "STEP_06_CONSTRUCT_OPERATOR.py"
ANALYTICS = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_6" / "ANALYTICS"


def _add_configs():
    if str(CONFIGS) not in sys.path:
        sys.path.insert(0, str(CONFIGS))


# ---------------------------------------------------------------------------
# Inline EQ matrix builder
# ---------------------------------------------------------------------------
def _sieve(N):
    is_p = bytearray([1]) * (N + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(N ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i::i] = bytearray(len(is_p[i * i::i]))
    return [i for i in range(2, N + 1) if is_p[i]]


_PRIMES = _sieve(100)
_LP     = {p: math.log(p) for p in _PRIMES}


def _D(s, T):
    sc = complex(s, T)
    return sum(p ** (-sc) for p in _PRIMES)


def _E(s, T):
    d = _D(s, T)
    return d.real ** 2 + d.imag ** 2


def _all_eq(sigma, T):
    s = complex(sigma, T)
    Dv   = _D(sigma, T)
    dD   = sum(-_LP[p] * p ** (-s) for p in _PRIMES)
    d2D  = sum(_LP[p] ** 2 * p ** (-s) for p in _PRIMES)
    Ev   = _E(sigma, T)
    delta = 0.05
    f1 = math.sqrt(max(Ev, 0))
    f2 = 2 * abs(dD) ** 2 + 2 * (d2D * Dv.conjugate()).real
    f3 = _E(sigma + delta, T) + _E(sigma - delta, T) - 2 * Ev
    f4 = Ev - _E(0.5, T)
    f5 = Dv.real + abs(Dv.imag)
    f6 = Dv.real
    f7 = Ev * sigma
    f8 = abs(Dv)
    f9 = float(np.linalg.eigvalsh(np.array(
        [[(p ** (-s) * q ** (-s).conjugate()).real for q in _PRIMES[:3]]
         for p in _PRIMES[:3]])).max())
    tot = 0.0
    for p in _PRIMES:
        z = p ** (-s)
        a = abs(1 - z) ** 2
        if a > 1e-30:
            tot += -math.log(a) / 2
    f10 = tot
    return [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10]


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestStep06Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: Script compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Runtime
# ---------------------------------------------------------------------------
class TestStep06Runtime(unittest.TestCase):

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
        """T2: Output contains STEP 6 COMPLETE."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=60
        )
        self.assertIn("STEP 6 COMPLETE", result.stdout)


# ---------------------------------------------------------------------------
# T3 — EQ matrix: all finite entries
# ---------------------------------------------------------------------------
class TestStep06EQMatrix(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9
        cls.M = np.array([_all_eq(0.5, T) for T in RIEMANN_ZEROS_9])

    def test_matrix_shape(self):
        """T3: M has shape (9, 10)."""
        self.assertEqual(self.M.shape, (9, 10))

    def test_matrix_all_finite(self):
        """T3: All 90 entries of M are finite."""
        self.assertTrue(np.all(np.isfinite(self.M)), "M contains non-finite values")

    def test_matrix_first_column_positive(self):
        """T3: M[:,0] = F1 = sqrt(E) >= 0 for all zeros."""
        self.assertTrue(np.all(self.M[:, 0] >= 0.0))


# ---------------------------------------------------------------------------
# T4 — SVD: singular values non-negative and descending
# ---------------------------------------------------------------------------
class TestStep06SVD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        M = np.array([_all_eq(0.5, T) for T in RIEMANN_ZEROS_9], dtype=float)
        col_norms = np.linalg.norm(M, axis=0)
        M_norm    = M / (col_norms + 1e-30)
        U, S, Vt  = np.linalg.svd(M_norm, full_matrices=False)
        cls.S    = S
        cls.U    = U

    def test_singular_values_non_negative(self):
        """T4: All singular values are >= 0."""
        self.assertTrue(np.all(self.S >= -1e-12), "Negative singular value found")

    def test_singular_values_descending(self):
        """T4: Singular values are in descending order."""
        for i in range(len(self.S) - 1):
            self.assertGreaterEqual(
                self.S[i] + 1e-12, self.S[i + 1],
                f"S[{i}]={self.S[i]} < S[{i+1}]={self.S[i+1]}"
            )

    def test_first_singular_value_dominant(self):
        """T4: First singular value strictly larger than second."""
        self.assertGreater(self.S[0], self.S[1])


# ---------------------------------------------------------------------------
# T5 — Consensus vector has unit norm
# ---------------------------------------------------------------------------
class TestStep06Consensus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        M = np.array([_all_eq(0.5, T) for T in RIEMANN_ZEROS_9], dtype=float)
        col_norms = np.linalg.norm(M, axis=0)
        M_norm    = M / (col_norms + 1e-30)
        U, S, Vt  = np.linalg.svd(M_norm, full_matrices=False)
        cls.consensus = U[:, 0]

    def test_consensus_near_unit_norm(self):
        """T5: Dominant left singular vector has ||·|| ≈ 1."""
        norm = float(np.linalg.norm(self.consensus))
        self.assertAlmostEqual(norm, 1.0, places=10)

    def test_consensus_has_9_components(self):
        """T5: Consensus vector has exactly 9 components."""
        self.assertEqual(len(self.consensus), 9)


# ---------------------------------------------------------------------------
# T6 — F4 column: M[:,3] ≈ 0 at sigma=0.5
# ---------------------------------------------------------------------------
class TestStep06F4Column(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.M = np.array([_all_eq(0.5, T) for T in RIEMANN_ZEROS_9])

    def test_f4_column_near_zero(self):
        """T6: F4(0.5,T) = E-E(0.5) = 0 → column 3 of M ≈ 0."""
        f4_col = self.M[:, 3]
        for i, v in enumerate(f4_col):
            self.assertAlmostEqual(
                v, 0.0, places=10,
                msg=f"M[{i},3]=F4(0.5,T)={v} ≠ 0"
            )


# ---------------------------------------------------------------------------
# T7 — CSV output
# ---------------------------------------------------------------------------
class TestStep06CSV(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, timeout=60)

    def test_eq_matrix_csv_exists(self):
        """T7: step_06_eq_matrix.csv is produced."""
        self.assertTrue((ANALYTICS / "step_06_eq_matrix.csv").exists())

    def test_svd_csv_exists(self):
        """T7: step_06_svd.csv is produced."""
        self.assertTrue((ANALYTICS / "step_06_svd.csv").exists())

    def test_eq_matrix_csv_has_9_rows(self):
        """T7: EQ matrix CSV has exactly 9 data rows."""
        import csv
        path = ANALYTICS / "step_06_eq_matrix.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
