#!/usr/bin/env python3
"""
================================================================================
kernel.py — The sech² Kernel and Fourier Transforms
================================================================================

MATHEMATICAL FOUNDATION:
    w_H(t) = sech²(t/H)                                       (smoothing kernel)
    W_curv(t) = -w_H''(t) = -(2/H²)(3tanh²(t/H)-1)sech²(t/H) (curvature weight)
    ŵ_H(ω) = πH²ω / sinh(πHω/2)                               (FT of kernel)
    Ŵ_curv(ω) = ω²ŵ_H(ω) ≥ 0                                 (FT of curvature)

KEY PROPERTIES:
    1. sech²(x) ∈ [0, 1] for all real x
    2. w_H ∈ S(ℝ) — Schwartz class (exponential decay, smooth)
    3. ŵ_H(ω) > 0 for all ω — strictly positive Fourier transform
    4. ∫ w_H dt = 2H, ŵ_H(0) = 2H

NO LOG OPERATIONS — entire module is log()-free by design.
================================================================================
"""

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# §1 — Core sech²
# ─────────────────────────────────────────────────────────────────────────────

def sech2(x):
    """
    sech²(x) = 1/cosh²(x).

    Numerically stable: returns 0 for |x| > 350 (cosh² overflow).
    Invariant: 0 ≤ sech²(x) ≤ 1 for all real x.
    """
    x = np.asarray(x, dtype=np.float64)
    ax = np.abs(x)
    return np.where(ax > 350.0, 0.0, 1.0 / np.cosh(np.minimum(ax, 350.0)) ** 2)


# ─────────────────────────────────────────────────────────────────────────────
# §2 — Smoothing kernel and curvature weight
# ─────────────────────────────────────────────────────────────────────────────

def w_H(t, H):
    """Smoothing kernel: w_H(t) = sech²(t/H). Even, Schwartz, w_H(0) = 1."""
    return sech2(np.asarray(t, dtype=np.float64) / float(H))


def w_H_deriv2(t, H):
    """w_H''(t) = (2/H²)(3tanh²(t/H) - 1)sech²(t/H)."""
    H = float(H)
    t = np.asarray(t, dtype=np.float64)
    u = np.clip(t / H, -350, 350)
    return (2.0 / H**2) * (3.0 * np.tanh(u)**2 - 1.0) * sech2(t / H)


def W_curv(t, H):
    """Curvature weight: W_curv(t) = -w_H''(t)."""
    return -w_H_deriv2(t, H)


# ─────────────────────────────────────────────────────────────────────────────
# §3 — Fourier transforms
# ─────────────────────────────────────────────────────────────────────────────

def fourier_w_H(omega, H):
    """
    ŵ_H(ω) = πH²ω / sinh(πHω/2).

    At ω = 0: ŵ_H(0) = 2H (L'Hôpital).
    Strictly positive for all ω ∈ ℝ.
    """
    omega = np.asarray(omega, dtype=np.float64)
    H = float(H)
    arg = np.pi * H * omega / 2.0
    safe = np.clip(arg, -350, 350)
    sinh_val = np.sinh(safe)
    at_zero = np.abs(omega) < 1e-15
    denom = np.where(at_zero, 1.0, sinh_val)
    denom = np.where(np.abs(denom) < 1e-300, 1e-300, denom)
    return np.where(at_zero, 2.0 * H, np.pi * H**2 * omega / denom)


def fourier_W_curv(omega, H):
    """Ŵ_curv(ω) = ω²ŵ_H(ω) ≥ 0."""
    omega = np.asarray(omega, dtype=np.float64)
    return omega**2 * fourier_w_H(omega, H)


def fourier_sech4(omega, H):
    r"""
    Fourier transform of sech⁴(t/H).

    Closed-form (standard result via residue calculus):
        FT[sech⁴(t/H)](ω) = πH²ω(4 + H²ω²) / (6 sinh(πHω/2))

    At ω = 0: FT[sech⁴(t/H)](0) = 4H/3  (by L'Hôpital or direct integral).

    Derivation: ∫ sech⁴(t) dt = 4/3 (standard), and the FT is obtained
    via the recurrence for sech^{2n} or by contour integration.
    """
    omega = np.asarray(omega, dtype=np.float64)
    H = float(H)
    arg = np.pi * H * omega / 2.0
    safe = np.clip(arg, -350, 350)
    at_zero = np.abs(omega) < 1e-15
    sinh_val = np.sinh(safe)
    denom = np.where(at_zero, 1.0, sinh_val)
    denom = np.where(np.abs(denom) < 1e-300, 1e-300, denom)
    return np.where(
        at_zero,
        4.0 * H / 3.0,
        np.pi * H**2 * omega * (4.0 + H**2 * omega**2) / (6.0 * denom),
    )


def fourier_g_lambda(omega, H, lam):
    r"""
    Fourier transform of the corrected kernel g_λ(t) = −w_H″(t) + λ w_H(t).

    ĝ_λ(ω) = (ω² + λ) · ŵ_H(ω)

    Since ŵ_H(ω) > 0 for all ω, the sign of ĝ_λ(ω) depends solely on
    ω² + λ.  For λ ≥ 0 this is always positive, so ĝ_λ(ω) ≥ 0 for all ω.

    IMPORTANT: ĝ_λ(ω) ≥ 0 pointwise does NOT imply ĝ_λ is positive-definite.
    A function can be everywhere non-negative yet not positive-definite.
    (Example: f(x) = 1 + x² is positive everywhere but not PD.)
    Positive-definiteness of ĝ_λ is governed by Bochner's theorem applied
    to the *spectral measure* g_λ(t) dt, NOT by the pointwise sign of ĝ_λ.
    """
    omega = np.asarray(omega, dtype=np.float64)
    return (omega**2 + lam) * fourier_w_H(omega, H)


# ─────────────────────────────────────────────────────────────────────────────
# §4 — Schwartz seminorms (for Barrier 2 verification)
# ─────────────────────────────────────────────────────────────────────────────

def schwartz_seminorm(H, m, k, n_grid=5000):
    """
    Schwartz seminorm p_{m,k}(w_H) = sup_t |t^m · d^k w_H / dt^k|.

    w_H ∈ S(ℝ) requires all p_{m,k} < ∞.
    Computed numerically on a dense grid.
    """
    t = np.linspace(-20 * H, 20 * H, n_grid)
    # Compute k-th derivative via finite differences on sech²(t/H)
    if k == 0:
        f = w_H(t, H)
    elif k == 1:
        u = np.clip(t / float(H), -350, 350)
        f = -(2.0 / float(H)) * sech2(t / float(H)) * np.tanh(u)
    elif k == 2:
        f = w_H_deriv2(t, H)
    else:
        # Higher derivatives via central differences
        dt = t[1] - t[0]
        f = w_H(t, H)
        for _ in range(k):
            f = np.gradient(f, dt)
    integrand = np.abs(t**m * f)
    return float(np.max(integrand))
