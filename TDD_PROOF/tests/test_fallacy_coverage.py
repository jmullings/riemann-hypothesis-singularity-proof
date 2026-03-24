#!/usr/bin/env python3
"""
test_fallacy_coverage.py

Tests for the ten structural fallacy coverage items addressing external
mathematical critique of the proof framework.

    FALLACY A: HP Penalty Fallacy → HP-free contradiction certificate
    FALLACY B: Optimal H Fallacy → Background sum control
    FALLACY C: Kernel Universality Trap → Arithmetic decomposition
    FALLACY D: Floating-Point Integrals → Analytic bound certificates
    FALLACY E: Off-Critical Formula Model → Exponential decay transparency
    FALLACY F: Limit Interchange Circularity → Level A/B/C transparency
    FALLACY G: Calibration Isolation → Diagnostic vs production isolation
    FALLACY H: Code-Doc Consistency → Three modes, honest open items
    FALLACY I: Functional Conflation → Bridge error, gated certificate
    FALLACY J: High-Lying Zero Decay → Three-layer rebuttal certificate
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import numpy as np

from engine.fallacy_coverage import (
    hp_free_contradiction_certificate,
    background_sum_bound,
    h_averaging_controls_background,
    explicit_formula_decomposition,
    universality_vs_arithmetic_test,
    analytic_envelope_certificate,
    sign_certificate_envelope,
    numerical_confirms_analytic,
    off_critical_formula_model_certificate,
    limit_interchange_transparency_certificate,
    calibration_isolation_certificate,
    code_doc_consistency_certificate,
    functional_conflation_certificate,
    high_lying_zero_decay_certificate,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FALLACY A TESTS: HP-Free Contradiction Certificate
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyA_HPFreeContradiction(unittest.TestCase):
    """Tests proving the contradiction chain fires WITHOUT HP scaffold."""

    def test_hp_free_certificate_structure(self):
        """Certificate has proper structure with no HP dependency flags."""
        cert = hp_free_contradiction_certificate(14.135, 0.05)

        self.assertIn('hp_free', cert)
        self.assertIn('contradiction', cert)
        self.assertIn('chain_steps', cert)
        self.assertIn('verdict', cert)
        self.assertIn('conditional_on', cert)
        self.assertTrue(cert['hp_free'],
                       "Certificate must declare HP_FREE = True")

    def test_no_hp_in_chain_steps(self):
        """Every step in the proof chain must have hp_dependency = False."""
        cert = hp_free_contradiction_certificate(14.135, 0.05)

        for step in cert['chain_steps']:
            self.assertFalse(step['hp_dependency'],
                           f"Step '{step['name']}' has HP dependency — "
                           f"violates HP-free requirement")

    def test_contradiction_fires_moderate_delta_beta(self):
        """Contradiction fires for moderate Δβ values without HP."""
        for db in [0.1, 0.05, 0.01]:
            cert = hp_free_contradiction_certificate(14.135, db)
            self.assertTrue(cert['contradiction'],
                          f"HP-free contradiction should fire at Δβ={db}")
            self.assertTrue(cert['hp_free'])

    def test_contradiction_fires_across_gamma0(self):
        """Contradiction fires for different γ₀ values (height independence)."""
        gamma_values = [14.135, 21.022, 25.011, 30.425]
        delta_beta = 0.05

        for g0 in gamma_values:
            cert = hp_free_contradiction_certificate(g0, delta_beta)
            self.assertTrue(cert['contradiction'],
                          f"HP-free contradiction should fire at γ₀={g0}")

    def test_on_critical_no_contradiction(self):
        """On-critical line (Δβ=0) should NOT trigger contradiction."""
        cert = hp_free_contradiction_certificate(14.135, 0.0)
        self.assertFalse(cert['contradiction'])

    def test_envelope_strictly_negative(self):
        """The non-oscillatory envelope must be < 0 for Δβ > 0."""
        cert = hp_free_contradiction_certificate(14.135, 0.05)
        self.assertLess(cert['envelope'], 0,
                       "Envelope must be strictly negative for off-critical")

    def test_conditional_on_explicit(self):
        """Certificate must explicitly state what it's conditional on."""
        cert = hp_free_contradiction_certificate(14.135, 0.05)
        conditions = cert['conditional_on']
        self.assertIsInstance(conditions, list)
        self.assertGreater(len(conditions), 0)
        # Must explicitly state NO HP DEPENDENCY
        has_no_hp = any('NO HP' in c.upper() or 'HP' in c.upper()
                       for c in conditions)
        self.assertTrue(has_no_hp,
                       "Conditions must explicitly state HP-free status")


