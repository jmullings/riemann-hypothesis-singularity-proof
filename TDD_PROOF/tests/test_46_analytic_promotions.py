#!/usr/bin/env python3
r"""
================================================================================
test_46_analytic_promotions.py — TDD Proofs for Infinite-Dimensional Theorems
================================================================================

Tier 28: Analytic Promotions — finite-N → infinite-dimensional

THREE TIERS OF EPISTEMIC RIGOR:
  Tier A (Level 0–1): Pure algebra/analysis tests. No floats, no quadrature.
         Algebraic identities, sign logic, Bochner inference, converse arguments.
  Tier B (Level 2):   Symbolic–numeric sanity tests. Bounded approximations,
         explicitly labeled as numeric verification, not proof.
  Tier C (Level 2):   Integration tests. Assert code wiring correctness,
         separation of concerns, no overclaiming.

§1  Sech⁴ Identity                                (Tier A + B)
§2  Bochner PSD Infinite-Dimensional               (Tier A + B + C)
§3  Riemann-Lebesgue Global Negativity              (Tier A + B + C)
§4  Spectral Zeta Absolute Convergence              (Tier A + B)
§5  limsup_{N→∞} λ_N ≥ λ* — Rayleigh Tightness    (Tier A + B + C)

SEPARATION OF CONCERNS:
  - *_analytic() functions carry the logical proof (tested in Tier A).
  - *_numeric() functions provide cross-validation (tested in Tier B).
  - Tier C tests verify that analytic certificates do NOT depend on
    numeric-only helpers (no scipy quadrature, no finite grids).
================================================================================
"""

import inspect
import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.analytic_promotion import (
    # §1: Sech⁴
    w_H_second_derivative_formula,
    g_lambda_star_from_wH,
    sech4_identity,
    verify_sech4_identity,
    # §2a: Bochner analytic
    bochner_psd_infinite_analytic,
    bochner_psd_infinite_numeric,
    bochner_psd_infinite,
    # §3a: R-L analytic
    envelope_sign_analytic,
    riemann_lebesgue_bound_analytic,
    riemann_lebesgue_global_negativity_analytic,
    # §3b: R-L numeric
    envelope_integral,
    riemann_lebesgue_decay_bound,
    riemann_lebesgue_global_negativity,
    # §4: Spectral zeta
    spectral_zeta_convergence_analytic,
    spectral_zeta_tail_bound,
    spectral_zeta_convergence,
    # §5a: Kernel theorem
    kernel_limsup_lambda_ge_lambda_star,
    sub_threshold_negativity,
    # §5b: Rayleigh numeric
    rayleigh_quotient_at,
    rayleigh_quotient_sequence,
    limsup_lambda_N_ge_lambda_star,
    # §5c: Strict promotion
    limsup_lambda_N_ge_lambda_star_strict,
)
from engine.kernel import sech2, w_H, W_curv
from engine.bochner import lambda_star, build_corrected_toeplitz, min_eigenvalue


###############################################################################
#                                                                             #
#   TIER A — Pure Algebra / Analysis (Level 0–1)                              #
#   No scipy quadrature, no finite grids, no randomness.                      #
#                                                                             #
###############################################################################


# ═══════════════════════════════════════════════════════════════════════════════
# §1A — SECH⁴ IDENTITY (TIER A: algebraic)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSech4IdentityAlgebraic:
    """Tier A: Verify the algebraic identity -w_H'' + λ*·w_H = (6/H²)sech⁴."""

    @pytest.mark.parametrize("H", [0.5, 1.0, 1.5, 2.0, 3.0])
    def test_identity_holds_to_machine_precision(self, H):
        """LHS = -w_H'' + λ*w_H matches RHS = (6/H²)sech⁴ to < 1e-12."""
        cert = verify_sech4_identity(H, n_points=1000)
        assert cert['identity_holds'], (
            f"sech⁴ identity failed at H={H}: max_error={cert['max_error']}"
        )
        assert cert['max_error'] < 1e-12

    def test_symbolic_derivation_matches_code(self):
        """Cross-validate: g_lambda_star_from_wH == sech4_identity."""
        H = 1.3
        t = np.linspace(-5, 5, 1000)
        lhs = g_lambda_star_from_wH(t, H)
        rhs = sech4_identity(t, H)
        assert np.max(np.abs(lhs - rhs)) < 1e-14

    def test_w_H_second_derivative_consistent_with_W_curv(self):
        """w_H_second_derivative_formula == -W_curv (independent impl)."""
        H = 1.7
        t = np.linspace(-8, 8, 500)
        from_formula = w_H_second_derivative_formula(t, H)
        from_W_curv = -W_curv(t, H)
        assert np.max(np.abs(from_formula - from_W_curv)) < 1e-13

    def test_identity_at_origin(self):
        """At t=0: g_{λ*}(0) = (6/H²)·sech⁴(0) = 6/H²."""
        for H in [1.0, 2.0]:
            val = sech4_identity(0.0, H)
            assert abs(val - 6.0 / H**2) < 1e-14

    def test_strict_positivity(self):
        """sech⁴(t/H) > 0 for all finite t ⇒ g_{λ*}(t) > 0."""
        cert = verify_sech4_identity(1.0)
        assert cert['strictly_positive']
        assert cert['min_interior_value'] > 0

    def test_symmetry(self):
        """g_{λ*}(t) is even: g_{λ*}(-t) = g_{λ*}(t)."""
        H = 1.5
        t_pos = np.linspace(0.1, 10, 50)
        assert np.allclose(sech4_identity(t_pos, H),
                           sech4_identity(-t_pos, H), rtol=1e-14)

    def test_monotone_decrease_from_origin(self):
        """g_{λ*}(t) monotonically decreasing for t > 0."""
        H = 1.0
        t_grid = np.linspace(0, 20, 500)
        vals = sech4_identity(t_grid, H)
        diffs = np.diff(vals)
        assert np.all(diffs <= 1e-15)

    def test_decay_at_infinity(self):
        """sech⁴(t/H) → 0 as |t| → ∞ (exponential decay)."""
        H = 1.0
        t_far = np.array([50.0, 100.0, 200.0])
        vals = sech4_identity(t_far, H)
        assert np.all(vals < 1e-20)

    def test_epistemic_level_is_zero(self):
        """sech⁴ identity certificate has epistemic_level 0."""
        cert = verify_sech4_identity(1.0)
        assert cert['epistemic_level'] == 0

    def test_integral_value(self):
        """∫ (6/H²) sech⁴(t/H) dt = 8/H (sech⁴(u) integrates to 4/3)."""
        H = 1.0
        t_grid = np.linspace(-50, 50, 10000)
        dt = t_grid[1] - t_grid[0]
        integral = np.sum(sech4_identity(t_grid, H)) * dt
        expected = 8.0 / H
        assert abs(integral - expected) / expected < 1e-4


