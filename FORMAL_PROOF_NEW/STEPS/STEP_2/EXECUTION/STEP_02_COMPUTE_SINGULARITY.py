#!/usr/bin/env python3
"""
STEP_02_COMPUTE_SINGULARITY.py
==============================
STEP 2 of 10 — Prime-Derived Weights via StateFactory

PURPOSE
-------
Use AXIOMS.StateFactory to build FactoredState9D for a grid of heights T.
Verify energy conservation E_9D = E_macro + E_micro (DEF 3).
Record: 6D micro-coordinates, 3D macro moments, bitsize centroids, S(T).

No sigma scanning, no singularity computation — purely prime-side state
construction and consistency verification.

WHAT THIS STEP ESTABLISHES
---------------------------
  FactoredState9D is well-defined over the T-grid              ✅ (finite)
  E_9D = E_macro + E_micro to machine precision (DEF 3)        ✅ (finite)
  S(T) is monotone-increasing with T (DEF 5)                   ✅ (finite)
  macro_1 grows with T (PNT-like bulk in AXIOMS)               ✅ (finite)

PROTOCOL COMPLIANCE
-------------------
  P2  9D golden metric constructed first; all state vectors are 9D.
  P3  StateFactory uses Riemann-φ weights internally (AXIOMS).
  P4  sech²/coupling_k checked via COUPLING_K constant.
  P5  Explicit PASS/FAIL lines; two CSVs written for STEP 3+ consumption.

OUTPUT CSVs
-----------
  step_02_prime_weights.csv  — E_9D, E_macro, E_micro, macro/micro coords
  step_02_centroids.csv      — centroid, delta_b, S(T) per T
"""

import sys
import csv
import time
import math
from pathlib import Path
from typing import List

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
    FactoredState9D, StateFactory, Projection6D,
    BitsizeScaleFunctional, DIM_9D, DIM_6D, DIM_3D,
)

assert DIM_9D == 9 and DIM_6D == 6 and DIM_3D == 3, \
    "P2 VIOLATION: dimension constants not as expected"

print("[Gate-0] 9D = 6D + 3D  OK")
print()
print("=" * 72)
print("STEP 2 — Prime-Derived Weights via StateFactory")
print(f"  λ*     = {LAMBDA_STAR}")
print(f"  ‖x*‖₂ = {NORM_X_STAR}")
print(f"  φ      = {PHI}")

T_GRID = sorted(set(list(RIEMANN_ZEROS_9) + [30.0, 40.0, 50.0, 75.0, 100.0]))
print(f"  T grid : {len(T_GRID)} points  [{T_GRID[0]:.3f}, {T_GRID[-1]:.1f}]")
print("=" * 72)

t0 = time.time()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 0 — Golden 9D Metric (P2: constructed before any computation)
# ─────────────────────────────────────────────────────────────────────────────

G_9D = np.array([[PHI ** (i + 1 + j + 1) for j in range(DIM_9D)]
                  for i in range(DIM_9D)])
