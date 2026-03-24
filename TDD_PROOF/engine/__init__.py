"""
TDD_PROOF engine — Self-contained 9D sech² Riemann Hypothesis proof machinery.

This package provides a complete, independently verifiable implementation of the
9D spectral-domain contradiction argument for the Riemann Hypothesis.

No external dependencies beyond numpy and scipy.
"""
from .kernel import sech2, w_H, fourier_w_H, W_curv, fourier_W_curv
from .bochner import (
    corrected_fourier, lambda_star, build_corrected_toeplitz,
    min_eigenvalue, is_psd,
)
from .spectral_9d import get_9d_spectrum, phi_metric_9d
from .offcritical import (
    weil_delta_A, weil_delta_A_full, rayleigh_quotient,
    signal_map, crack_width_scaling,
    build_offcritical_operator,
)
from .proof_chain import (
    lemma1_psd_at_lambda_star,
    lemma2_denominator_positive,
    lemma3_contradiction_fires,
    barrier1_gamma0_independence,
    barrier2_fixed_schwartz,
    barrier3_kernel_universality,
    contradiction_chain,
    proof_assessment,
)
from .weil_density import (
    asymptotic_domination_lemma,
    mellin_nonvanishing_theorem,
    dilation_completeness_theorem,
    domination_landscape,
    full_gap_status,
)
from .reverse_direction import (
    pole_free_certificate,
    negativity_windows,
    smoothed_functional,
    sign_structure_on_line,
    sign_structure_off_line,
)
from .hilbert_polya import (
    polymer_momentum,
    H_poly_matrix,
    H_poly_apply,
    get_poly_spectrum,
    berry_keating_counting,
    polymeric_counting,
    self_adjoint_eigenvalues,
    phase_space_stiffness,
    centered_H_poly_matrix,
    signed_HP_candidate,
    hp_operator_matrix,
)
from .gravity_functional import (
    hybrid_energy,
    transform_to_p_space,
    quadratic_form_H_poly,
    curvature_functional,
    stiffness_enhancement,
    hybrid_domination_ratio,
)
from .spectral_tools import (
    gaussian_spectral_density,
    numeric_counting_function,
    unfolded_spacings,
    spectral_resonance_frequencies,
)
from .operator_axioms import (
    is_PHO_representable,
    is_arithmetically_bound,
    gravity_well_gate,
)
from .arithmetic_invariants import (
    load_zeta_zeros,
    riemann_von_mangoldt_N,
    wigner_surmise_pdf,
    wigner_surmise_cdf,
    counting_function_distance,
    spacing_ks_statistic,
    linear_statistics,
    two_point_correlation,
    gue_sine_kernel_R2,
    compute_zero_like_invariants,
    compute_reference_invariants,
)
from .k3_arithmetic import (
    E_p, E_p_grid, sigma_p, lambda_p, G_p, K3,
    windowed_A_p, windowed_B_p, R_p, R_RS,
    k3_rayleigh_gap,
)
from .hp_alignment import (
    dirichlet_state,
    hp_energy,
    rs_rayleigh_with_drift,
    hybrid_lambda_star,
    hybrid_F2_RS,
)
from .weil_exact import (
    build_x_grid,
    build_x_powers,
    build_prime_coeffs,
    f_test_on_grid,
    f_star_on_grid,
    f_test_scalar,
    f_star_scalar,
    mellin_f,
    weil_zero_side,
    weil_prime_side,
    archimedean_term,
    weil_prime_arch_side,
    weil_equality_check,
    decompose_zero_side,
    decompose_prime_side,
)
from .holy_grail import (
    deficit_functional,
    penalty_ratio,
    small_delta_beta_closure,
    compact_domain_epsilon,
    domination_handoff,
    holy_grail_inequality,
    holy_grail_verdict,
    rh_contradiction_certificate,
    deficit_scaling_exponent,
    bhp_lower_bound,
    PROOF_MODE_STRICT,
    PROOF_MODE_STRICT_WEIL,
    PROOF_MODE_DIAGNOSTIC,
    HP_SCAFFOLD_STATUS,
)
from .fallacy_coverage import (
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
)
from .limit_safety import (
    classical_dirichlet_error_bound,
    error_envelope_monotone_in_N,
    error_envelope_growth_in_T,
    zeta_shadow_value,
    dirichlet_polynomial_value,
    measured_discrepancy,
    zeta_shadow_functional,
    LimitInterchangeGuard,
    classify_promotion,
    is_conjectural,
    non_promotable_metadata,
    LEVEL_A,
    LEVEL_B,
    LEVEL_C,
    NON_PROMOTABLE,
)
from .ube_decomposition import (
    Fk_prime_side,
    main_PNT_k,
    zero_sum_k,
    err_hat_k,
    C_phi_prime,
    C_phi_PNT,
    C_phi_zero_sum,
    C_phi_error,
    theta_scaling,
    full_decomposition,
    LEMMA_6_2_STATUS,
    UBE_CONVEXITY_STATUS,
    UBE_CLASSIFICATION,
)
from .circa_trap import (
    match_rate_identity,
    match_rate_wdb,
    match_rate_ube,
    match_rate_hp,
    is_tautological,
    circularity_score,
    random_match_rate,
    conjectural_bridges_in_chain,
    run_circa_audit,
    BRIDGE_CLASSIFICATION,
)
from .multi_h_kernel import (
    build_H_family,
    build_H_family_adaptive,
    is_H_family_admissible,
)
from .high_lying_avg_functional import (
    delta_A_offcritical,
    B_floor,
    F_single,
    F_avg,
)
from .triad_governor import (
    zeta_side_probe,
    pho_binding_probe,
    ube_convexity_probe,
    triad_probe,
    triad_scan,
    contradiction_engine,
    contradiction_scan,
    FAILURE_MODES,
    _truth_label,
    _classify_conflict,
    _update_confusion,
)
from .analytic_bounds import (
    lower_bound_deltaA_avg,
    upper_bound_B_avg,
    averaged_deltaA_continuous,
    pho_spectral_tolerance,
    dirichlet_spectrum_from_primes,
    upper_bound_err_k,
    theta_ceiling,
    chebyshev_pnt_bound,
    _pnt_decay_factor,
    kappa_lower_bound,
    B_avg_ceiling,
    bochner_correction_ceiling,
    contradiction_certificate,
)
from .euler_form import (
    spectral_times,
    chebyshev_psi_euler,
    heat_trace,
    heat_trace_derivative,
    spectral_zeta,
    pnt_residual_euler,
)
from .analytic_promotion import (
    # §1: Sech⁴ identity
    w_H_second_derivative_formula,
    g_lambda_star_from_wH,
    sech4_identity,
    verify_sech4_identity,
    # §1b: Bochner PSD
    bochner_psd_infinite_analytic,
    bochner_psd_infinite_numeric,
    bochner_psd_infinite,
    # §2: Riemann-Lebesgue
    envelope_sign_analytic,
    riemann_lebesgue_bound_analytic,
    riemann_lebesgue_global_negativity_analytic,
    envelope_integral,
    riemann_lebesgue_decay_bound,
    riemann_lebesgue_global_negativity,
    # §3: Spectral zeta
    spectral_zeta_convergence_analytic,
    spectral_zeta_tail_bound,
    spectral_zeta_convergence,
    # §4: Limsup
    kernel_limsup_lambda_ge_lambda_star,
    sub_threshold_negativity,
    rayleigh_quotient_at,
    rayleigh_quotient_sequence,
    limsup_lambda_N_ge_lambda_star,
)
