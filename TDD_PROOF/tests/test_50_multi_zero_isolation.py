#!/usr/bin/env python3
"""
================================================================================
test_50_multi_zero_isolation.py — Gap 1: Multi-Zero Interference Tests
================================================================================

Tier 50: Tests for engine/multi_zero_isolation.py

Validates the minimal counterexample technique: additional off-critical
zeros only STRENGTHEN the negative ΔA injection, so it suffices to
prove the contradiction for a single zero with minimal |Δβ|.
================================================================================
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import numpy as np

from engine.multi_zero_isolation import (
    multi_zero_total_injection,
    multi_zero_exact_domination,
    minimal_counterexample_certificate,
    multi_zero_monotonicity_scan,
    on_critical_independence_certificate,
    gap1_multi_zero_certificate,
)
from engine.weil_density import GAMMA_30


class TestMultiZeroTotalInjection(unittest.TestCase):
    """Tests for the multi-zero BASE ΔA total injection (always negative)."""

    def test_empty_zeros(self):
        """Empty zero list produces zero injection."""
        result = multi_zero_total_injection([], H=10.0)
        self.assertEqual(result['deltaA_total'], 0.0)
        self.assertTrue(result['all_negative'])
        self.assertTrue(result['monotonicity_holds'])
        self.assertIsNone(result['minimal_zero'])

    def test_single_zero_negative(self):
        """Single off-critical zero has base ΔA < 0."""
        zeros = [(14.135, 0.05)]
        result = multi_zero_total_injection(zeros, H=10.0)
        self.assertLess(result['deltaA_total'], 0.0)
        self.assertTrue(result['all_negative'])
        self.assertEqual(len(result['deltaA_individual']), 1)

    def test_two_zeros_stronger(self):
        """Two off-critical zeros give |ΔA_total| ≥ |ΔA_single|."""
        zeros_1 = [(14.135, 0.05)]
        zeros_2 = [(14.135, 0.05), (21.022, 0.08)]
        r1 = multi_zero_total_injection(zeros_1, H=10.0)
        r2 = multi_zero_total_injection(zeros_2, H=10.0)
        self.assertLessEqual(r2['deltaA_total'], r1['deltaA_total'])
        self.assertGreaterEqual(abs(r2['deltaA_total']),
                                abs(r1['deltaA_total']) - 1e-15)

    def test_five_zeros_all_negative(self):
        """Five off-critical zeros all contribute negative base ΔA."""
        zeros = [
            (14.135, 0.05), (21.022, 0.08), (25.011, 0.12),
            (30.425, 0.06), (32.935, 0.10),
        ]
        result = multi_zero_total_injection(zeros, H=10.0)
        self.assertTrue(result['all_negative'])
        self.assertLess(result['deltaA_total'], 0.0)

    def test_minimal_zero_identified(self):
        """The zero with smallest |Δβ| is correctly identified."""
        zeros = [(14.135, 0.15), (21.022, 0.03), (25.011, 0.10)]
        result = multi_zero_total_injection(zeros, H=10.0)
        self.assertAlmostEqual(result['minimal_zero'][1], 0.03, places=10)
        self.assertAlmostEqual(result['minimal_zero'][0], 21.022, places=3)

    def test_monotonicity_holds_multiple(self):
        """Monotonicity: |ΔA_total| ≥ |ΔA of minimal zero|."""
        zeros = [
            (14.135, 0.05), (21.022, 0.08), (25.011, 0.12),
        ]
        result = multi_zero_total_injection(zeros, H=10.0)
        self.assertTrue(result['monotonicity_holds'])

    def test_large_delta_beta_saturates(self):
        """Large Δβ zeros contribute strongly negative ΔA."""
        zeros = [(14.135, 0.3)]
        result = multi_zero_total_injection(zeros, H=10.0)
        self.assertLess(result['deltaA_total'], -10.0)

    def test_small_delta_beta_weak(self):
        """Small Δβ zeros contribute weakly negative ΔA."""
        zeros = [(14.135, 0.001)]
        result = multi_zero_total_injection(zeros, H=10.0)
        self.assertLess(result['deltaA_total'], 0.0)
        self.assertGreater(result['deltaA_total'], -1.0)

    def test_total_is_sum_of_individual(self):
        """Total equals the sum of individual contributions."""
        zeros = [(14.135, 0.05), (21.022, 0.08), (25.011, 0.12)]
        result = multi_zero_total_injection(zeros, H=10.0)
        self.assertAlmostEqual(
            result['deltaA_total'],
            sum(result['deltaA_individual']),
            places=12,
        )

    def test_various_H_values(self):
        """ΔA < 0 for various kernel bandwidths."""
        zeros = [(14.135, 0.05)]
        for H in [5.0, 10.0, 20.0, 50.0]:
            result = multi_zero_total_injection(zeros, H=H)
            self.assertLess(result['deltaA_total'], 0.0,
                            f"Failed for H={H}")

    def test_base_formula_gamma0_independent(self):
        """Base ΔA depends only on Δβ, not on γ₀."""
        z1 = [(14.135, 0.05)]
        z2 = [(100.0, 0.05)]
        r1 = multi_zero_total_injection(z1, H=10.0)
        r2 = multi_zero_total_injection(z2, H=10.0)
        self.assertAlmostEqual(r1['deltaA_total'], r2['deltaA_total'], places=12)


class TestMultiZeroExactDomination(unittest.TestCase):
    """Tests using Theorem 6.1 for low-lying zeros."""

    def test_low_lying_dominates(self):
        """Theorem 6.1 holds for zeros with γ₀ ≤ γ₁."""
        zeros = [(10.0, 0.05)]
        result = multi_zero_exact_domination(zeros)
        self.assertTrue(result['all_dominated'])
        self.assertEqual(result['n_low_lying'], 1)

    def test_at_gamma1_dominates(self):
        """Theorem 6.1 holds at γ₀ = γ₁."""
        zeros = [(GAMMA_30[0], 0.05)]
        result = multi_zero_exact_domination(zeros)
        self.assertTrue(result['all_dominated'])

    def test_high_lying_not_dominated(self):
        """Theorem 6.1 does NOT apply for γ₀ > γ₁."""
        zeros = [(20.0, 0.05)]
        result = multi_zero_exact_domination(zeros)
        self.assertFalse(result['all_dominated'])
        self.assertEqual(result['n_low_lying'], 0)

    def test_mixed_zeros(self):
        """Mixed low and high-lying zeros: not all dominated."""
        zeros = [(10.0, 0.05), (20.0, 0.08)]
        result = multi_zero_exact_domination(zeros)
        self.assertEqual(result['n_low_lying'], 1)


class TestMinimalCounterexample(unittest.TestCase):
    """Tests for the minimal counterexample isolation certificate."""

    def test_certificate_structure(self):
        """Certificate has all required keys."""
        zeros = [(14.135, 0.05), (21.022, 0.08)]
        cert = minimal_counterexample_certificate(zeros, H=10.0)
        for key in ['certified', 'minimal_zero', 'isolation_argument',
                     'base_model']:
            self.assertIn(key, cert)

    def test_certified_for_typical_zeros(self):
        """Certificate holds for typical off-critical configurations."""
        zeros = [
            (14.135, 0.05), (21.022, 0.08),
            (25.011, 0.12), (30.425, 0.06),
        ]
        cert = minimal_counterexample_certificate(zeros, H=10.0)
        self.assertTrue(cert['certified'])

    def test_minimal_zero_is_smallest_db(self):
        """Certificate correctly identifies the minimal-|Δβ| zero."""
        zeros = [(14.135, 0.10), (21.022, 0.02), (25.011, 0.15)]
        cert = minimal_counterexample_certificate(zeros, H=10.0)
        self.assertAlmostEqual(cert['minimal_zero'][1], 0.02, places=10)

    def test_isolation_argument_nonempty(self):
        """Isolation argument is a non-empty explanatory string."""
        zeros = [(14.135, 0.05)]
        cert = minimal_counterexample_certificate(zeros, H=10.0)
        self.assertIsInstance(cert['isolation_argument'], str)
        self.assertGreater(len(cert['isolation_argument']), 50)

    def test_single_zero_certified(self):
        """Even a single zero is trivially certified."""
        zeros = [(14.135, 0.05)]
        cert = minimal_counterexample_certificate(zeros, H=10.0)
        self.assertTrue(cert['certified'])

    def test_with_domination_check(self):
        """Certificate works with domination check enabled."""
        zeros = [(10.0, 0.05)]
        cert = minimal_counterexample_certificate(zeros, H=10.0,
                                                   check_domination=True)
        self.assertTrue(cert['certified'])
        self.assertIsNotNone(cert['domination_model'])


class TestMultiZeroMonotonicity(unittest.TestCase):
    """Tests for monotonicity scan: adding zeros strengthens injection."""

    def test_monotonicity_holds(self):
        """Adding zeros monotonically increases |ΔA_total|."""
        result = multi_zero_monotonicity_scan(0.05, H=10.0, n_extra=5)
        self.assertTrue(result['monotone'])
        self.assertEqual(result['n_tested'], 5)

    def test_cumulative_grows(self):
        """Cumulative |ΔA| sequence is non-decreasing."""
        result = multi_zero_monotonicity_scan(0.05, H=10.0, n_extra=8)
        totals = result['cumulative_totals']
        for i in range(len(totals) - 1):
            self.assertGreaterEqual(totals[i+1], totals[i] - 1e-15)

    def test_monotonicity_various_db(self):
        """Monotonicity holds for various starting Δβ values."""
        for db in [0.01, 0.05, 0.1, 0.2]:
            result = multi_zero_monotonicity_scan(db, H=10.0, n_extra=3)
            self.assertTrue(result['monotone'],
                            f"Monotonicity failed for Δβ₀={db}")

    def test_custom_additional_zeros(self):
        """Monotonicity with user-specified additional zeros."""
        extras = [(30.0, 0.15), (50.0, 0.08), (70.0, 0.20)]
        result = multi_zero_monotonicity_scan(0.05, H=10.0,
                                               additional_zeros=extras)
        self.assertTrue(result['monotone'])
        self.assertEqual(result['n_tested'], 3)


class TestOnCriticalIndependence(unittest.TestCase):
    """Tests that S_on is unaffected by off-critical configuration."""

    def test_all_positive(self):
        """S_on > 0 for all α in the tested range."""
        cert = on_critical_independence_certificate()
        self.assertTrue(cert['all_positive'])

    def test_min_S_on_positive(self):
        """Minimum S_on over α range is strictly positive."""
        cert = on_critical_independence_certificate()
        self.assertGreater(cert['min_S_on'], 0.0)

    def test_independence_note_present(self):
        """Certificate includes the independence argument."""
        cert = on_critical_independence_certificate()
        self.assertIn('independent', cert['independence_note'].lower())

    def test_custom_gammas(self):
        """Works with custom on-critical gamma list."""
        custom = GAMMA_30[:5]
        cert = on_critical_independence_certificate(gammas_on=custom)
        self.assertTrue(cert['all_positive'])

    def test_wide_alpha_range(self):
        """Positive over a wider α range."""
        cert = on_critical_independence_certificate(
            alpha_range=(0.001, 5.0), n_alpha=500)
        self.assertTrue(cert['all_positive'])


class TestGap1FullCertificate(unittest.TestCase):
    """Tests for the complete Gap 1 closure certificate."""

    def test_gap1_closed(self):
        """Full Gap 1 certificate reports closed."""
        cert = gap1_multi_zero_certificate(delta_beta_0=0.05, H=10.0)
        self.assertTrue(cert['gap1_closed'])

    def test_certificate_components(self):
        """All four components are present."""
        cert = gap1_multi_zero_certificate()
        for key in ['minimal_counterexample', 'monotonicity',
                     'on_critical_independence', 'domination']:
            self.assertIn(key, cert)

    def test_domination_for_low_lying(self):
        """Domination check confirms Theorem 6.1 for low-lying zeros."""
        cert = gap1_multi_zero_certificate()
        self.assertIn('n_low_lying', cert['domination'])

    def test_various_delta_beta(self):
        """Gap 1 closes for various Δβ₀ values."""
        for db in [0.01, 0.05, 0.1, 0.2]:
            cert = gap1_multi_zero_certificate(delta_beta_0=db)
            self.assertTrue(cert['gap1_closed'],
                            f"Gap 1 not closed for Δβ₀={db}")

    def test_various_H(self):
        """Gap 1 closes for various kernel bandwidths."""
        for H in [5.0, 10.0, 20.0]:
            cert = gap1_multi_zero_certificate(delta_beta_0=0.05, H=H)
            self.assertTrue(cert['gap1_closed'],
                            f"Gap 1 not closed for H={H}")


if __name__ == '__main__':
    unittest.main()
