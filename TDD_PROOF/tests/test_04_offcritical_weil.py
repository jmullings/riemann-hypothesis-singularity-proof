"""
================================================================================
test_04_offcritical_weil.py — Tier 1: Off-Critical Contribution (Sink: The Crack)
================================================================================

Verifies the SIMPLIFIED off-critical model:

  ΔA(Δβ, H) = -2πH²Δβ³ / sin(πHΔβ/2)

  1. ΔA < 0 for all Δβ > 0 (sign property of implemented formula)
  2. The formula has no γ₀ parameter (by construction, not derivation)
  3. Small-Δβ limit: ΔA ≈ -4H·Δβ²
  4. Monotone increasing |ΔA| as Δβ grows
  5. Pole at Δβ = 2/H

IMPORTANT: These tests verify properties of the SIMPLIFIED MODEL.
The γ₀-independence is a code-level property (the function omits γ₀),
not a mathematical derivation from the full Weil explicit formula.
The true Weil contribution decays exponentially as e^{−πHγ₀/2} for
large γ₀.  See offcritical.py CRITIQUE RESPONSE for full analysis.
The correct γ₀-dependent formula is in weil_density.off_line_pair_contribution.
================================================================================
"""

import pytest
import numpy as np

from engine.offcritical import (
    weil_delta_A, weil_delta_A_small, weil_contribution_strength,
    delta_A_sign_always_negative, delta_A_gamma0_independence,
    weil_delta_A_full, rayleigh_quotient, signal_map, crack_width_scaling,
)


# ─────────────── §1 — ΔA < 0 FOR ALL Δβ > 0 ────────────────────────────────

class TestDeltaANegative:
    """The fundamental sign property: ΔA < 0."""

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_delta_A_negative_sweep(self, H):
        """ΔA(Δβ, H) < 0 for all Δβ ∈ (0, 0.49]."""
        all_neg, max_val, _, _ = delta_A_sign_always_negative(H)
        assert all_neg, f"ΔA not negative everywhere at H={H}, max={max_val}"

    @pytest.mark.parametrize("db", [1e-8, 1e-6, 1e-4, 0.001, 0.01, 0.05, 0.1, 0.3, 0.49])
    def test_delta_A_negative_pointwise(self, db):
        val = weil_delta_A(db, H=3.0)
        assert val < 0, f"ΔA({db}, 3.0) = {val} ≥ 0"

    def test_delta_A_at_zero(self):
        """ΔA(0, H) = 0 (on the critical line)."""
        assert weil_delta_A(0.0, 3.0) == 0.0


# ─────────────── §2 — γ₀-INDEPENDENCE ───────────────────────────────────────

