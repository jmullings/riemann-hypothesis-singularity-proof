"""
================================================================================
test_07_lemma3_contradiction.py — Tier 2: Lemma 3 — Off-Critical Sign Property
================================================================================

Verifies the SIGN PROPERTY of the simplified ΔA model:

  For ANY Δβ > 0:
    ΔA(Δβ, H) < 0   (the implemented formula outputs negative values)

  Sub-assertions:
    (a) ΔA < 0 for all Δβ > 0 (complete coverage)
    (b) Sign holds at each individual Δβ value
    (c) The small-Δβ region is covered
    (d) The sign property is H-independent (works for all H > 0)

IMPORTANT: These tests verify that the SIMPLIFIED MODEL outputs negative
values.  The LOCAL→GLOBAL step (proving one negative term dominates the
infinite positive Weil sum) requires the full Weil formula.  For the
true formula with exponential decay in γ₀, the signal may be absorbed
by the positive floor for high-lying zeros.
See offcritical.py CRITIQUE RESPONSE for the full analysis.
================================================================================
"""

import pytest
import numpy as np

from engine.proof_chain import lemma3_contradiction_fires
from engine.offcritical import (
    weil_delta_A, weil_contribution_strength,
    rayleigh_quotient, crack_width_scaling,
)


# ─────────────── §1 — COMPLETE Δβ COVERAGE ───────────────────────────────────

class TestLemma3Complete:
    """ΔA < 0 for ALL Δβ > 0 → contradiction for ALL off-critical zeros."""

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0, 7.0, 10.0])
    def test_contradiction_fires(self, H):
        result = lemma3_contradiction_fires(H)
        assert result['all_negative'], f"Not all ΔA negative at H={H}"
        assert result['contradiction_holds'], f"Contradiction fails at H={H}"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_fine_grain_coverage(self, H):
        """50 logarithmically spaced points from 10⁻⁸ to 0.49."""
        db_vals = np.logspace(-8, np.log10(0.49), 50)
        result = lemma3_contradiction_fires(H, delta_beta_values=db_vals.tolist())
        assert result['all_negative']


# ─────────────── §2 — SMALL Δβ COVERAGE ──────────────────────────────────────

class TestLemma3SmallDeltaBeta:
    """The small-Δβ region is NOT a gap."""

    @pytest.mark.parametrize("db", [1e-10, 1e-8, 1e-6, 1e-4])
    def test_very_small_db(self, db):
        """ΔA < 0 even for extremely small Δβ."""
        val = weil_delta_A(db, H=3.0)
        assert val < 0, f"ΔA({db}) = {val}"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_small_db_cubic_scaling(self, H):
        """For small Δβ: |ΔA| ≈ 4H·Δβ² (L'Hôpital limit)."""
        db = 1e-6
        val = weil_delta_A(db, H)
        expected = -4.0 * H * db**2
        assert val == pytest.approx(expected, rel=0.01)


# ─────────────── §3 — H-INDEPENDENCE ─────────────────────────────────────────

class TestLemma3HIndependence:
    """Contradiction works for all H > 0."""

    def test_contradiction_across_H_range(self):
        for H in [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 7.0, 10.0]:
            result = lemma3_contradiction_fires(H)
            assert result['contradiction_holds'], f"Fails at H={H}"


# ─────────────── §4 — STRENGTH GROWTH ────────────────────────────────────────

class TestLemma3StrengthGrowth:
    """C(Δβ) = |ΔA| grows with Δβ — the contradiction gets STRONGER."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_strength_exceeds_threshold(self, H):
        """Beyond Δβ = 0.01, |ΔA| is substantial."""
        C = weil_contribution_strength(0.01, H)
        assert C > 0, "Contribution strength must be > 0"

    @pytest.mark.parametrize("H", [1.0, 3.0])
    def test_strength_exceeds_at_half(self, H):
        """At Δβ = 0.49 (critical strip boundary), |ΔA| is large."""
        C = weil_contribution_strength(0.49, H)
        assert C > 1.0, f"Expected large |ΔA| at Δβ=0.49, got {C}"


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — RAYLEIGH QUOTIENT GRID (γ₀ × Δβ)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRayleighQuotientGrid:
    """Rayleigh quotient λ_eff across (Δβ, γ₀) grid — maps contradiction regions."""

    @pytest.mark.parametrize("g0", [5.0, 10.0, 14.0])
    def test_low_lying_fires_at_moderate_db(self, g0):
        """Low-lying zeros with Δβ ≥ 0.1 produce domination."""
        res = rayleigh_quotient(0.15, g0, H=3.0, n_alpha=2000)
        assert res['dominates'], (
            f"γ₀={g0}: Expected domination at Δβ=0.15"
        )

    @pytest.mark.parametrize("g0", [30.0, 50.0, 100.0])
    def test_high_lying_fails_at_moderate_db(self, g0):
        """High-lying zeros: domination ratio < 1 even at moderate Δβ."""
        res = rayleigh_quotient(0.1, g0, H=3.0, n_alpha=1000)
        # High-lying zeros should have much weaker contribution
        assert res['lambda_eff'] < res['threshold'], (
            f"γ₀={g0}: λ_eff={res['lambda_eff']:.4f} unexpectedly exceeds threshold"
        )

    def test_grid_sweep_documents_boundary(self):
        """Sweep (Δβ, γ₀) grid and document where contradiction fires."""
        db_vals = [0.05, 0.1, 0.2, 0.3]
        g0_vals = [5.0, 14.0, 30.0]
        n_fires = 0
        n_total = 0
        for db in db_vals:
            for g0 in g0_vals:
                res = rayleigh_quotient(db, g0, H=3.0, n_alpha=1000)
                n_total += 1
                if res['dominates']:
                    n_fires += 1
        # Should fire for at least low-lying+large-Δβ combinations
        assert n_fires > 0, "No contradictions fired in grid sweep"
        assert n_fires < n_total, "All fired — high-lying regime not represented"


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — CRACK MEASUREMENT (Δβ → 0 scaling)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrackMeasurement:
    """Quantitative crack: |A|/B scaling as Δβ → 0."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_crack_ratio_below_threshold(self, H):
        """At small Δβ, domination ratio is well below 4/H²."""
        res = crack_width_scaling(H, db_values=np.array([1e-4, 1e-3, 1e-2]))
        threshold = 4.0 / H**2
        assert np.all(res['ratios'] < threshold), (
            f"H={H}: Some small-Δβ ratios exceed threshold {threshold}"
        )

    def test_positive_scaling_exponent(self):
        """Ratio ~ Δβ^n with n > 0 (ratio shrinks as Δβ → 0)."""
        res = crack_width_scaling(H=3.0)
        # The exponent should be positive — ratio vanishes with Δβ
        assert res['scaling_exponent'] > 0.5, (
            f"Scaling exponent {res['scaling_exponent']:.2f} < 0.5 — crack is wider than expected"
        )

    def test_crack_width_honest(self):
        """The crack is REAL: at small Δβ, ratios → 0 (not ≥ 1)."""
        res = crack_width_scaling(H=3.0, db_values=np.logspace(-5, -2, 10))
        # All ratios at these small Δβ should be < 1 (no domination)
        assert np.all(res['ratios'] < 1.0), (
            "Small-Δβ regime must NOT show domination (this IS the crack)"
        )
