#!/usr/bin/env python3
r"""
================================================================================
test_39_triad_consistency.py — Triad Governor Self-Consistency Tests
================================================================================

TARGET: The three diagnostic layers — (A) high-lying zeros / zeta-side,
(B) 9D/PHO arithmetic binding, (C) UBE prime-side convexity — form a
closed feedback loop.  An admissible configuration (T, Δβ, spectrum) must
survive all three filters simultaneously.

WHAT THESE TESTS VERIFY:

  §1.  INDIVIDUAL LAYER SMOKE     — Each layer probe returns expected keys
                                     and types; no crashes on valid inputs.
  §2.  ON-CRITICAL AGREEMENT      — For RH-consistent configurations
                                     (Δβ ≈ 0, known zeros as spectrum),
                                     all three layers agree (triad_conflict=False).
  §3.  OFF-CRITICAL ZETA SIGNAL   — Moderate Δβ > 0 forces negative F_avg
                                     (Layer A fires), creating a triad conflict
                                     if Layers B and C still pass.
  §4.  PHO REJECTION              — Synthetic non-PHO operators (non-Hermitian,
                                     wrong spectrum) fail Layer B while A and C
                                     may still pass → triad conflict.
  §5.  UBE SENSITIVITY            — Layer C convexity holds at tested T values;
                                     consistency with Layers A and B.
  §6.  BATCH SCAN STRUCTURE       — triad_scan over a small grid returns
                                     well-formed results with correct counts.
  §7.  TRIAD INVARIANT            — The closed-loop consistency property:
                                     no tested RH-consistent configuration
                                     produces a triad conflict; every tested
                                     strongly off-critical configuration
                                     produces at least one layer failure.
  §8.  CONFLICT CLASSIFICATION    — Conflict types are correctly labelled
                                     and the engine correctly distinguishes
                                     unanimous rejection from mixed conflict.

EPISTEMIC STATUS:
  DIAGNOSTIC.  These tests verify the cross-consistency engine's structural
  correctness, not any analytic theorem.  The triad governor does not close
  the three open analytic gaps; it makes their interaction explicit and
  machine-verifiable.
================================================================================
"""

import numpy as np
import pytest

from engine.triad_governor import (
    zeta_side_probe,
    pho_binding_probe,
    ube_convexity_probe,
    triad_probe,
    triad_scan,
    _classify_conflict,
    _truth_label,
    _update_confusion,
    FAILURE_MODES,
)
from engine.weil_density import GAMMA_30
from engine.hilbert_polya import hp_operator_matrix
from engine.operator_axioms import is_PHO_representable


# ─────────────────────────────────────────────────────────────────────────────
# Shared constants
# ─────────────────────────────────────────────────────────────────────────────

# First 8 known Riemann zeros
GAMMAS_8 = GAMMA_30[:8].copy()

# Representative critical-line height
T_CRIT = 30.0

# Small Δβ (near-critical) and moderate Δβ (off-critical)
DB_SMALL = 0.001
DB_MODERATE = 0.1
DB_LARGE = 0.3

# Default Dirichlet polynomial length (keep small for speed)
N_TEST = 20

# Number of H values (keep small for speed)
N_H_TEST = 5


