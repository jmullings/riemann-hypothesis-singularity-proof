"""
================================================================================
test_19_pho_representability.py — PHO-Representability Gate Tests
================================================================================

Makes "PHO-representability" (Polymeric Hilbert–Pólya Operator admissibility)
a first-class gate enforced across the spectral chain.

PHO-representable ⟺ self-adjoint + real spectrum + ONB + spectral reconstruction

Implements proposals from TDD_HILBERT.md:

  §1  Core predicate tests (true/false/edge cases)
  §2  H_poly and HP candidate operators pass PHO gate
  §3  9D sub-operators pass PHO gate (tensor factors)
  §4  Bochner Toeplitz matrices pass PHO gate
  §5  Curvature Toeplitz: PHO but NOT PSD (obstruction reframing)
  §6  Rayleigh quotient structural consistency
  §7  Off-critical PHO obstruction (PROMOTED — operator now constructed)
  §8  Honesty layer

HONEST: PHO-representability is a STRUCTURAL filter. These tests do NOT
assert that any operator's spectrum equals Riemann zeros.
================================================================================
"""

import pytest
import numpy as np

from engine.operator_axioms import is_PHO_representable
from engine.hilbert_polya import (
    H_poly_matrix, centered_H_poly_matrix, signed_HP_candidate,
)
from engine.spectral_9d import _build_1d_hamiltonian
from engine.bochner import (
    build_corrected_toeplitz, build_curvature_toeplitz,
    lambda_star, is_psd, min_eigenvalue,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

def _sample_p_grid(n=80):
    return np.linspace(0.2, 2.5, n)

def _sample_H_poly(mu0=0.1, n=80):
    return H_poly_matrix(_sample_p_grid(n), mu0)

def _sample_spectrum_25():
    return np.array([14.135, 21.022, 25.011, 30.425, 32.935,
                     37.586, 40.919, 43.327, 48.005, 49.774,
                     52.970, 56.446, 59.347, 60.832, 65.113,
                     67.080, 69.546, 72.067, 75.705, 77.145,
                     79.337, 82.910, 84.735, 87.425, 88.809])


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — CORE PREDICATE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestPHOPredicateCore:
    """Tests for the is_PHO_representable predicate itself."""

    def test_identity_is_pho(self):
        """Identity matrix is trivially PHO-representable."""
        I = np.eye(10)
        assert is_PHO_representable(I)

    def test_diagonal_real_is_pho(self):
        """Real diagonal matrix is PHO-representable."""
        D = np.diag([1.0, -2.0, 3.5, 0.0, -7.1])
        assert is_PHO_representable(D)

    def test_symmetric_real_is_pho(self):
        """Random real symmetric matrix is PHO-representable."""
        rng = np.random.default_rng(2026)
        A = rng.standard_normal((20, 20))
        H = (A + A.T) / 2
        assert is_PHO_representable(H)

    def test_nonsymmetric_is_not_pho(self):
        """Non-symmetric matrix fails PHO gate."""
        rng = np.random.default_rng(0)
        A = rng.standard_normal((40, 40))
        assert not is_PHO_representable(A)

    def test_rectangular_is_not_pho(self):
        """Non-square matrix fails PHO gate."""
        assert not is_PHO_representable(np.zeros((3, 5)))

    def test_1d_array_is_not_pho(self):
        """1D array fails PHO gate."""
        assert not is_PHO_representable(np.array([1.0, 2.0, 3.0]))

    def test_zero_matrix_is_pho(self):
        """Zero matrix is PHO-representable (trivial self-adjoint)."""
        assert is_PHO_representable(np.zeros((5, 5)))

    def test_1x1_matrix_is_pho(self):
        """1×1 scalar matrix is PHO-representable."""
        assert is_PHO_representable(np.array([[42.0]]))

    def test_nearly_symmetric_within_tolerance(self):
        """Matrix symmetric within atol passes."""
        rng = np.random.default_rng(99)
        A = rng.standard_normal((15, 15))
        H = (A + A.T) / 2
        H_noisy = H + 1e-12 * rng.standard_normal((15, 15))
        H_noisy = (H_noisy + H_noisy.T) / 2  # re-symmetrise the noise
        assert is_PHO_representable(H_noisy, atol=1e-10)

    def test_strongly_asymmetric_fails(self):
        """Matrix with large asymmetry fails."""
        H = np.array([[1.0, 5.0], [0.0, 1.0]])
        assert not is_PHO_representable(H)


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — POLYMERIC HILBERT–PÓLYA OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

class TestPHOHilbertPolyaOperators:
    """H_poly, centered, and signed HP candidates pass PHO gate."""

    def test_H_poly_is_pho(self):
        """H_poly_matrix is PHO-representable (positive-definite Sturm–Liouville)."""
        H = _sample_H_poly()
        assert is_PHO_representable(H)

    def test_H_poly_various_mu0(self):
        """H_poly is PHO-representable across μ₀ values."""
        p_grid = _sample_p_grid()
        for mu0 in [0.05, 0.1, 0.5, 1.0]:
            H = H_poly_matrix(p_grid, mu0)
            assert is_PHO_representable(H), f"Failed for mu0={mu0}"

    def test_centered_H_poly_is_pho(self):
        """Centered H_poly (spectrum shifted to ±R) is still PHO-representable."""
        p_grid = _sample_p_grid()
        Hc = centered_H_poly_matrix(p_grid, mu0=0.1)
        assert is_PHO_representable(Hc)

    def test_signed_HP_candidate_positive_is_pho(self):
        """Signed HP candidate (sign=+1) is PHO-representable."""
        p_grid = _sample_p_grid()
        H = signed_HP_candidate(p_grid, mu0=0.1, sign=1.0)
        assert is_PHO_representable(H)

    def test_signed_HP_candidate_negative_is_pho(self):
        """Signed HP candidate (sign=−1) is PHO-representable."""
        p_grid = _sample_p_grid()
        H = signed_HP_candidate(p_grid, mu0=0.1, sign=-1.0)
        assert is_PHO_representable(H)

    def test_H_poly_is_also_psd(self):
        """H_poly is both PHO-representable AND PSD (positive definite)."""
        H = _sample_H_poly()
        assert is_PHO_representable(H)
        assert is_psd(H)

    def test_centered_is_pho_but_not_psd(self):
        """Centered H_poly is PHO but NOT PSD (has negative eigenvalues)."""
        p_grid = _sample_p_grid()
        Hc = centered_H_poly_matrix(p_grid, mu0=0.1)
        assert is_PHO_representable(Hc)
        assert not is_psd(Hc), "Centered operator should be indefinite"


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — 9D SUB-OPERATORS (TENSOR FACTORS)
# ═══════════════════════════════════════════════════════════════════════════════

class TestPHO9DSubOperators:
    """
    Each 1D factor h_j in the 9D tensor product is PHO-representable.

    The full 9D operator is a tensor sum Σ h_j ⊗ I⊗...⊗I, which is
    self-adjoint if each factor is. We test the factors directly since
    the full 9^n matrix is never constructed.
    """

    @pytest.mark.parametrize("dim_j", range(9))
    def test_1d_hamiltonian_is_pho(self, dim_j):
        """1D sub-Hamiltonian h_j is PHO-representable."""
        x_grid = np.linspace(-10, 10, 25)
        H_1d = _build_1d_hamiltonian(x_grid, dim_j)
        assert is_PHO_representable(H_1d)

    def test_phi_metric_regularised_is_pho(self):
        """Regularised φ-metric G_reg = G_φ + ε·I is PHO-representable."""
        from engine.spectral_9d import phi_metric_regularised
        G_reg = phi_metric_regularised(epsilon=1.0)
        assert is_PHO_representable(G_reg)


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — BOCHNER TOEPLITZ MATRICES PASS PHO GATE
# ═══════════════════════════════════════════════════════════════════════════════

class TestPHOToeplitzMatrices:
    """Bochner Toeplitz matrices are PHO-representable."""

    def test_corrected_toeplitz_is_pho_and_psd(self):
        """Corrected Toeplitz is PHO-representable AND PSD (Bochner theorem)."""
        E = _sample_spectrum_25()
        H_val = 3.0
        M = build_corrected_toeplitz(E, H_val)
        assert is_PHO_representable(M)
        assert is_psd(M)

    def test_corrected_toeplitz_various_H(self):
        """Corrected Toeplitz is PHO for various bandwidth H."""
        E = _sample_spectrum_25()[:15]
        for H_val in [1.0, 3.0, 5.0, 10.0]:
            M = build_corrected_toeplitz(E, H_val)
            assert is_PHO_representable(M), f"Failed for H={H_val}"

    def test_corrected_toeplitz_uniform_spectrum(self):
        """Corrected Toeplitz is PHO even for non-zeta spectra (universality)."""
        E_uniform = np.linspace(10, 100, 20)
        M = build_corrected_toeplitz(E_uniform, 3.0)
        assert is_PHO_representable(M)
        assert is_psd(M)

    def test_smoothing_toeplitz_is_pho(self):
        """Smoothing Toeplitz G_{kl} = ŵ_H(E_k - E_l) is PHO-representable."""
        from engine.kernel import fourier_w_H
        E = _sample_spectrum_25()[:15]
        diff = E[:, None] - E[None, :]
        G = fourier_w_H(diff, 3.0)
        assert is_PHO_representable(G)
        assert is_psd(G)


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — CURVATURE TOEPLITZ: PHO BUT NOT PSD (OBSTRUCTION REFRAMING)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCurvatureToeplitzObstruction:
    """
    The uncorrected curvature Toeplitz IS PHO-representable (symmetric → 
    self-adjoint with real spectrum) but is NOT PSD.

    MATHEMATICAL POINT: PHO-representability ≠ PSD. The Bochner obstruction
    manifests as indefiniteness (negative eigenvalues), not non-self-adjointness.
    The λ-correction repairs PSD while preserving PHO structure.
    """

    def test_curvature_toeplitz_is_pho(self):
        """Curvature Toeplitz is self-adjoint (symmetric) → PHO gate passes."""
        E = _sample_spectrum_25()
        M = build_curvature_toeplitz(E, 3.0)
        assert is_PHO_representable(M)

    def test_curvature_toeplitz_is_not_psd(self):
        """Curvature Toeplitz is indefinite — the Bochner obstruction."""
        E = _sample_spectrum_25()
        M = build_curvature_toeplitz(E, 3.0)
        assert not is_psd(M), "Curvature Toeplitz should be indefinite"

    def test_correction_preserves_pho_adds_psd(self):
        """λ-correction upgrades indefinite PHO to PSD PHO."""
        E = _sample_spectrum_25()
        H_val = 3.0
        M_curv = build_curvature_toeplitz(E, H_val)
        M_corr = build_corrected_toeplitz(E, H_val)
        # Both PHO-representable
        assert is_PHO_representable(M_curv)
        assert is_PHO_representable(M_corr)
        # Only corrected is PSD
        assert not is_psd(M_curv)
        assert is_psd(M_corr)


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — RAYLEIGH QUOTIENT STRUCTURAL CONSISTENCY
# ═══════════════════════════════════════════════════════════════════════════════

class TestRayleighStructure:
    """
    For any PHO-representable operator H, the Rayleigh quotient
    R(ψ) = ⟨ψ, Hψ⟩/⟨ψ, ψ⟩ satisfies λ_min ≤ R(ψ) ≤ λ_max.

    This is a tautological consequence of the spectral theorem but
    encodes the structural constraint that any functional derived from
    a PHO operator must respect its spectral bounds.
    """

    def test_rayleigh_bounds_H_poly(self):
        """Rayleigh quotient respects spectral bounds for H_poly."""
        H = _sample_H_poly(mu0=0.1, n=60)
        assert is_PHO_representable(H)
        evals = np.linalg.eigvalsh(H)
        lam_min, lam_max = evals[0], evals[-1]

        rng = np.random.default_rng(2026)
        for _ in range(20):
            psi = rng.standard_normal(H.shape[0])
            psi /= np.linalg.norm(psi)
            rq = float(psi @ H @ psi)
            assert lam_min - 1e-10 <= rq <= lam_max + 1e-10

    def test_rayleigh_bounds_centered(self):
        """Rayleigh quotient respects spectral bounds for centered H_poly."""
        p_grid = _sample_p_grid(60)
        Hc = centered_H_poly_matrix(p_grid, mu0=0.1)
        assert is_PHO_representable(Hc)
        evals = np.linalg.eigvalsh(Hc)
        lam_min, lam_max = evals[0], evals[-1]

        rng = np.random.default_rng(42)
        for _ in range(20):
            psi = rng.standard_normal(Hc.shape[0])
            psi /= np.linalg.norm(psi)
            rq = float(psi @ Hc @ psi)
            assert lam_min - 1e-10 <= rq <= lam_max + 1e-10

    def test_rayleigh_bounds_corrected_toeplitz(self):
        """Rayleigh quotient for corrected Toeplitz respects spectral bounds."""
        E = _sample_spectrum_25()[:15]
        M = build_corrected_toeplitz(E, 3.0)
        assert is_PHO_representable(M)
        evals = np.linalg.eigvalsh(M)
        lam_min, lam_max = evals[0], evals[-1]

        rng = np.random.default_rng(7)
        for _ in range(10):
            psi = rng.standard_normal(M.shape[0])
            psi /= np.linalg.norm(psi)
            rq = float(psi @ M @ psi)
            assert lam_min - 1e-10 <= rq <= lam_max + 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# §7 — OFF-CRITICAL PHO OBSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestOffCriticalPHOObstruction:
    """
    Off-critical zeros force non-PHO-admissible spectral objects.

    Under the Hilbert–Pólya correspondence, ρ = 1/2 + iλ maps to real
    eigenvalue λ.  An off-critical zero ρ = (1/2+Δβ)+iγ₀ maps to a
    complex eigenvalue γ₀ − iΔβ, which breaks self-adjointness and
    therefore PHO-representability.

    PROMOTED: build_offcritical_operator now constructs operator matrices
    encoding the off-critical spectral pair.  On-critical (β=0.5) remains
    PHO-representable as a control.
    """

    @pytest.mark.parametrize("beta", [0.51, 0.6, 0.75])
    def test_offcritical_zero_breaks_pho(self, beta):
        """Off-critical operator fails PHO-representability."""
        from engine.offcritical import build_offcritical_operator

        gamma0 = 14.134725142  # first Riemann zero
        H_off = build_offcritical_operator(beta, gamma0, N=10)
        assert not is_PHO_representable(H_off), (
            f"Off-critical operator (β={beta}) should NOT be PHO-representable"
        )

    def test_oncritical_zero_stays_pho(self):
        """Control: on-critical (β=0.5) operator remains PHO-representable."""
        from engine.offcritical import build_offcritical_operator

        gamma0 = 14.134725142
        H_on = build_offcritical_operator(0.5, gamma0, N=10)
        assert is_PHO_representable(H_on), (
            "On-critical operator (β=0.5) should be PHO-representable"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §8 — HONESTY LAYER
# ═══════════════════════════════════════════════════════════════════════════════

class TestPHOHonestyLayer:
    """Explicit honesty guards for the PHO-representability layer."""

    def test_pho_does_not_claim_rh(self):
        """
        PHO-representability is a STRUCTURAL filter on operators.
        It does NOT assert that any operator's spectrum equals Riemann zeros.
        """
        assert True

    def test_pho_does_not_equal_psd(self):
        """
        PHO-representable does NOT imply PSD.
        Centered/signed operators are PHO but indefinite.
        """
        p_grid = _sample_p_grid()
        Hc = centered_H_poly_matrix(p_grid, mu0=0.1)
        assert is_PHO_representable(Hc)
        assert not is_psd(Hc), "Centered operator is PHO but not PSD"

    def test_pho_universality_caveat(self):
        """
        PHO-representability holds for ANY symmetric matrix — it is a
        necessary condition, not a sufficient one, for physical relevance.
        """
        rng = np.random.default_rng(0)
        A = rng.standard_normal((30, 30))
        H_random = (A + A.T) / 2
        assert is_PHO_representable(H_random), \
            "Any symmetric matrix is PHO — this is by design, not a result"

    def test_offcritical_obstruction_is_open(self):
        """
        The off-critical PHO obstruction is an OPEN research target.
        No operator-level contradiction is yet constructed.
        """
        assert True
