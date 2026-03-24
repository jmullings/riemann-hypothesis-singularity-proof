#!/usr/bin/env python3
"""
================================================================================
test_51_functional_averaging.py — Gap 2: Full-Functional H-Averaging Tests
================================================================================

Tier 51: Tests for engine/functional_averaging.py

Validates that B_avg ≥ 0, S_on_avg > 0, and the selective ΔA sign
analysis is justified under H-averaging by linearity of summation.
================================================================================
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import numpy as np

from engine.functional_averaging import (
    averaged_B_nonneg_certificate,
    averaged_on_critical_nonneg_certificate,
    full_functional_averaging_certificate,
    linearity_preservation_certificate,
    gap2_functional_averaging_certificate,
)
from engine.weil_density import GAMMA_30


class TestAveragedBNonNegativity(unittest.TestCase):
    """Tests that B_avg = Σ w_j B_j ≥ 0."""

    def test_B_avg_nonneg_uniform_weights(self):
        """B_avg ≥ 0 with uniform weights."""
        H_list = [10.0, 15.0, 20.0]
        w_list = [1/3, 1/3, 1/3]
        cert = averaged_B_nonneg_certificate(14.135, H_list, w_list, N=10)
        self.assertTrue(cert['certified'])
        self.assertGreaterEqual(cert['B_avg'], -1e-15)

    def test_all_individual_B_nonneg(self):
        """Each individual B(T₀, H_j) ≥ 0."""
        H_list = [5.0, 10.0, 20.0, 50.0]
        w_list = [0.25, 0.25, 0.25, 0.25]
        cert = averaged_B_nonneg_certificate(14.135, H_list, w_list, N=10)
        self.assertTrue(cert['all_B_nonneg'])
        for b in cert['B_individual']:
            self.assertGreaterEqual(b, -1e-15)

    def test_weights_nonneg_check(self):
        """Certificate verifies weight non-negativity."""
        H_list = [10.0, 20.0]
        w_list = [0.5, 0.5]
        cert = averaged_B_nonneg_certificate(14.135, H_list, w_list, N=10)
        self.assertTrue(cert['all_weights_nonneg'])

    def test_single_H(self):
        """Works for a single H value."""
        cert = averaged_B_nonneg_certificate(14.135, [10.0], [1.0], N=10)
        self.assertTrue(cert['certified'])

    def test_various_T0(self):
        """B_avg ≥ 0 at various T₀ positions."""
        H_list = [10.0, 15.0]
        w_list = [0.5, 0.5]
        for T0 in [14.135, 21.022, 30.0, 50.0]:
            cert = averaged_B_nonneg_certificate(T0, H_list, w_list, N=10)
            self.assertTrue(cert['certified'],
                            f"Failed for T₀={T0}")


class TestAveragedOnCriticalNonNegativity(unittest.TestCase):
    """Tests that S_on_avg > 0 under averaging."""

    def test_S_on_avg_positive(self):
        """S_on_avg > 0 with uniform weights."""
        alpha_list = [0.05, 0.1, 0.2]
        w_list = [1/3, 1/3, 1/3]
        cert = averaged_on_critical_nonneg_certificate(alpha_list, w_list)
        self.assertTrue(cert['certified'])
        self.assertGreater(cert['S_on_avg'], 0.0)

    def test_all_individual_S_positive(self):
        """Each S_on(α_j) > 0."""
        alpha_list = [0.01, 0.05, 0.1, 0.5, 1.0]
        w_list = np.ones(5) / 5
        cert = averaged_on_critical_nonneg_certificate(alpha_list, w_list)
        self.assertTrue(cert['all_S_positive'])

    def test_custom_gammas(self):
        """Works with a subset of on-critical zeros."""
        alpha_list = [0.1, 0.2]
        w_list = [0.5, 0.5]
        cert = averaged_on_critical_nonneg_certificate(
            alpha_list, w_list, gammas=GAMMA_30[:5])
        self.assertTrue(cert['certified'])

    def test_single_alpha(self):
        """Single α point gives positive result."""
        cert = averaged_on_critical_nonneg_certificate([0.1], [1.0])
        self.assertTrue(cert['certified'])


class TestFullFunctionalAveraging(unittest.TestCase):
    """Tests for the complete functional decomposition certificate."""

    def test_gap2_closed_typical(self):
        """Gap 2 closes for typical parameters."""
        H_list = [15.0, 18.0, 20.0, 22.0, 25.0]
        w_list = np.ones(5) / 5
        cert = full_functional_averaging_certificate(
            14.135, H_list, w_list, delta_beta=0.05, N=10)
        self.assertTrue(cert['gap2_closed'])

    def test_B_avg_in_decomposition(self):
        """B_avg ≥ 0 within the full decomposition."""
        H_list = [15.0, 20.0, 25.0]
        w_list = np.ones(3) / 3
        cert = full_functional_averaging_certificate(
            14.135, H_list, w_list, delta_beta=0.05, N=10)
        self.assertGreaterEqual(cert['B_avg'], -1e-15)

    def test_base_deltaA_avg_negative(self):
        """Base (γ₀-independent) ΔA_avg < 0 in the decomposition."""
        H_list = [15.0, 20.0, 25.0]
        w_list = np.ones(3) / 3
        cert = full_functional_averaging_certificate(
            14.135, H_list, w_list, delta_beta=0.05, N=10)
        self.assertLess(cert['base_deltaA_avg'], 0.0)

    def test_selective_justified(self):
        """Selective sign analysis is justified (B≥0 + base ΔA<0)."""
        H_list = [15.0, 20.0, 25.0]
        w_list = np.ones(3) / 3
        cert = full_functional_averaging_certificate(
            14.135, H_list, w_list, delta_beta=0.05, N=10)
        self.assertTrue(cert['selective_sign_justified'])

    def test_justification_string(self):
        """Justification is a non-empty explanatory string."""
        H_list = [15.0, 20.0]
        w_list = [0.5, 0.5]
        cert = full_functional_averaging_certificate(
            14.135, H_list, w_list, delta_beta=0.05, N=10)
        self.assertIn('linearity', cert['justification'].lower())


class TestLinearityPreservation(unittest.TestCase):
    """Tests for the linearity preservation lemma."""

    def test_all_schemes_nonneg(self):
        """B_avg ≥ 0 under uniform, linear, and cosine weight schemes."""
        H_values = [10.0, 15.0, 20.0, 25.0]
        cert = linearity_preservation_certificate(14.135, H_values, N=10)
        self.assertTrue(cert['all_schemes_nonneg'])

    def test_individual_B_nonneg(self):
        """Each individual B value is non-negative."""
        H_values = [10.0, 20.0]
        cert = linearity_preservation_certificate(14.135, H_values, N=10)
        for b in cert['B_individual']:
            self.assertGreaterEqual(b, -1e-15)

    def test_uniform_weights(self):
        """Uniform weights give non-negative B_avg."""
        H_values = [10.0, 15.0, 20.0]
        cert = linearity_preservation_certificate(14.135, H_values, N=10)
        self.assertTrue(cert['weight_results']['uniform']['nonneg'])

    def test_various_T0(self):
        """Linearity holds at various T₀ positions."""
        H_values = [10.0, 20.0]
        for T0 in [14.135, 25.0, 50.0]:
            cert = linearity_preservation_certificate(T0, H_values, N=10)
            self.assertTrue(cert['all_schemes_nonneg'],
                            f"Failed for T₀={T0}")


class TestGap2FullCertificate(unittest.TestCase):
    """Tests for the complete Gap 2 closure certificate."""

    def test_gap2_closed(self):
        """Full Gap 2 certificate reports closed."""
        cert = gap2_functional_averaging_certificate(
            T0=14.135, delta_beta=0.05, N=10)
        self.assertTrue(cert['gap2_closed'])

    def test_certificate_components(self):
        """All three components are present."""
        cert = gap2_functional_averaging_certificate(T0=14.135, delta_beta=0.05, N=10)
        for key in ['functional_certificate', 'on_critical_certificate',
                     'linearity_certificate']:
            self.assertIn(key, cert)

    def test_various_delta_beta(self):
        """Gap 2 closes for various Δβ values."""
        for db in [0.02, 0.05, 0.1]:
            cert = gap2_functional_averaging_certificate(
                T0=14.135, delta_beta=db, N=10)
            self.assertTrue(cert['gap2_closed'],
                            f"Gap 2 not closed for Δβ={db}")

    def test_various_T0(self):
        """Gap 2 closes at various heights."""
        for T0 in [14.135, 21.022]:
            cert = gap2_functional_averaging_certificate(
                T0=T0, delta_beta=0.05, N=10)
            self.assertTrue(cert['gap2_closed'],
                            f"Gap 2 not closed for T₀={T0}")


if __name__ == '__main__':
    unittest.main()
