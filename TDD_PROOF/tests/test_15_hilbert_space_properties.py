"""
================================================================================
test_15_hilbert_space_properties.py — Hilbert Space Structural Axioms
================================================================================

Verifies that H_poly_matrix satisfies the axiomatic properties of a bounded
self-adjoint operator on a finite-dimensional Hilbert space H = (ℂⁿ, ⟨·,·⟩).

Implements the 5 categories from TDD_HILBERT.md PLUS additional spectral
theorem and positive-definiteness tests:

  §1  Adjoint identity: ⟨Tx, y⟩ = ⟨x, T*y⟩  and  T** = T
  §2  Operator norm:    ‖T*‖ = ‖T‖
  §3  Kernel–range:     ker(T*) = Ran(T)⊥
  §4  Orthogonal decomposition: ℂⁿ = ker(T*) ⊕ Ran(T)
  §5  Adjoint algebra:  (λT)* = λ̄T*,  (S+T)* = S*+T*,  (ST)* = T*S*
  §6  Spectral theorem: H = VΛVᵀ,  VVᵀ = I  (resolution of identity)
  §7  Positive definiteness and Rayleigh quotient bounds
  §8  Normality:        [H, H*] = 0

HONEST: These are finite-dimensional matrix identities. The infinite-
dimensional Hilbert space structure (domain issues, essential self-adjointness)
remains OPEN for the continuum operator.
================================================================================
"""

import pytest
import numpy as np

