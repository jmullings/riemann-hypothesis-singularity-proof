#!/usr/bin/env python3
"""
================================================================================
ube_decomposition.py — Analytic Decomposition of the UBE Convexity Inequality
================================================================================

MATHEMATICAL FRAMEWORK (Lemma 6.2):

    F_k(T) = e^T · M_k
             − Σ_ρ (e^{ρT} / |ρ|) · Ĝ_k(ρ)
             + Err_k(T)

    C_φ(T; h) = Δ_h² F_k(T)    (projected and summed over k)

where:
    • e^T · M_k  is the PNT (Prime Number Theorem) main term
    • Σ_ρ ...    is the zero sum (truncated to known zeros)
    • Err_k(T)   is the numerical residual

This module exposes the analytic decomposition so that TDD tests can:
  (a) Measure the error term |Err_k(T)| relative to the main term
  (b) Track scaling of θ(T) = |Err_k(T)| / (e^T M_k · 2(cosh h − 1))
  (c) Guard the Lemma 6.2 OPEN/CLOSED status

The inequality C_φ(T;h) ≥ 0 (UBE convexity) is EMPIRICALLY observed.
The analytic bound on Err_k(T) that would PROVE it remains OPEN.

INTEGRATION:
    Built from BRIDGE_05_UBE.py primitives (FORMAL_PROOF_NEW/BRIDGES/BRIDGE_5).
    Uses the same sieve and φ-canonical architecture.
    NO zeros enter the F_k computation; zeros enter ONLY the zero_sum_k
    comparison term.

LOG-FREE: Uses precomputed log table (same as BRIDGE_05_UBE).
================================================================================
"""

import numpy as np
from .weil_density import GAMMA_30


# ═══════════════════════════════════════════════════════════════════════════════
# STATUS CONSTANTS — epistemic honest markers
# ═══════════════════════════════════════════════════════════════════════════════

LEMMA_6_2_STATUS = "OPEN"
"""The analytic bound on Err_k(T) that would PROVE C_φ(T;h) ≥ 0 remains
OPEN.  The UBE convexity is observed empirically but not proven.

CRITIQUE RESPONSE (External Review, Critique #5):
An external review noted this status.  The critic is CORRECT: Lemma 6.2
IS genuinely open.  This is by design — the UBE pathway is an INDEPENDENT
DIAGNOSTIC CHANNEL, not part of the main contradiction chain (Lemmas 1-3).
The main proof chain (proof_chain.contradiction_chain) does NOT depend on
UBE or Lemma 6.2.  Its chain_complete flag evaluates Lemmas 1-3 and
Barriers 1-3 only.  The UBE provides prime-side cross-validation."""

UBE_CONVEXITY_STATUS = "EMPIRICAL"

UBE_CLASSIFICATION = "ARITHMETIC EXPERIMENT — NOT A PROOF"

# ═══════════════════════════════════════════════════════════════════════════════
# §1 — UBE PRIMITIVES (self-contained, from BRIDGE_05_UBE.py)
# ═══════════════════════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2
N_MAX = 3000
NUM_BRANCHES = 9
PROJECTION_DIM = 6

# Precomputed log table (LOG-FREE protocol)
_LOG_TABLE = np.zeros(N_MAX + 1)
for _n in range(2, N_MAX + 1):
    _LOG_TABLE[_n] = float(np.log(_n))

# φ-canonical weights and geodesic lengths (Law D)
PHI_WEIGHTS = np.array([PHI ** (-k) for k in range(NUM_BRANCHES)], dtype=float)
PHI_WEIGHTS /= PHI_WEIGHTS.sum()
GEODESIC_LENGTHS = np.array([PHI ** k for k in range(NUM_BRANCHES)], dtype=float)


def sieve_mangoldt(N):
    """Λ(n) = log(p) if n = p^k, else 0."""
    lam = np.zeros(N + 1)
    sieve = np.ones(N + 1, dtype=bool)
    sieve[0] = sieve[1] = False
    for p in range(2, N + 1):
        if not sieve[p]:
            continue
        for m in range(p * p, N + 1, p):
            sieve[m] = False
        log_p = _LOG_TABLE[min(p, N_MAX)]
        pk = p
        while pk <= N:
            lam[pk] = log_p
            pk *= p
    return lam