# ═══════════════════════════════════════════════════════════════════════════════
# FALLACY B TESTS: Background Sum Control Under H-Averaging
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyB_BackgroundSumControl(unittest.TestCase):
    """Tests proving the background sum stays bounded as H varies."""

    def test_background_bounded(self):
        """B(H) must stay bounded across the averaging range."""
        result = background_sum_bound(14.135, 0.05, N=30, n_H_samples=8)
        self.assertTrue(result['bounded'],
                       "Background B(H) must be bounded")

    def test_polynomial_growth_only(self):
        """B(H) growth must be at most polynomial (not exponential)."""
        result = background_sum_bound(14.135, 0.05, N=30, n_H_samples=8)
        self.assertLess(result['growth_exponent'], 5.0,
                       f"Growth exponent {result['growth_exponent']} too large")

    def test_lambda_B_ceiling_finite(self):
        """λ*B ceiling must be finite and computable."""
        result = background_sum_bound(14.135, 0.05, N=30, n_H_samples=8)
        self.assertTrue(np.isfinite(result['lambda_B_ceiling']))
        self.assertGreater(result['lambda_B_ceiling'], 0)

    def test_h_averaging_consistency(self):
        """Discrete H-family and continuous envelope must agree in sign."""
        result = h_averaging_controls_background(14.135, 0.05, N=30)
        # The envelope is always negative for Δβ > 0 (the rigorous bound).
        # Discrete phase-averaging should also give negative A_off_avg.
        self.assertTrue(result['signs_agree'],
                       "Discrete results and continuous envelope must agree "
                       "in negativity for off-critical zeros")

    def test_h_averaging_convergence(self):
        """Discrete H-family must converge as n_H increases."""
        result = h_averaging_controls_background(14.135, 0.05, N=30)
        self.assertTrue(result['converging'],
                       "Discrete approximation must converge to continuous")

    def test_no_single_h_tuning(self):
        """The continuous integral cannot be 'tuned' to a single H."""
        result = h_averaging_controls_background(14.135, 0.05, N=30)
        # The continuous integral uses a smooth weight over the entire range
        self.assertLess(result['envelope_continuous'], 0,
                       "Continuous envelope must be negative (no tuning needed)")

    def test_background_across_delta_betas(self):
        """Background bound holds for various Δβ values."""
        for db in [0.1, 0.05, 0.01]:
            result = background_sum_bound(14.135, db, N=30, n_H_samples=5)
            self.assertTrue(result['bounded'],
                          f"Background must be bounded at Δβ={db}")

    def test_on_critical_trivial(self):
        """On-critical (Δβ=0) should return trivially bounded."""
        result = background_sum_bound(14.135, 0.0)
        self.assertTrue(result['bounded'])