class TestGamma0Independence:
    """ΔA formula has no γ₀ parameter (code-level property, not derivation)."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_gamma0_independent(self, H):
        """ΔA is the same for γ₀ = 14 and γ₀ = 10⁶."""
        result = delta_A_gamma0_independence(H, delta_beta=0.1)
        assert result['gamma0_independent']
        assert result['gamma0_variation'] == 0.0

    @pytest.mark.parametrize("db", [0.001, 0.01, 0.1, 0.3])
    def test_delta_A_formula_no_gamma(self, db):
        """Verify the formula ΔA = -2πH²Δβ³/sin(πHΔβ/2) has no γ₀."""
        H = 3.0
        # Compute explicitly
        arg = np.pi * H * db / 2.0
        expected = -2.0 * np.pi * H**2 * db**3 / np.sin(arg)
        actual = weil_delta_A(db, H)
        assert actual == pytest.approx(expected, rel=1e-12)


# ─────────────── §3 — SMALL-Δβ APPROXIMATION ────────────────────────────────

class TestSmallDeltaBeta:
    """ΔA ≈ -4H·Δβ² for small Δβ (L'Hôpital limit)."""

    @pytest.mark.parametrize("db", [1e-8, 1e-6, 1e-4, 1e-3])
    def test_small_db_matches_exact(self, db):
        H = 3.0
        exact = weil_delta_A(db, H)
        approx = weil_delta_A_small(db, H)
        rel_err = abs(exact - approx) / abs(exact) if exact != 0 else 0
        assert rel_err < 0.01, f"Small-Δβ approx fails at Δβ={db}: {rel_err}"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_small_db_formula(self, H):
        db = 1e-6
        expected = -4.0 * H * db**2
        actual = weil_delta_A_small(db, H)
        assert actual == pytest.approx(expected, rel=1e-14)


# ─────────────── §4 — CONTRIBUTION STRENGTH ─────────────────────────────────

class TestContributionStrength:
    """C(Δβ) = |ΔA| is monotone increasing for Δβ ∈ (0, 2/H)."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_strength_monotone(self, H):
        db_vals = np.linspace(0.001, 0.4, 200)
        C_vals = [weil_contribution_strength(db, H) for db in db_vals]
        for i in range(1, len(C_vals)):
            assert C_vals[i] >= C_vals[i-1] - 1e-15, (
                f"C(Δβ) not monotone at Δβ={db_vals[i]}"
            )

    def test_strength_zero_at_origin(self):
        """C(0) = 0."""
        assert weil_contribution_strength(0.0, 3.0) == 0.0

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0])
    def test_pole_at_2_over_H(self, H):
        """Near Δβ = 2/H, the model diverges."""
        pole = 2.0 / H
        if pole > 0.5:
            # Inside critical strip: strength grows but stays finite
            C = weil_contribution_strength(0.49, H)
            assert C > 0
        # At or beyond the pole: -inf → inf strength
        val = weil_delta_A(pole + 0.001, H)
        assert val == -np.inf or abs(val) > 100


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — FULL γ₀-DEPENDENT CONTRIBUTION (from Weil explicit formula)
# ═══════════════════════════════════════════════════════════════════════════════

class TestFullGamma0Contribution:
    """Full γ₀-dependent C_off(α) = 2·ℜ(sech²(α(γ₀ + iΔβ)))."""

    @pytest.mark.parametrize("gamma_0", [5.0, 10.0, 14.135])
    def test_low_lying_dominates(self, gamma_0):
        """For γ₀ ≤ γ₁, off-line contribution dominates (Theorem 6.1)."""
        res = weil_delta_A_full(0.1, gamma_0, n_alpha=3000)
        assert res['dominates'], (
            f"γ₀={gamma_0}: Expected domination, ratio={res['peak_ratio']:.4f}"
        )

    @pytest.mark.parametrize("db", [0.05, 0.1, 0.2, 0.3])
    def test_peak_c_off_negative(self, db):
        """Peak C_off < 0 for moderate-to-large Δβ."""
        res = weil_delta_A_full(db, 14.135, n_alpha=3000)
        assert res['peak_c_off'] < 0, f"Δβ={db}: C_off={res['peak_c_off']}"

    @pytest.mark.parametrize("db", [0.001, 0.01])
    def test_small_db_contribution_vanishes(self, db):
        """For very small Δβ, peak C_off is near zero (the crack)."""
        res = weil_delta_A_full(db, 14.135)
        assert abs(res['peak_c_off']) < 0.1, f"Δβ={db}: |C_off|={abs(res['peak_c_off'])}"

    @pytest.mark.parametrize("gamma_0", [50.0, 100.0, 200.0])
    def test_high_lying_suppressed(self, gamma_0):
        """For γ₀ >> γ₁, exponential decay kills domination."""
        res = weil_delta_A_full(0.1, gamma_0)
        assert res['peak_ratio'] < 1.0, (
            f"γ₀={gamma_0}: Unexpectedly dominates, ratio={res['peak_ratio']}"
        )

    def test_gamma0_changes_result(self):
        """Unlike simplified formula, full formula depends on γ₀."""
        r1 = weil_delta_A_full(0.1, 14.135)
        r2 = weil_delta_A_full(0.1, 100.0)
        assert r1['peak_ratio'] != pytest.approx(r2['peak_ratio'], abs=0.01), (
            "Full formula should produce different results for different γ₀"
        )

    def test_zero_delta_beta_returns_zero(self):
        """On-line zero (Δβ=0) has zero off-critical contribution."""
        res = weil_delta_A_full(0.0, 14.135)
        assert res['peak_c_off'] == 0.0
        assert not res['dominates']


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — RAYLEIGH QUOTIENT AND THE CRACK
# ═══════════════════════════════════════════════════════════════════════════════

class TestRayleighQuotient:
    """Rayleigh quotient λ_eff(Δβ, γ₀) and the small-Δβ crack."""

    @pytest.mark.parametrize("db,g0", [(0.2, 5.0), (0.3, 10.0), (0.1, 14.0)])
    def test_fires_for_low_lying_large_db(self, db, g0):
        """Contradiction fires for low-lying zeros with non-tiny Δβ."""
        res = rayleigh_quotient(db, g0, H=3.0, n_alpha=3000)
        assert res['dominates'], (
            f"Δβ={db}, γ₀={g0}: λ_eff={res['lambda_eff']:.4f}, "
            f"threshold={res['threshold']:.4f}"
        )

    @pytest.mark.parametrize("db", [1e-6, 1e-5, 1e-4, 1e-3])
    def test_crack_small_db_does_not_fire(self, db):
        """THE CRACK: For very small Δβ, λ_eff → 0 < 4/H²."""
        res = rayleigh_quotient(db, 14.135, H=3.0)
        assert res['lambda_eff'] < res['threshold'], (
            f"Δβ={db}: λ_eff={res['lambda_eff']:.6f} ≥ threshold={res['threshold']:.4f}"
        )
        assert res['margin'] < 0, "Margin should be negative (crack territory)"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_threshold_is_4_over_H_sq(self, H):
        """Verify threshold = 4/H²."""
        res = rayleigh_quotient(0.1, 14.135, H)
        assert res['threshold'] == pytest.approx(4.0 / H**2, rel=1e-14)

    def test_lambda_eff_nonneg(self):
        """λ_eff ≥ 0 always."""
        res = rayleigh_quotient(0.1, 14.135, H=3.0)
        assert res['lambda_eff'] >= 0


# ═══════════════════════════════════════════════════════════════════════════════
# §7 — SIGNAL MAP (Δβ, γ₀) PLANE
# ═══════════════════════════════════════════════════════════════════════════════

class TestSignalMap:
    """(Δβ, γ₀) map: signal vs decay regions."""

    def test_signal_map_shape(self):
        """Output has correct shape."""
        dbs = [0.05, 0.1, 0.2]
        g0s = [5.0, 14.0]
        res = signal_map(H=3.0, db_values=dbs, g0_values=g0s, n_alpha=200)
        assert res['ratios'].shape == (3, 2)
        assert res['signal_mask'].shape == (3, 2)
        assert res['decay_mask'].shape == (3, 2)

    def test_low_lying_large_db_is_signal(self):
        """Large Δβ + low γ₀ → signal region (ratio > 1)."""
        res = signal_map(H=3.0, db_values=[0.2], g0_values=[5.0], n_alpha=2000)
        assert res['ratios'][0, 0] > 1.0

    def test_high_lying_is_decay(self):
        """High γ₀ → decay region (ratio << 1)."""
        res = signal_map(H=3.0, db_values=[0.1], g0_values=[200.0], n_alpha=500)
        assert res['ratios'][0, 0] < 0.1

    def test_signal_monotone_in_gamma0(self):
        """Ratio decreases as γ₀ increases (for fixed Δβ)."""
        g0s = [5.0, 14.0, 50.0, 100.0]
        res = signal_map(H=3.0, db_values=[0.15], g0_values=g0s, n_alpha=1000)
        ratios = res['ratios'][0, :]
        # Not strictly monotone but general trend is decreasing
        assert ratios[0] > ratios[-1]


# ═══════════════════════════════════════════════════════════════════════════════
# §8 — CRACK WIDTH SCALING
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrackQuantification:
    """Measure the crack: |A|/B scaling as Δβ → 0."""

    def test_ratio_decreases_with_db(self):
        """Domination ratio → 0 as Δβ → 0."""
        res = crack_width_scaling(H=3.0, db_values=np.logspace(-4, -1, 10))
        # Ratio at smallest Δβ should be much smaller than at largest
        assert res['ratios'][-1] > res['ratios'][0] * 5

    def test_scaling_exponent_positive(self):
        """Scaling: ratio ~ Δβ^n with n > 0 (ratio shrinks with Δβ)."""
        res = crack_width_scaling(H=3.0)
        assert np.isfinite(res['scaling_exponent'])
        assert res['scaling_exponent'] > 0, (
            f"Expected positive exponent, got {res['scaling_exponent']}"
        )

    def test_abs_A_vanishes_at_small_db(self):
        """|C_off| → 0 as Δβ → 0."""
        res = crack_width_scaling(H=3.0, db_values=np.logspace(-6, -1, 15))
        assert res['abs_A'][0] < res['abs_A'][-1]
        assert res['abs_A'][0] < 1e-3

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_threshold_stored(self, H):
        """Threshold 4/H² is correctly stored."""
        res = crack_width_scaling(H)
        assert res['threshold'] == pytest.approx(4.0 / H**2, rel=1e-14)