def T_phi_9D(T, lam):
    """9D Eulerian state vector T_φ(T) = (F_0(T), ..., F_8(T))."""
    N = min(int(np.exp(T)) + 1, len(lam) - 1)
    if N < 2:
        return np.zeros(NUM_BRANCHES)
    n_range = np.arange(2, N + 1)
    log_n = _LOG_TABLE[np.clip(n_range, 0, N_MAX)]
    lambdas = lam[2:N + 1]
    vec = np.zeros(NUM_BRANCHES)
    for k in range(NUM_BRANCHES):
        L_k = GEODESIC_LENGTHS[k]
        w_k = PHI_WEIGHTS[k]
        z = (log_n - T) / L_k
        gauss = np.exp(-0.5 * z * z) / (L_k * np.sqrt(2 * np.pi))
        vec[k] = w_k * float(np.dot(gauss, lambdas))
    return vec


def build_P6():
    """Static 6×9 projection matrix P₆ (Law D × Law E collapse)."""
    P6 = np.zeros((PROJECTION_DIM, NUM_BRANCHES), dtype=float)
    for i in range(PROJECTION_DIM):
        P6[i, i] = 1.0
    return P6


# Module-level sieve and projection (computed once)
_LAM = sieve_mangoldt(N_MAX)
_P6 = build_P6()


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — ANALYTIC DECOMPOSITION
# ═══════════════════════════════════════════════════════════════════════════════

def Fk_prime_side(T, lam=None, P6=None):
    """
    F_k(T) computed entirely from primes (Phase 1 — ZKZ compliant).

    Returns the 6D projected norm ||P_6 · T_φ(T)||.
    This is the prime-side observable; NO zero data used.
    """
    if lam is None:
        lam = _LAM
    if P6 is None:
        P6 = _P6
    return float(np.linalg.norm(P6 @ T_phi_9D(T, lam)))


def main_PNT_k(T):
    """
    Main PNT term: e^T · M_k  (the leading-order contribution).

    For the φ-Gaussian kernel, M_k is the projected norm of the
    PNT weight vector.  At leading order, ψ(e^T) ~ e^T, so the
    T_φ state vector receives weight ~ e^T from the Chebyshev ψ function.

    The M_k coefficients are the static φ-weights projected through P₆.
    """
    M_k = float(np.linalg.norm(_P6 @ PHI_WEIGHTS))
    return np.exp(T) * M_k


def zero_sum_k(T, zeros=None, k_max=None):
    """
    Zero sum: Σ_ρ (e^{ρT} / |ρ|) · Ĝ_k(ρ)  (truncated).

    Uses the known Riemann zeros as input — called ONLY for
    decomposition comparison, NOT in Phase 1 computation.

    The kernel Ĝ_k(ρ) for the φ-Gaussian is approximated as:
        Ĝ_k(ρ) ≈ Σ_j w_j · exp(−L_j² · Im(ρ)² / 2) / L_j

    Each zero ρ = 1/2 + iγ contributes an oscillatory + decaying term.
    """
    if zeros is None:
        zeros = GAMMA_30
    if k_max is not None:
        zeros = zeros[:k_max]

    total = 0.0
    for gamma in zeros:
        rho_abs = np.sqrt(0.25 + gamma * gamma)
        exp_factor = np.exp(0.5 * T)  # e^{Re(ρ)·T} = e^{T/2}

        # Kernel hat function: sum over φ-branches
        G_hat = 0.0
        for j in range(PROJECTION_DIM):
            L_j = GEODESIC_LENGTHS[j]
            w_j = PHI_WEIGHTS[j]
            G_hat += w_j * np.exp(-0.5 * L_j**2 * gamma**2) / L_j

        # Oscillatory contribution: cos(γT) (real part of e^{iγT})
        osc = np.cos(gamma * T)
        total += (exp_factor / rho_abs) * G_hat * osc

    return total


def err_hat_k(T, Fk_val=None, main_val=None, zero_val=None):
    """
    Numerical residual: Err_k(T) = F_k(T) − (main_PNT_k(T) − zero_sum_k(T)).

    This is the gap that Lemma 6.2 needs to bound:
        |Err_k(T)| ≤ θ(T) · e^T · M_k · 2(cosh h − 1)
    with θ(T) → 0 as T → ∞.

    STATUS: θ(T) observed numerically; analytic bound OPEN.
    """
    if Fk_val is None:
        Fk_val = Fk_prime_side(T)
    if main_val is None:
        main_val = main_PNT_k(T)
    if zero_val is None:
        zero_val = zero_sum_k(T)

    return Fk_val - (main_val - zero_val)


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — CONVEXITY DECOMPOSITION
# ═══════════════════════════════════════════════════════════════════════════════

def C_phi_prime(T, h, lam=None, P6=None):
    """
    C_φ(T; h) = N_φ(T+h) + N_φ(T-h) − 2 N_φ(T).

    Convexity functional computed entirely from primes.
    Should be ≥ 0 everywhere (the UBE inequality).
    """
    Np = Fk_prime_side(T + h, lam, P6)
    Nm = Fk_prime_side(T - h, lam, P6)
    N0 = Fk_prime_side(T, lam, P6)
    return Np + Nm - 2 * N0


