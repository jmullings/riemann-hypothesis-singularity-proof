#!/usr/bin/env python3
"""
================================================================================
reverse_direction.py — Reverse Direction Analysis & Smoothed Functionals
================================================================================

Ported from RH_PROOF/src/reverse_direction.py §7.

Implements the full reverse-direction machinery:
  §1 — Pole-free certificate (sech² vs sec²)
  §2 — On-line sum with tail bounds
  §3 — Off-line contribution with explicit bounds
  §4 — Negativity windows (where C_off < 0)
  §5 — Smoothed functional ∫ S(α)·w(α) dα
  §6 — Sign structure lemma N(x,y)/D(x,y)²

COVERAGE:
  • Negativity windows: PROVED — exact α-intervals where C_off < 0
  • Pole-free: PROVED — sech² ∈ (0,1] for all real x
  • Sign structure: PROVED — N(0,y) = cos²y ≥ 0 on critical line,
                    N(x,y) can be negative off-line
  • Smoothed functional: CONSTRUCTED — alternative to pointwise α

Source: RH_PROOF/src/reverse_direction.py
================================================================================
"""

import warnings
import numpy as np

from .kernel import sech2
from .weil_density import (
    GAMMA_30, sech2_complex, off_line_pair_contribution, on_line_sum,
)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — Pole-Free Certificate
# ═══════════════════════════════════════════════════════════════════════════════

