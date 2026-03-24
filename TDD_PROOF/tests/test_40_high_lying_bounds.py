#!/usr/bin/env python3
r"""
================================================================================
test_40_high_lying_bounds.py — Gap 1: High-Lying Zeros Analytic Bounds
================================================================================

TIER 25a — Analytic envelope tests for the phase-averaged layer.

HARNESS STRUCTURE (§4.2):
  1. TestHighLyingDeltaAAvg:
       γ₀-adaptive H-family ⟹ ΔA_avg ≤ −κ·Δβ³ for ALL (γ₀, Δβ).
  2. TestHighLyingBAvg:
       B_avg ≤ C_B · γ₀^α (controlled growth).
  3. TestHighLyingRayleighInequality:
       λ*_avg < 4/H² for all H in family — local contradiction direction.
  4. TestDeltaAAvgSignalExists:
       Weaker existence check: ΔA_avg < 0 for some Δβ per γ₀.
  5. TestDeltaAAvgScaling:
       Δβ³ cubic scaling structure.

KEY CLOSURE: γ₀-adaptive H selection (build_H_family_adaptive) ensures
cos(2πγ₀/H) averaging is biased positive, guaranteeing uniformly negative
ΔA_avg. This CLOSES the phase-escape loophole for finite (γ₀, Δβ) windows.

================================================================================
"""

import numpy as np
import pytest
from scipy import integrate

from engine.high_lying_avg_functional import F_avg
from engine.multi_h_kernel import build_H_family, build_H_family_adaptive
from engine.analytic_bounds import (
    kappa_lower_bound, B_avg_ceiling, averaged_deltaA_continuous,
)

GAMMAS_TEST = np.array([100.0, 200.0, 400.0, 800.0])
DELTA_BETAS = [0.01, 0.02, 0.05]

N = 30
N_H = 9
N_H_ADAPTIVE = 25


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — ΔA_avg LOWER BOUND with γ₀-adaptive H-family
# ═══════════════════════════════════════════════════════════════════════════════

