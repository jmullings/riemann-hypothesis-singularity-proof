#!/usr/bin/env python3
"""
test_23_gravity_gate.py — Tier 11: Gravity-Well Gate Integration
================================================================

TDD tests for the full gravity-well gate: an operator+spectrum pair
passes ONLY if it is BOTH PHO-representable AND arithmetically bound
to ζ(s) invariants.

Sections:
  A: Gate accepts (mock HP from true zeros)    (4 tests)
  B: Gate rejects (PHO but inert spectrum)     (4 tests)
  C: Gate rejects (not PHO)                    (3 tests)
  D: Gate edge cases                           (3 tests)
  E: Honest limits                             (2 tests)

Expected: ~16 tests.
"""

import numpy as np
import pytest

from engine.operator_axioms import (
    is_PHO_representable,
    is_arithmetically_bound,
    gravity_well_gate,
)
from engine.arithmetic_invariants import (
    GAMMA_30,
    compute_reference_invariants,
)
from engine.spectral_9d import get_9d_spectrum


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def ref_invariants():
    return compute_reference_invariants()


@pytest.fixture(scope="module")
def mock_hp_operator():
    """Diagonal matrix with eigenvalues = zeta zeros.
    Trivially self-adjoint, real spectrum, ONB = I, spectral theorem exact."""
    return np.diag(GAMMA_30)


@pytest.fixture(scope="module")
def nine_d_eigenvalues():
    """9D operator eigenvalues — structurally valid but arithmetically inert."""
    return get_9d_spectrum(n_lowest=30)


@pytest.fixture(scope="module")
def nine_d_operator(nine_d_eigenvalues):
    """Diagonal matrix from 9D eigenvalues — PHO-representable."""
    return np.diag(nine_d_eigenvalues)


# ═══════════════════════════════════════════════════════════════════════════════
# Section A: Gate Accepts (Mock HP from True Zeros)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGateAccepts:

    def test_mock_hp_is_pho(self, mock_hp_operator):
        """Diagonal zeta-zero matrix is PHO-representable."""
        assert is_PHO_representable(mock_hp_operator)

    def test_zeta_zeros_are_bound(self, ref_invariants):
        """Zeta zeros pass arithmetic binding."""
        assert is_arithmetically_bound(GAMMA_30, ref_invariants)

    def test_gravity_gate_passes(self, mock_hp_operator, ref_invariants):
        """Mock HP operator with zeta zeros passes the full gate."""
        assert gravity_well_gate(mock_hp_operator, GAMMA_30, ref_invariants)

    def test_gravity_gate_passes_default(self, mock_hp_operator):
        """Passes even with default (auto-computed) reference invariants."""
        assert gravity_well_gate(mock_hp_operator, GAMMA_30)


# ═══════════════════════════════════════════════════════════════════════════════
# Section B: Gate Rejects (PHO-representable but Inert Spectrum)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGateRejectsPHOButInert:

    def test_nine_d_is_pho(self, nine_d_operator):
        """9D diagonal is PHO — passes structural gate."""
        assert is_PHO_representable(nine_d_operator)

    def test_nine_d_not_bound(self, nine_d_eigenvalues, ref_invariants):
        """9D eigenvalues fail arithmetic binding."""
        assert not is_arithmetically_bound(nine_d_eigenvalues, ref_invariants)

    def test_nine_d_gate_rejected(self, nine_d_operator, nine_d_eigenvalues, ref_invariants):
        """9D operator fails gravity-well gate despite PHO status."""
        assert not gravity_well_gate(nine_d_operator, nine_d_eigenvalues, ref_invariants)

    def test_uniform_spectrum_rejected(self, ref_invariants):
        """Uniform spacing in wrong range: PHO-representable but arithmetically inert."""
        uniform = np.linspace(200.0, 400.0, 30)
        H = np.diag(uniform)
        assert is_PHO_representable(H)
        assert not gravity_well_gate(H, uniform, ref_invariants)


# ═══════════════════════════════════════════════════════════════════════════════
# Section C: Gate Rejects (Not PHO-representable)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGateRejectsNonPHO:

    def test_non_symmetric_rejected(self, ref_invariants):
        """Non-symmetric matrix fails PHO and therefore fails gate."""
        rng = np.random.default_rng(99)
        H = rng.normal(size=(30, 30))  # not symmetric
        assert not is_PHO_representable(H)
        assert not gravity_well_gate(H, GAMMA_30, ref_invariants)

    def test_non_square_rejected(self, ref_invariants):
        """Non-square matrix fails immediately."""
        H = np.zeros((30, 20))
        assert not is_PHO_representable(H)
        assert not gravity_well_gate(H, GAMMA_30, ref_invariants)

    def test_complex_eigenvalues_rejected(self, ref_invariants):
        """Complex off-diag breaks self-adjointness."""
        H = np.diag(GAMMA_30).astype(complex)
        H[0, 1] = 1j
        H[1, 0] = -1j  # skew-Hermitian entry breaks Hermiticity
        # Actually H[1,0] = -1j makes it non-Hermitian (Hermitian needs H[1,0] = conj(H[0,1]) = -1j)
        # Wait: conj(1j) = -1j, so H[0,1]=1j and H[1,0]=-1j IS Hermitian.
        # Make it non-Hermitian instead:
        H[1, 0] = 2j  # now H ≠ H†
        assert not is_PHO_representable(H)
        assert not gravity_well_gate(H, GAMMA_30, ref_invariants)


# ═══════════════════════════════════════════════════════════════════════════════
# Section D: Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestGateEdgeCases:

    def test_single_eigenvalue(self, ref_invariants):
        """Single eigenvalue operator — too few for spacings."""
        H = np.array([[14.134725]])
        # Should not crash; may simply fail binding
        result = gravity_well_gate(H, np.array([14.134725]), ref_invariants)
        assert isinstance(result, bool)

    def test_empty_spectrum(self, ref_invariants):
        """Empty spectrum should not crash."""
        H = np.zeros((0, 0))
        result = gravity_well_gate(H, np.array([]), ref_invariants)
        assert isinstance(result, bool)

    def test_gate_result_is_bool(self, mock_hp_operator, ref_invariants):
        """Gate always returns bool."""
        result = gravity_well_gate(mock_hp_operator, GAMMA_30, ref_invariants)
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════════════
# Section E: Honest Limits
# ═══════════════════════════════════════════════════════════════════════════════

class TestHonestLimitsGate:

    def test_gate_necessary_not_sufficient(self):
        """Passing the gate does NOT prove RH — only proves structural + arithmetic compatibility."""
        assert True  # documentary

    def test_gate_rejection_is_hard_evidence(self, nine_d_operator, nine_d_eigenvalues, ref_invariants):
        """9D rejection IS hard evidence that 9D spectrum ≠ zeta spectrum."""
        assert not gravity_well_gate(nine_d_operator, nine_d_eigenvalues, ref_invariants)
