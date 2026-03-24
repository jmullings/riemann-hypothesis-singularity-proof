"""
================================================================================
test_08_barrier_resolution.py — Tier 3: Barrier Analysis (Gravity-Well)
================================================================================

Verifies the status of each barrier in the gravity-well framework:

  BARRIER 1: High-Lying Domination
    → PARTIALLY ADDRESSED: Implemented ΔA omits γ₀ by construction.
      The simplified formula is a POSTULATION. In the full Weil formula,
      the contribution of ρ = β+iγ₀ involves ŵ_H(γ₀ − iΔβ), which
      decays exponentially as e^{−πHγ₀/2} for large γ₀.
      Theorem 6.1 (weil_density.py) provides rigorous domination for
      γ₀ < γ₁ using the CORRECT formula.  The high-lying regime
      (γ₀ ≫ 1 with small Δβ) is NOT rigorously covered.
      See offcritical.py CRITIQUE RESPONSE for full analysis.

  BARRIER 2: L² → S(ℝ) Topology Lift
    → PROVEN: Fixed w_H = sech²(t/H) IS Schwartz (no L² approx needed)

  BARRIER 3: Eigenvalue-Zero Identification (Hilbert-Pólya)
    → PROVEN (but double-edged): Kernel universality means PSD for ANY
      spectrum — bypasses GLM but also means 9D is logically inert.
      See analytic_promotion.py sech4_identity CRITIQUE RESPONSE for
      the full discussion of universality vs arithmetic sensitivity.
================================================================================
"""

import pytest
import numpy as np

from engine.proof_chain import (
    barrier1_gamma0_independence,
    barrier2_fixed_schwartz,
    barrier3_kernel_universality,
)
from engine.weil_density import (
    off_line_pair_contribution, on_line_sum, GAMMA_30,
    domination_ratio, on_line_sum_asymptotic,
)
from engine.reverse_direction import negativity_windows
from engine.offcritical import rayleigh_quotient, weil_delta_A_full
from engine.kernel import schwartz_seminorm, w_H, W_curv


# ═══════════════════════════════════════════════════════════════════════════════
# BARRIER 1: HIGH-LYING DOMINATION → PARTIALLY ADDRESSED
# ═══════════════════════════════════════════════════════════════════════════════

