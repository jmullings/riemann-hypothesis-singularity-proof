#!/usr/bin/env python3
"""
================================================================================
test_26_holy_grail_critic.py — Tier 14: Critic Layer for the Holy Grail
================================================================================

TDD_TODO §1: Core critic tests.

This file does NOT assume the Holy Grail inequality is true.
It enforces:
  • Old crack is still visible without HP (control).
  • HP term strictly improves small-Δβ behavior in tested range.
  • Deficit scaling exponent is positive (crack vanishes as Δβ→0).
  • Any "closure" verdict comes with explicit caveats and diagnostics.

Cross-references:
  FORMAL_PROOF_NEW/QED_ASSEMBLY/FULL_PROOF.py  — Theorems A-D assembly
  FORMAL_PROOF_NEW/PROOFS/PROOF_6              — Prime-side contribution
  FORMAL_PROOF_NEW/SELECTIVITY/PATH_4          — 12-step σ-selectivity chain
================================================================================
"""

import numpy as np
import pytest

from engine.bochner import lambda_star
from engine.hp_alignment import hybrid_lambda_star
from engine.holy_grail import (
    holy_grail_verdict,
    deficit_scaling_exponent,
    bhp_lower_bound,
    deficit_functional,
    rh_contradiction_certificate,
)
from engine.hilbert_polya import hp_operator_matrix
from engine.weil_density import GAMMA_30


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

H_TEST = 3.0
N_TEST = 30
MU0_TEST = 1.0
EPS_TEST = 0.1
N_PTS = 300


@pytest.fixture(scope="module")
def hp_op():
    return hp_operator_matrix(N_TEST, mu0=MU0_TEST)


@pytest.fixture(scope="module")
def gamma1():
    return float(GAMMA_30[0])


# ═══════════════════════════════════════════════════════════════════════════════
# §A — CONTROL: OLD CRACK PERSISTS WITHOUT HP
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrackControl:
    """Confirm that without HP (ε=0) the old crack is visible."""

    def test_old_crack_persists_without_hp(self, hp_op, gamma1):
        """
        Control: with eps=0 (no HP), λ_old dips below λ*(H)
        for small Δβ near a low-lying zero.
        """
        lam_floor = lambda_star(H_TEST)
        deltas = np.logspace(-3, -1, num=5)
        lam_old_vals = []
        for db in deltas:
            res = hybrid_lambda_star(
                gamma1, H_TEST, N_TEST, hp_op, eps=0.0,
                delta_beta=db, n_points=N_PTS,
            )
            lam_old_vals.append(res["lambda_old"])
        lam_old_vals = np.array(lam_old_vals)
        assert lam_old_vals.min() < lam_floor, (
            "Old crack should be visible (λ_old < λ*) without HP"
        )

    def test_crack_depth_positive_off_line(self, gamma1):
        """Deficit functional shows positive crack depth off critical line."""
        d = deficit_functional(gamma1, H_TEST, N_TEST,
                               delta_beta=0.05, n_points=N_PTS)
        assert d['crack_depth'] >= 0.0, "Crack depth must be ≥ 0"
        # F2_off should be defined and finite
        assert np.isfinite(d['F2_off'])

    def test_deficit_is_finite(self, gamma1):
        """Deficit is always finite for valid parameters."""
        for db in [1e-4, 0.01, 0.1, 0.3]:
            d = deficit_functional(gamma1, H_TEST, N_TEST,
                                   delta_beta=db, n_points=N_PTS)
            assert np.isfinite(d['deficit']), f"Deficit not finite at Δβ={db}"
            assert np.isfinite(d['lambda_old'])


# ═══════════════════════════════════════════════════════════════════════════════
# §B — HP TERM MONOTONE IMPROVEMENT
# ═══════════════════════════════════════════════════════════════════════════════

class TestHPImprovement:
    """Critic: HP penalty must help, not hurt, in tested regime."""

    def test_hp_term_monotone_improvement(self, hp_op, gamma1):
        """
        Adding HP penalty should not worsen the crack:
          λ_new(Δβ) ≥ λ_old(Δβ)  pointwise.
        """
        deltas = np.logspace(-3, -1, num=5)
        for db in deltas:
            res = hybrid_lambda_star(
                gamma1, H_TEST, N_TEST, hp_op, eps=EPS_TEST,
                delta_beta=db, n_points=N_PTS,
            )
            assert res["lambda_new"] >= res["lambda_old"] - 1e-8, (
                f"HP must not worsen crack at Δβ={db:.4f}: "
                f"λ_new={res['lambda_new']:.6f} < λ_old={res['lambda_old']:.6f}"
            )

    def test_hp_energy_positive(self, hp_op, gamma1):
        """B_HP must be positive for the HP penalty to work."""
        from engine.hp_alignment import hp_energy
        for db in [0.0, 0.01, 0.1]:
            val = hp_energy(gamma1, hp_op, N_TEST, delta_beta=db)
            assert val > 0, f"B_HP must be positive at Δβ={db}"

    def test_hp_improvement_at_multiple_zeros(self, hp_op):
        """HP improvement holds near multiple low-lying zeros."""
        for gamma in GAMMA_30[:5]:
            res = hybrid_lambda_star(
                float(gamma), H_TEST, N_TEST, hp_op, eps=EPS_TEST,
                delta_beta=0.01, n_points=N_PTS,
            )
            assert res["lambda_new"] >= res["lambda_old"] - 1e-8


