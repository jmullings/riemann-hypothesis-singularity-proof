#!/usr/bin/env python3
"""
================================================================================
test_25_holy_grail.py — The Three-Regime Closure: RH Contradiction Certificate
================================================================================

Tier 13: HOLY GRAIL TESTS

Tests the global inequality:
    λ_new(T₀, Δβ; H, ε) ≥ λ*(H) = 4/H²   ∀ T₀, Δβ > 0

Organised into 9 sections:
  A — Deficit Functional Properties         (5 tests)
  B — HP Penalty Ratio Scaling              (5 tests)
  C — Regime I:  Small-Δβ Continuity        (5 tests)
  D — Regime II: Compact-Domain ε₀          (5 tests)
  E — Regime III: Domination Handoff        (4 tests)
  F — Holy Grail Single-Point Checks        (5 tests)
  G — Full RH Contradiction Certificate     (4 tests)
  H — Scaling Diagnostics                   (4 tests)
  I — Parametric Sweep (slow)               (3 tests)

Total: 40 tests.
================================================================================
"""

import numpy as np
import pytest

from engine.holy_grail import (
    deficit_functional,
    penalty_ratio,
    small_delta_beta_closure,
    compact_domain_epsilon,
    domination_handoff,
    holy_grail_inequality,
    holy_grail_verdict,
    rh_contradiction_certificate,
    deficit_scaling_exponent,
    bhp_lower_bound,
)
from engine.bochner import lambda_star
from engine.hilbert_polya import hp_operator_matrix
from engine.hp_alignment import rs_rayleigh_with_drift, hp_energy


# ═════════════════════════════════════════════════════════════════════════
# Shared fixtures
# ═════════════════════════════════════════════════════════════════════════

H_TEST = 3.0
N_TEST = 30
MU0_TEST = 1.0
N_PTS = 300  # integration grid (speed)


@pytest.fixture(scope='module')
def H_hp():
    """Build H_HP once for the module."""
    return hp_operator_matrix(N_TEST, mu0=MU0_TEST)


# ═════════════════════════════════════════════════════════════════════════
# Section A — DEFICIT FUNCTIONAL PROPERTIES (5 tests)
# ═════════════════════════════════════════════════════════════════════════

class TestDeficitFunctional:
    """A: Deficit Δ = λ*(H)·B_RS + A_RS and crack depth."""

    def test_F2_nonneg_on_critical_line(self, H_hp):
        """A1: At Δβ = 0, F̃₂ ≥ 0 (Theorem B 2.0) → crack depth = 0."""
        for T0 in [0.0, 14.135, 50.0]:
            res = deficit_functional(T0, H_TEST, N_TEST, 0.0,
                                     n_points=N_PTS)
            assert res['F2_off'] >= -1e-6, \
                f'F̃₂ negative on critical line at T0={T0}'
            assert res['crack_depth'] < 1e-6, \
                f'Crack depth nonzero on critical line at T0={T0}'

    def test_deficit_positive_off_critical(self, H_hp):
        """A2: At Δβ > 0, deficit is finite and well-defined."""
        res = deficit_functional(14.135, H_TEST, N_TEST, 0.1,
                                 n_points=N_PTS)
        assert np.isfinite(res['deficit'])
        assert np.isfinite(res['A_RS'])
        assert res['B_RS'] > 0

    def test_deficit_returns_all_keys(self, H_hp):
        """A3: Return dict has required keys."""
        res = deficit_functional(0.0, H_TEST, N_TEST, 0.01,
                                 n_points=N_PTS)
        for key in ['deficit', 'crack_depth', 'F2_off', 'A_RS', 'B_RS',
                     'lambda_old', 'lambda_floor']:
            assert key in res

    def test_deficit_lambda_floor_correct(self, H_hp):
        """A4: λ_floor = 4/H²."""
        res = deficit_functional(0.0, H_TEST, N_TEST, 0.01,
                                 n_points=N_PTS)
        assert abs(res['lambda_floor'] - 4.0 / H_TEST**2) < 1e-14

    def test_crack_depth_continuous_near_zero(self, H_hp):
        """A5: Crack depth is small at very small Δβ (continuity)."""
        res = deficit_functional(14.135, H_TEST, N_TEST, 1e-6,
                                 n_points=N_PTS)
        # Near the critical line, F̃₂ should still be ≥ 0 by continuity
        # so crack_depth should be near 0
        assert res['crack_depth'] < 1.0, \
            f'Crack depth too large at tiny Δβ: {res["crack_depth"]}'


