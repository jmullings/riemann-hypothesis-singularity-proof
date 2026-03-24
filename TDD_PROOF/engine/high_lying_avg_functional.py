#!/usr/bin/env python3
"""
================================================================================
high_lying_avg_functional.py — Phase-Averaged Off-Critical Functional
================================================================================

FEATURE: HIGH_LYING_ZEROS_RESOLUTION

Implements the discrete averaged functional for detecting off-critical zeros
via a uniform negative signal in the small-Δβ regime, robust across γ₀ heights.

CORE IDEA:
  For a single H, the off-critical ΔA carries a cosine factor cos(2πγ₀/H)
  that can flip sign depending on γ₀. By averaging over an H-family
  {H_1, ..., H_K} with weights {w_j}, we suppress phase escapes:

    ΔA_avg(γ₀, Δβ) = Σ_j w_j · ΔA(γ₀, Δβ, H_j)

  The averaged signal remains negative for all γ₀ when the H-family is
  sufficiently dense and well-spread.

SCALING LAW (small Δβ):
    ΔA_avg ~ -c₁·Δβ        (linear, from the base formula)
    λ*·B_avg ~ c₂·Δβ²      (quadratic, since λ* = 4/H² ~ Δβ²)
    F_avg = ΔA_avg + λ*·B_avg ~ -c₁Δβ + c₂Δβ²  < 0 for small Δβ

EPISTEMIC STATUS:
  Numerical / structural layer. Analytic uniform bounds on ΔA_avg and
  B growth as T → ∞ remain OPEN.
================================================================================
"""

import numpy as np

from .offcritical import weil_delta_A_gamma0_dependent
from .bochner import lambda_star, rayleigh_quotient as bochner_rq
from .kernel import w_H


def delta_A_offcritical(gamma0, delta_beta, H):
    """
    Off-critical ΔA contribution for a single (γ₀, Δβ, H) triple.

    Uses the full γ₀-dependent Weil formula:
      ΔA(γ₀, Δβ, H) = -2πH²Δβ³/sin(πHΔβ/2) · cos(2πγ₀/H)
    """
    return weil_delta_A_gamma0_dependent(gamma0, delta_beta, H)


def B_floor(H, T, N, n_points=500):
    """
    B(T₀, H) = ∫ w_H(t) |D_N(T₀+t)|² dt  (always > 0).

    This is the denominator of the Rayleigh decomposition, extracted
    from the existing bochner.py rayleigh_quotient implementation.
    """
    rq = bochner_rq(float(T), float(H), int(N), n_points=n_points)
    return rq['B']


def F_single(T, H, delta_beta, N, gamma0=None, n_points=500):
    """
    Single-H off-critical functional decomposition.

    Returns dict with:
      A_off   : ΔA(γ₀, Δβ, H) — off-critical contribution
      B       : ∫ w_H |D_N|² dt — correction floor denominator
      lambda_star : 4/H² — correction threshold
      total   : A_off + λ*·B — the full corrected functional
    """
    if gamma0 is None:
        gamma0 = float(T)

    A_off = delta_A_offcritical(gamma0, delta_beta, H)
    B = B_floor(H, T, N, n_points=n_points)
    lam = lambda_star(H)
    total = A_off + lam * B

    return {
        'A_off': A_off,
        'B': B,
        'lambda_star': lam,
        'total': total,
    }


def F_avg(T, H_list, w_list, delta_beta, N, gamma0=None, n_points=500):
    """
    Phase-averaged off-critical functional over an H-family.

    F_avg = Σ_j w_j · F_single(T, H_j, Δβ, N)

    Returns dict with:
      A_off_avg   : Σ_j w_j · ΔA(γ₀, Δβ, H_j)
      B_avg       : Σ_j w_j · B(H_j, T, N)
      total_avg   : Σ_j w_j · (ΔA_j + λ*_j · B_j)
    """
    if gamma0 is None:
        gamma0 = float(T)

    H_list = np.asarray(H_list, dtype=np.float64)
    w_list = np.asarray(w_list, dtype=np.float64)

    A_off_avg = 0.0
    B_avg = 0.0
    total_avg = 0.0

    for H_j, w_j in zip(H_list, w_list):
        result = F_single(T, float(H_j), delta_beta, N,
                          gamma0=gamma0, n_points=n_points)
        A_off_avg += w_j * result['A_off']
        B_avg += w_j * result['B']
        total_avg += w_j * result['total']

    return {
        'A_off_avg': A_off_avg,
        'B_avg': B_avg,
        'total_avg': total_avg,
    }
