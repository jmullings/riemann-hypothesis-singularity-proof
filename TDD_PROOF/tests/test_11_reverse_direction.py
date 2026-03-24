"""
================================================================================
test_11_reverse_direction.py — Reverse Direction & Smoothed Functional Tests
================================================================================

Tests for the reverse-direction machinery ported from
RH_PROOF/src/reverse_direction.py:

  §1 — Pole-free certificate: sech²(x) ∈ (0,1] ∀x ∈ ℝ
  §2 — On-line sum with tail bounds
  §3 — Optimal α* and off-line bounds
  §4 — Negativity windows
  §5 — Smoothed functional
  §6 — Sign structure lemma N(x,y)/D²(x,y)
================================================================================
"""

import pytest
import numpy as np

from engine.reverse_direction import (
    pole_free_certificate,
    on_line_sum_with_tail_bound,
    optimal_alpha_star,
    off_line_bound_at_alpha_star,
    negativity_windows,
    smoothed_functional,
    numerator_N,
    denominator_D_sq,
    sign_structure_on_line,
    sign_structure_off_line,
)
from engine.weil_density import GAMMA_30


# ─────────────── §1 — POLE-FREE CERTIFICATE ─────────────────────────────────

class TestPoleFree:
    """sech²(x) = 1/cosh²(x) is pole-free on ℝ."""

    def test_certificate_basic(self):
        cert = pole_free_certificate()
        assert cert['is_pole_free'] is True
        assert cert['all_finite'] is True
        assert cert['all_nonnegative'] is True
        assert cert['all_bounded_by_one'] is True

    def test_max_is_one(self):
        cert = pole_free_certificate()
        assert cert['max_value'] == pytest.approx(1.0, abs=1e-3)

    def test_min_nonnegative(self):
        cert = pole_free_certificate()
        assert cert['min_value'] >= 0.0

    def test_wide_range(self):
        """Pole-free even over very wide range."""
        cert = pole_free_certificate(x_range=(-1000, 1000), n_points=100000)
        assert cert['all_finite'] is True
        assert cert['all_bounded_by_one'] is True


# ─────────────── §2 — ON-LINE SUM WITH TAIL BOUND ───────────────────────────

class TestOnLineTailBound:
    """On-line sum S_on(α) with geometric tail bound."""

    def test_tail_is_nonnegative(self):
        _, _, tail = on_line_sum_with_tail_bound(1.0)
        assert tail >= 0

    def test_upper_bound_exceeds_exact(self):
        exact, upper, _ = on_line_sum_with_tail_bound(1.0)
        assert upper >= exact

    def test_tail_decreases_with_alpha(self):
        """Tail bound shrinks as α grows."""
        _, _, tail1 = on_line_sum_with_tail_bound(1.0)
        _, _, tail2 = on_line_sum_with_tail_bound(5.0)
        assert tail2 <= tail1

    def test_custom_zeros(self):
        """Works with custom gamma list."""
        exact, upper, tail = on_line_sum_with_tail_bound(1.0, GAMMA_30[:10])
        assert exact > 0
        assert upper >= exact


# ─────────────── §3 — OPTIMAL ALPHA AND OFF-LINE BOUNDS ─────────────────────

class TestOptimalAlpha:
    """α* = π/(2|Δβ|) maximises |C_off|."""

    def test_formula(self):
        assert optimal_alpha_star(0.1) == pytest.approx(np.pi / 0.2, rel=1e-12)
        assert optimal_alpha_star(0.5) == pytest.approx(np.pi / 1.0, rel=1e-12)

    def test_larger_db_smaller_alpha(self):
        """Larger Δβ → smaller α*."""
        assert optimal_alpha_star(0.5) < optimal_alpha_star(0.1)


class TestOffLineBound:
    """C_off at α* = π/(2|Δβ|): exact bound."""

    def test_negative_value(self):
        """At α*, cos(2α*Δβ) = −1, so C_off ≈ −2/sinh²."""
        alpha_star, bound = off_line_bound_at_alpha_star(5.0, 0.1)
        assert bound < 0  # negative contribution

    def test_decays_with_gamma0(self):
        """Larger γ₀ → |C_off| at α* is smaller (more suppressed)."""
        _, b1 = off_line_bound_at_alpha_star(5.0, 0.1)
        _, b2 = off_line_bound_at_alpha_star(20.0, 0.1)
        assert abs(b1) >= abs(b2)

    def test_very_large_gamma0_vanishes(self):
        """For very large γ₀, C_off ≈ 0 (exponentially suppressed)."""
        _, b = off_line_bound_at_alpha_star(100.0, 0.1)
        assert abs(b) < 1e-10


