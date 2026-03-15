#!/usr/bin/env python3
"""
test_step_07_li_positivity.py
================================
Mirror unit tests for:
    FORMAL_PROOF_NEW/STEPS/STEP_7/EXECUTION/STEP_07_LI_POSITIVITY.py

Test categories:
    T1 — Syntax       : script compiles without errors
    T2 — Runtime      : script runs to completion (exit 0)
    T3 — EQ2 vector   : curvature vector from F2(0.5, Tk) is all positive
    T4 — Alignment    : normalised EQ2 vector has unit norm
    T5 — 9D geometry  : StateFactory + FactoredState9D full_vector has 9 components
    T6 — Covariance   : leading eigenvalue of the 9D covariance matrix > 0
    T7 — CSV output   : step_07_alignment.csv produced with 9 rows
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
SCRIPT    = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_7" / "EXECUTION" / "STEP_07_LI_POSITIVITY.py"
ANALYTICS = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_7" / "ANALYTICS"


def _add_configs():
    if str(CONFIGS) not in sys.path:
        sys.path.insert(0, str(CONFIGS))


# ---------------------------------------------------------------------------
# Inline F2 helper
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


def _D(sigma, T):
    s = complex(sigma, T)
    return sum(p ** (-s) for p in _PRIMES)


def _F2(sigma, T):
    s = complex(sigma, T)
    Dv  = _D(sigma, T)
    dD  = sum(-_LP[p] * p ** (-s) for p in _PRIMES)
    d2D = sum(_LP[p] ** 2 * p ** (-s) for p in _PRIMES)
    return 2 * abs(dD) ** 2 + 2 * (d2D * Dv.conjugate()).real


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestStep07Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: Script compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Runtime
# ---------------------------------------------------------------------------
class TestStep07Runtime(unittest.TestCase):

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
        """T2: Output contains STEP 7 COMPLETE."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=60
        )
        self.assertIn("STEP 7 COMPLETE", result.stdout)


# ---------------------------------------------------------------------------
# T3 — EQ2 curvature vector is all positive
# ---------------------------------------------------------------------------
class TestStep07CurvatureVector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        cls.zeros = RIEMANN_ZEROS_9
        cls.curv  = np.array([_F2(0.5, T) for T in RIEMANN_ZEROS_9])

    def test_all_curvatures_positive(self):
        """T3: F2(0.5, Tk) > 0 for k = 1…9."""
        for k, (T, c) in enumerate(zip(self.zeros, self.curv)):
            self.assertGreater(c, 0.0, f"F2(0.5, T_{k+1}={T:.4f}) = {c} not positive")

    def test_curvature_vector_length(self):
        """T3: Curvature vector has exactly 9 components."""
        self.assertEqual(len(self.curv), 9)

    def test_curvature_first_reference(self):
        """T3: First curvature value in expected range (>1, <1e5)."""
        self.assertGreater(self.curv[0], 1.0)
        self.assertLess(self.curv[0], 1e5)


# ---------------------------------------------------------------------------
# T4 — Normalised EQ2 vector has unit norm
# ---------------------------------------------------------------------------
class TestStep07Normalisation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import RIEMANN_ZEROS_9
        curv = np.array([_F2(0.5, T) for T in RIEMANN_ZEROS_9])
        norm = float(np.linalg.norm(curv))
        cls.x_eq2 = curv / norm

    def test_unit_norm(self):
        """T4: ||x_eq2|| = 1."""
        self.assertAlmostEqual(float(np.linalg.norm(self.x_eq2)), 1.0, places=12)

    def test_all_components_finite(self):
        """T4: All components of x_eq2 are finite."""
        for i, v in enumerate(self.x_eq2):
            self.assertTrue(math.isfinite(v), f"x_eq2[{i}] is not finite")


# ---------------------------------------------------------------------------
# T5 — 9D geometry: StateFactory full_vector has 9 components
# ---------------------------------------------------------------------------
class TestStep07Geometry9D(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import StateFactory, PHI, RIEMANN_ZEROS_9
        cls.factory = StateFactory(phi=PHI)
        cls.zeros   = RIEMANN_ZEROS_9

    def test_full_vector_9_components(self):
        """T5: full_vector has 9 components for each zero height."""
        for T in self.zeros[:3]:
            st = self.factory.create(T)
            self.assertEqual(len(st.full_vector), 9)

    def test_full_vector_all_finite(self):
        """T5: full_vector components are all finite."""
        for T in self.zeros[:3]:
            st = self.factory.create(T)
            for i, v in enumerate(st.full_vector):
                self.assertTrue(math.isfinite(float(v)),
                                f"full_vector[{i}] not finite at T={T}")


# ---------------------------------------------------------------------------
# T6 — Leading eigenvalue of 9D covariance > 0
# ---------------------------------------------------------------------------
class TestStep07Covariance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import StateFactory, PHI, RIEMANN_ZEROS_9
        factory = StateFactory(phi=PHI)
        states  = [factory.create(T) for T in RIEMANN_ZEROS_9]
        full_vecs = np.array([s.full_vector for s in states], dtype=float)
        cov = full_vecs.T @ full_vecs / len(states)
        eigs = np.linalg.eigvalsh(cov)
        cls.leading_eig = float(eigs.max())
        cls.min_eig     = float(eigs.min())

    def test_leading_eigenvalue_positive(self):
        """T6: Leading eigenvalue of 9D covariance matrix > 0."""
        self.assertGreater(self.leading_eig, 0.0)

    def test_all_eigenvalues_non_negative(self):
        """T6: All eigenvalues >= 0 (covariance is PSD)."""
        self.assertGreaterEqual(self.min_eig, -1e-10)


# ---------------------------------------------------------------------------
# T7 — CSV output
# ---------------------------------------------------------------------------
class TestStep07CSV(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, timeout=60)

    def test_csv_exists(self):
        """T7: step_07_alignment.csv is produced."""
        self.assertTrue((ANALYTICS / "step_07_alignment.csv").exists())

    def test_csv_has_9_rows(self):
        """T7: CSV has exactly 9 rows."""
        import csv
        path = ANALYTICS / "step_07_alignment.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 9)

    def test_csv_columns(self):
        """T7: CSV contains expected columns."""
        import csv
        path = ANALYTICS / "step_07_alignment.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            cols = csv.DictReader(f).fieldnames
        for col in ("k", "T_k", "F2_half", "xstar_eq2_k"):
            self.assertIn(col, cols)


if __name__ == "__main__":
    unittest.main(verbosity=2)
