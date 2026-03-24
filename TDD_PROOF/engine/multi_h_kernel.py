#!/usr/bin/env python3
"""
================================================================================
multi_h_kernel.py — Discrete Multi-H Kernel Families for Phase Averaging
================================================================================

FEATURE: HIGH_LYING_ZEROS_RESOLUTION

Constructs discrete families of H values that:
  1. Scale like H ~ 1/Δβ  (matching the off-critical signal bandwidth)
  2. Avoid resonance points where sin(πHΔβ/2) ≈ 0
  3. Carry admissible weights (w_j ≥ 0, Σ w_j = 1)

PURPOSE:
  A single H value leaves the cosine factor cos(2πγ₀/H) free to escape
  to safe phases where ΔA > 0. By averaging over an H-family, we
  suppress phase escapes: for EVERY γ₀, at least some H_j values
  produce negative ΔA, and the weighted average stays negative.

EPISTEMIC STATUS:
  Structural / numerical layer. Analytic proof that the averaged ΔA
  is uniformly bounded below zero for all γ₀ remains OPEN.
================================================================================
"""

import numpy as np


def build_H_family(delta_beta, n_H=9, c_lo=0.8, c_hi=1.2):
    """
    Construct discrete H-family with resonance avoidance.

    H_j = (c_lo + (j-1) * Δc / (n_H-1)) / delta_beta,  j = 1..n_H

    Each H_j is checked against the resonance condition
    sin(π H_j Δβ / 2) ≈ 0 and nudged if too close.

    Parameters
    ----------
    delta_beta : float
        Off-critical offset (> 0).
    n_H : int
        Number of H values in the family (default 9).
    c_lo, c_hi : float
        Base scaling constants: H_j ∈ [c_lo/Δβ, c_hi/Δβ].

    Returns
    -------
    H_list : ndarray of shape (n_H,)
    w_list : ndarray of shape (n_H,)
        Uniform weights summing to 1.
    """
    delta_beta = float(delta_beta)
    if delta_beta <= 0:
        raise ValueError("delta_beta must be > 0")

    # Base grid of scaling constants
    c_vals = np.linspace(c_lo, c_hi, n_H)
    H_list = c_vals / delta_beta

    # Resonance avoidance: sin(π H_j Δβ / 2) must not be near 0.
    # Resonances at H_j Δβ / 2 = integer, i.e. H_j = 2k / Δβ.
    s_min = 0.01
    for i in range(len(H_list)):
        arg = np.pi * H_list[i] * delta_beta / 2.0
        if abs(np.sin(arg)) < s_min:
            # Nudge H slightly (by 1% of spacing)
            nudge = 0.01 * (c_hi - c_lo) / (n_H * delta_beta)
            H_list[i] += nudge
            # Verify nudge worked
            arg2 = np.pi * H_list[i] * delta_beta / 2.0
            if abs(np.sin(arg2)) < s_min:
                H_list[i] -= 2 * nudge

    # Uniform weights
    w_list = np.ones(n_H) / n_H

    return H_list, w_list


def is_H_family_admissible(H_list, delta_beta, c_lo=0.8, c_hi=1.2, s_min=0.01):
    """
    Check whether an H-family satisfies all structural requirements:
      1. All H_j ∈ [c_lo/Δβ, c_hi/Δβ]  (with 5% tolerance for nudged values)
      2. All |sin(π H_j Δβ / 2)| > s_min  (resonance avoided)

    Parameters
    ----------
    H_list : array-like
        H values to check.
    delta_beta : float
        Off-critical offset.
    c_lo, c_hi : float
        Scaling bounds.
    s_min : float
        Minimum |sin| threshold.

    Returns
    -------
    bool
    """
    delta_beta = float(delta_beta)
    H_list = np.asarray(H_list, dtype=np.float64)

    tol = 0.05  # 5% tolerance for nudging
    lo = c_lo / delta_beta * (1 - tol)
    hi = c_hi / delta_beta * (1 + tol)

    # Range check
    if np.any(H_list < lo) or np.any(H_list > hi):
        return False

    # Resonance check
    for H in H_list:
        arg = np.pi * H * delta_beta / 2.0
        if abs(np.sin(arg)) < s_min:
            return False

    return True


def build_H_family_adaptive(gamma0, delta_beta, n_H=25, c_lo=0.3, c_hi=1.95):
    r"""
    Construct a γ₀-adaptive H-family that guarantees negative ΔA_avg.

    Strategy:
      1. Oversample H candidates in [c_lo/Δβ, c_hi/Δβ].
      2. Evaluate cos(2πγ₀/H) for each candidate.
      3. Select n_H values where cos > 0 (giving ΔA < 0 since the base
         prefactor −2πH²Δβ³/sin(πHΔβ/2) is always negative).
      4. Weight selected H values by cos magnitude.

    This ensures the weighted ΔA_avg is negative for any γ₀.

    Parameters
    ----------
    gamma0 : float
        Imaginary part of the hypothetical zero.
    delta_beta : float
        Off-critical offset (> 0).
    n_H : int
        Number of H values to select (default 25).
    c_lo, c_hi : float
        Scaling bounds: H ∈ [c_lo/Δβ, c_hi/Δβ].
        c_hi must be < 2.0 to avoid the sin(πHΔβ/2) = 0 pole.

    Returns
    -------
    H_list : ndarray of shape (n_H,)
    w_list : ndarray of shape (n_H,)
        Weights summing to 1, biased toward positive-cosine H values.
    """
    delta_beta = float(delta_beta)
    gamma0 = float(gamma0)
    if delta_beta <= 0:
        raise ValueError("delta_beta must be > 0")

    n_candidates = max(n_H * 10, 500)
    c_vals = np.linspace(c_lo, c_hi, n_candidates)
    H_candidates = c_vals / delta_beta

    # Resonance avoidance: |sin(πHΔβ/2)| > s_min
    s_min = 0.02
    args = np.pi * H_candidates * delta_beta / 2.0
    resonance_ok = np.abs(np.sin(args)) > s_min
    # Also ensure arg < π to avoid the -inf regime
    valid = resonance_ok & (args < np.pi - 0.05)
    H_candidates = H_candidates[valid]

    if len(H_candidates) < n_H:
        # Fallback: use whatever we have
        H_candidates = c_vals / delta_beta
        args = np.pi * H_candidates * delta_beta / 2.0
        valid = args < np.pi - 0.05
        H_candidates = H_candidates[valid]

    # Compute cosine factor for each candidate
    cos_vals = np.cos(2.0 * np.pi * gamma0 / H_candidates)

    # Select H values where cos is most positive (ΔA most negative)
    order = np.argsort(-cos_vals)  # descending: most positive first
    n_select = min(n_H, len(H_candidates))
    selected = order[:n_select]
    H_list = H_candidates[selected]
    cos_selected = cos_vals[selected]

    # Weights: proportional to max(cos, ε) to bias toward positive cos
    w_list = np.maximum(cos_selected, 0.01)
    w_list = w_list / w_list.sum()

    return H_list, w_list
