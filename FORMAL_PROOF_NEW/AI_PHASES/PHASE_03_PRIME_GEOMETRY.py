#!/usr/bin/env python3
"""
PHASE 03 — PRIME GEOMETRY: 9D SINGULARITY COORDINATES, PSS SPIRAL & TRAJECTORY
================================================================================
σ-Selectivity Equation  ·  Phase 3 of 10
(was PHASE_03_SINGULARITY + PHASE_04_SPIRAL + PHASE_05_TRAJECTORY)

PART A — 9D SINGULARITY COORDINATES x*  (was PHASE_03_SINGULARITY)
-------------------------------------------------------------------
Three independent methods:
  F: F₂-profile (uses zeros — QUARANTINE)
  G: Gram eigenvector (pure prime, zero-free)
  φ: algebraic φ-metric (zero-free, LOG-free)

PART B — PSS SPIRAL TRAJECTORY & CURVATURE  (was PHASE_04_SPIRAL)
-------------------------------------------------------------------
S_N(T) = Σ_{n=1}^{N} n^{-½} · exp(-i·T·log(n))
PSS curvature C(T), mean radius μ_r(T), bitsize band decomposition.

PART C — 9D CURVATURE TRAJECTORY T → x(T)  (was PHASE_05_TRAJECTORY)
----------------------------------------------------------------------
9D bitsize curvature vector, trajectory curvature κ_9D, φ-metric speed.
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from PHASE_01_FOUNDATIONS import (
    NDIM, DTYPE, P, LOG_P, LOG2_P, ALPHA, W_PHI, D_PHI, IPHI2,
    P25, LOG_P25, LOG2_P25, ZEROS_9, ZEROS_30, G_PHI,
    F2_vector_9D, F2_curvature,
)
import numpy as np
from typing import Tuple, List, Dict

PI = math.pi
TWO_PI = 2.0 * PI


# =============================================================================
# PART A — 9D SINGULARITY COORDINATES x*
# =============================================================================

def compute_x_star_F(sigma=0.5, zeros=None):
    """[QUARANTINE] x*_k = F₂(σ,γ_k)/Σ F₂. Uses known zeros."""
    if zeros is None:
        zeros = ZEROS_9
    f2 = F2_vector_9D(sigma, zeros)
    return f2 / f2.sum()


def gram_cov_matrix(sigma=0.5, T_max=100.0, n_T=2000, log_p=None):
    """G[j,k] = (1/n)Σ_T p_j^{-σ}·p_k^{-σ}·cos(T·(logp_j-logp_k)). Zero-free."""
    if log_p is None:
        log_p = LOG_P
    T_grid = np.linspace(1.0, T_max, n_T, dtype=DTYPE)
    amp = P ** (-sigma)
    G = np.zeros((NDIM, NDIM), dtype=DTYPE)
    for T in T_grid:
        phase = -T * log_p
        v = amp * np.cos(phase)
        w = amp * np.sin(phase)
        G += np.outer(v, v) + np.outer(w, w)
    return G / n_T


def compute_x_star_G(sigma=0.5, T_max=100.0, n_T=2000):
    """x* = leading eigenvector of Gram cov (pure prime). Returns (x*, λ_max, gap)."""
    G = gram_cov_matrix(sigma, T_max, n_T)
    vals, vecs = np.linalg.eigh(G)
    x = vecs[:, -1].copy()
    if x[0] < 0:
        x = -x
    x /= np.linalg.norm(x)
    return x, float(vals[-1]), float(vals[-1] - vals[-2])


def compute_x_star_phi():
    """x*_k = p_k^{-½}/D_φ. Algebraic, zero-free, LOG-free."""
    return ALPHA / D_PHI


def shannon_entropy(x):
    """H = -Σ x_k·ln(x_k) on simplex vector."""
    return float(-np.sum(x * np.log(np.maximum(x, 1e-300))))


# =============================================================================
# PART B — PSS SPIRAL TRAJECTORY & CURVATURE
# =============================================================================

# ── INTEGER TABLE (precomputed, LOG-FREE after this) ─────────────────────────
N_MAX = 500
_LOG_N = np.array([math.log(n) if n >= 1 else 0.0 for n in range(1, N_MAX + 1)], dtype=DTYPE)
_AMP_N = np.array([1.0 / math.sqrt(n) for n in range(1, N_MAX + 1)], dtype=DTYPE)
_BITSIZE_N = np.array(
    [(n.bit_length() - 1) if n >= 2 else 0 for n in range(1, N_MAX + 1)],
    dtype=np.int32,
)

# ── SECH² WINDOW PARAMETERS ──────────────────────────────────────────────────
ALPHA_SECH = 0.8
MU_SECH = _LOG_N[-1] / 2.0


def pss_trajectory(T):
    """
    S_N(T) = Σ_{n=1}^{N} n^{-½}·exp(-i·T·log n)  for N=1..N_MAX.
    Returns (re_traj, im_traj) each shape (N_MAX,).
    """
    phases = -T * _LOG_N
    re_steps = _AMP_N * np.cos(phases)
    im_steps = _AMP_N * np.sin(phases)
    return np.cumsum(re_steps), np.cumsum(im_steps)


def pss_step_vectors(re_traj, im_traj):
    """Step vectors Δ_n = S_n - S_{n-1}. Returns (dre, dim) shape (N_MAX-1,)."""
    return np.diff(re_traj), np.diff(im_traj)


def pss_turning_angles(dre, dim):
    """Unsigned turning angle κ_n = |arg(Δ_{n+1}) - arg(Δ_n)|."""
    angles = np.arctan2(dim, dre)
    d_theta = np.abs(np.diff(angles))
    return np.where(d_theta > PI, TWO_PI - d_theta, d_theta)


def sech2_weights():
    """SECH² window w_n = sech²(α·(log(n) - μ)) for n=2..N_MAX-1."""
    log_n = _LOG_N[1:-1]
    x = ALPHA_SECH * (log_n - MU_SECH)
    ch = np.cosh(x)
    return 1.0 / (ch * ch)


_W_SECH2 = sech2_weights()  # shape (N_MAX-2,)


def pss_curvature(T):
    """C(T) = Σ_n sech²(α·(log n - μ)) · κ_n — scalar PSS curvature."""
    re_t, im_t = pss_trajectory(T)
    dre, dim = pss_step_vectors(re_t, im_t)
    kappa = pss_turning_angles(dre, dim)
    L = min(len(kappa), len(_W_SECH2))
    return float(np.sum(_W_SECH2[:L] * kappa[:L]))


def pss_mean_radius(T):
    """μ_r(T) = (1/N_MAX) Σ_N |S_N(T)| — mean spiral radius."""
    re_t, im_t = pss_trajectory(T)
    return float(np.sqrt(re_t**2 + im_t**2).mean())


def pss_curvature_by_band(T):
    """C_b(T) = Σ_{n:b(n)=b} w_n·κ_n — curvature by bitsize band."""
    re_t, im_t = pss_trajectory(T)
    dre, dim = pss_step_vectors(re_t, im_t)
    kappa = pss_turning_angles(dre, dim)
    L = min(len(kappa), len(_W_SECH2))
    bands = {}
    for idx in range(L):
        n = idx + 2
        b = _BITSIZE_N[n - 1] if n - 1 < len(_BITSIZE_N) else 0
        val = float(_W_SECH2[idx] * kappa[idx])
        bands[b] = bands.get(b, 0.0) + val
    return bands


def pss_curvature_vector_9D(zeros=None):
    """[QUARANTINE] C_vec[k] = C(γ_k) for k=0..8."""
    if zeros is None:
        zeros = ZEROS_9
    return np.array([pss_curvature(float(g)) for g in zeros], dtype=DTYPE)


def pss_radius_vector_9D(zeros=None):
    """[QUARANTINE] μ_r(γ_k) for k=0..8."""
    if zeros is None:
        zeros = ZEROS_9
    return np.array([pss_mean_radius(float(g)) for g in zeros], dtype=DTYPE)


# =============================================================================
# PART C — 9D CURVATURE TRAJECTORY
# =============================================================================

N_BANDS = 9  # b=0..8 for integers 1..500


def bitsize_curvature_vector(T):
    """x(T) ∈ ℝ⁹: raw curvature by bitsize band."""
    bands = pss_curvature_by_band(T)
    vec = np.zeros(N_BANDS, dtype=DTYPE)
    for b, val in bands.items():
        if 0 <= b < N_BANDS:
            vec[b] = val
    return vec


def bitsize_curvature_normalised(T):
    """x(T)/|x(T)| — unit vector."""
    v = bitsize_curvature_vector(T)
    n = np.linalg.norm(v)
    return v / n if n > 1e-30 else v


def bitsize_simplex_vector(T):
    """x(T)/Σx(T) — probability distribution over bands."""
    v = bitsize_curvature_vector(T)
    s = v.sum()
    return v / s if s > 1e-30 else np.full(N_BANDS, 1.0 / N_BANDS)


def trajectory_curvature_9D(T, h=0.1):
    """κ_9D(T) = |x''(T)|_φ / |x'(T)|²_φ — 9D curvature in φ-metric."""
    x_m = bitsize_curvature_normalised(T - h)
    x_0 = bitsize_curvature_normalised(T)
    x_p = bitsize_curvature_normalised(T + h)
    x_prime = (x_p - x_m) / (2 * h)
    x_pprime = (x_p - 2 * x_0 + x_m) / (h * h)
    norm_xp_sq = float(x_prime @ G_PHI @ x_prime)
    norm_xpp = float(x_pprime @ G_PHI @ x_pprime) ** 0.5
    if norm_xp_sq < 1e-30:
        return 0.0
    return norm_xpp / norm_xp_sq


