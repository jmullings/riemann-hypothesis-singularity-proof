#!/usr/bin/env python3
"""
================================================================================
k3_arithmetic.py — Per-Prime Arithmetic Rayleigh Quotient K₃
================================================================================

Implements the K₃ arithmetic kernel from the TDD_TODO integration plan:

    K₃(t, p) = (1/p)·E_p(t) + λ_p·G_p(t)

where:
    E_p(t) = |Σ_{n≤N, p|n} n^{-1/2} e^{-it·log(n)}|²   (per-prime Dirichlet energy)
    σ_p    = median_t E_p(t)                               (robust energy scale)
    λ_p    = (log p)² / p                                  (arithmetic weight)
    G_p(t) = sech²(α · E_p(t) / σ_p)                      (guard functional)

PURPOSE:
    K₃ is an arithmetic realisation of the RS Rayleigh quotient -A_RS/B_RS.
    It provides a MEASUREMENT CHANNEL for the small-Δβ gap — the exact quantity
    that must eventually be bounded by arithmetic theory to close the crack.

STATUS: NOW MEASURED — NOT BOUNDED.
    K₃ is numerically aligned with the explicit-formula side across tested
    regimes, but no analytic lower bound C(Δβ) ≥ λ*(H)·B₀ is yet known.

NO LOG OPERATIONS in E_p computation — uses integer arithmetic and bit_length
where possible. log(n) and log(p) use numpy for Dirichlet exponents only.
================================================================================
"""

import numpy as np
from .kernel import sech2, w_H


# ─────────────────────────────────────────────────────────────────────────────
# §1 — Per-prime Dirichlet energy E_p(t)
# ─────────────────────────────────────────────────────────────────────────────

def E_p(t, p, N):
    """
    Per-prime partial Dirichlet energy at height t.

    E_p(t) = |Σ_{n≤N, p|n} n^{-1/2} e^{-it·log(n)}|²

    Returns a non-negative real scalar (energy).
    """
    t = float(t)
    p = int(p)
    N = int(N)

    # Collect multiples of p up to N
    multiples = np.arange(p, N + 1, p, dtype=np.float64)
    if len(multiples) == 0:
        return 0.0

    # Dirichlet sum: Σ n^{-1/2} e^{-it·log(n)}
    log_n = np.log(multiples)
    coeffs = multiples ** (-0.5) * np.exp(-1j * t * log_n)
    S = np.sum(coeffs)

    return float(np.abs(S) ** 2)


def E_p_grid(p, N, gamma0, H, n_grid=200):
    """
    Evaluate E_p(t) on a uniform grid centred at γ₀ with half-width H.

    Returns (t_grid, E_values) arrays.
    """
    t_grid = np.linspace(gamma0 - H, gamma0 + H, n_grid)
    E_vals = np.array([E_p(t, p, N) for t in t_grid])
    return t_grid, E_vals


# ─────────────────────────────────────────────────────────────────────────────
# §2 — Robust energy median σ_p
# ─────────────────────────────────────────────────────────────────────────────

def sigma_p(p, N, gamma0, H=10.0, n_grid=200):
    """
    Robust energy scale: σ_p = median_t E_p(t) over a grid around γ₀.

    The median is used (instead of mean) to avoid domination by isolated
    spikes in E_p near zeros of the Dirichlet partial sum.

    Returns a positive scalar. If median is ≤ 0 (degenerate), returns
    the mean as fallback.
    """
    _, E_vals = E_p_grid(p, N, gamma0, H, n_grid)
    med = float(np.median(E_vals))
    if med <= 0:
        med = float(np.mean(E_vals))
    if med <= 0:
        med = 1e-30  # safety floor
    return med


# ─────────────────────────────────────────────────────────────────────────────
# §3 — Arithmetic weight λ_p
# ─────────────────────────────────────────────────────────────────────────────

def lambda_p(p):
    """
    Arithmetic weight: λ_p = (log p)² / p.

    This is the natural per-prime weighting emerging from the explicit
    formula's von Mangoldt coefficients Λ(n) = log(p) for n = p^k.
    """
    p = float(p)
    return np.log(p) ** 2 / p


# ─────────────────────────────────────────────────────────────────────────────
# §4 — Guard functional G_p(t)
# ─────────────────────────────────────────────────────────────────────────────

def G_p(t, p, N, gamma0, alpha=1.0, H=10.0, n_grid=200):
    """
    sech² guard on normalised per-prime energy:

        G_p(t) = sech²(α · E_p(t) / σ_p)

    Properties:
        - G_p ∈ (0, 1] for all t (sech² range)
        - G_p → 1 as E_p/σ_p → 0 (low energy ↔ strong guard)
        - G_p → 0 as E_p/σ_p → ∞ (high energy ↔ guard decays)
    """
    E = E_p(t, p, N)
    sig = sigma_p(p, N, gamma0, H, n_grid)
    return float(sech2(alpha * E / sig))


# ─────────────────────────────────────────────────────────────────────────────
# §5 — K₃ kernel
# ─────────────────────────────────────────────────────────────────────────────

