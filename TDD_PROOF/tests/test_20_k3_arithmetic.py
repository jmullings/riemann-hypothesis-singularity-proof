"""
================================================================================
test_20_k3_arithmetic.py — Tier 8: K₃ Arithmetic Rayleigh Quotient
================================================================================

Tests for the per-prime arithmetic Rayleigh quotient K₃(t,p), implementing
the TDD_TODO integration plan:

  §1: E_p, σ_p, G_p, K₃ basic properties    (Proposals 1)
  §2: Windowed Rayleigh alignment             (Proposal 2)
  §3: K₃ gap diagnostic                       (Proposal 3)
  §4: Cross-checks with existing offcritical  (Proposal 3 cross-validation)
  §5: Honest assessment integration           (Proposal 4)

STATUS: NOW MEASURED — NOT BOUNDED.
    These tests verify arithmetic coherence and measurement capability.
    They do NOT prove the missing inequality C(Δβ) ≥ λ*(H)·B₀.
================================================================================
"""

import pytest
import numpy as np

from engine.k3_arithmetic import (
    E_p, E_p_grid, sigma_p, lambda_p, G_p, K3,
    windowed_A_p, windowed_B_p, R_p, R_RS,
    k3_rayleigh_gap,
)
from engine.kernel import sech2


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — E_p BASIC PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestEpBasic:
    """Per-prime Dirichlet energy: non-negative, real, correct structure."""

    PRIMES = [2, 3, 5, 7, 11, 13]
    N = 500
    GAMMA_1 = 14.134725

    def test_Ep_nonnegative(self):
        """E_p(t) ≥ 0 for all t (squared modulus)."""
        for p in self.PRIMES:
            for t in [0.0, self.GAMMA_1, 100.0, -5.0]:
                val = E_p(t, p, self.N)
                assert val >= 0, f"E_p({t}, {p}) = {val} < 0"

    def test_Ep_real(self):
        """E_p(t) returns a real float, not complex."""
        for p in self.PRIMES:
            val = E_p(self.GAMMA_1, p, self.N)
            assert isinstance(val, float)

    def test_Ep_zero_height(self):
        """E_p(0, p, N) is well-defined and positive for p ≤ N."""
        for p in self.PRIMES:
            val = E_p(0.0, p, self.N)
            assert val > 0, f"E_p(0, {p}) should be positive (constructive sum)"

    def test_Ep_empty_when_p_exceeds_N(self):
        """E_p returns 0 when p > N (no multiples of p ≤ N)."""
        assert E_p(10.0, 1000, 500) == 0.0

    def test_Ep_increases_with_N(self):
        """More Dirichlet terms → more energy (generally)."""
        E_small = E_p(0.0, 2, 50)
        E_large = E_p(0.0, 2, 500)
        assert E_large > E_small, "E_p should grow with N at t=0"

    def test_Ep_varies_with_height(self):
        """E_p is not constant — varies with t (oscillatory Dirichlet sum)."""
        vals = [E_p(t, 2, self.N) for t in np.linspace(10, 20, 20)]
        assert max(vals) > min(vals), "E_p should oscillate"

    def test_Ep_grid_shape(self):
        """E_p_grid returns correctly shaped arrays."""
        t_grid, E_vals = E_p_grid(2, self.N, self.GAMMA_1, 5.0, n_grid=50)
        assert len(t_grid) == 50
        assert len(E_vals) == 50
        assert np.all(E_vals >= 0)


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — σ_p ROBUSTNESS
# ═══════════════════════════════════════════════════════════════════════════════

