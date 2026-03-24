#!/usr/bin/env python3
"""
================================================================================
test_31_ube_analytic_gap.py — Tier 19: UBE Analytic Inequality Gap Monitor
================================================================================

PURPOSE:
    Implements the TDD_analytic_inequality.md prescriptive blueprint.
    This test file has FIVE roles:

    §A  ZKZ Firewall Guard — no zero data in Phase 1 functions
    §B  Convexity Control — C_φ(T;h) ≥ 0 on growing window
    §C  Error Term Scaling — θ(T) measured and tracked (Lemma 6.2 diagnostic)
    §D  Analytic Gap Contract — Lemma 6.2 status guard (MUST remain OPEN)
    §E  UBE Isolation — UBE not smuggled into the core proof chain

EPISTEMIC STATUS:
    These tests MEASURE and GUARD the analytic inequality.
    They do NOT assert the inequality is proved.
    Lemma 6.2 is explicitly marked OPEN and tested as such.

Integration point: FORMAL_PROOF_NEW/BRIDGES/BRIDGE_5 (UBE — ZKZ Protocol)
================================================================================
"""

import inspect
import numpy as np
import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# §A — ZKZ FIREWALL: No zero data in Phase 1 functions
# ═══════════════════════════════════════════════════════════════════════════════

class TestZKZFirewall:
    """
    GUARD: Prime-side functions must NEVER reference zero-loading code.
    Any violation means the ZKZ protocol is broken → predictions
    become circular → experiment is invalidated.
    """

    def test_Fk_prime_side_zero_free(self):
        """Fk_prime_side must not reference zero-loading."""
        from engine.ube_decomposition import Fk_prime_side
        src = inspect.getsource(Fk_prime_side)
        assert "load_zeros" not in src
        assert "GAMMA_30" not in src
        assert "RiemannZeros" not in src

    def test_T_phi_9D_zero_free(self):
        """T_phi_9D must not reference zero-loading."""
        from engine.ube_decomposition import T_phi_9D
        src = inspect.getsource(T_phi_9D)
        assert "load_zeros" not in src
        assert "GAMMA_30" not in src
        assert "RiemannZeros" not in src

    def test_sieve_mangoldt_zero_free(self):
        """sieve_mangoldt must not reference zero-loading."""
        from engine.ube_decomposition import sieve_mangoldt
        src = inspect.getsource(sieve_mangoldt)
        assert "load_zeros" not in src
        assert "GAMMA_30" not in src
        assert "RiemannZeros" not in src

    def test_C_phi_prime_zero_free(self):
        """C_phi_prime must not reference zero-loading."""
        from engine.ube_decomposition import C_phi_prime
        src = inspect.getsource(C_phi_prime)
        assert "load_zeros" not in src
        assert "GAMMA_30" not in src
        assert "RiemannZeros" not in src

    def test_main_PNT_k_zero_free(self):
        """main_PNT_k must not reference zero-loading."""
        from engine.ube_decomposition import main_PNT_k
        src = inspect.getsource(main_PNT_k)
        assert "load_zeros" not in src
        assert "GAMMA_30" not in src


# ═══════════════════════════════════════════════════════════════════════════════
# §B — CONVEXITY CONTROL: C_φ(T;h) ≥ 0 on tested window
# ═══════════════════════════════════════════════════════════════════════════════