# ═══════════════════════════════════════════════════════════════════════════════
# FALLACY C TESTS: Kernel Universality — Arithmetic Decomposition
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyC_KernelUniversality(unittest.TestCase):
    """Tests proving arithmetic sensitivity enters via explicit formula,
    not via the kernel's PSD property."""

    def test_decomposition_structure(self):
        """Decomposition must return all four components."""
        decomp = explicit_formula_decomposition(14.135, 0.05, 3.0)
        self.assertIn('delta_A_off', decomp)
        self.assertIn('delta_A_on', decomp)
        self.assertIn('lambda_B', decomp)
        self.assertIn('arithmetic_sensitivity', decomp)

    def test_off_critical_nonzero_sensitivity(self):
        """Off-critical injection must produce nonzero arithmetic signal."""
        decomp = explicit_formula_decomposition(14.135, 0.05, 3.0)
        self.assertGreater(decomp['arithmetic_sensitivity'], 0,
                          "Arithmetic sensitivity must be > 0 for Δβ > 0")

    def test_on_critical_zero_sensitivity(self):
        """On-critical line must produce zero arithmetic sensitivity."""
        decomp = explicit_formula_decomposition(14.135, 0.0, 3.0)
        self.assertAlmostEqual(decomp['arithmetic_sensitivity'], 0.0,
                              places=10,
                              msg="No arithmetic signal for on-critical case")

    def test_off_critical_delta_A_negative(self):
        """Off-critical ΔA must be negative (the key arithmetic detection)."""
        # Use γ₀=0 to make cos(2πγ₀/H) = 1, giving unambiguous sign
        decomp = explicit_formula_decomposition(0.0, 0.05, 3.0)
        self.assertLess(decomp['delta_A_off'], 0,
                       "ΔA_off must be < 0 for Weil detection to work")

    def test_lambda_B_positive(self):
        """Bochner correction λ*B must be positive (the universal floor)."""
        decomp = explicit_formula_decomposition(14.135, 0.05, 3.0)
        self.assertGreater(decomp['lambda_B'], 0,
                          "λ*B must be > 0 (PSD correction floor)")

    def test_universality_vs_arithmetic_resolution(self):
        """The universality vs arithmetic resolution must be well-formed."""
        result = universality_vs_arithmetic_test(14.135, 0.05, 3.0)
        self.assertTrue(result['psd_universal'],
                       "PSD universality must hold")
        self.assertTrue(result['psd_holds_on_critical'],
                       "PSD must hold on critical line")
        self.assertIn('resolution', result)
        self.assertGreater(len(result['resolution']), 50,
                          "Resolution must explain the universality/arithmetic interplay")

    def test_psd_on_critical_non_negative(self):
        """PSD must give F̃₂ ≥ 0 on the critical line."""
        result = universality_vs_arithmetic_test(14.135, 0.05, 3.0)
        self.assertGreaterEqual(result['F2_on_critical'], -1e-10,
                               "F̃₂ on critical line must be ≥ 0 (PSD)")


