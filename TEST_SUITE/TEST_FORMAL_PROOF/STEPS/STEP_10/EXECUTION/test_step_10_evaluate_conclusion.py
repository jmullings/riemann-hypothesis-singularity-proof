#!/usr/bin/env python3
"""
test_step_10_evaluate_conclusion.py
======================================
Mirror unit tests for:
    FORMAL_PROOF_NEW/STEPS/STEP_10/EXECUTION/STEP_10_EVALUATE_CONCLUSION.py

Test categories:
    T1 — Syntax         : script compiles without errors
    T2 — Runtime        : script runs to completion (exit 0)
    T3 — AXIOMS imports : LAMBDA_STAR, NORM_X_STAR, PHI loadable
    T4 — CSVs present   : all prerequisite step CSVs exist
    T5 — Skeleton CSV   : step_10_proof_skeleton.csv produced with 10 rows
    T6 — Finite steps   : all FINITE rows in skeleton are marked ok
    T7 — Status output  : output contains SOLID FOUNDATION marker
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT      = Path(__file__).resolve().parents[5]
CONFIGS   = ROOT / "FORMAL_PROOF_NEW" / "CONFIGURATIONS"
STEPS_DIR = ROOT / "FORMAL_PROOF_NEW" / "STEPS"
SCRIPT    = STEPS_DIR / "STEP_10" / "EXECUTION" / "STEP_10_EVALUATE_CONCLUSION.py"
ANALYTICS = STEPS_DIR / "STEP_10" / "ANALYTICS"

# Expected CSV outputs from preceding steps
EXPECTED_CSVS = [
    STEPS_DIR / "STEP_1"  / "ANALYTICS" / "step_01_axiom_report.csv",
    STEPS_DIR / "STEP_2"  / "ANALYTICS" / "step_02_prime_weights.csv",
    STEPS_DIR / "STEP_3"  / "ANALYTICS" / "step_03_eq_kernel.csv",
    STEPS_DIR / "STEP_4"  / "ANALYTICS" / "step_04_sigma_star.csv",
    STEPS_DIR / "STEP_5"  / "ANALYTICS" / "step_05_curvature_spectrum.csv",
    STEPS_DIR / "STEP_6"  / "ANALYTICS" / "step_06_eq_matrix.csv",
    STEPS_DIR / "STEP_7"  / "ANALYTICS" / "step_07_alignment.csv",
    STEPS_DIR / "STEP_8"  / "ANALYTICS" / "step_08_def_validation.csv",
    STEPS_DIR / "STEP_9"  / "ANALYTICS" / "step_09_bridges.csv",
]


def _add_configs():
    if str(CONFIGS) not in sys.path:
        sys.path.insert(0, str(CONFIGS))


def _run_all_steps():
    """Run steps 1-9 to ensure their CSVs exist for step 10."""
    for step_num in range(1, 10):
        step_dir = STEPS_DIR / f"STEP_{step_num}" / "EXECUTION"
        scripts  = list(step_dir.glob("STEP_0*.py"))
        if not scripts:
            scripts = list(step_dir.glob("STEP_*.py"))
        for s in scripts:
            subprocess.run([sys.executable, str(s)],
                           capture_output=True, timeout=120)


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestStep10Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: Script compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Runtime
# ---------------------------------------------------------------------------
class TestStep10Runtime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure prerequisite CSVs exist
        _run_all_steps()

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
        """T2: Output contains STEP 10 COMPLETE."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=60
        )
        self.assertIn("STEP 10 COMPLETE", result.stdout)


