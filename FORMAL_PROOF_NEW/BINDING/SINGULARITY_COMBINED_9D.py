#!/usr/bin/env python3
"""
SINGULARITY_COMBINED_9D.py
==========================
Non-Tautological Combined 9D Singularity Coordinate for the Riemann Zeta Function
Date   : March 13, 2026
Version: 2.0.0  (self-contained, algebraic combination, no sigma-search)

MATHEMATICAL FRAMEWORK
----------------------
Two structurally independent probes are combined by a fixed algebraic rule
to produce a 9D coordinate x_comb in R^9.

PROBE 1 -- sigma-Curvature Eigenvector  (prime Dirichlet polynomial)
  D_X(sigma,T) = sum_{p<=X} p^{-sigma-iT}           (X = 100)
  E_X(sigma,T) = |D_X(sigma,T)|^2

  F2_k = d^2 E_X/dsigma^2  at (sigma=1/2, T=gamma_k)   (analytic, no search)
       = 2|dD/dsigma|^2 + 2 Re(d^2D/dsigma^2 * conj(D))  at sigma=1/2

  Weights w_p = log^2(p) are precomputed prime constants (P1-compliant).

PROBE 2 -- PSS+SECH^2 Geometric Curvature  (integer partial-sum chain)
  S_N(gamma_k) = sum_{n<=N} n^{-1/2} e^{-i gamma_k log n}
  kappa_N      = unsigned turning angle at step N
  C_k          = sum_N sech^2(alpha*(log N - mu)) * kappa_N

  Uses ALL positive integers 1..N_MAX, not just primes.

COMBINATION  (fixed coefficients A=B=1, no iteration, no sigma-search)
  F2_norm_k = F2_k / max_j(F2_j)
  C_norm_k  = C_k  / max_j(C_j)
  S_k       = A * F2_norm_k + B * C_norm_k
  x_comb_k  = S_k / sum_j(S_j)

NON-CIRCULARITY GUARANTEES
  * sigma = 1/2 is a fixed input -- never searched over.
  * gamma_k used only as sample heights; no zetafunction property assumed.
  * A = B = 1 fixed; no data-driven tuning.
  * EQ10 (Euler-product log) excluded entirely.
  * No bootstrap, no iterative consensus.
"""

from __future__ import annotations

import csv
import math
import sys
import time
from pathlib import Path
from typing import List, Tuple

# -- High-precision arithmetic ------------------------------------------------
try:
    import mpmath
    from mpmath import mp, mpf, mpc, nstr
    mp.dps = 60
    MPMATH_OK = True
except ImportError:
    MPMATH_OK = False
    mpf = float
    mpc = complex
    nstr = str
    print("WARNING: mpmath not available. Install: pip install mpmath")
    print("Falling back to float64.\n")


# =============================================================================
# SECTION 0 -- CONSTANTS AND INPUT DATA
# =============================================================================

_ZEROS_STR = [
    "14.134725141734693790457251983562470270784257323570722301738673",
    "21.022039638771554992628479593896902777334340524902781754629520",
    "25.010857580145688763213790992562821818659549672557996672496424",
    "30.424876125859513210311897530584091320181560023715440180962146",
    "32.935061587739189690662368964074903488812715603517039009280003",
    "37.586178158825671257217763480705332821405597350830793218333001",
    "40.918719012147495187398126914633254395726165962777279536161303",
    "43.327073280914999519496122165406805782645668371836871446099198",
    "48.005150881167159727942472749427516765271532563522936790595236",
]

if MPMATH_OK:
    ZEROS_9 = [mpf(z) for z in _ZEROS_STR]
    SIGMA_HALF = mpf("0.5")
else:
    ZEROS_9 = [float(z) for z in _ZEROS_STR]
    SIGMA_HALF = 0.5


# =============================================================================
# SECTION 1 -- PROBE 1: sigma-CURVATURE EIGENVECTOR
# =============================================================================
# Locked at sigma = 1/2. No scanning. Analytic formula only.