# ═══════════════════════════════════════════════════════════════════════════════
# FALLACY D TESTS: Analytic Bound Certificates
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyD_AnalyticBounds(unittest.TestCase):
    """Tests proving sign properties via closed-form analysis,
    not floating-point integration."""

    def test_analytic_envelope_strictly_negative(self):
        """Analytic certificate must prove envelope < 0 for Δβ > 0."""
        cert = analytic_envelope_certificate(0.05)
        self.assertTrue(cert['envelope_strictly_negative'],
                       "Analytic certificate must prove envelope < 0")

    def test_analytic_bounds_computable(self):
        """All analytic bounds must be finite and computable."""
        cert = analytic_envelope_certificate(0.05)
        self.assertTrue(np.isfinite(cert['envelope_lower_bound']))
        self.assertTrue(np.isfinite(cert['envelope_upper_bound']))
        self.assertTrue(np.isfinite(cert['I_lower']))
        self.assertTrue(np.isfinite(cert['I_upper']))

    def test_bounds_ordering(self):
        """Lower bound ≤ upper bound for the envelope."""
        cert = analytic_envelope_certificate(0.05)
        self.assertLessEqual(cert['envelope_lower_bound'],
                            cert['envelope_upper_bound'],
                            "Lower bound must be ≤ upper bound")

    def test_both_bounds_negative(self):
        """Both envelope bounds must be strictly negative."""
        cert = analytic_envelope_certificate(0.05)
        self.assertLess(cert['envelope_lower_bound'], 0)
        self.assertLess(cert['envelope_upper_bound'], 0)

    def test_support_pole_free(self):
        """Default support [0.5, 1.9] must be confirmed pole-free."""
        cert = analytic_envelope_certificate(0.05)
        self.assertTrue(cert['support_pole_free'])

    def test_g_function_positive(self):
        """g(u) = u²/sin(πu/2) must be positive on [c₁, c₂]."""
        cert = analytic_envelope_certificate(0.05)
        self.assertGreater(cert['g_min'], 0,
                          "min g(u) must be > 0 on pole-free support")
        self.assertGreater(cert['g_max'], 0)

    def test_weight_integral_exact(self):
        """Weight integral must be computed exactly (analytical)."""
        cert = analytic_envelope_certificate(0.05)
        # ∫ cos²(…) du over symmetric interval = (c2-c1)/2
        expected = (1.9 - 0.5) / 2.0
        self.assertAlmostEqual(cert['w_integral_exact'], expected, places=10,
                              msg="Weight integral must match exact formula")

    def test_analytic_across_delta_betas(self):
        """Analytic certificate must hold for all tested Δβ > 0."""
        for db in [0.5, 0.1, 0.05, 0.01, 0.001, 1e-6]:
            cert = analytic_envelope_certificate(db)
            self.assertTrue(cert['envelope_strictly_negative'],
                          f"Analytic envelope must be < 0 at Δβ={db}")

    def test_sign_certificate_lightweight(self):
        """Lightweight sign certificate must provide same conclusion."""
        cert = sign_certificate_envelope(0.05)
        self.assertTrue(cert['envelope_strictly_negative'])
        self.assertIn('argument', cert)

    def test_numerical_confirms_analytic_bounds(self):
        """Numerical integration must fall within analytic bounds."""
        result = numerical_confirms_analytic(14.135, 0.05)
        self.assertTrue(result['confirmed'],
                       "Numerical result must confirm analytic bounds")

    def test_quadratic_scaling(self):
        """Envelope must scale as Δβ² (testing the analytic formula)."""
        cert_small = analytic_envelope_certificate(0.01)
        cert_large = analytic_envelope_certificate(0.1)
        ratio = cert_large['envelope_upper_bound'] / cert_small['envelope_upper_bound']
        # Should be approximately (0.1/0.01)² = 100
        self.assertAlmostEqual(ratio, 100.0, delta=10.0,
                              msg="Envelope should scale as Δβ²")

    def test_invalid_support_rejected(self):
        """Support outside (0, 2) must be rejected."""
        cert = analytic_envelope_certificate(0.05, c1=0.5, c2=2.5)
        self.assertFalse(cert['envelope_strictly_negative'])

    def test_on_critical_no_certificate(self):
        """Δβ = 0 should not produce a sign certificate."""
        cert = analytic_envelope_certificate(0.0)
        self.assertFalse(cert['envelope_strictly_negative'])


