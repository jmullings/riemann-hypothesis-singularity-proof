#!/usr/bin/env python3
"""
test_part_10_qed_assembly.py
===============================
Unit tests for QED_ASSEMBLY/PART_10_QED_ASSEMBLY.py

Test categories:
    T1 — Syntax    : script compiles without errors
    T2 — Runtime   : run_all() runs and returns bool (long-running: ~290s)
    T3 — Functions : run_all exists and is callable
    T4 — Assembly  : all 9 PARTs imported successfully
    T5 — Output    : output contains Human Figure and status table
"""

from __future__ import annotations

import sys
import subprocess
import unittest
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QED_ASSEMBLY = ROOT / "FORMAL_PROOF_NEW" / "QED_ASSEMBLY"
SCRIPT = QED_ASSEMBLY / "PART_10_QED_ASSEMBLY.py"
AI_PHASES = ROOT / "FORMAL_PROOF_NEW" / "AI_PHASES"


def _add_paths():
    for p in [str(QED_ASSEMBLY), str(AI_PHASES)]:
        if p not in sys.path:
            sys.path.insert(0, p)


class TestPart10Syntax(unittest.TestCase):
    def test_compiles(self):
        """T1: PART_10_QED_ASSEMBLY.py compiles."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


class TestPart10Functions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()
        import PART_10_QED_ASSEMBLY as mod
        cls.mod = mod

    def test_run_all_exists(self):
        """T3: run_all function exists."""
        self.assertTrue(callable(getattr(self.mod, 'run_all', None)))


class TestPart10Imports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _add_paths()

    def test_all_parts_importable(self):
        """T4: All 9 PART modules can be imported."""
        part_names = [
            'PART_01_RH_STATEMENT',
            'PART_02_PSS_SECH2_FRAMEWORK',
            'PART_03_PRIME_SIDE_CURVATURE',
            'PART_04_CLASSICAL_BACKBONE',
            'PART_05_MONTGOMERY_VAUGHAN',
            'PART_06_MELLIN_MEAN_DECOMPOSITION',
            'PART_07_MV_SECH2_ANTISYMMETRISATION',
            'PART_08_UNIFORM_CURVATURE_BOUND',
            'PART_09_RS_BRIDGE',
        ]
        for name in part_names:
            try:
                __import__(name)
            except Exception as e:
                self.fail(f"Failed to import {name}: {e}")

    def test_each_part_has_main(self):
        """T4: Each PART module has a callable main()."""
        part_names = [
            'PART_01_RH_STATEMENT',
            'PART_02_PSS_SECH2_FRAMEWORK',
            'PART_03_PRIME_SIDE_CURVATURE',
            'PART_04_CLASSICAL_BACKBONE',
            'PART_05_MONTGOMERY_VAUGHAN',
            'PART_06_MELLIN_MEAN_DECOMPOSITION',
            'PART_07_MV_SECH2_ANTISYMMETRISATION',
            'PART_08_UNIFORM_CURVATURE_BOUND',
            'PART_09_RS_BRIDGE',
        ]
        for name in part_names:
            mod = __import__(name)
            self.assertTrue(
                callable(getattr(mod, 'main', None)),
                f"{name} has no callable main()"
            )


class TestPart10FullRun(unittest.TestCase):
    def test_full_assembly_exit_zero(self):
        """T2/T5: Full PART_10 assembly runs and exits 0 (may take ~5 min)."""
        result = subprocess.run(
            [sys.executable, '-u', str(SCRIPT)],
            capture_output=True, text=True, timeout=600,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertEqual(result.returncode, 0,
                         f"Exit {result.returncode}.\nSTDERR:\n{result.stderr[:500]}")

    def test_output_contains_human_figure(self):
        """T5: Output contains the Human Figure diagram."""
        result = subprocess.run(
            [sys.executable, '-u', str(SCRIPT)],
            capture_output=True, text=True, timeout=600,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertIn("CRANIUM", result.stdout)
        self.assertIn("PELVIS", result.stdout)

    def test_output_contains_pass_markers(self):
        """T5: Output contains PASS markers for PARTs."""
        result = subprocess.run(
            [sys.executable, '-u', str(SCRIPT)],
            capture_output=True, text=True, timeout=600,
            cwd=str(QED_ASSEMBLY)
        )
        self.assertIn("PASS", result.stdout.upper())


if __name__ == '__main__':
    unittest.main()
