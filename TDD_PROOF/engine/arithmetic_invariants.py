#!/usr/bin/env python3
"""
================================================================================
arithmetic_invariants.py — Arithmetic Binding Invariants
================================================================================

Computes number-theoretic invariants from discrete spectra and compares them
against known Riemann-zeta reference data.  This module provides the
computational backend for the `is_arithmetically_bound` predicate in
operator_axioms.py.

INVARIANTS COMPUTED:
  1. Counting function N(T) = #{λ_j ≤ T} vs Riemann–von Mangoldt N_ζ(T)
  2. Nearest-neighbour spacing distribution vs GUE Wigner surmise
  3. Linear statistics Σ φ(λ_j) for admissible test functions φ
  4. Two-point correlation R₂(x) vs GUE sine-kernel prediction

DESIGN:
  - Reuses spectral_tools.py for spacing/counting infrastructure
  - Imports GAMMA_30 from weil_density.py as reference zeta spectrum
  - All comparisons are statistical (KS-test, L²-distance); no RH assumption

HONEST: Passing arithmetic binding does NOT prove RH.  It proves that a
spectrum reproduces specific verifiable number-theoretic invariants that
random/structural spectra almost never satisfy.
================================================================================
"""

import numpy as np
from .spectral_tools import unfolded_spacings, numeric_counting_function
from .weil_density import GAMMA_30


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — REFERENCE DATA
# ═══════════════════════════════════════════════════════════════════════════════

def load_zeta_zeros(n=30):
    """Load the first n known Riemann zeta zeros (imaginary parts)."""
    return GAMMA_30[:n].copy()


def riemann_von_mangoldt_N(T):
    """
    Smooth part of the Riemann–von Mangoldt counting function:

        N₀(T) = (T/(2π)) log(T/(2πe)) + 7/8

    This counts the expected number of zeros with 0 < γ ≤ T.
    """
    if T <= 0:
        return 0.0
    return (T / (2.0 * np.pi)) * np.log(T / (2.0 * np.pi * np.e)) + 7.0 / 8.0


def wigner_surmise_pdf(s):
    """
    GUE Wigner surmise for nearest-neighbour spacings:

        p(s) = (32/π²) s² exp(−4s²/π)

    This is the leading-order GUE prediction for P(s).
    """
    return (32.0 / np.pi**2) * s**2 * np.exp(-4.0 * s**2 / np.pi)


def wigner_surmise_cdf(s):
    """
    CDF of the GUE Wigner surmise, computed by numerical integration
    of the PDF on a fine grid.
    """
    from scipy.special import erf
    # Exact CDF: 1 - erf(2s/√π) + (2s/√π)·exp(-4s²/π)... 
    # Actually integrate numerically for robustness
    s = np.asarray(s, dtype=float)
    result = np.zeros_like(s)
    for i, si in enumerate(s.flat):
        if si <= 0:
            result.flat[i] = 0.0
        else:
            t = np.linspace(0, si, max(500, int(si * 200)))
            dt = t[1] - t[0] if len(t) > 1 else 1.0
            result.flat[i] = float(np.sum(wigner_surmise_pdf(t)) * dt)
    return np.minimum(result, 1.0)


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — INVARIANT COMPUTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def counting_function_distance(spectrum, T_values=None):
    """
    Compute the L²-distance between the empirical counting function
    N_spec(T) and the Riemann–von Mangoldt smooth approximation N₀(T).

    For true zeta zeros, this distance should be O(log T) (fluctuations).
    For random spectra, it will be much larger.

    Returns:
        (distance, details_dict)
    """
    spectrum = np.sort(np.asarray(spectrum, dtype=float))
    if T_values is None:
        T_min = max(spectrum[0] * 0.5, 1.0) if len(spectrum) > 0 else 1.0
        T_max = spectrum[-1] * 1.2 if len(spectrum) > 0 else 100.0
        T_values = np.linspace(T_min, T_max, 200)

    N_spec = np.array([np.searchsorted(spectrum, T, side='right')
                       for T in T_values], dtype=float)
    N_rvm = np.array([riemann_von_mangoldt_N(T) for T in T_values])

    diff = N_spec - N_rvm
    l2_dist = float(np.sqrt(np.mean(diff**2)))

    return l2_dist, {
        'T_values': T_values,
        'N_spec': N_spec,
        'N_rvm': N_rvm,
        'max_deviation': float(np.max(np.abs(diff))),
    }