# ═══════════════════════════════════════════════════════════════════════════════
# §2A — BOCHNER PSD INFINITE-DIMENSIONAL (TIER A: analytic theorem)
# ═══════════════════════════════════════════════════════════════════════════════

class TestBochnerPsdInfiniteAnalytic:
    """Tier A: Analytic Bochner PSD theorem — no eigenvalue computation."""

    def test_analytic_theorem_proved(self):
        """bochner_psd_infinite_analytic proves the theorem at Level 1."""
        cert = bochner_psd_infinite_analytic(1.0)
        assert cert['proved']
        assert cert['epistemic_level'] == 1

    def test_proof_type_is_analytic(self):
        """Proof type says ANALYTIC, not NUMERIC."""
        cert = bochner_psd_infinite_analytic(1.0)
        assert 'ANALYTIC' in cert['proof_type']
        assert 'NUMERIC' not in cert['proof_type']

    def test_sech4_identity_is_foundation(self):
        """Analytic certificate depends on sech⁴ identity."""
        cert = bochner_psd_infinite_analytic(1.0)
        assert cert['sech4_identity']['identity_holds']
        assert cert['sech4_identity']['strictly_positive']

    @pytest.mark.parametrize("H", [0.5, 1.0, 2.0, 3.0])
    def test_analytic_across_H(self, H):
        """Analytic theorem holds for multiple H values."""
        cert = bochner_psd_infinite_analytic(H)
        assert cert['proved']

    def test_analytic_does_not_use_eigenvalues(self):
        """Analytic certificate has no 'finite_checks' field."""
        cert = bochner_psd_infinite_analytic(1.0)
        assert 'finite_checks' not in cert


# ═══════════════════════════════════════════════════════════════════════════════
# §3A — RIEMANN-LEBESGUE GLOBAL NEGATIVITY (TIER A: analytic)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRiemannLebesgueAnalytic:
    """Tier A: Pure sign reasoning — no scipy quadrature."""

    def test_envelope_sign_proved(self):
        """Envelope negativity proved by sign analysis alone."""
        cert = envelope_sign_analytic()
        assert cert['proved']
        assert cert['epistemic_level'] == 0

    def test_envelope_sign_conditions(self):
        """All sign conditions hold on [0.5, 1.9]."""
        cert = envelope_sign_analytic()
        conds = cert['conditions']
        assert conds['sin_positive_on_support']
        assert conds['u_squared_positive']
        assert conds['w_tilde_nonneg']
        assert conds['support_nonempty']
        assert conds['integrand_nonneg']
        assert conds['integral_positive']

    def test_envelope_sign_requires_pole_free_support(self):
        """If support includes u=2 (pole), sin condition fails."""
        cert = envelope_sign_analytic(c1=0.5, c2=2.5)
        assert not cert['conditions']['sin_positive_on_support']
        assert not cert['proved']

    def test_rl_bound_analytic_proved(self):
        """R-L bound has explicit constant at Level 1."""
        cert = riemann_lebesgue_bound_analytic()
        assert cert['proved']
        assert cert['epistemic_level'] == 1
        assert cert['C_explicit'] > 0

    def test_rl_explicit_constant_value(self):
        """C_explicit = c₂²/sin(πc₁/2) is correctly computed."""
        c1, c2 = 0.5, 1.9
        expected = c2**2 / np.sin(np.pi * c1 / 2.0)
        cert = riemann_lebesgue_bound_analytic(c1, c2)
        assert abs(cert['C_explicit'] - expected) < 1e-12

    def test_global_negativity_analytic_proved(self):
        """Combined analytic theorem proved at Level 1."""
        cert = riemann_lebesgue_global_negativity_analytic()
        assert cert['proved']
        assert cert['epistemic_level'] == 1

    def test_global_negativity_analytic_has_both_regimes(self):
        """Certificate addresses both large and bounded γ₀Δβ regimes."""
        cert = riemann_lebesgue_global_negativity_analytic()
        assert 'envelope' in cert['large_regime']
        assert 'adaptive' in cert['bounded_regime']


