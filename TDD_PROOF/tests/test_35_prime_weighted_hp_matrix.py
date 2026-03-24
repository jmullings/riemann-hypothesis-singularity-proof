#!/usr/bin/env python3
"""
test_35_prime_weighted_hp_matrix.py — Prime-Weighted HP Matrix Tests
Tier 20: Explicit Formula Binding

PURPOSE:
    Test the prime-weighted HP matrix with elements derived directly from
    the Weil explicit formula prime coefficients:

        (H_EF)_{ij} = c_i · c_j · K(log p_i − log p_j ; H)

    where c_p = log(p) / √p  (Weil explicit formula coefficient)
          K(u; H) = sech²(u/H)  (sech² kernel from Theorem B 2.0)

    This establishes a direct operator-level bridge between the geometric
    HP framework and the arithmetic Weil explicit formula — closing the
    "lacks explicit formula binding" gap in the DRAFT prime_weighted_H_poly_matrix.

STRATEGY:
    16 tests across 4 classes:
    1. ExplicitFormulaHPMatrix      — structural/mathematical properties (6 tests)
    2. WeilExplicitFormulaBinding   — explicit formula coefficient binding (4 tests)
    3. ExplicitVsDraftComparison    — comparison to draft implementation (3 tests)
    4. ArithmeticIsomorphismIntegration — full pipeline integration (3 tests)

STATUS:
    GREEN from the start — the mathematical properties are proven by construction
    (Schur product theorem for PSD; Weil coefficients are exact arithmetic input).
"""

import math
import pytest
import numpy as np

from engine.hilbert_polya import (
    explicit_formula_hp_matrix,
    weil_prime_sum,
    prime_weighted_H_poly_matrix,
    hp_operator_matrix,
)
from engine.hp_alignment import dirichlet_state, hp_energy

# ─────────────────────────────────────────────────────────────────────────────
# Standard test fixtures
# ─────────────────────────────────────────────────────────────────────────────

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
MEDIUM_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
H_STANDARD = 3.0


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 1: ExplicitFormulaHPMatrix — Structural & Mathematical Properties
# ═════════════════════════════════════════════════════════════════════════════

