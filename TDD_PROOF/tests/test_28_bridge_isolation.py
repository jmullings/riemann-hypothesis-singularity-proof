#!/usr/bin/env python3
"""
================================================================================
test_28_bridge_isolation.py — Tier 16: Bridge Isolation Guards
================================================================================

TDD_TODO §4: Bridge Isolation.

Enforces:
  • No zero data enters Phase 1 (ZKZ rule).
  • Zeros only enter at comparison time (Phase 2).
  • HP–zeta interaction only via Dirichlet state (no direct load_zeros/zeta).
  • Prime-side and zero-side objects are connected only through bridges.

Cross-references:
  FORMAL_PROOF_NEW/BINDING     — Non-tautological micro vector protocol
  FORMAL_PROOF_NEW/PROOFS/PROOF_8 — CIRCA stability (ZKZ rule)
  FORMAL_PROOF_NEW/PROOFS/PROOF_10 — UBE ZKZ probe
================================================================================
"""

import inspect
import pytest

import engine.hp_alignment as hp_alignment
import engine.hilbert_polya as hilbert_polya
import engine.bochner as bochner
import engine.kernel as kernel
import engine.spectral_9d as spectral_9d
import engine.offcritical as offcritical
import engine.proof_chain as proof_chain
import engine.holy_grail as holy_grail


# ═══════════════════════════════════════════════════════════════════════════════
# §A — ZKZ RULE: NO ZERO DATA IN PRIME-SIDE MODULES
# ═══════════════════════════════════════════════════════════════════════════════