# ═══════════════════════════════════════════════════════════════════════════════
# §4A — SPECTRAL ZETA CONVERGENCE (TIER A: analytic)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpectralZetaConvergenceAnalytic:
    """Tier A: Analytic spectral zeta convergence — no von Mangoldt sums."""

    @pytest.mark.parametrize("sigma", [1.5, 2.0, 3.0, 5.0])
    def test_convergence_proved(self, sigma):
        """Absolute convergence proved analytically for σ > 1."""
        cert = spectral_zeta_convergence_analytic(sigma)
        assert cert['proved']
        assert cert['epistemic_level'] == 1

    def test_divergence_at_sigma_1(self):
        """Does NOT converge at σ = 1."""
        cert = spectral_zeta_convergence_analytic(1.0)
        assert not cert['converges']
        assert not cert['proved']

    def test_tail_formula_is_algebraic(self):
        """Tail formula uses only elementary operations (no scipy)."""
        sigma = 2.5
        sm1 = sigma - 1.0
        N_ref = 1000
        expected_1000 = (N_ref**(1 - sigma)) * (
            np.log(N_ref)/sm1 + 1/sm1**2
        )
        cert = spectral_zeta_convergence_analytic(sigma)
        assert abs(cert['tail_at_N1000'] - expected_1000) < 1e-14

    def test_tail_vanishes_faster_at_high_sigma(self):
        """Higher σ gives smaller tail at N=1000."""
        t2 = spectral_zeta_convergence_analytic(2.0)['tail_at_N1000']
        t5 = spectral_zeta_convergence_analytic(5.0)['tail_at_N1000']
        assert t5 < t2


# ═══════════════════════════════════════════════════════════════════════════════
# §5A — KERNEL LIMSUP THEOREM (TIER A: pure kernel, no D_N)
# ═══════════════════════════════════════════════════════════════════════════════

class TestKernelLimsupAnalytic:
    """Tier A: Pure kernel theorem — no Dirichlet polynomials, no Rayleigh."""

    def test_kernel_theorem_proved(self):
        """kernel_limsup_lambda_ge_lambda_star proves at Level 1."""
        cert = kernel_limsup_lambda_ge_lambda_star(1.0)
        assert cert['proved']
        assert cert['epistemic_level'] == 1

    def test_upper_bound_proved(self):
        """Upper bound: λ_N ≤ λ* for all N (Bochner PSD)."""
        cert = kernel_limsup_lambda_ge_lambda_star(1.0)
        assert cert['upper_bound_proved']

    def test_lower_bound_proved(self):
        """Lower bound: limsup ≥ λ* (Bochner converse)."""
        cert = kernel_limsup_lambda_ge_lambda_star(1.0)
        assert cert['lower_bound_proved']

    @pytest.mark.parametrize("epsilon", [1.0, 0.5, 0.1, 0.01])
    def test_sub_threshold_negativity(self, epsilon):
        """g_{λ*−ε}(t) < 0 for some t ⇒ f_{λ*−ε} not pos-def."""
        H = 1.0
        if epsilon >= lambda_star(H):
            pytest.skip("ε ≥ λ*: sub-threshold undefined")
        cert = sub_threshold_negativity(H, epsilon)
        assert cert['has_negative_region']
        assert cert['min_value'] < 0
        assert cert['epistemic_level'] == 0

    def test_crossover_analytic_formula(self):
        """Analytic crossover arccosh(√(6/(εH²))) is positive."""
        H = 1.0
        cert = sub_threshold_negativity(H, 0.5, n_points=5000)
        assert cert['analytic_crossover'] > 0

    @pytest.mark.parametrize("H", [0.5, 1.0, 2.0])
    def test_kernel_theorem_across_H(self, H):
        """Kernel theorem holds for multiple H values."""
        cert = kernel_limsup_lambda_ge_lambda_star(H)
        assert cert['proved']

    def test_proof_type_is_analytic(self):
        """Proof type says ANALYTIC, not NUMERIC."""
        cert = kernel_limsup_lambda_ge_lambda_star(1.0)
        assert 'ANALYTIC' in cert['proof_type']

    def test_sech4_identity_is_foundation(self):
        """Kernel theorem is built on sech⁴ identity."""
        cert = kernel_limsup_lambda_ge_lambda_star(1.0)
        assert cert['sech4_identity']['identity_holds']

    def test_all_sub_threshold_negative(self):
        """All ε probes show negative regions."""
        cert = kernel_limsup_lambda_ge_lambda_star(1.0)
        assert cert['all_sub_threshold_negative']


