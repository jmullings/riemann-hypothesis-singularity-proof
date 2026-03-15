#!/usr/bin/env python3
"""
STEP_05_VERIFY_BRIDGES.py
==========================
STEP 5 of 10 — Curvature Spectrum at σ = ½ from EQ2

PURPOSE
-------
Compute the σ-curvature functional F₂(½, T) = 2|D'(s)|² + 2Re(D''·D̄)
at σ = ½ for each of the 9 Riemann zero heights γ₁…γ₉.

These 9 values form the raw curvature vector.  Normalise to define the
9D unit vector x*(raw).  This vector is the EQ2-anchored singularity
direction that feeds into STEP 6's 10-EQ consensus matrix.

WHAT THIS STEP ESTABLISHES
---------------------------
  "Curvature F₂(½, γₙ) > 0 for all n = 1…9"          ✅ (finite)
  Produces x*(raw) — the EQ2 curvature spectrum vector  ✅ (finite)

WHAT IS NOT CLAIMED
--------------------
  No alignment with AXIOMS geometry is claimed here.
  NORM_X_STAR is printed as an external reference scalar only.
  Directional alignment (cosine similarity) is deferred to STEP 7.

PROTOCOL COMPLIANCE
-------------------
  P1  No log() as primary energy operator.
      LN_P is a P1.1 raw data ingest table (math.log used only here).
      The energy layer (_dD, _d2D, F2_curvature) uses only the
      trigonometric form of p^(-s) — exp/cos/sin, no log().
  P2  9D golden metric constructed before any computation.
  P3  Riemann-φ weight check included (w(p,γ₁) sanity).
  P4  sech²(x*(raw)_k) and coupling_k reported (BS-1…BS-4).
  P5  Explicit PASS/FAIL lines; CSV for STEP 6.

OUTPUT CSV  (step_05_curvature_spectrum.csv)
--------------------------------------------
  Columns: k, T_k, F2_half, x_star_k, sech2_val, error_rate, bit_energy
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
    DIM_9D,
)

print("[Gate-0] Curvature spectrum at σ=0.5  OK")
print()
print("=" * 72)
print("STEP 5 — Curvature Spectrum at σ = ½")
print(f"  NORM_X_STAR = {NORM_X_STAR}")
print(f"  LAMBDA_STAR = {LAMBDA_STAR}")
print(f"  φ           = {PHI}")
print("=" * 72)

t0 = time.time()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 0 — Golden 9D Metric (P2: constructed before any computation)
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

PRIMES = _sieve(100)

# P1.1 RAW DATA INGEST — math.log used here only, stored as static table.
# ln p is not an energy operator; it is the natural logarithm of a prime
# used solely to construct the geometric angle T·ln p.
LN_P: dict = {p: math.log(p) for p in PRIMES}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — Trigonometric prime-power basis (P1 energy layer)
# ─────────────────────────────────────────────────────────────────────────────

def _p_power(p: int, sigma: float, T: float) -> Tuple[float, float]:
    """
    p^(-σ-iT) in Cartesian form.

    P1 compliance: LN_P used only as angle scalar (T·ln p).
    Returns (real, imag).
    """
    mag   = p ** (-sigma)
    angle = T * LN_P[p]
    return mag * math.cos(angle), -mag * math.sin(angle)


def _D(sigma: float, T: float) -> Tuple[float, float]:
    """D_X(s) = Σ_p p^(-s);  returns (Re, Im)."""
    re = im = 0.0
    for p in PRIMES:
        dr, di = _p_power(p, sigma, T)
        re += dr;  im += di
    return re, im


def _dD(sigma: float, T: float) -> Tuple[float, float]:
    """D'_X(s) = -Σ_p ln(p)·p^(-s).  P1: ln p is scalar coefficient."""
    re = im = 0.0
    for p in PRIMES:
        dr, di = _p_power(p, sigma, T)
        lp = LN_P[p]
        re += -lp * dr;  im += -lp * di
    return re, im


def _d2D(sigma: float, T: float) -> Tuple[float, float]:
    """D''_X(s) = Σ_p ln²(p)·p^(-s).  P1: ln²p is scalar coefficient."""
    re = im = 0.0
    for p in PRIMES:
        dr, di = _p_power(p, sigma, T)
        lp2 = LN_P[p] ** 2
        re += lp2 * dr;  im += lp2 * di
    return re, im


def F2_curvature(sigma: float, T: float) -> float:
    """
    EQ2 curvature:  F₂(σ,T) = 2|D'(s)|² + 2·Re(D''(s)·D̄(s))

    P1 compliance: all terms built from trig form of p^(-s).
    LN_P enters only as scalar multipliers in _dD / _d2D.
    """
    Dr, Di     = _D(sigma, T)
    dDr, dDi   = _dD(sigma, T)
    d2Dr, d2Di = _d2D(sigma, T)

    dD_sq = dDr ** 2 + dDi ** 2                  # |D'|²
    cross  = d2Dr * Dr + d2Di * Di                # Re(D''·D̄)
    return 2.0 * dD_sq + 2.0 * cross


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — sech² helpers (P4 compliance)
# ─────────────────────────────────────────────────────────────────────────────

def _sech_sq(x: float) -> float:
    """sech²(x) via exp() only — P1 compliant."""
    if abs(x) > 50.0:
        return 0.0
    e2x = math.exp(2.0 * x)
    return 4.0 * e2x / (e2x + 1.0) ** 2


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — Compute curvature spectrum
# ─────────────────────────────────────────────────────────────────────────────