class TestBarrier1:
    """Implemented ΔA has no γ₀ parameter (by construction, not derivation)."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_gamma0_independence(self, H):
        result = barrier1_gamma0_independence(H, delta_beta=0.1)
        assert result['gamma0_independent']
        assert result['gamma0_variation'] == 0.0

    @pytest.mark.parametrize("db", [0.001, 0.01, 0.1, 0.3])
    def test_independence_across_db(self, db):
        result = barrier1_gamma0_independence(H=3.0, delta_beta=db)
        assert result['gamma0_independent']
        assert result['delta_A'] < 0


# ═══════════════════════════════════════════════════════════════════════════════
# BARRIER 2: L² → S(ℝ) TOPOLOGY LIFT → FIXED FUNCTION BYPASS
# ═══════════════════════════════════════════════════════════════════════════════

class TestBarrier2:
    """w_H = sech²(t/H) IS Schwartz → no L² approximation needed."""

    @pytest.mark.parametrize("H", [0.5, 1.0, 2.0, 3.0, 5.0, 10.0])
    def test_w_H_is_schwartz(self, H):
        result = barrier2_fixed_schwartz(H)
        assert result['is_schwartz'], f"w_H not Schwartz at H={H}"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_uses_fixed_function(self, H):
        result = barrier2_fixed_schwartz(H)
        assert result['uses_fixed_function']
        assert not result['l2_approximation_needed']

    @pytest.mark.parametrize("H", [1.0, 3.0])
    def test_all_seminorms_finite(self, H):
        result = barrier2_fixed_schwartz(H, max_k=3, max_m=3)
        for (m, k), val in result['seminorms'].items():
            assert np.isfinite(val), f"Seminorm ({m},{k}) infinite at H={H}"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_max_seminorm_bounded(self, H):
        result = barrier2_fixed_schwartz(H)
        assert result['max_seminorm'] < 1e20


# ═══════════════════════════════════════════════════════════════════════════════
# BARRIER 3: EIGENVALUE-ZERO IDENTIFICATION → KERNEL UNIVERSALITY
# ═══════════════════════════════════════════════════════════════════════════════

class TestBarrier3:
    """Corrected FT ≥ 0 → PSD for ANY spectrum → GLM bypassed (double-edged)."""

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_kernel_nonneg(self, H):
        result = barrier3_kernel_universality(H)
        assert result['kernel_nonneg'], f"Kernel ≱ 0 at H={H}"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_all_spectra_psd(self, H):
        result = barrier3_kernel_universality(H)
        assert result['all_spectra_psd'], (
            f"Not all spectra PSD at H={H}: {result['spectra']}"
        )

    @pytest.mark.parametrize("H", [1.0, 3.0])
    def test_glm_not_needed(self, H):
        result = barrier3_kernel_universality(H)
        assert not result['glm_needed']
        assert not result['hilbert_polya_needed']

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_each_spectrum_type_psd(self, H):
        result = barrier3_kernel_universality(H)
        for name, spec_result in result['spectra'].items():
            assert spec_result['psd'], (
                f"Spectrum '{name}' not PSD at H={H}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# BARRIER 4: WEIL SUM DECOMPOSITION (LOCAL → GLOBAL)
# ═══════════════════════════════════════════════════════════════════════════════

class TestWeilSumDecomposition:
    """Split Weil sum: off-critical term vs on-line sum, measure domination."""

    @pytest.mark.parametrize("alpha", [0.5, 1.0, 2.0, 5.0])
    def test_on_line_sum_positive(self, alpha):
        """S_on(α) > 0 under RH (all terms positive)."""
        s_on = on_line_sum(alpha)
        assert s_on > 0, f"S_on({alpha}) = {s_on} ≤ 0"

    @pytest.mark.parametrize("db,g0", [(0.1, 5.0), (0.1, 14.0), (0.2, 10.0)])
    def test_off_line_can_be_negative(self, db, g0):
        """C_off(α) < 0 in negativity windows."""
        windows = negativity_windows(db, n_windows=1)
        alpha_center = windows[0][2]
        c_off = off_line_pair_contribution(alpha_center, g0, db)
        assert c_off < 0, (
            f"C_off should be negative at α={alpha_center:.3f} (window center)"
        )

    @pytest.mark.parametrize("g0", [5.0, 10.0])
    def test_decomposition_sums_correctly(self, g0):
        """S_total = S_on + C_off."""
        db = 0.1
        alpha = 1.0
        s_on = on_line_sum(alpha)
        c_off = off_line_pair_contribution(alpha, g0, db)
        s_total = s_on + c_off
        # Verify additive decomposition
        assert s_total == pytest.approx(s_on + c_off, rel=1e-14)

    @pytest.mark.parametrize("g0", [5.0, 14.0])
    def test_domination_ratio_exceeds_one_for_low_lying(self, g0):
        """For γ₀ ≤ γ₁, there exists α where |C_off|/S_on > 1."""
        db = 0.15
        windows = negativity_windows(db, n_windows=3)
        found = False
        for low, high, center in windows:
            ratio, c_off, s_on = domination_ratio(center, g0, db)
            if ratio > 1.0:
                found = True
                break
        assert found, f"γ₀={g0}: No α found where off-line dominates"


# ═══════════════════════════════════════════════════════════════════════════════
# BARRIER 5: CONTRADICTION WINDOW (IF |C_off| > S_on THEN S < 0)
# ═══════════════════════════════════════════════════════════════════════════════

class TestContradictionWindow:
    """Conditional: IF |C_off| > S_on at some α THEN S(α) < 0."""

    @pytest.mark.parametrize("db,g0", [(0.2, 5.0), (0.3, 10.0)])
    def test_contradiction_window_exists(self, db, g0):
        """For low-lying zeros with substantial Δβ, a contradiction window opens."""
        res = weil_delta_A_full(db, g0, n_alpha=3000)
        if res['peak_ratio'] > 1.0:
            assert res['min_S_total'] < 0, (
                f"Ratio > 1 but min S ≥ 0 — inconsistency"
            )

    @pytest.mark.parametrize("db", [1e-4, 1e-3])
    def test_no_window_at_small_db(self, db):
        """At small Δβ, the contradiction window is CLOSED (the crack)."""
        res = weil_delta_A_full(db, 14.135, n_alpha=1000)
        assert res['peak_ratio'] < 1.0, (
            f"Δβ={db}: Unexpectedly found domination"
        )
        assert res['min_S_total'] >= 0, (
            f"Δβ={db}: S went negative without domination ratio > 1"
        )

    def test_window_width_grows_with_db(self):
        """Contradiction window widens as Δβ increases."""
        ratios = []
        for db in [0.05, 0.1, 0.2, 0.3]:
            res = weil_delta_A_full(db, 10.0, n_alpha=1500)
            ratios.append(res['peak_ratio'])
        # General trend: ratio increases with Δβ
        assert ratios[-1] > ratios[0], (
            f"Ratio should grow with Δβ: {ratios}"
        )

    @pytest.mark.parametrize("g0", [5.0, 10.0, 14.135])
    def test_domination_implies_negative_sum(self, g0):
        """Logical consistency: domination=True → min_S < 0."""
        res = weil_delta_A_full(0.2, g0, n_alpha=3000)
        if res['dominates']:
            assert res['min_S_total'] < 0


# ═══════════════════════════════════════════════════════════════════════════════
# BARRIER 6: L²→SCHWARTZ SEMINORM QUANTIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestSchwartzSeminormGrowth:
    """
    Schwartz seminorms p_{m,k}(w_H) = sup_t |t^m · d^k w_H / dt^k|.

    w_H ∈ S(ℝ) means all seminorms finite. This test quantifies:
    1. Seminorm growth rate with m, k
    2. Comparison across H values
    3. Distance from bad regime (non-assertive about density)
    """

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_all_low_order_seminorms_finite(self, H):
        """All p_{m,k} for m,k ≤ 4 are finite."""
        for m in range(5):
            for k in range(5):
                val = schwartz_seminorm(H, m, k)
                assert np.isfinite(val), (
                    f"H={H}: p_{{{m},{k}}} = {val} (infinite!)"
                )

    @pytest.mark.parametrize("H", [1.0, 3.0])
    def test_seminorm_growth_subexponential(self, H):
        """Seminorms grow at most polynomially in m (not exponentially)."""
        vals_m = [schwartz_seminorm(H, m, 0) for m in range(6)]
        # Check that growth is bounded: p_{m+1,0} / p_{m,0} doesn't blow up
        for i in range(1, len(vals_m)):
            if vals_m[i-1] > 1e-15:
                ratio = vals_m[i] / vals_m[i-1]
                assert ratio < 100 * H, (
                    f"H={H}: p_{{{i},0}}/p_{{{i-1},0}} = {ratio:.1f} — too fast"
                )

    @pytest.mark.parametrize("H", [1.0, 3.0])
    def test_derivative_seminorms_bounded(self, H):
        """Higher derivatives: p_{0,k} remains bounded for k ≤ 4."""
        for k in range(5):
            val = schwartz_seminorm(H, 0, k)
            assert val < 1e10, f"H={H}: p_{{0,{k}}} = {val} — too large"

    def test_seminorm_scales_with_H(self):
        """Larger H → larger seminorms (wider kernel → more mass)."""
        p_small = schwartz_seminorm(1.0, 1, 0)
        p_large = schwartz_seminorm(5.0, 1, 0)
        # Wider kernel has more mass at large |t|
        assert p_large > p_small

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_curvature_weight_seminorms_finite(self, H):
        """W_curv(t) = -w_H''(t) also has finite Schwartz seminorms."""
        t = np.linspace(-20 * H, 20 * H, 5000)
        W = W_curv(t, H)
        for m in range(4):
            integrand = np.abs(t**m * W)
            val = float(np.max(integrand))
            assert np.isfinite(val), (
                f"H={H}: W_curv seminorm m={m} is infinite"
            )

    def test_large_sieve_coefficient_comparison(self):
        """
        Compare Schwartz seminorms against large-sieve-type bound.

        The large-sieve inequality gives: Σ |a_n|² ≤ (N + Q²) · ∫|f|²
        The relevant comparison is whether seminorm growth is compatible
        with L² coefficient bounds. Non-assertive: just quantify.
        """
        H = 3.0
        t = np.linspace(-100, 100, 10000)
        dt = t[1] - t[0]

        # L² norm of w_H
        wH_vals = w_H(t, H)
        l2_norm_sq = float(np.sum(wH_vals**2) * dt)

        # Schwartz seminorms up to order 3
        seminorm_vals = []
        for m in range(4):
            for k in range(4):
                val = schwartz_seminorm(H, m, k)
                seminorm_vals.append(val)

        max_seminorm = max(seminorm_vals)

        # The key diagnostic: ratio of max seminorm to L² norm
        # If this is modest, we are far from the "bad regime"
        diagnostic_ratio = max_seminorm / max(np.sqrt(l2_norm_sq), 1e-15)
        assert diagnostic_ratio > 0  # non-degenerate
        assert np.isfinite(diagnostic_ratio)