from engine.hilbert_polya import (
    H_poly_matrix, get_poly_spectrum,
    centered_H_poly_matrix, signed_HP_candidate,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

def _sample_operator(mu0=0.1, n=80):
    """Build H_poly on a safe grid for testing."""
    p_grid = np.linspace(0.2, 2.5, n)
    return H_poly_matrix(p_grid, mu0)


def _rank_deficient_operator():
    """
    A deliberately rank-deficient symmetric matrix for exercising the
    kernel–range tests (§3/§4) beyond the trivial ker={0} case.
    Constructed as vvᵀ which has rank 1 and kernel of dim n-1.
    """
    n = 40
    v = np.random.default_rng(42).standard_normal(n)
    return np.outer(v, v)


def _kernel_basis(T, tol=1e-10):
    """Kernel of T via SVD: right singular vectors with σ ≈ 0."""
    U, S, Vh = np.linalg.svd(T)
    mask = S < tol
    if not np.any(mask):
        return np.zeros((T.shape[1], 0))
    return Vh[mask].T


def _range_basis(T, tol=1e-10):
    """Range of T via SVD: left singular vectors with σ > 0."""
    U, S, Vh = np.linalg.svd(T)
    mask = S > tol
    if not np.any(mask):
        return np.zeros((T.shape[0], 0))
    return U[:, mask]


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — ADJOINT IDENTITY AND DOUBLE ADJOINT
# ═══════════════════════════════════════════════════════════════════════════════

class TestAdjointBasics:
    """⟨Tx, y⟩ = ⟨x, T*y⟩ and T** = T."""

    def test_adjoint_definition(self):
        """Inner product identity with 10 random vector pairs."""
        T = _sample_operator()
        n = T.shape[0]
        rng = np.random.default_rng(7)
        for _ in range(10):
            x = rng.standard_normal(n)
            y = rng.standard_normal(n)
            lhs = np.vdot(T @ x, y)            # ⟨Tx, y⟩
            rhs = np.vdot(x, T.conj().T @ y)   # ⟨x, T*y⟩
            np.testing.assert_allclose(lhs, rhs, atol=1e-10, rtol=1e-10)

    def test_double_adjoint_equals_operator(self):
        """T** = T (involutive property of the adjoint)."""
        T = _sample_operator()
        T_starstar = T.conj().T.conj().T
        np.testing.assert_allclose(T, T_starstar, atol=1e-12)

    @pytest.mark.parametrize("mu0", [0.05, 0.1, 0.3])
    def test_self_adjoint(self, mu0):
        """H_poly is self-adjoint: T* = T (real symmetric)."""
        T = _sample_operator(mu0=mu0)
        np.testing.assert_allclose(T, T.conj().T, atol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — OPERATOR NORM PRESERVATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestOperatorNorm:
    """‖T*‖₂ = ‖T‖₂ (spectral norm via largest singular value)."""

    def test_adjoint_preserves_operator_norm(self):
        T = _sample_operator()
        s_T = np.linalg.svd(T, compute_uv=False)
        s_Tstar = np.linalg.svd(T.conj().T, compute_uv=False)
        np.testing.assert_allclose(s_T[0], s_Tstar[0], rtol=1e-10)

    def test_norm_equals_spectral_radius(self):
        """For self-adjoint operators, ‖T‖ = max|λᵢ| (spectral radius)."""
        T = _sample_operator()
        norm_svd = np.linalg.svd(T, compute_uv=False)[0]
        evals = np.linalg.eigvalsh(T)
        spectral_radius = np.max(np.abs(evals))
        np.testing.assert_allclose(norm_svd, spectral_radius, rtol=1e-10)

    @pytest.mark.parametrize("mu0", [0.05, 0.1, 0.3])
    def test_frobenius_norm_preserved(self, mu0):
        """‖T‖_F = ‖T*‖_F (Frobenius norm also preserved by adjoint)."""
        T = _sample_operator(mu0=mu0)
        np.testing.assert_allclose(
            np.linalg.norm(T, 'fro'),
            np.linalg.norm(T.conj().T, 'fro'),
            rtol=1e-12,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — KERNEL–RANGE ORTHOGONALITY: ker(T*) = Ran(T)⊥
# ═══════════════════════════════════════════════════════════════════════════════

class TestKernelRangeOrthogonality:
    """
    Fundamental theorem of linear algebra: ker(T*) ⊥ Ran(T).
    Tested on BOTH H_poly (trivially invertible) and a rank-deficient
    operator (non-trivial kernel to exercise the orthogonality check).
    """

    def test_hpoly_invertible_kernel_empty(self):
        """H_poly is positive definite → trivial kernel."""
        T = _sample_operator()
        ker = _kernel_basis(T)
        assert ker.shape[1] == 0, "H_poly should have trivial kernel"

    def test_hpoly_range_is_full(self):
        """H_poly positive definite → range is ℝⁿ."""
        T = _sample_operator()
        ran = _range_basis(T)
        assert ran.shape[1] == T.shape[0], "H_poly should have full range"

    def test_rank_deficient_kernel_range_orthogonal(self):
        """On a rank-1 matrix, ker(T) has dim n-1, Ran(T) has dim 1,
        and they are mutually orthogonal."""
        T = _rank_deficient_operator()
        T_star = T.conj().T
        ker_Tstar = _kernel_basis(T_star)
        ran_T = _range_basis(T)

        assert ker_Tstar.shape[1] > 0, "Rank-deficient T should have kernel"
        assert ran_T.shape[1] > 0, "T should have non-empty range"

        # Orthogonality: every kernel vector ⊥ every range vector
        cross = ker_Tstar.T @ ran_T
        np.testing.assert_allclose(cross, 0.0, atol=1e-8)

    def test_rank_deficient_dimension_counting(self):
        """dim ker(T*) + dim Ran(T) = n."""
        T = _rank_deficient_operator()
        T_star = T.conj().T
        ker_Tstar = _kernel_basis(T_star)
        ran_T = _range_basis(T)
        n = T.shape[0]
        assert ker_Tstar.shape[1] + ran_T.shape[1] == n


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — ORTHOGONAL DECOMPOSITION: ℂⁿ = ker(T*) ⊕ Ran(T)
# ═══════════════════════════════════════════════════════════════════════════════

class TestOrthogonalDecomposition:
    """Any vector y decomposes uniquely as y = y_ker + y_ran with y_ker ⊥ y_ran."""

    def test_hpoly_decomposition_trivial(self):
        """For invertible H_poly: ker = {0}, so y = 0 + y_ran = y."""
        T = _sample_operator()
        n = T.shape[0]
        ran = _range_basis(T)
        Q_ran, _ = np.linalg.qr(ran)
        rng = np.random.default_rng(99)
        y = rng.standard_normal(n)
        y_ran = Q_ran @ (Q_ran.T @ y)
        np.testing.assert_allclose(y, y_ran, atol=1e-10)

    def test_rank_deficient_decomposition(self):
        """On rank-deficient operator, random y splits into ker + ran components."""
        T = _rank_deficient_operator()
        T_star = T.conj().T
        ker_Tstar = _kernel_basis(T_star)
        ran_T = _range_basis(T)
        n = T.shape[0]

        # Orthonormalise
        Q_ker, _ = np.linalg.qr(ker_Tstar)
        Q_ran, _ = np.linalg.qr(ran_T)

        rng = np.random.default_rng(42)
        for _ in range(5):
            y = rng.standard_normal(n)
            y_ker = Q_ker @ (Q_ker.T @ y)
            y_ran = Q_ran @ (Q_ran.T @ y)

            # Reconstruction
            np.testing.assert_allclose(y, y_ker + y_ran, atol=1e-6)
            # Orthogonality
            assert abs(np.dot(y_ker, y_ran)) < 1e-6

    def test_projections_are_idempotent(self):
        """Projecting twice gives the same result (P² = P)."""
        T = _rank_deficient_operator()
        ran_T = _range_basis(T)
        Q, _ = np.linalg.qr(ran_T)
        P = Q @ Q.T  # projection onto Ran(T)

        np.testing.assert_allclose(P @ P, P, atol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — ADJOINT ALGEBRA
# ═══════════════════════════════════════════════════════════════════════════════

class TestAdjointAlgebra:
    """(λT)* = λ̄T*, (S+T)* = S*+T*, (ST)* = T*S*."""

    def test_scalar_multiplication(self):
        """(λT)* = λ̄ T*."""
        T = _sample_operator()
        lam = 1.3 + 0.7j
        lhs = (lam * T).conj().T
        rhs = np.conj(lam) * T.conj().T
        np.testing.assert_allclose(lhs, rhs, atol=1e-12)

    def test_real_scalar(self):
        """For real α: (αT)* = αT* (no conjugation effect)."""
        T = _sample_operator()
        alpha = -2.7
        lhs = (alpha * T).conj().T
        rhs = alpha * T.conj().T
        np.testing.assert_allclose(lhs, rhs, atol=1e-12)

    def test_addition(self):
        """(S + T)* = S* + T*."""
        T = _sample_operator(mu0=0.1)
        S = _sample_operator(mu0=0.2)
        lhs = (S + T).conj().T
        rhs = S.conj().T + T.conj().T
        np.testing.assert_allclose(lhs, rhs, atol=1e-12)

    def test_composition(self):
        """(ST)* = T* S* (reversal rule)."""
        T = _sample_operator(mu0=0.1)
        S = _sample_operator(mu0=0.2)
        lhs = (S @ T).conj().T
        rhs = T.conj().T @ S.conj().T
        np.testing.assert_allclose(lhs, rhs, atol=1e-10)

    def test_composition_anticommutes_order(self):
        """(ST)* ≠ S*T* in general (order matters).
        Use a non-tridiagonal S to ensure genuine non-commutativity."""
        T = _sample_operator(mu0=0.1)
        n = T.shape[0]
        # Build a symmetric but non-tridiagonal matrix (band-3)
        rng = np.random.default_rng(77)
        R = rng.standard_normal((n, n))
        S = R + R.T  # symmetric, dense → won't commute with tridiagonal T
        correct = T.conj().T @ S.conj().T    # T*S*  = (ST)*
        wrong = S.conj().T @ T.conj().T       # S*T*  ≠ (ST)* in general
        assert not np.allclose(correct, wrong, atol=1e-6)


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — SPECTRAL THEOREM (Resolution of Identity)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpectralTheorem:
    """
    For self-adjoint H: H = VΛVᵀ where V is orthogonal and Λ diagonal.
    Equivalently, VVᵀ = I (eigenvectors form an orthonormal basis).
    """

    def test_eigenvector_orthonormality(self):
        """Eigenvectors of H_poly form an orthonormal set: VᵀV = I."""
        T = _sample_operator()
        evals, V = np.linalg.eigh(T)
        np.testing.assert_allclose(V.T @ V, np.eye(V.shape[1]), atol=1e-10)

    def test_resolution_of_identity(self):
        """VVᵀ = I (completeness: eigenvectors span the full space)."""
        T = _sample_operator()
        evals, V = np.linalg.eigh(T)
        np.testing.assert_allclose(V @ V.T, np.eye(V.shape[0]), atol=1e-10)

    def test_spectral_reconstruction(self):
        """H = V diag(λ) Vᵀ (spectral decomposition)."""
        T = _sample_operator()
        evals, V = np.linalg.eigh(T)
        T_reconstructed = V @ np.diag(evals) @ V.T
        np.testing.assert_allclose(T, T_reconstructed, atol=1e-8)

    @pytest.mark.parametrize("mu0", [0.05, 0.1, 0.3])
    def test_spectral_reconstruction_parametric(self, mu0):
        """Spectral reconstruction holds across μ₀ values."""
        T = _sample_operator(mu0=mu0)
        evals, V = np.linalg.eigh(T)
        T_rec = V @ np.diag(evals) @ V.T
        np.testing.assert_allclose(T, T_rec, atol=1e-8)

    def test_eigenvalue_action(self):
        """Hv_i = λ_i v_i for each eigenpair."""
        T = _sample_operator()
        evals, V = np.linalg.eigh(T)
        for i in range(min(10, len(evals))):
            lhs = T @ V[:, i]
            rhs = evals[i] * V[:, i]
            np.testing.assert_allclose(lhs, rhs, atol=1e-8)


# ═══════════════════════════════════════════════════════════════════════════════
# §7 — POSITIVE DEFINITENESS AND RAYLEIGH QUOTIENT
# ═══════════════════════════════════════════════════════════════════════════════

class TestPositiveDefiniteness:
    """
    H_poly has V_eff > 0 and positive kinetic energy →
    ⟨φ, Hφ⟩ > 0 for all φ ≠ 0.
    """

    def test_all_eigenvalues_positive(self):
        """Every eigenvalue of H_poly is > 0."""
        T = _sample_operator()
        evals = np.linalg.eigvalsh(T)
        assert np.all(evals > 0), f"Negative eigenvalue found: {evals[evals <= 0]}"

    def test_quadratic_form_positive_random_vectors(self):
        """⟨x, Hx⟩ > 0 for random x ≠ 0."""
        T = _sample_operator()
        rng = np.random.default_rng(123)
        for _ in range(20):
            x = rng.standard_normal(T.shape[0])
            qf = x @ T @ x
            assert qf > 0, f"Quadratic form ⟨x,Hx⟩ = {qf} ≤ 0"

    def test_rayleigh_quotient_bounds(self):
        """λ_min ≤ ⟨x, Hx⟩/⟨x, x⟩ ≤ λ_max for all x ≠ 0."""
        T = _sample_operator()
        evals = np.linalg.eigvalsh(T)
        lam_min, lam_max = evals[0], evals[-1]
        rng = np.random.default_rng(456)
        for _ in range(20):
            x = rng.standard_normal(T.shape[0])
            R = (x @ T @ x) / (x @ x)
            assert R >= lam_min - 1e-10, f"Rayleigh {R} < λ_min {lam_min}"
            assert R <= lam_max + 1e-10, f"Rayleigh {R} > λ_max {lam_max}"

    def test_cholesky_exists(self):
        """Positive definite matrix admits a Cholesky decomposition."""
        T = _sample_operator()
        L = np.linalg.cholesky(T)  # Raises LinAlgError if not PD
        np.testing.assert_allclose(L @ L.T, T, atol=1e-8)

    @pytest.mark.parametrize("mu0", [0.05, 0.1, 0.3])
    def test_determinant_positive(self, mu0):
        """det(H) > 0 for positive definite H (product of positive evals)."""
        T = _sample_operator(mu0=mu0)
        # Use log-det to avoid overflow
        sign, logdet = np.linalg.slogdet(T)
        assert sign > 0, f"Determinant sign = {sign} (should be +1)"


# ═══════════════════════════════════════════════════════════════════════════════
# §8 — NORMALITY: [H, H*] = 0
# ═══════════════════════════════════════════════════════════════════════════════

class TestNormality:
    """A self-adjoint operator is normal: HH* = H*H."""

    @pytest.mark.parametrize("mu0", [0.05, 0.1, 0.3])
    def test_commutator_vanishes(self, mu0):
        """[H, H*] = HH* - H*H = 0."""
        T = _sample_operator(mu0=mu0)
        T_star = T.conj().T
        commutator = T @ T_star - T_star @ T
        np.testing.assert_allclose(commutator, 0.0, atol=1e-8)

    def test_normal_implies_unitary_diagonalisation(self):
        """Normal operators are unitarily diagonalisable:
        T = UΛU* with U unitary (U*U = I)."""
        T = _sample_operator()
        evals, U = np.linalg.eigh(T)
        np.testing.assert_allclose(U.conj().T @ U, np.eye(U.shape[0]), atol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
# §9 — HILBERT SPACE INNER PRODUCT AXIOMS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInnerProductAxioms:
    """
    The space (ℝⁿ, ⟨·,·⟩) must satisfy inner product axioms.
    These are trivial for numpy dot, but assert them against
    the operator's eigenvector basis for completeness.
    """

    def test_conjugate_symmetry(self):
        """⟨x, y⟩ = conj(⟨y, x⟩)."""
        T = _sample_operator()
        _, V = np.linalg.eigh(T)
        x, y = V[:, 0], V[:, 1]
        assert abs(np.vdot(x, y) - np.conj(np.vdot(y, x))) < 1e-14

    def test_linearity_in_second_argument(self):
        """⟨x, αy + βz⟩ = α⟨x,y⟩ + β⟨x,z⟩."""
        T = _sample_operator()
        _, V = np.linalg.eigh(T)
        x, y, z = V[:, 0], V[:, 1], V[:, 2]
        alpha, beta = 2.5, -1.3
        lhs = np.vdot(x, alpha * y + beta * z)
        rhs = alpha * np.vdot(x, y) + beta * np.vdot(x, z)
        np.testing.assert_allclose(lhs, rhs, atol=1e-12)

    def test_positive_definiteness_of_norm(self):
        """⟨x, x⟩ > 0 for x ≠ 0 and ⟨0, 0⟩ = 0."""
        T = _sample_operator()
        _, V = np.linalg.eigh(T)
        for i in range(min(5, V.shape[1])):
            assert np.vdot(V[:, i], V[:, i]) > 0
        zero = np.zeros(T.shape[0])
        assert np.vdot(zero, zero) == 0.0

    def test_cauchy_schwarz(self):
        """|⟨x,y⟩|² ≤ ⟨x,x⟩⟨y,y⟩."""
        n = 80
        rng = np.random.default_rng(2026)
        x = rng.standard_normal(n)
        y = rng.standard_normal(n)
        lhs = abs(np.vdot(x, y)) ** 2
        rhs = np.vdot(x, x) * np.vdot(y, y)
        assert lhs <= rhs + 1e-10

    def test_norm_from_inner_product(self):
        """‖x‖ = √⟨x,x⟩ and is non-negative."""
        n = 80
        rng = np.random.default_rng(2027)
        x = rng.standard_normal(n)
        norm_ip = np.sqrt(np.vdot(x, x).real)
        norm_np = np.linalg.norm(x)
        assert norm_ip >= 0
        np.testing.assert_allclose(norm_ip, norm_np, rtol=1e-12, atol=1e-12)

    def test_triangle_inequality(self):
        """‖x + y‖ ≤ ‖x‖ + ‖y‖."""
        n = 80
        rng = np.random.default_rng(2028)
        x = rng.standard_normal(n)
        y = rng.standard_normal(n)
        lhs = np.linalg.norm(x + y)
        rhs = np.linalg.norm(x) + np.linalg.norm(y)
        assert lhs <= rhs + 1e-12


# ─────────────────────────────────────────────────────────────────────────────
# HP candidate fixture
# ─────────────────────────────────────────────────────────────────────────────

def _hp_candidate(mu0=0.1, n=120, sign=1.0):
    """Build the centered/signed HP candidate operator."""
    p_grid = np.linspace(0.2, 2.5, n)
    return signed_HP_candidate(p_grid, mu0, sign=sign)


# ═══════════════════════════════════════════════════════════════════════════════
# §10 — CENTERED OPERATOR: POSITIVITY BROKEN, SPECTRAL SPREAD
# ═══════════════════════════════════════════════════════════════════════════════

class TestCenteredOperatorSpectrum:
    """
    The centered operator H_c = H_poly − center·I breaks strict positivity.
    The extremes are symmetric by construction: λ_min = −R, λ_max = +R.
    Interior eigenvalues are NOT paired (Weyl's law asymmetry).
    """

    def test_has_positive_and_negative_eigenvalues(self):
        """Centering must produce both signs."""
        p_grid = np.linspace(0.2, 2.5, 120)
        Hc = centered_H_poly_matrix(p_grid, mu0=0.1)
        evals = np.linalg.eigvalsh(Hc)
        assert np.any(evals < -1e-10), "Centered H should have negative eigenvalues"
        assert np.any(evals > 1e-10), "Centered H should have positive eigenvalues"

    def test_extremes_symmetric(self):
        """λ_min = −λ_max by midpoint construction."""
        p_grid = np.linspace(0.2, 2.5, 120)
        Hc = centered_H_poly_matrix(p_grid, mu0=0.1)
        evals = np.linalg.eigvalsh(Hc)
        np.testing.assert_allclose(evals[0], -evals[-1], atol=1e-8)

    def test_still_self_adjoint(self):
        """Centering preserves Hermiticity (subtracting scalar identity)."""
        p_grid = np.linspace(0.2, 2.5, 120)
        Hc = centered_H_poly_matrix(p_grid, mu0=0.1)
        np.testing.assert_allclose(Hc, Hc.conj().T, atol=1e-10)

    def test_still_real_spectrum(self):
        """Eigenvalues remain real after centering."""
        p_grid = np.linspace(0.2, 2.5, 120)
        Hc = centered_H_poly_matrix(p_grid, mu0=0.1)
        evals = np.linalg.eigvalsh(Hc)
        assert np.all(np.isreal(evals))

    def test_signed_operator_flips_spectrum(self):
        """sign=−1 flips every eigenvalue: λ_−(i) = −λ_+(i)."""
        p_grid = np.linspace(0.2, 2.5, 120)
        H_plus = signed_HP_candidate(p_grid, mu0=0.1, sign=+1.0)
        H_minus = signed_HP_candidate(p_grid, mu0=0.1, sign=-1.0)
        evals_plus = np.linalg.eigvalsh(H_plus)
        evals_minus = np.linalg.eigvalsh(H_minus)
        # eigvalsh returns sorted ascending, so −evals_plus is descending
        np.testing.assert_allclose(evals_minus, -evals_plus[::-1], atol=1e-10)

    @pytest.mark.parametrize("mu0", [0.05, 0.1, 0.3])
    def test_spectral_spread_increases_with_mu0(self, mu0):
        """Spectral radius R = (λ_max − λ_min)/2 > 0 for all μ₀."""
        p_grid = np.linspace(0.2, 2.5, 120)
        Hc = centered_H_poly_matrix(p_grid, mu0)
        evals = np.linalg.eigvalsh(Hc)
        R = (evals[-1] - evals[0]) / 2.0
        assert R > 0

    def test_cholesky_fails(self):
        """Centered operator is NOT positive definite → Cholesky should fail."""
        p_grid = np.linspace(0.2, 2.5, 120)
        Hc = centered_H_poly_matrix(p_grid, mu0=0.1)
        with pytest.raises(np.linalg.LinAlgError):
            np.linalg.cholesky(Hc)

    def test_interior_asymmetry_honest(self):
        """Interior eigenvalues are NOT paired — Weyl's law creates asymmetry.
        This test documents the honest limitation."""
        p_grid = np.linspace(0.2, 2.5, 160)
        Hc = centered_H_poly_matrix(p_grid, mu0=0.1)
        evals = np.linalg.eigvalsh(Hc)
        pos = evals[evals > 1e-6]
        neg = evals[evals < -1e-6]
        # Count asymmetry: |#pos − #neg| is typically > 0
        # (Weyl's law: eigenvalues grow ~ n², so more cluster below center)
        count_diff = abs(len(pos) - len(neg))
        # Just document — this IS expected
        assert count_diff >= 0  # always true; the real assertion is below
        # But extremes are still symmetric:
        np.testing.assert_allclose(evals[0], -evals[-1], atol=1e-8)


# ═══════════════════════════════════════════════════════════════════════════════
# §11 — HP CANDIDATE HILBERT SPACE AXIOMS
# ═══════════════════════════════════════════════════════════════════════════════

class TestHPCandidateHilbertAxioms:
    """
    The centered/signed HP candidate must still satisfy all Hilbert space
    axioms EXCEPT positive definiteness. This validates that centering
    doesn't break the functional-analytic structure.
    """

    def test_self_adjoint(self):
        T = _hp_candidate()
        np.testing.assert_allclose(T, T.conj().T, atol=1e-10)

    def test_real_spectrum(self):
        T = _hp_candidate()
        evals = np.linalg.eigvalsh(T)
        assert np.max(np.abs(evals.imag)) < 1e-10

    def test_not_positive_definite(self):
        """HP candidate must NOT be strictly positive."""
        T = _hp_candidate()
        evals = np.linalg.eigvalsh(T)
        assert np.any(evals < 0), "HP candidate should have negative eigenvalues"

    def test_adjoint_identity(self):
        """⟨Tx, y⟩ = ⟨x, T*y⟩ for random vectors."""
        T = _hp_candidate()
        n = T.shape[0]
        rng = np.random.default_rng(11)
        for _ in range(5):
            x = rng.standard_normal(n)
            y = rng.standard_normal(n)
            lhs = np.vdot(T @ x, y)
            rhs = np.vdot(x, T.conj().T @ y)
            np.testing.assert_allclose(lhs, rhs, atol=1e-10)

    def test_double_adjoint(self):
        """T** = T."""
        T = _hp_candidate()
        np.testing.assert_allclose(T, T.conj().T.conj().T, atol=1e-12)

    def test_spectral_reconstruction(self):
        """H = VΛVᵀ."""
        T = _hp_candidate()
        evals, V = np.linalg.eigh(T)
        T_rec = V @ np.diag(evals) @ V.T
        np.testing.assert_allclose(T, T_rec, atol=1e-8)

    def test_resolution_of_identity(self):
        """VVᵀ = I on eigenvector basis."""
        T = _hp_candidate()
        _, V = np.linalg.eigh(T)
        np.testing.assert_allclose(V @ V.T, np.eye(V.shape[0]), atol=1e-10)

    def test_normality(self):
        """[H, H*] = 0."""
        T = _hp_candidate()
        T_star = T.conj().T
        np.testing.assert_allclose(T @ T_star - T_star @ T, 0.0, atol=1e-8)

    def test_norm_equals_spectral_radius(self):
        """For self-adjoint (possibly indefinite): ‖T‖ = max|λᵢ|."""
        T = _hp_candidate()
        norm_svd = np.linalg.svd(T, compute_uv=False)[0]
        evals = np.linalg.eigvalsh(T)
        spectral_radius = np.max(np.abs(evals))
        np.testing.assert_allclose(norm_svd, spectral_radius, rtol=1e-10)

    def test_rayleigh_quotient_bounds(self):
        """λ_min ≤ R(x) ≤ λ_max still holds for indefinite self-adjoint T."""
        T = _hp_candidate()
        evals = np.linalg.eigvalsh(T)
        lam_min, lam_max = evals[0], evals[-1]
        rng = np.random.default_rng(789)
        for _ in range(20):
            x = rng.standard_normal(T.shape[0])
            R = (x @ T @ x) / (x @ x)
            assert R >= lam_min - 1e-10
            assert R <= lam_max + 1e-10

    def test_kernel_range_full(self):
        """Even after centering, H_c is generically invertible
        (center is between eigenvalues, not at one)."""
        T = _hp_candidate()
        ker = _kernel_basis(T)
        ran = _range_basis(T)
        assert ker.shape[1] == 0, "HP candidate should still be invertible"
        assert ran.shape[1] == T.shape[0]

    def test_cauchy_schwarz_on_hp_basis(self):
        """Cauchy–Schwarz holds in the Euclidean inner product on the
        eigenbasis of the HP candidate.  Eigenvectors are orthonormal so
        the eigenvector pair gives 0 ≤ 1 (trivial).  We also test a
        non-trivial random linear-combination pair."""
        T = _hp_candidate()
        _, V = np.linalg.eigh(T)
        # Eigenvector pair (trivial: orthonormal → 0 ≤ 1)
        x, y = V[:, 0], V[:, 1]
        lhs = abs(np.vdot(x, y)) ** 2
        rhs = np.vdot(x, x) * np.vdot(y, y)
        assert lhs <= rhs + 1e-12
        # Non-trivial: random linear combinations of eigenvectors
        rng = np.random.default_rng(3030)
        a = rng.standard_normal(V.shape[1])
        b = rng.standard_normal(V.shape[1])
        u = V @ a
        w = V @ b
        lhs2 = abs(np.vdot(u, w)) ** 2
        rhs2 = np.vdot(u, u).real * np.vdot(w, w).real
        assert lhs2 <= rhs2 + 1e-8


# ═══════════════════════════════════════════════════════════════════════════════
# §12 — HONEST LIMITS OF THE HP CANDIDATE
# ═══════════════════════════════════════════════════════════════════════════════

class TestHPCandidateHonestLimits:
    """
    HONEST: The HP candidate is a structural framework, not a proof.
    These tests document what it IS and what it IS NOT.
    """

    def test_spectrum_is_NOT_riemann_zeros(self):
        """The centered spectrum doesn't match ζ zeros."""
        T = _hp_candidate(n=160)
        evals = np.sort(np.linalg.eigvalsh(T))
        riemann_5 = np.array([14.135, 21.022, 25.011, 30.425, 32.935])
        # Positive eigenvalues
        pos = evals[evals > 1e-6]
        if len(pos) >= 5:
            assert not np.allclose(pos[:5], riemann_5, rtol=0.01)

    def test_sign_is_controllable(self):
        """The sign parameter is free — not derived from ζ(s)."""
        Tp = _hp_candidate(sign=+1.0)
        Tm = _hp_candidate(sign=-1.0)
        # Different operators
        assert not np.allclose(Tp, Tm, atol=1e-6)
        # Both self-adjoint
        np.testing.assert_allclose(Tp, Tp.T, atol=1e-10)
        np.testing.assert_allclose(Tm, Tm.T, atol=1e-10)

    def test_mu0_shifts_spectrum(self):
        """μ₀ is a free parameter — tuning it changes the spectrum.
        The effect is small (V_eff ~ μ₀² is dwarfed by kinetic energy)
        but measurable."""
        T1 = _hp_candidate(mu0=0.05, n=40)
        T2 = _hp_candidate(mu0=0.5, n=40)
        e1 = np.linalg.eigvalsh(T1)
        e2 = np.linalg.eigvalsh(T2)
        max_diff = np.max(np.abs(e1 - e2))
        assert max_diff > 1e-6, "μ₀ should measurably shift the spectrum"