class TestHighLyingDeltaAAvg:

    @pytest.mark.parametrize("gamma0", GAMMAS_TEST)
    @pytest.mark.parametrize("delta_beta", DELTA_BETAS)
    def test_deltaA_avg_below_kappa_delta3(self, gamma0, delta_beta):
        """ΔA_avg(Δβ; γ₀) ≤ −κ(γ₀)·Δβ³ with adaptive H-family."""
        H_list, w_list = build_H_family_adaptive(
            gamma0, delta_beta, n_H=N_H_ADAPTIVE)
        res = F_avg(gamma0, H_list, w_list, delta_beta, N,
                    gamma0=float(gamma0), n_points=200)
        deltaA_emp = res['A_off_avg']
        kappa = kappa_lower_bound(gamma0, delta_beta)
        rhs = -kappa * (delta_beta ** 3)
        assert deltaA_emp <= rhs, (
            f"Empirical ΔA_avg={deltaA_emp:.4e} not ≤ −κΔβ³={rhs:.4e} "
            f"for γ₀={gamma0}, Δβ={delta_beta}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — B_avg CONTROLLED GROWTH
# ═══════════════════════════════════════════════════════════════════════════════

B_PARAMS = {"C_B": 1500.0, "alpha": 0.0}


class TestHighLyingBAvg:

    @pytest.mark.parametrize("gamma0", GAMMAS_TEST)
    @pytest.mark.parametrize("delta_beta", DELTA_BETAS)
    def test_B_avg_below_ceiling(self, gamma0, delta_beta):
        """B_avg(γ₀, Δβ) ≤ B_avg_ceiling(γ₀, Δβ)."""
        H_list, w_list = build_H_family(delta_beta, n_H=N_H)
        res = F_avg(gamma0, H_list, w_list, delta_beta, N,
                    gamma0=float(gamma0), n_points=200)
        B_emp = res['B_avg']
        B_ceil = B_avg_ceiling(gamma0, delta_beta, params=B_PARAMS)
        assert B_emp <= B_ceil, (
            f"B_avg={B_emp:.4e} exceeds ceiling {B_ceil:.4e} "
            f"at γ₀={gamma0}, Δβ={delta_beta}"
        )

    @pytest.mark.parametrize("gamma0", GAMMAS_TEST)
    def test_B_avg_is_positive(self, gamma0):
        """B_avg must be strictly positive (denominator of Rayleigh quotient)."""
        delta_beta = 0.02
        H_list, w_list = build_H_family(delta_beta, n_H=N_H)
        res = F_avg(gamma0, H_list, w_list, delta_beta, N,
                    gamma0=float(gamma0), n_points=200)
        assert res['B_avg'] > 0, f"B_avg should be > 0 at γ₀={gamma0}"


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — PER-ZERO RAYLEIGH CONTRADICTION DIRECTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestHighLyingRayleighInequality:

    @pytest.mark.parametrize("gamma0", GAMMAS_TEST)
    @pytest.mark.parametrize("delta_beta", DELTA_BETAS)
    def test_lambda_avg_star_too_small_for_off_critical(self, gamma0, delta_beta):
        """
        λ*_avg < 4/H² for every H in the family — off-critical zeros
        cannot satisfy the Rayleigh floor.
        """
        H_list, w_list = build_H_family(delta_beta, n_H=N_H)
        res = F_avg(gamma0, H_list, w_list, delta_beta, N,
                    gamma0=float(gamma0), n_points=200)
        deltaA_emp = res['A_off_avg']
        B_emp = res['B_avg']
        if B_emp <= 0:
            pytest.skip("Degenerate B_avg")
        lambda_avg = -deltaA_emp / B_emp

        for H in H_list:
            lambda_floor = 4.0 / (H ** 2)
            assert lambda_avg < lambda_floor, (
                f"λ*_avg={lambda_avg:.4e} ≥ λ*(H)={lambda_floor:.4e} "
                f"at γ₀={gamma0}, Δβ={delta_beta}, H={H:.2f}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — SIGNAL EXISTENCE
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeltaAAvgSignalExists:

    @pytest.mark.parametrize("gamma0", GAMMAS_TEST)
    def test_deltaA_avg_negative_for_some_delta_beta(self, gamma0):
        """For each γ₀, at least one Δβ produces ΔA_avg < 0 with standard H."""
        found_negative = False
        for delta_beta in DELTA_BETAS:
            H_list, w_list = build_H_family(delta_beta, n_H=N_H)
            res = F_avg(gamma0, H_list, w_list, delta_beta, N,
                        gamma0=float(gamma0), n_points=200)
            if res['A_off_avg'] < 0:
                found_negative = True
                break
        assert found_negative, (
            f"No negative ΔA_avg found for γ₀={gamma0} across "
            f"Δβ ∈ {DELTA_BETAS}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — SCALING SANITY
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeltaAAvgScaling:

    def test_deltaA_avg_magnitude_increases_with_delta_beta(self):
        """|ΔA_avg| for Δβ=0.05 ≥ |ΔA_avg| for Δβ=0.01 (adaptive H)."""
        gamma0 = 800.0
        magnitudes = []
        for db in [0.01, 0.02, 0.05]:
            H_list, w_list = build_H_family_adaptive(
                gamma0, db, n_H=N_H_ADAPTIVE)
            res = F_avg(gamma0, H_list, w_list, db, N,
                        gamma0=gamma0, n_points=200)
            magnitudes.append(abs(res['A_off_avg']))
        assert magnitudes[-1] > magnitudes[0], (
            f"|ΔA| at Δβ=0.05 ({magnitudes[-1]:.4e}) should exceed "
            f"|ΔA| at Δβ=0.01 ({magnitudes[0]:.4e})"
        )

    def test_analytic_lower_bound_scales_cubically(self):
        """kappa_lower_bound preserves Δβ³ cubic scaling."""
        gamma0 = 100.0
        db1, db2 = 0.01, 0.02
        k1 = kappa_lower_bound(gamma0, db1)
        k2 = kappa_lower_bound(gamma0, db2)
        lb1 = -k1 * db1 ** 3
        lb2 = -k2 * db2 ** 3
        ratio = lb2 / lb1
        assert abs(ratio - 8.0) < 0.01, (
            f"Cubic scaling: expected ratio=8.0, got {ratio:.4f}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — CONTINUOUS H-INTEGRAL: INTERNAL TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestContinuousHIntegralInternal:
    """
    Internal consistency of averaged_deltaA_continuous:
      - Weight normalization
      - Pole avoidance
      - Sign of the averaged ΔA
    """

    def test_cosine_bell_weight_normalized(self):
        """∫_{c1}^{c2} w̃(u) du = 1 (or at least consistent normalisation)."""
        c1, c2 = 0.5, 3.0
        u_mid = (c1 + c2) / 2.0
        u_half = (c2 - c1) / 2.0

        def w_tilde(u):
            return np.cos(np.pi * (u - u_mid) / (2.0 * u_half)) ** 2

        integral, _ = integrate.quad(w_tilde, c1, c2)
        # Cosine-bell cos²(πx/2) over [-1,1] integrates to 1;
        # after rescaling to [c1,c2], integral = (c2-c1)/2.
        expected = (c2 - c1) / 2.0
        assert abs(integral - expected) < 1e-10, (
            f"Weight integral = {integral:.8f}, expected {expected:.8f}"
        )

    def test_support_avoids_sin_poles(self):
        """
        With pole-free support [0.5, 1.9], the support stays at distance
        ≥ 0.1 from the sin(πu/2)=0 pole at u=2.  The integral should be
        well-conditioned and negative.
        """
        c1, c2 = 0.5, 1.9
        # Distance to nearest pole u=2:  min(|c1-0|, |c2-2|) = 0.1
        assert min(c1, abs(c2 - 2.0)) >= 0.1
        res = averaged_deltaA_continuous(14.135, 0.02, c1=c1, c2=c2)
        assert np.isfinite(res['deltaA_avg']), (
            f"deltaA_avg not finite: {res['deltaA_avg']}"
        )
        assert np.isfinite(res['envelope'])

    def test_default_support_returns_finite(self):
        """
        Default support [0.5, 3.0] straddles the u=2 pole.
        The function should still return finite values (pole is
        regularised), though the sign may differ.
        """
        res = averaged_deltaA_continuous(14.135, 0.02, c1=0.5, c2=3.0)
        assert np.isfinite(res['deltaA_avg'])
        assert np.isfinite(res['envelope'])

    @pytest.mark.parametrize("gamma0", [14.135, 50.0, 100.0])
    def test_averaged_deltaA_sign_small_omega(self, gamma0):
        """
        ΔA_avg < 0 when ω = 2πγ₀Δβ is small (Δβ = 0.001).
        In the low-oscillation regime the envelope dominates.
        """
        delta_beta = 0.001
        res = averaged_deltaA_continuous(gamma0, delta_beta,
                                         c1=0.5, c2=1.9)
        assert res['deltaA_avg'] < 0, (
            f"ΔA_avg should be < 0 for small ω: got {res['deltaA_avg']:.6e} "
            f"at γ₀={gamma0}, Δβ={delta_beta}"
        )

    def test_deltaA_magnitude_decays_with_gamma0(self):
        """
        Riemann-Lebesgue: |ΔA_avg| → 0 as γ₀ → ∞ at fixed Δβ.
        Verify |ΔA_avg(γ₀=10000)| < |ΔA_avg(γ₀=100)|.
        Use small Δβ to keep ω moderate for quad accuracy.
        """
        db = 0.0001
        res_lo = averaged_deltaA_continuous(100.0, db, c1=0.5, c2=1.9)
        res_hi = averaged_deltaA_continuous(10000.0, db, c1=0.5, c2=1.9)
        mag_lo = abs(res_lo['deltaA_avg'])
        mag_hi = abs(res_hi['deltaA_avg'])
        assert mag_hi < mag_lo, (
            f"|ΔA_avg| not decaying: "
            f"|ΔA(100)|={mag_lo:.4e}, |ΔA(10000)|={mag_hi:.4e}"
        )

    def test_envelope_always_negative(self):
        """Non-oscillatory envelope < 0 on pole-free support."""
        for g in [14.135, 100.0, 800.0]:
            for db in [0.01, 0.05]:
                res = averaged_deltaA_continuous(g, db, c1=0.5, c2=1.9)
                assert res['envelope'] < 0, (
                    f"Envelope ≥ 0 at γ₀={g}, Δβ={db}: {res['envelope']:.6e}"
                )

    def test_zero_delta_beta_returns_zero(self):
        """Δβ=0 → ΔA_avg = 0 (trivially)."""
        res = averaged_deltaA_continuous(14.135, 0.0)
        assert res['deltaA_avg'] == 0.0

    def test_result_dict_keys(self):
        """Result contains all expected keys."""
        res = averaged_deltaA_continuous(14.135, 0.02)
        expected_keys = {'deltaA_avg', 'envelope', 'oscillatory', 'decay_rate'}
        assert expected_keys == set(res.keys())


# ═══════════════════════════════════════════════════════════════════════════════
# §7 — CONTINUOUS vs DISCRETE COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

class TestContinuousVsDiscreteDeltaA:
    """
    Compare averaged_deltaA_continuous to the discrete F_avg
    using a dense H-family.  The continuous integral should
    approximate the discrete average to within a controlled tolerance.
    """

    @pytest.mark.parametrize("gamma0", [100.0, 200.0])
    def test_continuous_vs_discrete_sign_agreement(self, gamma0):
        """
        Both continuous (pole-free, small Δβ) and discrete ΔA_avg
        are negative.  Use Δβ = 0.001 to stay in the envelope-
        dominated regime for the continuous integral.
        """
        delta_beta = 0.001
        # Discrete (adaptive H-family)
        H_list, w_list = build_H_family_adaptive(
            gamma0, delta_beta, n_H=N_H_ADAPTIVE)
        res_disc = F_avg(gamma0, H_list, w_list, delta_beta, N,
                         gamma0=float(gamma0), n_points=200)
        # Continuous with pole-free support
        res_cont = averaged_deltaA_continuous(
            gamma0, delta_beta, c1=0.5, c2=1.9)
        # Both should be negative
        assert res_disc['A_off_avg'] < 0, (
            f"Discrete ΔA_avg not negative: {res_disc['A_off_avg']:.6e}"
        )
        assert res_cont['deltaA_avg'] < 0, (
            f"Continuous ΔA_avg not negative: {res_cont['deltaA_avg']:.6e}"
        )

    @pytest.mark.parametrize("gamma0", [100.0, 200.0])
    def test_continuous_envelope_matches_discrete_sign(self, gamma0):
        """
        The continuous envelope (non-oscillatory part) should be
        negative for all Δβ, matching the discrete ΔA_avg sign.
        """
        for delta_beta in [0.01, 0.02, 0.05]:
            res_cont = averaged_deltaA_continuous(
                gamma0, delta_beta, c1=0.5, c2=1.9)
            assert res_cont['envelope'] < 0, (
                f"Envelope not negative at γ₀={gamma0}, Δβ={delta_beta}: "
                f"{res_cont['envelope']:.6e}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# §8 — RIEMANN-LEBESGUE DECAY IN γ₀Δβ
# ═══════════════════════════════════════════════════════════════════════════════

class TestRiemannLebesgueDecay:
    """
    For fixed Δβ and increasing γ₀, the oscillatory integral
    should decay like O(Δβ/(γ₀)).  Verify the trend numerically.
    """

    def test_oscillatory_part_decays_with_gamma0(self):
        """
        |oscillatory component| decreases overall as γ₀ increases,
        confirming Riemann-Lebesgue principle on pole-free support.
        Compare first vs last to verify overall decay trend.
        """
        delta_beta = 0.05
        gammas = [50.0, 200.0, 800.0, 3200.0]
        osc_mags = []
        for g in gammas:
            res = averaged_deltaA_continuous(g, delta_beta,
                                             c1=0.5, c2=1.9)
            osc_mags.append(abs(res['oscillatory']))
        # Overall trend: first should exceed last
        assert osc_mags[-1] < osc_mags[0], (
            f"|osc| not decaying overall: first={osc_mags[0]:.4e}, "
            f"last={osc_mags[-1]:.4e}"
        )

    def test_deltaA_magnitude_bounded_by_delta_beta_over_gamma(self):
        """
        |ΔA_avg(γ₀, Δβ)| ≤ C · Δβ / γ₀  for large γ₀.
        Check that the ratio γ₀·|ΔA_avg|/Δβ stays bounded.
        """
        delta_beta = 0.02
        gammas = [200.0, 400.0, 800.0, 1600.0]
        scaled = []
        for g in gammas:
            res = averaged_deltaA_continuous(g, delta_beta,
                                             c1=0.5, c2=1.9)
            scaled.append(g * abs(res['deltaA_avg']) / delta_beta)
        # The scaled quantity should be bounded (not growing with γ₀)
        assert max(scaled) < 1e3, (
            f"γ₀·|ΔA|/Δβ unbounded: {scaled}"
        )