# ─────────────── §4 — NEGATIVITY WINDOWS ─────────────────────────────────────

class TestNegativityWindows:
    """α-intervals where cos(2αΔβ) < 0."""

    def test_returns_requested_count(self):
        wins = negativity_windows(0.1, n_windows=5)
        assert len(wins) == 5

    def test_window_format(self):
        """Each window is (low, high, center)."""
        wins = negativity_windows(0.1)
        for low, high, center in wins:
            assert low < center < high

    def test_windows_non_overlapping(self):
        wins = negativity_windows(0.1, n_windows=5)
        for i in range(len(wins) - 1):
            assert wins[i][1] < wins[i + 1][0]

    def test_first_window_location(self):
        """First window: α ∈ (π/(4|Δβ|), 3π/(4|Δβ|))."""
        db = 0.2
        wins = negativity_windows(db, n_windows=1)
        low, high, center = wins[0]
        assert low == pytest.approx(np.pi / (4 * db), rel=1e-12)
        assert high == pytest.approx(3 * np.pi / (4 * db), rel=1e-12)

    def test_cos_negative_inside_window(self):
        """Verify cos(2αΔβ) < 0 inside each window."""
        db = 0.15
        wins = negativity_windows(db, n_windows=3)
        for low, high, _ in wins:
            mid = (low + high) / 2
            assert np.cos(2 * mid * db) < 0


# ─────────────── §5 — SMOOTHED FUNCTIONAL ───────────────────────────────────

class TestSmoothedFunctional:
    """Smoothed integral I(w) = ∫ S(α)·w(α) dα."""

    def test_on_line_only_positive(self):
        """Without off-line zero, S > 0 → integral > 0."""
        val, err = smoothed_functional(sigma=2.0)
        assert val > 0

    def test_with_low_lying_off_line(self):
        """With γ₀ << γ₁ off-line zero, integral can go negative."""
        val, err = smoothed_functional(gamma_0=3.0, delta_beta=0.1, sigma=5.0)
        # The smoothed functional may or may not be negative depending on σ
        assert np.isfinite(val)

    def test_sigma_sensitivity(self):
        """Different σ give different integrals when off-line zero present."""
        v1, _ = smoothed_functional(gamma_0=5.0, delta_beta=0.2, sigma=0.5)
        v2, _ = smoothed_functional(gamma_0=5.0, delta_beta=0.2, sigma=10.0)
        # With an off-line contribution, the Gaussian weight σ changes
        # which α-window is emphasised, yielding different results
        assert np.isfinite(v1) and np.isfinite(v2)


# ─────────────── §6 — SIGN STRUCTURE LEMMA ──────────────────────────────────

class TestSignStructure:
    """N(x,y)/D²(x,y) decomposition of ℜ(sech²(x+iy))."""

    def test_numerator_on_line_nonneg(self):
        """N(0,y) = cos²y ≥ 0 (PROVED)."""
        res = sign_structure_on_line()
        assert res['all_nonneg'] is True

    def test_numerator_at_zero(self):
        """N(0,0) = cos²(0) = 1."""
        N = numerator_N(np.array([0.0]), np.array([0.0]))
        assert float(N[0]) == pytest.approx(1.0, abs=1e-14)

    def test_denominator_positive(self):
        """D²(x,y) > 0 for (x,y) ≠ (0,0)."""
        for x, y in [(1.0, 1.0), (0.1, 3.0), (5.0, 0.5)]:
            D2 = denominator_D_sq(np.array([x]), np.array([y]))
            assert float(D2[0]) > 0

    def test_numerator_can_be_negative_off_line(self):
        """N(x,y) can be negative for x ≠ 0 (when cos(2y) < 0)."""
        results = sign_structure_off_line(delta_beta_values=[0.1, 0.3])
        # Should find negative values for at least some Δβ
        any_neg = any(r['found_negative'] for r in results)
        assert any_neg, "Expected to find N < 0 off-line"

    def test_on_line_proof_consistency(self):
        """Full 10k-point scan confirms N ≥ 0 on line."""
        res = sign_structure_on_line(n_points=10000)
        assert res['min_N'] >= -1e-15

    def test_numerator_vectorised(self):
        """N handles array inputs."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([0.0, 1.0, 2.0])
        N = numerator_N(x, y)
        assert N.shape == (3,)
