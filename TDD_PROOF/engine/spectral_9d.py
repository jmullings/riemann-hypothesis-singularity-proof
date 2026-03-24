#!/usr/bin/env python3
"""
================================================================================
spectral_9d.py — 9D Golden-Ratio Spectral Operator
================================================================================

Constructs a TRUE 9-dimensional spectral operator via separable tensor
product of prime-direction sub-operators.

ARCHITECTURE:
  For each prime direction j = 1..9 (primes 2,3,5,...,23):
      h_j = -(1/φ^{j+1}) d²/dx_j² + (A/p_j)·sech²(x/w_j)

  9D eigenvalues are tensor sums: E = Σ λ_j^{(k_j)}

THE WEYL ADVANTAGE:
  1D: N(E) ~ E^{0.5}   → trapped below T log T
  9D: N(E) ~ E^{4.5}   → vastly exceeds T log T

LOG-FREE PROTOCOL:
  All ln(p) values are precomputed ONCE and frozen.
  No runtime log() calls in operator building.
  Bit-size via n.bit_length() (pure integer operation).
================================================================================
"""

import math
import heapq
import numpy as np

# ─────────────── MODULE-LEVEL CONSTANTS (ONE-TIME, FROZEN) ───────────────────

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PRIMES_9 = [2, 3, 5, 7, 11, 13, 17, 19, 23]
_NDIM = 9

# Precomputed prime logs (frozen — the ONLY use of math.log in this module)
_PRIME_LN = np.array([math.log(p) for p in PRIMES_9], dtype=np.float64)
_LN2 = math.log(2)

# Precomputed prime bitsizes (integer op only)
_PRIME_BITSIZE = np.array([p.bit_length() - 1 for p in PRIMES_9], dtype=np.int32)

# Fractional bitsize offset: δ_b(p) = ln(p) - b(p)·ln(2)
_PRIME_FRAC_BITSIZE = _PRIME_LN - _PRIME_BITSIZE.astype(np.float64) * _LN2

# φ-weights for kinetic scaling
_PHI_WEIGHTS = np.array([PHI ** (j + 1) for j in range(_NDIM)], dtype=np.float64)
_INV_PHI_WEIGHTS = 1.0 / _PHI_WEIGHTS


# ─────────────────────────────────────────────────────────────────────────────
# §1 — GOLDEN φ-METRIC
# ─────────────────────────────────────────────────────────────────────────────

def phi_metric_9d():
    """
    9×9 golden ratio metric tensor: g_{ij} = φ^{(i+1)+(j+1)}.
    Rank-1 (= w·w^T where w_j = φ^{j+1}) and positive semidefinite.
    """
    idx = np.arange(1, _NDIM + 1, dtype=np.float64)
    w = PHI ** idx
    return np.outer(w, w)


def phi_metric_regularised(epsilon=1.0):
    """Positive definite φ-metric: G_reg = G_φ + ε·I."""
    return phi_metric_9d() + epsilon * np.eye(_NDIM)


# ─────────────────────────────────────────────────────────────────────────────
# §2 — BIT-SIZE ENERGY (LOG-FREE)
# ─────────────────────────────────────────────────────────────────────────────

def _sech2(x):
    """Stable sech²(x) = 1/cosh²(x)."""
    x = np.asarray(x, dtype=np.float64)
    safe = np.clip(x, -350, 350)
    return 1.0 / np.cosh(safe) ** 2


def bitsize_prime_corrections():
    """
    Bit-size energy for the 9 primes:
      E_bit(p_j) = (1 - sech²(δ_b)) · |δ_b|
    where δ_b = ln(p) - b(p)·ln(2).  Uses ONLY precomputed values.
    """
    s = _sech2(_PRIME_FRAC_BITSIZE)
    return (1.0 - s) * np.abs(_PRIME_FRAC_BITSIZE)


# ─────────────────────────────────────────────────────────────────────────────
# §3 — 1D PRIME-DIRECTION OPERATORS
# ─────────────────────────────────────────────────────────────────────────────

def build_prime_potential(x_grid, dim_j, base_depth=5.0, base_width=2.0):
    """
    V_j(x) = (A/p_j)·(1 + 0.1·E_bit(p_j))·sech²(x/w_j)
    where w_j = base_width·(1 + 0.05·j).
    """
    x = np.asarray(x_grid, dtype=np.float64)
    p_j = PRIMES_9[dim_j]
    bit_corr = bitsize_prime_corrections()[dim_j]
    w_j = base_width * (1.0 + 0.05 * dim_j)
    depth = (base_depth / p_j) * (1.0 + 0.1 * bit_corr)
    arg = np.clip(x / w_j, -500.0, 500.0)
    return depth / np.cosh(arg) ** 2