def C_phi_PNT(T, h):
    """
    PNT main-term contribution to convexity:
        Δ_h²(e^T · M_k) = e^T · M_k · 2(cosh h − 1)

    This is always > 0, providing the positive baseline.
    """
    M_k = float(np.linalg.norm(_P6 @ PHI_WEIGHTS))
    return np.exp(T) * M_k * 2.0 * (np.cosh(h) - 1.0)


def C_phi_zero_sum(T, h, zeros=None):
    """
    Zero-sum contribution to convexity:
        Δ_h²(zero_sum_k(T)) = zero_sum_k(T+h) + zero_sum_k(T-h) − 2·zero_sum_k(T)
    """
    return (zero_sum_k(T + h, zeros) + zero_sum_k(T - h, zeros)
            - 2 * zero_sum_k(T, zeros))


def C_phi_error(T, h, lam=None, P6=None, zeros=None):
    """
    Error contribution to convexity:
        Δ_h²(Err_k(T)) = C_φ(T;h) − C_φ_PNT(T;h) + C_φ_zero(T;h)
    """
    c_prime = C_phi_prime(T, h, lam, P6)
    c_pnt = C_phi_PNT(T, h)
    c_zero = C_phi_zero_sum(T, h, zeros)
    return c_prime - c_pnt + c_zero


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — SCALING DIAGNOSTIC: θ(T) = |Err_k(T)| / main_PNT
# ═══════════════════════════════════════════════════════════════════════════════

def theta_scaling(T_values, h=0.02):
    """
    Compute θ(T) = |Err_k(T)| / (e^T · M_k · 2(cosh h − 1)) for each T.

    Lemma 6.2 requires θ(T) → 0 as T → ∞.
    This function measures the empirical scaling.

    Returns dict with:
        T_values, theta_values, all_finite, max_theta, trend
    """
    theta_vals = np.zeros(len(T_values))

    for i, T in enumerate(T_values):
        Fk = Fk_prime_side(T)
        main_val = main_PNT_k(T)
        zero_val = zero_sum_k(T)
        err = err_hat_k(T, Fk, main_val, zero_val)

        pnt_conv = main_val * 2.0 * (np.cosh(h) - 1.0)
        if pnt_conv > 0:
            theta_vals[i] = abs(err) / pnt_conv
        else:
            theta_vals[i] = np.inf

    # Trend: fit log(θ) vs T to estimate decay rate
    finite_mask = np.isfinite(theta_vals) & (theta_vals > 0)
    if np.sum(finite_mask) >= 3:
        T_fit = T_values[finite_mask]
        log_theta = np.log(theta_vals[finite_mask])
        coeffs = np.polyfit(T_fit, log_theta, 1)
        trend_slope = float(coeffs[0])
    else:
        trend_slope = np.nan

    return {
        "T_values": T_values,
        "theta_values": theta_vals,
        "all_finite": bool(np.all(np.isfinite(theta_vals))),
        "max_theta": float(np.max(theta_vals[np.isfinite(theta_vals)]))
                     if np.any(np.isfinite(theta_vals)) else np.inf,
        "trend_slope": trend_slope,
        "trend_decreasing": trend_slope < 0 if np.isfinite(trend_slope) else False,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — FULL DECOMPOSITION REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def full_decomposition(T, h=0.02):
    """
    Full analytic decomposition at a single point T.

    Returns dict with all terms and diagnostics.
    """
    Fk = Fk_prime_side(T)
    main_val = main_PNT_k(T)
    zero_val = zero_sum_k(T)
    err = err_hat_k(T, Fk, main_val, zero_val)

    c_prime = C_phi_prime(T, h)
    c_pnt = C_phi_PNT(T, h)
    c_zero = C_phi_zero_sum(T, h)
    c_err = C_phi_error(T, h)

    pnt_conv = main_val * 2.0 * (np.cosh(h) - 1.0)
    theta = abs(err) / pnt_conv if pnt_conv > 0 else np.inf

    return {
        "T": T,
        "h": h,
        "Fk_prime_side": Fk,
        "main_PNT_k": main_val,
        "zero_sum_k": zero_val,
        "err_hat_k": err,
        "theta": theta,
        "C_phi_prime": c_prime,
        "C_phi_PNT": c_pnt,
        "C_phi_zero_sum": c_zero,
        "C_phi_error": c_err,
        "convexity_holds": c_prime >= -1e-10,
        "lemma_6_2_status": LEMMA_6_2_STATUS,
    }
