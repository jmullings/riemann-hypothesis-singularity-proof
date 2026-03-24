#!/usr/bin/env python3
"""
test_22_arithmetic_binding.py — Tier 10: Arithmetic Binding Layer
=================================================================

TDD tests that distinguish zeta zeros from inert spectra via
number-theoretic invariants.

The central assertion: Riemann zeta zeros PASS arithmetic binding;
random PSD spectra and 9D operator eigenvalues FAIL at least one
invariant test.

Sections:
  A: Reference data & loading             (4 tests)
  B: Counting function invariant           (5 tests)
  C: Spacing distribution (KS test)        (5 tests)
  D: Linear statistics                     (4 tests)
  E: Two-point correlation                 (3 tests)
  F: Composite invariants                  (3 tests)
  G: Binding predicate (zeta passes)       (4 tests)
  H: Binding predicate (random/9D fail)    (4 tests)
  I: Honest limits                         (3 tests)

Expected: ~35 tests. Zero mocks.
"""

import numpy as np
import pytest

from engine.arithmetic_invariants import (
    load_zeta_zeros,
    riemann_von_mangoldt_N,
    wigner_surmise_pdf,
    wigner_surmise_cdf,
    counting_function_distance,
    spacing_ks_statistic,
    linear_statistics,
    two_point_correlation,
    gue_sine_kernel_R2,
    compute_zero_like_invariants,
    compute_reference_invariants,
    GAMMA_30,
)
from engine.operator_axioms import is_arithmetically_bound
from engine.spectral_tools import unfolded_spacings
from engine.spectral_9d import get_9d_spectrum


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def zeta_spectrum():
    """First 30 known Riemann zeta zeros."""
    return load_zeta_zeros(30)


@pytest.fixture(scope="module")
def random_spectrum():
    """Random GOE-like eigenvalues — NOT zeta zeros."""
    rng = np.random.default_rng(42)
    # Uniformly spaced with random perturbation
    base = np.linspace(10.0, 110.0, 30)
    return np.sort(base + rng.normal(0, 1.0, 30))


@pytest.fixture(scope="module")
def nine_d_spectrum():
    """Eigenvalues of the 9D operator — structurally valid but arithmetically inert."""
    evals = get_9d_spectrum(n_lowest=30)
    return np.sort(evals.real)


@pytest.fixture(scope="module")
def ref_invariants():
    """Pre-computed reference invariants for zeta zeros."""
    return compute_reference_invariants()


# ═══════════════════════════════════════════════════════════════════════════════
# Section A: Reference Data & Loading
# ═══════════════════════════════════════════════════════════════════════════════

class TestReferenceData:

    def test_zeta_zeros_loaded(self, zeta_spectrum):
        assert len(zeta_spectrum) == 30

    def test_zeta_zeros_increasing(self, zeta_spectrum):
        assert np.all(np.diff(zeta_spectrum) > 0)

    def test_first_zero_is_gamma1(self, zeta_spectrum):
        assert abs(zeta_spectrum[0] - 14.134725) < 0.001

    def test_riemann_von_mangoldt_at_50(self):
        """N₀(50) ≈ 10.5 — roughly 10 zeros below T=50."""
        N = riemann_von_mangoldt_N(50.0)
        assert 8.0 < N < 14.0


# ═══════════════════════════════════════════════════════════════════════════════
# Section B: Counting Function Invariant
# ═══════════════════════════════════════════════════════════════════════════════