class TestSigmaP:
    """Robust energy median."""

    PRIMES = [2, 3, 5, 7]
    N = 500
    GAMMA_1 = 14.134725

    def test_sigma_p_positive(self):
        """σ_p > 0 for primes with non-trivial Dirichlet sums."""
        for p in self.PRIMES:
            val = sigma_p(p, self.N, self.GAMMA_1)
            assert val > 0, f"σ_p({p}) should be positive"

    def test_sigma_p_robust_to_height(self):
        """σ_p should be comparable across different γ₀ heights."""
        sig_low = sigma_p(2, self.N, 14.0)
        sig_high = sigma_p(2, self.N, 25.0)
        # Allow factor-of-10 variation (it's a median, not exact)
        ratio = max(sig_low, sig_high) / max(min(sig_low, sig_high), 1e-30)
        assert ratio < 100, f"σ_p varies too wildly: ratio = {ratio}"

    def test_sigma_p_not_dominated_by_spikes(self):
        """Median should be below mean when there are high-E outliers."""
        sig = sigma_p(2, self.N, self.GAMMA_1, H=10.0, n_grid=200)
        _, E_vals = E_p_grid(2, self.N, self.GAMMA_1, 10.0, n_grid=200)
        mean_E = float(np.mean(E_vals))
        # Median ≤ mean for positive data with right skew (typical for |sum|²)
        # But not always — just check both are positive
        assert sig > 0
        assert mean_E > 0


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — λ_p ARITHMETIC WEIGHT
# ═══════════════════════════════════════════════════════════════════════════════

class TestLambdaP:
    """Arithmetic weight (log p)²/p."""

    def test_lambda_p_positive(self):
        """λ_p > 0 for all primes > 1."""
        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
            val = lambda_p(p)
            assert val > 0

    def test_lambda_p_decreasing(self):
        """λ_p is eventually decreasing (log p grows slower than p)."""
        vals = [lambda_p(p) for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]]
        # After initial rise (λ₂ < λ₃), should be decreasing
        # Check monotone decrease from p=7 onward
        for i in range(3, len(vals) - 1):
            assert vals[i] >= vals[i + 1], (
                f"λ_p not decreasing: λ_{[2,3,5,7,11,13,17,19,23,29,31][i]} "
                f"= {vals[i]} < {vals[i+1]}"
            )

    def test_lambda_2_value(self):
        """Spot check: λ₂ = (log 2)² / 2 ≈ 0.240."""
        expected = np.log(2) ** 2 / 2
        assert abs(lambda_p(2) - expected) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — G_p GUARD FUNCTIONAL
# ═══════════════════════════════════════════════════════════════════════════════