# ═══════════════════════════════════════════════════════════════════════════════
# §C — DEFICIT SCALING EXPONENT
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeficitScaling:
    """Critic: crack_depth ~ Δβ^α with α > 0 (vanishes at Δβ→0)."""

    def test_deficit_vanishes_faster_than_hp_floor(self, hp_op, gamma1):
        """
        Near Δβ→0, crack_depth vanishes (positive exponent),
        and HP energy at Δβ=0 should be bounded below.
        """
        scaling = deficit_scaling_exponent(
            H_TEST, N_TEST, hp_op, T0=gamma1,
            n_db=12, n_points=N_PTS,
        )
        if scaling["crack_found"]:
            assert scaling["exponent"] > 0.0, (
                "Crack depth must vanish as Δβ→0 (exponent > 0)"
            )
            assert scaling["fit_quality"] > 0.8, (
                "Power-law fit must be reasonable"
            )

    def test_bhp_lower_bound_nonpathological(self, hp_op):
        """HP energy floor must be finite and positive across T₀."""
        floor = bhp_lower_bound(
            H_TEST, N_TEST, hp_op,
            T0_values=np.linspace(0, 80, 20),
        )
        assert np.isfinite(floor["min_B_HP"]), "B_HP floor must be finite"
        assert floor["all_positive"], "B_HP must be positive everywhere tested"

    def test_scaling_exponent_at_multiple_heights(self, hp_op):
        """Scaling exponent should be positive at various T₀."""
        for T0 in [5.0, 14.135, 30.0]:
            scaling = deficit_scaling_exponent(
                H_TEST, N_TEST, hp_op, T0=T0,
                n_db=10, n_points=N_PTS,
            )
            if scaling["crack_found"]:
                assert scaling["exponent"] > 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# §D — HOLY GRAIL VERDICT IS CONDITIONAL
# ═══════════════════════════════════════════════════════════════════════════════

class TestVerdictConditional:
    """Verdict must surface margins and conditionals, never blind claims."""

    def test_holy_grail_verdict_has_diagnostics(self):
        """Verdict must report worst_margin, coordinates, and grid count."""
        verdict = holy_grail_verdict(
            H_TEST, N_TEST, mu0=MU0_TEST, eps=EPS_TEST,
            n_points=200,
        )
        assert "worst_margin" in verdict
        assert "worst_T0" in verdict
        assert "worst_db" in verdict
        assert isinstance(verdict["holds_everywhere"], bool)
        assert np.isfinite(verdict["worst_margin"])
        assert verdict["n_tested"] > 0

    def test_certificate_conditional_on_list(self):
        """Certificate must have nonempty conditional_on list."""
        cert = rh_contradiction_certificate(H=H_TEST, N=N_TEST, mu0=MU0_TEST,
                                            n_points=200)
        assert "conditional_on" in cert
        assert len(cert["conditional_on"]) > 0, (
            "Certificate MUST list its conditions — never a blind oracle"
        )

    def test_certificate_verdict_string(self):
        """Verdict string must be informative, not empty."""
        cert = rh_contradiction_certificate(H=H_TEST, N=N_TEST, mu0=MU0_TEST,
                                            n_points=200)
        assert "verdict" in cert
        assert len(cert["verdict"]) > 10

    def test_certificate_sub_verdicts_present(self):
        """All sub-component verdicts must be present."""
        cert = rh_contradiction_certificate(H=H_TEST, N=N_TEST, mu0=MU0_TEST,
                                            n_points=200)
        for key in ("lemma_1", "lemma_2", "lemma_3",
                     "holy_grail", "regime_iii"):
            assert key in cert, f"Sub-verdict '{key}' missing from certificate"


# ═══════════════════════════════════════════════════════════════════════════════
# §E — CROSS-REFERENCE: FORMAL_PROOF_NEW CONSISTENCY
# ═══════════════════════════════════════════════════════════════════════════════

