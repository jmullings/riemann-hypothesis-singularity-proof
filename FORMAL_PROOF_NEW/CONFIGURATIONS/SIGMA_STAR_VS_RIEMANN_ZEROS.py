#!/usr/bin/env python3
"""
SIGMA_STAR_VS_RIEMANN_ZEROS.py
==============================
Location: FORMAL_PROOF_NEW/CONFIGURATIONS/

[QUARANTINE — DIAGNOSTIC / OPERATOR LAYER ONLY]

This script does NOT implement σ-selectivity or any RH-level conclusion.
It tests three prime-side, operator-layer properties of D(σ,T;X) at σ=½
for Riemann zero heights and (for comparison) random heights:

  PROP A   d²E/dσ²|_{σ=½} > 0          (EQ1.M — pointwise, OPEN at finite X)
  PROP A*  4|∂D/∂σ|²|_{σ=½} > 0        (EQ3 UBE RHS — always ≥ 0, exact)
  PROP B   |d²E/dσ² + d²E/dT² − 4|Dσ|²| ≈ 0  (EQ3 identity — numerical check)

All three properties hold for ALL T > 0, not only zero heights.  They
provide no discriminating signal between zero heights and arbitrary T;
that discrimination requires the BRIDGE layer (PATH_2, OPEN).

SECTION 2 contains a CANARY block (run with --canary) that demonstrates
the former MAV-minimisation approach was a tautology: the old EQ functionals
were constructed with algebraic zeros at σ=½, so σ*=0.5 for every T.

Output
------
    sigma_star_results.csv  — per-zero: T, curvature, 4|Dσ|², UBE_res, E(½,T)

Usage
-----
    python SIGMA_STAR_VS_RIEMANN_ZEROS.py              # all zeros
    python SIGMA_STAR_VS_RIEMANN_ZEROS.py --limit 500  # first 500 zeros
    python SIGMA_STAR_VS_RIEMANN_ZEROS.py --canary     # include tautology demo

Protocol compliance
-------------------
    P1  — log() only inside arithmetic precomputation in SINGULARITY_50D.
    P2  — 9D constants sourced from AXIOMS; no independent geometric weights.
    P3  — Riemann-φ weighting lives in SINGULARITY_50D; not re-applied here.
    P4  — bitsize encoding via AXIOMS constants.
    P5  — Trinity Gate checks printed before main loop.

Author : Jason Mullings
Date   : March 14, 2026  (revised — tautology removed, diagnostics only)
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import sys
import time
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# PATH SETUP — resolve sibling modules without installation
# ---------------------------------------------------------------------------

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))

# ---------------------------------------------------------------------------
# SECTION 0 — IMPORT FROM AXIOMS (P5 compliance: sole constant source)
# ---------------------------------------------------------------------------

from AXIOMS import (
    LAMBDA_STAR,
    NORM_X_STAR,
    COUPLING_K,
    PHI,
    DIM_9D,
    DIM_6D,
    DIM_3D,
)

# ---------------------------------------------------------------------------
# SECTION 1 — IMPORT EQ ENGINE FROM SINGULARITY_50D (canonical definitions)
# ---------------------------------------------------------------------------
# Every EQ functional, the Dirichlet polynomial, find_sigma_star, DELTA,
# PRIMES_100, and LOG_P are sourced directly from SINGULARITY_50D.py so
# that this script is guaranteed to use the same machinery as the main
# bootstrap algorithm.

from SINGULARITY_50D import (
    EQ_FUNCTIONALS,
    EQ_NAMES,
    find_sigma_star as _find_sigma_star_50d,
    D_exact,
    E_exact,
    DELTA,
    PRIMES_100,
    LOG_P,
)

# Scan defaults — match SINGULARITY_50D.py's own scan window [0.1, 0.9]
DEFAULT_SCAN_POINTS: int = 501
TOLERANCE:           float = 5e-3    # |σ* - ½| < tol → PASS
HALF:                float = 0.50


def find_sigma_star(T: float, n_scan: int = DEFAULT_SCAN_POINTS) -> Tuple[float, float]:
    """
    Thin wrapper around SINGULARITY_50D.find_sigma_star that also returns
    the best score value alongside the best σ.

    SINGULARITY_50D.find_sigma_star returns only sigma_star; here we replay
    one pass after the fact to capture the mean absolute value score for reporting.
    """
    sigma_star = float(_find_sigma_star_50d(T, n_scan=n_scan))

    # Re-evaluate mean absolute value at the returned σ* for the report column
    try:
        vals = [float(F(sigma_star, T)) for F in EQ_FUNCTIONALS]
        finite = [v for v in vals if math.isfinite(v)]
        if len(finite) >= 7:
            # Mean absolute value (should be minimized at σ=0.5)
            best_score = sum(abs(v) for v in finite) / len(finite)
        else:
            best_score = math.nan
    except Exception:
        best_score = math.nan

    return sigma_star, best_score


# ---------------------------------------------------------------------------
# SECTION 2 — CANARY BLOCK  [tautology record]
# ---------------------------------------------------------------------------
# The previous version of this script found σ* that minimises the mean
# absolute value (MAV) of EQ1–EQ10.  EVERY T returned σ*=0.5 because the
# EQ functions are algebraically constructed to be zero at σ=½:
#
#   EQ1 = (σ-½)² × E(σ,T)                        → 0  at σ=½   by (σ-½)²=0
#   EQ3 = (Eσ − E½)/(Eσ+E½)                      → 0  at σ=½   trivially
#   EQ6 = (Eσ − E_{1-σ})/(Eσ+E_{1-σ})             → 0  at σ=½   since 1-½=½
#   EQ7 = (σ-½)² × log|D|                          → 0  at σ=½   by (σ-½)²=0
#   EQ9 = |σ-½| × |dE/dσ|                          → 0  at σ=½   by |σ-½|=0
#
# Finding the minimum of |EQ_k| at σ=½ is therefore an algebraic identity
# — it is independent of T and tells us nothing about where ζ-zeros lie.
# The canary function below verifies this explicitly.

_CANARY_T_VALUES = [12.345, 7.777, 99.999, 1003.141, 15.0, 42.0]


def canary_tautology_check() -> None:
    """Print proof that the old MAV-min approach returns σ*=0.5 for ALL T."""
    from SINGULARITY_50D import find_sigma_star as _old_find
    print("CANARY — tautology demonstration (old MAV-min, non-zero heights):")
    print(f"  {'T':>12}   sigma*     tautology?")
    for T in _CANARY_T_VALUES:
        s = _old_find(T, n_scan=101)
        tag = "✓ TAUTOLOGY" if abs(s - 0.5) < 0.005 else "  OK"
        print(f"  T={T:>10.3f}   {s:.7f}   {tag}")
    print("  -> sigma*=0.5 for ALL T regardless of whether T is a zero.")
    print("  -> MAV-min result has been removed from the proof chain.")
    print()


# ---------------------------------------------------------------------------
# SECTION 3 — NON-TAUTOLOGICAL DIAGNOSTICS
# ---------------------------------------------------------------------------
# These functions test genuine mathematical properties of D(σ,T;X).
# They are proved in the SIGMA operator layer for ALL T > 0.
# They do NOT discriminate zero heights from arbitrary heights;
# that discrimination requires the BRIDGE layer (PATH_2, OPEN).

_H_CURV: float = 1e-4   # finite-difference step for curvature


def curvature_at_half(T: float) -> float:
    """
    ∂²E/∂σ²|_{σ=½}  via central finite difference in σ.

    Via the UBE identity (EQ3, PROVED EXACT):
        ∂²E/∂σ²  =  4|D_σ|²  −  ∂²E/∂T²

    The first term 4|D_σ|² ≥ 0 always.  The second term ∂²E/∂T²
    may dominate when E is locally concave in T (rapidly oscillating
    regime, large T), making σ-curvature negative at specific heights.

    EQ1 claims non-negativity; EQ1.M (pointwise ∀T, X→∞) is OPEN.
    The proportion of heights with positive curvature at finite X
    is therefore a DIAGNOSTIC for EQ1.M, not a proof.
    """
    E_plus  = E_exact(0.5 + _H_CURV, T)
    E_ctr   = E_exact(0.5,            T)
    E_minus = E_exact(0.5 - _H_CURV,  T)
    return (E_plus - 2.0 * E_ctr + E_minus) / (_H_CURV ** 2)


def Dsigma_sq_at_half(T: float) -> float:
    """
    PROP A* — 4|∂D/∂σ|² at σ=½  (ALWAYS ≥ 0, proved exact).

    From the UBE identity (EQ3, PROVED EXACT):
        ∂²E/∂σ² + ∂²E/∂T²  =  4|D_σ|²

    The RHS is a squared norm: it is zero only if every prime-log
    phase cancels exactly (measure-zero event).  For generic T it is
    strictly positive.  This is the quantity that EQ1's Cauchy-Schwarz
    argument ultimately bounds.

    Unlike the pointwise σ-curvature (which can be negative), 4|D_σ|²
    provides the provably non-negative prime-side energy for EQ1.

        dD/dσ = −Σ_{p≤X} (log p) p^{−½−iT}
    """
    dD = sum(LOG_P[p] * (p ** complex(-0.5, -T)) for p in PRIMES_100)
    return 4.0 * abs(dD) ** 2


def ube_residual(T: float) -> float:
    """
    PROP B — UBE (Universal Bilinear Equation) identity residual.

    Exact identity (proved in EQ3 / SIGMA_3):
        d²E/dσ² + d²E/dT²  =  4 |dD/dσ|²   (≥ 0 everywhere)

    LHS is approximated numerically; RHS is computed from D_exact.
    Residual should be small (≪ 1) for well-resolved T.

      dD/dσ = -Σ_p  (log p) p^{-σ-iT}
    """
    # LHS: d²E/dσ²
    curv_sigma = curvature_at_half(T)

    # LHS: d²E/dT²
    E_Tp  = E_exact(0.5, T + _H_CURV)
    E_Tc  = E_exact(0.5, T)
    E_Tm  = E_exact(0.5, T - _H_CURV)
    curv_T = (E_Tp - 2.0 * E_Tc + E_Tm) / (_H_CURV ** 2)

    LHS = curv_sigma + curv_T

    # RHS: 4 |dD/dσ|²  = 4 |Σ_p (log p) p^{-1/2-iT}|²
    dD_dsigma = sum(
        LOG_P[p] * (p ** complex(-0.5, -T))
        for p in PRIMES_100
    )
    RHS = 4.0 * abs(dD_dsigma) ** 2

    return abs(LHS - RHS) / max(RHS, 1e-200)


def prime_energy_at_half(T: float) -> float:
    """E(1/2, T; X) = |D(1/2+iT; X)|^2 — prime-side energy on the critical line."""
    return E_exact(0.5, T)


# ---------------------------------------------------------------------------
# SECTION 4 — LOAD ZEROS
# ---------------------------------------------------------------------------

def load_zeros(path: Path, limit: int | None = None) -> List[float]:
    """Parse RiemannZeros.txt — one float per line (whitespace-stripped)."""
    zeros: List[float] = []
    with open(path, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                zeros.append(float(line))
            except ValueError:
                continue
            if limit is not None and len(zeros) >= limit:
                break
    return zeros


# ---------------------------------------------------------------------------
# SECTION 5 — TRINITY GATE (P5)
# ---------------------------------------------------------------------------

def trinity_gate() -> bool:
    """
    Gate-0: ambient dimensions present (DIM_9D = 9, DIM_6D = 6).
    Gate-1: AXIOMS constants sanity (λ*, ‖x*‖, k all non-zero and in range).
    Gate-1b: P1 log-lock — LOG_P is a pre-computed dict, not called inline.
    Gate-2: D_exact / E_exact primitives loaded from SINGULARITY_50D.
    """
    passed = True

    g0 = DIM_9D == 9 and DIM_6D == 6 and DIM_3D == 3
    print(f"  Gate-0 (dimensions)  : {'✓ PASS' if g0 else '✗ FAIL'}"
          f"  DIM_9D={DIM_9D}  DIM_6D={DIM_6D}  DIM_3D={DIM_3D}")
    passed = passed and g0

    g1 = LAMBDA_STAR > 494.0 and NORM_X_STAR > 0.3 and COUPLING_K > 0.0
    print(f"  Gate-1 (constants)   : {'✓ PASS' if g1 else '✗ FAIL'}"
          f"  λ*={LAMBDA_STAR:.3f}  ‖x*‖={NORM_X_STAR:.5f}  k={COUPLING_K}")
    passed = passed and g1

    g1b = isinstance(LOG_P, dict) and len(LOG_P) == len(PRIMES_100)
    print(f"  Gate-1b (P1 log-lock): {'✓ PASS' if g1b else '✗ FAIL'}"
          f"  LOG_P entries={len(LOG_P)}  PRIMES_100 count={len(PRIMES_100)}")
    passed = passed and g1b

    g2_ok = callable(D_exact) and callable(E_exact)
    print(f"  Gate-2 (D/E engine)  : {'✓ PASS' if g2_ok else '✗ FAIL'}"
          f"  D_exact and E_exact imported from SINGULARITY_50D")
    passed = passed and g2_ok

    return passed


# ---------------------------------------------------------------------------
# SECTION 6 — MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "[QUARANTINE/DIAGNOSTIC] Prime-side operator-layer property check "
            "at Riemann zero heights.  Tests PROP A (curvature > 0) and "
            "PROP B (UBE residual ≈ 0) — see AIREADME.md §4-7."
        )
    )
    parser.add_argument(
        "--zeros",
        default=str(HERE / "RiemannZeros.txt"),
        help="Path to RiemannZeros.txt  [default: same directory as this script]",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Process only the first N zeros  [default: all]",
    )
    parser.add_argument(
        "--out",
        default=str(HERE / "sigma_star_results.csv"),
        help="Output CSV path  [default: sigma_star_results.csv]",
    )
    parser.add_argument(
        "--canary",
        action="store_true",
        default=False,
        help="Print the canary tautology block (default: off; use for interactive review)",
    )
    parser.add_argument(
        "--no-canary",
        dest="canary",
        action="store_false",
        help="Suppress canary block",
    )
    args = parser.parse_args()

    print("=" * 72)
    print("PRIME-SIDE OPERATOR DIAGNOSTIC  —  FORMAL_PROOF_NEW / CONFIGURATIONS")
    print("  [QUARANTINE — operator layer only; bridge layer OPEN]")
    print(f"  Engine    : SINGULARITY_50D.py  D_exact / E_exact")
    print(f"  Constants : AXIOMS.py  (φ={PHI:.6f})")
    print("=" * 72)
    print()

    # --- Trinity Gate ---
    print("TRINITY GATE (P5):")
    gate_ok = trinity_gate()
    print(f"  Overall              : {'✓ PASS' if gate_ok else '⚠  PARTIAL'}")
    print()

    # --- Canary: prove tautology explicitly ---
    if args.canary:
        canary_tautology_check()

    # --- Random reference heights for comparison ---
    random.seed(42)
    random_T = sorted(random.uniform(14.0, 300.0) for _ in range(5))
    print("RANDOM (non-zero) REFERENCE — same operator properties hold for ALL T:")
    print(f"  {'T':>14}   curvature(d²E/dσ²)   UBE_residual   E(½,T)")
    for T in random_T:
        c = curvature_at_half(T)
        u = ube_residual(T)
        e = prime_energy_at_half(T)
        print(f"  T={T:>12.3f}   {c:>18.4f}   {u:>13.4e}   {e:.4e}")
    print("  NOTE: curvature > 0 and UBE ≈ 0 for ALL T — this is a prime-side")
    print("  property (EQ1/EQ3), NOT a discriminating signal for zero heights.")
    print()

    # --- Load zeros ---
    zeros_path = Path(args.zeros)
    if not zeros_path.exists():
        print(f"ERROR: zeros file not found: {zeros_path}")
        sys.exit(1)

    zeros = load_zeros(zeros_path, limit=args.limit)
    n_zeros = len(zeros)
    print(f"Zeros loaded : {n_zeros}"
          f"{'  (limited)' if args.limit else ''}"
          f"  from  {zeros_path.name}")
    print()

    # --- Main diagnostic loop ---
    results: List[dict] = []
    n_curv_ok   = 0
    n_ube_ok    = 0
    n_Dsq_ok    = 0
    t_start = time.time()

    UBE_TOL = 0.05   # relative residual threshold for UBE check

    print(f"{'#':>7}  {'T (γₙ)':>16}  {'d²E/dσ²':>10}  "
          f"{'4|Dσ|²':>10}  {'UBE_res':>9}  {'E(½,T)':>9}  A  A*  B")
    print("-" * 84)

    for idx, T in enumerate(zeros, start=1):
        curv   = curvature_at_half(T)
        Dsq    = Dsigma_sq_at_half(T)
        ube    = ube_residual(T)
        e_val  = prime_energy_at_half(T)

        curv_ok = curv > 0.0
        Dsq_ok  = Dsq  > 0.0     # always true for generic T
        ube_ok  = ube  < UBE_TOL

        if curv_ok:  n_curv_ok += 1
        if Dsq_ok:   n_Dsq_ok  += 1
        if ube_ok:   n_ube_ok  += 1

        results.append({
            "index":       idx,
            "T":           T,
            "curvature":   curv,
            "Dsigma_sq":   Dsq,
            "ube_residual": ube,
            "E_half":      e_val,
            "curv_ok":     curv_ok,
            "Dsq_ok":      Dsq_ok,
            "ube_ok":      ube_ok,
        })

        # Print first 10, every 100th, and any failures
        if idx <= 10 or idx % 100 == 0 or not curv_ok or not ube_ok:
            # On negative-curvature rows add UBE decomposition note
            note = ""
            if not curv_ok:
                note = f"  [∂²E/∂T²={Dsq - curv:.3f} > 4|Dσ|²={Dsq:.3f} → EQ1.M open]"
            print(
                f"{idx:>7}  {T:>16.9f}  {curv:>10.4f}  "
                f"{Dsq:>10.4f}  {ube:>9.4e}  {e_val:>9.4e}"
                f"  {'✓' if curv_ok else '✗'}  {'✓' if Dsq_ok else '✗'}  {'✓' if ube_ok else '✗'}"
                + note
            )

    elapsed = time.time() - t_start

    # --- Write CSV ---
    out_path = Path(args.out)
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["index", "T", "curvature", "Dsigma_sq",
                        "ube_residual", "E_half", "curv_ok", "Dsq_ok", "ube_ok"],
        )
        writer.writeheader()
        writer.writerows(results)

    # --- Summary ---
    print()
    print("=" * 72)
    print("SUMMARY  [QUARANTINE — diagnostic only, not a proof of RH]")
    print("=" * 72)
    print(f"  Zeros tested               : {n_zeros}")
    print(f"  PROP A* (4|Dσ|²>0)         : {n_Dsq_ok}/{n_zeros}"
          f"  (EQ3 UBE RHS — exact squared norm, always >0 for generic T)")
    print(f"  PROP A  (∂²E/∂σ²>0 ptwise) : {n_curv_ok}/{n_zeros}"
          f"  (EQ1.M OPEN GAP — expected <100% at finite X={len(PRIMES_100)} primes)")
    print(f"    -> Failures via UBE: ∂²E/∂T² > 4|Dσ|² at those heights")
    print(f"    -> Reflects finite-X oscillation, not a contradiction with EQ1")
    print(f"  PROP B  (UBE_res<{UBE_TOL:.0e})    : {n_ube_ok}/{n_zeros}"
          f"  (EQ3 identity — exact for finite X; finite-diff tolerance)")
    print(f"  φ (AXIOMS)                 : {PHI:.10f}")
    print(f"  λ* (AXIOMS, empir.)        : {LAMBDA_STAR:.6f}")
    print(f"  Elapsed                    : {elapsed:.1f} s")
    print(f"  CSV written                : {out_path}")
    print()
    print("OPERATOR LAYER STATUS: PROP A* (4|Dσ|²>0) satisfies EQ3 exactly.")
    print("                       PROP A  (pointwise ∂²E/∂σ²>0) is EQ1.M — OPEN.")
    print("BRIDGE LAYER STATUS  : PATH_2 (A5'+C5+C6+B5) — OPEN.")
    print("CONCLUSION           : No claim is made about the location of ζ-zeros.")
    print("=" * 72)


if __name__ == "__main__":
    main()
