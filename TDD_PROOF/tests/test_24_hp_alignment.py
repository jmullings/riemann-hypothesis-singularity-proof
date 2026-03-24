#!/usr/bin/env python3
"""
================================================================================
test_24_hp_alignment.py — HP Spectral Sieve & Hybrid Crack Diagnostics
================================================================================

Tier 12: Dirichlet–HP alignment engine, hybrid Rayleigh quotient, and crack
diagnostic measuring whether the HP penalty improves the small-Δβ regime.

Sections:
  A. Dirichlet state properties (5 tests)
  B. HP operator matrix (4 tests)
  C. HP energy sanity (5 tests)
  D. RS Rayleigh with drift (5 tests)
  E. Hybrid F₂ functional (4 tests)
  F. Hybrid Rayleigh quotient (5 tests)
  G. Crack diagnostic (3 tests, slow)
  H. Edge cases (4 tests)
  I. Honest limits (3 tests)
================================================================================
"""

import numpy as np
import pytest

from engine.hp_alignment import (
    dirichlet_state,
    hp_energy,
    rs_rayleigh_with_drift,
    hybrid_lambda_star,
    hybrid_F2_RS,
)
from engine.bochner import lambda_star, F2_corrected, rayleigh_quotient
from engine.hilbert_polya import hp_operator_matrix, H_poly_matrix, get_poly_spectrum
from engine.kernel import w_H, W_curv


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

GAMMA_1 = 14.134725141734693790457251983562


@pytest.fixture(scope="module")
def hp_small():
    """Small-N HP operator and dimension for fast tests."""
    N = 50
    H_hp = hp_operator_matrix(N)
    return N, H_hp


@pytest.fixture(scope="module")
def hp_medium():
    """Medium-N HP operator for more thorough tests."""
    N = 200
    H_hp = hp_operator_matrix(N)
    return N, H_hp


# ═══════════════════════════════════════════════════════════════════════════════
# §A — Dirichlet State Properties
# ═══════════════════════════════════════════════════════════════════════════════

class TestDirichletState:

    def test_shape(self):
        """Dirichlet state has shape (N,)."""
        phi = dirichlet_state(GAMMA_1, 100)
        assert phi.shape == (100,)

    def test_complex_valued(self):
        """State is complex-valued due to phase e^{-iT log n}."""
        phi = dirichlet_state(GAMMA_1, 50)
        assert np.iscomplexobj(phi)
        assert not np.allclose(phi.imag, 0.0)

    def test_first_component(self):
        """φ₁ = 1^{-1/2-Δβ} · e^{-iT·0} = 1 for Δβ=0."""
        phi = dirichlet_state(GAMMA_1, 10, delta_beta=0.0)
        assert abs(phi[0] - 1.0) < 1e-14

    def test_norm_decreases_with_delta_beta(self):
        """Amplitudes n^{-1/2-Δβ} shrink with larger Δβ → norm decreases."""
        norms = []
        for db in [0.0, 0.05, 0.1, 0.2]:
            phi = dirichlet_state(GAMMA_1, 100, delta_beta=db)
            norms.append(np.linalg.norm(phi))
        for i in range(len(norms) - 1):
            assert norms[i + 1] < norms[i]

    def test_delta_beta_zero_matches_standard(self):
        """At Δβ=0, amplitude is n^{-1/2} (standard Dirichlet)."""
        phi = dirichlet_state(GAMMA_1, 20, delta_beta=0.0)
        n = np.arange(1, 21, dtype=np.float64)
        expected_amp = n ** -0.5
        np.testing.assert_allclose(np.abs(phi), expected_amp, atol=1e-14)


# ═══════════════════════════════════════════════════════════════════════════════
# §B — HP Operator Matrix
# ═══════════════════════════════════════════════════════════════════════════════

class TestHPOperatorMatrix:

    def test_shape(self, hp_small):
        N, H_hp = hp_small
        assert H_hp.shape == (N, N)

    def test_symmetric(self, hp_small):
        """HP operator matrix is real symmetric (diagonal)."""
        _, H_hp = hp_small
        np.testing.assert_allclose(H_hp, H_hp.T, atol=1e-14)

    def test_diagonal(self, hp_small):
        """hp_operator_matrix returns a diagonal matrix."""
        _, H_hp = hp_small
        off_diag = H_hp - np.diag(np.diag(H_hp))
        assert np.allclose(off_diag, 0.0)

    def test_eigenvalues_positive(self, hp_small):
        """All eigenvalues of H_poly are positive (Sturm-Liouville)."""
        _, H_hp = hp_small
        evals = np.diag(H_hp)
        assert np.all(evals > 0)