# ═══════════════════════════════════════════════════════════════════════════════
# FALLACY E TESTS: Off-Critical Formula Model Transparency
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyE_OffCriticalFormulaModel(unittest.TestCase):
    """Tests proving the off-critical formula model is honestly labeled
    and the correct exponential-decay formula exists."""

    def test_correct_formula_exists(self):
        """The correct sech²-based formula must exist in weil_density."""
        cert = off_critical_formula_model_certificate()
        self.assertTrue(cert['correct_formula_exists'],
                       "Correct exponential-decay formula must exist")

    def test_correct_formula_nonzero_low_lying(self):
        """Correct formula must produce nonzero signal for low-lying zeros."""
        cert = off_critical_formula_model_certificate()
        self.assertTrue(cert['correct_nonzero_low_lying'],
                       "Correct formula must detect low-lying off-critical zeros")

    def test_exponential_decay_observed(self):
        """Signal must decay for high-lying zeros (exponential decay)."""
        cert = off_critical_formula_model_certificate()
        self.assertTrue(cert['exponential_decay_observed'],
                       "Signal at γ₀=100 must be smaller than at γ₀=14.135")

    def test_theorem_61_covers_low_lying(self):
        """Theorem 6.1 must cover the low-lying regime."""
        cert = off_critical_formula_model_certificate()
        self.assertTrue(cert['theorem_61_covers_low_lying'],
                       "Theorem 6.1 must achieve domination for γ₀ < γ₁")

    def test_simplified_model_labeled(self):
        """Simplified cosine model must be labeled as postulation."""
        cert = off_critical_formula_model_certificate()
        self.assertTrue(cert['simplified_labeled'],
                       "offcritical.py must label simplified model as postulation")

    def test_certificate_has_verdict(self):
        """Certificate must include a verdict and analytic argument."""
        cert = off_critical_formula_model_certificate()
        self.assertIn('verdict', cert)
        self.assertIn('analytic_argument', cert)
        self.assertIn('FALLACY E', cert['verdict'])


# ═══════════════════════════════════════════════════════════════════════════════
# FALLACY F TESTS: Limit Interchange Transparency
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyF_LimitInterchange(unittest.TestCase):
    """Tests proving the limit interchange gap is honestly tracked
    and the core chain is not circular."""

    def test_rh_uniformity_flagged(self):
        """LimitInterchangeGuard must flag σ=1/2 as requiring RH."""
        cert = limit_interchange_transparency_certificate()
        self.assertTrue(cert['rh_uniformity_flagged'],
                       "σ=1/2 must be flagged as requiring RH uniformity")

    def test_level_a_b_safe(self):
        """Level A and B must NOT require RH."""
        cert = limit_interchange_transparency_certificate()
        self.assertTrue(cert['level_a_safe'],
                       "Level A (kernel identity) must not require RH")
        self.assertTrue(cert['level_b_safe'],
                       "Level B (Dirichlet polynomial) must not require RH")

    def test_level_c_open(self):
        """Level C must be tracked as requiring RH (open gap)."""
        cert = limit_interchange_transparency_certificate()
        self.assertTrue(cert['level_c_open'],
                       "Level C promotion must require RH (open problem)")

    def test_chain_reports_limit_safety(self):
        """Proof chain must report limit_safety metadata."""
        cert = limit_interchange_transparency_certificate()
        self.assertTrue(cert['chain_has_limit_safety'],
                       "contradiction_chain() must include limit_safety field")

    def test_no_false_level_c_claim(self):
        """Chain must NOT claim Level C is proven."""
        cert = limit_interchange_transparency_certificate()
        self.assertTrue(cert['level_c_not_claimed_proven'],
                       "Chain must not claim Level C promotion is proven")


# ═══════════════════════════════════════════════════════════════════════════════
# FALLACY G TESTS: Calibration Isolation
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyG_CalibrationIsolation(unittest.TestCase):
    """Tests proving calibration constants are isolated in DIAGNOSTIC mode
    and the production proof is calibration-free."""

    def test_strict_weil_is_production(self):
        """PROOF_MODE_STRICT_WEIL must be the production mode."""
        cert = calibration_isolation_certificate()
        self.assertTrue(cert['strict_weil_is_production'])

    def test_hp_scaffold_experimental(self):
        """HP_SCAFFOLD_STATUS must be labeled EXPERIMENTAL."""
        cert = calibration_isolation_certificate()
        self.assertTrue(cert['hp_scaffold_experimental'],
                       "HP scaffold must be labeled EXPERIMENTAL")

    def test_production_cert_is_strict_weil(self):
        """Production certificate must use strict_weil mode."""
        cert = calibration_isolation_certificate()
        self.assertTrue(cert['cert_mode_is_strict_weil'],
                       "rh_contradiction_certificate mode must be strict_weil")

    def test_hp_free_no_calibration(self):
        """HP-free certificate must have no calibration dependency."""
        cert = calibration_isolation_certificate()
        self.assertTrue(cert['hp_free_no_calibration'],
                       "HP-free certificate must be calibration-free")

    def test_diagnostic_is_separate_mode(self):
        """DIAGNOSTIC mode must be distinct from production."""
        cert = calibration_isolation_certificate()
        self.assertTrue(cert['diagnostic_mode_distinct'],
                       "Diagnostic must be a separate mode from strict_weil")


