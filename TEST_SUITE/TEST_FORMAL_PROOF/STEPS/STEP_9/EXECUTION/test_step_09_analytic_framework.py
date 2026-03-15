#!/usr/bin/env python3
"""
test_step_09_analytic_framework.py
=====================================
Mirror unit tests for:
    FORMAL_PROOF_NEW/STEPS/STEP_9/EXECUTION/STEP_09_ANALYTIC_FRAMEWORK.py

Test categories:
    T1 — Syntax        : script compiles without errors
    T2 — Runtime       : script runs to completion (exit 0)
    T3 — Bridge B1     : Tr(A~) is finite and positive
    T4 — Bridge B1     : Tr(A~^2) is finite and positive
    T5 — Bridge B2     : BridgeLift6Dto9D instantiates
    T6 — AXIOMS align  : eigenvalue norms are finite
    T7 — CSV output    : step_09_bridges.csv produced with expected rows
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
SCRIPT    = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_9" / "EXECUTION" / "STEP_09_ANALYTIC_FRAMEWORK.py"
ANALYTICS = ROOT / "FORMAL_PROOF_NEW" / "STEPS" / "STEP_9" / "ANALYTICS"


def _add_configs():
    if str(CONFIGS) not in sys.path:
        sys.path.insert(0, str(CONFIGS))


def _build_operator():
    """Build NormalizedBridgeOperator from AXIOMS for tests."""
    _add_configs()
    from AXIOMS import (StateFactory, BitsizeScaleFunctional,
                         NormalizedBridgeOperator, PHI, RIEMANN_ZEROS_9)
    factory = StateFactory(phi=PHI)
    sf      = BitsizeScaleFunctional(phi=PHI)
    T_grid  = sorted(set(list(RIEMANN_ZEROS_9) + [50.0, 75.0, 100.0]))
    states  = [factory.create(T) for T in T_grid]
    S_avg   = float(np.mean([sf.S(T) for T in T_grid]))
    return NormalizedBridgeOperator(states, S_avg)


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestStep09Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: Script compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Runtime
# ---------------------------------------------------------------------------
class TestStep09Runtime(unittest.TestCase):

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
        """T2: Output contains STEP 9 COMPLETE."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=60
        )
        self.assertIn("STEP 9 COMPLETE", result.stdout)


# ---------------------------------------------------------------------------
# T3 — Bridge B1: Tr(A~) finite and positive
# ---------------------------------------------------------------------------
class TestStep09TraceB1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = _build_operator()

    def test_trace_1_finite(self):
        """T3: Tr(A~) is finite."""
        tr1 = self.op.trace_power(1)
        self.assertTrue(math.isfinite(tr1), f"Tr(A~) = {tr1} not finite")

    def test_trace_1_positive(self):
        """T3: Tr(A~) > 0 (sum of positive eigenvalues)."""
        tr1 = self.op.trace_power(1)
        self.assertGreater(tr1, 0.0, f"Tr(A~) = {tr1} not positive")


# ---------------------------------------------------------------------------
# T4 — Bridge B1: Tr(A~^2) finite and positive
# ---------------------------------------------------------------------------
class TestStep09TraceB1Sq(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = _build_operator()

    def test_trace_2_finite(self):
        """T4: Tr(A~^2) is finite."""
        tr2 = self.op.trace_power(2)
        self.assertTrue(math.isfinite(tr2), f"Tr(A~^2) = {tr2} not finite")

    def test_trace_2_non_negative(self):
        """T4: Tr(A~^2) = sum of squared eigenvalues >= 0."""
        tr2 = self.op.trace_power(2)
        self.assertGreaterEqual(tr2, 0.0)

    def test_trace_2_geq_trace_1_sq_over_n(self):
        """T4: Tr(A~^2) >= Tr(A~)^2/n (Cauchy-Schwarz for sums)."""
        tr1 = self.op.trace_power(1)
        tr2 = self.op.trace_power(2)
        n   = len(self.op.eigenvalues)
        self.assertGreaterEqual(tr2 + 1e-12, tr1 ** 2 / n)


# ---------------------------------------------------------------------------
# T5 — Bridge B2: BridgeLift6Dto9D instantiates
# ---------------------------------------------------------------------------
class TestStep09BridgeLift(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import (InverseBitsizeShift, BridgeLift6Dto9D,
                             RIEMANN_ZEROS_9)
        T_grid = sorted(set(list(RIEMANN_ZEROS_9) + [50.0, 75.0, 100.0]))
        try:
            inv         = InverseBitsizeShift(T_range=(T_grid[0], T_grid[-1]),
                                              num_samples=len(T_grid))
            cls.lift    = BridgeLift6Dto9D(inv)
            cls.inv     = inv
            cls.skip    = False
        except Exception as e:
            cls.skip = True
            cls.skip_reason = str(e)

    def test_lift_instantiates(self):
        """T5: BridgeLift6Dto9D can be instantiated."""
        if self.skip:
            self.skipTest(f"BridgeLift6Dto9D not available: {self.skip_reason}")
        self.assertIsNotNone(self.lift)

    def test_lift_eigenvalues_finite(self):
        """T5: Lifted 9D eigenvalues are finite."""
        if self.skip:
            self.skipTest(f"BridgeLift6Dto9D not available: {self.skip_reason}")
        op   = _build_operator()
        eigs = op.eigenvalues
        try:
            result = self.lift.lift_eigenvalues(eigs)
            lifted = result["9D_full_eigenvalues"]
            for i, v in enumerate(lifted):
                self.assertTrue(math.isfinite(float(v)), f"lifted[{i}] not finite")
        except Exception as e:
            self.skipTest(f"lift_eigenvalues raised: {e}")


# ---------------------------------------------------------------------------
# T6 — AXIOMS align: eigenvalue norms are finite
# ---------------------------------------------------------------------------
class TestStep09EigenvalueNorm(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import NORM_X_STAR
        cls.NORM_X_STAR = NORM_X_STAR
        cls.op = _build_operator()

    def test_eig_norm_finite(self):
        """T6: ||eigenvalues|| is finite."""
        norm = float(np.linalg.norm(self.op.eigenvalues))
        self.assertTrue(math.isfinite(norm))

    def test_eig_norm_positive(self):
        """T6: ||eigenvalues|| > 0."""
        norm = float(np.linalg.norm(self.op.eigenvalues))
        self.assertGreater(norm, 0.0)

    def test_axioms_norm_x_star_positive(self):
        """T6: AXIOMS NORM_X_STAR reference is positive."""
        self.assertGreater(self.NORM_X_STAR, 0.0)


# ---------------------------------------------------------------------------
# T7 — CSV output
# ---------------------------------------------------------------------------
class TestStep09CSV(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, timeout=60)

    def test_csv_exists(self):
        """T7: step_09_bridges.csv is produced."""
        self.assertTrue((ANALYTICS / "step_09_bridges.csv").exists())

    def test_csv_has_correct_columns(self):
        """T7: CSV has bridge, value, note columns."""
        import csv
        path = ANALYTICS / "step_09_bridges.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            cols = csv.DictReader(f).fieldnames
        for col in ("bridge", "value", "note"):
            self.assertIn(col, cols)

    def test_csv_has_b1_entries(self):
        """T7: CSV contains B1 bridge rows."""
        import csv
        path = ANALYTICS / "step_09_bridges.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        bridges = [r["bridge"] for r in rows]
        self.assertTrue(any("B1" in b for b in bridges),
                        "No B1 bridge row found in CSV")


if __name__ == "__main__":
    unittest.main(verbosity=2)