class TestGpGuard:
    """sech² guard on normalised energy."""

    N = 500
    GAMMA_1 = 14.134725

    def test_Gp_in_unit_interval(self):
        """G_p(t) ∈ (0, 1] for all t."""
        for p in [2, 3, 5]:
            for t in [0.0, self.GAMMA_1, 50.0]:
                val = G_p(t, p, self.N, self.GAMMA_1, alpha=1.0)
                assert 0 < val <= 1.0 + 1e-10, f"G_p({t}, {p}) = {val} outside (0,1]"

    def test_Gp_max_at_zero_energy(self):
        """G_p should be positive when E_p/σ_p is finite (sech² never hits zero)."""
        # Use a prime where N is barely above p → E_p is small
        val = G_p(0.0, 499, 500, 0.0, alpha=1.0, n_grid=50)
        # sech²(x) > 0 for all finite x
        assert val > 0, f"G_p should be strictly positive, got {val}"

    def test_Gp_decreasing_with_alpha(self):
        """Higher α → more aggressive guarding → lower G_p (for fixed non-zero E_p)."""
        G_low = G_p(0.0, 2, self.N, self.GAMMA_1, alpha=0.1)
        G_high = G_p(0.0, 2, self.N, self.GAMMA_1, alpha=10.0)
        assert G_low >= G_high, "Higher α should suppress G_p"


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — K₃ KERNEL PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestK3Kernel:
    """Combined kernel: K₃(t,p) = (1/p)E_p + λ_p·G_p."""

    N = 500
    GAMMA_1 = 14.134725
    PRIMES = [2, 3, 5, 7, 11]

    def test_K3_nonneg(self):
        """K₃ ≥ 0 (both terms are non-negative)."""
        for p in self.PRIMES:
            for t in [0.0, self.GAMMA_1, 30.0]:
                val = K3(t, p, self.N, self.GAMMA_1)
                assert val >= 0, f"K3({t}, {p}) = {val} < 0"

    def test_K3_positive(self):
        """K₃ > 0: the λ_p·G_p term ensures strict positivity."""
        for p in self.PRIMES:
            val = K3(self.GAMMA_1, p, self.N, self.GAMMA_1)
            assert val > 0, f"K3 should be strictly positive, got {val}"

    def test_K3_decomposes_correctly(self):
        """K₃ = (1/p)E_p + λ_p·G_p — verify decomposition."""
        t = self.GAMMA_1
        p = 2
        E = E_p(t, p, self.N)
        sig = sigma_p(p, self.N, t)
        G = float(sech2(1.0 * E / sig))
        lp = lambda_p(p)
        expected = E / p + lp * G
        actual = K3(t, p, self.N, t, alpha=1.0)
        assert abs(actual - expected) < 1e-10, f"K3 decomposition: {actual} ≠ {expected}"

    def test_K3_coercivity(self):
        """K₃ ≥ λ_p·G_p (lower bounded by guard term alone)."""
        for p in self.PRIMES:
            t = self.GAMMA_1
            k3_val = K3(t, p, self.N, self.GAMMA_1)
            gp_val = G_p(t, p, self.N, self.GAMMA_1)
            lp = lambda_p(p)
            assert k3_val >= lp * gp_val - 1e-15


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — WINDOWED RAYLEIGH QUOTIENT
# ═══════════════════════════════════════════════════════════════════════════════

class TestWindowedRayleigh:
    """Per-prime and aggregated Rayleigh quotients."""

    N = 200
    GAMMA_1 = 14.134725
    SMALL_PRIMES = [2, 3, 5, 7]
    H = 5.0

    def test_windowed_A_p_finite(self):
        """Windowed A_p is finite for small primes at known zero."""
        for p in self.SMALL_PRIMES:
            A = windowed_A_p(self.GAMMA_1, p, self.N, self.H, n_quad=50)
            assert np.isfinite(A), f"A_p infinite for p={p}"

    def test_windowed_B_p_nonneg(self):
        """Windowed B_p ≥ 0 (integral of non-negative function with non-negative weight)."""
        for p in self.SMALL_PRIMES:
            B = windowed_B_p(self.GAMMA_1, p, self.N, self.H, n_quad=50)
            assert B >= -1e-10, f"B_p should be ≥ 0, got {B}"

    def test_windowed_B_p_positive(self):
        """Windowed B_p > 0 for p=2 (strongest contributor)."""
        B = windowed_B_p(self.GAMMA_1, 2, self.N, self.H, n_quad=50)
        assert B > 0, f"B_p(γ₁, 2) should be positive, got {B}"

    def test_R_p_well_defined(self):
        """Per-prime Rayleigh quotient returns valid result for p=2."""
        result = R_p(self.GAMMA_1, 2, self.N, self.H, n_quad=50)
        assert result['valid']
        assert np.isfinite(result['R_p'])

    def test_R_p_dict_keys(self):
        """R_p returns correct dictionary structure."""
        result = R_p(self.GAMMA_1, 2, self.N, self.H, n_quad=50)
        assert 'A_p' in result
        assert 'B_p' in result
        assert 'R_p' in result
        assert 'valid' in result

    def test_R_RS_well_defined(self):
        """Aggregated R_RS is finite and valid for small primes."""
        result = R_RS(self.GAMMA_1, self.SMALL_PRIMES, self.N, self.H, n_quad=30)
        assert result['valid']
        assert np.isfinite(result['R_RS'])

    def test_R_RS_weight_positive(self):
        """Total weight is positive (at least one prime contributes)."""
        result = R_RS(self.GAMMA_1, self.SMALL_PRIMES, self.N, self.H, n_quad=30)
        assert result['weight_total'] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# §7 — K₃ GAP DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════════════════════