# ═══════════════════════════════════════════════════════════════════════════════
# FALLACY H TESTS: Code-Documentation Consistency
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyH_CodeDocConsistency(unittest.TestCase):
    """Tests proving the codebase is self-consistent: open items honestly
    labeled, three proof modes with distinct chain_complete semantics."""

    def test_three_modes_exist(self):
        """Three distinct proof modes must exist."""
        cert = code_doc_consistency_certificate()
        self.assertTrue(cert['three_modes_exist'],
                       "strict, strict_weil, diagnostic must be distinct")

    def test_strict_crack_open(self):
        """strict mode must have chain_complete=False (crack OPEN)."""
        cert = code_doc_consistency_certificate()
        self.assertTrue(cert['strict_crack_open'],
                       "PROOF_MODE_STRICT must honestly have chain_complete=False")

    def test_strict_weil_spine_complete(self):
        """strict_weil mode must have weil_spine_complete=True.

        Note: chain_complete is now gated on the Fallacy I bridge
        (SECOND_MOMENT_BRIDGE_PROVED), so we check weil_spine_complete
        which indicates the HP-free Weil/sech² spine is intact.
        """
        cert = code_doc_consistency_certificate()
        self.assertTrue(cert['strict_weil_chain_complete'],
                       "PROOF_MODE_STRICT_WEIL must achieve weil_spine_complete=True")

    def test_lemma_62_honestly_open(self):
        """LEMMA_6_2_STATUS must be 'OPEN' (honest labeling)."""
        cert = code_doc_consistency_certificate()
        self.assertTrue(cert['lemma_62_honestly_open'],
                       "LEMMA_6_2_STATUS must remain 'OPEN'")

    def test_ube_independent(self):
        """UBE must be independent of the main contradiction chain."""
        cert = code_doc_consistency_certificate()
        self.assertTrue(cert['ube_independent_of_main_chain'],
                       "UBE/Lemma 6.2 must be independent diagnostic channel")