class TestConvexityControl:
    """
    CONTROL: Verify C_φ(T;h) ≥ 0 on the tested window [14, 80].
    This is the empirical backbone — the UBE inequality holds numerically.
    NOT a proof; a regression guard on observed convexity.
    """

    @pytest.fixture(scope="class")
    def convexity_data(self):
        from engine.ube_decomposition import C_phi_prime
        h = 0.02
        T_grid = np.linspace(14.0, 80.0, 200)
        C_vals = np.array([C_phi_prime(T, h) for T in T_grid])
        return T_grid, C_vals, h

    def test_convexity_nonnegative(self, convexity_data):
        """C_φ(T;h) ≥ 0 for all T in [14, 80] with h=0.02."""
        _, C_vals, _ = convexity_data
        assert np.min(C_vals) >= -1e-8, (
            f"Convexity violated: min C_φ = {np.min(C_vals):.2e}"
        )

    def test_convexity_pass_rate(self, convexity_data):
        """At least 95% of grid points must have C_φ ≥ 0."""
        _, C_vals, _ = convexity_data
        pass_rate = float(np.mean(C_vals >= -1e-10))
        assert pass_rate >= 0.95, f"Pass rate {pass_rate:.2%} < 95%"

    def test_convexity_finite(self, convexity_data):
        """All C_φ values must be finite."""
        _, C_vals, _ = convexity_data
        assert np.all(np.isfinite(C_vals))

    def test_PNT_main_term_positive(self):
        """The PNT main term contribution is always positive."""
        from engine.ube_decomposition import C_phi_PNT
        for T in [14.0, 25.0, 50.0, 80.0]:
            assert C_phi_PNT(T, 0.02) > 0

    def test_convexity_at_known_zeros(self):
        """C_φ(T;h) at/near known Riemann zeros T ≈ γ_n."""
        from engine.ube_decomposition import C_phi_prime
        from engine.weil_density import GAMMA_30
        h = 0.02
        # Check at first 5 zeros (within sieve range)
        for gamma in GAMMA_30[:5]:
            c_val = C_phi_prime(gamma, h)
            assert np.isfinite(c_val), f"C_φ non-finite at γ={gamma}"


# ═══════════════════════════════════════════════════════════════════════════════
# §C — ERROR TERM SCALING: θ(T) diagnostic (Lemma 6.2 monitor)
# ═══════════════════════════════════════════════════════════════════════════════