def _sieve(N: int) -> List[int]:
    """Sieve of Eratosthenes."""
    if N < 2:
        return []
    sieve = bytearray([1]) * (N + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(N ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
    return [i for i in range(2, N + 1) if sieve[i]]


PRIMES_X = _sieve(100)   # 25 primes <= 100

# Prime log constants (fixed arithmetic constants, P1-compliant)
if MPMATH_OK:
    _LP  = {p: mpmath.log(mpf(p))      for p in PRIMES_X}
    _LP2 = {p: mpmath.log(mpf(p)) ** 2 for p in PRIMES_X}
else:
    _LP  = {p: math.log(p)   for p in PRIMES_X}
    _LP2 = {p: math.log(p) ** 2 for p in PRIMES_X}


def _D(sigma, T):
    """D_X(sigma,T) = sum_{p<=100} p^{-sigma-iT}."""
    if MPMATH_OK:
        s = mpc(sigma, T)
        return sum(mpmath.power(p, -s) for p in PRIMES_X)
    s = complex(sigma, T)
    return sum(p ** (-s) for p in PRIMES_X)


def _D1(sigma, T):
    """dD/dsigma = -sum_p log(p)*p^{-sigma-iT}."""
    if MPMATH_OK:
        s = mpc(sigma, T)
        return -sum(_LP[p] * mpmath.power(p, -s) for p in PRIMES_X)
    s = complex(sigma, T)
    return -sum(_LP[p] * p ** (-s) for p in PRIMES_X)


def _D2(sigma, T):
    """d^2 D/dsigma^2 = sum_p log^2(p)*p^{-sigma-iT}."""
    if MPMATH_OK:
        s = mpc(sigma, T)
        return sum(_LP2[p] * mpmath.power(p, -s) for p in PRIMES_X)
    s = complex(sigma, T)
    return sum(_LP2[p] * p ** (-s) for p in PRIMES_X)


def probe1_F2(gamma_k):
    """
    F2_k = d^2 E_X/dsigma^2 at (sigma=1/2, T=gamma_k).

    Formula: 2|D'|^2 + 2 Re(D'' * conj(D))  where ' denotes d/dsigma.
    sigma is locked at 1/2; no scanning performed.
    """
    d  = _D(SIGMA_HALF, gamma_k)
    d1 = _D1(SIGMA_HALF, gamma_k)
    d2 = _D2(SIGMA_HALF, gamma_k)
    term1 = 2 * (d1.real ** 2 + d1.imag ** 2)
    term2 = 2 * (d2.real * d.real + d2.imag * d.imag)
    return term1 + term2


def compute_probe1(zeros: list) -> List:
    """Return raw F2_k for all 9 zeros. sigma = 1/2 throughout."""
    results = []
    print("Probe 1 -- sigma-Curvature of Prime Dirichlet Energy at sigma=1/2")
    print(f"         D_X with X=100 ({len(PRIMES_X)} primes), sigma fixed at 1/2")
    print()
    for k, gamma in enumerate(zeros, start=1):
        f2 = probe1_F2(gamma)
        results.append(f2)
        gstr = nstr(gamma, 20) if MPMATH_OK else f"{float(gamma):.15f}"
        f2str = nstr(f2, 25) if MPMATH_OK else f"{float(f2):.10e}"
        print(f"  [{k}/9]  gamma_{k} = {gstr}")
        print(f"         F2_k     = {f2str}")
    print()
    return results


# =============================================================================
# SECTION 2 -- PROBE 2: PSS + SECH^2 GEOMETRIC CURVATURE
# =============================================================================

N_MAX_PSS = 500       # PSS truncation
ALPHA_PSS = mpf("0.8") if MPMATH_OK else 0.8
_LOG1     = mpf("0.0") if MPMATH_OK else 0.0
_LOG_NMAX = (mpmath.log(mpf(N_MAX_PSS)) if MPMATH_OK
             else math.log(N_MAX_PSS))
MU_PSS    = (_LOG1 + _LOG_NMAX) / 2

# Precomputed tables for speed
if MPMATH_OK:
    _LOG_N = [mpmath.log(mpf(n)) for n in range(1, N_MAX_PSS + 1)]
    _AMP_N = [mpf(1) / mpmath.sqrt(mpf(n)) for n in range(1, N_MAX_PSS + 1)]
else:
    _LOG_N = [math.log(n) for n in range(1, N_MAX_PSS + 1)]
    _AMP_N = [1.0 / math.sqrt(n) for n in range(1, N_MAX_PSS + 1)]


def _sech2(x):
    if MPMATH_OK:
        c = mpmath.cosh(x)
        return mpf(1) / (c * c)
    c = math.cosh(float(x))
    return 1.0 / (c * c)


def _pss_trajectory(gamma) -> List:
    """
    PSS trajectory S_N(gamma) for N=1..N_MAX_PSS.

        S_N = sum_{n=1}^{N} n^{-1/2} * exp(-i*gamma*log(n))

    Returns list of running complex sums.
    """
    S = mpc(0, 0) if MPMATH_OK else complex(0, 0)
    traj = []
    for n_idx in range(N_MAX_PSS):
        amp   = _AMP_N[n_idx]
        phase = -gamma * _LOG_N[n_idx]
        if MPMATH_OK:
            term = amp * mpmath.expj(phase)
        else:
            term = amp * complex(math.cos(float(phase)), math.sin(float(phase)))
        S += term
        traj.append(S)
    return traj


def _curvature_weighted(traj: List):
    """
    SECH^2-weighted total turning angle.

        C = sum_{N=2}^{N_MAX-1}  sech^2(alpha*(log N - mu)) * kappa_N

    kappa_N = unsigned angle between step vectors at index N.
    """
    ZERO   = mpf("0.0") if MPMATH_OK else 0.0
    TWO_PI = 2 * mpmath.pi if MPMATH_OK else 2.0 * math.pi
    PI     = mpmath.pi     if MPMATH_OK else math.pi

    C = ZERO
    for idx in range(1, N_MAX_PSS - 1):
        v1 = traj[idx]     - traj[idx - 1]
        v2 = traj[idx + 1] - traj[idx]

        if MPMATH_OK:
            if abs(v1) == 0 or abs(v2) == 0:
                continue
            ang1 = mpmath.atan2(v1.imag, v1.real)
            ang2 = mpmath.atan2(v2.imag, v2.real)
        else:
            if abs(v1) < 1e-300 or abs(v2) < 1e-300:
                continue
            ang1 = math.atan2(v1.imag, v1.real)
            ang2 = math.atan2(v2.imag, v2.real)

        d_theta = abs(ang2 - ang1)
        if d_theta > PI:
            d_theta = TWO_PI - d_theta

        logN = _LOG_N[idx]
        w    = _sech2(ALPHA_PSS * (logN - MU_PSS))
        C   += w * d_theta

    return C


def compute_probe2(zeros: list) -> List:
    """Return raw C_k (PSS+SECH^2 curvature scores) for all 9 zeros."""
    results = []
    print("Probe 2 -- PSS+SECH^2 Geometric Curvature (integer partial sums)")
    print(f"         N_MAX={N_MAX_PSS},  alpha={float(ALPHA_PSS):.2f},  "
          f"mu={float(MU_PSS):.4f}")
    print()
    for k, gamma in enumerate(zeros, start=1):
        traj = _pss_trajectory(gamma)
        C_k  = _curvature_weighted(traj)
        results.append(C_k)
        gstr = nstr(gamma, 20) if MPMATH_OK else f"{float(gamma):.15f}"
        cstr = nstr(C_k, 25)   if MPMATH_OK else f"{float(C_k):.10e}"
        print(f"  [{k}/9]  gamma_{k} = {gstr}")
        print(f"         C_k      = {cstr}")
    print()
    return results


# =============================================================================
# SECTION 3 -- ALGEBRAIC COMBINATION
# =============================================================================

def combine(F2_raw: List, C_raw: List,
            A=None, B=None) -> Tuple[List, List, List]:
    """
    Combine Probe 1 and Probe 2 into the combined 9D coordinate.

    S_k = A * (F2_k/max(F2)) + B * (C_k/max(C))
    x_comb_k = S_k / sum_j(S_j)

    Returns (x_curv, x_pss, x_comb) each normalised to sum=1.
    """
    if MPMATH_OK:
        A_val = mpf("1.0") if A is None else mpf(A)
        B_val = mpf("1.0") if B is None else mpf(B)
    else:
        A_val = 1.0 if A is None else float(A)
        B_val = 1.0 if B is None else float(B)

    sum_F2 = sum(F2_raw)
    sum_C  = sum(C_raw)
    x_curv = [f / sum_F2 for f in F2_raw]
    x_pss  = [c / sum_C  for c in C_raw]

    max_F2 = max(F2_raw)
    max_C  = max(C_raw)

    S_vals = [A_val * (f2 / max_F2) + B_val * (c / max_C)
              for f2, c in zip(F2_raw, C_raw)]
    total_S = sum(S_vals)
    x_comb  = [s / total_S for s in S_vals]

    return x_curv, x_pss, x_comb


# =============================================================================
# SECTION 4 -- DIAGNOSTICS
# =============================================================================

def _pearson_correlation(xs: List, ys: List):
    n  = len(xs)
    if MPMATH_OK:
        xm = sum(xs) / mpf(n)
        ym = sum(ys) / mpf(n)
    else:
        xm = sum(xs) / n
        ym = sum(ys) / n
    num   = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
    var_x = sum((x - xm) ** 2 for x in xs)
    var_y = sum((y - ym) ** 2 for y in ys)
    denom = (mpmath.sqrt(var_x * var_y) if MPMATH_OK
             else math.sqrt(float(var_x) * float(var_y)))
    if denom == 0:
        return mpf("0") if MPMATH_OK else 0.0
    return num / denom


def print_comparison_table(zeros, F2_raw, C_raw,
                            x_curv, x_pss, x_comb) -> None:
    max_F2 = max(F2_raw)
    max_C  = max(C_raw)
    print("  " + "-" * 88)
    print(f"  {'k':>2}  {'gamma_k':>20}  {'F2_norm':>10}  {'C_norm':>10}  "
          f"{'x*(curv)':>12}  {'x*(pss)':>12}  {'x*(comb)':>12}")
    print("  " + "-" * 88)
    for k, row in enumerate(
            zip(zeros, F2_raw, C_raw, x_curv, x_pss, x_comb), start=1):
        gamma, f2, c, xcu, xps, xcb = row
        print(f"  {k:>2}  {float(gamma):>20.10f}  "
              f"{float(f2/max_F2):>10.6f}  {float(c/max_C):>10.6f}  "
              f"{float(xcu):>12.8f}  {float(xps):>12.8f}  {float(xcb):>12.8f}")
    print("  " + "-" * 88)
    corr = _pearson_correlation(x_curv, x_pss)
    print(f"\n  Pearson corr(x_curv, x_pss) = {float(corr):+.6f}")
    print("  (near 0 confirms structural independence of the two probes)")


def export_csv(zeros, F2_raw, C_raw, x_curv, x_pss, x_comb,
               path: Path) -> None:
    max_F2 = max(F2_raw)
    max_C  = max(C_raw)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "k", "gamma_k",
            "F2_raw", "C_raw",
            "F2_norm", "C_norm",
            "x_curv", "x_pss", "x_combined",
        ])
        for k, row in enumerate(
                zip(zeros, F2_raw, C_raw, x_curv, x_pss, x_comb), start=1):
            gamma, f2, c, xcu, xps, xcb = row
            def _s(v, digits=35):
                return nstr(v, digits) if MPMATH_OK else float(v)
            writer.writerow([
                k,
                _s(gamma, 55), _s(f2, 35), _s(c, 35),
                _s(f2 / max_F2, 35), _s(c / max_C, 35),
                _s(xcu, 55), _s(xps, 55), _s(xcb, 55),
            ])
    print(f"  CSV written -> {path}")


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    t_start = time.time()

    print("=" * 78)
    print("NON-TAUTOLOGICAL COMBINED 9D SINGULARITY COORDINATE")
    print("Probe 1 : sigma-Curvature Eigenvector (prime Dirichlet polynomial)")
    print("Probe 2 : PSS+SECH^2 Geometric Curvature (integer partial-sum chain)")
    print("Method  : S_k = A*F2_norm + B*C_norm,  A=B=1,  sigma=1/2 fixed")
    print("=" * 78)
    print()
    prec_str = f"mpmath  mp.dps={mp.dps}" if MPMATH_OK else "float64"
    print(f"Precision : {prec_str}")
    print(f"Primes    : {len(PRIMES_X)} primes <= 100  (Probe 1)")
    print(f"PSS N_MAX : {N_MAX_PSS}  (Probe 2)")
    print(f"Zeros     : 9 non-trivial Riemann zero heights gamma_1...gamma_9")
    print()

    # -- Probe 1 ---------------------------------------------------------------
    F2_raw = compute_probe1(ZEROS_9)

    # -- Probe 2 ---------------------------------------------------------------
    C_raw  = compute_probe2(ZEROS_9)

    # -- Combine ---------------------------------------------------------------
    x_curv, x_pss, x_comb = combine(F2_raw, C_raw)

    # -- Summary ---------------------------------------------------------------
    print("=" * 78)
    print("COMBINED 9D SINGULARITY COORDINATE  x*(comb)  (50 decimal places)")
    print("=" * 78)
    print()
    print("  Definition:")
    print("    S_k       = F2_k/max(F2) + C_k/max(C)        (A=B=1)")
    print("    x*(comb)  = S_k / sum_j(S_j)")
    print()

    if MPMATH_OK:
        norm_l1 = sum(x_comb)
        norm_l2 = mpmath.sqrt(sum(xk * xk for xk in x_comb))
    else:
        norm_l1 = sum(x_comb)
        norm_l2 = math.sqrt(sum(float(xk) ** 2 for xk in x_comb))

    for k, xk in enumerate(x_comb, start=1):
        val = nstr(xk, 52) if MPMATH_OK else f"{float(xk):.15e}"
        print(f"  x*(comb)_{k} = {val}")

    print()
    l1v = nstr(norm_l1, 52) if MPMATH_OK else f"{float(norm_l1):.15e}"
    l2v = nstr(norm_l2, 52) if MPMATH_OK else f"{float(norm_l2):.15e}"
    print(f"  ||x*(comb)||_1 = {l1v}")
    print(f"  ||x*(comb)||_2 = {l2v}")
    print()

    # -- Individual coordinates ------------------------------------------------
    print("-" * 78)
    print("INDIVIDUAL PROBE COORDINATES")
    print()
    print("  x*(curv)  [Probe 1 only -- sigma-curvature eigenvector]:")
    for k, xk in enumerate(x_curv, start=1):
        val = nstr(xk, 35) if MPMATH_OK else f"{float(xk):.15e}"
        print(f"    x*(curv)_{k} = {val}")

    print()
    print("  x*(pss)   [Probe 2 only -- PSS+SECH^2 geometric curvature]:")
    for k, xk in enumerate(x_pss, start=1):
        val = nstr(xk, 35) if MPMATH_OK else f"{float(xk):.15e}"
        print(f"    x*(pss)_{k}  = {val}")
    print()

    # -- Comparison table ------------------------------------------------------
    print("COMPARISON TABLE")
    print()
    print_comparison_table(ZEROS_9, F2_raw, C_raw, x_curv, x_pss, x_comb)
    print()

    # -- CSV export ------------------------------------------------------------
    here     = Path(__file__).resolve().parent
    csv_path = here / "singularity_combined_9d.csv"
    export_csv(ZEROS_9, F2_raw, C_raw, x_curv, x_pss, x_comb, csv_path)

    elapsed = time.time() - t_start
    print(f"\n  Completed in {elapsed:.1f} s")
    print()
    print("EPISTEMIC NOTE")
    print("  These coordinates are a well-defined algebraic construction from")
    print("  two independent finite computations.  They are NOT a proof of RH.")
    print("  Probe 1 (primes, spectral) and Probe 2 (integers, geometric) are")
    print("  structurally independent; their relationship to zeta zeros requires")
    print("  further rigorous analysis.")


if __name__ == "__main__":
    main()