class TestFormalProofConsistency:
    """
    Verify TDD results are consistent with FORMAL_PROOF_NEW findings.
    These are cross-checks, not imports.
    """

    def test_sigma_selectivity_critical_point(self):
        """
        FORMAL_PROOF_NEW/SIGMAS: σ* = ½ is the unique critical point.
        TDD check: λ*(H) = 4/H² is the universal Bochner floor.
        """
        for H in [1.0, 2.0, 3.0, 5.0]:
            assert lambda_star(H) == pytest.approx(4.0 / H**2, rel=1e-12)

    def test_three_regime_coverage_complete(self):
        """
        FORMAL_PROOF_NEW established 11/12 steps proved.
        TDD: verify Three-Regime covers all (T₀, Δβ).
        """
        cert = rh_contradiction_certificate(H=H_TEST, N=N_TEST, mu0=MU0_TEST,
                                            n_points=200)
        # All sub-components must fire
        assert cert["lemma_1"]["psd"]
        assert cert["lemma_2"]["psd"]
        assert cert["lemma_3"]["fires"]
        assert cert["holy_grail"]["holds"]
        assert cert["regime_iii"]["all_dominate"]

    def test_dsigma_nonzero_consistency(self):
        """
        FORMAL_PROOF_NEW/PROOFS/DSIGMA_NONZERO: D_σ ≠ 0 proved.
        TDD: Lemma 3 contradiction requires ΔA < 0, implying D_σ separates.
        """
        cert = rh_contradiction_certificate(H=H_TEST, N=N_TEST, mu0=MU0_TEST,
                                            n_points=200)
        assert cert["lemma_3"]["fires"], "Lemma 3 (ΔA < 0 → D_σ separation) must hold"


# ═══════════════════════════════════════════════════════════════════════════════
# §F — EPSILON ARTIFICIALITY: ε IS NOT INTRINSICALLY DERIVED
# ═══════════════════════════════════════════════════════════════════════════════

class TestEpsilonArtificiality:
    """
    Critic: ε is a free parameter grid-searched for closure,
    NOT derived from a normalization identity or the Weil/Dirichlet
    structure.  These tests enforce honest acknowledgement.
    """

    def test_eps_is_grid_searched_not_normalization(self):
        """
        compact_domain_epsilon uses a grid search (linspace) to find ε₀.
        It must NOT contain a normalization identity.
        """
        import inspect
        from engine.holy_grail import compact_domain_epsilon
        src = inspect.getsource(compact_domain_epsilon)
        assert "linspace" in src or "grid" in src.lower(), (
            "compact_domain_epsilon must use grid search"
        )
        # Normalization-based ε would reference an identity equation
        # The docstring warns it's NOT from normalization; check the
        # computational body doesn't derive \u03b5 via a normalization identity.
        # Strip docstrings/comments before checking.
        import re
        body = re.sub(r'""".*?"""', '', src, flags=re.DOTALL)
        body = re.sub(r"'''.*?'''", '', body, flags=re.DOTALL)
        body = re.sub(r'#[^\n]*', '', body)
        assert "normalization" not in body.lower(), (
            "ε is grid-searched, not from a normalization identity"
        )

    def test_certificate_marks_hp_as_scaffold(self):
        """Certificate must flag the HP term as experimental scaffold."""
        cert = rh_contradiction_certificate(H=H_TEST, N=N_TEST, mu0=MU0_TEST,
                                            n_points=200)
        assert "SCAFFOLD" in cert["holy_grail"]["status"].upper(), (
            "Certificate must mark HP as EXPERIMENTAL SCAFFOLD"
        )

    def test_strict_mode_returns_incomplete(self):
        """In strict mode, chain_complete must be False
        because the small-Δβ crack is OPEN without HP."""
        cert = rh_contradiction_certificate(H=H_TEST, N=N_TEST, mu0=MU0_TEST,
                                            n_points=200, mode="strict")
        assert not cert["chain_complete"], (
            "Strict Weil mode must NOT claim chain complete"
        )
        assert "OPEN" in cert["verdict"], (
            "Strict mode verdict must mention OPEN status"
        )

    def test_diagnostic_mode_flags_conditional_eps(self):
        """Diagnostic mode must list ε as a conditional assumption."""
        cert = rh_contradiction_certificate(H=H_TEST, N=N_TEST, mu0=MU0_TEST,
                                            n_points=200, mode="diagnostic")
        eps_cond = [c for c in cert["conditional_on"] if "grid" in c.lower() or "ε" in c]
        assert len(eps_cond) > 0, (
            "Diagnostic certificate must list ε grid-search as conditional"
        )