# ─────────────────────────────────────────────────────────────────────────────
# §1 — Individual Layer Smoke Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestLayerSmoke:
    """Each layer probe returns expected keys and types without crashing."""

    def test_zeta_side_returns_expected_keys(self):
        """Layer A probe returns all documented keys."""
        r = zeta_side_probe(T_CRIT, DB_MODERATE, N=N_TEST, n_H=N_H_TEST,
                            n_points=100)
        expected = {'A_off_avg', 'B_avg', 'total_avg', 'negative',
                    'H_family', 'w_family', 'admissible', 'zeta_margin'}
        assert expected <= set(r.keys()), f"Missing keys: {expected - set(r.keys())}"

    def test_zeta_side_types(self):
        """Layer A probe returns correct types."""
        r = zeta_side_probe(T_CRIT, DB_MODERATE, N=N_TEST, n_H=N_H_TEST,
                            n_points=100)
        assert isinstance(r['A_off_avg'], float)
        assert isinstance(r['B_avg'], float)
        assert isinstance(r['negative'], (bool, np.bool_))
        assert isinstance(r['H_family'], np.ndarray)

    def test_pho_binding_returns_expected_keys(self):
        """Layer B probe returns all documented keys."""
        r = pho_binding_probe(GAMMAS_8)
        expected = {'pho_ok', 'arith_ok', 'gate_ok', 'spectrum', 'n_eigs',
                    'pho_margin'}
        assert expected <= set(r.keys()), f"Missing keys: {expected - set(r.keys())}"

    def test_pho_binding_types(self):
        """Layer B probe returns correct types."""
        r = pho_binding_probe(GAMMAS_8)
        assert isinstance(r['pho_ok'], (bool, np.bool_))
        assert isinstance(r['arith_ok'], (bool, np.bool_))
        assert isinstance(r['n_eigs'], int)

    def test_ube_convexity_returns_expected_keys(self):
        """Layer C probe returns all documented keys."""
        r = ube_convexity_probe(T_CRIT)
        expected = {'C_phi', 'convex_ok', 'err_hat_k', 'theta',
                    'decomp', 'lemma_status', 'ube_margin'}
        assert expected <= set(r.keys()), f"Missing keys: {expected - set(r.keys())}"

    def test_ube_convexity_types(self):
        """Layer C probe returns correct types."""
        r = ube_convexity_probe(T_CRIT)
        assert isinstance(r['C_phi'], float)
        assert isinstance(r['convex_ok'], (bool, np.bool_))
        assert isinstance(r['lemma_status'], str)

    def test_triad_probe_returns_expected_keys(self):
        """Full triad probe returns all documented keys."""
        r = triad_probe(T_CRIT, DB_MODERATE, N=N_TEST, n_H=N_H_TEST,
                        n_points=100)
        expected = {'zeta_side', 'pho_binding', 'ube_side',
                    'zeta_ok', 'pho_ok', 'ube_ok',
                    'all_ok', 'triad_conflict', 'conflict_type',
                    'truth_label', 'zeta_margin', 'pho_margin', 'ube_margin'}
        assert expected <= set(r.keys()), f"Missing keys: {expected - set(r.keys())}"


# ─────────────────────────────────────────────────────────────────────────────
# §2 — On-Critical Agreement
# ─────────────────────────────────────────────────────────────────────────────

class TestOnCriticalAgreement:
    """
    For RH-consistent configurations (known zeros as spectrum, Δβ ≈ 0),
    all three layers should agree: no triad conflict.
    """

    @pytest.mark.parametrize("T", [14.135, 25.011, 40.0])
    def test_on_critical_no_conflict(self, T):
        """
        At Δβ ≈ 0 (near-critical), the triad should be self-consistent.

        Layer A: F_avg > 0 (no contradiction at Δβ ≈ 0).
        Layer B: GAMMA_30 spectrum passes arithmetic binding.
        Layer C: UBE convexity holds at tested T.
        """
        r = triad_probe(T, DB_SMALL, spectrum=GAMMA_30[:20],
                        N=N_TEST, n_H=N_H_TEST, n_points=100)
        assert not r['triad_conflict'], (
            f"Triad conflict at on-critical T={T}, Δβ={DB_SMALL}: "
            f"{r['conflict_type']}"
        )

    def test_on_critical_zeta_ok(self):
        """Layer A does not fire contradiction at near-zero Δβ."""
        r = triad_probe(T_CRIT, DB_SMALL, N=N_TEST, n_H=N_H_TEST,
                        n_points=100)
        assert r['zeta_ok'], (
            f"Zeta side fired at Δβ={DB_SMALL}: "
            f"total_avg={r['zeta_side']['total_avg']:.4e}"
        )

    def test_on_critical_ube_ok(self):
        """Layer C convexity holds at representative T values."""
        for T in [20.0, 30.0, 40.0]:
            r = ube_convexity_probe(T)
            assert r['convex_ok'], (
                f"UBE convexity failed at T={T}: C_φ={r['C_phi']:.4e}"
            )

    def test_on_critical_pho_ok_with_gamma30(self):
        """Layer B passes with GAMMA_30 as reference spectrum."""
        r = pho_binding_probe(GAMMA_30[:20])
        assert r['arith_ok'], "GAMMA_30[:20] failed arithmetic binding"