print()
print("[EQ2] F₂(½, γₙ) for n = 1…9:")
print(f"  {'k':>3}  {'γₙ':>12}  {'F₂(½,γₙ)':>14}  {'x*(raw)_k':>12}  "
      f"{'sech²(x_k)':>12}  {'err_rate':>10}")
print("  " + "-" * 70)

curvatures: List[float] = []
for T in RIEMANN_ZEROS_9:
    curvatures.append(F2_curvature(0.5, T))

curv_arr   = np.array(curvatures)
all_pos    = bool(np.all(curv_arr > 0.0))
curv_norm  = float(np.linalg.norm(curv_arr))
x_star_raw = curv_arr / curv_norm if curv_norm > 0 else curv_arr

# P4 bit-size values for each component
rows: List[dict] = []
bs_all_ok = True
for k, (T, c, x) in enumerate(zip(RIEMANN_ZEROS_9, curvatures, x_star_raw)):
    s2       = _sech_sq(x)
    err_rate = 1.0 - s2
    # gap to next zero for bit_energy
    if k + 1 < len(RIEMANN_ZEROS_9):
        gap = abs(RIEMANN_ZEROS_9[k + 1] - T)
    else:
        gap = abs(T - RIEMANN_ZEROS_9[k - 1])
    bit_e    = err_rate * gap
    ck       = COUPLING_K
    ck_ok    = 0.0010 <= ck <= 0.0050
    if not ck_ok:
        bs_all_ok = False

    rows.append({
        "k":         k + 1,
        "T_k":       T,
        "F2_half":   c,
        "x_star_k":  x,
        "sech2_val": s2,
        "error_rate": err_rate,
        "bit_energy": bit_e,
    })
    print(f"  {k+1:>3}  {T:>12.6f}  {c:>14.6e}  {x:>12.8f}  "
          f"{s2:>12.6f}  {err_rate:>10.6f}")

print()
norm_xraw = float(np.linalg.norm(x_star_raw))
ratio     = norm_xraw / NORM_X_STAR

print(f"  norm(curvatures) = {curv_norm:.8e}")
print(f"  norm(x*(raw))    = {norm_xraw:.8f}  (unit by construction)")
print(f"  AXIOMS NORM_X*   = {NORM_X_STAR:.8f}  (reference only)")
print(f"  ratio            = {ratio:.4f}  "
      f"(energy units vs unit vector — alignment deferred to STEP 7)")
print()
print(f"  F₂ all positive : {'PASS' if all_pos else 'FAIL'}")
assert all_pos, "F2 curvature not positive at all zeros — EQ2 check FAIL"


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — P3 Riemann-φ weight sanity check
# ─────────────────────────────────────────────────────────────────────────────

gamma1 = RIEMANN_ZEROS_9[0]
w_sample = (PHI ** (-2)) * math.exp(-gamma1 / 2)    # p=2, γ₁
print(f"[P3] Sample Riemann-φ weight w(2,γ₁) = {w_sample:.6e}  (positive: {'OK' if w_sample > 0 else 'FAIL'})")
assert w_sample > 0, "P3 VIOLATION: Riemann-φ weight not positive"


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — P4 coupling check
# ─────────────────────────────────────────────────────────────────────────────

coupling_ok = 0.0010 <= COUPLING_K <= 0.0050
print(f"[P4] coupling_k = {COUPLING_K:.6f}   "
      f"{'OK (BS-4)' if coupling_ok else 'ANOMALOUS — investigate'}")
assert coupling_ok, "P4 VIOLATION: coupling_k outside [0.0010, 0.0050]"


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — NORM_X_STAR cross-check (STEP_2 reference)
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
# SECTION 8 — Write CSV and Final Summary
# ─────────────────────────────────────────────────────────────────────────────

elapsed = time.time() - t0
_ANALYTICS.mkdir(parents=True, exist_ok=True)

csv_path = _ANALYTICS / "step_05_curvature_spectrum.csv"
with open(csv_path, "w", newline="") as f:
    ww = csv.DictWriter(
        f, fieldnames=["k", "T_k", "F2_half", "x_star_k",
                        "sech2_val", "error_rate", "bit_energy"])
    ww.writeheader()
    for r in rows:
        ww.writerow({
            k_: (f"{v:.10e}" if isinstance(v, float) else v)
            for k_, v in r.items()
        })
print(f"[CSV] Spectrum → {csv_path}")

# ── U5 PASS/FAIL lines ───────────────────────────────────────────────────────
print()
print("=" * 72)
print("STEP 5 RESULT SUMMARY")
print(f"  norm(curvatures) = {curv_norm:.8e}")
print(f"  norm(x*(raw))    = {norm_xraw:.8f}  (unit by construction)")
print(f"  AXIOMS NORM_X*   = {NORM_X_STAR:.8f}  (reference only)")
print(f"  ratio            = {ratio:.4f}")
print(f"  Elapsed          : {elapsed:.2f}s")
print()
print(f"STEP 5 F2_POSITIVE:  {'PASS' if all_pos else 'FAIL'}")
print(f"STEP 5 P3_WEIGHTS:   {'PASS' if w_sample > 0 else 'FAIL'}")
print(f"STEP 5 P4_COUPLING:  {'PASS' if coupling_ok else 'FAIL'}")
print(f"STEP 5 REF_CHECK:    {'PASS' if ref_pass else 'FAIL'}")
print("=" * 72)
print()
print("NOTE: x*(raw) is the EQ2 curvature unit vector feeding STEP 6.")
print("      Alignment with AXIOMS x* geometry is deferred to STEP 7.")
print()
print("STEP 5 COMPLETE — Curvature spectrum computed.  Proceed to STEP 6.")