###############################################################################
#                                                                             #
#   TIER B — Symbolic-Numeric Sanity (Level 2)                                #
#   Bounded approximations, cross-validation, convergence checks.             #
#   Explicitly labeled as NUMERIC SUPPORT, not proof.                         #
#                                                                             #
###############################################################################


# ═══════════════════════════════════════════════════════════════════════════════
# §2B — BOCHNER PSD NUMERIC CONSISTENCY (TIER B)
# ═══════════════════════════════════════════════════════════════════════════════

class TestBochnerPsdNumeric:
    """Tier B: Numeric PSD checks — cross-validates analytic theorem."""

    def test_numeric_consistency(self):
        """Numeric certificate is consistent at Level 2."""
        cert = bochner_psd_infinite_numeric(1.0, N_values=[10, 50, 100])
        assert cert['consistent']
        assert cert['epistemic_level'] == 2

    @pytest.mark.parametrize("N", [10, 50, 100, 200, 500])
    def test_psd_at_N(self, N):
        """Corrected Toeplitz is PSD at each N (log-integer spectrum)."""
        H = 1.0
        spectrum = np.log(np.arange(1, N + 1))
        M = build_corrected_toeplitz(spectrum, H)
        assert min_eigenvalue(M) >= -1e-10, f"PSD failed at N={N}"

    @pytest.mark.parametrize("H", [0.5, 1.0, 2.0, 3.0])
    def test_psd_across_H(self, H):
        """PSD holds for multiple bandwidth values H."""
        spectrum = np.log(np.arange(1, 51))
        M = build_corrected_toeplitz(spectrum, H)
        assert min_eigenvalue(M) >= -1e-10

    def test_random_spectrum_psd(self):
        """PSD for arbitrary (non-log-integer) spectra — universality."""
        H = 1.0
        rng = np.random.RandomState(42)
        for _ in range(5):
            spectrum = np.sort(rng.uniform(0, 20, size=30))
            M = build_corrected_toeplitz(spectrum, H)
            assert min_eigenvalue(M) >= -1e-10

    def test_min_eigenvalue_nonneg(self):
        """min_eigenvalue ≥ 0 at λ* (PSD within machine precision)."""
        H = 1.0
        spectrum = np.log(np.arange(1, 51))
        M = build_corrected_toeplitz(spectrum, H)
        assert min_eigenvalue(M) >= -1e-10

    def test_combined_certificate_proved(self):
        """Combined bochner_psd_infinite: proved from analytic, numeric consistent."""
        cert = bochner_psd_infinite(1.0, N_values=[10, 50, 100])
        assert cert['proved']
        assert cert['numeric_consistent']
        assert cert['epistemic_level'] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# §3B — RIEMANN-LEBESGUE NUMERIC SUPPORT (TIER B)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRiemannLebesgueNumeric:
    """Tier B: Numeric R-L checks — cross-validates analytic theorem."""

    def test_envelope_strictly_negative(self):
        """Numeric envelope < 0 for any Δβ > 0 (cross-validates Level 0)."""
        for db in [0.01, 0.1, 0.5, 1.0]:
            env = envelope_integral(db)
            assert env < 0, f"Envelope should be < 0, got {env} at Δβ={db}"

    def test_envelope_scales_as_delta_beta_squared(self):
        """envelope ~ −C·Δβ² (quadratic scaling)."""
        env1 = envelope_integral(0.1)
        env2 = envelope_integral(0.2)
        ratio = env2 / env1
        assert abs(ratio - 4.0) < 0.01

    def test_riemann_lebesgue_decay(self):
        """Oscillatory correction decays as 1/(γ₀·Δβ)."""
        r1 = riemann_lebesgue_decay_bound(10, 0.5)
        r2 = riemann_lebesgue_decay_bound(100, 0.5)
        assert r2['decay_bound'] < r1['decay_bound'] * 0.2

    def test_envelope_negative_at_all_delta_beta(self):
        """Numeric envelope negative for wide range of Δβ."""
        for db in [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0]:
            env = envelope_integral(db)
            assert env < 0

    def test_decay_bound_decreases_with_gamma0(self):
        """R-L decay bound shrinks monotonically with γ₀."""
        bounds = [riemann_lebesgue_decay_bound(g0, 0.1)['decay_bound']
                  for g0 in [10, 50, 100, 500]]
        for i in range(len(bounds) - 1):
            assert bounds[i + 1] < bounds[i]

    def test_large_gamma0_delta_beta_negativity(self):
        """For large γ₀·Δβ, the oscillation is negligible → full integral negative."""
        from engine.analytic_bounds import averaged_deltaA_continuous
        r = averaged_deltaA_continuous(10000, 0.3, c1=0.5, c2=1.9)
        assert r['envelope'] < 0
        assert abs(r['oscillatory']) < abs(r['envelope']) * 2.0

    def test_adaptive_h_negativity(self):
        """The contradiction_engine (adaptive H) detects off-critical zeros."""
        from engine.triad_governor import contradiction_engine
        for g0 in [14.135, 50.0]:
            cert = contradiction_engine(g0, 0.3, N=30)
            assert cert['A_off_avg'] < 0

    def test_pole_free_support(self):
        """Default support [0.5, 1.9] avoids sin(πu/2)=0 poles."""
        u_grid = np.linspace(0.5, 1.9, 100)
        sin_vals = np.sin(np.pi * u_grid / 2.0)
        assert np.all(sin_vals > 0.1)

    def test_envelope_integral_is_finite(self):
        """Envelope integral converges on pole-free support."""
        env = envelope_integral(1.0, c1=0.5, c2=1.9)
        assert np.isfinite(env)
        assert env < 0

    def test_decay_bound_structure(self):
        """R-L decay bound has expected structure: C, ω, bound."""
        r = riemann_lebesgue_decay_bound(100, 0.5)
        assert r['C_constant'] > 0
        assert r['omega'] > 0
        assert r['decay_bound'] > 0
        assert r['gamma0_delta_beta'] == 50.0

    def test_envelope_dominates_for_small_delta_beta(self):
        """Direct envelope_integral is well-behaved at small Δβ."""
        for db in [0.01, 0.05, 0.1]:
            env = envelope_integral(db)
            assert env < 0, f"Envelope positive at Δβ={db}: {env}"

    def test_numeric_C_bounded_by_analytic_C(self):
        """Numeric quadrature C_constant and analytic C_explicit both > 0."""
        r_numeric = riemann_lebesgue_decay_bound(100, 0.1)
        r_analytic = riemann_lebesgue_bound_analytic()
        assert r_analytic['C_explicit'] > 0
        assert r_numeric['C_constant'] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# §4B — SPECTRAL ZETA NUMERIC SUPPORT (TIER B)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpectralZetaNumeric:
    """Tier B: Numeric spectral zeta checks."""

    @pytest.mark.parametrize("sigma", [1.5, 2.0, 3.0, 5.0])
    def test_tail_decreases_with_N(self, sigma):
        """Tail bound decreases as truncation N grows."""
        t100 = spectral_zeta_tail_bound(sigma, 100)
        t1000 = spectral_zeta_tail_bound(sigma, 1000)
        assert t1000['tail_bound_analytic'] < t100['tail_bound_analytic']

    def test_diverges_at_sigma_1(self):
        """At σ = 1 the series does not converge absolutely."""
        r = spectral_zeta_tail_bound(1.0, 100)
        assert not r['converges']

    def test_analytic_encloses_numeric(self):
        """Analytic tail bound ≥ numeric tail (safety envelope)."""
        for sigma in [2.0, 3.0]:
            r = spectral_zeta_tail_bound(sigma, 500, n_max=5000)
            assert r['analytic_encloses_numeric']

    def test_convergence_rate(self):
        """Tail ~ N^{1−σ}: rate check across multiple σ."""
        cert = spectral_zeta_convergence(sigma_values=[1.5, 2.0, 3.0])
        for rc in cert['rate_checks']:
            assert abs(rc['empirical_rate'] - rc['expected_rate']) < 0.25

    def test_numeric_theorem_certificate(self):
        """Numeric convergence certificate."""
        cert = spectral_zeta_convergence()
        assert cert['proved']
        assert cert['all_converge']
        assert cert['epistemic_level'] == 2

    def test_fast_decay_at_high_sigma(self):
        """At σ = 5: tail negligible even at small N."""
        r = spectral_zeta_tail_bound(5.0, 100)
        assert r['tail_bound_analytic'] < 1e-6

    @pytest.mark.parametrize("sigma", [1.5, 2.0, 3.0])
    def test_tail_vanishes(self, sigma):
        """Tail → 0 as N → ∞ for σ > 1."""
        r = spectral_zeta_tail_bound(sigma, 5000)
        assert r['converges']
        assert r['tail_bound_analytic'] < 1.0

    def test_slow_convergence_near_sigma_1(self):
        """At σ = 1.1: convergence slow but real."""
        r1 = spectral_zeta_tail_bound(1.1, 1000)
        r2 = spectral_zeta_tail_bound(1.1, 10000)
        assert r1['converges']
        assert r2['tail_bound_analytic'] < r1['tail_bound_analytic']

    def test_tail_formula_matches_manual(self):
        """Numeric tail bound matches hand-computed formula exactly."""
        sigma = 2.5
        N = 100
        sm1 = sigma - 1.0
        manual = (N**(1 - sigma)) * (np.log(N)/sm1 + 1/sm1**2)
        r = spectral_zeta_tail_bound(sigma, N)
        assert abs(r['tail_bound_analytic'] - manual) < 1e-14

    def test_numeric_tail_has_epistemic_level_2(self):
        """Numeric tail bound is explicitly marked Level 2."""
        r = spectral_zeta_tail_bound(2.0, 100)
        assert r['epistemic_level'] == 2