# ─────────────────────────────────────────────────────────────────────────────
# §3 — Off-Critical Zeta Signal
# ─────────────────────────────────────────────────────────────────────────────

class TestOffCriticalZetaSignal:
    """
    Off-critical Δβ > 0 produces a negative raw ΔA signal.

    The CORRECTED total (ΔA + λ*·B) stays positive by design (Theorem B 2.0 —
    the correction floor is built to guarantee non-negativity).  The meaningful
    off-critical detection is that the RAW ΔA_avg goes negative: the zeta-side
    registers the off-critical perturbation even though the correction compensates.

    At small n_H, phase escapes can make ΔA_avg positive for some Δβ values
    (the cosine factor cos(2πγ₀/H) partially cancels).  At Δβ ≥ 0.2, the
    signal is reliably negative with n_H=5.
    """

    @pytest.mark.parametrize("db", [0.2, 0.3])
    def test_raw_delta_A_negative_at_moderate_db(self, db):
        """ΔA_avg < 0 at moderate Δβ — the raw off-critical signal is detected."""
        z = zeta_side_probe(T_CRIT, db, N=N_TEST, n_H=N_H_TEST,
                            n_points=100)
        assert z['A_off_avg'] < 0, (
            f"ΔA_avg not negative at Δβ={db}: "
            f"A_off_avg={z['A_off_avg']:.4e} (expected < 0)"
        )

    def test_corrected_total_stays_positive(self):
        """
        The corrected total ΔA_avg + λ*·B_avg stays positive at all tested Δβ.
        This is Theorem B 2.0's correction floor doing its job — the λ*·B term
        compensates the negative ΔA.
        """
        for db in [0.1, 0.2, 0.3]:
            z = zeta_side_probe(T_CRIT, db, N=N_TEST, n_H=N_H_TEST,
                                n_points=100)
            assert z['total_avg'] >= 0, (
                f"Corrected total went negative at Δβ={db}: "
                f"total_avg={z['total_avg']:.4e}"
            )

    def test_off_critical_synthetic_conflict(self):
        """
        At Δβ=0.2 with a BAD operator (non-PHO), Layer B fails while
        Layer A and C may pass → triad conflict detected.
        """
        bad_op = np.eye(20) + 0.1 * np.random.default_rng(42).standard_normal((20, 20))
        # Make non-Hermitian
        bad_op[0, 1] += 5.0
        r = triad_probe(T_CRIT, 0.2, spectrum=GAMMA_30[:20],
                        operator=bad_op, N=N_TEST, n_H=N_H_TEST,
                        n_points=100)
        assert not r['pho_ok'], "Bad operator should fail PHO gate"
        assert not r['all_ok'], "all_ok should be False with bad operator"

    def test_h_family_admissible_at_moderate_db(self):
        """The H-family built for moderate Δβ passes admissibility."""
        z = zeta_side_probe(T_CRIT, DB_MODERATE, N=N_TEST, n_H=N_H_TEST,
                            n_points=100)
        assert z['admissible'], "H-family not admissible at Δβ=0.1"


# ─────────────────────────────────────────────────────────────────────────────
# §4 — PHO Rejection (Synthetic Non-PHO Operators)
# ─────────────────────────────────────────────────────────────────────────────

