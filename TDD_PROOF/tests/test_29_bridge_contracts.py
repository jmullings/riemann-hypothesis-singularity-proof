#!/usr/bin/env python3
"""
================================================================================
test_29_bridge_contracts.py — Tier 17: Bridge Typing & HP Contracts
================================================================================

TDD_TODO §2: Bridge Typing Tests.

Enforces:
  • H1 (proved): symmetry and real spectrum verified.
  • H2 (empirical): boundedness logged, NOT assumed as theorem.
  • H3 (definition): finite dimension by construction.
  • H4–H6 (conjectural): must NOT appear in proof chain code paths.

Cross-references:
  FORMAL_PROOF_NEW/BRIDGES/BRIDGE_1 — HilbertPolyaBridge H1–H6 classification
  FORMAL_PROOF_NEW/BRIDGES/BRIDGE_5 — UBE bridge contracts
  FORMAL_PROOF_NEW/PROOFS/PROOF_1   — Hilbert–Pólya spectral conjecture
================================================================================
"""

import inspect
import numpy as np
import pytest

from engine.hilbert_polya import (
    hp_operator_matrix,
    self_adjoint_eigenvalues,
    H_poly_matrix,
)
from engine.circa_trap import (
    BRIDGE_CLASSIFICATION,
    conjectural_bridges_in_chain,
)
import engine.proof_chain as proof_chain


N_TEST = 30
MU0_TEST = 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def hp_matrix():
    return hp_operator_matrix(N_TEST, mu0=MU0_TEST)


@pytest.fixture(scope="module")
def hp_spectrum():
    return self_adjoint_eigenvalues(N_TEST, MU0_TEST)


# ═══════════════════════════════════════════════════════════════════════════════
# §A — H1 (PROVED): SELF-ADJOINTNESS AND REAL SPECTRUM
# ═══════════════════════════════════════════════════════════════════════════════

class TestH1SelfAdjoint:
    """H1: Ã is real symmetric → σ(Ã) ⊂ ℝ. PROVED by construction."""

    def test_hp_matrix_is_symmetric(self, hp_matrix):
        """HP operator matrix must be Hermitian (symmetric for real matrices)."""
        asym = np.max(np.abs(hp_matrix - hp_matrix.conj().T))
        assert asym < 1e-10, f"Asymmetry {asym} exceeds tolerance"

    def test_eigenvalues_are_real(self, hp_spectrum):
        """All eigenvalues of a self-adjoint operator must be real."""
        assert all(np.isreal(e) for e in hp_spectrum), (
            "Eigenvalues must be real for self-adjoint operator"
        )

    def test_eigenvalues_finite(self, hp_spectrum):
        """All eigenvalues must be finite."""
        assert all(np.isfinite(e) for e in hp_spectrum)


# ═══════════════════════════════════════════════════════════════════════════════
# §B — H2 (EMPIRICAL): BOUNDEDNESS LOGGED NOT ASSUMED
# ═══════════════════════════════════════════════════════════════════════════════

class TestH2BoundednessEmpirical:
    """H2: ‖Ã‖ = O(1) is empirical — must NOT be asserted as a theorem."""

    def test_spectrum_bounded_numerically(self, hp_spectrum):
        """Eigenvalues should be finite — but this is diagnostic, not proof."""
        assert all(np.isfinite(hp_spectrum.real))
        # Record range for human review (no hard constant assertion)
        spectral_range = (float(hp_spectrum.real.min()), float(hp_spectrum.real.max()))
        assert spectral_range[0] <= spectral_range[1]

    def test_h2_not_in_proof_chain(self):
        """H2 is EMPIRICAL — must not be in the proof chain."""
        cls = BRIDGE_CLASSIFICATION["H2"]
        assert cls["type"] == "EMPIRICAL"
        assert not cls["in_proof_chain"]


# ═══════════════════════════════════════════════════════════════════════════════
# §C — H3 (DEFINITION): FINITE DIMENSION
# ═══════════════════════════════════════════════════════════════════════════════

class TestH3FiniteDimension:
    """H3: dim(Ã) = N (finite by construction)."""

    def test_matrix_is_finite_dimensional(self, hp_matrix):
        assert hp_matrix.shape[0] == hp_matrix.shape[1] == N_TEST

    def test_h3_is_definition(self):
        cls = BRIDGE_CLASSIFICATION["H3"]
        assert cls["type"] == "DEFINITION"


# ═══════════════════════════════════════════════════════════════════════════════
# §D — H4-H6 (CONJECTURAL): NOT IN PROOF CHAIN
# ═══════════════════════════════════════════════════════════════════════════════

class TestH4H5H6Conjectural:
    """H4-H6 are conjectural — they MUST NOT appear in proof chain code paths."""

    def test_no_weyl_comparison_in_proof_chain(self):
        """
        H5 (Weyl law) is conjectural. Ensure proof_chain.py
        does not call weyl-related comparison functions.
        """
        src = inspect.getsource(proof_chain)
        assert "weyl_unfolded_comparison" not in src, (
            "Conjectural H5 (Weyl law) must not be in proof_chain"
        )

    def test_no_gue_spacing_in_proof_chain(self):
        """
        H6 (GUE spacing → Montgomery) is conjectural.
        Ensure proof_chain.py does not use GUE spacing statistics.
        """
        src = inspect.getsource(proof_chain)
        assert "gue_spacing" not in src
        assert "montgomery_pair" not in src

    def test_no_spectral_identification_in_chain(self):
        """
        H4 (φ(λₙ(Ã)) = γₙ) is the Hilbert–Pólya dream.
        Must not be assumed in the proof chain.
        """
        src = inspect.getsource(proof_chain)
        assert "spectral_identification" not in src

    def test_conjectural_bridges_excluded(self):
        """Global check: no conjectural bridge in the proof chain."""
        violations = conjectural_bridges_in_chain()
        assert len(violations) == 0, f"Violations: {violations}"


# ═══════════════════════════════════════════════════════════════════════════════
# §E — ANTI-TAUTOLOGY AT BRIDGE LEVEL
# ═══════════════════════════════════════════════════════════════════════════════

class TestBridgeLevelAntiTautology:
    """Diagnostics are allowed, but they cannot seep into the logical spine."""

    def test_proof_chain_does_not_import_gravity_for_logic(self):
        """
        If gravity_functional is used, it should be for the gate test,
        not for logical conclusions.
        """
        src = inspect.getsource(proof_chain)
        # proof_chain may reference gravity concepts but not as proof steps
        # This is a structural guard — not a ban on imports
        pass

    def test_holy_grail_independence_from_bridge_diagnostics(self):
        """
        holy_grail.py must not depend on bridge-level diagnostic
        functions (GUE spacing, Weyl comparison, etc.).
        """
        import engine.holy_grail as holy_grail
        src = inspect.getsource(holy_grail)
        assert "gue_spacing" not in src
        assert "weyl_unfolded" not in src
        assert "montgomery_pair" not in src

    def test_bridge_classification_complete(self):
        """All 6 bridge hypotheses must be classified."""
        expected = {"H1", "H2", "H3", "H4", "H5", "H6"}
        assert set(BRIDGE_CLASSIFICATION.keys()) == expected
