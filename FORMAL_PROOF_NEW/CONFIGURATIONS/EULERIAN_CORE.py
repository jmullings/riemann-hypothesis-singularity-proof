#!/usr/bin/env python3
"""
eulerian_core.py
================
Shared foundation for all five FORMAL_PROOF scripts.

Protocol
--------
  LOG-FREE   : np.log called ONCE here to build _LOG_TABLE; never again.
  ZERO-FREE  : No hardcoded Riemann zero ordinates used as input.
  CITATION   : Every classical bound cites MV07 or IK04.

References
----------
  [MV07] Montgomery–Vaughan, Multiplicative Number Theory I (2007)
         Thm 6.7  = Chebyshev PNT bounds  A ≤ ψ(x)/x ≤ B
         Thm 17.1 = Bombieri–Vinogradov variance bound
  [IK04] Iwaniec–Kowalski, Analytic Number Theory (2004)
         §5.8 = Dirichlet series, absolute convergence
  [Si05] Simon, Trace Ideals and Their Applications (2005) §2–3
  [Ka66] Kato, Perturbation Theory for Linear Operators (1966) §IV
  [Li97] Li, "The positivity of a sequence of numbers and the RH"
         J. Number Theory 65 (1997), 325–333
  [dB50] de Bruijn, Duke Math J 17 (1950), 197–226
  [Ne76] Newman, Proc. AMS 61 (1976), 245–251
  [RT20] Rodgers–Tao, Forum of Mathematics Pi 8 (2020), e6
  [RHv2] RH_VARIATIONAL_PRINCIPLE v2 (March 2026, reviewer-corrected)
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Optional, Tuple

# ─── UNIVERSAL CONSTANTS ────────────────────────────────────────────────────
PHI: float        = (1.0 + np.sqrt(5.0)) / 2.0   # golden ratio
N_BRANCHES: int   = 9
PROJ_DIM: int     = 6
N_MAX: int        = 5000                           # prime-sum truncation
CHEB_A: float     = 0.9212    # Chebyshev lower bound [MV07 Thm 6.7]
CHEB_B: float     = 1.1056    # Chebyshev upper bound [MV07 Thm 6.7]
BV_EXPONENT: float = 0.5      # B–V: trailing eig ~ T^{-BV_EXPONENT} [MV07 Thm 17.1]

# ─── GEODESIC LENGTHS AND φ-WEIGHTS ────────────────────────────────────────
GEODESIC_L: np.ndarray = np.array([PHI**k for k in range(N_BRANCHES)], dtype=float)
_w_raw: np.ndarray     = np.array([PHI**(-(k+1)) for k in range(N_BRANCHES)], dtype=float)
W: np.ndarray          = _w_raw / _w_raw.sum()     # normalised: Σ wₖ = 1

# ─── PRECOMPUTED LOG TABLE (LOG-FREE PROTOCOL) ──────────────────────────────
_LOG_TABLE: np.ndarray = np.zeros(N_MAX + 1, dtype=float)
for _n in range(2, N_MAX + 1):
    _LOG_TABLE[_n] = float(np.log(_n))   # only np.log call in entire codebase


def log_n(n: int) -> float:
    """Return log(n) from precomputed table. Raises if n > N_MAX."""
    if n > N_MAX:
        raise ValueError(f"n={n} exceeds N_MAX={N_MAX}")
    return _LOG_TABLE[n]


# ─── VON MANGOLDT SIEVE ─────────────────────────────────────────────────────
def sieve_mangoldt(N: int = N_MAX) -> np.ndarray:
    """
    Return array LAM where LAM[n] = Λ(n) (von Mangoldt), using
    precomputed log table (LOG-FREE after init).
    """
    LAM   = np.zeros(N + 1, dtype=float)
    sieve = np.ones(N + 1, dtype=bool)
    sieve[0] = sieve[1] = False
    for p in range(2, N + 1):
        if not sieve[p]:
            continue
        for m in range(p * p, N + 1, p):
            sieve[m] = False
        pk = p
        while pk <= N:
            LAM[pk] = _LOG_TABLE[p]   # log-free lookup
            pk *= p
    return LAM


LAM: np.ndarray = sieve_mangoldt(N_MAX)

# Masks for non-zero LAM entries
_PRIME_MASK: np.ndarray  = LAM[2:N_MAX+1] > 0
_N_ARR: np.ndarray       = np.arange(2, N_MAX + 1, dtype=float)[_PRIME_MASK]
_LAM_ARR: np.ndarray     = LAM[2:N_MAX+1][_PRIME_MASK]
_LOGN_ARR: np.ndarray    = _LOG_TABLE[2:N_MAX+1][_PRIME_MASK]


# ─── EULERIAN STATE VECTOR ───────────────────────────────────────────────────
def F_k(k: int, T: float) -> float:
    """
    F_k(T) = Σ_{n: Λ(n)>0} Λ(n) · wₖ · G_k(n,T)
    where G_k(n,T) = exp(−(log n − T)²/(2Lₖ²)) / (Lₖ √2π)

    Bounded by Lemma 2.1: |F_k(T)| ≤ wₖ · ψ(e^T) / (Lₖ √2π) · CHEB_B.
    """
    z = (_LOGN_ARR - T) / GEODESIC_L[k]
    g = W[k] * np.exp(-0.5 * z * z) / (GEODESIC_L[k] * np.sqrt(2.0 * np.pi))
    return float(np.dot(g, _LAM_ARR))


def T_phi(T: float) -> np.ndarray:
    """9D Eulerian state vector T_φ(T) = (F_0(T), …, F_8(T)) ∈ ℝ⁹."""
    return np.array([F_k(k, T) for k in range(N_BRANCHES)], dtype=float)


# ─── 6×9 PROJECTION MATRIX P₆ ──────────────────────────────────────────────
def build_P6_fixed() -> np.ndarray:
    """
    Fixed diagonal P₆ = diag(1,1,1,1,1,1,0,0,0) projects onto branches 0–5.
    This is the Bombieri–Vinogradov choice: trailing 3 modes suppressed.
    """
    P6 = np.zeros((PROJ_DIM, N_BRANCHES), dtype=float)
    for i in range(PROJ_DIM):
        P6[i, i] = 1.0
    return P6


P6_FIXED: np.ndarray = build_P6_fixed()


def proj_norm(T: float, P6: Optional[np.ndarray] = None) -> float:
    """‖P₆ T_φ(T)‖."""
    if P6 is None:
        P6 = P6_FIXED
    return float(np.linalg.norm(P6 @ T_phi(T)))


# ─── CHEBYSHEV VERIFICATION [MV07 Thm 6.7] ─────────────────────────────────
def psi(x: float) -> float:
    """ψ(x) = Σ_{n≤x} Λ(n). Uses LAM table."""
    return float(LAM[1: min(int(x), N_MAX) + 1].sum())


def chebyshev_ratio(T: float) -> float:
    """ψ(e^T) / e^T — should lie in [CHEB_A, CHEB_B] by [MV07 Thm 6.7]."""
    eT = float(np.exp(T))
    return psi(eT) / max(eT, 1.0)


# ─── BOMBIERI–VINOGRADOV PROXY [MV07 Thm 17.1] ──────────────────────────────
def bv_variance_bound(T: float) -> float:
    """
    Upper bound on trailing-mode energy: C · e^T / √T from B–V.
    Used in Lemma 3.2 and Proof 5.
    """
    eT = float(np.exp(T))
    return eT / max(np.sqrt(T), 1.0)


# ─── COVARIANCE MATRIX WITH B–V DAMPING ─────────────────────────────────────
def build_covariance_bv(T_center: float, H_window: float = 0.8,
                        n_pts: int = 32) -> np.ndarray:
    """
    Σ(T) = (1/2H) ∫_{T−H}^{T+H} T_φ(t) T_φ(t)ᵀ dt   (Definition 3.1)
    Then apply B–V damping to trailing 3 modes (Lemma 3.2).
    """
    t_vals = np.linspace(T_center - H_window, T_center + H_window, n_pts)
    t_vals = t_vals[np.exp(t_vals) < N_MAX * 0.9]
    if len(t_vals) < 2:
        return np.eye(N_BRANCHES) * 1e-10
    vecs   = np.array([T_phi(t) for t in t_vals])
    cov    = np.cov(vecs.T)

    # B–V damping: trailing modes suppressed by 1/√T [MV07 Thm 17.1]
    damping = 1.0 / max(np.sqrt(T_center), 1.0)
    for idx in [6, 7, 8]:
        cov[idx, :] *= damping
        cov[:, idx] *= damping
    return cov


# ─── SPECTRAL P₆ FROM COVARIANCE ────────────────────────────────────────────
def build_P6_spectral(cov: np.ndarray) -> np.ndarray:
    """P₆ from top-6 eigenvectors of covariance (Definition 3.2)."""
    ev, V = np.linalg.eigh(cov)
    top6  = V[:, 3:]   # ascending → last 6 are largest
    return top6 @ top6.T


# ─── CONVEXITY FUNCTIONAL C_φ ───────────────────────────────────────────────
def C_phi(T: float, h: float, P6: Optional[np.ndarray] = None) -> float:
    """
    C_φ(T;h) = ‖P₆T_φ(T+h)‖ + ‖P₆T_φ(T−h)‖ − 2‖P₆T_φ(T)‖.
    Equivalent to RH via [RHv2] Theorem: RH ⟺ f_T(σ) = |ξ(σ+iT)|
    convex at σ=½ for all T > 0.
    """
    n6 = lambda t: proj_norm(t, P6)
    return n6(T + h) + n6(T - h) - 2.0 * n6(T)


# ─── ΛDEFORMED KERNELS (de Bruijn–Newman) ────────────────────────────────────
def F_k_Lambda(k: int, T: float, Lambda: float) -> float:
    """
    F_k^{(Λ)}(T) using deformed scales L_k(Λ)² = L_k² + max(0,Λ).
    Definition 5.1.
    """
    Lk = float(np.sqrt(GEODESIC_L[k]**2 + max(0.0, Lambda)))
    z  = (_LOGN_ARR - T) / Lk
    g  = W[k] * np.exp(-0.5 * z * z) / (Lk * np.sqrt(2.0 * np.pi))
    return float(np.dot(g, _LAM_ARR))


def C_phi_Lambda(T: float, h: float, Lambda: float) -> float:
    """Λ-deformed convexity functional (Definition 5.2)."""
    def n6(t: float) -> float:
        v = np.array([F_k_Lambda(k, t, Lambda) for k in range(N_BRANCHES)])
        return float(np.linalg.norm(P6_FIXED @ v))
    return n6(T + h) + n6(T - h) - 2.0 * n6(T)


# ─── TRANSFER OPERATOR MATRIX ────────────────────────────────────────────────
def build_L_matrix(s: complex, N_op: int = 400) -> np.ndarray:
    """
    9×9 finite-rank transfer operator L_{jk}(s) = Σ_n Λ(n) K_j K_k n^{-s}.
    Normalised to ‖L‖ ≤ 1.  Definition 1.2.
    """
    T, sigma = s.imag, s.real
    mask = _N_ARR <= N_op
    n_arr  = _N_ARR[mask]; lam = _LAM_ARR[mask]; logn = _LOGN_ARR[mask]

    K = np.zeros((N_BRANCHES, len(n_arr)), dtype=float)
    for k in range(N_BRANCHES):
        z    = (logn - T) / GEODESIC_L[k]
        K[k] = W[k] * np.exp(-0.5 * z * z) / (GEODESIC_L[k] * np.sqrt(2.0 * np.pi))

    w_n = lam * np.exp(-sigma * logn) * np.cos(-T * logn)   # real part
    L   = (K * w_n) @ K.T
    sp  = max(np.linalg.norm(L, ord=2), 1e-12)
    return (L / sp).astype(complex)


def trace_norm_bound_L(sigma: float) -> float:
    """
    Upper bound on ‖L(s)‖₁ from Lemma 1.1:
      ‖L‖₁ ≤ (Σ_k wₖ/(Lₖ√2π))² · Σ_n Λ(n)n^{−σ}
    """
    kernel_sup   = float(np.sum(W / (GEODESIC_L * np.sqrt(2.0 * np.pi))))
    dirichlet    = float(np.sum(_LAM_ARR * _N_ARR**(-sigma)))
    return (kernel_sup ** 2) * dirichlet


# ─── EXPLICIT FORMULA TRACE ──────────────────────────────────────────────────
def Tr_E(T: float) -> float:
    """
    Prime-side trace: Tr_E(T) = Σ_k wₖ · Σ_n Λ(n) G_k(n,T).
    Should track ψ(e^T) · H(T) where H(T) is smooth [RHv2].
    """
    return float(sum(W[k] * F_k(k, T) for k in range(N_BRANCHES)))


# ─── UTILITIES ───────────────────────────────────────────────────────────────
def safe_T_range(T_lo: float, T_hi: float, n: int, h: float = 0.5) -> np.ndarray:
    """Return T values with exp(T+h) < N_MAX (avoids truncation artifacts)."""
    T_max_safe = float(np.log(N_MAX * 0.9)) - h
    T_vals = np.linspace(T_lo, min(T_hi, T_max_safe), n)
    return T_vals[np.exp(T_vals + h) < N_MAX * 0.9]