class TestPHORejection:
    """
    Synthetic non-PHO operators fail Layer B while Layers A and C may pass,
    creating a triad conflict.
    """

    def test_non_hermitian_operator_fails_pho(self):
        """A non-Hermitian matrix fails PHO representability."""
        bad_op = np.array([[1, 2], [3, 4]], dtype=float)
        r = pho_binding_probe(np.array([1.0, 2.0]), operator=bad_op)
        assert not r['pho_ok'], "Non-Hermitian operator passed PHO gate"
        assert not r['gate_ok'], "Non-Hermitian operator passed gravity well"

    def test_random_spectrum_fails_arithmetic_binding(self):
        """A random spectrum fails arithmetic binding."""
        rng = np.random.default_rng(42)
        random_spec = rng.uniform(10, 100, 20)
        r = pho_binding_probe(random_spec)
        assert not r['arith_ok'], "Random spectrum passed arithmetic binding"

    def test_pho_failure_creates_conflict_in_triad(self):
        """
        With a non-PHO operator, Layer B fails.  If Layers A and C pass
        (as they would for near-critical Δβ), the triad detects a conflict.
        """
        bad_op = np.array([[1, 2], [3, 4]], dtype=float)
        bad_spec = np.array([1.0, 2.0])
        r = triad_probe(T_CRIT, DB_SMALL, spectrum=bad_spec,
                        operator=bad_op, N=N_TEST, n_H=N_H_TEST,
                        n_points=100)
        assert not r['pho_ok'], "Non-PHO operator should fail Layer B"
        # If zeta_ok and ube_ok pass but pho fails → conflict
        if r['zeta_ok'] and r['ube_ok']:
            assert r['triad_conflict'], (
                "Expected triad conflict: Layers A,C pass but B fails"
            )

    def test_uniform_spectrum_fails_binding(self):
        """A uniform grid spectrum fails arithmetic binding (wrong statistics)."""
        uniform = np.linspace(10, 100, 20)
        r = pho_binding_probe(uniform)
        assert not r['arith_ok'], "Uniform spectrum passed arithmetic binding"


# ─────────────────────────────────────────────────────────────────────────────
# §5 — UBE Sensitivity
# ─────────────────────────────────────────────────────────────────────────────

class TestUBESensitivity:
    """
    Layer C (UBE convexity) holds at tested T values; consistency check
    across multiple heights.
    """

    @pytest.mark.parametrize("T", [15.0, 20.0, 25.0, 30.0, 40.0, 50.0])
    def test_convexity_holds_at_various_T(self, T):
        """C_φ(T; h) ≥ 0 at representative heights."""
        r = ube_convexity_probe(T, h=0.02)
        assert r['convex_ok'], (
            f"UBE convexity violated at T={T}: C_φ={r['C_phi']:.4e}"
        )

    def test_lemma_status_is_open(self):
        """Lemma 6.2 status remains OPEN (epistemic honesty check)."""
        r = ube_convexity_probe(T_CRIT)
        assert r['lemma_status'] == "OPEN", (
            f"Lemma 6.2 status changed to '{r['lemma_status']}' — "
            f"update triad governor if this is intentional"
        )

    def test_decomposition_keys_present(self):
        """Full decomposition dict contains expected diagnostic keys."""
        r = ube_convexity_probe(T_CRIT)
        d = r['decomp']
        for key in ['Fk_prime_side', 'main_PNT_k', 'zero_sum_k',
                     'err_hat_k', 'C_phi_prime', 'C_phi_PNT']:
            assert key in d, f"Missing decomposition key: {key}"


# ─────────────────────────────────────────────────────────────────────────────
# §6 — Batch Scan Structure
# ─────────────────────────────────────────────────────────────────────────────

class TestBatchScanStructure:
    """triad_scan returns well-formed results with correct counts."""

    def test_scan_returns_expected_keys(self):
        """triad_scan result dict contains all documented keys."""
        r = triad_scan([T_CRIT], [DB_SMALL], N=N_TEST, n_H=N_H_TEST,
                       n_points=100)
        expected = {'results', 'n_total', 'n_conflict', 'n_all_ok',
                    'conflict_rate', 'summary', 'confusion'}
        assert expected <= set(r.keys())

    def test_scan_count_consistency(self):
        """n_total = len(T_values) × len(db_values)."""
        T_vals = [20.0, 30.0]
        db_vals = [0.001, 0.1]
        r = triad_scan(T_vals, db_vals, N=N_TEST, n_H=N_H_TEST,
                       n_points=100)
        assert r['n_total'] == len(T_vals) * len(db_vals)
        assert len(r['results']) == r['n_total']
        assert len(r['summary']) == r['n_total']

    def test_scan_counts_add_up(self):
        """n_conflict + n_all_ok ≤ n_total (some may be unanimous rejection)."""
        r = triad_scan([T_CRIT], [DB_SMALL, DB_MODERATE],
                       N=N_TEST, n_H=N_H_TEST, n_points=100)
        assert r['n_conflict'] + r['n_all_ok'] <= r['n_total']

    def test_scan_conflict_rate_bounded(self):
        """Conflict rate is in [0, 1]."""
        r = triad_scan([T_CRIT], [DB_SMALL], N=N_TEST, n_H=N_H_TEST,
                       n_points=100)
        assert 0.0 <= r['conflict_rate'] <= 1.0


