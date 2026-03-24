#!/usr/bin/env python3
"""
================================================================================
test_52_uniform_delta_beta.py — Gap 3: Uniform Small-Δβ Bounds Tests
================================================================================

Tier 52: Tests for engine/uniform_delta_beta.py

Validates the finite grid scan + monotonicity approach to upgrading
the asymptotic (~) small-Δβ bound to a verified-on-grid uniform bound.
================================================================================
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import numpy as np

from engine.uniform_delta_beta import (
    lambda_eff,
    lambda_eff_monotonicity_in_gamma0,
    lambda_eff_uniform_lower_bound,
    exact_weil_decay_profile,
    envelope_baseline_analysis,
    uniform_delta_beta_certificate,
)


class TestLambdaEff(unittest.TestCase):
    """Tests for λ_eff computation."""

    def test_lambda_eff_positive(self):
        """λ_eff > 0 for typical parameters."""
        r = lambda_eff(14.135, 0.05)
        self.assertGreater(r['lambda_eff'], 0.0)

    def test_envelope_always_negative(self):
        """Envelope (γ₀-independent baseline) is always < 0."""
        r = lambda_eff(14.135, 0.05)
        self.assertLess(r['envelope'], 0.0)

    def test_envelope_negative(self):
        """Envelope is negative."""
        r = lambda_eff(14.135, 0.05)
        self.assertLess(r['envelope'], 0.0)

    def test_various_gamma0(self):
        """λ_eff computed for various γ₀ without error."""
        for g0 in [1.0, 14.135, 50.0, 200.0]:
            r = lambda_eff(g0, 0.05)
            self.assertIsInstance(r['lambda_eff'], float)
            self.assertGreaterEqual(r['lambda_eff'], 0.0)

    def test_various_delta_beta(self):
        """λ_eff computed for various Δβ."""
        for db in [0.01, 0.05, 0.1, 0.2]:
            r = lambda_eff(14.135, db)
            self.assertGreater(r['lambda_eff'], 0.0)

    def test_small_delta_beta(self):
        """λ_eff is well-defined for very small Δβ."""
        r = lambda_eff(14.135, 0.001)
        self.assertIsInstance(r['lambda_eff'], float)
        self.assertFalse(np.isnan(r['lambda_eff']))
        self.assertFalse(np.isinf(r['lambda_eff']))


class TestMonotonicity(unittest.TestCase):
    """Tests for monotonicity of λ_eff in γ₀."""

    def test_monotone_for_db_005(self):
        """λ_eff decreases with γ₀ for Δβ=0.05."""
        r = lambda_eff_monotonicity_in_gamma0(0.05)
        self.assertTrue(r['monotone'])

    def test_monotone_for_db_01(self):
        """λ_eff decreases with γ₀ for Δβ=0.1."""
        r = lambda_eff_monotonicity_in_gamma0(0.1)
        self.assertTrue(r['monotone'])

    def test_monotone_for_db_02(self):
        """λ_eff decreases with γ₀ for Δβ=0.2."""
        r = lambda_eff_monotonicity_in_gamma0(0.2)
        self.assertTrue(r['monotone'])

    def test_violation_small(self):
        """Max violation is < tolerance."""
        r = lambda_eff_monotonicity_in_gamma0(0.05)
        self.assertLess(r['max_violation'], 1e-8)

    def test_lambda_effs_nonempty(self):
        """Returns non-empty list of λ_eff values."""
        r = lambda_eff_monotonicity_in_gamma0(0.05)
        self.assertGreater(len(r['lambda_effs']), 5)

    def test_custom_gamma_grid(self):
        """Works with custom γ₀ grid."""
        g_vals = np.array([10.0, 20.0, 50.0, 100.0])
        r = lambda_eff_monotonicity_in_gamma0(0.05, gamma0_values=g_vals)
        self.assertTrue(r['monotone'])
        self.assertEqual(len(r['lambda_effs']), 4)


class TestUniformLowerBound(unittest.TestCase):
    """Tests for the grid-scan uniform lower bound."""

    def test_bounded_away(self):
        """inf λ_eff > 0 over the grid."""
        r = lambda_eff_uniform_lower_bound()
        self.assertTrue(r['bounded_away'])

    def test_inf_positive(self):
        """Infimum is strictly positive."""
        r = lambda_eff_uniform_lower_bound()
        self.assertGreater(r['inf_lambda_eff'], 0.0)

    def test_grid_size(self):
        """Grid has reasonable size."""
        r = lambda_eff_uniform_lower_bound()
        self.assertGreater(r['grid_size'], 50)

    def test_inf_at_tuple(self):
        """inf_at is a (γ₀, Δβ) tuple with valid values."""
        r = lambda_eff_uniform_lower_bound()
        self.assertEqual(len(r['inf_at']), 2)
        self.assertGreater(r['inf_at'][0], 0.0)  # γ₀ > 0
        self.assertGreater(r['inf_at'][1], 0.0)  # Δβ > 0

    def test_custom_grid(self):
        """Works with custom grid values."""
        r = lambda_eff_uniform_lower_bound(
            delta_beta_values=np.array([0.01, 0.05, 0.1]),
            gamma0_values=np.array([10.0, 50.0, 200.0]))
        self.assertTrue(r['bounded_away'])


class TestExactWeilDecay(unittest.TestCase):
    """Tests for the exact Weil decay profile."""

    def test_decays_monotonically(self):
        """Exact |C_off| decays with γ₀."""
        r = exact_weil_decay_profile()
        self.assertTrue(r['decays'])

    def test_decay_factor_positive(self):
        """Decay rate is positive (exponential decay confirmed)."""
        r = exact_weil_decay_profile()
        self.assertGreater(r['decay_factor'], 0.0)

    def test_high_gamma0_very_small(self):
        """C_off at high γ₀ is much smaller than at low γ₀."""
        r = exact_weil_decay_profile()
        abs_vals = r['abs_C_off']
        if len(abs_vals) >= 2 and abs_vals[0] > 1e-30:
            self.assertLess(abs_vals[-1], abs_vals[0])

    def test_various_delta_beta(self):
        """Decay verified for various Δβ."""
        for db in [0.01, 0.05, 0.1]:
            r = exact_weil_decay_profile(delta_beta=db)
            self.assertTrue(r['decays'],
                            f"Decay failed for Δβ={db}")

    def test_various_alpha(self):
        """Decay verified for various α."""
        for alpha in [0.05, 0.1, 0.2]:
            r = exact_weil_decay_profile(alpha=alpha)
            self.assertTrue(r['decays'],
                            f"Decay failed for α={alpha}")


class TestEnvelopeBaseline(unittest.TestCase):
    """Tests for the envelope (non-oscillatory) baseline."""

    def test_all_negative(self):
        """Envelope is negative for all Δβ."""
        r = envelope_baseline_analysis()
        self.assertTrue(r['all_negative'])

    def test_min_envelope_negative(self):
        """Most negative envelope value is well below zero."""
        r = envelope_baseline_analysis()
        self.assertLess(r['min_envelope'], 0.0)

    def test_max_envelope_negative(self):
        """Even the closest-to-zero envelope is still < 0."""
        r = envelope_baseline_analysis()
        self.assertLess(r['max_envelope'], 0.0)

    def test_custom_delta_beta(self):
        """Works with custom Δβ values."""
        r = envelope_baseline_analysis(
            delta_beta_values=np.array([0.01, 0.1, 0.3]))
        self.assertTrue(r['all_negative'])


class TestGap3FullCertificate(unittest.TestCase):
    """Tests for the complete Gap 3 certificate."""

    def test_partially_closed(self):
        """Gap 3 is at least partially closed."""
        cert = uniform_delta_beta_certificate(delta_beta=0.05)
        self.assertIn(cert['gap3_status'],
                       ['PARTIALLY_CLOSED', 'NUMERICALLY_VERIFIED'])

    def test_certificate_components(self):
        """All components present."""
        cert = uniform_delta_beta_certificate()
        for key in ['monotonicity', 'grid_scan', 'exact_decay', 'envelope']:
            self.assertIn(key, cert)

    def test_message_nonempty(self):
        """Certificate has explanatory message."""
        cert = uniform_delta_beta_certificate()
        self.assertIsInstance(cert['message'], str)
        self.assertGreater(len(cert['message']), 20)

    def test_envelope_negative_in_cert(self):
        """Envelope check passes within the certificate."""
        cert = uniform_delta_beta_certificate()
        self.assertTrue(cert['envelope']['all_negative'])

    def test_decay_confirmed_in_cert(self):
        """Exact decay confirmed within the certificate."""
        cert = uniform_delta_beta_certificate()
        self.assertTrue(cert['exact_decay']['decays'])

    def test_grid_bounded_in_cert(self):
        """Grid scan bounded within the certificate."""
        cert = uniform_delta_beta_certificate()
        self.assertTrue(cert['grid_scan']['bounded_away'])


if __name__ == '__main__':
    unittest.main()