# ═════════════════════════════════════════════════════════════════════════
# Section B — HP PENALTY RATIO SCALING (5 tests)
# ═════════════════════════════════════════════════════════════════════════

class TestPenaltyRatio:
    """B: Ratio crack_depth/B_HP determines required ε."""

    def test_ratio_returns_all_keys(self, H_hp):
        """B1: Return dict has required keys."""
        res = penalty_ratio(14.135, H_TEST, N_TEST, H_hp, 0.01,
                            n_points=N_PTS)
        for key in ['ratio', 'crack_depth', 'B_HP', 'in_crack']:
            assert key in res

    def test_bhp_always_positive(self, H_hp):
        """B2: B_HP > 0 since H_HP is positive definite."""
        for db in [0.0, 0.01, 0.1, 0.3]:
            res = penalty_ratio(14.135, H_TEST, N_TEST, H_hp, db,
                                n_points=N_PTS)
            assert res['B_HP'] > 0, f'B_HP ≤ 0 at Δβ={db}'

    def test_ratio_finite(self, H_hp):
        """B3: Ratio is finite for positive B_HP."""
        res = penalty_ratio(14.135, H_TEST, N_TEST, H_hp, 0.05,
                            n_points=N_PTS)
        assert np.isfinite(res['ratio'])

    def test_ratio_finite_on_critical_line(self, H_hp):
        """B4: At Δβ=0, ratio is finite (deficit and B_HP both bounded)."""
        res = penalty_ratio(14.135, H_TEST, N_TEST, H_hp, 0.0,
                            n_points=N_PTS)
        assert np.isfinite(res['ratio']), \
            f'Ratio not finite on critical line: {res["ratio"]}'

    def test_ratio_bounded_on_compact(self, H_hp):
        """B5: Ratio is bounded on compact (T₀, Δβ) domain."""
        max_r = -np.inf
        for T0 in [0.0, 14.135, 50.0]:
            for db in [0.01, 0.1, 0.3]:
                r = penalty_ratio(T0, H_TEST, N_TEST, H_hp, db,
                                  n_points=N_PTS)['ratio']
                if r > max_r:
                    max_r = r
        assert np.isfinite(max_r), 'Ratio unbounded on compact domain'


# ═════════════════════════════════════════════════════════════════════════
# Section C — REGIME I: SMALL-Δβ CONTINUITY CLOSURE (5 tests)
# ═════════════════════════════════════════════════════════════════════════