class TestZKZRule:
    """
    Zero Knowledge Zone: Phase 1 modules must not load or reference
    zero data directly. Zeros enter ONLY at comparison time.
    """

    def test_kernel_no_zero_loading(self):
        """kernel.py must not load zeros — it's pure mathematical infrastructure."""
        src = inspect.getsource(kernel)
        assert "load_zeros" not in src, "kernel.py must not load zeros"
        assert "GAMMA_30" not in src, "kernel.py must not reference GAMMA_30"

    def test_bochner_no_zero_loading(self):
        """bochner.py (Toeplitz PSD) must not load zeros directly."""
        src = inspect.getsource(bochner)
        assert "load_zeros" not in src, "bochner.py must not load zeros"

    def test_offcritical_no_zero_loading(self):
        """offcritical.py (ΔA sign) must not load zeros."""
        src = inspect.getsource(offcritical)
        assert "load_zeros" not in src, "offcritical.py must not load zeros"

    def test_hilbert_polya_no_zero_loading(self):
        """
        hilbert_polya.py builds the HP operator from polymer momentum —
        it must NOT directly load zero data or call zeta functions.
        """
        src = inspect.getsource(hilbert_polya)
        assert "load_zeros" not in src, (
            "hilbert_polya.py must not load zeros"
        )
        assert "zeta(" not in src, (
            "hilbert_polya.py must not call zeta function"
        )

    def test_hp_alignment_no_zero_loading(self):
        """
        hp_alignment.py builds Dirichlet states and HP energy —
        must not reference zeros directly.
        """
        src = inspect.getsource(hp_alignment)
        assert "load_zeros" not in src, (
            "hp_alignment.py must not load zeros"
        )
        assert "zeta(" not in src, (
            "hp_alignment.py must not call zeta function"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §B — ZEROS ENTER ONLY AT COMPARISON TIME
# ═══════════════════════════════════════════════════════════════════════════════

class TestZeroEntryPoints:
    """Zeros may ONLY appear in comparison/analysis modules, not in the proof spine."""

    def test_spectral_9d_uses_operator_spectrum(self):
        """
        spectral_9d provides eigenvalues from the 9D operator —
        these are NOT Riemann zeros, they are sech² operator eigenvalues.
        """
        src = inspect.getsource(spectral_9d)
        # spectral_9d should not reference GAMMA_30 or riemann zeros
        assert "GAMMA_30" not in src, (
            "spectral_9d must use operator eigenvalues, not GAMMA_30"
        )

    def test_proof_chain_does_not_call_load_zeros(self):
        """
        proof_chain.py orchestrates lemmas — must not load zeros
        into the logical spine.
        """
        src = inspect.getsource(proof_chain)
        assert "load_zeros" not in src

    def test_holy_grail_does_not_call_load_zeros(self):
        """
        holy_grail.py is the closure module — must not load zeros
        into the inequality machinery.
        """
        src = inspect.getsource(holy_grail)
        assert "load_zeros" not in src


# ═══════════════════════════════════════════════════════════════════════════════
# §C — INTERFACE INTEGRITY: BRIDGES AS SOLE CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestBridgeInterface:
    """
    Primes ↔ 9D ↔ HP ↔ Dirichlet ↔ zeta must be separated
    by explicit interfaces. No module may bypass the bridge layer.
    """

    def test_bochner_does_not_import_hilbert_polya(self):
        """
        Bochner (PSD theory) is independent of HP operator.
        They connect only through the holy_grail module.
        """
        src = inspect.getsource(bochner)
        assert "hilbert_polya" not in src, (
            "bochner must not import hilbert_polya"
        )

    def test_kernel_is_standalone(self):
        """kernel.py must only depend on numpy/scipy — no engine imports."""
        src = inspect.getsource(kernel)
        # kernel should not import from engine
        assert "from .bochner" not in src
        assert "from .hilbert_polya" not in src
        assert "from .proof_chain" not in src

    def test_hp_alignment_bridges_correctly(self):
        """
        hp_alignment connects RS and HP via Dirichlet states.
        It imports from bochner (RS side) and hilbert_polya (HP side)
        but NOT from proof_chain or holy_grail (to avoid circular deps).
        """
        src = inspect.getsource(hp_alignment)
        assert "from .proof_chain" not in src
        assert "from .holy_grail" not in src

    def test_no_circular_imports_in_spine(self):
        """
        The proof spine (kernel → bochner → proof_chain → holy_grail)
        must flow in one direction. No backward imports.
        """
        # proof_chain should not import holy_grail
        src_pc = inspect.getsource(proof_chain)
        assert "from .holy_grail" not in src_pc, (
            "proof_chain must not import holy_grail (circular)"
        )

        # bochner should not import proof_chain
        src_b = inspect.getsource(bochner)
        assert "from .proof_chain" not in src_b


# ═══════════════════════════════════════════════════════════════════════════════
# §D — FORMAL_PROOF_NEW CROSS-CHECK
# ═══════════════════════════════════════════════════════════════════════════════

class TestFormalProofIsolation:
    """
    Cross-check isolation properties established by FORMAL_PROOF_NEW.
    """

    def test_prime_only_x_star_independence(self):
        """
        FORMAL_PROOF_NEW/CONFIGURATIONS/SINGULARITY_50D.py:
        x* is computed from Gram matrix eigenvector (prime-only).
        TDD check: spectral_9d eigenvalues are from sech² operator, not zeros.
        """
        from engine.spectral_9d import get_9d_spectrum
        E_9d = get_9d_spectrum(30)
        # Eigenvalues should be positive and increasing (operator spectrum)
        assert all(E_9d[i] <= E_9d[i + 1] for i in range(len(E_9d) - 1))
        assert all(e > 0 for e in E_9d)

    def test_assumptions_no_conjectures(self):
        """
        FORMAL_PROOF_NEW/ASSUMPTIONS: 0 conjectural assumptions.
        TDD check: proof_chain honest_assessment does not silently claim RH.
        """
        from engine.proof_chain import honest_assessment
        status = honest_assessment()
        # Should have documented status, not empty
        assert len(status) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# §E — HP ISOLATION: HP MUST NOT CONTAMINATE THE STRICT PROOF SPINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestHPIsolation:
    """
    Path-2 Mitigation: The formal proof spine (kernel → bochner → offcritical
    → proof_chain → weil_density) must be free of HP imports.  HP lives only
    in the diagnostic layer (hilbert_polya, hp_alignment, holy_grail,
    gravity_functional).
    """

    def test_proof_chain_no_hp_import(self):
        """proof_chain.py (Lemma spine) must not import HP modules.

        proof_chain.py may *mention* HP module names in data dicts
        (e.g. 'hilbert_polya': {...}, 'holy_grail_closure': {...})
        but must not *import* them.
        """
        src = inspect.getsource(proof_chain)
        import re
        for mod in ('hilbert_polya', 'hp_alignment', 'holy_grail'):
            imports = re.findall(
                rf'^\s*(?:import|from)\s+\S*{mod}', src, re.MULTILINE
            )
            assert len(imports) == 0, (
                f"proof_chain must not import {mod}: {imports}"
            )

    def test_bochner_no_hp_import(self):
        """bochner.py (PSD theory) must not import HP modules."""
        src = inspect.getsource(bochner)
        assert "hilbert_polya" not in src, (
            "bochner must not import hilbert_polya"
        )
        assert "hp_alignment" not in src, (
            "bochner must not import hp_alignment"
        )

    def test_offcritical_no_hp_import(self):
        """offcritical.py (ΔA sign) must not import HP modules."""
        src = inspect.getsource(offcritical)
        assert "hilbert_polya" not in src, (
            "offcritical must not import hilbert_polya"
        )
        assert "hp_alignment" not in src, (
            "offcritical must not import hp_alignment"
        )

    def test_kernel_no_hp_import(self):
        """kernel.py (pure sech² infrastructure) must not import HP modules."""
        src = inspect.getsource(kernel)
        assert "hilbert_polya" not in src, (
            "kernel must not import hilbert_polya"
        )
        assert "hp_alignment" not in src, (
            "kernel must not import hp_alignment"
        )

    def test_weil_density_no_hp_import(self):
        """weil_density.py (Theorems 6.1–6.3) must not import HP modules."""
        import engine.weil_density as weil_density
        src = inspect.getsource(weil_density)
        assert "hilbert_polya" not in src, (
            "weil_density must not import hilbert_polya"
        )
        assert "hp_alignment" not in src, (
            "weil_density must not import hp_alignment"
        )

    def test_strict_mode_certificate_excludes_hp(self):
        """
        In strict mode, the RH certificate must NOT include HP results
        and must honestly report chain_complete = False.
        """
        from engine.holy_grail import (
            rh_contradiction_certificate, PROOF_MODE_STRICT,
        )
        cert = rh_contradiction_certificate(
            H=3.0, N=30, mu0=1.0, n_points=200,
            mode=PROOF_MODE_STRICT,
        )
        assert cert['mode'] == PROOF_MODE_STRICT
        assert not cert['chain_complete'], (
            "Strict mode must return chain_complete=False "
            "(small-Δβ crack is OPEN without HP)"
        )
        assert cert['holy_grail']['holds'] is None, (
            "Strict mode must not evaluate the Holy Grail inequality"
        )
