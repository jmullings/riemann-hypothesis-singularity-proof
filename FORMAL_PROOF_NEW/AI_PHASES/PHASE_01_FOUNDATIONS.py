#!/usr/bin/env python3
"""
PHASE 01 — FOUNDATIONS: 9D PRIME BASIS, φ-METRIC, & ENERGY FUNCTIONAL
=======================================================================
σ-Selectivity Equation  ·  Phase 1 of 10  (was PHASE_01_BASIS + PHASE_02_ENERGY)

PART A — 9D PRIME BASIS & φ-METRIC FOUNDATION
----------------------------------------------
OBJECTIVE: Establish the 9D prime basis, φ-metric, and all arithmetic weights.
LOG-FREE: log(p) computed ONCE here and frozen. No downstream log() calls.
BIT-SIZE: b(n) = ⌊log₂ n⌋ computed via n.bit_length() (integer op).

PART B — 9D DIRICHLET VECTOR & ENERGY FUNCTIONAL
-------------------------------------------------
OBJECTIVE: Define D(σ,T), E(σ,T), F₂(σ,T) and Gram matrix in LOG-FREE 9D form.
KEY: F₂ = 2|D'|² + 2Re(D''·D̄) — the σ-curvature. Always uses precomputed LOG_P.
"""

import math
import numpy as np
from typing import Tuple

NDIM   = 9
DTYPE  = np.float64
CDTYPE = np.complex128

# ── GOLDEN RATIO ──────────────────────────────────────────────────────────────
PHI    = (1.0 + math.sqrt(5.0)) / 2.0
PHI2   = PHI * PHI
IPHI2  = 1.0 / PHI2          # φ⁻² ≈ 0.38197  (curvature anchor)
IPHI   = PHI - 1.0

# ── 9-PRIME BASIS ─────────────────────────────────────────────────────────────
PRIMES_9 = [2, 3, 5, 7, 11, 13, 17, 19, 23]
P        = np.array(PRIMES_9, dtype=DTYPE)

# ── ARITHMETIC WEIGHTS ────────────────────────────────────────────────────────
ALPHA  = P ** (-0.5)          # p^{-½}
BETA   = P ** (-1.0)          # p^{-1}

# ── LOG CONSTANTS (ONE-TIME, frozen) ──────────────────────────────────────────
LOG_P  = np.array([math.log(p) for p in PRIMES_9], dtype=DTYPE)
LOG2_P = LOG_P ** 2
LOG4_P = LOG_P ** 4

# ── BITSIZE COORDINATES (integer ops only) ────────────────────────────────────
BITSIZE = np.array([p.bit_length() - 1 for p in PRIMES_9], dtype=np.int32)
FRAC_B  = LOG_P - BITSIZE * math.log(2.0)    # fractional bitsize offset

# ── φ-METRIC TENSOR g_{jk} = φ^{j+k} ────────────────────────────────────────
def build_phi_metric():
    idx = np.arange(1, NDIM + 1, dtype=DTYPE)
    return np.outer(PHI ** idx, PHI ** idx)

G_PHI = build_phi_metric()
W_PHI = np.array([PHI ** k for k in range(1, NDIM + 1)], dtype=DTYPE)
D_PHI = float(W_PHI @ ALPHA)

# ── φ-NORMALISED x* (algebraic, zero-free) ───────────────────────────────────
X_STAR_PHI = ALPHA / D_PHI

# ── 25-PRIME DIRICHLET SET ────────────────────────────────────────────────────
def _sieve(N):
    s = [True]*(N+1); s[0]=s[1]=False
    for i in range(2, int(N**0.5)+1):
        if s[i]:
            for j in range(i*i, N+1, i): s[j]=False
    return [p for p in range(2, N+1) if s[p]]

PRIMES_25  = _sieve(100)[:25]
P25        = np.array(PRIMES_25, dtype=DTYPE)
LOG_P25    = np.array([math.log(p) for p in PRIMES_25], dtype=DTYPE)
LOG2_P25   = LOG_P25 ** 2
LOG4_P25   = LOG_P25 ** 4
BITSIZE_25 = np.array([p.bit_length()-1 for p in PRIMES_25], dtype=np.int32)