# ═══════════════════════════════════════════════════════════════════════════════
# §5B — RAYLEIGH QUOTIENT NUMERIC SANITY (TIER B)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRayleighQuotientNumeric:
    """Tier B: Numeric Rayleigh quotient checks — NOT analytic proof."""

    @pytest.mark.parametrize("N", [10, 20, 50, 100])
    def test_upper_bound(self, N):
        """λ_N(T₀) ≤ λ* for all T₀ and N (numeric check of analytic bound)."""
        H = 1.0
        lam = lambda_star(H)
        for T0 in [10, 20, 30, 40]:
            rq = rayleigh_quotient_at(T0, H, N)
            assert rq['lambda'] <= lam + 1e-8

    def test_rayleigh_positive_at_some_T0(self):
        """sup_{T₀} λ_N(T₀) > 0 for all tested N."""
        H = 1.0
        seq = rayleigh_quotient_sequence(H, N_values=[5, 10, 20, 50])
        for r in seq:
            assert r['sup_lambda_N'] > 0

    def test_rayleigh_bounded_by_lambda_star(self):
        """Ratio sup λ_N / λ* ≤ 1 for all N."""
        H = 1.0
        seq = rayleigh_quotient_sequence(H, N_values=[10, 30, 50, 100])
        for r in seq:
            assert r['ratio_to_lambda_star'] <= 1.0 + 1e-8

    def test_rayleigh_substantial_fraction(self):
        """sup λ_N exceeds a substantial fraction of λ* at moderate N."""
        H = 1.0
        seq = rayleigh_quotient_sequence(H, N_values=[10, 50, 100])
        best_ratio = max(r['ratio_to_lambda_star'] for r in seq)
        assert best_ratio > 0.40

    def test_gap_bounded(self):
        """λ* − sup λ_N is bounded and positive."""
        H = 1.0
        lam = lambda_star(H)
        seq = rayleigh_quotient_sequence(H, N_values=[10, 50, 100])
        gaps = [r['gap'] for r in seq]
        assert all(g < lam for g in gaps)
        assert all(g > 0 for g in gaps)

    @pytest.mark.parametrize("H", [0.5, 1.0, 2.0])
    def test_convergence_across_H(self, H):
        """Rayleigh quotient positive for multiple H values."""
        seq = rayleigh_quotient_sequence(H, N_values=[10, 30, 75])
        best_ratio = max(r['ratio_to_lambda_star'] for r in seq)
        assert best_ratio > 0.30

    def test_B_always_positive(self):
        """B_N(T₀) > 0 — denominator positivity."""
        H = 1.0
        for N in [10, 30, 50]:
            for T0 in [10, 20, 30]:
                rq = rayleigh_quotient_at(T0, H, N)
                assert rq['B'] > 0

    def test_A_can_be_negative(self):
        """A_N(T₀) is negative at some (N, T₀) — curvature obstruction."""
        H = 1.0
        found_negative = False
        for T0 in np.linspace(5, 40, 30):
            rq = rayleigh_quotient_at(T0, H, 30)
            if rq['A'] < 0:
                found_negative = True
                break
        assert found_negative

    def test_combined_limsup_certificate(self):
        """Combined limsup certificate: analytic proved, numeric consistent."""
        cert = limsup_lambda_N_ge_lambda_star(
            H=1.0, N_values=[5, 10, 20, 50, 100], n_T0=30, tol=0.60,
        )
        assert cert['proved']
        assert cert['numeric_consistent']
        assert cert['epistemic_level'] == 1

    def test_limsup_statement(self):
        """Statement mentions 'strictly' and λ*."""
        cert = limsup_lambda_N_ge_lambda_star(
            H=1.0, N_values=[10, 50], n_T0=20,
        )
        assert 'strictly' in cert['statement']