def spacing_ks_statistic(spectrum):
    """
    Kolmogorov-Smirnov statistic between the empirical spacing distribution
    and the GUE Wigner surmise CDF.

    Returns:
        (ks_stat, details_dict)
    """
    spectrum = np.sort(np.asarray(spectrum, dtype=float))
    spacings = unfolded_spacings(spectrum)

    if len(spacings) < 2:
        return 1.0, {'spacings': spacings, 'n_spacings': len(spacings)}

    # Empirical CDF
    sorted_s = np.sort(spacings)
    n = len(sorted_s)
    ecdf = np.arange(1, n + 1) / n

    # Theoretical CDF (Wigner surmise)
    tcdf = wigner_surmise_cdf(sorted_s)

    # KS statistic
    ks_stat = float(np.max(np.abs(ecdf - tcdf)))

    return ks_stat, {
        'n_spacings': n,
        'mean_spacing': float(spacings.mean()),
        'var_spacing': float(spacings.var()),
    }


def linear_statistics(spectrum, phi_func=None):
    """
    Compute linear statistic: Σ φ(λ_j) for test function φ.

    Default φ(x) = sin(x) / x (sinc-like), which is sensitive to
    zero correlations.

    Returns float value of the sum.
    """
    spectrum = np.asarray(spectrum, dtype=float)
    if phi_func is None:
        def phi_func(x):
            return np.sinc(x / np.pi)  # sin(x)/x
    return float(np.sum(phi_func(spectrum)))


def two_point_correlation(spectrum, x_values=None, sigma=0.3):
    """
    Smoothed two-point correlation function R₂(x):

        R₂(x) = (1/N²) Σ_{i≠j} K_σ(x - (λ_i - λ_j)/Δ)

    where Δ is the mean spacing and K_σ is a Gaussian kernel.
    For GUE, R₂(x) → 1 - (sin(πx)/(πx))² (sine-kernel).

    Returns:
        (x_values, R2_values)
    """
    spectrum = np.sort(np.asarray(spectrum, dtype=float))
    n = len(spectrum)
    if n < 3:
        return np.array([0.0]), np.array([0.0])

    gaps = np.diff(spectrum)
    mean_gap = gaps.mean() if gaps.mean() > 0 else 1.0

    if x_values is None:
        x_values = np.linspace(0.01, 4.0, 100)

    # Compute all pairwise differences
    diffs = []
    for i in range(n):
        for j in range(n):
            if i != j:
                diffs.append((spectrum[i] - spectrum[j]) / mean_gap)
    diffs = np.array(diffs)

    R2 = np.zeros_like(x_values)
    for k, x in enumerate(x_values):
        kernel_vals = np.exp(-0.5 * ((x - diffs) / sigma)**2) / (
            np.sqrt(2 * np.pi) * sigma)
        R2[k] = kernel_vals.sum() / n**2

    return x_values, R2


def gue_sine_kernel_R2(x_values):
    """
    GUE two-point correlation (sine-kernel prediction):

        R₂_GUE(x) = 1 - (sin(πx)/(πx))²
    """
    x = np.asarray(x_values, dtype=float)
    sinc_sq = np.sinc(x)**2  # np.sinc(x) = sin(πx)/(πx)
    return 1.0 - sinc_sq


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — COMPOSITE INVARIANT STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

def compute_zero_like_invariants(spectrum):
    """
    Compute a full suite of arithmetic invariants for a given spectrum.

    Returns dict with:
        'counting_distance': L² distance from Riemann–von Mangoldt
        'ks_statistic': KS distance from GUE Wigner surmise
        'linear_stat': Σ sinc(λ_j)
        'n_levels': number of levels
    """
    spectrum = np.sort(np.asarray(spectrum, dtype=float))

    count_dist, count_details = counting_function_distance(spectrum)
    ks_stat, ks_details = spacing_ks_statistic(spectrum)
    lin_stat = linear_statistics(spectrum)

    return {
        'counting_distance': count_dist,
        'counting_details': count_details,
        'ks_statistic': ks_stat,
        'ks_details': ks_details,
        'linear_stat': lin_stat,
        'n_levels': len(spectrum),
    }


def compute_reference_invariants():
    """
    Compute invariants for the known Riemann zeta zeros (GAMMA_30).
    These serve as the ground-truth reference for binding tests.
    """
    return compute_zero_like_invariants(GAMMA_30)