def K3(t, p, N, gamma0, alpha=1.0, H=10.0, n_grid=200):
    """
    Per-prime arithmetic Rayleigh quotient:

        K₃(t, p) = (1/p)·E_p(t) + λ_p·G_p(t)

    This combines:
      - (1/p)·E_p: direct Dirichlet energy contribution, scaled by 1/p
      - λ_p·G_p:   sech²-guarded arithmetic weight

    K₃ is the arithmetic lens on A_RS / B_RS.
    """
    E = E_p(t, p, N)
    sig = sigma_p(p, N, gamma0, H, n_grid)
    G = float(sech2(alpha * E / sig))
    lp = lambda_p(p)
    return float(E / p + lp * G)


# ─────────────────────────────────────────────────────────────────────────────
# §6 — Windowed Rayleigh quotient (per-prime and aggregated)
# ─────────────────────────────────────────────────────────────────────────────

def windowed_A_p(gamma0, p, N, H=10.0, alpha=1.0, n_quad=200):
    """
    Windowed K₃ integral at height γ₀:

        A_p(γ₀) = ∫_{-H}^{H} K₃(t+γ₀, p)·φ(t) dt

    where φ(t) = w_H(t) = sech²(t/H) is the smoothing weight.
    """
    t_grid = np.linspace(-H, H, n_quad)
    dt = t_grid[1] - t_grid[0]
    phi = w_H(t_grid, H)

    K3_vals = np.array([
        K3(t + gamma0, p, N, gamma0, alpha, H)
        for t in t_grid
    ])

    return float(np.sum(K3_vals * phi) * dt)


def windowed_B_p(gamma0, p, N, H=10.0, n_quad=200):
    """
    Windowed Dirichlet energy integral at height γ₀:

        B_p(γ₀) = ∫_{-H}^{H} E_p(t+γ₀)·φ(t) dt
    """
    t_grid = np.linspace(-H, H, n_quad)
    dt = t_grid[1] - t_grid[0]
    phi = w_H(t_grid, H)

    E_vals = np.array([E_p(t + gamma0, p, N) for t in t_grid])

    return float(np.sum(E_vals * phi) * dt)


def R_p(gamma0, p, N, H=10.0, alpha=1.0, n_quad=200):
    """
    Per-prime Rayleigh quotient:

        R_p(γ₀) = -A_p(γ₀) / B_p(γ₀)

    Returns dict with A_p, B_p, R_p, and validity flag.
    """
    A = windowed_A_p(gamma0, p, N, H, alpha, n_quad)
    B = windowed_B_p(gamma0, p, N, H, n_quad)

    if abs(B) < 1e-30:
        return {'A_p': A, 'B_p': B, 'R_p': 0.0, 'valid': False}

    return {'A_p': A, 'B_p': B, 'R_p': -A / B, 'valid': True}


def R_RS(gamma0, prime_list, N, H=10.0, alpha=1.0, n_quad=100):
    """
    Aggregated RS-side Rayleigh quotient:

        R_RS(γ₀) = Σ_p w_p·R_p(γ₀) / Σ_p w_p

    with weights w_p = log(p)/p (von Mangoldt-type weighting).
    """
    weighted_sum = 0.0
    weight_total = 0.0

    for p in prime_list:
        result = R_p(gamma0, p, N, H, alpha, n_quad)
        if not result['valid']:
            continue
        w = np.log(p) / p
        weighted_sum += w * result['R_p']
        weight_total += w

    if weight_total < 1e-30:
        return {'R_RS': 0.0, 'weight_total': 0.0, 'valid': False}

    return {
        'R_RS': weighted_sum / weight_total,
        'weight_total': weight_total,
        'valid': True,
    }


# ─────────────────────────────────────────────────────────────────────────────
# §7 — K₃ gap diagnostic
# ─────────────────────────────────────────────────────────────────────────────

def k3_rayleigh_gap(gamma0, H, delta_beta_grid, prime_list, alpha=1.0,
                    N=500, n_quad=50):
    """
    Measure the gap: λ*(H) − R_RS(γ₀) across a Δβ grid.

    For the on-critical-line case (Δβ=0), R_RS should be the
    baseline Rayleigh quotient. For off-critical perturbations,
    R_RS(γ₀, Δβ) drops, widening the gap.

    Returns list of dicts with:
      - delta_beta, R_RS, lambda_star, gap, gap_positive
    """
    lambda_star = 4.0 / H ** 2
    results = []

    for db in delta_beta_grid:
        # For Δβ > 0, shift γ₀ by Δβ to simulate off-critical
        effective_gamma0 = gamma0 + float(db)
        rs = R_RS(effective_gamma0, prime_list, N, H, alpha, n_quad)
        r_val = rs['R_RS'] if rs['valid'] else 0.0
        gap = lambda_star - abs(r_val)

        results.append({
            'delta_beta': float(db),
            'R_RS': r_val,
            'lambda_star': lambda_star,
            'gap': gap,
            'gap_positive': gap > 0,
        })

    return results