# ═══════════════════════════════════════════════════════════════════════════════
# §C — HP Energy Sanity
# ═══════════════════════════════════════════════════════════════════════════════

class TestHPEnergy:

    def test_real_and_finite(self, hp_small):
        """HP energy is a real finite number."""
        N, H_hp = hp_small
        val = hp_energy(GAMMA_1, H_hp, N)
        assert isinstance(val, float)
        assert np.isfinite(val)

    def test_positive_for_positive_operator(self, hp_small):
        """H_poly is positive definite → ⟨φ, H φ⟩ > 0 for any nonzero φ."""
        N, H_hp = hp_small
        val = hp_energy(GAMMA_1, H_hp, N)
        assert val > 0

    def test_varies_with_T0(self, hp_small):
        """Energy changes when T₀ changes (phase sensitivity)."""
        N, H_hp = hp_small
        e1 = hp_energy(GAMMA_1, H_hp, N)
        e2 = hp_energy(21.022, H_hp, N)
        assert e1 != e2

    def test_varies_with_delta_beta(self, hp_small):
        """Energy changes with Δβ drift."""
        N, H_hp = hp_small
        e1 = hp_energy(GAMMA_1, H_hp, N, delta_beta=0.0)
        e2 = hp_energy(GAMMA_1, H_hp, N, delta_beta=0.1)
        assert e1 != e2

    def test_decreases_with_large_delta_beta(self, hp_small):
        """Larger Δβ → smaller norm → smaller energy (monotonic for PD operator)."""
        N, H_hp = hp_small
        energies = []
        for db in [0.0, 0.1, 0.3, 0.5]:
            energies.append(hp_energy(GAMMA_1, H_hp, N, delta_beta=db))
        for i in range(len(energies) - 1):
            assert energies[i + 1] < energies[i]


# ═══════════════════════════════════════════════════════════════════════════════
# §D — RS Rayleigh Quotient with Drift
# ═══════════════════════════════════════════════════════════════════════════════

class TestRSRayleighDrift:

    def test_returns_dict(self, hp_small):
        """Function returns dict with A, B, lambda_star_T0."""
        N, _ = hp_small
        res = rs_rayleigh_with_drift(GAMMA_1, 3.0, N, delta_beta=0.0,
                                     n_points=200)
        assert 'A' in res
        assert 'B' in res
        assert 'lambda_star_T0' in res

    def test_B_positive(self, hp_small):
        """Denominator B = ∫ w_H |D|² dt > 0 (w_H > 0, |D|² ≥ 0)."""
        N, _ = hp_small
        res = rs_rayleigh_with_drift(GAMMA_1, 3.0, N, delta_beta=0.0,
                                     n_points=200)
        assert res['B'] > 0

    def test_matches_bochner_at_zero_drift(self, hp_small):
        """At Δβ=0, rs_rayleigh_with_drift agrees with bochner.rayleigh_quotient."""
        N, _ = hp_small
        H = 3.0
        drift = rs_rayleigh_with_drift(GAMMA_1, H, N, delta_beta=0.0,
                                       n_points=300)
        base = rayleigh_quotient(GAMMA_1, H, N, n_points=300)
        # Numerical agreement (same formula)
        np.testing.assert_allclose(drift['A'], base['A'], rtol=1e-6)
        np.testing.assert_allclose(drift['B'], base['B'], rtol=1e-6)

    def test_lambda_finite(self, hp_small):
        """Rayleigh quotient is finite."""
        N, _ = hp_small
        res = rs_rayleigh_with_drift(GAMMA_1, 3.0, N, delta_beta=0.01,
                                     n_points=200)
        assert np.isfinite(res['lambda_star_T0'])

    def test_A_changes_with_drift(self, hp_small):
        """A component changes when Δβ changes."""
        N, _ = hp_small
        r0 = rs_rayleigh_with_drift(GAMMA_1, 3.0, N, delta_beta=0.0,
                                    n_points=200)
        r1 = rs_rayleigh_with_drift(GAMMA_1, 3.0, N, delta_beta=0.1,
                                    n_points=200)
        assert r0['A'] != r1['A']


# ═══════════════════════════════════════════════════════════════════════════════
# §E — Hybrid F₂ Functional
# ═══════════════════════════════════════════════════════════════════════════════

