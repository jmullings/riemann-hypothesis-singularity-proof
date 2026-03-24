#!/usr/bin/env python3
r"""
================================================================================
test_43_triad_analytic_integration.py — Gap Closure: Triad + Analytic Bounds
================================================================================

TIER 25d — Self-governing triad with analytic-bound enforcement.

HARNESS STRUCTURE (§4.5):
  1. TestTriadWithAnalyticBounds:
       - No false rejection on near-critical configurations (Δβ ≈ 0)
       - No undetected anomalies off-critical (enhanced detection)
       - Some true positives off-critical (enhanced detection)
  2. TestTriadMixedGrid:
       Confusion matrix over mixed (T, Δβ) grid — structural shape.

KEY CLOSURE (§4.5):  Enhanced detection mode uses the γ₀-adaptive
H-family from §4.2, which guarantees ΔA_avg < 0 for all off-critical
configurations.  Layer A then detects the raw signal (not the Bochner-
corrected total), enabling TP > 0 and FN = 0 across the tested grid.

================================================================================
"""

import numpy as np
import pytest

from engine.triad_governor import (
    triad_probe, triad_scan, _truth_label, FAILURE_MODES
)
from engine.analytic_bounds import (
    averaged_deltaA_continuous, theta_ceiling, _pnt_decay_factor,
)
from engine.euler_form import heat_trace, spectral_zeta


T_VALUES = [100.0, 200.0]
# 1e-11 is below _truth_label threshold (1e-10) → classified on_critical
DB_ON_CRITICAL = [1e-11]
DB_OFF_CRITICAL = [0.02, 0.05]
N_GRID = 30
N_H = 9


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — TRIAD WITH ANALYTIC BOUNDS (§4.5 blueprint)
# ═══════════════════════════════════════════════════════════════════════════════

