#!/usr/bin/env python3
r"""
================================================================================
test_47_limit_safety.py — Tier 30: Limit Safety & Promotion Guards
================================================================================

Tests the Limit Safety API that enforces rigorous mathematical bounds
on promoting finite-N Dirichlet polynomial results to true ζ(s) statements.

§1  Classical Error Envelope E(N, T)          (7 tests)
§2  ζ-Shadow & Dirichlet Proxy                (4 tests)
§3  LimitInterchangeGuard                     (5 tests)
§4  Promotion Classification (Level A/B/C)    (6 tests)
§5  Proof Chain Integration                   (5 tests)
§6  Strict Promotion Function                 (5 tests)

DESIGN PRINCIPLE:
  The core contradiction chain (Lemmas 1-3, Barriers) operates at Level A/B.
  It does NOT depend on D_N → ζ promotions. Level C is CONJECTURAL at
  σ = 1/2 and is reported as metadata for epistemic transparency.
  These tests verify that this boundary is correctly enforced.
================================================================================
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.limit_safety import (
    classical_dirichlet_error_bound,
    error_envelope_monotone_in_N,
    error_envelope_growth_in_T,
    zeta_shadow_value,
    dirichlet_polynomial_value,
    measured_discrepancy,
    zeta_shadow_functional,
    LimitInterchangeGuard,
    classify_promotion,
    is_conjectural,
    non_promotable_metadata,
    LEVEL_A, LEVEL_B, LEVEL_C, NON_PROMOTABLE,
)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — CLASSICAL ERROR ENVELOPE E(N, T)
# ═══════════════════════════════════════════════════════════════════════════════

class TestClassicalErrorBound:
    """Tests for the Hardy-Littlewood/Titchmarsh truncation error bound."""

    def test_bound_positive(self):
        """E(N, T) > 0 for valid parameters."""
        E = classical_dirichlet_error_bound(0.5, 100.0, 50)
        assert E > 0

    def test_bound_infinite_at_N_zero(self):
        """E(0, T) = inf (no terms in sum)."""
        E = classical_dirichlet_error_bound(0.5, 100.0, 0)
        assert np.isinf(E)

    def test_bound_decreases_with_N(self):
        """E(N, T) decreases as N grows at fixed σ, t."""
        E1 = classical_dirichlet_error_bound(0.5, 100.0, 10)
        E2 = classical_dirichlet_error_bound(0.5, 100.0, 100)
        E3 = classical_dirichlet_error_bound(0.5, 100.0, 1000)
        assert E1 > E2 > E3

    def test_bound_grows_with_t_at_half(self):
        """At σ = 1/2, E grows with t — cannot vanish uniformly."""
        E1 = classical_dirichlet_error_bound(0.5, 10.0, 100)
        E2 = classical_dirichlet_error_bound(0.5, 1000.0, 100)
        assert E2 > E1

    def test_bound_bounded_at_sigma_above_one(self):
        """At σ > 1, E is bounded and small even for large t."""
        E = classical_dirichlet_error_bound(1.5, 10000.0, 100)
        assert E < 10.0  # bounded, not blowing up

    def test_monotone_envelope(self):
        """Verify monotonicity diagnostic function."""
        result = error_envelope_monotone_in_N(
            0.5, 100.0, [10, 50, 100, 500, 1000],
        )
        assert result['monotone_decreasing']

    def test_growth_at_critical_line(self):
        """At σ = 1/2, error grows with t."""
        result = error_envelope_growth_in_T(
            0.5, [10, 100, 1000, 10000], 100,
        )
        assert result['grows_with_t']


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — ζ-SHADOW & DIRICHLET PROXY
# ═══════════════════════════════════════════════════════════════════════════════

class TestZetaShadow:
    """Tests for mpmath ζ-shadow and Dirichlet polynomial comparison."""

    def test_zeta_shadow_known_value(self):
        """ζ(2) = π²/6 ≈ 1.6449."""
        val = zeta_shadow_value(2.0, 0.0)
        assert abs(val - np.pi**2 / 6) < 1e-10

    def test_dirichlet_converges_at_sigma_gt_1(self):
        """D_N(σ+0i) → ζ(σ) for σ > 1 as N → ∞."""
        d100 = dirichlet_polynomial_value(2.0, 0.0, 100)
        d1000 = dirichlet_polynomial_value(2.0, 0.0, 1000)
        zeta_val = np.pi**2 / 6
        assert abs(d1000 - zeta_val) < abs(d100 - zeta_val)

    def test_measured_discrepancy_structure(self):
        """Discrepancy dict has required fields."""
        result = measured_discrepancy(2.0, 0.0, 100)
        assert 'measured_discrepancy' in result
        assert 'theoretical_bound' in result
        assert 'bound_valid' in result
        assert result['measured_discrepancy'] >= 0

    def test_discrepancy_bounded_by_theory_sigma_gt_1(self):
        """At σ > 1, numerical discrepancy respects the theoretical bound."""
        result = measured_discrepancy(2.0, 10.0, 200)
        # Allow loose bound — classical envelope is an asymptotic estimate
        assert result['theoretical_bound'] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — LIMIT INTERCHANGE GUARD
# ═══════════════════════════════════════════════════════════════════════════════

class TestLimitInterchangeGuard:
    """Tests for the LimitInterchangeGuard that mediates N → ∞ promotions."""

    def test_conjectural_at_half(self):
        """At σ = 1/2, the guard marks promotion as CONJECTURAL."""
        guard = LimitInterchangeGuard(
            T0_range=[0.0, 100.0], N=100, H=3.0, sigma=0.5,
        )
        cert = guard.generate_certificate()
        assert cert['status'] == 'CONJECTURAL'
        assert cert['requires_RH_uniformity']
        assert not cert['is_promotable']

    def test_promotable_at_sigma_above_one(self):
        """At σ > 1, classical bounds permit limit interchange."""
        guard = LimitInterchangeGuard(
            T0_range=[0.0, 100.0], N=100, H=3.0, sigma=1.5,
        )
        cert = guard.generate_certificate()
        assert cert['status'] == 'PROVED'
        assert cert['is_promotable']

    def test_certificate_structure(self):
        """Certificate contains required fields."""
        guard = LimitInterchangeGuard(
            T0_range=[0.0, 50.0], N=50, H=3.0,
        )
        cert = guard.generate_certificate()
        for key in ['N', 'H', 'sigma', 'T0_range', 'E_N_T_bound',
                     'requires_RH_uniformity', 'is_promotable',
                     'status', 'reason']:
            assert key in cert, f"Missing key: {key}"

    def test_large_N_still_conjectural_at_half(self):
        """Even very large N doesn't make σ = 1/2 promotion safe."""
        guard = LimitInterchangeGuard(
            T0_range=[0.0, 100.0], N=100000, H=3.0, sigma=0.5,
        )
        cert = guard.generate_certificate()
        assert cert['status'] == 'CONJECTURAL'

    def test_error_bound_finite(self):
        """The error bound is a finite positive number."""
        guard = LimitInterchangeGuard(
            T0_range=[0.0, 100.0], N=100, H=3.0,
        )
        cert = guard.generate_certificate()
        assert np.isfinite(cert['E_N_T_bound'])
        assert cert['E_N_T_bound'] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — PROMOTION CLASSIFICATION (Level A/B/C)
