#!/usr/bin/env python3
"""
test_sigma_07_debruijn_newman_sigma.py
========================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/SIGMAS/SIGMA_7/EXECUTION/EQ7_DEBRUIJN_NEWMAN_SIGMA.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads and key symbols are present
    T3 — SigmaFlowEngine: C_0, FD2_d2E, C_lambda, flow_result
    T4 — FlowResult fields and semantics
    T5 — Proposition runners EQ7.1 – EQ7.7 all pass
"""

from __future__ import annotations

import sys
import unittest
import py_compile
import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT   = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SCRIPT = ROOT / 'FORMAL_PROOF_NEW' / 'SIGMAS' / 'SIGMA_7' / 'EXECUTION' / 'EQ7_DEBRUIJN_NEWMAN_SIGMA.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('EQ7_DEBRUIJN_NEWMAN_SIGMA', SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules['EQ7_DEBRUIJN_NEWMAN_SIGMA'] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestSigma07Syntax(unittest.TestCase):

    def test_script_exists(self):
        """T1: Script file is present."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")

    def test_compiles_without_errors(self):
        """T1: EQ7_DEBRUIJN_NEWMAN_SIGMA.py compiles cleanly."""
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import and symbols
# ---------------------------------------------------------------------------
class TestSigma07Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module loads without ImportError."""
        self.assertIsNotNone(self.mod)

    def test_key_classes_present(self):
        """T2: Key classes exported by EQ7."""
        for name in ('SigmaFlowEngine', 'FlowResult', 'EQ7ValidationSummary',
                     'PrimeSideEnergyModel'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")

    def test_key_functions_present(self):
        """T2: Proposition runners exported."""
        for name in ('run_eq7_1', 'run_eq7_2', 'run_eq7_3',
                     'run_eq7_4', 'run_eq7_5', 'run_eq7_6', 'run_eq7_7'):
            self.assertTrue(hasattr(self.mod, name), f"Missing function: {name}")


# ---------------------------------------------------------------------------
# T3 — SigmaFlowEngine
# ---------------------------------------------------------------------------
class TestSigma07FlowEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        em      = cls.mod.PrimeSideEnergyModel(pa)
        cls.em  = em
        cls.fe  = cls.mod.SigmaFlowEngine(em)

    def test_c0_nonneg_at_critical_line(self):
        """T3: C_0(sigma=0.5, T=14.134) >= 0."""
        c0 = self.fe.C_0(sigma=0.5, T=14.134)
        self.assertGreaterEqual(c0, 0.0, f"C_0 = {c0}")

    def test_fd2_d2e_nonneg(self):
        """T3: FD2[d2E](sigma=0.5, T=14.134) >= 0 (proved in EQ7.3)."""
        fd2 = self.fe.FD2_d2E(sigma=0.5, T=14.134)
        self.assertGreaterEqual(fd2, 0.0, f"FD2_d2E = {fd2}")

    def test_c_lambda_monotone(self):
        """T3: C_lambda >= C_0 for lambda > 0 (flow is monotone)."""
        c0  = self.fe.C_0(sigma=0.5, T=14.134)
        for lam in [0.01, 0.05, 0.10]:
            c_lam = self.fe.C_lambda(sigma=0.5, T=14.134, lam=lam)
            self.assertGreaterEqual(c_lam, c0 - 1e-10,
                                    f"C_lambda({lam}) < C_0: {c_lam} < {c0}")

    def test_e_lambda_at_zero_equals_energy(self):
        """T3: E_lambda(sigma, T, lam=0) == E_0(sigma, T)."""
        sigma, T = 0.5, 14.134
        e0  = self.em.energy(sigma, T)
        e_l = self.fe.E_lambda(sigma, T, lam=0.0)
        self.assertAlmostEqual(e_l, e0, places=12)


# ---------------------------------------------------------------------------
# T4 — FlowResult
# ---------------------------------------------------------------------------
class TestSigma07FlowResult(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        em      = cls.mod.PrimeSideEnergyModel(pa)
        cls.fe  = cls.mod.SigmaFlowEngine(em)

    def test_flow_result_fields(self):
        """T4: flow_result() returns FlowResult with correct fields."""
        result = self.fe.flow_result(sigma=0.5, T=14.134, lam=0.05)
        self.assertIsInstance(result, self.mod.FlowResult)
        for field in ('sigma', 'T', 'lam', 'C_0', 'C_lam',
                      'FD2_d2E', 'flow_mono', 'flow_pos'):
            self.assertTrue(hasattr(result, field), f"Missing field: {field}")

    def test_flow_mono_at_positive_lambda(self):
        """T4: flow_mono == True for lambda > 0."""
        result = self.fe.flow_result(sigma=0.5, T=14.134, lam=0.05)
        self.assertTrue(result.flow_mono,
                        f"flow_mono False at lam=0.05, C_0={result.C_0}, C_lam={result.C_lam}")

    def test_fd2_positive(self):
        """T4: FD2_d2E > 0 at sigma=0.5, T=14.134."""
        result = self.fe.flow_result(sigma=0.5, T=14.134, lam=0.05)
        self.assertGreater(result.FD2_d2E, 0.0)


# ---------------------------------------------------------------------------
# T5 — Proposition runners EQ7.1 – EQ7.7
# ---------------------------------------------------------------------------
class TestSigma07PropositionRunners(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        pa      = cls.mod.PrimeArithmetic(X=50)
        em      = cls.mod.PrimeSideEnergyModel(pa)
        cls.em  = em
        cls.fe  = cls.mod.SigmaFlowEngine(em)

    def test_eq7_1_energy_nonneg(self):
        """T5: EQ7.1 — E_0(sigma,T) >= 0 at all test points."""
        passed, total = self.mod.run_eq7_1(self.em)
        self.assertEqual(passed, total, f"EQ7.1: {passed}/{total}")

    def test_eq7_2_c0_nonneg(self):
        """T5: EQ7.2 — C_0(sigma,T) >= 0 at all test points."""
        passed, total, _ = self.mod.run_eq7_2(self.fe)
        self.assertEqual(passed, total, f"EQ7.2: {passed}/{total}")

    def test_eq7_3_flow_monotone(self):
        """T5: EQ7.3 — C_lambda >= C_0 for lambda > 0."""
        passed, total = self.mod.run_eq7_3(self.fe)
        self.assertEqual(passed, total, f"EQ7.3: {passed}/{total}")

    def test_eq7_4_lambda0_strict(self):
        """T5: EQ7.4 — C_0 > 0 strictly at sigma=1/2."""
        passed, total = self.mod.run_eq7_4(self.fe)
        self.assertEqual(passed, total, f"EQ7.4: {passed}/{total}")

    def test_eq7_5_fd2_positive(self):
        """T5: EQ7.5 — FD2[d2E] > 0 (flow stability derivative > 0)."""
        passed, total, _ = self.mod.run_eq7_5(self.fe)
        self.assertEqual(passed, total, f"EQ7.5: {passed}/{total}")

    def test_eq7_6_offline_sigma_flow(self):
        """T5: EQ7.6 — C_lambda >= C_0 for off-critical sigma."""
        passed, total = self.mod.run_eq7_6(self.fe)
        self.assertEqual(passed, total, f"EQ7.6: {passed}/{total}")

    def test_eq7_7_riemann_zeros(self):
        """T5: EQ7.7 — C_0 > 0 at 8 Riemann zero heights."""
        passed, total = self.mod.run_eq7_7(self.fe)
        self.assertEqual(passed, total, f"EQ7.7: {passed}/{total}")


if __name__ == '__main__':
    unittest.main()