def _build_1d_hamiltonian(x_grid, dim_j, base_depth=5.0, base_width=2.0):
    """
    h_j = -(1/φ^{j+1})·d²/dx² + V_j(x)
    3-point stencil for kinetic energy.
    """
    x = np.asarray(x_grid, dtype=np.float64)
    n = len(x)
    dx = x[1] - x[0]
    k_coeff = _INV_PHI_WEIGHTS[dim_j]

    H = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        H[i, i] = 2.0 * k_coeff / dx ** 2
        if i > 0:
            H[i, i - 1] = -k_coeff / dx ** 2
        if i < n - 1:
            H[i, i + 1] = -k_coeff / dx ** 2

    V = build_prime_potential(x, dim_j, base_depth, base_width)
    for i in range(n):
        H[i, i] += V[i]
    return H


def solve_1d_eigenvalues(x_grid, dim_j, base_depth=5.0, base_width=2.0):
    """Solve h_j·ψ = λ·ψ and return sorted eigenvalues."""
    H = _build_1d_hamiltonian(x_grid, dim_j, base_depth, base_width)
    return np.sort(np.linalg.eigvalsh(H))


# ─────────────────────────────────────────────────────────────────────────────
# §4 — 9D TENSOR PRODUCT EIGENVALUES (MIN-HEAP)
# ─────────────────────────────────────────────────────────────────────────────

def tensor_lowest_eigenvalues(evals_per_dim, n_lowest=200):
    """
    Find n_lowest smallest 9D eigenvalues:  E = Σ λ_j^{(k_j)}.
    Min-heap extraction avoids building the full n^9 × n^9 matrix.
    """
    ndim = len(evals_per_dim)
    sorted_evals = [np.sort(np.asarray(e, dtype=np.float64)) for e in evals_per_dim]
    for j, ev in enumerate(sorted_evals):
        if len(ev) == 0:
            raise ValueError(f"Dimension {j} has no eigenvalues")

    start = tuple([0] * ndim)
    start_E = sum(float(sorted_evals[j][0]) for j in range(ndim))
    heap = [(start_E, start)]
    visited = {start}
    result = []

    while heap and len(result) < n_lowest:
        E, idx = heapq.heappop(heap)
        result.append(E)
        for d in range(ndim):
            new_idx = list(idx)
            new_idx[d] += 1
            if new_idx[d] < len(sorted_evals[d]):
                new_idx = tuple(new_idx)
                if new_idx not in visited:
                    visited.add(new_idx)
                    new_E = sum(float(sorted_evals[j][new_idx[j]]) for j in range(ndim))
                    heapq.heappush(heap, (new_E, new_idx))

    return np.array(result, dtype=np.float64)


# ─────────────────────────────────────────────────────────────────────────────
# §5 — FULL 9D SPECTRUM EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def get_9d_spectrum(n_lowest=100, n_per_dim=25, domain_L=10.0,
                    base_depth=5.0, base_width=2.0):
    """
    Build all 9 prime-direction sub-operators, solve each 1D eigenvalue
    problem, then extract n_lowest tensor-product eigenvalues.

    Returns sorted 1D array of 9D eigenvalues.
    """
    x_grid = np.linspace(-domain_L, domain_L, n_per_dim)

    evals_per_dim = []
    for j in range(_NDIM):
        ev = solve_1d_eigenvalues(x_grid, j, base_depth, base_width)
        evals_per_dim.append(ev)

    return tensor_lowest_eigenvalues(evals_per_dim, n_lowest)


# ─────────────────────────────────────────────────────────────────────────────
# §6 — SPECTRAL COUNTING
# ─────────────────────────────────────────────────────────────────────────────

def spectral_count_9d(eigenvalues, E_vals):
    """N_9D(E) = #{E_n ≤ E} for each E in E_vals."""
    evals = np.sort(np.asarray(eigenvalues, dtype=np.float64))
    return np.array([int(np.sum(evals <= E)) for E in np.asarray(E_vals)],
                    dtype=np.float64)


def weyl_9d_theoretical(E_max, L=20.0, dim=9):
    """Theoretical 9D Weyl prediction: N(E) ~ (L/2π)^d · ω_d · E^{d/2}."""
    if E_max <= 0:
        return 0.0
    omega_d = (np.pi ** (dim / 2.0)) / math.gamma(dim / 2.0 + 1)
    return (L / (2 * np.pi)) ** dim * omega_d * E_max ** (dim / 2.0)