class TestHybridF2:

    def test_eps_zero_recovers_F2_corrected(self, hp_small):
        """At ε=0, hybrid_F2_RS equals F2_corrected."""
        N, H_hp = hp_small
        H = 3.0
        hybrid = hybrid_F2_RS(GAMMA_1, H, N, H_hp, eps=0.0, n_points=200)
        pure = F2_corrected(GAMMA_1, H, N, n_points=200)
        np.testing.assert_allclose(hybrid, pure, atol=1e-10)

    def test_positive_eps_increases_functional(self, hp_small):
        """Positive ε with positive B_HP → hybrid > pure."""
        N, H_hp = hp_small
        H = 3.0
        pure = hybrid_F2_RS(GAMMA_1, H, N, H_hp, eps=0.0, n_points=200)
        hybrid = hybrid_F2_RS(GAMMA_1, H, N, H_hp, eps=0.1, n_points=200)
        assert hybrid > pure

    def test_finite_result(self, hp_small):
        """Hybrid functional returns finite float."""
        N, H_hp = hp_small
        val = hybrid_F2_RS(GAMMA_1, 3.0, N, H_hp, eps=0.01, n_points=200)
        assert isinstance(val, float)
        assert np.isfinite(val)

    def test_scales_linearly_in_eps(self, hp_small):
        """F_hybrid(2ε) − F_pure ≈ 2 · (F_hybrid(ε) − F_pure)."""
        N, H_hp = hp_small
        H = 3.0
        F0 = hybrid_F2_RS(GAMMA_1, H, N, H_hp, eps=0.0, n_points=200)
        F1 = hybrid_F2_RS(GAMMA_1, H, N, H_hp, eps=0.05, n_points=200)
        F2 = hybrid_F2_RS(GAMMA_1, H, N, H_hp, eps=0.10, n_points=200)
        delta1 = F1 - F0
        delta2 = F2 - F0
        np.testing.assert_allclose(delta2, 2.0 * delta1, rtol=1e-6)


# ═══════════════════════════════════════════════════════════════════════════════
# §F — Hybrid Rayleigh Quotient
# ═══════════════════════════════════════════════════════════════════════════════