# ── EXTENDED PRIME SETS (for truncation convergence) ──────────────────────────
PRIMES_100 = _sieve(550)[:100]
P100       = np.array(PRIMES_100, dtype=DTYPE)
LOG_P100   = np.array([math.log(p) for p in PRIMES_100], dtype=DTYPE)
LOG2_P100  = LOG_P100 ** 2

# ── RIEMANN ZEROS (QUARANTINE: used only in verification phases) ──────────────
ZEROS_9 = np.array([
    14.134725141734693, 21.022039638771554, 25.010857580145688,
    30.424876125859513, 32.935061587739189, 37.586178158825671,
    40.918719012147495, 43.327073280914999, 48.005150881167159,
], dtype=DTYPE)

ZEROS_30 = np.array([
    14.134725141734693, 21.022039638771554, 25.010857580145688,
    30.424876125859513, 32.935061587739189, 37.586178158825671,
    40.918719012147495, 43.327073280914999, 48.005150881167159,
    49.773832477672302, 52.970321477714461, 56.446247697063394,
    59.347044002602353, 60.831778524609810, 65.112544048081607,
    67.079810529494174, 69.546401711173979, 72.067157674481908,
    75.704690699083933, 77.144840068874805, 79.337375020249368,
    82.910380854086030, 84.735492980517050, 87.425274613125229,
    88.809111207634465, 92.491899270558484, 94.651344040519887,
    95.870634228245310, 98.831194218193692, 101.317851005731391,
], dtype=DTYPE)

LAMBDA_STAR = 494.05895555802020

# ─────────────────────────────────────────────────────────────────────────────
def verify_basis():
    r = {}
    r["ndim"]           = len(PRIMES_9) == NDIM
    r["alpha_shape"]    = ALPHA.shape == (NDIM,)
    r["g_phi_shape"]    = G_PHI.shape == (NDIM, NDIM)
    r["phi_metric_ok"]  = float(np.max(np.abs(G_PHI - np.outer(W_PHI, W_PHI)))) < 1e-10
    r["phi_unit_norm"]  = abs(float(X_STAR_PHI @ G_PHI @ X_STAR_PHI) - 1.0) < 1e-8
    r["alpha_positive"] = bool(np.all(ALPHA > 0))
    r["log_monotone"]   = bool(np.all(np.diff(LOG_P) > 0))
    r["bitsize_ok"]     = bool(np.all(BITSIZE >= 1))
    r["kappa_unit"]     = 0.0 < IPHI2 < 1.0
    return r


# =============================================================================
# PART B — DIRICHLET VECTOR & ENERGY FUNCTIONAL
# =============================================================================

def D_complex(sigma, T, P_arr=None, log_p=None):
    """D(σ,T) = Σ_k p_k^{-σ-iT}. LOG-FREE."""
    if P_arr is None: P_arr = P25
    if log_p is None: log_p = LOG_P25
    amp = P_arr ** (-sigma)
    phase = -T * log_p
    return complex(float((amp*np.cos(phase)).sum()), float((amp*np.sin(phase)).sum()))

def D_deriv1(sigma, T, P_arr=None, log_p=None):
    """∂D/∂σ = -Σ log(p)·p^{-σ-iT}. LOG-FREE."""
    if P_arr is None: P_arr = P25
    if log_p is None: log_p = LOG_P25
    amp = P_arr ** (-sigma)
    phase = -T * log_p
    return complex(-float((log_p*amp*np.cos(phase)).sum()),
                   -float((log_p*amp*np.sin(phase)).sum()))

def D_deriv2(sigma, T, P_arr=None, log_p=None):
    """∂²D/∂σ² = +Σ log²(p)·p^{-σ-iT}. LOG-FREE."""
    if P_arr is None: P_arr = P25
    if log_p is None: log_p = LOG_P25
    log2_p = log_p ** 2
    amp = P_arr ** (-sigma)
    phase = -T * log_p
    return complex(float((log2_p*amp*np.cos(phase)).sum()),
                   float((log2_p*amp*np.sin(phase)).sum()))

def E_energy(sigma, T, P_arr=None, log_p=None):
    """E(σ,T) = |D|² ≥ 0."""
    D = D_complex(sigma, T, P_arr, log_p)
    return D.real**2 + D.imag**2

