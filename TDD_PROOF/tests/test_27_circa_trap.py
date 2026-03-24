#!/usr/bin/env python3
"""
================================================================================
test_27_circa_trap.py — Tier 15: CIRCA Anti-Tautology Guards
================================================================================

TDD_TODO §3: CIRCA Trap.

Enforces:
  • WDB bridge is CAUGHT as tautological (uses zeros in construction).
  • UBE bridge is confirmed non-tautological (prime-only).
  • HP bridge is confirmed non-tautological (operator-only).
  • No tautological bridge exists in the proof chain.
  • Circularity scoring classifies bridges correctly.

Cross-references:
  FORMAL_PROOF_NEW/PROOFS/PROOF_10 — CIRCA Tautology Trap (4-test suite)
  FORMAL_PROOF_NEW/PROOFS/PROOF_8  — Explicit Formula CIRCA
  FORMAL_PROOF_NEW/BINDING          — Non-tautological micro vector
================================================================================
"""

import numpy as np
import pytest

from engine.circa_trap import (
    match_rate_identity,
    match_rate_wdb,
    match_rate_ube,
    match_rate_hp,
    is_tautological,
    circularity_score,
    random_match_rate,
    conjectural_bridges_in_chain,
    get_bridge_classification,
    run_circa_audit,
    BRIDGE_CLASSIFICATION,
)
from engine.weil_density import GAMMA_30


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def zeros():
    return GAMMA_30


@pytest.fixture(scope="module")
def mr_identity(zeros):
    return match_rate_identity(zeros)


@pytest.fixture(scope="module")
def mr_random(zeros):
    return random_match_rate(len(zeros), zeros)