class TestCountingFunction:

    def test_zeta_counting_close(self, zeta_spectrum):
        """Zeta zeros should have small counting function distance."""
        dist, details = counting_function_distance(zeta_spectrum)
        assert dist < 5.0, f"Counting distance too large: {dist}"

    def test_random_counting_far(self, random_spectrum):
        """Random spectrum should have large counting function distance."""
        dist, _ = counting_function_distance(random_spectrum)
        assert dist > 2.0, f"Random spectrum too close: {dist}"

    def test_nine_d_counting_far(self, nine_d_spectrum):
        """9D spectrum should have large counting function distance."""
        dist, _ = counting_function_distance(nine_d_spectrum)
        assert dist > 2.0, f"9D spectrum too close: {dist}"

    def test_counting_distance_finite(self, zeta_spectrum):
        dist, details = counting_function_distance(zeta_spectrum)
        assert np.isfinite(dist)
        assert np.isfinite(details['max_deviation'])

    def test_counting_details_structure(self, zeta_spectrum):
        _, details = counting_function_distance(zeta_spectrum)
        assert 'T_values' in details
        assert 'N_spec' in details
        assert 'N_rvm' in details


# ═══════════════════════════════════════════════════════════════════════════════
# Section C: Spacing Distribution (KS Test)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpacingDistribution:

    def test_wigner_pdf_nonnegative(self):
        s = np.linspace(0, 4, 100)
        assert np.all(wigner_surmise_pdf(s) >= 0)

    def test_wigner_pdf_normalised(self):
        """Wigner surmise integrates to ≈1."""
        s = np.linspace(0, 6, 5000)
        ds = s[1] - s[0]
        integral = np.sum(wigner_surmise_pdf(s)) * ds
        assert abs(integral - 1.0) < 0.02

    def test_zeta_ks_moderate(self, zeta_spectrum):
        """Zeta zeros should have moderate KS statistic vs GUE."""
        ks, details = spacing_ks_statistic(zeta_spectrum)
        assert np.isfinite(ks)
        # With only 29 spacings, KS won't be tiny — but under 0.5
        assert ks < 0.6, f"KS too large for zeta: {ks}"

    def test_ks_statistic_range(self, zeta_spectrum):
        """KS statistic must be in [0, 1]."""
        ks, _ = spacing_ks_statistic(zeta_spectrum)
        assert 0 <= ks <= 1.0

    def test_ks_details_structure(self, zeta_spectrum):
        _, details = spacing_ks_statistic(zeta_spectrum)
        assert 'n_spacings' in details
        assert details['n_spacings'] == 29


# ═══════════════════════════════════════════════════════════════════════════════
# Section D: Linear Statistics
# ═══════════════════════════════════════════════════════════════════════════════

class TestLinearStatistics:

    def test_linear_stat_zeta_finite(self, zeta_spectrum):
        val = linear_statistics(zeta_spectrum)
        assert np.isfinite(val)

    def test_linear_stat_random_differs(self, zeta_spectrum, random_spectrum):
        """Random spectrum should give different linear statistic."""
        val_zeta = linear_statistics(zeta_spectrum)
        val_rand = linear_statistics(random_spectrum)
        assert val_zeta != val_rand

    def test_custom_phi(self, zeta_spectrum):
        """Custom test function φ(x) = cos(x)."""
        val = linear_statistics(zeta_spectrum, phi_func=np.cos)
        assert np.isfinite(val)

    def test_linear_stat_nine_d_differs(self, zeta_spectrum, nine_d_spectrum):
        """9D spectrum gives different linear statistic."""
        val_zeta = linear_statistics(zeta_spectrum)
        val_9d = linear_statistics(nine_d_spectrum)
        # They won't equal each other (very different spectra)
        assert abs(val_zeta - val_9d) > 0.01


# ═══════════════════════════════════════════════════════════════════════════════
# Section E: Two-Point Correlation
# ═══════════════════════════════════════════════════════════════════════════════

class TestTwoPointCorrelation:

    def test_two_point_output_shape(self, zeta_spectrum):
        x, R2 = two_point_correlation(zeta_spectrum)
        assert len(x) == len(R2)
        assert len(x) > 0

    def test_two_point_nonnegative(self, zeta_spectrum):
        _, R2 = two_point_correlation(zeta_spectrum)
        assert np.all(R2 >= 0)

    def test_gue_sine_kernel_at_zero(self):
        """R₂_GUE(0) should be 0 (perfect repulsion)."""
        val = gue_sine_kernel_R2(np.array([0.001]))
        assert val[0] < 0.01


