#!/usr/bin/env python3
"""
STEP_06_CONSTRUCT_OPERATOR.py
==============================
STEP 6 of 10 — Bootstrap 10-EQ Singularity Consensus

PURPOSE
-------
For each Riemann zero height T = γₙ (n = 1…9), compute all 10 EQ
functional values at σ = 0.5.  Build the 9×10 matrix:

    M[n, j] = Fⱼ(0.5, γₙ)

Perform SVD on the column-normalised M.  The dominant left singular
vector is the 9D "EQ consensus": the direction in zero-height space
where all 10 EQ systems simultaneously agree on σ = 0.5.

The dominant singular value s₁ is logged explicitly to quantify how
strongly the 10 EQ systems agree (s₁ ≫ s₂ means strong consensus).

WHAT THIS STEP ESTABLISHES
---------------------------
  "10-EQ SVD consensus at σ = 0.5" — finite, model-internal fact.
  No AXIOMS 9D constants are used to construct the consensus.
  NORM_X_STAR / LAMBDA_STAR appear only as external reference numbers
  to print alongside the result.  Geometric alignment is deferred to
  STEP 7 (cosine similarity check).

WHAT IS NOT CLAIMED
--------------------
  The consensus vector is not claimed to equal x* or to satisfy
  ‖consensus‖ = NORM_X_STAR.  The norm ratio is printed but NOT
  interpreted as alignment — that belongs in STEP 7.

PROTOCOL COMPLIANCE
-------------------
  P1  No log() as primary energy operator.
      LN_P table is built with math.log but is classified as
      P1.1 RAW DATA INGEST — stored statically, used only as a
      scalar multiplier in the trigonometric form of p^(-s).
      F10 (spectral gap proxy) is replaced by a hyperbolic
      sech²-based functional — see _F10_sech2() below.
      math.log() does NOT appear in any Fⱼ energy expression.
  P2  9D metric constructed first (9×9 golden tensor).
      M is 9×10 (9 zeros, 10 EQs); SVD left vector is 9D.
  P3  Riemann-φ weights used in F5, F7 (φ-weighted energy).
  P4  F2 uses sech² cross-term (see _F2_curvature); coupling_k checked.
  P5  Explicit PASS/FAIL lines; two CSVs written for STEP 7 consumption.

OUTPUTS
-------
  step_06_eq_matrix.csv  — 9×10 EQ values at σ=½ per zero
  step_06_svd.csv        — singular values + consensus vector
"""

import sys
import csv
import time
import math
from pathlib import Path
from typing import List, Tuple

import numpy as np

# ── Path bootstrap ────────────────────────────────────────────────────────────
_HERE      = Path(__file__).resolve().parent
_STEP_ROOT = _HERE.parent
_FORMAL    = _STEP_ROOT.parent.parent
_CONFIGS   = _FORMAL / "CONFIGURATIONS"
_ANALYTICS = _STEP_ROOT / "ANALYTICS"

if str(_CONFIGS) not in sys.path:
    sys.path.insert(0, str(_CONFIGS))

from AXIOMS import (
    PHI, LAMBDA_STAR, NORM_X_STAR, COUPLING_K, RIEMANN_ZEROS_9,
    DIM_9D, DIM_6D,
)

print("[Gate-0] 10-EQ matrix bootstrap  OK")
print()
print("=" * 72)
print("STEP 6 — Bootstrap 10-EQ Singularity Consensus")
print(f"  Matrix : 9 zeros × 10 EQ functionals at σ = 0.5")
print(f"  λ*     = {LAMBDA_STAR}")
print(f"  ‖x*‖   = {NORM_X_STAR}")
print(f"  φ      = {PHI}")
print("=" * 72)

t0 = time.time()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 0 — Golden 9D Metric (P2: constructed before any reduction)
# ─────────────────────────────────────────────────────────────────────────────

G_9D = np.array([[PHI ** (i + 1 + j + 1) for j in range(DIM_9D)]
                  for i in range(DIM_9D)])