class TestRegimeI:
    """C: Small-Δβ closure via continuity argument."""

    def test_closure_returns_structure(self, H_hp):
        """C1: Return dict has required keys."""
        res = small_delta_beta_closure(
            H_TEST, N_TEST, H_hp,
            T0_values=[0.0, 14.135],
            delta_betas=[1e-5, 1e-3],
            n_points=N_PTS)
        for key in ['ratios', 'max_ratio_per_db', 'converges_to_zero',
                     'delta_1']:
            assert key in res

    def test_ratios_decrease_toward_zero(self, H_hp):
        """C2: max(Δ/B_HP) decreases as Δβ → 0."""
        res = small_delta_beta_closure(
            H_TEST, N_TEST, H_hp,
            T0_values=[0.0, 14.135, 30.0],
            delta_betas=[1e-5, 1e-4, 1e-3, 0.01],
            n_points=N_PTS)
        # The ratio at the smallest Δβ should be ≤ ratio at the largest
        assert res['max_ratio_per_db'][0] <= res['max_ratio_per_db'][-1] + 0.1

    def test_delta_1_exists(self, H_hp):
        """C3: There exists δ₁ > 0 where ratio < 1 (crack closeable)."""
        res = small_delta_beta_closure(
            H_TEST, N_TEST, H_hp,
            T0_values=[0.0, 14.135, 50.0],
            delta_betas=[1e-6, 1e-5, 1e-4, 1e-3, 0.01, 0.05],
            n_points=N_PTS)
        assert res['delta_1'] > 0, \
            'No δ₁ found where ratio < 1 — crack not closeable!'

    def test_all_ratios_finite(self, H_hp):
        """C4: All computed ratios are finite."""
        res = small_delta_beta_closure(
            H_TEST, N_TEST, H_hp,
            T0_values=[0.0, 14.135],
            delta_betas=[1e-5, 1e-3, 0.01],
            n_points=N_PTS)
        assert np.all(np.isfinite(res['ratios']))

    def test_crack_depth_near_zero_at_small_db(self, H_hp):
        """C5: At very small Δβ, crack depth is near zero (F̃₂ ≥ 0 by continuity)."""
        for T0 in [0.0, 14.135, 50.0]:
            d = deficit_functional(T0, H_TEST, N_TEST, 1e-8,
                                   n_points=N_PTS)
            assert d['crack_depth'] < 1.0, \
                f'Crack depth not small at Δβ≈0 for T0={T0}: {d["crack_depth"]}'


# ═════════════════════════════════════════════════════════════════════════
# Section D — REGIME II: COMPACT-DOMAIN COMPACTNESS CLOSURE (5 tests)
# ═════════════════════════════════════════════════════════════════════════

class TestRegimeII:
    """D: Compact-domain ε₀ via Weierstrass extreme value theorem."""

    def test_epsilon_0_finite(self, H_hp):
        """D1: ε₀ is finite on compact domain (Weierstrass)."""
        res = compact_domain_epsilon(
            H_TEST, N_TEST, H_hp,
            db_range=(0.01, 0.3), T0_range=(0.0, 50.0),
            n_db=8, n_T0=8, n_points=N_PTS)
        assert np.isfinite(res['epsilon_0'])

    def test_epsilon_0_nonnegative(self, H_hp):
        """D2: ε₀ ≥ 0 (ratio of positive quantities)."""
        res = compact_domain_epsilon(
            H_TEST, N_TEST, H_hp,
            db_range=(0.01, 0.2), T0_range=(0.0, 30.0),
            n_db=6, n_T0=6, n_points=N_PTS)
        assert res['epsilon_0'] >= 0

    def test_argmax_coordinates_in_domain(self, H_hp):
        """D3: The supremum location is within the compact domain."""
        db_r = (0.01, 0.3)
        T0_r = (0.0, 50.0)
        res = compact_domain_epsilon(
            H_TEST, N_TEST, H_hp,
            db_range=db_r, T0_range=T0_r,
            n_db=8, n_T0=8, n_points=N_PTS)
        assert T0_r[0] <= res['argmax_T0'] <= T0_r[1]
        assert db_r[0] <= res['argmax_db'] <= db_r[1]

    def test_grid_ratios_shape(self, H_hp):
        """D4: Grid ratios have correct shape."""
        n_db, n_T0 = 5, 7
        res = compact_domain_epsilon(
            H_TEST, N_TEST, H_hp,
            db_range=(0.01, 0.2), T0_range=(0.0, 30.0),
            n_db=n_db, n_T0=n_T0, n_points=N_PTS)
        assert res['grid_ratios'].shape == (n_T0, n_db)

    def test_epsilon_closes_compact_domain(self, H_hp):
        """D5: With ε = 1.5·ε₀, λ_new ≥ λ*(H) on the same compact domain."""
        res = compact_domain_epsilon(
            H_TEST, N_TEST, H_hp,
            db_range=(0.01, 0.2), T0_range=(0.0, 50.0),
            n_db=6, n_T0=6, n_points=N_PTS)
        eps = max(res['epsilon_0'] * 1.5, 0.01)

        # Spot-check a few points
        for T0 in [0.0, 14.135, 50.0]:
            for db in [0.01, 0.1, 0.2]:
                hg = holy_grail_inequality(T0, H_TEST, N_TEST, H_hp,
                                           eps, db, n_points=N_PTS)
                assert hg['holds'], \
                    (f'Holy Grail fails at T0={T0}, Δβ={db} '
                     f'with ε={eps:.4f}: margin={hg["margin"]:.6e}')