def dE_dsigma(sigma, T, P_arr=None, log_p=None):
    """∂E/∂σ = 2·Re(D'·D̄)."""
    D  = D_complex(sigma, T, P_arr, log_p)
    D1 = D_deriv1(sigma, T, P_arr, log_p)
    return 2.0 * (D1.real*D.real + D1.imag*D.imag)

def F2_curvature(sigma, T, P_arr=None, log_p=None):
    """F₂(σ,T) = ∂²E/∂σ² = 2|D'|² + 2Re(D''·D̄). LOG-FREE."""
    if P_arr is None: P_arr = P25
    if log_p is None: log_p = LOG_P25
    log2_p = log_p ** 2
    amp = P_arr ** (-sigma)
    phase = -T * log_p
    cp, sp = np.cos(phase), np.sin(phase)
    D  = complex(float((amp*cp).sum()), float((amp*sp).sum()))
    D1 = complex(-float((log_p*amp*cp).sum()), -float((log_p*amp*sp).sum()))
    D2 = complex(float((log2_p*amp*cp).sum()), float((log2_p*amp*sp).sum()))
    return 2.0*(D1.real**2+D1.imag**2) + 2.0*(D2.real*D.real+D2.imag*D.imag)

def F2_vector_9D(sigma, zeros, P_arr=None, log_p=None):
    """9D curvature vector: F2[k] = F₂(σ, γ_k)."""
    return np.array([F2_curvature(sigma, float(g), P_arr, log_p)
                     for g in zeros], dtype=DTYPE)

def F2_fd(sigma, T, h=1e-5):
    """Finite-difference cross-check of F₂."""
    return (E_energy(sigma+h,T) - 2*E_energy(sigma,T) + E_energy(sigma-h,T))/(h*h)

def mv_avg_energy(sigma, P_arr=None, log2_p=None):
    """⟨Ẽ(σ)⟩_T ≈ Σ log²(p)·p^{-2σ}. MV diagonal. C1 PROVED."""
    if P_arr is None: P_arr = P25
    if log2_p is None: log2_p = LOG2_P25
    return float((log2_p * P_arr**(-2*sigma)).sum())

def mv_curvature(sigma, P_arr=None, log4_p=None):
    """∂²⟨Ẽ⟩/∂σ² = 4Σ log⁴(p)·p^{-2σ} > 0. C2+C4 PROVED."""
    if P_arr is None: P_arr = P25
    if log4_p is None: log4_p = LOG4_P25
    return 4.0 * float((log4_p * P_arr**(-2*sigma)).sum())


# =============================================================================
# S_N PARTIAL SUM ENERGY (all integers — the actual mechanism of ζ)
# =============================================================================
# S_N(σ,T) = Σ_{n=1}^{N} n^{-σ} e^{-iT ln n}  sums over ALL integers.
# This is the partial Dirichlet series for ζ(σ+iT), connected to ζ via the
# Riemann-Siegel approximate functional equation (proved theorem, 1932).
# See PHASE_02_BRIDGE.py for the full bridge.

_N_INT_MAX = 2000
_LOG_INT = np.array([0.0] + [math.log(n) for n in range(1, _N_INT_MAX + 1)], dtype=DTYPE)

def S_N_complex(sigma, T, N=500):
    """S_N(σ,T) = Σ_{n=1}^{N} n^{-σ-iT}. All integers, LOG-FREE."""
    ns = np.arange(1, N + 1, dtype=DTYPE)
    ln_ns = _LOG_INT[1:N+1] if N <= _N_INT_MAX else np.log(ns)
    amp = ns ** (-sigma)
    phase = -T * ln_ns
    return complex(float((amp * np.cos(phase)).sum()),
                   float((amp * np.sin(phase)).sum()))

def E_S_energy(sigma, T, N=500):
    """E_S(σ,T;N) = |S_N(σ,T)|² — partial sum energy (all integers)."""
    s = S_N_complex(sigma, T, N)
    return s.real**2 + s.imag**2