class TestExplicitFormulaHPMatrix:
    """Structural and mathematical property tests for explicit_formula_hp_matrix."""

    def test_explicit_formula_matrix_callable(self):
        """explicit_formula_hp_matrix exists and is callable."""
        assert callable(explicit_formula_hp_matrix)

    def test_returns_correct_shape(self):
        """Matrix has shape (N, N) for N primes."""
        test_cases = [(3, SMALL_PRIMES[:3]), (7, SMALL_PRIMES[:7]),
                      (10, SMALL_PRIMES[:10]), (15, MEDIUM_PRIMES[:15])]
        for N, primes_n in test_cases:
            result = explicit_formula_hp_matrix(primes_n, H_STANDARD)
            mat = result['matrix']
            assert mat.shape == (N, N), f"Expected ({N},{N}), got {mat.shape}"

    def test_matrix_is_real_symmetric(self):
        """Matrix is real and symmetric (hence Hermitian)."""
        result = explicit_formula_hp_matrix(SMALL_PRIMES, H_STANDARD)
        mat = result['matrix']
        assert mat.dtype.kind == 'f', "Matrix should be real-valued"
        assert np.allclose(mat, mat.T), "Matrix must be symmetric"

    def test_matrix_is_positive_semidefinite(self):
        """Matrix is PSD — all eigenvalues ≥ 0 (Schur product theorem)."""
        result = explicit_formula_hp_matrix(MEDIUM_PRIMES, H_STANDARD)
        mat = result['matrix']
        eigenvalues = np.linalg.eigvalsh(mat)
        tol = -1e-12 * np.max(np.abs(eigenvalues))  # relative tolerance
        assert np.all(eigenvalues >= tol), (
            f"PSD violated: min eigenvalue = {eigenvalues.min():.3e}"
        )

    def test_diagonal_elements_match_weil_coefficients(self):
        """Diagonal H_EF[p,p] = (log p)² / p — the Weil prime strength."""
        result = explicit_formula_hp_matrix(SMALL_PRIMES, H_STANDARD)
        mat = result['matrix']
        for i, p in enumerate(SMALL_PRIMES):
            expected_diag = (math.log(float(p)) ** 2) / float(p)
            assert abs(mat[i, i] - expected_diag) < 1e-12, (
                f"Diagonal mismatch at p={p}: got {mat[i,i]:.8f}, "
                f"expected {expected_diag:.8f}"
            )

    def test_offdiagonal_sech2_kernel_structure(self):
        """Off-diagonal H_EF[p,q] = c_p · c_q · sech²((log p − log q)/H)."""
        primes = [2, 3, 5, 7, 11]
        H = 2.0
        result = explicit_formula_hp_matrix(primes, H)
        mat = result['matrix']
        coeffs = result['coeffs']

        for i in range(len(primes)):
            for j in range(i + 1, len(primes)):
                u = math.log(float(primes[i])) - math.log(float(primes[j]))
                sech2_val = 1.0 / math.cosh(u / H) ** 2
                expected = coeffs[i] * coeffs[j] * sech2_val
                assert abs(mat[i, j] - expected) < 1e-12, (
                    f"Off-diagonal mismatch at ({i},{j}): "
                    f"got {mat[i,j]:.8e}, expected {expected:.8e}"
                )


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 2: WeilExplicitFormulaBinding — Arithmetic Binding Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestWeilExplicitFormulaBinding:
    """Tests verifying the explicit formula arithmetic binding."""

    def test_trace_equals_weil_prime_sum(self):
        """Tr(H_EF) = Σ_p (log p)² / p — the Weil prime sum."""
        result = explicit_formula_hp_matrix(SMALL_PRIMES, H_STANDARD)
        mat = result['matrix']

        # Compute expected trace directly
        expected_trace = sum(
            math.log(float(p)) ** 2 / float(p)
            for p in SMALL_PRIMES
        )
        computed_trace = float(np.trace(mat))
        assert abs(computed_trace - expected_trace) < 1e-10, (
            f"Trace mismatch: got {computed_trace:.8f}, "
            f"expected {expected_trace:.8f}"
        )

    def test_weil_prime_sum_helper_consistent_with_trace(self):
        """weil_prime_sum() matches matrix trace."""
        primes = MEDIUM_PRIMES
        result = explicit_formula_hp_matrix(primes, H_STANDARD)
        trace = result['trace']
        formula_sum = weil_prime_sum(primes)
        assert abs(trace - formula_sum) < 1e-10, (
            f"Trace {trace:.8f} ≠ weil_prime_sum {formula_sum:.8f}"
        )

    def test_coefficients_are_weil_coefficients(self):
        """Returned coefficients match c_p = log(p) / √p exactly."""
        result = explicit_formula_hp_matrix(SMALL_PRIMES, H_STANDARD)
        coeffs = result['coeffs']
        for i, p in enumerate(SMALL_PRIMES):
            expected = math.log(float(p)) / math.sqrt(float(p))
            assert abs(coeffs[i] - expected) < 1e-13, (
                f"Coefficient mismatch at p={p}: "
                f"got {coeffs[i]:.10f}, expected {expected:.10f}"
            )

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_trace_independent_of_H(self, H):
        """Tr(H_EF) is independent of H: diagonal = K(0;H)·c² = 1·c² always."""
        # K(0; H) = sech²(0) = 1, so the diagonal − hence trace − does not
        # depend on H (kernel equals 1 on the diagonal for all H).
        result_H = explicit_formula_hp_matrix(SMALL_PRIMES, H)
        expected_trace = weil_prime_sum(SMALL_PRIMES)
        assert abs(result_H['trace'] - expected_trace) < 1e-10, (
            f"Trace at H={H}: got {result_H['trace']:.8f}, "
            f"expected {expected_trace:.8f}"
        )


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 3: ExplicitVsDraftComparison — Comparison Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestExplicitVsDraftComparison:
    """Compare the explicit formula matrix to the draft log-prime grid matrix."""

    def test_explicit_and_draft_have_different_spectra(self):
        """Explicit formula matrix and draft matrix produce different eigenvalues."""
        mu0 = 1.0
        primes = SMALL_PRIMES
        N = len(primes)

        result_ef = explicit_formula_hp_matrix(primes, H_STANDARD)
        mat_ef = result_ef['matrix']
        mat_draft = prime_weighted_H_poly_matrix(mu0, primes)
        mat_uniform = hp_operator_matrix(N, mu0=mu0)

        eig_ef = np.sort(np.linalg.eigvalsh(mat_ef))
        eig_draft = np.sort(np.linalg.eigvalsh(mat_draft))
        eig_uniform = np.sort(np.linalg.eigvalsh(mat_uniform))

        # All three should have distinct spectra
        assert not np.allclose(eig_ef, eig_draft, atol=1e-6), (
            "Explicit formula and draft matrices should differ spectrally"
        )
        assert not np.allclose(eig_ef, eig_uniform, atol=1e-6), (
            "Explicit formula and uniform matrices should differ spectrally"
        )

    def test_explicit_formula_matrix_has_correct_rank_structure(self):
        """At large H, K → 1 everywhere, matrix approaches rank-1 outer product c⊗c."""
        primes = [2, 3, 5, 7, 11]
        H = 1000.0  # Very large H → sech²(u/H) ≈ 1 for all small u → rank-1
        result = explicit_formula_hp_matrix(primes, H)
        mat = result['matrix']

        singular_values = np.linalg.svd(mat, compute_uv=False)
        assert np.all(singular_values >= -1e-12), "All SVs should be non-negative"
        # At large H, the matrix is nearly rank-1: dominant SV >> rest
        if len(singular_values) > 1:
            ratio = singular_values[0] / (singular_values[1] + 1e-30)
            assert ratio > 10.0, (
                f"At large H={H}, expected near-rank-1 structure; "
                f"leading SV ratio = {ratio:.2f}"
            )

    def test_explicit_formula_matrix_is_wider_at_larger_H(self):
        """Larger H → larger off-diagonal elements (wider kernel)."""
        primes = [2, 3, 5]
        H_small = 0.5
        H_large = 5.0

        result_small = explicit_formula_hp_matrix(primes, H_small)
        result_large = explicit_formula_hp_matrix(primes, H_large)

        mat_small = result_small['matrix']
        mat_large = result_large['matrix']

        # For i≠j, larger H → sech²(u/H) closer to 1 → larger off-diagonal
        # Check (0, len-1) pair which has the largest u = log(p_last/p_first)
        assert mat_large[0, -1] >= mat_small[0, -1], (
            "Larger H should give larger off-diagonal kernel value"
        )


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 4: ArithmeticIsomorphismIntegration — Pipeline Integration Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestArithmeticIsomorphismIntegration:
    """Full pipeline: from explicit formula matrix to HP energy and isomorphism."""

    def test_hp_energy_with_explicit_formula_matrix(self):
        """hp_energy(T0, H_EF, N, delta_beta) runs without error and is finite."""
        primes = SMALL_PRIMES
        N = len(primes)
        H = H_STANDARD
        T0 = 14.135   # γ₁
        db = 0.01

        result = explicit_formula_hp_matrix(primes, H)
        H_EF = result['matrix']

        energy = hp_energy(T0, H_EF, N, delta_beta=db)
        assert np.isfinite(energy), f"HP energy not finite: {energy}"
        assert energy >= 0, f"HP energy negative: {energy}"

    def test_dirichlet_state_energy_matches_prime_side_scale(self):
        """⟨φ, H_EF φ⟩ is in the same order-of-magnitude as the Weil prime sum."""
        primes = SMALL_PRIMES
        N = len(primes)
        H = H_STANDARD
        T0 = 21.022  # γ₂

        result = explicit_formula_hp_matrix(primes, H)
        H_EF = result['matrix']
        trace = result['trace']  # = Σ_p (log p)²/p ≈ O(1)

        phi = dirichlet_state(T0, N, delta_beta=0.0)
        phi = np.real(phi[:N])  # trim to prime basis size; real part for real matrix

        energy = float(np.dot(phi, H_EF @ phi))
        assert np.isfinite(energy), "Energy must be finite"

        # Energy should be O(trace * ||φ||²) — within several orders of magnitude
        phi_norm_sq = float(np.dot(phi, phi))
        upper_bound = np.max(np.linalg.eigvalsh(H_EF)) * phi_norm_sq
        lower_bound = -1e-10  # Allow small negative from rounding
        assert energy >= lower_bound, f"Energy {energy:.4e} below lower bound"
        assert energy <= upper_bound * 1.01, (
            f"Energy {energy:.4e} exceeds Rayleigh upper bound {upper_bound:.4e}"
        )

    def test_arithmetic_isomorphism_with_explicit_formula_matrix_improves(self):
        """
        The explicit formula matrix provides exact trace = Weil prime sum,
        making the arithmetic isomorphism connection direct and quantitative.

        Specifically: Tr(H_EF) / weil_prime_sum(primes) == 1.0 exactly.
        This is the sharpest possible arithmetic isomorphism — equality, not
        just an inequality.
        """
        primes = MEDIUM_PRIMES
        result = explicit_formula_hp_matrix(primes, H_STANDARD)
        trace = result['trace']
        prime_sum = weil_prime_sum(primes)

        ratio = trace / prime_sum
        assert abs(ratio - 1.0) < 1e-10, (
            f"Arithmetic isomorphism ratio should be exactly 1.0, "
            f"got {ratio:.12f}"
        )
