#!/usr/bin/env python3
"""
1_EULER_VARIATIONAL_PRINCIPLE.py

Unified Eulerian variational check on the 6D projection of the 9D
phi-weighted prime geometry:

    C_phi(T; h) = ||P6 * T_phi(T + h)|| + ||P6 * T_phi(T - h)|| - 2||P6 * T_phi(T)|| >= 0

This script is intentionally zeta-free: it works purely with the Euler-style
Dirichlet series sum

    ψ_E(T) = sum_{n=1}^N n^{-1/2} e^{-iT log n}

and builds a 9D curvature-based state vector T_phi(T) from finite-difference
second derivatives of ψ_E(T) at multiple φ-scaled step sizes.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


PHI: float = (1.0 + np.sqrt(5.0)) / 2.0
NUM_BRANCHES: int = 9
PROJECTION_DIM: int = 6


# ---------------------------------------------------------------------------
# φ-weights for the 9D branches
# ---------------------------------------------------------------------------

def _phi_weights_9d() -> np.ndarray:
    """
    Return normalized φ-weights for the 9 branches.

    weights_k ∝ φ^{-(k+1)}, k = 0..8, normalized to sum to 1.
    """
    weights = np.array([PHI ** (-(k + 1)) for k in range(NUM_BRANCHES)], dtype=float)
    total = float(np.sum(weights))
    if total == 0.0:
        return weights
    return weights / total


# ---------------------------------------------------------------------------
# 6x9 projection matrix P6
# ---------------------------------------------------------------------------

def build_projection_p6() -> np.ndarray:
    """
    Build the 6x9 projection matrix P6 used by the unified convexity test.

    Modes 0..5 are retained directly; modes 6..8 are suppressed
    (Bombieri–Vinogradov-thin directions in the conceptual framework).
    """
    p6 = np.zeros((PROJECTION_DIM, NUM_BRANCHES), dtype=float)
    for idx in range(PROJECTION_DIM):
        p6[idx, idx] = 1.0
    return p6


# ---------------------------------------------------------------------------
# Euler-style ψ_E(T) sum (prime-free Dirichlet-type)
# ---------------------------------------------------------------------------

def euler_psi_sum(T: float, N: int = 4000) -> complex:
    """
    Euler-style Dirichlet-like sum:

        ψ_E(T) = sum_{n=1}^N n^{-1/2} e^{-iT log n}

    This is a smoothed, prime-agnostic analogue of a Dirichlet/xi-type kernel.
    """
    # Ensure N is at least 1 to avoid empty arrays
    N_int = max(1, int(N))
    n = np.arange(1, N_int + 1, dtype=float)
    log_n = np.log(n)
    n_power = 1.0 / np.sqrt(n)
    phases = -T * log_n
    return np.sum(n_power * np.exp(1j * phases))


# ---------------------------------------------------------------------------
# 9D Eulerian state vector T_phi(T)
# ---------------------------------------------------------------------------

def euler_t_phi_vector(T: float, N: int = 4000, delta: float = 0.015) -> np.ndarray:
    """
    Build the 9D Eulerian vector T_phi(T) from finite-difference curvature magnitudes.

    For branch k, we use a scaled step h_k = delta * scale_k and compute

        second_k(T) ≈ [ψ_E(T + h_k) - 2 ψ_E(T) + ψ_E(T - h_k)] / h_k^2,

    then set

        T_phi_k(T) = weight_k * |second_k(T)|.
    """
    scales = np.array([1, 2, 4, 8, 16, 24, 32, 48, 64], dtype=float)
    assert len(scales) == NUM_BRANCHES
    weights = _phi_weights_9d()

    center = euler_psi_sum(T, N=N)
    vector = np.zeros(NUM_BRANCHES, dtype=float)

    for k in range(NUM_BRANCHES):
        h = float(delta * scales[k])
        # Guard against degenerate step
        if h <= 0.0:
            vector[k] = 0.0
            continue
        plus = euler_psi_sum(T + h, N=N)
        minus = euler_psi_sum(T - h, N=N)
        # Standard second finite difference
        second = (plus - 2.0 * center + minus) / (h * h)
        vector[k] = weights[k] * abs(second)

    return vector


# ---------------------------------------------------------------------------
# 6D projected norm ||P6 * T_phi(T)||_2
# ---------------------------------------------------------------------------

def projected_6d_norm(T: float, P6: np.ndarray, N: int = 4000) -> float:
    """
    Compute the 2-norm of the 6D projection of T_phi(T):

        ||P6 * T_phi(T)||_2.
    """
    t9 = euler_t_phi_vector(T, N=N)
    projected = P6 @ t9
    return float(np.linalg.norm(projected, ord=2))


# ---------------------------------------------------------------------------
# Convexity result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ConvexityResult:
    T: float
    h: float
    lhs: float
    convex: bool


# ---------------------------------------------------------------------------
# Convexity check C_phi(T; h)
# ---------------------------------------------------------------------------

def convexity_check(
    T: float,
    h: float = 0.02,
    N: int = 4000,
    P6: Optional[np.ndarray] = None,
) -> ConvexityResult:
    """
    Evaluate the discrete convexity functional:

        C_phi(T; h) = ||P6 T_phi(T + h)|| + ||P6 T_phi(T - h)|| - 2||P6 T_phi(T)||.

    The 'convex' flag is True if lhs >= -1e-10 (numerical tolerance).
    """
    if P6 is None:
        P6 = build_projection_p6()

    n_plus = projected_6d_norm(T + h, P6=P6, N=N)
    n_minus = projected_6d_norm(T - h, P6=P6, N=N)
    n_center = projected_6d_norm(T, P6=P6, N=N)

    lhs = n_plus + n_minus - 2.0 * n_center
    return ConvexityResult(T=T, h=h, lhs=float(lhs), convex=bool(lhs >= -1e-10))


# ---------------------------------------------------------------------------
# Scan convexity over a T-range
# ---------------------------------------------------------------------------

def scan_convexity(
    T_range: Tuple[float, float] = (14.0, 80.0),
    num_points: int = 120,
    h: float = 0.02,
    N: int = 4000,
) -> Dict[str, float]:
    """
    Scan C_phi(T; h) over a uniform T-grid and return summary statistics.

    Returns
    -------
    dict with keys:
      - "num_points"
      - "convexity_pass_rate"
      - "min_lhs"
      - "mean_lhs"
      - "max_lhs"
    """
    p6 = build_projection_p6()
    T_values = np.linspace(T_range[0], T_range[1], num_points)

    results = [convexity_check(float(T), h=h, N=N, P6=p6) for T in T_values]
    lhs_values = np.array([r.lhs for r in results], dtype=float)
    passes = np.array([r.convex for r in results], dtype=bool)

    return {
        "num_points": float(num_points),
        "convexity_pass_rate": float(np.mean(passes)),
        "min_lhs": float(np.min(lhs_values)),
        "mean_lhs": float(np.mean(lhs_values)),
        "max_lhs": float(np.max(lhs_values)),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  EULERIAN UNIFIED VARIATIONAL PRINCIPLE                         ║")
    print("║  6D Projected Convexity: C_phi(T;h) >= 0                        ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    summary = scan_convexity()

    print(f"\nPoints tested: {int(summary['num_points'])}")
    print(f"Convexity pass rate: {summary['convexity_pass_rate']:.2%}")
    print(f"min C_phi(T;h): {summary['min_lhs']:.6e}")
    print(f"mean C_phi(T;h): {summary['mean_lhs']:.6e}")
    print(f"max C_phi(T;h): {summary['max_lhs']:.6e}")


if __name__ == "__main__":
    main()