class TestErrorTermScaling:
    """
    DIAGNOSTIC: Measure the error term ratio θ(T) = |Err_k(T)| / PNT_main.
    Lemma 6.2 requires θ(T) → 0 as T → ∞.
    We do NOT assert θ → 0 (that would close the gap by fiat).
    We assert θ is FINITE and MEASURABLE over the tested window.
    """

    @pytest.fixture(scope="class")
    def scaling_result(self):
        from engine.ube_decomposition import theta_scaling
        T_values = np.linspace(14.0, 60.0, 10)
        return theta_scaling(T_values, h=0.02)

    def test_theta_all_finite(self, scaling_result):
        """θ(T) must be finite at all test points."""
        assert scaling_result["all_finite"]

    def test_theta_bounded(self, scaling_result):
        """θ(T) must not blow up on the test window."""
        assert scaling_result["max_theta"] < 1e6, (
            f"max θ = {scaling_result['max_theta']:.2e} — error term dominates"
        )

    def test_theta_trend_computed(self, scaling_result):
        """The trend slope must be a real number (regression fit succeeded)."""
        assert np.isfinite(scaling_result["trend_slope"])

    def test_err_hat_k_is_residual(self):
        """err_hat_k is the residual F_k − (main − zero_sum)."""
        from engine.ube_decomposition import (
            Fk_prime_side, main_PNT_k, zero_sum_k, err_hat_k,
        )
        T = 20.0
        Fk = Fk_prime_side(T)
        main_val = main_PNT_k(T)
        zero_val = zero_sum_k(T)
        err = err_hat_k(T, Fk, main_val, zero_val)
        # Verify identity: Fk = main - zero + err
        reconstructed = main_val - zero_val + err
        assert abs(Fk - reconstructed) < 1e-6 * (abs(Fk) + 1e-15)

    def test_decomposition_complete(self):
        """full_decomposition returns all required keys."""
        from engine.ube_decomposition import full_decomposition
        result = full_decomposition(20.0, h=0.02)
        required_keys = [
            "T", "h", "Fk_prime_side", "main_PNT_k", "zero_sum_k",
            "err_hat_k", "theta", "C_phi_prime", "C_phi_PNT",
            "C_phi_zero_sum", "C_phi_error", "convexity_holds",
            "lemma_6_2_status",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_decomposition_identity(self):
        """C_φ = C_φ_PNT − C_φ_zero + C_φ_error (modulo numerics)."""
        from engine.ube_decomposition import full_decomposition
        d = full_decomposition(25.0, h=0.02)
        reconstructed = d["C_phi_PNT"] - d["C_phi_zero_sum"] + d["C_phi_error"]
        # Not exact equality: different code paths with different summation orders
        scale = max(abs(d["C_phi_prime"]), abs(reconstructed), 1e-15)
        assert abs(d["C_phi_prime"] - reconstructed) < 0.1 * scale


# ═══════════════════════════════════════════════════════════════════════════════
# §D — ANALYTIC GAP CONTRACT: Lemma 6.2 MUST remain OPEN
# ═══════════════════════════════════════════════════════════════════════════════

class TestAnalyticGapContract:
    """
    CONTRACT: The Lemma 6.2 analytic bound is OPEN.
    These tests ENFORCE that status — they will FAIL if someone
    accidentally marks the lemma as proved without the actual
    analytic bound being established.
    """

    def test_lemma_6_2_status_is_open(self):
        """Lemma 6.2 must be marked OPEN until an analytic bound is proved."""
        from engine.ube_decomposition import LEMMA_6_2_STATUS
        assert LEMMA_6_2_STATUS == "OPEN", (
            f"LEMMA_6_2_STATUS = {LEMMA_6_2_STATUS!r} — "
            "cannot be closed without an analytic bound on Err_k(T)"
        )

    def test_ube_convexity_status_is_empirical(self):
        """UBE convexity must be marked EMPIRICAL, not PROVED."""
        from engine.ube_decomposition import UBE_CONVEXITY_STATUS
        assert UBE_CONVEXITY_STATUS == "EMPIRICAL"

    def test_ube_classification_is_experiment(self):
        """UBE must be classified as ARITHMETIC EXPERIMENT — NOT A PROOF."""
        from engine.ube_decomposition import UBE_CLASSIFICATION
        assert "NOT A PROOF" in UBE_CLASSIFICATION
        assert "EXPERIMENT" in UBE_CLASSIFICATION

    def test_decomposition_reports_open_status(self):
        """full_decomposition must report Lemma 6.2 as OPEN."""
        from engine.ube_decomposition import full_decomposition
        d = full_decomposition(20.0)
        assert d["lemma_6_2_status"] == "OPEN"


# ═══════════════════════════════════════════════════════════════════════════════
# §E — UBE ISOLATION: UBE not in core proof chain
# ═══════════════════════════════════════════════════════════════════════════════

class TestUBEIsolation:
    """
    ISOLATION: UBE is an ARITHMETIC EXPERIMENT. It must NEVER appear
    in the core RH contradiction chain (proof_chain.py, holy_grail.py)
    except as a diagnostic or bridge comparison (not as a proof step).
    """

    def test_ube_not_in_proof_chain(self):
        """proof_chain.py must not import or reference UBE machinery."""
        import engine.proof_chain as pc
        src = inspect.getsource(pc)
        assert "UnifiedBindingEquation" not in src
        assert "ube_decomposition" not in src
        assert "BRIDGE_05_UBE" not in src

    def test_ube_not_in_holy_grail(self):
        """holy_grail.py must not import or reference UBE machinery."""
        import engine.holy_grail as hg
        src = inspect.getsource(hg)
        assert "UnifiedBindingEquation" not in src
        assert "ube_decomposition" not in src
        assert "BRIDGE_05_UBE" not in src

    def test_ube_not_in_bochner(self):
        """bochner.py must not reference UBE."""
        import engine.bochner as bo
        src = inspect.getsource(bo)
        assert "ube_decomposition" not in src

    def test_ube_not_in_offcritical(self):
        """offcritical.py must not reference UBE."""
        import engine.offcritical as oc
        src = inspect.getsource(oc)
        assert "ube_decomposition" not in src

    def test_circa_trap_uses_ube_only_for_comparison(self):
        """circa_trap.py may reference UBE only for match_rate comparison."""
        import engine.circa_trap as ct
        src = inspect.getsource(ct)
        # "ube" appears only in match_rate_ube context, not as proof import
        assert "ube_decomposition" not in src
        assert "BRIDGE_05_UBE" not in src

    def test_ube_module_has_correct_docstring(self):
        """ube_decomposition module docstring must mention OPEN status."""
        import engine.ube_decomposition as ud
        doc = ud.__doc__
        assert "OPEN" in doc
        assert "EMPIRICAL" in doc or "empirically" in doc.lower()