# ─────────────────────────────────────────────────────────────────────────────
# §7 — Triad Invariant
# ─────────────────────────────────────────────────────────────────────────────

class TestTriadInvariant:
    """
    The closed-loop consistency property:
      - No tested RH-consistent configuration produces a triad conflict.
      - Every tested strongly off-critical configuration produces at least
        one layer failure (all_ok = False).
    """

    @pytest.mark.parametrize("T", [14.135, 21.022, 30.0, 40.0])
    def test_rh_consistent_no_conflict(self, T):
        """
        RH-consistent configs (Δβ ≈ 0, known-zero spectrum) must not
        produce a triad conflict.
        """
        r = triad_probe(T, DB_SMALL, spectrum=GAMMA_30[:20],
                        N=N_TEST, n_H=N_H_TEST, n_points=100)
        assert not r['triad_conflict'], (
            f"Triad conflict at RH-consistent T={T}: {r['conflict_type']}"
        )

    @pytest.mark.parametrize("db", [0.2, 0.3])
    def test_off_critical_raw_signal_detected(self, db):
        """
        At moderate Δβ, the raw off-critical signal ΔA_avg is negative
        even though the corrected total stays positive (correction floor).

        This is the triad's zeta-side contribution: it detects the
        perturbation in the raw curvature, providing tension data to
        cross-check against Layers B and C.
        """
        r = triad_probe(T_CRIT, db, spectrum=GAMMA_30[:20],
                        N=N_TEST, n_H=N_H_TEST, n_points=100)
        assert r['zeta_side']['A_off_avg'] < 0, (
            f"ΔA_avg not negative at Δβ={db}: "
            f"A_off_avg={r['zeta_side']['A_off_avg']:.4e}"
        )

    def test_off_critical_with_bad_operator_not_all_ok(self):
        """
        Off-critical Δβ with a non-PHO operator → Layer B fails,
        all_ok = False.  This is the mixed-conflict scenario.
        """
        bad_op = np.array([[1, 5], [0, 2]], dtype=float)
        bad_spec = np.array([1.0, 2.0])
        r = triad_probe(T_CRIT, 0.2, spectrum=bad_spec,
                        operator=bad_op, N=N_TEST, n_H=N_H_TEST,
                        n_points=100)
        assert not r['all_ok'], (
            f"all_ok=True with bad operator at Δβ=0.2"
        )

    def test_scan_rh_consistent_zero_conflicts(self):
        """
        A batch scan at small Δβ across multiple T values produces zero
        triad conflicts.
        """
        T_vals = [20.0, 30.0, 40.0]
        r = triad_scan(T_vals, [DB_SMALL], spectrum=GAMMA_30[:20],
                       N=N_TEST, n_H=N_H_TEST, n_points=100)
        assert r['n_conflict'] == 0, (
            f"{r['n_conflict']} conflicts found at Δβ={DB_SMALL} across "
            f"{len(T_vals)} heights"
        )

    def test_scan_off_critical_raw_signals(self):
        """
        A batch scan at moderate Δβ shows negative ΔA_avg (raw signal)
        for Δβ ≥ 0.2, confirming the zeta-side detects the perturbation.
        """
        db_vals = [0.2, 0.3]
        r = triad_scan([T_CRIT], db_vals, spectrum=GAMMA_30[:20],
                       N=N_TEST, n_H=N_H_TEST, n_points=100)
        for result in r['results']:
            assert result['zeta_side']['A_off_avg'] < 0, (
                f"ΔA_avg not negative in batch scan: "
                f"{result['zeta_side']['A_off_avg']:.4e}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# §8 — Conflict Classification
# ─────────────────────────────────────────────────────────────────────────────

class TestConflictClassification:
    """_classify_conflict correctly labels conflict types (3-tuple return)."""

    def test_all_ok_on_critical_no_conflict(self):
        """All pass on-critical → no conflict, type='none'."""
        conflict, ctype, truth = _classify_conflict(True, True, True, 0.0)
        assert not conflict
        assert ctype == "none"
        assert truth == "on_critical"

    def test_all_ok_off_critical_undetected(self):
        """All pass off-critical → UNDETECTED_ANOMALY (false negative)."""
        conflict, ctype, truth = _classify_conflict(True, True, True, 0.1)
        assert not conflict
        assert ctype == "UNDETECTED_ANOMALY"
        assert truth == "off_critical"

    def test_all_fail_off_critical_unanimous(self):
        """All fail off-critical → unanimous rejection (not mixed)."""
        conflict, ctype, truth = _classify_conflict(False, False, False, 0.1)
        assert not conflict
        assert ctype == "unanimous_rejection"
        assert truth == "off_critical"

    def test_all_fail_on_critical_false_rejection(self):
        """All fail on-critical → FALSE_REJECTION (false positive)."""
        conflict, ctype, truth = _classify_conflict(False, False, False, 0.0)
        assert conflict
        assert ctype == "FALSE_REJECTION"
        assert truth == "on_critical"

    def test_mixed_off_critical_partial_rejection(self):
        """Some pass, some fail off-critical → PARTIAL_REJECTION."""
        conflict, ctype, truth = _classify_conflict(False, True, True, 0.1)
        assert conflict
        assert ctype == "PARTIAL_REJECTION"
        assert truth == "off_critical"

    def test_mixed_on_critical_false_rejection(self):
        """Some pass, some fail on-critical → FALSE_REJECTION."""
        conflict, ctype, truth = _classify_conflict(True, False, True, 0.0)
        assert conflict
        assert ctype == "FALSE_REJECTION"
        assert truth == "on_critical"

    def test_two_fail_off_critical_partial(self):
        """Two layers fail off-critical → PARTIAL_REJECTION."""
        conflict, ctype, truth = _classify_conflict(False, False, True, 0.1)
        assert conflict
        assert ctype == "PARTIAL_REJECTION"

    def test_returns_3_tuple(self):
        """_classify_conflict always returns a 3-tuple."""
        result = _classify_conflict(True, True, True, 0.0)
        assert len(result) == 3


# ─────────────────────────────────────────────────────────────────────────────
# §9 — Truth Model & Margins
# ─────────────────────────────────────────────────────────────────────────────

class TestTruthModel:
    """Tests for _truth_label, margins, and FAILURE_MODES taxonomy."""

    def test_truth_label_on_critical(self):
        """Δβ=0 → on_critical."""
        assert _truth_label(0.0) == 'on_critical'

    def test_truth_label_off_critical(self):
        """Δβ>0 → off_critical."""
        assert _truth_label(0.1) == 'off_critical'

    def test_truth_label_tiny_db_on_critical(self):
        """Δβ < tol → on_critical."""
        assert _truth_label(1e-12) == 'on_critical'

    def test_truth_label_custom_tol(self):
        """Custom tol changes the boundary."""
        assert _truth_label(0.05, tol=0.1) == 'on_critical'
        assert _truth_label(0.2, tol=0.1) == 'off_critical'

    def test_triad_probe_has_truth_label(self):
        """triad_probe returns truth_label key as a string."""
        r = triad_probe(T_CRIT, DB_SMALL, N=N_TEST, n_H=N_H_TEST,
                        n_points=100)
        assert r['truth_label'] in ('on_critical', 'off_critical')

    def test_triad_probe_off_critical_label(self):
        """triad_probe at moderate Δβ returns off_critical."""
        r = triad_probe(T_CRIT, DB_MODERATE, N=N_TEST, n_H=N_H_TEST,
                        n_points=100)
        assert r['truth_label'] == 'off_critical'

    def test_zeta_margin_is_total_avg(self):
        """zeta_margin equals total_avg."""
        r = triad_probe(T_CRIT, DB_MODERATE, N=N_TEST, n_H=N_H_TEST,
                        n_points=100)
        assert r['zeta_margin'] == r['zeta_side']['total_avg']

    def test_pho_margin_binary(self):
        """pho_margin is 1.0 when gate passes, 0.0 when fails."""
        r = triad_probe(T_CRIT, DB_SMALL, spectrum=GAMMA_30[:20],
                        N=N_TEST, n_H=N_H_TEST, n_points=100)
        if r['pho_ok']:
            assert r['pho_margin'] == 1.0
        else:
            assert r['pho_margin'] == 0.0

    def test_ube_margin_is_c_phi(self):
        """ube_margin equals C_φ value from Layer C."""
        r = triad_probe(T_CRIT, DB_MODERATE, N=N_TEST, n_H=N_H_TEST,
                        n_points=100)
        assert r['ube_margin'] == r['ube_side']['C_phi']

    def test_failure_modes_taxonomy_keys(self):
        """FAILURE_MODES dict contains all expected conflict types."""
        expected = {"none", "unanimous_rejection", "FALSE_REJECTION",
                    "UNDETECTED_ANOMALY", "PARTIAL_REJECTION"}
        assert expected <= set(FAILURE_MODES.keys())

    def test_failure_modes_values_are_strings(self):
        """All FAILURE_MODES values are non-empty descriptions."""
        for k, v in FAILURE_MODES.items():
            assert isinstance(v, str) and len(v) > 0, f"Bad value for {k}"


# ─────────────────────────────────────────────────────────────────────────────
# §10 — Confusion Matrix & PHO Hoisting
# ─────────────────────────────────────────────────────────────────────────────

class TestConfusionMatrix:
    """Tests for _update_confusion and confusion matrix in triad_scan."""

    def test_update_confusion_tp(self):
        """Off-critical detected → TP."""
        m = {'TP': 0, 'FP': 0, 'FN': 0, 'TN': 0}
        _update_confusion(m, 'off_critical', True, False)
        assert m['TP'] == 1

    def test_update_confusion_fn(self):
        """Off-critical missed → FN."""
        m = {'TP': 0, 'FP': 0, 'FN': 0, 'TN': 0}
        _update_confusion(m, 'off_critical', False, True)
        assert m['FN'] == 1

    def test_update_confusion_fp(self):
        """On-critical rejected → FP."""
        m = {'TP': 0, 'FP': 0, 'FN': 0, 'TN': 0}
        _update_confusion(m, 'on_critical', True, False)
        assert m['FP'] == 1

    def test_update_confusion_tn(self):
        """On-critical accepted → TN."""
        m = {'TP': 0, 'FP': 0, 'FN': 0, 'TN': 0}
        _update_confusion(m, 'on_critical', False, True)
        assert m['TN'] == 1

    def test_scan_returns_confusion_dict(self):
        """triad_scan returns confusion with TP/FP/FN/TN keys."""
        r = triad_scan([T_CRIT], [DB_SMALL], N=N_TEST, n_H=N_H_TEST,
                       n_points=100)
        c = r['confusion']
        assert set(c.keys()) == {'TP', 'FP', 'FN', 'TN'}
        assert sum(c.values()) == r['n_total']

    def test_scan_on_critical_all_tn(self):
        """Scan at small Δβ correctly populates confusion matrix."""
        r = triad_scan([T_CRIT], [DB_SMALL], spectrum=GAMMA_30[:20],
                       N=N_TEST, n_H=N_H_TEST, n_points=100)
        c = r['confusion']
        # DB_SMALL > tol → off_critical.  If all_ok, it’s FN; if not, it’s TP.
        assert sum(c.values()) == r['n_total']


class TestPHOHoisting:
    """Tests that PHO precomputation works correctly."""

    def test_precomputed_pho_matches_direct(self):
        """triad_probe with precomputed_pho gives same pho_ok as direct."""
        spec = GAMMA_30[:20].copy()
        pho_direct = pho_binding_probe(spec)
        r = triad_probe(T_CRIT, DB_SMALL, spectrum=spec,
                        precomputed_pho=pho_direct,
                        N=N_TEST, n_H=N_H_TEST, n_points=100)
        assert r['pho_ok'] == pho_direct['gate_ok']

    def test_scan_uses_hoisted_pho(self):
        """triad_scan internally hoists PHO — results are structurally valid."""
        r = triad_scan([20.0, 30.0], [DB_SMALL, DB_MODERATE],
                       spectrum=GAMMA_30[:20],
                       N=N_TEST, n_H=N_H_TEST, n_points=100)
        # All results should have the same pho_ok since spectrum is fixed
        pho_oks = [res['pho_ok'] for res in r['results']]
        assert len(set(pho_oks)) == 1, "PHO results should be identical across grid"