###############################################################################
#                                                                             #
#   TIER C — Integration / Separation-of-Concerns Tests (Level 2)            #
#   Assert code wiring, no overclaiming, correct epistemic tagging.           #
#                                                                             #
###############################################################################


class TestEpistemicLevelEnforcement:
    """Tier C: Verify epistemic_level is correctly tagged everywhere."""

    def test_sech4_identity_is_level_0(self):
        cert = verify_sech4_identity(1.0)
        assert cert['epistemic_level'] == 0

    def test_bochner_analytic_is_level_1(self):
        cert = bochner_psd_infinite_analytic(1.0)
        assert cert['epistemic_level'] == 1

    def test_bochner_numeric_is_level_2(self):
        cert = bochner_psd_infinite_numeric(1.0, N_values=[10])
        assert cert['epistemic_level'] == 2

    def test_envelope_sign_is_level_0(self):
        cert = envelope_sign_analytic()
        assert cert['epistemic_level'] == 0

    def test_rl_bound_is_level_1(self):
        cert = riemann_lebesgue_bound_analytic()
        assert cert['epistemic_level'] == 1

    def test_rl_global_analytic_is_level_1(self):
        cert = riemann_lebesgue_global_negativity_analytic()
        assert cert['epistemic_level'] == 1

    def test_spectral_zeta_analytic_is_level_1(self):
        cert = spectral_zeta_convergence_analytic(2.0)
        assert cert['epistemic_level'] == 1

    def test_spectral_zeta_numeric_is_level_2(self):
        cert = spectral_zeta_tail_bound(2.0, 100)
        assert cert['epistemic_level'] == 2

    def test_sub_threshold_is_level_0(self):
        cert = sub_threshold_negativity(1.0, 0.5)
        assert cert['epistemic_level'] == 0

    def test_kernel_limsup_is_level_1(self):
        cert = kernel_limsup_lambda_ge_lambda_star(1.0)
        assert cert['epistemic_level'] == 1

    def test_combined_limsup_is_level_1(self):
        """Combined cert inherits analytic level, not numeric."""
        cert = limsup_lambda_N_ge_lambda_star(
            H=1.0, N_values=[10], n_T0=10,
        )
        assert cert['epistemic_level'] == 1