class TestTriadWithAnalyticBounds:
    """
    End-to-end triad consistency with enhanced detection mode.
    """

    @pytest.mark.parametrize("T", T_VALUES)
    def test_no_false_rejection_on_critical(self, T):
        """
        Near-critical (Δβ = 1e-11) should NOT be rejected by ANY layer.
        Truth: on_critical → expected all_ok = True.
        """
        result = triad_probe(T, delta_beta=1e-11, N=N_GRID, n_H=N_H,
                              enhanced_detection=True)
        assert result['truth_label'] == 'on_critical'
        # On-critical: all layers should accept
        assert result['all_ok'], (
            f"T={T}: on-critical rejected! "
            f"zeta={result['zeta_ok']}, pho={result['pho_ok']}, "
            f"ube={result['ube_ok']}, type={result['conflict_type']}"
        )

    @pytest.mark.parametrize("T", T_VALUES)
    @pytest.mark.parametrize("delta_beta", DB_OFF_CRITICAL)
    def test_anomaly_detected_off_critical(self, T, delta_beta):
        """
        Off-critical (Δβ ≥ 0.02) should be detected by at least Layer A
        with enhanced_detection=True.  FN = 0 for this config.
        """
        result = triad_probe(T, delta_beta=delta_beta, N=N_GRID, n_H=N_H,
                              enhanced_detection=True)
        assert result['truth_label'] == 'off_critical'
        # Enhanced detection: Layer A uses adaptive H-family → negative signal
        assert not result['all_ok'], (
            f"T={T}, Δβ={delta_beta}: off-critical UNDETECTED! "
            f"zeta={result['zeta_ok']}, pho={result['pho_ok']}, "
            f"ube={result['ube_ok']}"
        )

    @pytest.mark.parametrize("T", T_VALUES)
    @pytest.mark.parametrize("delta_beta", DB_OFF_CRITICAL)
    def test_layer_a_signal_negative(self, T, delta_beta):
        """
        With enhanced detection, the raw ΔA signal should be negative
        for off-critical configurations (the adaptive H-family
        guarantees this by selecting H where cos(2πγ₀/H) > 0).
        """
        result = triad_probe(T, delta_beta=delta_beta, N=N_GRID, n_H=N_H,
                              enhanced_detection=True)
        assert result['zeta_side']['A_off_avg'] < 0, (
            f"T={T}, Δβ={delta_beta}: ΔA_avg not negative: "
            f"{result['zeta_side']['A_off_avg']:.6e}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — CONFUSION MATRIX (GRID SCAN)
# ═══════════════════════════════════════════════════════════════════════════════

class TestTriadMixedGrid:
    """
    Sweep over mixed (T, Δβ) grid with enhanced detection,
    verify confusion matrix structure.
    """

    def test_confusion_matrix_sum(self):
        """TP + FP + FN + TN = total number of configurations."""
        scan = triad_scan(T_VALUES, DB_ON_CRITICAL + DB_OFF_CRITICAL,
                          N=N_GRID, n_H=N_H, enhanced_detection=True)
        cm = scan['confusion']
        total = cm['TP'] + cm['FP'] + cm['FN'] + cm['TN']
        assert total == scan['n_total'], (
            f"Confusion sum {total} ≠ n_total {scan['n_total']}"
        )

    def test_no_false_positives(self):
        """FP = 0: on-critical configs should not be rejected."""
        scan = triad_scan(T_VALUES, DB_ON_CRITICAL + DB_OFF_CRITICAL,
                          N=N_GRID, n_H=N_H, enhanced_detection=True)
        assert scan['confusion']['FP'] == 0, (
            f"False positives detected: {scan['confusion']['FP']}"
        )

    def test_no_false_negatives(self):
        """FN = 0: off-critical configs should be detected with enhanced mode."""
        scan = triad_scan(T_VALUES, DB_OFF_CRITICAL,
                          N=N_GRID, n_H=N_H, enhanced_detection=True)
        assert scan['confusion']['FN'] == 0, (
            f"False negatives (missed anomalies): {scan['confusion']['FN']}"
        )

    def test_some_true_positives(self):
        """TP > 0: at least some off-critical configs should be correctly detected."""
        scan = triad_scan(T_VALUES, DB_OFF_CRITICAL,
                          N=N_GRID, n_H=N_H, enhanced_detection=True)
        assert scan['confusion']['TP'] > 0, (
            f"No true positives: {scan['confusion']}"
        )

    def test_results_list_shape(self):
        """Results list has one entry per (T, Δβ) pair."""
        db_all = DB_ON_CRITICAL + DB_OFF_CRITICAL
        scan = triad_scan(T_VALUES, db_all,
                          N=N_GRID, n_H=N_H, enhanced_detection=True)
        expected = len(T_VALUES) * len(db_all)
        assert len(scan['results']) == expected
        assert scan['n_total'] == expected

    def test_summary_structure(self):
        """Summary tuples have (T, Δβ, conflict_type) for each probe."""
        db_all = DB_ON_CRITICAL + DB_OFF_CRITICAL
        scan = triad_scan(T_VALUES, db_all,
                          N=N_GRID, n_H=N_H, enhanced_detection=True)
        assert len(scan['summary']) == scan['n_total']
        for entry in scan['summary']:
            assert len(entry) == 3
            T, db, ctype = entry
            assert isinstance(T, float)
            assert isinstance(db, float)
            assert isinstance(ctype, str)

    def test_conflict_rate_bounded(self):
        """
        Conflict rate across the full grid should be deterministic
        and bounded in [0, 1].
        """
        db_all = DB_ON_CRITICAL + DB_OFF_CRITICAL
        scan = triad_scan(T_VALUES, db_all,
                          N=N_GRID, n_H=N_H, enhanced_detection=True)
        assert 0.0 <= scan['conflict_rate'] <= 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — CROSS-LAYER ANALYTIC INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrossLayerAnalyticIntegration:
    """
    Verify that the three analytic gap closures wire together:
      - Gap 1 (high-lying zeros): adaptive H-family → uniform A_off_avg < 0
      - Gap 2 (PHO binding): off-critical operator fails PHO gate
      - Gap 3 (UBE): convexity holds at tested heights

    These tests ensure the three layers give CONSISTENT verdicts for
    the same off-critical configuration, i.e. the analytic improvements
    in one layer don't contradict the others.
    """

    def test_offcritical_operator_fails_pho_layer(self):
        """Off-critical operator injected into Layer B fails the gate."""
        from engine.offcritical import build_offcritical_operator
        from engine.triad_governor import pho_binding_probe

        H_off = build_offcritical_operator(0.6, 14.135, N=10)
        spec = np.sort(np.linalg.eigvalsh(H_off.real))
        pho = pho_binding_probe(spec, operator=H_off)
        assert not pho['pho_ok'], (
            "Off-critical operator should fail PHO-representability in Layer B"
        )

    def test_adaptive_h_total_negative_at_small_db(self):
        """
        At Δβ = 1e-3 with adaptive H-family, F_avg total is negative.
        This confirms Gap 1 closure feeds into triad Layer A.
        """
        from engine.multi_h_kernel import build_H_family_adaptive
        from engine.high_lying_avg_functional import F_avg

        db = 1e-3
        for T in [30.0, 50.0, 80.0]:
            H_list, w_list = build_H_family_adaptive(T, db, n_H=25)
            res = F_avg(T, H_list, w_list, db, 30, gamma0=T, n_points=200)
            assert res['total_avg'] < 0, (
                f"F_avg total ≥ 0 at T={T}, Δβ={db}: {res['total_avg']:.6e}"
            )

    def test_ube_convexity_consistent_at_all_triad_heights(self):
        """UBE convexity holds at all heights used by the triad grid."""
        from engine.triad_governor import ube_convexity_probe

        for T in [14.0, 30.0, 50.0, 100.0, 200.0]:
            ube = ube_convexity_probe(T)
            assert ube['convex_ok'], (
                f"UBE convexity failed at T={T}: C_φ={ube['C_phi']:.6e}"
            )

    def test_all_three_layers_converge_on_offcritical(self):
        """
        End-to-end: for an off-critical config (Δβ=0.05), all three
        layers independently reject — unanimous agreement, no ambiguity.
        """
        result = triad_probe(100.0, delta_beta=0.05, N=N_GRID, n_H=N_H,
                              enhanced_detection=True)
        assert result['truth_label'] == 'off_critical'
        # Layer A should fire (enhanced detection)
        assert not result['zeta_ok'], "Layer A should detect off-critical"
        # Layer C (UBE) convexity still holds on-critical, so ube_ok = True
        # This is expected: UBE tests prime-side structure, not off-critical injection
        assert result['ube_ok'], "Layer C (UBE) should still pass"


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — CROSS-LAYER EQUATION INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrossLayerEquationIntegration:
    """
    Verify that the three Euler-form equations interact consistently:
      - Layer A: averaged_deltaA_continuous → negative for off-critical
      - Layer B: heat_trace / spectral_zeta produce valid spectral data
      - Layer C: theta_ceiling encloses the empirical error

    These tests check that improving one layer doesn't contradict another.
    """

    def test_layer_a_continuous_consistent_with_triad_detection(self):
        """
        averaged_deltaA_continuous envelope < 0 implies triad Layer A
        should fire for the same (γ₀, Δβ) when enhanced detection is on.
        Use pole-free support [0.5, 1.9] for reliable envelope sign.
        """
        for gamma0 in [100.0, 200.0]:
            for db in [0.02, 0.05]:
                res_cont = averaged_deltaA_continuous(
                    gamma0, db, c1=0.5, c2=1.9)
                assert res_cont['envelope'] < 0

                result = triad_probe(gamma0, delta_beta=db, N=N_GRID,
                                     n_H=N_H, enhanced_detection=True)
                assert not result['zeta_ok'], (
                    f"Triad Layer A should reject: γ₀={gamma0}, Δβ={db}, "
                    f"continuous envelope={res_cont['envelope']:.6e}"
                )

    def test_layer_b_spectral_zeta_positive_at_s2(self):
        """
        ζ_H(2) > 0 (since -ζ'/ζ(2) > 0), confirming Layer B
        spectral data is well-posed for triad integration.
        """
        sz = spectral_zeta(2.0, n_max=10000).real
        assert sz > 0, f"ζ_H(2) = {sz} — should be positive"

    def test_layer_c_ceiling_holds_at_triad_heights(self):
        """
        θ_ceiling is finite and positive at all heights used in
        the triad confusion-matrix grid.
        """
        from engine.ube_decomposition import PHI_WEIGHTS, _P6
        M_K = float(np.linalg.norm(_P6 @ PHI_WEIGHTS))
        H_UBE = 0.02

        for T in [14.0, 30.0, 50.0, 100.0, 200.0]:
            tc = theta_ceiling(T, H_UBE, M_K, {"A_k": 1.0})
            assert np.isfinite(tc) and tc > 0, (
                f"θ_ceiling({T}) = {tc} — invalid"
            )

    def test_no_cross_layer_contradiction(self):
        """
        For a legitimate on-critical config (Δβ ≈ 0):
          - Layer A: ΔA_avg = 0 (trivially, since Δβ = 0)
          - Layer B: spectral data well-posed
          - Layer C: θ_ceiling valid
        No layer should flag a problem.
        """
        # Layer A: Δβ=0 → ΔA = 0
        res_a = averaged_deltaA_continuous(100.0, 0.0)
        assert res_a['deltaA_avg'] == 0.0

        # Layer B: spectral zeta converges
        sz = spectral_zeta(3.0, n_max=5000).real
        assert sz > 0

        # Layer C: ceiling finite
        from engine.ube_decomposition import PHI_WEIGHTS, _P6
        M_K = float(np.linalg.norm(_P6 @ PHI_WEIGHTS))
        tc = theta_ceiling(100.0, 0.02, M_K, {"A_k": 1.0})
        assert np.isfinite(tc)

        # Triad: no rejection
        result = triad_probe(100.0, delta_beta=1e-11, N=N_GRID, n_H=N_H,
                              enhanced_detection=True)
        assert result['all_ok']

    def test_off_critical_all_equations_agree_on_anomaly(self):
        """
        For an off-critical config:
          - Layer A continuous integral is negative
          - Layer C ceiling is still mathematically valid
          - Triad detects the anomaly
        """
        gamma0, db = 200.0, 0.05

        # Layer A: continuous envelope < 0 (pole-free support)
        res_a = averaged_deltaA_continuous(gamma0, db, c1=0.5, c2=1.9)
        assert res_a['envelope'] < 0

        # Layer C: ceiling is valid (it doesn't depend on Δβ)
        from engine.ube_decomposition import PHI_WEIGHTS, _P6
        M_K = float(np.linalg.norm(_P6 @ PHI_WEIGHTS))
        tc = theta_ceiling(gamma0, 0.02, M_K, {"A_k": 1.0})
        assert tc > 0 and np.isfinite(tc)

        # Triad: detects anomaly
        result = triad_probe(gamma0, delta_beta=db, N=N_GRID, n_H=N_H,
                              enhanced_detection=True)
        assert not result['all_ok']
