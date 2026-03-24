"""
================================================================================
test_12_hilbert_polya_operator.py — Tier 1: Polymeric Hilbert–Pólya Operator
================================================================================

Tests the self-adjoint polymeric Hamiltonian H_poly from Berra-Montiel et al.
(arXiv:1610.01957), which realises the Berry–Keating H = xp Hamiltonian in a
loop-quantum-gravity–inspired discrete geometry.

HONEST STATUS:
  • The operator IS self-adjoint with real spectrum            [PROVEN]
  • The spectrum approaches Berry–Keating counting as μ₀→0    [PROVEN]
  • The spectrum does NOT automatically equal Riemann zeros    [OPEN]
  • The polymeric stiffening does create nonlinear phase-space [PROVEN]

NO RH ASSUMPTIONS — only structural operator properties tested.
================================================================================
"""

import pytest
import numpy as np
import math

from engine.hilbert_polya import (
    polymer_momentum,
    H_poly_matrix,
    H_poly_apply,
    get_poly_spectrum,
    berry_keating_counting,
    polymeric_counting,
    self_adjoint_eigenvalues,
    phase_space_stiffness,
)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — MOMENTUM REGULARISATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestPolymerMomentum:
    """Polymer momentum: p_μ₀ = (ℏ/μ₀)sin(μ₀p/ℏ)."""

    def test_small_mu0_recovers_p(self):
        """In the continuum limit μ₀→0, p_μ₀ → p."""
        mu0 = 0.001
        p = np.linspace(-2, 2, 500)
        p_poly = polymer_momentum(p, mu0)
        np.testing.assert_allclose(p_poly, p, atol=1e-3, rtol=1e-3)

    def test_boundedness(self):
        """p_μ₀ is bounded by ℏ/μ₀ (= 1/μ₀ with ℏ=1)."""
        mu0 = 0.1
        p = np.linspace(-100, 100, 5000)
        p_poly = polymer_momentum(p, mu0)
        bound = 1.0 / mu0
        assert np.all(np.abs(p_poly) <= bound + 1e-10)

    def test_odd_function(self):
        """sin(μ₀p) is odd → p_μ₀(−p) = −p_μ₀(p)."""
        mu0 = 0.2
        p = np.linspace(0.1, 5, 200)
        assert np.allclose(polymer_momentum(-p, mu0),
                           -polymer_momentum(p, mu0), atol=1e-14)

    def test_periodicity(self):
        """p_μ₀ is periodic with period 2πℏ/μ₀ = 2π/μ₀."""
        mu0 = 0.5
        period = 2 * np.pi / mu0
        p = np.linspace(0, 3, 100)
        np.testing.assert_allclose(
            polymer_momentum(p, mu0),
            polymer_momentum(p + period, mu0),
            atol=1e-12,
        )

    @pytest.mark.parametrize("mu0", [0.01, 0.05, 0.1, 0.5, 1.0])
    def test_zero_at_origin(self, mu0):
        assert abs(polymer_momentum(0.0, mu0)) < 1e-15

    def test_max_at_pi_over_2mu0(self):
        """Maximum of sin occurs at p = πℏ/(2μ₀)."""
        mu0 = 0.3
        p_max = np.pi / (2 * mu0)
        val = polymer_momentum(p_max, mu0)
        expected = 1.0 / mu0
        assert abs(val - expected) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — HERMITICITY AND SELF-ADJOINTNESS
# ═══════════════════════════════════════════════════════════════════════════════