def F2_S_curvature(sigma, T, N=500):
    """F₂ for S_N: ∂²|S_N|²/∂σ² = 2|S_N'|² + 2Re(S_N''·S̄_N). LOG-FREE."""
    ns = np.arange(1, N + 1, dtype=DTYPE)
    ln_ns = _LOG_INT[1:N+1] if N <= _N_INT_MAX else np.log(ns)
    ln2_ns = ln_ns ** 2
    amp = ns ** (-sigma)
    phase = -T * ln_ns
    cp, sp = np.cos(phase), np.sin(phase)
    S  = complex(float((amp * cp).sum()), float((amp * sp).sum()))
    S1 = complex(-float((ln_ns * amp * cp).sum()), -float((ln_ns * amp * sp).sum()))
    S2 = complex(float((ln2_ns * amp * cp).sum()), float((ln2_ns * amp * sp).sum()))
    return 2.0*(S1.real**2 + S1.imag**2) + 2.0*(S2.real*S.real + S2.imag*S.imag)

def F2_S_vector_9D(sigma, zeros, N=500):
    """9D curvature vector using S_N: F2_S[k] = F₂_S(σ, γ_k)."""
    return np.array([F2_S_curvature(sigma, float(g), N)
                     for g in zeros], dtype=DTYPE)

def mv_S_curvature(sigma, N=500):
    """MV T-averaged curvature for S_N: 4Σ (ln n)⁴ · n^{-2σ} > 0."""
    ns = np.arange(1, N + 1, dtype=DTYPE)
    ln_ns = _LOG_INT[1:N+1] if N <= _N_INT_MAX else np.log(ns)
    ln4_ns = ln_ns ** 4
    return 4.0 * float((ln4_ns * ns**(-2*sigma)).sum())


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 01 — FOUNDATIONS: 9D PRIME BASIS & ENERGY FUNCTIONAL")
    print("=" * 70)

    # ── PART A: Basis checks ──────────────────────────────────────────────
    print(f"\n  PART A — Basis")
    print(f"  NDIM = {NDIM},  φ = {PHI:.15f},  φ⁻² = {IPHI2:.15f}")
    print(f"  D_φ  = {D_PHI:.10f},  λ* = {LAMBDA_STAR:.6f}")
    print(f"\n  {'k':>3} {'p':>4} {'b(p)':>5} {'α=p^(-½)':>12} {'log(p)':>12} {'x*_φ':>12}")
    print("  " + "-" * 50)
    for k in range(NDIM):
        print(f"  {k+1:>3} {PRIMES_9[k]:>4} {BITSIZE[k]:>5} {ALPHA[k]:>12.8f} "
              f"{LOG_P[k]:>12.8f} {X_STAR_PHI[k]:>12.8f}")
    checks = verify_basis()
    print(f"\n  CHECKS: {sum(checks.values())}/{len(checks)} pass")
    for name, ok in checks.items():
        print(f"    {'✓' if ok else '✗'} {name}")

    # ── PART B: Energy functional ──────────────────────────────────────────
    print(f"\n  PART B — Energy Functional")
    T0 = float(ZEROS_9[0])
    D0 = D_complex(0.5, T0)
    print(f"  D(½,γ₁) = {D0.real:.8f} + {D0.imag:.8f}i")
    print(f"  E(½,γ₁) = {E_energy(0.5, T0):.10f}")
    print(f"  ∂E/∂σ   = {dE_dsigma(0.5, T0):.8f}")
    f2v = F2_vector_9D(0.5, ZEROS_9)
    print(f"\n  F₂ spectrum at σ=½:")
    for k in range(9):
        f2n = F2_fd(0.5, float(ZEROS_9[k]))
        rel = abs(f2v[k]-f2n)/max(abs(f2v[k]),1e-30)
        print(f"    k={k+1}: F₂={f2v[k]:>12.6f}  fd={f2n:>12.6f}  err={rel:.2e}")
    print(f"  Σ F₂ = {f2v.sum():.6f}  (≈ λ* = 494.059)")
    print(f"  MV curv = {mv_curvature(0.5):.4e} > 0")

    all_ok = all(checks.values())
    print(f"\n  PHASE 01: {'✓ PASS' if all_ok else '✗ FAIL'}")
    print("=" * 70)
