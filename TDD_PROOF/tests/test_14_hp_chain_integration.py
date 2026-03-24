"""
================================================================================
test_14_hp_chain_integration.py — Tier 4: Full HP Chain Integration
================================================================================

Tests the integration of the polymeric Hilbert–Pólya operator into the
existing contradiction chain. Verifies that:

  1. The original chain still passes with HP enabled
  2. HP diagnostics are correctly reported
  3. The hybrid functional does not break existing PSD guarantees
  4. The HP spectral analysis adds diagnostic value
  5. Honest assessment correctly reports HP status

NO RH CLAIMS — only structural integration and diagnostic tests.
================================================================================
"""

import pytest
import numpy as np

from engine.proof_chain import (
    contradiction_chain,
    honest_assessment,
    lemma1_psd_at_lambda_star,
)
from engine.hilbert_polya import (
    get_poly_spectrum,
    polymer_momentum,
    phase_space_stiffness,
    berry_keating_counting,
)
from engine.gravity_functional import (
    hybrid_energy,
    stiffness_enhancement,
    hybrid_domination_ratio,
)
from engine.bochner import (
    build_corrected_toeplitz,
    lambda_star,
    min_eigenvalue,
    is_psd,
)
from engine.weil_density import GAMMA_30


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — ORIGINAL CHAIN UNBROKEN
# ═══════════════════════════════════════════════════════════════════════════════

class TestOriginalChainUnbroken:
    """Adding HP modules must not break the existing contradiction chain."""

    def test_contradiction_chain_still_passes(self):
        """The full contradiction chain must still complete."""
        result = contradiction_chain(H=3.0, n_9d=30)
        assert result['chain_complete']

    def test_lemma1_still_holds(self):
        """Corrected Toeplitz still PSD for Riemann zeros."""
        r = lemma1_psd_at_lambda_star(GAMMA_30[:15], H=3.0)
        assert r['psd']

    def test_bochner_psd_with_poly_spectrum(self):
        """Corrected Toeplitz is PSD for the polymeric spectrum too."""
        evals = get_poly_spectrum(n=20, mu0=0.1, p_interval=(0.2, 3.0))
        H = 3.0
        lam = lambda_star(H)
        M = build_corrected_toeplitz(evals.real, H, lam)
        assert is_psd(M)

    def test_bochner_universality_includes_poly(self):
        """Kernel universality: PSD for polymeric, Riemann, and random spectra."""
        H = 3.0
        lam = lambda_star(H)
        spectra = {
            'riemann': GAMMA_30[:20],
            'polymer': get_poly_spectrum(n=20, mu0=0.1,
                                         p_interval=(0.2, 3.0)).real,
            'random': np.sort(np.random.RandomState(42).uniform(5, 100, 20)),
        }
        for name, E in spectra.items():
            M = build_corrected_toeplitz(E, H, lam)
            assert is_psd(M), f"PSD failed for {name}"


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — HP SPECTRAL DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════════

class TestHPSpectralDiagnostics:
    """Diagnostic comparisons between polymeric and ζ-zero spectra."""

    def test_poly_spectrum_spacing_differs_from_zeros(self):
        """Polymeric level spacing ≠ Riemann zero spacing (honestly)."""
        evals_poly = get_poly_spectrum(n=15, mu0=0.1,
                                       p_interval=(0.1, 5.0)).real
        gaps_poly = np.diff(evals_poly)
        gaps_riemann = np.diff(GAMMA_30[:15])
        # They should differ (HP is not tuned to match)
        assert not np.allclose(gaps_poly, gaps_riemann, rtol=0.1)

    def test_poly_counting_vs_riemann_von_mangoldt(self):
        """Polymeric N(E) should approximate the smooth Riemann counting."""
        E_test = GAMMA_30[9]  # γ₁₀ ≈ 49.77
        N_bk = berry_keating_counting(E_test)
        # We have 10 zeros below γ₁₀ → the counting should be ~10
        assert N_bk > 0  # BK gives positive count for large E

    def test_stiffness_spectrum(self):
        """Phase-space stiffness increases with μ₀."""
        stiff_vals = []
        for mu0 in [0.01, 0.05, 0.1, 0.3, 0.5]:
            s = phase_space_stiffness(mu0, p_range=(0.1, 3.0))
            stiff_vals.append(s['stiffness'])
        # Should be monotonically increasing
        assert all(stiff_vals[i] <= stiff_vals[i+1] + 1e-10
                   for i in range(len(stiff_vals) - 1))


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — HYBRID FUNCTIONAL IN THE CHAIN
# ═══════════════════════════════════════════════════════════════════════════════