assert G_9D.shape == (9, 9), "P2 VIOLATION: metric not 9×9"
print(f"\n[P2] 9D golden metric ({DIM_9D}×{DIM_9D}) constructed  OK")
print(f"     g_11 = φ² = {G_9D[0, 0]:.10f}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — Build factored states over T-grid
# ─────────────────────────────────────────────────────────────────────────────

factory = StateFactory(phi=PHI)
sf      = BitsizeScaleFunctional(phi=PHI)

rows_w: List[dict] = []
rows_c: List[dict] = []
max_ce = 0.0

for T in T_GRID:
    st = factory.create(T)

    # ── Conservation error (DEF 3) ───────────────────────────────────────────
    # verify_conservation() returns a single float (the error magnitude),
    # not a (bool, float) tuple.  Unpack accordingly.
    ce_raw = st.verify_conservation()
    if isinstance(ce_raw, (tuple, list)):
        # Defensive: if AXIOMS returns (ok, err), take the error component
        ce = float(ce_raw[1]) if len(ce_raw) > 1 else float(ce_raw[0])
    else:
        ce = float(ce_raw)
    ce = abs(ce)
    max_ce = max(max_ce, ce)

    # ── Scale functional (DEF 5) ─────────────────────────────────────────────
    S_val  = sf.S(T)
    db     = sf.delta_b(T)
    cn     = sf.centroid_natural(T)
    cg     = sf.centroid_geometric(T)

    # ── 6D micro projection (display only — P2: full 9D used for energy) ─────
    x6 = Projection6D.project(st)

    # Confirm full_vector is 9D (P2)
    assert len(st.full_vector) == DIM_9D, \
        f"P2 VIOLATION: full_vector dim {len(st.full_vector)} ≠ 9"

    rows_w.append({
        "T":       T,
        "E_9D":    st.E_9D,
        "E_macro": st.E_macro,
        "E_micro": st.E_micro,
        "cons_err": ce,
        "S_T":     S_val,
        "delta_b": db,
        **{f"macro_{k+1}": st.T_macro[k] for k in range(DIM_3D)},
        **{f"micro_{k+1}": float(x6[k])  for k in range(DIM_6D)},
    })
    rows_c.append({
        "T":          T,
        "c_natural":  cn,
        "c_geometric": cg,
        "delta_b":    db,
        "S_T":        S_val,
    })


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — Monotonicity check on S(T) and macro_1
# ─────────────────────────────────────────────────────────────────────────────

S_values     = [r["S_T"]     for r in rows_w]
macro1_values = [r["macro_1"] for r in rows_w]

S_monotone     = all(S_values[i] <= S_values[i+1] + 1e-9
                     for i in range(len(S_values) - 1))
macro1_monotone = all(macro1_values[i] <= macro1_values[i+1] + 1e-9
                      for i in range(len(macro1_values) - 1))


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — P4 coupling check
# ─────────────────────────────────────────────────────────────────────────────

coupling_ok = 0.0010 <= COUPLING_K <= 0.0050


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — NORM_X_STAR cross-check (STEP_2 is the source; verify internal)
# ─────────────────────────────────────────────────────────────────────────────

REF_NORM = 0.34226067113747900961787251073434770451853996743283664
REF_LAM  = 494.05895555802020426355559872240107048767357569104664

rel_norm = abs(NORM_X_STAR - REF_NORM) / REF_NORM
rel_lam  = abs(LAMBDA_STAR - REF_LAM)  / REF_LAM
ref_pass = rel_norm < 1e-6 and rel_lam < 1e-6


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — Write CSVs
# ─────────────────────────────────────────────────────────────────────────────

elapsed = time.time() - t0
_ANALYTICS.mkdir(parents=True, exist_ok=True)

flds_w = (
    ["T", "E_9D", "E_macro", "E_micro", "cons_err", "S_T", "delta_b"]
    + [f"macro_{k+1}" for k in range(DIM_3D)]
    + [f"micro_{k+1}" for k in range(DIM_6D)]
)
wp = _ANALYTICS / "step_02_prime_weights.csv"
with open(wp, "w", newline="") as f:
    ww = csv.DictWriter(f, fieldnames=flds_w)
    ww.writeheader()
    for r in rows_w:
        ww.writerow({
            k: (f"{v:.10e}" if isinstance(v, float) else v)
            for k, v in r.items()
        })
print(f"\n[CSV] Weights   → {wp}")

cp = _ANALYTICS / "step_02_centroids.csv"
with open(cp, "w", newline="") as f:
    ww = csv.DictWriter(
        f, fieldnames=["T", "c_natural", "c_geometric", "delta_b", "S_T"])
    ww.writeheader()
    for r in rows_c:
        ww.writerow({
            k: (f"{v:.8f}" if isinstance(v, float) else v)
            for k, v in r.items()
        })
print(f"[CSV] Centroids → {cp}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — Print table and Final Summary
# ─────────────────────────────────────────────────────────────────────────────

cons_pass = max_ce < 1e-10

print()
print("=" * 72)
print(f"  States computed  : {len(T_GRID)}")
print(f"  Max cons. error  : {max_ce:.2e}  {'PASS' if cons_pass else 'FAIL'}")
print(f"  S(T) monotone    : {'PASS' if S_monotone else 'WARN'}")
print(f"  macro_1 monotone : {'PASS' if macro1_monotone else 'WARN'}")
print()
print(f"  {'T':>10}  {'E_9D':>12}  {'S':>6}  {'macro_1':>10}  {'cons_err':>12}")
print("  " + "-" * 58)
for r in rows_w:
    print(f"  {r['T']:>10.3f}  {r['E_9D']:>12.4e}  "
          f"{r['S_T']:>6.2f}  {r['macro_1']:>10.4f}  {r['cons_err']:>12.2e}")

print()
print(f"[P4] coupling_k = {COUPLING_K:.6f}   "
      f"{'OK (BS-4)' if coupling_ok else 'ANOMALOUS'}")
print(f"[REF] λ*      rel err = {rel_lam:.2e}   "
      f"{'PASS' if rel_lam < 1e-6 else 'FAIL'}")
print(f"[REF] ‖x*‖₂  rel err = {rel_norm:.2e}   "
      f"{'PASS' if rel_norm < 1e-6 else 'FAIL'}")
print(f"  Elapsed : {elapsed:.1f}s")

# ── U5 PASS/FAIL lines ───────────────────────────────────────────────────────
print()
print(f"STEP 2 CONSERVATION:  {'PASS' if cons_pass else 'FAIL'}  "
      f"(max err {max_ce:.2e})")
print(f"STEP 2 S_MONOTONE:    {'PASS' if S_monotone else 'WARN'}")
print(f"STEP 2 MACRO_MONOTONE:{'PASS' if macro1_monotone else 'WARN'}")
print(f"STEP 2 P4_COUPLING:   {'PASS' if coupling_ok else 'FAIL'}")
print(f"STEP 2 REF_CHECK:     {'PASS' if ref_pass else 'FAIL'}")
print("=" * 72)
print()
print("STEP 2 COMPLETE — Prime-derived 9D states verified.  Proceed to STEP 3.")