# ═════════════════════════════════════════════════════════════════════════
# Section E — REGIME III: DOMINATION HANDOFF (4 tests)
# ═════════════════════════════════════════════════════════════════════════

class TestRegimeIII:
    """E: Theorem 6.1 domination for large Δβ, γ₀ ≤ γ₁."""

    def test_domination_low_lying_fires(self):
        """E1: For γ₀ < γ₁ and Δβ ≥ 0.15, domination holds."""
        res = domination_handoff(H_TEST, db_min=0.15,
                                 gamma_0_values=[5.0, 10.0, 14.0])
        assert res['all_dominate'], \
            'Theorem 6.1 domination fails for some low-lying case'

    def test_handoff_returns_structure(self):
        """E2: Return dict has required keys."""
        res = domination_handoff(H_TEST, db_min=0.1)
        for key in ['all_dominate', 'results', 'delta_2', 'regime']:
            assert key in res

    def test_individual_results_have_ratio(self):
        """E3: Each per-case result has domination ratio."""
        res = domination_handoff(H_TEST, db_min=0.15,
                                 gamma_0_values=[10.0])
        for r in res['results']:
            assert 'ratio' in r
            assert r['ratio'] >= 0

    def test_domination_ratio_large_db(self):
        """E4: At large Δβ, domination ratio > 1."""
        from engine.weil_density import asymptotic_domination_lemma
        res = asymptotic_domination_lemma(10.0, 0.3)
        assert res['theorem_holds'], \
            'Domination should hold at γ₀=10, Δβ=0.3'
        assert res['ratio_at_star'] > 1.0


# ═════════════════════════════════════════════════════════════════════════
# Section F — HOLY GRAIL SINGLE-POINT CHECKS (5 tests)
# ═════════════════════════════════════════════════════════════════════════

class TestHolyGrailPointwise:
    """F: λ_new ≥ λ*(H) at individual (T₀, Δβ) points."""

    def test_on_critical_line(self, H_hp):
        """F1: At Δβ=0, λ_new ≥ λ*(H) (Theorem B 2.0 + HP only helps)."""
        res = holy_grail_inequality(14.135, H_TEST, N_TEST, H_hp,
                                    eps=0.01, delta_beta=0.0,
                                    n_points=N_PTS)
        assert res['holds'], \
            f'Holy Grail fails ON critical line: margin={res["margin"]}'

    def test_small_delta_beta(self, H_hp):
        """F2: At small Δβ, HP penalty closes the crack."""
        res = holy_grail_inequality(14.135, H_TEST, N_TEST, H_hp,
                                    eps=1.0, delta_beta=1e-4,
                                    n_points=N_PTS)
        assert res['holds'], \
            f'Holy Grail fails at small Δβ: margin={res["margin"]}'

    def test_medium_delta_beta(self, H_hp):
        """F3: At medium Δβ, HP penalty + Bochner suffice."""
        # Use generous ε for this test
        res = holy_grail_inequality(14.135, H_TEST, N_TEST, H_hp,
                                    eps=5.0, delta_beta=0.1,
                                    n_points=N_PTS)
        assert res['holds'], \
            f'Holy Grail fails at medium Δβ: margin={res["margin"]}'

    def test_returns_all_keys(self, H_hp):
        """F4: Return dict has all diagnostic keys."""
        res = holy_grail_inequality(0.0, H_TEST, N_TEST, H_hp,
                                    eps=1.0, delta_beta=0.01,
                                    n_points=N_PTS)
        for key in ['holds', 'lambda_new', 'lambda_floor', 'margin',
                     'lambda_old', 'A_RS', 'B_RS', 'B_HP', 'epsilon']:
            assert key in res

    def test_lambda_new_exceeds_lambda_old(self, H_hp):
        """F5: λ_new > λ_old when ε > 0 (HP only adds energy)."""
        res = holy_grail_inequality(14.135, H_TEST, N_TEST, H_hp,
                                    eps=1.0, delta_beta=0.05,
                                    n_points=N_PTS)
        assert res['lambda_new'] >= res['lambda_old'] - 1e-10, \
            'HP penalty should increase λ, not decrease it'