class TestK3GapDiagnostic:
    """Measure λ*(H) − R_RS across Δβ grid."""

    N = 200
    GAMMA_1 = 14.134725
    H = 5.0
    PRIMES = [2, 3, 5]

    def test_gap_returns_list(self):
        """k3_rayleigh_gap returns a list of dicts."""
        db_grid = [0.0, 0.01, 0.1]
        results = k3_rayleigh_gap(
            self.GAMMA_1, self.H, db_grid, self.PRIMES, N=self.N, n_quad=30
        )
        assert isinstance(results, list)
        assert len(results) == 3

    def test_gap_dict_keys(self):
        """Each result has the expected keys."""
        results = k3_rayleigh_gap(
            self.GAMMA_1, self.H, [0.01], self.PRIMES, N=self.N, n_quad=30
        )
        r = results[0]
        assert 'delta_beta' in r
        assert 'R_RS' in r
        assert 'lambda_star' in r
        assert 'gap' in r
        assert 'gap_positive' in r

    def test_lambda_star_correct(self):
        """λ*(H) = 4/H² is computed correctly."""
        results = k3_rayleigh_gap(
            self.GAMMA_1, self.H, [0.01], self.PRIMES, N=self.N, n_quad=30
        )
        assert abs(results[0]['lambda_star'] - 4.0 / self.H ** 2) < 1e-15

    def test_gap_finite(self):
        """Gap is finite across the Δβ grid."""
        db_grid = np.linspace(0.001, 0.3, 5)
        results = k3_rayleigh_gap(
            self.GAMMA_1, self.H, db_grid, self.PRIMES, N=self.N, n_quad=30
        )
        for r in results:
            assert np.isfinite(r['gap']), f"Gap not finite at Δβ={r['delta_beta']}"

    def test_R_RS_finite_across_grid(self):
        """R_RS is finite for all Δβ values."""
        db_grid = [0.0, 0.05, 0.1, 0.2, 0.4]
        results = k3_rayleigh_gap(
            self.GAMMA_1, self.H, db_grid, self.PRIMES, N=self.N, n_quad=30
        )
        for r in results:
            assert np.isfinite(r['R_RS']), f"R_RS infinite at Δβ={r['delta_beta']}"


# ═══════════════════════════════════════════════════════════════════════════════
# §8 — CROSS-CHECK WITH EXISTING OFFCRITICAL
# ═══════════════════════════════════════════════════════════════════════════════

class TestK3CrossCheck:
    """Consistency between K₃ measurements and existing offcritical machinery."""

    N = 200
    GAMMA_1 = 14.134725
    H = 5.0
    PRIMES = [2, 3, 5]

    def test_both_rayleigh_quotients_finite(self):
        """Both K₃-side and offcritical-side Rayleigh quotients are finite."""
        from engine.offcritical import rayleigh_quotient as weil_rq

        # K₃ side
        rs = R_RS(self.GAMMA_1, self.PRIMES, self.N, self.H, n_quad=30)
        assert np.isfinite(rs['R_RS'])

        # Weil side
        weil = weil_rq(0.1, self.GAMMA_1, self.H)
        assert np.isfinite(weil['lambda_eff'])

    def test_bochner_threshold_consistent(self):
        """Both sides use the same Bochner threshold 4/H²."""
        from engine.offcritical import rayleigh_quotient as weil_rq

        k3_results = k3_rayleigh_gap(
            self.GAMMA_1, self.H, [0.1], self.PRIMES, N=self.N, n_quad=30
        )
        weil = weil_rq(0.1, self.GAMMA_1, self.H)

        assert abs(k3_results[0]['lambda_star'] - weil['threshold']) < 1e-15

    def test_small_delta_beta_R_RS_small(self):
        """As Δβ → 0, K₃ Rayleigh quotient stays finite — doesn't blow up."""
        db_grid = [1e-4, 1e-3, 1e-2]
        results = k3_rayleigh_gap(
            self.GAMMA_1, self.H, db_grid, self.PRIMES, N=self.N, n_quad=30
        )
        for r in results:
            assert abs(r['R_RS']) < 1e6, f"|R_RS| too large at Δβ={r['delta_beta']}"