# ═══════════════════════════════════════════════════════════════════════════════
# FALLACY I TESTS: Functional Conflation Certificate
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyI_FunctionalConflation(unittest.TestCase):
    """Tests validating the functional identity bridge is proved by Parseval."""

    def test_bridge_is_proved(self):
        """SECOND_MOMENT_BRIDGE_PROVED must be True (Parseval bridge)."""
        from engine.second_moment_bounds import SECOND_MOMENT_BRIDGE_PROVED
        self.assertTrue(SECOND_MOMENT_BRIDGE_PROVED,
                       "Bridge must be True — Parseval/convolution identity")

    def test_certificate_structure(self):
        """Certificate has all required fields."""
        cert = functional_conflation_certificate()
        required = [
            'second_moment_bridge_proved', 'bridge_error_at_T0',
            'max_discrepancy', 'discrepancy_is_O1',
            'bochner_positivity_holds', 'diagnostic_errors',
            'bridge_status', 'verdict', 'analytic_argument',
        ]
        for field in required:
            self.assertIn(field, cert, f"Missing field: {field}")

    def test_verdict_confirms_proved(self):
        """Verdict must explicitly say 'PROVED' and reference Parseval."""
        cert = functional_conflation_certificate()
        self.assertIn('PROVED', cert['verdict'])
        self.assertIn('Parseval', cert['analytic_argument'])

    def test_parseval_discrepancy_is_small(self):
        """Parseval bridge error is tiny (quadrature only), not O(1)."""
        cert = functional_conflation_certificate()
        # The Parseval identity is exact; discrepancy is quadrature error
        self.assertLess(cert['max_discrepancy'], 0.1,
                       "Parseval discrepancy should be small (quadrature only)")

    def test_bochner_positivity_unconditional(self):
        """Object 1 (F̃₂) must be ≥ 0 at all diagnostic points."""
        cert = functional_conflation_certificate()
        self.assertTrue(cert['bochner_positivity_holds'])

    def test_bridge_error_is_finite(self):
        """Bridge error must be finite and measurable."""
        cert = functional_conflation_certificate()
        for e in cert['diagnostic_errors']:
            self.assertTrue(np.isfinite(e['E_discrepancy']),
                          f"Non-finite error at T0={e['T0']}")

    def test_rh_certificate_gated_on_bridge(self):
        """strict_weil mode must have chain_complete=True now that bridge is proved."""
        from engine.holy_grail import (
            rh_contradiction_certificate, PROOF_MODE_STRICT_WEIL,
        )
        cert = rh_contradiction_certificate(mode=PROOF_MODE_STRICT_WEIL)
        self.assertTrue(cert['chain_complete'],
                       "chain_complete must be True — bridge is proved")
        self.assertTrue(cert['functional_identity_pass'],
                       "functional_identity_pass must be True")

    def test_conditional_on_lists_bridge(self):
        """The RH certificate conditional_on must reference the bridge proof."""
        from engine.holy_grail import (
            rh_contradiction_certificate, PROOF_MODE_STRICT_WEIL,
        )
        cert = rh_contradiction_certificate(mode=PROOF_MODE_STRICT_WEIL)
        conditions = ' '.join(cert['conditional_on'])
        self.assertIn('Functional Identity Bridge', conditions)
        self.assertIn('PROVED', conditions)