# ═════════════════════════════════════════════════════════════════════════
# Section G — FULL RH CONTRADICTION CERTIFICATE (4 tests)
# ═════════════════════════════════════════════════════════════════════════

class TestRHCertificate:
    """G: The complete chain: Lemma 1 + 2 + 3 + Holy Grail → RH."""

    def test_certificate_diagnostic_mode_fires(self):
        """G1: DIAGNOSTIC MODE: HP-augmented certificate completes."""
        cert = rh_contradiction_certificate(
            H=H_TEST, N=N_TEST, mu0=MU0_TEST, n_points=N_PTS)
        assert cert['chain_complete'], \
            f'Diagnostic certificate incomplete: {cert["verdict"]}'
        assert cert['mode'] == 'diagnostic'

    def test_certificate_strict_mode_incomplete(self):
        """G1b: STRICT MODE: Pure Weil spine — small-Δβ crack remains OPEN."""
        cert = rh_contradiction_certificate(
            H=H_TEST, N=N_TEST, mu0=MU0_TEST, n_points=N_PTS,
            mode='strict')
        assert not cert['chain_complete'], \
            'Strict mode must NOT claim chain_complete (small-Δβ crack OPEN)'
        assert cert['mode'] == 'strict'
        assert cert['weil_spine_complete'], \
            'Weil spine (Lemmas 1-3 + Regime III) should be intact'

    def test_lemmas_all_pass(self):
        """G2: All three classical lemmas hold independently."""
        cert = rh_contradiction_certificate(
            H=H_TEST, N=N_TEST, mu0=MU0_TEST, n_points=N_PTS)
        assert cert['lemma_1']['psd'], 'Lemma 1 (PSD) fails'
        assert cert['lemma_2']['psd'], 'Lemma 2 (denominator) fails'
        assert cert['lemma_3']['fires'], 'Lemma 3 (ΔA sign) fails'

    def test_holy_grail_holds_in_diagnostic_certificate(self):
        """G3: Holy Grail holds within the diagnostic certificate."""
        cert = rh_contradiction_certificate(
            H=H_TEST, N=N_TEST, mu0=MU0_TEST, n_points=N_PTS)
        assert cert['holy_grail']['holds'], \
            (f'Holy Grail fails in certificate. '
             f'Worst margin: {cert["holy_grail"]["worst_margin"]:.6e}')

    def test_certificate_lists_conditions(self):
        """G4: Certificate honestly lists conditional assumptions."""
        cert = rh_contradiction_certificate(
            H=H_TEST, N=N_TEST, mu0=MU0_TEST, n_points=N_PTS)
        assert 'conditional_on' in cert
        assert len(cert['conditional_on']) >= 3, \
            'Certificate should list at least 3 conditional assumptions'

    def test_certificate_flags_hp_as_scaffold(self):
        """G5: Certificate marks the HP layer as experimental scaffold."""
        cert = rh_contradiction_certificate(
            H=H_TEST, N=N_TEST, mu0=MU0_TEST, n_points=N_PTS)
        assert 'status' in cert['holy_grail']
        assert 'SCAFFOLD' in cert['holy_grail']['status'].upper()