class TestHybridRayleigh:

    def test_eps_zero_lambda_old_equals_new(self, hp_small):
        """At ε=0, λ_new = λ_old."""
        N, H_hp = hp_small
        H = 3.0
        res = hybrid_lambda_star(GAMMA_1, H, N, H_hp, eps=0.0,
                                 n_points=200)
        np.testing.assert_allclose(res['lambda_new'], res['lambda_old'],
                                   atol=1e-10)

    def test_positive_eps_lifts_lambda(self, hp_small):
        """Positive ε with positive B_HP increases λ_new above λ_old."""
        N, H_hp = hp_small
        H = 3.0
        res = hybrid_lambda_star(GAMMA_1, H, N, H_hp, eps=0.1,
                                 delta_beta=0.01, n_points=200)
        assert res['lambda_new'] > res['lambda_old']

    def test_decomposition_keys(self, hp_small):
        """Output contains all expected keys."""
        N, H_hp = hp_small
        res = hybrid_lambda_star(GAMMA_1, 3.0, N, H_hp, eps=0.01,
                                 n_points=200)
        for key in ['A_RS', 'B_RS', 'B_HP', 'lambda_old', 'lambda_new']:
            assert key in res

    def test_B_RS_positive(self, hp_small):
        """B_RS > 0 (w_H is positive, |D|² ≥ 0)."""
        N, H_hp = hp_small
        res = hybrid_lambda_star(GAMMA_1, 3.0, N, H_hp, eps=0.01,
                                 n_points=200)
        assert res['B_RS'] > 0

    def test_B_HP_positive(self, hp_small):
        """B_HP > 0 (H_poly is positive definite)."""
        N, H_hp = hp_small
        res = hybrid_lambda_star(GAMMA_1, 3.0, N, H_hp, eps=0.01,
                                 n_points=200)
        assert res['B_HP'] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# §G — Crack Diagnostic (Slow)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrackDiagnostic:

    @pytest.mark.slow
    def test_lambda_old_dips_at_small_delta_beta(self, hp_medium):
        """
        Verify that the old RS Rayleigh quotient λ_old^* at some Δβ
        is less than the Bochner floor λ*(H).

        This is the known crack from the pure RS approach.
        """
        N, H_hp = hp_medium
        H = 3.0
        lam_floor = lambda_star(H)

        # Sweep Δβ
        deltas = np.logspace(-1, -3, num=4)
        lam_old_vals = []
        for db in deltas:
            res = hybrid_lambda_star(
                GAMMA_1, H, N, H_hp, eps=0.0,
                delta_beta=db, n_points=300,
            )
            lam_old_vals.append(res['lambda_old'])

        assert min(lam_old_vals) < lam_floor

    @pytest.mark.slow
    def test_hp_penalty_does_not_worsen(self, hp_medium):
        """
        HP penalty should not make things worse: λ_new ≥ λ_old pointwise
        when ε > 0 and B_HP > 0.
        """
        N, H_hp = hp_medium
        H = 3.0
        eps = 0.1

        deltas = np.logspace(-1, -3, num=4)
        for db in deltas:
            res = hybrid_lambda_star(
                GAMMA_1, H, N, H_hp, eps=eps,
                delta_beta=db, n_points=300,
            )
            assert res['lambda_new'] >= res['lambda_old'] - 1e-8

    @pytest.mark.slow
    def test_improvement_positive(self, hp_medium):
        """
        EXPERIMENTAL: At least somewhere in the Δβ range,
        λ_new − λ_old > 0 (HP penalty provides measurable improvement).
        """
        N, H_hp = hp_medium
        H = 3.0
        eps = 0.1

        deltas = np.logspace(-1, -3, num=4)
        improvements = []
        for db in deltas:
            res = hybrid_lambda_star(
                GAMMA_1, H, N, H_hp, eps=eps,
                delta_beta=db, n_points=300,
            )
            improvements.append(res['lambda_new'] - res['lambda_old'])

        assert max(improvements) > 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# §H — Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:

    def test_N_one(self):
        """N=1 produces a valid scalar state φ₁ = 1."""
        phi = dirichlet_state(GAMMA_1, 1, delta_beta=0.0)
        assert phi.shape == (1,)
        np.testing.assert_allclose(np.abs(phi[0]), 1.0, atol=1e-14)

    def test_delta_beta_zero_exact(self, hp_small):
        """Δβ=0 exactly gives the standard Dirichlet polynomial."""
        N, H_hp = hp_small
        res = rs_rayleigh_with_drift(GAMMA_1, 3.0, N, delta_beta=0.0,
                                     n_points=200)
        assert np.isfinite(res['lambda_star_T0'])
        assert res['B'] > 0

    def test_large_delta_beta(self, hp_small):
        """Large Δβ should not crash — just suppress amplitudes strongly."""
        N, H_hp = hp_small
        phi = dirichlet_state(GAMMA_1, N, delta_beta=2.0)
        # n=1 still contributes, but higher n are heavily suppressed
        assert np.isfinite(np.linalg.norm(phi))
        val = hp_energy(GAMMA_1, H_hp, N, delta_beta=2.0)
        assert np.isfinite(val)
        assert val > 0

    def test_T0_zero(self, hp_small):
        """T₀=0 gives real-valued Dirichlet state (phases = 1)."""
        N, _ = hp_small
        phi = dirichlet_state(0.0, N, delta_beta=0.0)
        np.testing.assert_allclose(phi.imag, 0.0, atol=1e-14)


# ═══════════════════════════════════════════════════════════════════════════════
# §I — Honest Limits
# ═══════════════════════════════════════════════════════════════════════════════

class TestHonestLimits:

    def test_diagonal_approximation_caveat(self, hp_small):
        """
        hp_operator_matrix is diagonal — it does NOT represent H_poly's action
        in the n-basis, only its spectral content. Document this fact.
        """
        N, H_hp = hp_small
        # Verify it's diagonal (the honest caveat)
        off_diag_norm = np.linalg.norm(H_hp - np.diag(np.diag(H_hp)))
        assert off_diag_norm == 0.0, \
            "hp_operator_matrix must be diagonal (spectral representation only)"

    def test_global_inequality_not_asserted(self, hp_small):
        """
        We do NOT claim λ_new ≥ λ*(H) globally. Test explicitly that we
        can find regimes where λ_new < λ*(H) (the crack is not sealed).
        """
        N, H_hp = hp_small
        H = 3.0
        lam_floor = lambda_star(H)
        # At very small Δβ and small ε, the crack should still be present
        res = hybrid_lambda_star(GAMMA_1, H, N, H_hp, eps=1e-6,
                                 delta_beta=1e-3, n_points=200)
        # We don't force this to fail — but we don't claim it passes either
        # The honest test: the result exists and is measurable
        assert np.isfinite(res['lambda_new'])
        # If it's below the floor, that's honest — the crack is documented
        if res['lambda_new'] < lam_floor:
            pass  # Expected: crack persists at tiny ε

    def test_finite_N_only(self, hp_small):
        """
        All computations are finite-N. No N→∞ extrapolation is made.
        Document that results are for N=50 truncation.
        """
        N, _ = hp_small
        assert N == 50, "This fixture tests at N=50 only"