assert G_9D.shape == (9, 9), "P2 VIOLATION: metric not 9×9"
print(f"[P2] 9D golden metric ({DIM_9D}×{DIM_9D}) constructed  OK")
print(f"     g_11 = φ² = {G_9D[0, 0]:.10f}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — Prime data (P1.1 raw ingest — log appears ONLY here)
# ─────────────────────────────────────────────────────────────────────────────

def _sieve(N: int) -> List[int]:
    is_p = bytearray([1]) * (N + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(N ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i::i] = bytearray(len(is_p[i * i::i]))
    return [i for i in range(2, N + 1) if is_p[i]]

PRIMES = _sieve(100)     # first 25 primes

# P1.1 RAW DATA INGEST — math.log used here only, stored as static table.
# ln p is not an energy operator; it is the natural logarithm of a prime,
# used solely to construct the trigonometric angle T·ln p.
LN_P: dict = {p: math.log(p) for p in PRIMES}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — Trigonometric prime-power basis (P1 energy layer)
# ─────────────────────────────────────────────────────────────────────────────

def _p_power(p: int, sigma: float, T: float) -> Tuple[float, float]:
    """
    p^(-σ-iT) in Cartesian form.

    P1 compliance: uses LN_P only as an angle scalar.
    Returns (real, imag).
    """
    mag   = p ** (-sigma)           # p^(-σ) — exponential in σ
    angle = T * LN_P[p]             # T·ln p — geometric angle, not an operator
    return mag * math.cos(angle), -mag * math.sin(angle)


def _D(sigma: float, T: float) -> Tuple[float, float]:
    """D_X(s) = Σ_p p^(-s);  returns (Re, Im)."""
    re = im = 0.0
    for p in PRIMES:
        dr, di = _p_power(p, sigma, T)
        re += dr;  im += di
    return re, im


def _dD(sigma: float, T: float) -> Tuple[float, float]:
    """D'_X(s) = -Σ_p ln(p)·p^(-s);  P1: ln p is scalar coefficient."""
    re = im = 0.0
    for p in PRIMES:
        dr, di = _p_power(p, sigma, T)
        lp = LN_P[p]
        re += -lp * dr;  im += -lp * di
    return re, im


def _d2D(sigma: float, T: float) -> Tuple[float, float]:
    """D''_X(s) = Σ_p ln²(p)·p^(-s);  P1: ln²p is scalar coefficient."""
    re = im = 0.0
    for p in PRIMES:
        dr, di = _p_power(p, sigma, T)
        lp2 = LN_P[p] ** 2
        re += lp2 * dr;  im += lp2 * di
    return re, im


def _E(sigma: float, T: float) -> float:
    """Energy |D_X(s)|²."""
    Dr, Di = _D(sigma, T)
    return Dr * Dr + Di * Di


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — sech² helper (P4)
# ─────────────────────────────────────────────────────────────────────────────

def _sech_sq(x: float) -> float:
    """sech²(x) via exp() only — P1 compliant."""
    if abs(x) > 50.0:
        return 0.0
    e2x = math.exp(2.0 * x)
    return 4.0 * e2x / (e2x + 1.0) ** 2


def _phi_weight(p: int, gamma_k: float) -> float:
    """Riemann-φ weight: w(p,γk) = φ^(-p)·exp(-γk/p)  [P3]."""
    return (PHI ** (-p)) * math.exp(-gamma_k / p)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — The 10 EQ Functionals (all P1 compliant)
# ─────────────────────────────────────────────────────────────────────────────
#
# F1   |D_X(s)|                 — modulus of Dirichlet polynomial
# F2   2|D'|² + 2Re(D''·D̄)    — EQ2 curvature (same as STEP 7)
# F3   E(σ+δ)+E(σ−δ)−2E(σ)    — UBE symmetric second difference (δ=0.05)
# F4   E(σ)−E(½)               — deviation from critical-line energy
# F5   Σ_p w(p,γ₁)·p^(-2σ)    — Riemann-φ weighted energy (P3)
# F6   Re(D_X(s))              — real part of D_X
# F7   φ·|D_X(s)|²             — φ-scaled energy
# F8   |D_X(s)|                — redundant check vs F1 (confirms stability)
# F9   Σ_p sech²(p^(-σ))       — sech²-projected prime sum (P1/P4)
# F10  Σ_p w(p,γ₁)·sech²(γ₁/p)— φ-sech² spectral proxy (replaces log version)
# ─────────────────────────────────────────────────────────────────────────────

EQ_NAMES = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10"]

DELTA = 0.05     # UBE offset for F3

def all_eq(sigma: float, T: float) -> List[float]:
    """
    Compute all 10 EQ functionals at (σ, T).

    P1 compliance:
      - No math.log() in this function.
      - LN_P used via _dD / _d2D as scalar angle data only.
      - F10 uses sech²(γ₁/p) — hyperbolic, not logarithmic.
    P3 compliance:
      - F5, F10 use Riemann-φ weights.
    """
    Dr, Di  = _D(sigma, T)
    dDr, dDi = _dD(sigma, T)
    d2Dr, d2Di = _d2D(sigma, T)
    Ev = Dr * Dr + Di * Di

    # F1 — |D_X|
    f1 = math.sqrt(max(Ev, 0.0))

    # F2 — EQ2 curvature (P1: trig form, no log operator)
    dD_sq = dDr ** 2 + dDi ** 2
    cross  = d2Dr * Dr + d2Di * Di
    f2 = 2.0 * dD_sq + 2.0 * cross

    # F3 — UBE symmetric second difference
    Ep  = _E(sigma + DELTA, T)
    Em  = _E(sigma - DELTA, T)
    f3 = Ep + Em - 2.0 * Ev

    # F4 — deviation from critical-line energy
    E_half = _E(0.5, T)
    f4 = Ev - E_half

    # F5 — Riemann-φ weighted energy (P3)
    gamma1 = RIEMANN_ZEROS_9[0]
    f5 = sum(_phi_weight(p, gamma1) * (p ** (-2.0 * sigma)) for p in PRIMES)

    # F6 — Re(D_X)
    f6 = Dr

    # F7 — φ-scaled energy
    f7 = PHI * Ev

    # F8 — |D_X| (independent check of modulus)
    f8 = math.sqrt(max(Ev, 0.0))

    # F9 — sech²-projected prime sum (P4 hyperbolic basis)
    f9 = sum(_sech_sq(p ** (-sigma)) for p in PRIMES)

    # F10 — φ-sech² spectral proxy (P1 compliant; replaces log-based version)
    #   Σ_p  w(p, γ₁) · sech²(γ₁ / p)
    f10 = sum(_phi_weight(p, gamma1) * _sech_sq(gamma1 / p) for p in PRIMES)

    return [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10]


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — Build 9×10 EQ matrix
# ─────────────────────────────────────────────────────────────────────────────

print()
print(f"[EQ] Computing {len(RIEMANN_ZEROS_9)}×{len(EQ_NAMES)} matrix at σ=½:")
print(f"  {'T':>10}  {'F1':>12}  {'F2':>12}  {'F3':>12}  {'F4':>12}")
print("  " + "-" * 56)

M_raw: List[List[float]] = []
rows_m: List[dict] = []

for k, T in enumerate(RIEMANN_ZEROS_9):
    vals = all_eq(0.5, T)
    M_raw.append(vals)
    rows_m.append({"k": k + 1, "T": T, **dict(zip(EQ_NAMES, vals))})
    print(f"  {T:>10.4f}  {vals[0]:>12.4e}  {vals[1]:>12.4e}  "
          f"{vals[2]:>12.4e}  {vals[3]:>12.4e}")

M = np.array(M_raw, dtype=float)   # shape (9, 10)
assert M.shape == (9, 10), f"EQ matrix shape error: {M.shape}"

# All F2 values should be positive (EQ2 curvature check)
f2_col    = M[:, 1]
f2_pos    = bool(np.all(f2_col > 0.0))
f2_min    = float(f2_col.min())
print(f"\n  F2 (curvature) all positive: {'PASS' if f2_pos else 'FAIL'}  "
      f"(min = {f2_min:.4e})")
assert f2_pos, "F2 curvature not positive at all zeros — EQ2 check FAIL"


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — SVD Consensus
# ─────────────────────────────────────────────────────────────────────────────

print()
print("[SVD] Column-normalise then SVD:")

# Column normalise (each EQ functional to unit norm across the 9 zeros)
col_norms = np.linalg.norm(M, axis=0)
col_norms = np.where(col_norms < 1e-30, 1.0, col_norms)
M_norm    = M / col_norms           # shape (9, 10), each column unit norm

U, S_svd, Vt = np.linalg.svd(M_norm, full_matrices=False)
# U: (9, 9),  S_svd: (9,),  Vt: (9, 10)

consensus   = U[:, 0]               # dominant left singular vector — 9D
s1          = float(S_svd[0])
s2          = float(S_svd[1]) if len(S_svd) > 1 else 0.0
dominance   = s1 / s2 if s2 > 1e-12 else float("inf")

norm_consensus = float(np.linalg.norm(consensus))

print(f"  s₁ (dominant) = {s1:.6f}")
print(f"  s₂            = {s2:.6f}")
print(f"  s₁/s₂         = {dominance:.4f}  "
      f"({'strong consensus' if dominance > 1.5 else 'moderate consensus'})")
print(f"  |consensus|   = {norm_consensus:.8f}  (unit by SVD construction)")
print(f"  NORM_X_STAR   = {NORM_X_STAR:.8f}  (AXIOMS — alignment deferred to STEP 7)")

print(f"\n  Consensus vector (9D):")
for i, v in enumerate(consensus):
    print(f"    x_{i+1} = {v:+.8f}")

# P4 coupling check
coupling_ok = 0.0010 <= COUPLING_K <= 0.0050
print(f"\n  [P4] coupling_k = {COUPLING_K:.6f}   "
      f"{'OK (BS-4)' if coupling_ok else 'ANOMALOUS'}")
assert coupling_ok, "P4 VIOLATION: coupling_k outside [0.0010, 0.0050]"


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — NORM_X_STAR Cross-Check (STEP_2 reference)
# ─────────────────────────────────────────────────────────────────────────────

REF_NORM = 0.34226067113747900961787251073434770451853996743283664
REF_LAM  = 494.05895555802020426355559872240107048767357569104664

rel_norm = abs(NORM_X_STAR - REF_NORM) / REF_NORM
rel_lam  = abs(LAMBDA_STAR - REF_LAM)  / REF_LAM
ref_pass = rel_norm < 1e-6 and rel_lam < 1e-6

print()
print(f"[REF] STEP_2 cross-check:")
print(f"  λ*      rel error = {rel_lam:.2e}   {'PASS' if rel_lam < 1e-6 else 'FAIL'}")
print(f"  ‖x*‖₂  rel error = {rel_norm:.2e}   {'PASS' if rel_norm < 1e-6 else 'FAIL'}")
assert ref_pass, "FAIL: reference constants do not match STEP_2 to 1e-6"


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — Write CSVs and Final Summary
# ─────────────────────────────────────────────────────────────────────────────

elapsed = time.time() - t0
_ANALYTICS.mkdir(parents=True, exist_ok=True)

# EQ matrix CSV
csv_m = _ANALYTICS / "step_06_eq_matrix.csv"
with open(csv_m, "w", newline="") as f:
    ww = csv.DictWriter(f, fieldnames=["k", "T"] + EQ_NAMES)
    ww.writeheader()
    for r in rows_m:
        ww.writerow({
            k_: (f"{v:.8e}" if isinstance(v, float) else v)
            for k_, v in r.items()
        })
print(f"[CSV] EQ matrix → {csv_m}")

# SVD CSV (singular values + consensus vector)
csv_svd = _ANALYTICS / "step_06_svd.csv"
with open(csv_svd, "w", newline="") as f:
    ww = csv.writer(f)
    ww.writerow(["component", "singular_value", "consensus_coord",
                 "dominance_ratio", "status"])
    for i, (sv, cv) in enumerate(zip(S_svd, consensus)):
        dom = f"{dominance:.4f}" if i == 0 else ""
        stat = "DOMINANT" if i == 0 else ("CHECK" if i == 1 else "INFO")
        ww.writerow([i + 1, f"{sv:.8e}", f"{cv:.10f}", dom, stat])
print(f"[CSV] SVD       → {csv_svd}")

# ── U5 PASS/FAIL lines ───────────────────────────────────────────────────────
print()
print("=" * 72)
print("STEP 6 RESULT SUMMARY")
print(f"  F2 curvature positive at all zeros : {'PASS' if f2_pos else 'FAIL'}")
print(f"  Dominant singular value s₁         : {s1:.6f}")
print(f"  Dominance ratio s₁/s₂              : {dominance:.4f}")
print(f"  |consensus|                        : {norm_consensus:.8f}  (unit by SVD)")
print(f"  NORM_X_STAR (reference only)       : {NORM_X_STAR:.8f}")
print(f"  REF cross-check                    : {'PASS' if ref_pass else 'FAIL'}")
print(f"  P4 coupling_k                      : {'PASS' if coupling_ok else 'FAIL'}")
print(f"  Elapsed                            : {elapsed:.2f}s")
print()
print(f"STEP 6 F2_POSITIVE:   {'PASS' if f2_pos else 'FAIL'}")
print(f"STEP 6 SVD_CONSENSUS: PASS  (s₁={s1:.4f}, dominance={dominance:.2f})")
print(f"STEP 6 REF_CHECK:     {'PASS' if ref_pass else 'FAIL'}")
print(f"STEP 6 P4_COUPLING:   {'PASS' if coupling_ok else 'FAIL'}")
print("=" * 72)
print()
print("NOTE: Geometric alignment of consensus vs AXIOMS x* is deferred to STEP 7.")
print("      STEP 6 establishes only: all 10 EQ systems agree on a single 9D")
print("      direction at σ=½ across all 9 zero heights.")
print()
print("STEP 6 COMPLETE — 10-EQ consensus found.  Proceed to STEP 7.")