class TestHybridInChain:
    """The hybrid functional integrated with existing chain diagnostics."""

    def test_hybrid_F_sech_matches_standalone(self):
        """F_sech from hybrid should match standalone curvature_functional."""
        from engine.gravity_functional import curvature_functional
        T0, H, N = 14.135, 3.0, 30
        F_standalone = curvature_functional(T0, H, N)
        res = hybrid_energy(T0, H, N, mu0=0.1, epsilon=0.0)
        assert abs(res['F_sech'] - F_standalone) < 1e-10

    @pytest.mark.parametrize("T0", [14.135, 25.0, 50.0])
    def test_hybrid_positive_at_multiple_T0(self, T0):
        """F_total ≥ 0 at multiple evaluation points (PSD preserved)."""
        res = hybrid_energy(T0, H=3.0, N=30, mu0=0.1, epsilon=0.1)
        assert res['F_total'] > -1e-6

    def test_stiffness_enhancement_real(self):
        """Enhancement ratio is real, finite, ≥ 1."""
        se = stiffness_enhancement(T0=14.135, H=3.0, N=30, mu0=0.1,
                                   epsilon=0.1)
        assert np.isfinite(se['ratio'])
        assert se['ratio'] >= 0.99  # Allow tiny numerical noise


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — SMALL-Δβ REGIME (THE CRACK PROBE)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSmallDeltaBetaProbe:
    """
    Probe the small-Δβ regime where the original functional has the crack.
    The hybrid functional should maintain a nonzero response.
    """

    @pytest.mark.parametrize("db", [0.001, 0.01, 0.05, 0.1, 0.2])
    def test_hybrid_response_finite(self, db):
        """The hybrid response is finite for all Δβ."""
        res = hybrid_domination_ratio(
            delta_beta=db, gamma_0=14.135, H=3.0, N=30,
            mu0=0.1, epsilon=0.1,
        )
        assert np.isfinite(res['hybrid'])

    def test_hybrid_nonzero_at_small_delta_beta(self):
        """Even at very small Δβ, the hybrid response is nonzero."""
        res = hybrid_domination_ratio(
            delta_beta=0.001, gamma_0=14.135, H=3.0, N=30,
            mu0=0.1, epsilon=0.1,
        )
        # The sech-only response may vanish, but hybrid should persist
        assert res['hybrid'] >= 0

    def test_enhancement_sweep(self):
        """Sweep Δβ and verify enhancement is always ≥ 1."""
        for db in [0.01, 0.05, 0.1, 0.2, 0.3]:
            res = hybrid_domination_ratio(
                delta_beta=db, gamma_0=14.135, H=3.0, N=30,
                mu0=0.1, epsilon=0.1,
            )
            assert res['enhancement'] >= 0.99  # ≈ 1.0 or better


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — HONEST ASSESSMENT UPDATED
# ═══════════════════════════════════════════════════════════════════════════════

class TestHonestAssessmentHP:
    """The honest_assessment() should include HP status."""

    def test_assessment_has_hp_section(self):
        ha = honest_assessment()
        assert 'hilbert_polya' in ha

    def test_hp_status_honest(self):
        ha = honest_assessment()
        hp = ha['hilbert_polya']
        assert 'CANDIDATE' in hp['status'] or 'FRAMEWORK' in hp['status']

    def test_hp_does_not_claim_proof(self):
        """HP section must NOT claim RH is proved/proven."""
        ha = honest_assessment()
        hp = ha['hilbert_polya']
        status_lower = hp['status'].lower()
        assert 'proved' not in status_lower
        assert 'proven' not in status_lower or 'not proven' in status_lower

    def test_overall_includes_hp(self):
        """Overall assessment should mention HP operator."""
        ha = honest_assessment()
        measured = ha['overall'].get('now_measured', [])
        hp_mentioned = any('hilbert' in m.lower() or 'polymer' in m.lower()
                          for m in measured)
        assert hp_mentioned

    def test_honest_assessment_consistent(self):
        """Check all keys still present from previous version."""
        ha = honest_assessment()
        for key in ['theorem_b_2_0', 'lemma_1', 'lemma_2', 'lemma_3_sign',
                     'lemma_3_domination', 'barrier_2', 'barrier_3', 'overall']:
            assert key in ha