# ═══════════════════════════════════════════════════════════════════════════════
# §A — IDENTITY PREDICTOR BASELINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestIdentityBaseline:
    """The identity predictor must always score 1.0."""

    def test_identity_rate_is_one(self, zeros):
        assert match_rate_identity(zeros) == 1.0

    def test_identity_rate_independent_of_window(self, zeros):
        for w in [0.5, 1.0, 2.0, 5.0]:
            assert match_rate_identity(zeros, window=w) == 1.0

    def test_random_rate_below_identity(self, zeros, mr_identity, mr_random):
        assert mr_random < mr_identity, (
            "Random baseline must be worse than identity predictor"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §B — WDB CAUGHT AS TAUTOLOGICAL
# ═══════════════════════════════════════════════════════════════════════════════

class TestWDBTautological:
    """WDB bridge uses zeros → MUST be caught as tautological."""

    def test_wdb_is_tautological(self, zeros):
        mr_wdb = match_rate_wdb(zeros)
        mr_id = match_rate_identity(zeros)
        assert is_tautological(mr_wdb, mr_id, eps_circa=0.05), (
            f"WDB MUST be caught as tautological: "
            f"|{mr_wdb:.4f} - {mr_id:.4f}| < 0.05"
        )

    def test_wdb_rate_near_one(self, zeros):
        mr_wdb = match_rate_wdb(zeros)
        assert mr_wdb > 0.90, f"WDB rate should be near 1.0, got {mr_wdb}"

    def test_wdb_circularity_score_high(self, zeros, mr_random):
        mr_wdb = match_rate_wdb(zeros)
        mr_id = match_rate_identity(zeros)
        cs = circularity_score(mr_wdb, mr_random, mr_id)
        assert cs["tautological"], (
            f"WDB circularity score {cs['score']:.4f} must be ≥ {cs['threshold']}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §C — UBE CONFIRMED NON-TAUTOLOGICAL
# ═══════════════════════════════════════════════════════════════════════════════

class TestUBENonTautological:
    """UBE bridge uses only primes → MUST NOT be tautological."""

    def test_ube_is_not_tautological(self, zeros):
        mr_ube = match_rate_ube(zeros)
        mr_id = match_rate_identity(zeros)
        assert not is_tautological(mr_ube, mr_id, eps_circa=0.05), (
            f"UBE must NOT be tautological: "
            f"|{mr_ube:.4f} - {mr_id:.4f}| should be ≥ 0.05"
        )

    def test_ube_rate_strictly_below_identity(self, zeros):
        mr_ube = match_rate_ube(zeros)
        assert mr_ube < 0.95, (
            f"UBE match rate should be well below 1.0, got {mr_ube}"
        )

    def test_ube_rate_above_random(self, zeros, mr_random):
        """UBE should perform better than random (it detects real structure)."""
        mr_ube = match_rate_ube(zeros)
        assert mr_ube > mr_random, (
            f"UBE ({mr_ube:.4f}) should beat random ({mr_random:.4f})"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §D — HP CONFIRMED NON-TAUTOLOGICAL
# ═══════════════════════════════════════════════════════════════════════════════

class TestHPNonTautological:
    """HP bridge uses operator spectrum only → MUST NOT be tautological."""

    def test_hp_is_not_tautological(self, zeros):
        mr_hp = match_rate_hp(zeros)
        mr_id = match_rate_identity(zeros)
        assert not is_tautological(mr_hp, mr_id, eps_circa=0.05), (
            f"HP must NOT be tautological: "
            f"|{mr_hp:.4f} - {mr_id:.4f}| should be ≥ 0.05"
        )

    def test_hp_rate_below_identity(self, zeros):
        mr_hp = match_rate_hp(zeros)
        assert mr_hp < 0.95, f"HP match rate should be below 1.0, got {mr_hp}"


# ═══════════════════════════════════════════════════════════════════════════════
# §E — BRIDGE CLASSIFICATION INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════

class TestBridgeClassification:
    """Bridge classification H1-H6 must be correctly structured."""

    def test_no_conjectural_bridge_in_proof_chain(self):
        """No CONJECTURE bridge may be in the proof chain."""
        violations = conjectural_bridges_in_chain()
        assert len(violations) == 0, (
            f"Conjectural bridges in proof chain: {violations}"
        )

    def test_h1_is_proved(self):
        cls = get_bridge_classification("H1")
        assert cls is not None
        assert cls["type"] == "PROVED"

    def test_h4_h5_h6_are_conjectural(self):
        for hid in ("H4", "H5", "H6"):
            cls = get_bridge_classification(hid)
            assert cls["type"] == "CONJECTURE", f"{hid} should be CONJECTURE"
            assert not cls["in_proof_chain"], (
                f"{hid} (conjectural) must NOT be in proof chain"
            )

    def test_all_six_bridges_defined(self):
        for hid in ("H1", "H2", "H3", "H4", "H5", "H6"):
            assert hid in BRIDGE_CLASSIFICATION


# ═══════════════════════════════════════════════════════════════════════════════
# §F — PROOF CHAIN GUARD
# ═══════════════════════════════════════════════════════════════════════════════

class TestProofChainGuard:
    """No tautological bridge may be cited as evidence in the RH chain."""

    def test_no_tautological_bridge_in_proof_chain(self, zeros):
        """
        All bridges used as supporting evidence must be non-tautological.
        WDB is deliberately excluded from the RH chain.
        """
        mr_id = match_rate_identity(zeros)
        bridges = {
            "HP": match_rate_hp(zeros),
            "UBE": match_rate_ube(zeros),
        }
        for name, mr in bridges.items():
            assert not is_tautological(mr, mr_id, eps_circa=0.05), (
                f"Bridge {name} is CIRCA-tautological; "
                "must NOT be in RH evidence chain."
            )


# ═══════════════════════════════════════════════════════════════════════════════
# §G — FULL AUDIT INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestFullCIRCAAudit:
    """Full CIRCA audit must pass all checks."""

    def test_full_audit_passes(self, zeros):
        audit = run_circa_audit(zeros)
        assert audit["all_pass"], (
            f"CIRCA audit failed: wdb_taut={audit['wdb_tautological']}, "
            f"ube_taut={audit['ube_tautological']}, "
            f"hp_taut={audit['hp_tautological']}, "
            f"violations={audit['chain_violations']}"
        )

    def test_audit_rates_reported(self, zeros):
        audit = run_circa_audit(zeros)
        for key in ("identity_rate", "wdb_rate", "ube_rate",
                     "hp_rate", "random_rate"):
            assert key in audit
            assert 0.0 <= audit[key] <= 1.0
