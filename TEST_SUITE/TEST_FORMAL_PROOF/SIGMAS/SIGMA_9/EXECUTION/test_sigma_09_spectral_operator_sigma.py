#!/usr/bin/env python3
"""
test_sigma_09_spectral_operator_sigma.py
==========================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/SIGMAS/SIGMA_9/EXECUTION/EQ9_SPECTRAL_OPERATOR_SIGMA.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads and key symbols are present
    T3 — PrimeSpectralEngine: ediag, lam_min, lam_max, eigenvalues
    T4 — PSD properties: all eigenvalues >= -eps, lam_min >= 0
    T5 — All EQ9 proposition runners pass (EQ9.1 – EQ9.7)
"""

from __future__ import annotations

import sys
import math
import unittest
import py_compile
import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT   = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SCRIPT = ROOT / 'FORMAL_PROOF_NEW' / 'SIGMAS' / 'SIGMA_9' / 'EXECUTION' / 'EQ9_SPECTRAL_OPERATOR_SIGMA.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('EQ9_SPECTRAL_OPERATOR_SIGMA', SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules['EQ9_SPECTRAL_OPERATOR_SIGMA'] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestSigma09Syntax(unittest.TestCase):

    def test_script_exists(self):
        """T1: Script file is present."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")

    def test_compiles_without_errors(self):
        """T1: EQ9_SPECTRAL_OPERATOR_SIGMA.py compiles cleanly."""
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import and symbols
# ---------------------------------------------------------------------------
class TestSigma09Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module loads without ImportError."""
        self.assertIsNotNone(self.mod)

    def test_key_classes_present(self):
        """T2: PrimeSpectralEngine exported."""
        self.assertTrue(hasattr(self.mod, 'PrimeSpectralEngine'), "Missing: PrimeSpectralEngine")

    def test_key_functions_present(self):
        """T2: All prove_eq9_N functions and PROOFS list exported."""
        for name in ('prove_eq9_1', 'prove_eq9_2', 'prove_eq9_3',
                     'prove_eq9_4', 'prove_eq9_5', 'prove_eq9_6',
                     'prove_eq9_7', 'prove_eq9_A',
                     'HellmannFeynmanEngine', 'PROOFS'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")


# ---------------------------------------------------------------------------
# T3 — PrimeSpectralEngine methods
# ---------------------------------------------------------------------------
class TestSigma09SpectralEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        cls.se  = cls.mod.PrimeSpectralEngine(pa)

    def test_ediag_positive(self):
        """T3: Ediag = Tr(M) = sum p^{-2sigma} > 0."""
        for sigma in [0.3, 0.5, 0.7]:
            ediag = self.se.ediag(sigma)
            self.assertGreater(ediag, 0.0, f"ediag({sigma}) = {ediag}")

    def test_ediag_strictly_decreasing(self):
        """T3: Ediag(0.3) > Ediag(0.5) > Ediag(0.7) (proved in EQ9.1)."""
        e30 = self.se.ediag(0.3)
        e50 = self.se.ediag(0.5)
        e70 = self.se.ediag(0.7)
        self.assertGreater(e30, e50)
        self.assertGreater(e50, e70)

    def test_lam_min_nonneg(self):
        """T3: lambda_min(sigma, T) >= 0 (proved via triangle inequality)."""
        SPEC_EPS = 1e-10
        for sigma in [0.3, 0.5, 0.7]:
            for T in [10.0, 14.134, 50.0]:
                lmin = self.se.lam_min_analytic(sigma, T)
                self.assertGreaterEqual(lmin, -SPEC_EPS,
                                        f"lam_min({sigma},{T}) = {lmin}")

    def test_lam_max_positive(self):
        """T3: lambda_max(sigma, T) > 0."""
        SPEC_EPS = 1e-10
        for sigma in [0.3, 0.5, 0.7]:
            for T in [10.0, 14.134, 50.0]:
                lmax = self.se.lam_max_analytic(sigma, T)
                self.assertGreater(lmax, SPEC_EPS,
                                   f"lam_max({sigma},{T}) = {lmax}")

    def test_curvature_positive(self):
        """T3: C0 > 0 at sigma=0.5, T=14.134."""
        SPEC_EPS = 1e-10
        c = self.se.curvature(0.5, 14.134)
        self.assertGreater(c, SPEC_EPS, f"curvature = {c}")


# ---------------------------------------------------------------------------
# T4 — PSD property: numerical eigenvalues >= -eps
# ---------------------------------------------------------------------------
class TestSigma09PSDProperty(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=20)   # small X for speed
        cls.se  = cls.mod.PrimeSpectralEngine(pa)

    def test_eigenvalues_psd(self):
        """T4: All eigenvalues of M(sigma, T) >= -eps (Gram PSD matrix)."""
        SPEC_EPS = 1e-10
        for sigma in [0.4, 0.5, 0.6]:
            for T in [10.0, 14.134, 50.0]:
                eigs = self.se.eigenvalues(sigma, T)
                min_eig = float(eigs.min())
                self.assertGreaterEqual(min_eig, -SPEC_EPS,
                                        f"min eigenvalue {min_eig} < -{SPEC_EPS} "
                                        f"at sigma={sigma}, T={T}")

    def test_lam_max_gte_lam_min(self):
        """T4: lam_max >= lam_min for all test points."""
        for sigma in [0.4, 0.5, 0.6]:
            for T in [10.0, 14.134, 50.0]:
                lmin = self.se.lam_min_analytic(sigma, T)
                lmax = self.se.lam_max_analytic(sigma, T)
                self.assertGreaterEqual(lmax, lmin,
                                        f"lam_max < lam_min at sigma={sigma}, T={T}")


# ---------------------------------------------------------------------------
# T5 — All EQ9 proposition runners
# ---------------------------------------------------------------------------
class TestSigma09PropositionRunners(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_eq9_1_ediag(self):
        """T5: EQ9.1 — Ediag > 0 and strictly decreasing in sigma."""
        passed, total = self.mod.prove_eq9_1()
        self.assertEqual(passed, total, f"EQ9.1: {passed}/{total}")

    def test_eq9_2_lam_min_nonneg(self):
        """T5: EQ9.2 — lambda_min >= 0 at all test points."""
        passed, total = self.mod.prove_eq9_2()
        self.assertEqual(passed, total, f"EQ9.2: {passed}/{total}")

    def test_eq9_3_lam_max_positive(self):
        """T5: EQ9.3 — lambda_max > 0 at all test points."""
        passed, total = self.mod.prove_eq9_3()
        self.assertEqual(passed, total, f"EQ9.3: {passed}/{total}")

    def test_eq9_4_eigenvalues_psd(self):
        """T5: EQ9.4 — All numerical eigenvalues >= -eps (PSD)."""
        passed, total = self.mod.prove_eq9_4()
        self.assertEqual(passed, total, f"EQ9.4: {passed}/{total}")

    def test_eq9_5_c0_positive(self):
        """T5: EQ9.5 — C0(sigma, T) > 0 (sigma-selectivity)."""
        passed, total = self.mod.prove_eq9_5()
        self.assertEqual(passed, total, f"EQ9.5: {passed}/{total}")

    def test_eq9_6_lam_max_decreasing(self):
        """T5: EQ9.6 — lambda_max strictly decreasing in sigma."""
        passed, total = self.mod.prove_eq9_6()
        self.assertEqual(passed, total, f"EQ9.6: {passed}/{total}")

    def test_eq9_7_riemann_zeros_spectral(self):
        """T5: EQ9.7 — Spectral structure valid at 8 Riemann zero heights."""
        passed, total = self.mod.prove_eq9_7()
        self.assertEqual(passed, total, f"EQ9.7: {passed}/{total}")

    def test_proofs_list_complete(self):
        """T5: PROOFS list contains all 8 proposition entries (7 numeric + EQ9.A analytic)."""
        self.assertEqual(len(self.mod.PROOFS), 8)

    def test_eq9_A_hellmann_feynman(self):
        """T5: prove_eq9_A — Hellmann-Feynman d(lam_max)/dsigma < 0."""
        passed, total = self.mod.prove_eq9_A()
        self.assertGreater(total, 0)
        self.assertEqual(passed, total, f"EQ9.A HF: {passed}/{total}")


if __name__ == '__main__':
    unittest.main()