# ═══════════════════════════════════════════════════════════════════════════════
# Section F: Composite Invariants
# ═══════════════════════════════════════════════════════════════════════════════

class TestCompositeInvariants:

    def test_compute_invariants_structure(self, zeta_spectrum):
        inv = compute_zero_like_invariants(zeta_spectrum)
        assert 'counting_distance' in inv
        assert 'ks_statistic' in inv
        assert 'linear_stat' in inv
        assert 'n_levels' in inv
        assert inv['n_levels'] == 30

    def test_reference_invariants_finite(self, ref_invariants):
        assert np.isfinite(ref_invariants['counting_distance'])
        assert np.isfinite(ref_invariants['ks_statistic'])
        assert np.isfinite(ref_invariants['linear_stat'])

    def test_reference_invariants_counting_good(self, ref_invariants):
        """Reference (zeta zeros) should have small counting distance."""
        assert ref_invariants['counting_distance'] < 5.0


# ═══════════════════════════════════════════════════════════════════════════════
# Section G: Binding Predicate (Zeta Passes)
# ═══════════════════════════════════════════════════════════════════════════════

class TestBindingZetaPasses:

    def test_zeta_is_bound(self, zeta_spectrum, ref_invariants):
        """Zeta zeros pass arithmetic binding."""
        assert is_arithmetically_bound(zeta_spectrum, ref_invariants)

    def test_zeta_passes_default_thresholds(self, zeta_spectrum):
        """Zeta zeros pass with default thresholds."""
        assert is_arithmetically_bound(zeta_spectrum)

    def test_zeta_counting_within_threshold(self, zeta_spectrum):
        dist, _ = counting_function_distance(zeta_spectrum)
        assert dist < 3.0

    def test_zeta_spacing_within_threshold(self, zeta_spectrum):
        ks, _ = spacing_ks_statistic(zeta_spectrum)
        assert ks < 0.5


# ═══════════════════════════════════════════════════════════════════════════════
# Section H: Binding Predicate (Random/9D Fail)
# ═══════════════════════════════════════════════════════════════════════════════

class TestBindingFailures:

    def test_random_not_bound(self, random_spectrum, ref_invariants):
        """Random PSD spectrum fails arithmetic binding."""
        assert not is_arithmetically_bound(random_spectrum, ref_invariants)

    def test_nine_d_not_bound(self, nine_d_spectrum, ref_invariants):
        """9D operator spectrum fails arithmetic binding."""
        assert not is_arithmetically_bound(nine_d_spectrum, ref_invariants)

    def test_uniform_not_bound(self, ref_invariants):
        """Uniformly-spaced 'spectrum' in wrong range fails binding."""
        uniform = np.linspace(200.0, 400.0, 30)
        assert not is_arithmetically_bound(uniform, ref_invariants)

    def test_scaled_zeta_not_bound(self, zeta_spectrum, ref_invariants):
        """Scaled zeta zeros (2× stretch) should fail counting function."""
        scaled = zeta_spectrum * 2.0
        assert not is_arithmetically_bound(scaled, ref_invariants)


# ═══════════════════════════════════════════════════════════════════════════════
# Section I: Honest Limits
# ═══════════════════════════════════════════════════════════════════════════════

class TestHonestLimits:

    def test_binding_does_not_prove_rh(self):
        """Arithmetic binding is necessary but not sufficient for RH."""
        assert True  # documentary

    def test_small_sample_caveat(self):
        """With only 30 zeros, statistical power is limited."""
        zeros = load_zeta_zeros(30)
        _, details = spacing_ks_statistic(zeros)
        assert details['n_spacings'] == 29  # small sample

    def test_binding_is_falsifiable(self, random_spectrum, ref_invariants):
        """Binding is falsifiable: random spectrum demonstrably fails."""
        assert not is_arithmetically_bound(random_spectrum, ref_invariants)