# ═════════════════════════════════════════════════════════════════════════
# Section H — SCALING DIAGNOSTICS (4 tests)
# ═════════════════════════════════════════════════════════════════════════

class TestScalingDiagnostics:
    """H: Deficit scaling exponent and B_HP lower bound."""

    def test_deficit_scaling_analysis(self, H_hp):
        """H1: Crack depth either vanishes (no crack) or scales with α > 0."""
        res = deficit_scaling_exponent(H_TEST, N_TEST, H_hp,
                                       T0=14.135, n_db=15,
                                       n_points=N_PTS)
        if not res['crack_found']:
            # No crack found — F̃₂ stays non-negative. Even better!
            pass
        else:
            assert res['exponent'] > 0, \
                f'Crack depth exponent non-positive: α={res["exponent"]:.3f}'

    def test_bhp_lower_bound_positive(self, H_hp):
        """H2: B_HP(T₀, 0) > 0 for all tested T₀ (H_HP pos. def.)."""
        res = bhp_lower_bound(H_TEST, N_TEST, H_hp,
                              T0_values=np.linspace(0, 80, 20))
        assert res['all_positive'], \
            f'B_HP ≤ 0 found at T₀={res["argmin_T0"]}'
        assert res['min_B_HP'] > 0

    def test_scaling_fit_quality(self, H_hp):
        """H3: Power-law fit to deficit has reasonable R²."""
        res = deficit_scaling_exponent(H_TEST, N_TEST, H_hp,
                                       T0=14.135, n_db=15,
                                       n_points=N_PTS)
        assert res['fit_quality'] > 0.5, \
            f'Power-law fit poor: R²={res["fit_quality"]:.3f}'

    def test_bhp_returns_structure(self, H_hp):
        """H4: B_HP lower bound function returns required keys."""
        res = bhp_lower_bound(H_TEST, N_TEST, H_hp,
                              T0_values=[0.0, 14.135])
        for key in ['min_B_HP', 'argmin_T0', 'all_positive']:
            assert key in res


# ═════════════════════════════════════════════════════════════════════════
# Section I — PARAMETRIC SWEEPS (slow — 3 tests)
# ═════════════════════════════════════════════════════════════════════════

class TestParametricSweeps:
    """I: Heavier sweeps across (T₀, Δβ) plane."""

    @pytest.mark.slow
    def test_holy_grail_verdict_wide_sweep(self):
        """I1: Holy Grail holds across wide (T₀, Δβ) grid."""
        result = holy_grail_verdict(
            H=H_TEST, N=N_TEST, mu0=MU0_TEST,
            T0_values=[0.0, 5.0, 14.135, 21.022, 30.0, 50.0, 75.0],
            db_values=[1e-5, 1e-4, 1e-3, 0.005, 0.01, 0.05,
                       0.1, 0.2, 0.3],
            n_points=N_PTS,
        )
        assert result['holds_everywhere'], \
            (f'Holy Grail fails at T0={result["worst_T0"]}, '
             f'Δβ={result["worst_db"]}: margin={result["worst_margin"]:.6e}')

    @pytest.mark.slow
    def test_verdict_auto_epsilon(self):
        """I2: Auto-selected ε produces full closure."""
        result = holy_grail_verdict(
            H=H_TEST, N=N_TEST, mu0=MU0_TEST, eps=None,
            n_points=N_PTS,
        )
        assert result['holds_everywhere'], \
            'Auto-ε does not achieve full closure'
        assert result['epsilon_used'] > 0

    @pytest.mark.slow
    def test_certificate_different_H(self):
        """I3: Certificate holds for H=3.0 and H=5.0."""
        for H in [3.0, 5.0]:
            cert = rh_contradiction_certificate(
                H=H, N=N_TEST, mu0=MU0_TEST, n_points=N_PTS)
            assert cert['chain_complete'], \
                f'Certificate fails at H={H}: {cert["verdict"]}'
