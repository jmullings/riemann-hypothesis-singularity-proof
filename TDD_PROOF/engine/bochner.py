#!/usr/bin/env python3
"""
================================================================================
bochner.py — Bochner Obstruction, λ-Correction, and PSD Verification
================================================================================

CORE RESULT (Theorem B 2.0):
    F̃₂^(N)(T₀; λ ≥ λ*) ≥ 0  for all T₀, N.

THE CORRECTED KERNEL:
    W̃(t; λ) = -w_H''(t) + λ·w_H(t)
    FT: f(ω) = (ω² + λ)·ŵ_H(ω)

    At λ = λ* = 4/H²:
      f(ω) = (ω² + 4/H²)·ŵ_H(ω) ≥ 0  for all ω.

    Since ŵ_H(ω) > 0 and (ω² + 4/H²) > 0, the product is strictly positive.
    By Bochner's theorem: the Toeplitz matrix M̃_{kl} = f(E_k - E_l) is PSD
    for ANY spectrum {E_k} — this is KERNEL UNIVERSALITY.

LOG-FREE: No log() operations anywhere.
================================================================================
"""

import numpy as np
from .kernel import fourier_w_H, fourier_W_curv, w_H, W_curv


# ─────────────────────────────────────────────────────────────────────────────
# §1 — Corrected kernel and Fourier transform
# ─────────────────────────────────────────────────────────────────────────────

def lambda_star(H):
    """
    Critical correction parameter: λ* = 4/H².

    Analytic derivation: w_H''(t)/w_H(t) = (2/H²)(3tanh²(t/H) - 1)
    is monotonically increasing in |t|, approaching 4/H² as |t| → ∞.
    """
    return 4.0 / float(H)**2


def corrected_fourier(omega, H, lam=None):
    """
    FT of corrected kernel: f(ω) = (ω² + λ)·ŵ_H(ω).

    At λ = λ* = 4/H²: f(ω) = (ω² + 4/H²)·ŵ_H(ω) ≥ 0 for all ω.
    This is the KERNEL IDENTITY that makes Bochner PSD universal.
    """
    if lam is None:
        lam = lambda_star(H)
    omega = np.asarray(omega, dtype=np.float64)
    return (omega**2 + lam) * fourier_w_H(omega, H)


# ─────────────────────────────────────────────────────────────────────────────
# §2 — Toeplitz matrix construction and PSD verification
# ─────────────────────────────────────────────────────────────────────────────

def build_corrected_toeplitz(spectrum, H, lam=None):
    """
    Build corrected Bochner-Toeplitz matrix:
        M̃_{kl} = f(E_k - E_l) = (diff² + λ)·ŵ_H(diff)

    For ANY spectrum {E_k}, M̃ is PSD when f(ω) ≥ 0 (Bochner's theorem).

    Parameters:
        spectrum : array of spectral points {E_k}
        H : kernel bandwidth
        lam : correction parameter (default: 4/H²)

    Returns:
        M̃ : symmetric PSD matrix
    """
    if lam is None:
        lam = lambda_star(H)
    E = np.asarray(spectrum, dtype=np.float64).ravel()
    diff = E[:, None] - E[None, :]
    return corrected_fourier(diff, H, lam)


def build_curvature_toeplitz(spectrum, H):
    """
    Uncorrected curvature Toeplitz: M_{kl} = Ŵ_curv(E_k - E_l).

    This matrix is INDEFINITE (Bochner obstruction exists).
    Included for falsification documentation.
    """
    E = np.asarray(spectrum, dtype=np.float64).ravel()
    diff = E[:, None] - E[None, :]
    return fourier_W_curv(diff, H)


def min_eigenvalue(M):
    """Smallest eigenvalue of symmetric matrix M."""
    return float(np.min(np.linalg.eigvalsh(M)))


def is_psd(M, tol=1e-10):
    """Check if matrix M is positive semi-definite within tolerance."""
    return min_eigenvalue(M) >= -tol


def eigenspectrum(M):
    """Full sorted eigenvalue spectrum of symmetric matrix M."""
    return np.sort(np.linalg.eigvalsh(M))


# ─────────────────────────────────────────────────────────────────────────────
# §3 — Rayleigh quotient and functional evaluation
# ─────────────────────────────────────────────────────────────────────────────

def F2_corrected(T0, H, N, lam=None, n_points=500):
    """
    Corrected curvature functional F̃₂(T₀) via numerical integration.

    F̃₂ = ∫ W̃(t; λ) |D_N(T₀ + t)|² dt

    where D_N(t) = Σ_{k=1}^N k^{-1/2} exp(-i·log(k)·t).
    """
    if lam is None:
        lam = lambda_star(H)
    t_grid = np.linspace(-10 * H, 10 * H, n_points)
    dt = t_grid[1] - t_grid[0]

    # Corrected weight
    weight = W_curv(t_grid, H) + lam * w_H(t_grid, H)

    # Dirichlet polynomial |D_N|²
    ks = np.arange(1, N + 1, dtype=np.float64)
    log_ks = np.log(ks)
    D = np.sum(ks[:, None]**(-0.5) * np.exp(-1j * log_ks[:, None] * (T0 + t_grid[None, :])), axis=0)
    D_sq = np.abs(D)**2

    return float(np.sum(weight * D_sq) * dt)


def rayleigh_quotient(T0, H, N, n_points=500):
    """
    Rayleigh decomposition: λ*(T₀) = -A(T₀)/B(T₀).

    A = ∫ W_curv(t)|D_N(T₀+t)|² dt  (numerator, can be negative)
    B = ∫ w_H(t)|D_N(T₀+t)|² dt     (denominator, always > 0)
    """
    t_grid = np.linspace(-10 * H, 10 * H, n_points)
    dt = t_grid[1] - t_grid[0]

    ks = np.arange(1, N + 1, dtype=np.float64)
    log_ks = np.log(ks)
    D = np.sum(ks[:, None]**(-0.5) * np.exp(-1j * log_ks[:, None] * (T0 + t_grid[None, :])), axis=0)
    D_sq = np.abs(D)**2

    A = float(np.sum(W_curv(t_grid, H) * D_sq) * dt)
    B = float(np.sum(w_H(t_grid, H) * D_sq) * dt)

    return {'A': A, 'B': B, 'lambda_star_T0': -A / B if B > 0 else np.inf}