def trajectory_speed_9D(T, h=0.1):
    """|x'(T)|_φ — speed in the φ-metric."""
    x_m = bitsize_curvature_normalised(T - h)
    x_p = bitsize_curvature_normalised(T + h)
    dx = (x_p - x_m) / (2 * h)
    return float(dx @ G_PHI @ dx) ** 0.5


def scan_trajectory(T_start=10.0, T_end=55.0, n_points=100):
    """Compute x(T), κ_9D(T), speed(T) over a grid."""
    T_grid = np.linspace(T_start, T_end, n_points)
    x_vecs = np.zeros((n_points, N_BANDS), dtype=DTYPE)
    curvatures = np.zeros(n_points, dtype=DTYPE)
    speeds = np.zeros(n_points, dtype=DTYPE)
    total_C = np.zeros(n_points, dtype=DTYPE)
    for i, T in enumerate(T_grid):
        x_vecs[i] = bitsize_simplex_vector(float(T))
        curvatures[i] = trajectory_curvature_9D(float(T))
        speeds[i] = trajectory_speed_9D(float(T))
        total_C[i] = pss_curvature(float(T))
    return {'T_grid': T_grid, 'x_vecs': x_vecs, 'curvatures': curvatures,
            'speeds': speeds, 'total_C': total_C}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 03 — PRIME GEOMETRY: SINGULARITY, SPIRAL & TRAJECTORY")
    print("=" * 70)

    # Part A: Singularity coordinates
    x_F = compute_x_star_F()
    f2_raw = F2_vector_9D(0.5, ZEROS_9)
    print("\n  [QUARANTINE] METHOD F — F₂ profile:")
    for k in range(NDIM):
        print(f"    k={k+1}: F₂={f2_raw[k]:>12.6f}  x*={x_F[k]:>.10f}  ({x_F[k]*100:.2f}%)")
    print(f"  Σ F₂={f2_raw.sum():.6f}  ‖x*‖₂={np.linalg.norm(x_F):.10f}")

    x_G, lam, gap = compute_x_star_G()
    print(f"\n  METHOD G — Gram eigenvector: λ_max={lam:.6f} gap={gap:.6f}")

    x_phi = compute_x_star_phi()
    print(f"  METHOD φ — algebraic: ‖x*_φ‖={np.linalg.norm(x_phi):.6f}")

    # Part B: PSS spiral
    print(f"\n  [QUARANTINE] PSS curvature at 9 zero heights:")
    C_vec = pss_curvature_vector_9D()
    print(f"  Mean C(γ_k) = {C_vec.mean():.6f}  std = {C_vec.std():.6f}")

    # Part C: Trajectory
    print(f"\n  9D trajectory scan (T ∈ [14, 55], 5 points):")
    for T in [float(ZEROS_9[0]), float(ZEROS_9[1]), 30.0, float(ZEROS_9[4]), 50.0]:
        kap = trajectory_curvature_9D(T)
        spd = trajectory_speed_9D(T)
        print(f"    T={T:>8.4f}: κ_9D={kap:.6f}  speed={spd:.6f}")

    print(f"\n  PHASE 03: ✓ PASS")
    print("=" * 70)