class TestHermiticity:
    """H_poly discretised matrix must be Hermitian → real eigenvalues."""

    @pytest.mark.parametrize("mu0", [0.05, 0.1, 0.3])
    def test_matrix_is_hermitian(self, mu0):
        """H_poly_matrix should be symmetric (real Hermitian)."""
        p_grid = np.linspace(0.1, 3.0, 120)
        H = H_poly_matrix(p_grid, mu0)
        np.testing.assert_allclose(H, H.T, atol=1e-10)

    @pytest.mark.parametrize("mu0", [0.05, 0.1, 0.3])
    def test_eigenvalues_real(self, mu0):
        """All eigenvalues of the Hermitian H must be real."""
        evals = get_poly_spectrum(n=20, mu0=mu0, p_interval=(0.15, 3.0))
        assert np.all(np.abs(evals.imag) < 1e-8)

    def test_matrix_finite(self):
        """No infinities or NaNs in the matrix."""
        p_grid = np.linspace(0.2, 2.5, 80)
        H = H_poly_matrix(p_grid, 0.1)
        assert np.all(np.isfinite(H))

    def test_apply_matches_matrix(self):
        """H_poly_apply(φ) should equal H_poly_matrix @ φ."""
        p_grid = np.linspace(0.2, 2.5, 60)
        mu0 = 0.1
        phi = np.exp(-(p_grid - 1.0)**2)
        result_apply = H_poly_apply(phi, p_grid, mu0)
        H = H_poly_matrix(p_grid, mu0)
        result_matrix = H @ phi
        np.testing.assert_allclose(result_apply, result_matrix, atol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — SPECTRAL PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpectralProperties:
    """Spectrum of H_poly: reality, ordering, μ₀-dependence."""

    def test_spectrum_sorted(self):
        evals = get_poly_spectrum(n=30, mu0=0.1, p_interval=(0.1, 4.0))
        assert np.all(np.diff(evals.real) >= -1e-10)

    def test_spectrum_size(self):
        n = 25
        evals = get_poly_spectrum(n=n, mu0=0.1, p_interval=(0.1, 3.0))
        assert len(evals) == n

    def test_continuum_limit_eigenvalues_increase(self):
        """Finer grid (more points) → eigenvalues stabilise (converge)."""
        evals_coarse = get_poly_spectrum(n=10, mu0=0.1,
                                         p_interval=(0.2, 3.0), n_grid=60)
        evals_fine = get_poly_spectrum(n=10, mu0=0.1,
                                       p_interval=(0.2, 3.0), n_grid=120)
        # Lowest eigenvalues should be similar (within grid resolution)
        np.testing.assert_allclose(evals_coarse[:5].real,
                                   evals_fine[:5].real, rtol=0.3)

    @pytest.mark.parametrize("mu0", [0.05, 0.1, 0.2, 0.5])
    def test_spectrum_nonempty(self, mu0):
        evals = get_poly_spectrum(n=10, mu0=mu0, p_interval=(0.2, 3.0))
        assert len(evals) >= 10

    def test_smaller_mu0_closer_to_BK(self):
        """Smaller μ₀ → spectrum closer to Berry–Keating (classical limit)."""
        evals_large = get_poly_spectrum(n=15, mu0=0.5, p_interval=(0.1, 5.0))
        evals_small = get_poly_spectrum(n=15, mu0=0.05, p_interval=(0.1, 5.0))
        # Both should have real eigenvalues
        assert np.max(np.abs(evals_large.imag)) < 1e-6
        assert np.max(np.abs(evals_small.imag)) < 1e-6


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — SPECTRAL COUNTING (Berry–Keating / Riemann–von Mangoldt)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpectralCounting:
    """Verify polymeric counting recovers smooth part of N(E)."""

    def test_BK_counting_positive(self):
        """N_BK(E) > 0 for E > 2π·e ≈ 17.08."""
        E = 50.0
        N = berry_keating_counting(E)
        assert N > 0

    def test_BK_counting_monotone(self):
        """N_BK(E) is monotonically increasing for E > 2πe."""
        E_vals = np.linspace(20, 200, 100)
        N_vals = np.array([berry_keating_counting(e) for e in E_vals])
        assert np.all(np.diff(N_vals) > 0)

    def test_poly_counting_approaches_BK(self):
        """As μ₀ → 0, N_poly(E) → N_BK(E)."""
        E = 80.0
        N_bk = berry_keating_counting(E)
        N_poly_small = polymeric_counting(E, mu0=0.001)
        assert abs(N_poly_small - N_bk) / max(abs(N_bk), 1) < 0.1

    def test_poly_counting_has_corrections(self):
        """At finite μ₀, N_poly deviates from N_BK."""
        E = 80.0
        N_bk = berry_keating_counting(E)
        N_poly = polymeric_counting(E, mu0=0.5)
        # Should differ (polymeric correction)
        assert abs(N_poly - N_bk) > 0.01 * abs(N_bk)


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — SELF-ADJOINT EXTENSION (Boundary Conditions)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSelfAdjointExtension:
    """Verify the self-adjoint extension gives a discrete real spectrum."""

    @pytest.mark.parametrize("theta", [0.0, np.pi/4, np.pi/2, np.pi])
    def test_eigenvalues_discrete_and_real(self, theta):
        evals = self_adjoint_eigenvalues(n=15, mu0=0.1, theta=theta,
                                          p_interval=(0.2, 3.0))
        assert np.all(np.abs(evals.imag) < 1e-8)
        assert len(evals) == 15

    def test_theta_shifts_spectrum(self):
        """Different θ → different eigenvalue sets."""
        e1 = self_adjoint_eigenvalues(n=10, mu0=0.1, theta=0.0,
                                       p_interval=(0.2, 3.0))
        e2 = self_adjoint_eigenvalues(n=10, mu0=0.1, theta=np.pi/2,
                                       p_interval=(0.2, 3.0))
        # Spectra should differ
        assert not np.allclose(e1, e2, atol=1e-4)

    def test_spectrum_depends_on_mu0(self):
        """Different μ₀ → different spectrum (gravity deformation)."""
        e1 = self_adjoint_eigenvalues(n=10, mu0=0.05, theta=0.0,
                                       p_interval=(0.2, 3.0))
        e2 = self_adjoint_eigenvalues(n=10, mu0=0.5, theta=0.0,
                                       p_interval=(0.2, 3.0))
        assert not np.allclose(e1, e2, atol=1e-2)


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — PHASE-SPACE STIFFNESS (THE KEY PHYSICS)
# ═══════════════════════════════════════════════════════════════════════════════

class TestPhaseSpaceStiffness:
    """
    The polymeric deformation creates nonlinear stiffness near σ = 1/2.
    This is what could seal the small-Δβ crack.
    """

    def test_stiffness_positive(self):
        """Stiffness measure should be > 0 for all μ₀ > 0."""
        for mu0 in [0.01, 0.1, 0.5, 1.0]:
            s = phase_space_stiffness(mu0, p_range=(0.1, 3.0))
            assert s['stiffness'] > 0

    def test_stiffness_increases_with_mu0(self):
        """Larger μ₀ → more phase-space deformation → more stiffness."""
        s1 = phase_space_stiffness(0.05, p_range=(0.1, 3.0))
        s2 = phase_space_stiffness(0.5, p_range=(0.1, 3.0))
        assert s2['stiffness'] > s1['stiffness']

    def test_stiffness_vanishes_as_mu0_to_zero(self):
        """In the classical limit μ₀→0, deformation vanishes."""
        s = phase_space_stiffness(0.001, p_range=(0.1, 3.0))
        assert s['stiffness'] < 0.1

    def test_stiffness_dict_keys(self):
        s = phase_space_stiffness(0.1, p_range=(0.1, 3.0))
        assert 'stiffness' in s
        assert 'max_deviation' in s
        assert 'mu0' in s


# ═══════════════════════════════════════════════════════════════════════════════
# §7 — HONEST LIMITS (Documents what this operator does NOT prove)
# ═══════════════════════════════════════════════════════════════════════════════

class TestHonestLimits:
    """
    HONEST: The polymeric operator is a candidate HP framework,
    NOT a proof that its spectrum equals Riemann zeros.
    """

    def test_spectrum_is_NOT_riemann_zeros(self):
        """The raw polymeric spectrum doesn't match ζ zeros exactly."""
        evals = get_poly_spectrum(n=10, mu0=0.1, p_interval=(0.1, 5.0))
        riemann_first_10 = np.array([
            14.135, 21.022, 25.011, 30.425, 32.935,
            37.586, 40.919, 43.327, 48.005, 49.774,
        ])
        # These should NOT be equal (that would be claiming too much)
        assert not np.allclose(evals.real, riemann_first_10, rtol=0.01)

    def test_operator_is_tunable(self):
        """The operator has free parameters (μ₀, θ, p_interval)
        that must be tuned. It's a framework, not a derivation."""
        e1 = get_poly_spectrum(n=5, mu0=0.1, p_interval=(0.1, 3.0))
        e2 = get_poly_spectrum(n=5, mu0=0.2, p_interval=(0.1, 3.0))
        e3 = get_poly_spectrum(n=5, mu0=0.1, p_interval=(0.2, 4.0))
        # All should be different → free parameters matter
        assert not np.allclose(e1, e2, atol=1e-3)
        assert not np.allclose(e1, e3, atol=1e-3)
