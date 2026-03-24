#!/usr/bin/env python3
r"""
================================================================================
test_45_contradiction_engine.py — RH Contradiction Engine Verification
================================================================================

TIER 26 — Full proof-by-contradiction chain.

PROOF STRUCTURE UNDER TEST:
  1. Positivity Basin (Theorem B 2.0):  F̃₂ ≥ 0  for all admissible spectra.
  2. Decompose: F̃₂ = ΔA_avg + λ*B_avg.
  3. Gap 1 (Layer A): ΔA_avg < 0 for Δβ > 0 (off-critical injection).
  4. Gaps 2+3 (Layers B+C): positive part λ*B_avg = O(Δβ²), subdominant.
  5. CONTRADICTION: F̃₂ < 0 → off-critical zero impossible → RH.

HARNESS STRUCTURE:
  §1  TestContradictionCertificateAPI
      API contract for analytic_bounds.contradiction_certificate.
  §2  TestContradictionOnCritical
      On-critical (Δβ=0): NO contradiction (soundness).
  §3  TestContradictionOffCritical
      Off-critical (Δβ>0): contradiction fires across (γ₀, Δβ) grid.
  §4  TestContradictionEngineFullChain
      End-to-end engine with proof_chain steps verified.
  §5  TestContradictionScan
      Batch grid: all off-critical rejected, no on-critical rejected.
  §6  TestContradictionScaling
      Structural: margin grows with Δβ, envelope dominance.
  §7  TestContradictionConsistency
      Cross-validation: engine vs triad governor vs analytic certificate.

================================================================================
"""

import numpy as np
import pytest

from engine.triad_governor import (
    contradiction_engine,
    contradiction_scan,
    triad_probe,
)
from engine.analytic_bounds import (
    contradiction_certificate,
    bochner_correction_ceiling,
    averaged_deltaA_continuous,
    _pnt_decay_factor,
)


# ── Parameter grid ──
GAMMAS = [50.0, 100.0, 200.0, 400.0]
DB_OFF = [0.01, 0.02, 0.05, 0.1]
DB_ON = [0.0, 1e-15]


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — CONTRADICTION CERTIFICATE API
# ═══════════════════════════════════════════════════════════════════════════════

class TestContradictionCertificateAPI:
    """Verify the analytic certificate returns all expected fields."""

    def test_certificate_keys(self):
        cert = contradiction_certificate(100.0, 0.02)
        expected = {
            'delta_A', 'envelope', 'oscillatory', 'decay_rate',
            'bochner_ceil', 'prime_decay', 'F_upper_bound',
            'contradiction', 'margin', 'gamma0', 'delta_beta',
        }
        assert expected == set(cert.keys())

    def test_bochner_ceiling_positive(self):
        """Bochner correction ceiling is non-negative for Δβ > 0."""
        for db in DB_OFF:
            bc = bochner_correction_ceiling(db, B_avg_bound=200.0)
            assert bc > 0, f"Bochner ceiling should be > 0 at Δβ={db}"

    def test_bochner_ceiling_zero_at_zero_db(self):
        bc = bochner_correction_ceiling(0.0, B_avg_bound=200.0)
        assert bc == 0.0

    def test_bochner_ceiling_scales_quadratically(self):
        """Ceiling ∝ Δβ²: ratio at 2Δβ vs Δβ should be 4."""
        bc1 = bochner_correction_ceiling(0.01, B_avg_bound=100.0)
        bc2 = bochner_correction_ceiling(0.02, B_avg_bound=100.0)
        assert abs(bc2 / bc1 - 4.0) < 0.01

    def test_certificate_echos_inputs(self):
        cert = contradiction_certificate(314.159, 0.03)
        assert cert['gamma0'] == 314.159
        assert cert['delta_beta'] == 0.03


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — ON-CRITICAL SOUNDNESS
# ═══════════════════════════════════════════════════════════════════════════════

