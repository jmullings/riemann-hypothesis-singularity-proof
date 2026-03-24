#!/usr/bin/env python3
r"""
================================================================================
euler_form.py — Non-Log Spectral Protocol (Euler form x = e^T)
================================================================================

Re-expresses the spectral-arithmetic duality in the Euler variable
T = ln x, so that all dynamics are additive in T-space and the
leading exponential structure becomes manifest.

KEY IDEA (todo-high.md §B):
  - Replace x-space sums over primes with T-space exponentials.
  - Spectral times τ_n = ln(p_n) are computed ONCE and stored as data.
  - All subsequent operations use e^{-t τ_n} — pure Laplace / heat-flow.

THREE CONSTRUCTIONS:
  §1  Spectral times & von Mangoldt weights
  §2  Heat trace  Θ_H(t) = Σ_n a_n e^{-t τ_n}
  §3  Spectral zeta  ζ_H(s) = Σ_n a_n e^{-s τ_n}

The residual log appears ONLY inside §1 (data ingest).  Once τ_n is
stored, every equation in §2 and §3 is strictly log-free.

================================================================================
"""

import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — SPECTRAL TIMES & VON MANGOLDT WEIGHTS (data ingest — log allowed here)
# ═══════════════════════════════════════════════════════════════════════════════

def _sieve_primes(limit):
    """Eratosthenes sieve returning sorted list of primes ≤ limit."""
    if limit < 2:
        return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for p in range(2, int(limit**0.5) + 1):
        if is_prime[p]:
            for m in range(p * p, limit + 1, p):
                is_prime[m] = False
    return [p for p in range(2, limit + 1) if is_prime[p]]


def spectral_times(n_max):
    r"""
    Compute spectral times τ_n for prime powers n = p^m ≤ n_max.

    Returns arrays (tau, weights, indices) where:
      - tau[k]     = m·ln(p)     (geodesic length / spectral time)
      - weights[k] = ln(p)       (von Mangoldt Λ(n) = ln p for n = p^m)
      - indices[k] = n = p^m     (the integer index)

    The spectral time τ_{p^m} = m·ln(p) = ln(n) is the primitive
    geodesic length times the iterate count.  This ensures that
    e^{-s τ_n} = n^{-s}, recovering the Dirichlet series.

    NOTE: log appears here (data ingest).  Once tau is returned,
    all downstream operations are exponential-only.
    """
    primes = _sieve_primes(n_max)
    taus = []
    weights = []
    indices = []
    for p in primes:
        pm = p
        m = 1
        log_p = np.log(p)
        while pm <= n_max:
            taus.append(m * log_p)     # τ = m·ln(p) = ln(p^m)
            weights.append(log_p)      # Λ(p^m) = ln(p)
            indices.append(pm)
            m += 1
            if pm > n_max // p:  # overflow guard
                break
            pm *= p
    order = np.argsort(indices)
    return (np.array(taus)[order],
            np.array(weights)[order],
            np.array(indices)[order])


def chebyshev_psi_euler(T, n_max=1000):
    r"""
    Chebyshev ψ(e^T) computed in Euler form.

        ψ(e^T) = Σ_{n ≤ e^T} Λ(n) = Σ_{p^m ≤ e^T} ln(p)

    In T-space: sum over prime powers with τ_n = ln(p) ≤ T
    (equivalently p^m ≤ e^T, or m·ln(p) ≤ T).

    Returns ψ(e^T) as a float.
    """
    limit = min(int(np.exp(T)) + 1, n_max)
    tau, wt, idx = spectral_times(limit)
    # Include only terms where n = p^m ≤ e^T
    mask = idx <= np.exp(T)
    return float(np.sum(wt[mask]))


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — HEAT TRACE (Laplace / heat-flow in T-space)
# ═══════════════════════════════════════════════════════════════════════════════

def heat_trace(t, n_max=1000):
    r"""
    Spectral heat trace in Euler form:

        Θ_H(t) = Σ_n Λ(n) · e^{-t τ_n}

    where τ_n = ln(p) for n = p^m.  This is the Laplace transform of the
    von Mangoldt measure evaluated at t.

    In the limit t → 0⁺, Θ_H(t) → ψ(∞).  For t → ∞, Θ_H(t) → 0.
    The heat trace encodes the same information as ζ'/ζ but through
    a strictly exponential kernel.

    Parameters
    ----------
    t : float or array
        Heat parameter (> 0).
    n_max : int
        Upper bound on prime powers to include.

    Returns
    -------
    float or array
        Θ_H(t) value(s).
    """
    tau, wt, _ = spectral_times(n_max)
    t = np.asarray(t, dtype=float)
    if t.ndim == 0:
        return float(np.sum(wt * np.exp(-t * tau)))
    # Vectorized: shape (len(t), len(tau))
    return np.sum(wt[None, :] * np.exp(-t[:, None] * tau[None, :]), axis=1)


def heat_trace_derivative(t, n_max=1000):
    r"""
    Derivative of the heat trace:

        Θ'_H(t) = -Σ_n Λ(n) · τ_n · e^{-t τ_n}

    This is negative for all t > 0 (the heat trace is monotonically
    decreasing), reflecting the spectral gap.
    """
    tau, wt, _ = spectral_times(n_max)
    return float(np.sum(-wt * tau * np.exp(-t * tau)))


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — SPECTRAL ZETA (Dirichlet series in Euler form)
# ═══════════════════════════════════════════════════════════════════════════════

def spectral_zeta(s, n_max=1000):
    r"""
    Spectral zeta function in Euler form:

        ζ_H(s) = Σ_n Λ(n) · e^{-s τ_n} = Σ_n Λ(n) · n^{-s}

    For Re(s) > 1 this converges and equals -ζ'/ζ(s).
    The Euler form makes explicit that ζ_H is a Laplace transform
    in the spectral times τ_n.

    Parameters
    ----------
    s : complex or float
        Complex argument with Re(s) > 1 for convergence.
    n_max : int
        Upper bound on prime powers.

    Returns
    -------
    complex
        ζ_H(s) = -ζ'/ζ(s) (approximately, for finite n_max).
    """
    tau, wt, _ = spectral_times(n_max)
    s = complex(s)
    terms = wt * np.exp(-s * tau)
    return complex(np.sum(terms))


def pnt_residual_euler(T, n_max=None):
    r"""
    PNT residual in Euler form:

        R(T) = ψ(e^T) - e^T

    This is the quantity bounded by the Kadiri-Faber inequality
    (see analytic_bounds.chebyshev_pnt_bound).

    Parameters
    ----------
    T : float
        Exponential height.
    n_max : int or None
        Upper bound on prime powers.  If None, uses e^T + safety margin.

    Returns
    -------
    float
        R(T) = ψ(e^T) - e^T.
    """
    if n_max is None:
        n_max = min(int(np.exp(T)) + 100, 10**7)
    psi_val = chebyshev_psi_euler(T, n_max=n_max)
    return psi_val - np.exp(T)