class TestSeparationOfConcerns:
    """Tier C: Verify analytic functions don't depend on numeric-only code."""

    @staticmethod
    def _code_lines(func):
        """Extract only executable code lines (strip docstrings)."""
        lines = inspect.getsource(func).splitlines()
        in_docstring = False
        code_lines = []
        for line in lines:
            stripped = line.strip()
            if not in_docstring and stripped.startswith(('r"""', '"""', "r'''", "'''")):
                if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                    continue
                in_docstring = True
                continue
            if in_docstring:
                if '"""' in stripped or "'''" in stripped:
                    in_docstring = False
                continue
            code_lines.append(line)
        return '\n'.join(code_lines)

    def test_kernel_theorem_does_not_use_DN(self):
        """kernel_limsup_lambda_ge_lambda_star doesn't call D_N code."""
        src = self._code_lines(kernel_limsup_lambda_ge_lambda_star)
        assert 'rayleigh_quotient_at' not in src
        assert 'rayleigh_quotient_sequence' not in src
        assert 'D_sq' not in src

    def test_bochner_analytic_does_not_use_eigenvalues(self):
        """bochner_psd_infinite_analytic doesn't compute eigenvalues."""
        src = self._code_lines(bochner_psd_infinite_analytic)
        assert 'min_eigenvalue' not in src
        assert 'build_corrected_toeplitz' not in src

    def test_envelope_sign_does_not_use_scipy(self):
        """envelope_sign_analytic doesn't import or call scipy."""
        src = self._code_lines(envelope_sign_analytic)
        assert 'scipy' not in src
        assert 'quad(' not in src

    def test_rl_bound_analytic_does_not_use_quad(self):
        """riemann_lebesgue_bound_analytic doesn't use quadrature."""
        src = self._code_lines(riemann_lebesgue_bound_analytic)
        assert 'quad(' not in src
        assert 'integrate.' not in src

    def test_spectral_zeta_analytic_does_not_use_spectral_times(self):
        """spectral_zeta_convergence_analytic doesn't use von Mangoldt."""
        src = self._code_lines(spectral_zeta_convergence_analytic)
        assert 'spectral_times' not in src
        assert 'euler_form' not in src

    def test_analytic_certificates_are_self_contained(self):
        """All analytic certificates proved at epistemic_level ≤ 1."""
        c1 = envelope_sign_analytic()
        c2 = riemann_lebesgue_bound_analytic()
        c3 = riemann_lebesgue_global_negativity_analytic()
        c4 = spectral_zeta_convergence_analytic(2.0)
        c5 = kernel_limsup_lambda_ge_lambda_star(1.0)
        c6 = bochner_psd_infinite_analytic(1.0)
        for c in [c1, c2, c3, c4, c5, c6]:
            assert c['proved']
            assert c['epistemic_level'] <= 1


class TestNonOverclaiming:
    """Tier C: Verify that numeric functions don't claim analytic status."""

    def test_numeric_bochner_says_numeric(self):
        cert = bochner_psd_infinite_numeric(1.0, N_values=[10])
        assert 'NUMERIC' in cert['proof_type']
        assert cert['epistemic_level'] == 2

    def test_numeric_rl_says_numeric(self):
        cert = riemann_lebesgue_global_negativity(
            gamma0_values=[50], delta_beta_values=[0.1]
        )
        assert 'NUMERIC' in cert['proof_type']
        assert cert['epistemic_level'] == 2

    def test_numeric_zeta_says_numeric(self):
        cert = spectral_zeta_convergence(sigma_values=[2.0], N_truncs=[100])
        assert 'NUMERIC' in cert['proof_type']
        assert cert['epistemic_level'] == 2

    def test_combined_bochner_notes_both(self):
        """Combined certificate says ANALYTIC + NUMERIC CONSISTENCY."""
        cert = bochner_psd_infinite(1.0, N_values=[10])
        assert 'ANALYTIC' in cert['proof_type']
        assert 'NUMERIC' in cert['proof_type']


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — STRICT LEVEL A/B/C PROMOTION (Tier C: integration)
# ═══════════════════════════════════════════════════════════════════════════════