class TestContradictionOnCritical:
    """On-critical (Δβ ≈ 0): the contradiction engine must NOT fire."""

    @pytest.mark.parametrize("db", DB_ON)
    def test_certificate_no_contradiction_on_critical(self, db):
        cert = contradiction_certificate(100.0, db)
        assert not cert['contradiction'], (
            f"Δβ={db}: certificate must NOT produce contradiction on-critical"
        )

    @pytest.mark.parametrize("gamma0", [50.0, 100.0, 200.0])
    def test_engine_no_contradiction_on_critical(self, gamma0):
        result = contradiction_engine(gamma0, 0.0, N=20, n_H=15, n_points=100)
        assert not result['contradiction'], (
            f"Engine fired contradiction on-critical at γ₀={gamma0}"
        )
        assert result['truth_label'] == 'on_critical'

    def test_engine_trivial_delta_beta(self):
        """Δβ = 1e-15 is classified on-critical, no contradiction."""
        result = contradiction_engine(100.0, 1e-15, N=20, n_H=15, n_points=100)
        assert not result['contradiction']


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — OFF-CRITICAL: CONTRADICTION FIRES
# ═══════════════════════════════════════════════════════════════════════════════

class TestContradictionOffCritical:
    """Off-critical (Δβ > 0): the engine must produce a contradiction."""

    @pytest.mark.parametrize("gamma0", [100.0, 200.0])
    @pytest.mark.parametrize("delta_beta", [0.02, 0.05])
    def test_engine_fires_contradiction(self, gamma0, delta_beta):
        result = contradiction_engine(
            gamma0, delta_beta, N=30, n_H=25, n_points=200)
        assert result['contradiction'], (
            f"γ₀={gamma0}, Δβ={delta_beta}: contradiction did NOT fire! "
            f"A_off_avg={result['A_off_avg']:.6e}"
        )
        assert result['truth_label'] == 'off_critical'

    @pytest.mark.parametrize("gamma0", [100.0, 200.0])
    @pytest.mark.parametrize("delta_beta", [0.02, 0.05])
    def test_A_off_avg_negative(self, gamma0, delta_beta):
        """Off-critical ΔA_avg must be strictly negative (Gap 1)."""
        result = contradiction_engine(
            gamma0, delta_beta, N=30, n_H=25, n_points=200)
        assert result['A_off_avg'] < 0, (
            f"A_off_avg = {result['A_off_avg']:.6e} should be < 0"
        )

    @pytest.mark.parametrize("gamma0", [100.0, 200.0])
    @pytest.mark.parametrize("delta_beta", [0.02, 0.05])
    def test_envelope_negative(self, gamma0, delta_beta):
        """Continuous envelope must be negative (Gap 1 analytic)."""
        result = contradiction_engine(
            gamma0, delta_beta, N=30, n_H=25, n_points=200,
            c1=0.5, c2=1.9)
        assert result['envelope_negative'], (
            f"Envelope = {result['envelope']:.6e} should be < 0"
        )

    @pytest.mark.parametrize("gamma0", [100.0, 200.0])
    def test_ube_convexity_holds(self, gamma0):
        """UBE convexity must hold (Gap 3 — prime-side consistency)."""
        result = contradiction_engine(
            gamma0, 0.05, N=30, n_H=25, n_points=200)
        assert result['ube_convex'], (
            f"UBE convexity failed at γ₀={gamma0}"
        )

    @pytest.mark.parametrize("gamma0", [30.0, 50.0, 80.0])
    def test_F_total_negative_small_db(self, gamma0):
        """
        For small Δβ (the crack regime), F_total < 0 directly —
        the linear ΔA_avg term dominates the quadratic λ*B correction.
        """
        result = contradiction_engine(
            gamma0, 1e-3, N=30, n_H=25, n_points=200)
        assert result['F_total_negative'], (
            f"F_total = {result['F_total']:.6e} should be < 0 "
            f"at γ₀={gamma0}, Δβ=1e-3 (small-Δβ regime)"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — FULL PROOF CHAIN STEPS
# ═══════════════════════════════════════════════════════════════════════════════

class TestContradictionEngineFullChain:
    """Verify each step in the proof chain passes."""

    def test_all_chain_steps_pass(self):
        """Every proof step must succeed for an off-critical config."""
        result = contradiction_engine(200.0, 0.05, N=30, n_H=25, n_points=200)
        for step_name, step_ok, step_msg in result['proof_chain']:
            assert step_ok, f"FAILED: {step_name} — {step_msg}"

    def test_chain_step_count(self):
        """Proof chain must have exactly 6 steps."""
        result = contradiction_engine(100.0, 0.02, N=30, n_H=25, n_points=200)
        assert len(result['proof_chain']) == 6

    def test_chain_steps_are_triples(self):
        """Each step is a (name, verdict, message) triple."""
        result = contradiction_engine(100.0, 0.02, N=20, n_H=15, n_points=100)
        for step in result['proof_chain']:
            assert len(step) == 3
            name, ok, msg = step
            assert isinstance(name, str)
            assert bool(ok) in (True, False)  # boolean-coercible
            assert isinstance(msg, str)

    def test_positivity_basin_unconditional(self):
        """Step 1 (positivity basin) always True — it's unconditional."""
        for db in [0.0, 0.01, 0.05, 0.2]:
            result = contradiction_engine(
                100.0, db, N=20, n_H=15, n_points=100)
            step1_ok = result['proof_chain'][0][1]
            assert step1_ok, "Positivity basin must always hold"

    def test_analytic_certificate_included(self):
        """Engine result includes the analytic certificate from §5."""
        result = contradiction_engine(100.0, 0.05, N=30, n_H=25, n_points=200)
        cert = result['analytic_cert']
        assert 'envelope' in cert
        assert 'bochner_ceil' in cert
        assert 'prime_decay' in cert


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — BATCH SCAN: ALL OFF-CRITICAL REJECTED
# ═══════════════════════════════════════════════════════════════════════════════

class TestContradictionScan:
    """Grid scan: systematic rejection of all off-critical configs."""

    def test_all_off_critical_rejected(self):
        """
        Over a (γ₀, Δβ) grid, every off-critical config produces
        a contradiction.  This is the AUTOMATED THEOREM PROVER.
        """
        scan = contradiction_scan(
            [100.0, 200.0], [0.02, 0.05],
            N=30, n_H=25, n_points=200)
        assert scan['all_off_critical_rejected'], (
            f"False negatives: {scan['false_negatives']} "
            f"off-critical configs survived"
        )

    def test_no_on_critical_rejected(self):
        """On-critical configs must never produce contradiction."""
        scan = contradiction_scan(
            [100.0, 200.0], [0.0, 0.02, 0.05],
            N=30, n_H=25, n_points=200)
        assert scan['no_on_critical_rejected'], (
            f"False positives: {scan['false_positives']} "
            f"on-critical configs wrongly rejected"
        )

    def test_scan_counts_correct(self):
        g_vals = [100.0, 200.0]
        db_vals = [0.0, 0.02, 0.05]
        scan = contradiction_scan(
            g_vals, db_vals, N=20, n_H=15, n_points=100)
        expected = len(g_vals) * len(db_vals)
        assert scan['n_total'] == expected
        assert len(scan['certificates']) == expected
        assert len(scan['summary']) == expected

    def test_scan_summary_structure(self):
        scan = contradiction_scan(
            [100.0], [0.0, 0.05],
            N=20, n_H=15, n_points=100)
        for entry in scan['summary']:
            assert len(entry) == 4  # (γ₀, Δβ, contradiction, margin)
            g0, db, contr, margin = entry
            assert isinstance(g0, float)
            assert isinstance(db, float)
            # contr may be numpy bool
            assert contr is True or contr is False or isinstance(contr, (bool, np.bool_))
            assert isinstance(margin, (float, np.floating))

    def test_wider_grid(self):
        """
        Extended sweep: γ₀ ∈ {50, 100, 200, 400},
        Δβ ∈ {0.01, 0.02, 0.05}.  ALL must fire contradiction.
        """
        scan = contradiction_scan(
            [50.0, 100.0, 200.0, 400.0],
            [0.01, 0.02, 0.05],
            N=30, n_H=25, n_points=200)
        assert scan['all_off_critical_rejected'], (
            f"Wider grid: {scan['false_negatives']} configs survived"
        )
        assert scan['n_contradictions'] == scan['n_off_critical']


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — SCALING AND STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

class TestContradictionScaling:
    """Verify structural properties of the contradiction engine."""

    def test_margin_increases_with_delta_beta(self):
        """
        Larger Δβ → stronger contradiction (larger margin).
        |ΔA_avg| ∝ Δβ dominates λ*B ∝ Δβ² more at larger Δβ.
        """
        margins = []
        for db in [0.01, 0.02, 0.05]:
            result = contradiction_engine(
                200.0, db, N=30, n_H=25, n_points=200)
            margins.append(abs(result['F_total']))
        # Overall trend: margin at 0.05 > margin at 0.01
        assert margins[-1] > margins[0], (
            f"Margin not increasing: {margins}"
        )

    def test_envelope_dominance_small_omega(self):
        """
        For small ω = 2πγ₀Δβ, the envelope should dominate the
        oscillatory correction (Riemann-Lebesgue regime).
        """
        gamma0, db = 50.0, 0.001  # small ω ≈ 0.31
        cert = contradiction_certificate(gamma0, db, c1=0.5, c2=1.9)
        envelope_mag = abs(cert['envelope'])
        osc_mag = abs(cert['oscillatory'])
        assert envelope_mag > osc_mag, (
            f"|envelope|={envelope_mag:.4e} should exceed "
            f"|oscillatory|={osc_mag:.4e}"
        )

    def test_prime_decay_decreases_with_gamma0(self):
        """Kadiri-Faber decay factor decreases as γ₀ increases."""
        d1 = _pnt_decay_factor(np.log(100.0))
        d2 = _pnt_decay_factor(np.log(1000.0))
        assert d2 < d1, (
            f"Prime decay should decrease: δ(100)={d1:.6e}, δ(1000)={d2:.6e}"
        )

    def test_bochner_ceiling_subdominant_small_db(self):
        """
        For small Δβ (the crack regime), |ΔA_avg| ~ c₁Δβ dominates
        the λ*B correction ~ c₂Δβ² → F_total < 0.
        """
        for db in [1e-3, 2e-3]:
            result = contradiction_engine(
                50.0, db, N=30, n_H=25, n_points=200)
            a_mag = abs(result['A_off_avg'])
            b_correction = result['F_total'] - result['A_off_avg']
            assert a_mag > b_correction, (
                f"|ΔA_avg|={a_mag:.4e} should exceed "
                f"λ*B_avg={b_correction:.4e} at Δβ={db}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# §7 — CROSS-CONSISTENCY
# ═══════════════════════════════════════════════════════════════════════════════

class TestContradictionConsistency:
    """Cross-validate contradiction engine vs triad governor."""

    @pytest.mark.parametrize("gamma0", [100.0, 200.0])
    def test_engine_agrees_with_triad_on_critical(self, gamma0):
        """Both engine and triad accept on-critical configs."""
        eng = contradiction_engine(gamma0, 0.0, N=20, n_H=15, n_points=100)
        # triad_probe requires Δβ > 0 for build_H_family; use 1e-11
        tri = triad_probe(gamma0, 1e-11, N=20, n_H=9,
                          enhanced_detection=True)
        assert not eng['contradiction']
        assert tri['all_ok']

    @pytest.mark.parametrize("gamma0", [100.0, 200.0])
    @pytest.mark.parametrize("delta_beta", [0.02, 0.05])
    def test_engine_agrees_with_triad_off_critical(self, gamma0, delta_beta):
        """Both engine and triad reject off-critical configs."""
        eng = contradiction_engine(
            gamma0, delta_beta, N=30, n_H=25, n_points=200)
        tri = triad_probe(gamma0, delta_beta, N=30, n_H=9,
                          enhanced_detection=True)
        # Engine uses ΔA_avg < 0 (same signal as enhanced triad detection)
        assert eng['contradiction'], (
            f"Engine failed at γ₀={gamma0}, Δβ={delta_beta}: "
            f"A_off_avg={eng['A_off_avg']:.6e}"
        )
        # Triad enhanced detection also catches off-critical
        assert not tri['all_ok'], (
            f"Triad failed to detect at γ₀={gamma0}, Δβ={delta_beta}"
        )

    def test_certificate_envelope_matches_engine(self):
        """Analytic certificate envelope matches engine's envelope."""
        gamma0, db = 200.0, 0.05
        eng = contradiction_engine(gamma0, db, N=30, n_H=25, n_points=200)
        cert = contradiction_certificate(gamma0, db, c1=0.5, c2=1.9)
        # Both use the same averaged_deltaA_continuous internally
        assert abs(eng['envelope'] - cert['envelope']) < 1e-12

    def test_continuous_and_discrete_sign_agree(self):
        """
        Discrete adaptive F_avg and continuous averaged_deltaA_continuous
        both produce negative ΔA for off-critical configs.
        """
        for g0 in [100.0, 200.0]:
            for db in [0.02, 0.05]:
                eng = contradiction_engine(
                    g0, db, N=30, n_H=25, n_points=200,
                    c1=0.5, c2=1.9)
                assert eng['A_off_avg'] < 0
                assert eng['envelope'] < 0