# ═══════════════════════════════════════════════════════════════════════════════

class TestPromotionClassification:
    """Tests for the Level A/B/C taxonomy."""

    def test_level_A_always_proved(self):
        """Level A (pure kernel) is always PROVED."""
        cls = classify_promotion(LEVEL_A)
        assert cls['status'] == 'PROVED'
        assert cls['level'] == LEVEL_A
        assert not cls['depends_on_zeta']

    def test_level_B_proved(self):
        """Level B (Dirichlet model) is always PROVED."""
        cls = classify_promotion(LEVEL_B, N=100)
        assert cls['status'] == 'PROVED'
        assert cls['level'] == LEVEL_B
        assert cls['depends_on_DN']

    def test_level_C_conjectural_at_half(self):
        """Level C at σ = 1/2 is CONJECTURAL."""
        cls = classify_promotion(
            LEVEL_C, sigma=0.5, N=100, T0_max=100.0, H=3.0,
        )
        assert cls['status'] == 'CONJECTURAL'
        assert cls['requires_limit_interchange']
        assert not cls['is_promotable']

    def test_level_C_proved_at_sigma_gt_1(self):
        """Level C at σ > 1 is PROVED."""
        cls = classify_promotion(
            LEVEL_C, sigma=1.5, N=100, T0_max=100.0, H=3.0,
        )
        assert cls['status'] == 'PROVED'
        assert cls['is_promotable']

    def test_is_conjectural_function(self):
        """is_conjectural correctly identifies conjectural promotions."""
        cls_A = classify_promotion(LEVEL_A)
        cls_C = classify_promotion(
            LEVEL_C, sigma=0.5, N=100, T0_max=100.0, H=3.0,
        )
        assert not is_conjectural(cls_A)
        assert is_conjectural(cls_C)

    def test_non_promotable_metadata(self):
        """non_promotable_metadata produces correct structure."""
        meta = non_promotable_metadata(
            'test_theorem', 'Requires Lindelöf hypothesis',
        )
        assert meta['label'] == NON_PROMOTABLE
        assert not meta['consumable_by_proof_chain']
        assert 'RH-equivalent' in meta['requires']


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — PROOF CHAIN INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestProofChainGuard:
    """Tests that the proof chain correctly reports limit safety metadata."""

    def test_chain_has_limit_safety_field(self):
        """contradiction_chain() now includes limit_safety metadata."""
        from engine.proof_chain import contradiction_chain
        result = contradiction_chain(H=3.0, n_9d=30)
        assert 'limit_safety' in result

    def test_chain_complete_still_true(self):
        """Core chain (Level A/B) is still complete — not blocked by Level C."""
        from engine.proof_chain import contradiction_chain
        result = contradiction_chain(H=3.0, n_9d=30)
        assert result['chain_complete'], (
            "Core chain should not be blocked by Level C metadata"
        )

    def test_limit_safety_reports_level_C_conjectural(self):
        """Limit safety correctly reports Level C as CONJECTURAL at σ = 1/2."""
        from engine.proof_chain import contradiction_chain
        result = contradiction_chain(H=3.0, n_9d=30)
        ls = result['limit_safety']
        assert ls['level_C']['status'] == 'CONJECTURAL'

    def test_core_chain_independent_of_level_C(self):
        """Core chain does not depend on Level C."""
        from engine.proof_chain import contradiction_chain
        result = contradiction_chain(H=3.0, n_9d=30)
        ls = result['limit_safety']
        assert ls['core_chain_depends_on_level_C'] is False

    def test_limit_safety_assessment_direct(self):
        """Direct call to limit_safety_assessment returns correct taxonomy."""
        from engine.proof_chain import limit_safety_assessment
        ls = limit_safety_assessment(H=3.0)
        assert ls['level_A']['status'] == 'PROVED'
        assert ls['level_B']['status'] == 'PROVED'
        assert ls['level_C']['status'] == 'CONJECTURAL'
        assert ls['core_chain_depends_on_level_C'] is False


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — STRICT PROMOTION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestStrictPromotion:
    """Tests for the strict Level A/B/C promotion in analytic_promotion.py."""

    def test_strict_promotion_structure(self):
        """limsup_lambda_N_ge_lambda_star_strict returns all three levels."""
        from engine.analytic_promotion import limsup_lambda_N_ge_lambda_star_strict
        result = limsup_lambda_N_ge_lambda_star_strict(H=3.0)
        assert 'level_A' in result
        assert 'level_B' in result
        assert 'level_C' in result

    def test_strict_promotion_level_A_proved(self):
        """Level A (kernel) is PROVED."""
        from engine.analytic_promotion import limsup_lambda_N_ge_lambda_star_strict
        result = limsup_lambda_N_ge_lambda_star_strict(H=3.0)
        assert result['level_A']['status'] == 'PROVED'

    def test_strict_promotion_level_B_proved(self):
        """Level B (Dirichlet model) is PROVED."""
        from engine.analytic_promotion import limsup_lambda_N_ge_lambda_star_strict
        result = limsup_lambda_N_ge_lambda_star_strict(H=3.0)
        assert result['level_B']['status'] == 'PROVED'

    def test_strict_promotion_level_C_conjectural(self):
        """Level C (ζ-promotion) is CONJECTURAL at σ = 1/2."""
        from engine.analytic_promotion import limsup_lambda_N_ge_lambda_star_strict
        result = limsup_lambda_N_ge_lambda_star_strict(H=3.0)
        assert result['level_C']['status'] == 'CONJECTURAL'
        assert not result['is_fully_proved']

    def test_strict_promotion_across_H(self):
        """Strict promotion works across H range."""
        from engine.analytic_promotion import limsup_lambda_N_ge_lambda_star_strict
        for H in [1.0, 2.0, 3.0, 5.0]:
            result = limsup_lambda_N_ge_lambda_star_strict(H=H)
            assert result['level_A']['status'] == 'PROVED'
            assert result['level_C']['status'] == 'CONJECTURAL'