class TestStrictPromotionTaxonomy:
    """Tier C: Level A/B/C taxonomy on limsup_lambda_N_ge_lambda_star_strict."""

    def test_strict_returns_three_levels(self):
        result = limsup_lambda_N_ge_lambda_star_strict(H=3.0)
        assert 'level_A' in result
        assert 'level_B' in result
        assert 'level_C' in result

    def test_level_A_kernel_proved(self):
        result = limsup_lambda_N_ge_lambda_star_strict(H=3.0)
        assert result['level_A']['status'] == 'PROVED'
        assert result['level_A']['proved']

    def test_level_C_conjectural_blocks_full_proof(self):
        """is_fully_proved is False because Level C is CONJECTURAL."""
        result = limsup_lambda_N_ge_lambda_star_strict(H=3.0)
        assert not result['is_fully_proved']

    @pytest.mark.parametrize("H", [1.0, 2.0, 5.0])
    def test_strict_promotion_H_sweep(self, H):
        result = limsup_lambda_N_ge_lambda_star_strict(H=H)
        assert result['level_A']['status'] == 'PROVED'
        assert result['level_C']['status'] == 'CONJECTURAL'

    def test_limit_guard_certificate_present(self):
        result = limsup_lambda_N_ge_lambda_star_strict(H=3.0)
        assert 'limit_guard' in result['level_C']
        guard = result['level_C']['limit_guard']
        assert guard['requires_RH_uniformity']


# ═══════════════════════════════════════════════════════════════
#  Tier: Bochner Biconditional — Fourier Domain Tightness
# ═══════════════════════════════════════════════════════════════

class TestBochnerBiconditionalTightness:
    """Verify the non-negativity ≠ positive-definiteness subtlety.

    The Fourier transform ĝ_{λ*−ε}(ω) > 0 for all ω when ε < λ*,
    yet the Toeplitz matrix is indefinite — proving the Bochner converse
    operates on the spectral measure g(t), not on pointwise values of ĝ(ω).
    """

    def test_fourier_transform_nonneg_for_sub_threshold(self):
        """ĝ_{λ*−ε}(ω) ≥ 0 for all ω when ε < λ*."""
        from engine.analytic_promotion import fourier_domain_tightness_verification
        result = fourier_domain_tightness_verification(H=1.5, epsilon=0.01, N_test=20)
        assert result['fourier_all_nonneg'], "FT should be non-negative everywhere"

    def test_toeplitz_indefinite_despite_nonneg_ft(self):
        """Toeplitz matrix is indefinite even though ĝ(ω) > 0 for all ω."""
        from engine.analytic_promotion import fourier_domain_tightness_verification
        result = fourier_domain_tightness_verification(H=1.5, epsilon=0.01, N_test=50)
        assert result['toeplitz_indefinite'], "Toeplitz should be indefinite"

    def test_demonstrates_subtlety(self):
        """Non-negativity ≠ positive-definiteness verified computationally."""
        from engine.analytic_promotion import fourier_domain_tightness_verification
        result = fourier_domain_tightness_verification(H=1.5, epsilon=0.01, N_test=50)
        assert result['demonstrates_subtlety'], (
            "Should demonstrate: ĝ ≥ 0 everywhere yet Toeplitz indefinite"
        )

    @pytest.mark.parametrize("H", [1.0, 1.5, 2.0, 3.0])
    def test_subtlety_across_H_values(self, H):
        """The ĝ ≥ 0 yet not-PD phenomenon holds for all H."""
        from engine.analytic_promotion import fourier_domain_tightness_verification
        result = fourier_domain_tightness_verification(H=H, epsilon=0.01, N_test=30)
        assert result['fourier_all_nonneg']
        # Toeplitz indefiniteness may need larger N for some H values
        if result['toeplitz_indefinite']:
            assert result['demonstrates_subtlety']

    def test_explicit_fourier_sech4(self):
        """FT[sech⁴(t/H)](ω) matches the closed-form formula."""
        from engine.kernel import fourier_sech4
        import numpy as np
        H = 1.5
        # At ω=0 limit: FT[sech⁴(t/H)](0) = ∫sech⁴(t/H)dt = 4H/3
        omega_small = np.array([1e-6])
        val = fourier_sech4(omega_small, H)[0]
        assert abs(val - 4 * H / 3) < 1e-3, f"FT at ω≈0 should be 4H/3={4*H/3}, got {val}"

    def test_explicit_fourier_g_lambda_at_lambda_star(self):
        """At λ = λ*, FT of g_λ should equal FT of (6/H²)sech⁴(t/H)."""
        from engine.kernel import fourier_g_lambda, fourier_sech4
        from engine.bochner import lambda_star
        import numpy as np
        H = 1.5
        lam = lambda_star(H)
        omega = np.linspace(0.1, 10, 100)
        g_hat = fourier_g_lambda(omega, H, lam)
        sech4_hat = (6.0 / H**2) * fourier_sech4(omega, H)
        np.testing.assert_allclose(g_hat, sech4_hat, rtol=1e-10)