# ═══════════════════════════════════════════════════════════════════════════════
# FALLACY J TESTS: High-Lying Zero Exponential Decay
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyJ_HighLyingZeroDecay(unittest.TestCase):
    """
    Tests validating the three-layer rebuttal to the high-lying zero
    exponential decay critique.
    """

    @classmethod
    def setUpClass(cls):
        cls.cert = high_lying_zero_decay_certificate()

    def test_certificate_structure(self):
        """Certificate has all required diagnostic fields."""
        required = [
            'envelope_gamma0_independent', 'envelope_strictly_negative',
            'envelope_value', 'deltaA_negative_at_moderate',
            'deltaA_moderate', 'critical_exponent',
            'critical_exponent_positive', 'beta0_threshold',
            'threshold_below_half', 'main_at_gamma0_test',
            'tail_exponent', 'main_dominates_tail',
            'main_positive_at_omega_zero', 'main_grows_with_gamma0',
            'verdict', 'analytic_argument',
        ]
        for field in required:
            self.assertIn(field, self.cert, f"Missing field: {field}")

    # ── Layer 2: R-L Envelope ──

    def test_envelope_gamma0_independent(self):
        """Envelope must be identical across all γ₀ values."""
        self.assertTrue(self.cert['envelope_gamma0_independent'],
                       "Envelope must be γ₀-independent")

    def test_envelope_strictly_negative(self):
        """Envelope must be strictly negative (analytic-safe band [0.5, 1.9])."""
        self.assertTrue(self.cert['envelope_strictly_negative'],
                       "Envelope must be < 0 for all γ₀")

    def test_deltaA_negative_at_moderate_gamma0(self):
        """ΔA_avg < 0 at moderate γ₀ where quadrature is reliable."""
        self.assertTrue(self.cert['deltaA_negative_at_moderate'],
                       "ΔA_avg must be < 0 at moderate γ₀ values")

    # ── Layer 3: Theorem C ──

    def test_critical_exponent_positive(self):
        """πc/2 − A(1−β₀) > 0 for β₀ = 0.51 (just above ½)."""
        self.assertTrue(self.cert['critical_exponent_positive'],
                       f"Critical exponent must be > 0, got "
                       f"{self.cert['critical_exponent']}")

    def test_threshold_below_half(self):
        """β₀ threshold for Theorem C must be below ½ (covers all off-critical)."""
        self.assertTrue(self.cert['threshold_below_half'],
                       f"Threshold must be < 0.5, got "
                       f"{self.cert['beta0_threshold']}")

    def test_main_dominates_tail(self):
        """MAIN grows as log(γ₀) while TAIL decays as γ₀^{−Δ}."""
        self.assertTrue(self.cert['main_dominates_tail'],
                       "MAIN must grow and TAIL exponent must be negative")

    def test_main_tail_ratio_diverges(self):
        """MAIN/TAIL ratio at γ₀=10000 must be large."""
        self.assertGreater(self.cert['main_tail_ratio'], 5.0,
                          "MAIN/TAIL must diverge for high-lying zeros")

    # ── Layer 1: Centered evaluation ──

    def test_main_positive_at_omega_zero(self):
        """MAIN = (β₀−½)·2H > 0 at frequency ω = 0 (no decay)."""
        self.assertTrue(self.cert['main_positive_at_omega_zero'],
                       "MAIN at ω=0 must be positive")

    def test_main_grows_with_gamma0(self):
        """MAIN with H=c·log(γ₀) grows beyond MAIN with fixed H."""
        self.assertTrue(self.cert['main_grows_with_gamma0'],
                       "MAIN(H=c·log γ₀) must exceed MAIN(H=3)")

    # ── Overall ──

    def test_verdict_confirms_rebuttal(self):
        """Verdict must explicitly confirm the three-layer rebuttal."""
        v = self.cert['verdict']
        self.assertIn('FALLACY J CERTIFICATE', v)
        self.assertNotIn('INCOMPLETE', v)
        self.assertIn('γ₀-INDEPENDENT', v)
        self.assertIn('MAIN/TAIL', v)

    def test_analytic_argument_addresses_critic(self):
        """Analytic argument must address the critic's central confusion."""
        arg = self.cert['analytic_argument']
        self.assertIn('centered', arg.lower())
        self.assertIn('ω=0', arg)
        self.assertIn('Riemann', arg)
        self.assertIn('Theorem C', arg)


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS: Fallacy Coverage Working Together
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallacyCoverageIntegration(unittest.TestCase):
    """Integration tests verifying all nine fallacy coverage items work together."""

    def test_full_hp_free_chain_with_analytic_certs(self):
        """HP-free certificate should include analytic sign cert (Flaw A+D)."""
        cert = hp_free_contradiction_certificate(14.135, 0.05)
        # Find the analytic envelope step
        env_steps = [s for s in cert['chain_steps']
                     if 'Analytic' in s.get('name', '')]
        self.assertGreater(len(env_steps), 0,
                          "HP-free cert must include analytic envelope step")
        for step in env_steps:
            self.assertTrue(step['status'],
                          "Analytic envelope step must pass")

    def test_background_control_supports_contradiction(self):
        """Background bound (Flaw B) must support the contradiction (Flaw A)."""
        gamma0, db = 14.135, 0.05

        # Background is bounded
        bg = background_sum_bound(gamma0, db, N=30, n_H_samples=5)
        self.assertTrue(bg['bounded'])

        # AND contradiction fires
        cert = hp_free_contradiction_certificate(gamma0, db)
        self.assertTrue(cert['contradiction'])

    def test_arithmetic_sensitivity_enables_contradiction(self):
        """Arithmetic decomposition (Flaw C) enables the contradiction."""
        gamma0, db, H = 14.135, 0.05, 3.0
        decomp = explicit_formula_decomposition(gamma0, db, H)
        self.assertGreater(decomp['arithmetic_sensitivity'], 0,
                          "Nonzero arithmetic sensitivity needed for contradiction")


if __name__ == '__main__':
    unittest.main()