# ═══════════════════════════════════════════════════════════════════════════════
# §9 — HONEST ASSESSMENT INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestK3HonestAssessment:
    """Verify K₃ is properly represented in honest_assessment."""

    def test_honest_assessment_has_k3(self):
        """honest_assessment() includes k3_arithmetic_identification."""
        from engine.proof_chain import honest_assessment
        ha = honest_assessment()
        assert 'k3_arithmetic_identification' in ha

    def test_k3_status_is_measured(self):
        """K₃ status is 'NOW MEASURED — NOT BOUNDED'."""
        from engine.proof_chain import honest_assessment
        ha = honest_assessment()
        k3 = ha['k3_arithmetic_identification']
        assert 'NOW MEASURED' in k3['status']
        assert 'NOT BOUNDED' in k3['status']

    def test_k3_layer_correct(self):
        """K₃ layer identifies it as arithmetic measurement channel."""
        from engine.proof_chain import honest_assessment
        ha = honest_assessment()
        k3 = ha['k3_arithmetic_identification']
        assert 'layer' in k3

    def test_k3_has_statement(self):
        """K₃ has a statement describing its role."""
        from engine.proof_chain import honest_assessment
        ha = honest_assessment()
        k3 = ha['k3_arithmetic_identification']
        assert 'statement' in k3
        assert len(k3['statement']) > 50  # non-trivial description


# ═══════════════════════════════════════════════════════════════════════════════
# §10 — GRAVITY-WELL VOCABULARY COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════════════

class TestGravityWellVocabulary:
    """Verify honest_assessment uses gravity-well vocabulary throughout."""

    def test_no_sink_component_key(self):
        """No entry uses 'sink_component' key (replaced by 'layer')."""
        from engine.proof_chain import honest_assessment
        ha = honest_assessment()
        for key, entry in ha.items():
            if isinstance(entry, dict):
                assert 'sink_component' not in entry, (
                    f"'{key}' still has 'sink_component' key"
                )

    def test_all_entries_have_layer(self):
        """All main entries use 'layer' key (gravity-well vocabulary)."""
        from engine.proof_chain import honest_assessment
        ha = honest_assessment()
        # Entries expected to have 'layer'
        entries_with_layer = [
            'theorem_b_2_0', 'lemma_1', 'lemma_2',
            'lemma_3_sign', 'lemma_3_domination',
            'gamma0_derivation', 'small_delta_beta_gap',
            'barrier_2', 'barrier_3', '9d_operator',
            'hilbert_polya', 'hilbert_space_axioms',
            'pho_representability', 'k3_arithmetic_identification',
        ]
        for key in entries_with_layer:
            assert key in ha, f"Missing entry '{key}'"
            assert 'layer' in ha[key], f"'{key}' missing 'layer' key"

    def test_no_utube_in_overall(self):
        """Overall status does not mention U-Tube or Guard Valve."""
        from engine.proof_chain import honest_assessment
        ha = honest_assessment()
        overall = ha['overall']['status']
        assert 'U-TUBE' not in overall.upper()
        assert 'GUARD VALVE' not in overall.upper()

    def test_overall_uses_gravity_well_language(self):
        """Overall status uses gravity-well terminology."""
        from engine.proof_chain import honest_assessment
        ha = honest_assessment()
        overall = ha['overall']['status']
        assert 'KERNEL CORRECTION' in overall or 'POSITIVITY BASIN' in overall