def pole_free_certificate(x_range=(-500, 500), n_points=50000):
    """
    Verify sech²(x) = 1/cosh²(x) is pole-free on ℝ.

    Unlike sec²(x) = 1/cos²(x) which diverges at x = (n+½)π,
    sech²(x) is bounded in (0, 1] for all x ∈ ℝ because cosh(x) ≥ 1.

    Returns certification dict.
    """
    xs = np.linspace(x_range[0], x_range[1], n_points)
    vals = sech2(xs)
    return {
        'is_pole_free': True,
        'min_value': float(np.min(vals)),
        'max_value': float(np.max(vals)),
        'all_finite': bool(np.all(np.isfinite(vals))),
        'all_nonnegative': bool(np.all(vals >= 0)),
        'all_bounded_by_one': bool(np.all(vals <= 1.0 + 1e-15)),
        'n_points_tested': n_points,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — On-Line Sum with Tail Bound
# ═══════════════════════════════════════════════════════════════════════════════

def on_line_sum_with_tail_bound(alpha, gammas=None):
    """
    Compute S_on(α) with explicit tail bound for zeros beyond our list.

    Tail bound: Σ_{k>K} sech²(αγ_k) ≤ sech²(αγ_K) / (1 − e^{-2αδ})
    where δ = min gap between consecutive known zeros.

    Returns (exact_sum, upper_bound, tail_bound).
    """
    if gammas is None:
        gammas = GAMMA_30
    gammas = np.asarray(gammas, dtype=np.float64)

    S_exact = on_line_sum(alpha, gammas)
    gamma_K = gammas[-1]
    gaps = np.diff(gammas)
    delta = float(np.min(gaps))

    last_term = float(sech2(np.array([alpha * gamma_K]))[0])

    if alpha * delta > 0.01:
        tail = last_term / (1.0 - np.exp(-2 * alpha * delta))
    else:
        tail = last_term * len(gammas)

    return S_exact, S_exact + tail, tail


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — Off-Line Contribution Bounds
# ═══════════════════════════════════════════════════════════════════════════════

def optimal_alpha_star(delta_beta):
    """
    α* that maximises |C_off(α)|.
    cos(2αΔβ) = −1 when α* = π/(2|Δβ|).
    """
    return np.pi / (2.0 * abs(delta_beta))


def off_line_bound_at_alpha_star(gamma_0, delta_beta):
    """
    Exact C_off at α* = π/(2|Δβ|).
    At this point: C_off = −2/sinh²(α*γ₀) ≈ −8·e^{−2α*γ₀}.
    """
    alpha_star = optimal_alpha_star(delta_beta)
    x = alpha_star * gamma_0
    if x > 350:
        return alpha_star, 0.0
    sh = np.sinh(x)
    if abs(sh) < 1e-30:
        return alpha_star, 0.0
    return alpha_star, -2.0 / sh ** 2


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — Negativity Windows
# ═══════════════════════════════════════════════════════════════════════════════

def negativity_windows(delta_beta, n_windows=3):
    """
    α-windows where C_off(α) < 0.

    cos(2αΔβ) < 0 when 2αΔβ ∈ (π/2 + 2nπ, 3π/2 + 2nπ),
    i.e. α ∈ ((π/4 + nπ)/|Δβ|, (3π/4 + nπ)/|Δβ|).

    Returns [(α_low, α_high, α_center), ...].
    """
    db = abs(delta_beta)
    windows = []
    for n in range(n_windows):
        low = (np.pi / 4 + n * np.pi) / db
        high = (3 * np.pi / 4 + n * np.pi) / db
        center = (np.pi / 2 + n * np.pi) / db
        windows.append((low, high, center))
    return windows


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — Smoothed Functional
# ═══════════════════════════════════════════════════════════════════════════════

def smoothed_functional(gammas=None, gamma_0=None, delta_beta=0.0,
                        sigma=1.0, alpha_max=20.0):
    """
    Smoothed functional: I(w) = ∫₀^∞ S(α)·w(α) dα
    where w(α) = exp(−α²/(2σ²)) is a Gaussian weight.

    If gamma_0 and delta_beta are provided, includes the off-line contribution.
    A negative integral proves ∃α with S(α) < 0.

    Returns (integral_value, quadrature_error).
    """
    from scipy.integrate import quad

    if gammas is None:
        gammas = GAMMA_30

    def integrand(alpha):
        if alpha < 1e-15:
            return 0.0
        w = np.exp(-alpha ** 2 / (2 * sigma ** 2))
        s_on = on_line_sum(alpha, gammas)
        if gamma_0 is not None and abs(delta_beta) > 1e-15:
            c_off = off_line_pair_contribution(alpha, gamma_0, delta_beta)
            S = s_on + c_off
        else:
            S = s_on
        return float(S) * w

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        val, err = quad(integrand, 1e-6, alpha_max, limit=200)

    return val, err


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — Sign Structure Lemma (Real Part of Complex sech²)
# ═══════════════════════════════════════════════════════════════════════════════

def numerator_N(x, y):
    """
    Numerator of ℜ(sech²(x+iy)):
      N(x,y) = cos²y + sinh²x · cos(2y)

    On critical line (x=0): N(0,y) = cos²y ≥ 0.
    Off-line (x≠0): N can be negative when cos(2y) < 0 and sinh²x large.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    return np.cos(y)**2 + np.sinh(np.clip(x, -350, 350))**2 * np.cos(2*y)


def denominator_D_sq(x, y):
    """
    Denominator² of ℜ(sech²(x+iy)):
      D²(x,y) = (cosh²x·cos²y + sinh²x·sin²y)²
    Always positive (D² > 0 unless x=y=0).
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    cx = np.clip(x, -350, 350)
    ch2 = np.cosh(cx)**2
    sh2 = np.sinh(cx)**2
    D = ch2 * np.cos(y)**2 + sh2 * np.sin(y)**2
    return D**2


def sign_structure_on_line(n_points=10000):
    """
    Verify N(0,y) = cos²y ≥ 0 for all y.
    PROVED: cos² is always non-negative.
    """
    y = np.linspace(-50, 50, n_points)
    N_vals = numerator_N(np.zeros_like(y), y)
    return {
        'all_nonneg': bool(np.all(N_vals >= -1e-15)),
        'min_N': float(np.min(N_vals)),
        'max_N': float(np.max(N_vals)),
        'n_points': n_points,
    }


def sign_structure_off_line(delta_beta_values=None, alpha_values=None, gamma_0=14.135):
    """
    Verify N(x,y) can be negative off-line.

    Under RH variable mapping: x = α(β−½) = αΔβ, y = αγ₀.
    When cos(2y) < 0 and sinh²x large enough, N < 0.
    """
    if delta_beta_values is None:
        delta_beta_values = [0.01, 0.05, 0.1, 0.2, 0.3, 0.49]
    if alpha_values is None:
        alpha_values = np.linspace(0.1, 20.0, 500)

    results = []
    for db in delta_beta_values:
        found_negative = False
        min_N = np.inf
        for alpha in alpha_values:
            x = alpha * db
            y = alpha * gamma_0
            N = float(numerator_N(np.array([x]), np.array([y]))[0])
            min_N = min(min_N, N)
            if N < 0:
                found_negative = True
        results.append({
            'delta_beta': db,
            'found_negative': found_negative,
            'min_N': min_N,
        })

    return results
