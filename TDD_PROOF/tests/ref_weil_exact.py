#!/usr/bin/env python3
"""
ref_weil_exact.py — Reference oracle for the Weil Explicit Formula.

This module MAY USE log(), mpmath, scipy — it is the trusted ground truth.
Tests compare engine/weil_exact.py (non-log) against this oracle.
"""

import numpy as np
from scipy import integrate

# ─────────────────────────────────────────────────────────────────────────────
# Known Riemann zeros (imaginary parts, first 30)
# ─────────────────────────────────────────────────────────────────────────────

GAMMA_30 = np.array([
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
    79.337375, 82.910381, 84.735493, 87.425275, 88.809111,
    92.491899, 94.651344, 95.870634, 98.831194, 101.317851,
])

# Euler–Mascheroni constant
EULER_MASCHERONI = 0.5772156649015329


def ref_sech2(x):
    """sech²(x) = 1/cosh²(x)."""
    return 1.0 / np.cosh(x) ** 2


def ref_f_test(x, H):
    """f(x) = sech²(log(x)/H) for x > 0."""
    return ref_sech2(np.log(x) / H)


def ref_f_star(x, H):
    """f*(x) = (1/x) f(1/x) = f(x)/x (since sech² is even)."""
    return ref_f_test(x, H) / x


def ref_mellin_f(s, H, limit=100.0, n_points=8000):
    """
    Reference Mellin transform: f̂(s) = ∫₀^∞ f(x) x^{s-1} dx.

    Uses substitution x = e^t, dx = e^t dt:
        f̂(s) = ∫ sech²(t/H) e^{ts} dt
    """
    s = complex(s)
    t_grid = np.linspace(-limit, limit, n_points)
    dt = t_grid[1] - t_grid[0]
    integrand = ref_sech2(t_grid / H) * np.exp(t_grid * s)
    return complex(np.sum(integrand) * dt)


def ref_weil_zero_side(H, zeros=None, **kwargs):
    """
    Reference LHS: f̂(0) + f̂(1) − Σ_ρ [f̂(ρ) + f̂(ρ̄)]
    """
    if zeros is None:
        zeros = GAMMA_30
    val = ref_mellin_f(0, H, **kwargs) + ref_mellin_f(1, H, **kwargs)
    for gamma_k in zeros:
        rho = complex(0.5, gamma_k)
        val -= ref_mellin_f(rho, H, **kwargs)
        val -= ref_mellin_f(rho.conjugate(), H, **kwargs)
    return val


def ref_weil_prime_side(H, primes=None, max_m=4):
    """
    Reference prime sum: Σ_{p,m} (log p / p^{m/2}) [f(p^m) + f*(p^m)]
    """
    if primes is None:
        primes = _small_primes(100)
    total = 0.0
    for p in primes:
        log_p = np.log(float(p))
        for m in range(1, max_m + 1):
            pm = float(p) ** m
            coeff = log_p / (float(p) ** (m / 2.0))
            total += coeff * (ref_f_test(pm, H) + ref_f_star(pm, H))
    return total


def ref_archimedean_term(H, x_min=1e-8, x_max=1e6, n_points=10000):
    """
    Reference archimedean integral:
        I_∞ = ∫₀^∞ [f(x)+f*(x) - 2·x^{-1/2}·f(1)] / [x^{1/2}·(x-1)²] dx

    Regularised by splitting at x=1.
    """
    f_at_1 = ref_f_test(1.0, H)  # = sech²(0) = 1.0

    def integrand(t):
        """Evaluate in t-space: x = e^t, dx = e^t dt."""
        x = np.exp(t)
        if abs(x - 1.0) < 1e-6:
            return 0.0  # regularise at singularity
        num = ref_f_test(x, H) + ref_f_star(x, H) - 2.0 * x ** (-0.5) * f_at_1
        denom = x ** 0.5 * (x - 1.0) ** 2
        return (num / denom) * x  # the extra x from dx = e^t dt

    t_min = np.log(x_min)
    t_max = np.log(x_max)

    # Split around t=0 (x=1) to handle singularity
    eps = 0.01
    result = 0.0

    # Left of singularity
    t_left = np.linspace(t_min, -eps, n_points // 2)
    dt = t_left[1] - t_left[0] if len(t_left) > 1 else 0
    for t in t_left:
        result += integrand(t) * dt

    # Right of singularity
    t_right = np.linspace(eps, t_max, n_points // 2)
    dt = t_right[1] - t_right[0] if len(t_right) > 1 else 0
    for t in t_right:
        result += integrand(t) * dt

    return result


def ref_weil_prime_arch_side(H, primes=None, max_m=4):
    """
    Reference full RHS: S_prime − I_∞ − (log 4π + γ_EM)·f(1)
    """
    S_prime = ref_weil_prime_side(H, primes, max_m)
    I_inf = ref_archimedean_term(H)
    log4pi_gamma = np.log(4.0 * np.pi) + EULER_MASCHERONI
    f_at_1 = ref_f_test(1.0, H)
    return S_prime - I_inf - log4pi_gamma * f_at_1


def ref_weil_equality_check(H, zeros=None, primes=None, max_m=4):
    """
    Reference full equality check: LHS vs RHS.
    """
    LHS = ref_weil_zero_side(H, zeros)
    RHS = ref_weil_prime_arch_side(H, primes, max_m)
    return {
        'LHS': complex(LHS),
        'RHS': float(RHS),
        'residual': abs(LHS - RHS),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def _small_primes(P_max):
    """Primes up to P_max via sieve."""
    if P_max < 2:
        return []
    sieve = [True] * (P_max + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(P_max ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, P_max + 1, i):
                sieve[j] = False
    return [i for i in range(2, P_max + 1) if sieve[i]]


def build_x_grid_and_weights(n_points=3000, t_min=-30.0, t_max=30.0):
    """Build an exponential grid with integration weights."""
    t_grid = np.linspace(t_min, t_max, n_points)
    dt = t_grid[1] - t_grid[0]
    x_grid = np.exp(t_grid)
    return x_grid, dt


def get_reference_zeros(T_max=50.0):
    """Returns known zeros with γ ≤ T_max."""
    return GAMMA_30[GAMMA_30 <= T_max]


def get_reference_primes(P_max=100):
    """Returns primes up to P_max."""
    return _small_primes(P_max)