# ---------------------------------------------------------------------------
# T3 — AXIOMS imports
# ---------------------------------------------------------------------------
class TestStep10AxiomsImports(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _add_configs()
        from AXIOMS import LAMBDA_STAR, NORM_X_STAR, PHI
        cls.LAMBDA_STAR = LAMBDA_STAR
        cls.NORM_X_STAR = NORM_X_STAR
        cls.PHI         = PHI

    def test_lambda_star_loadable(self):
        """T3: LAMBDA_STAR is loadable and positive."""
        self.assertGreater(self.LAMBDA_STAR, 0.0)

    def test_norm_x_star_loadable(self):
        """T3: NORM_X_STAR is loadable and in (0, 1)."""
        self.assertGreater(self.NORM_X_STAR, 0.0)
        self.assertLess(self.NORM_X_STAR, 1.0)

    def test_phi_loadable(self):
        """T3: PHI ≈ 1.618."""
        self.assertAlmostEqual(self.PHI, 1.618, delta=0.001)


# ---------------------------------------------------------------------------
# T4 — Prerequisite CSVs present
# ---------------------------------------------------------------------------
class TestStep10PrerequisiteCSVs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _run_all_steps()

    def test_all_step_csvs_exist(self):
        """T4: All 9 prerequisite CSV files exist after running steps 1-9."""
        missing = [str(p) for p in EXPECTED_CSVS if not p.exists()]
        self.assertEqual(
            missing, [],
            f"Missing prerequisite CSVs:\n" + "\n".join(missing)
        )


# ---------------------------------------------------------------------------
# T5 — Skeleton CSV
# ---------------------------------------------------------------------------
class TestStep10SkeletonCSV(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _run_all_steps()
        subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, timeout=60)

    def test_skeleton_csv_exists(self):
        """T5: step_10_proof_skeleton.csv is produced."""
        self.assertTrue((ANALYTICS / "step_10_proof_skeleton.csv").exists())

    def test_skeleton_csv_has_10_rows(self):
        """T5: Skeleton CSV has exactly 10 rows."""
        import csv
        path = ANALYTICS / "step_10_proof_skeleton.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 10)

    def test_skeleton_csv_columns(self):
        """T5: Skeleton CSV has step, kind, ok, info, desc columns."""
        import csv
        path = ANALYTICS / "step_10_proof_skeleton.csv"
        if not path.exists():
            self.skipTest("CSV not produced yet")
        with open(path) as f:
            cols = csv.DictReader(f).fieldnames
        for col in ("step", "kind", "ok", "desc"):
            self.assertIn(col, cols)


# ---------------------------------------------------------------------------
# T6 — Finite steps all marked ok
# ---------------------------------------------------------------------------
class TestStep10FiniteStepsOK(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _run_all_steps()
        subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, timeout=60)
        import csv
        path = ANALYTICS / "step_10_proof_skeleton.csv"
        cls.rows = []
        if path.exists():
            with open(path) as f:
                cls.rows = list(csv.DictReader(f))

    def test_finite_rows_all_ok(self):
        """T6: All FINITE rows in the skeleton are ok=True."""
        if not self.rows:
            self.skipTest("Skeleton CSV not available")
        finite_rows = [r for r in self.rows if "FINITE" in r.get("kind", "")]
        self.assertGreater(len(finite_rows), 0, "No FINITE rows found in skeleton")
        failed = [r for r in finite_rows if r.get("ok", "").lower() not in ("true", "1")]
        self.assertEqual(
            failed, [],
            f"FINITE steps not ok: {[(r['step'], r['desc']) for r in failed]}"
        )

    def test_step_10_is_ok(self):
        """T6: Row for step 10 (SKELETON) is marked ok."""
        if not self.rows:
            self.skipTest("Skeleton CSV not available")
        row10 = next((r for r in self.rows if str(r.get("step")) == "10"), None)
        self.assertIsNotNone(row10, "No row for step 10 found")
        self.assertIn(str(row10.get("ok", "")).lower(), ("true", "1"))


# ---------------------------------------------------------------------------
# T7 — Status output contains SOLID FOUNDATION
# ---------------------------------------------------------------------------
class TestStep10StatusOutput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _run_all_steps()
        cls.result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=60
        )

    def test_solid_foundation_marker(self):
        """T7: Output contains 'SOLID FOUNDATION' (all finite steps verified)."""
        self.assertIn("SOLID FOUNDATION", self.result.stdout)

    def test_conjectural_gap_acknowledged(self):
        """T7: Output acknowledges the conjectural gap (Axiom 8)."""
        self.assertTrue(
            "CONJECTURAL" in self.result.stdout or "conjectural" in self.result.stdout.lower(),
            "No mention of CONJECTURAL gap in output"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
