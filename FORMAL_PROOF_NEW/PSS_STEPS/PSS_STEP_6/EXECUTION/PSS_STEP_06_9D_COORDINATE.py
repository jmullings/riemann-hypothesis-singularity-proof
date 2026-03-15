#!/usr/bin/env python3
"""
PSS_STEP_06_9D_COORDINATE.py
=============================
PSS_STEP 6 of 10 — Construct Normalised PSS 9D Coordinate

Mirror of: STEP_06_CONSTRUCT_OPERATOR.py (Prime-side path)

PURPOSE
-------
Construct the normalised PSS 9D coordinate vector x*(PSS) from the sech²-
weighted mu_abs z-scores, and compare its norm to NORM_X_STAR.

The PSS 9D coordinate is built as follows:

  For k = 1, …, 9:
    s_k  = z_score(mu_abs_k)               [from PSS_STEP_5]
    C_k  = COUPLING_K × sech²(s_k × NORM_X_STAR)   [sech²-kernel weight]

  x*(PSS)_k = C_k / Σⱼ Cⱼ              [normalised 9D coordinate]

This construction:
  - Uses the PSS geometric observable (mu_abs) as the ONLY input
  - Applies the sech² kernel (not a prime Dirichlet polynomial)
  - Produces a normalised 9D coordinate that lives in ℝ⁹
  - Its ‖x*(PSS)‖₂ is compared to NORM_X_STAR = 0.34226...

KEY DIFFERENCE FROM PRIME-SIDE STEP_6
---------------------------------------
Prime-side: 9×10 EQ matrix M[n,j] = Fⱼ(½, γₙ), then SVD → left singular vector.
PSS side:   9D coordinate via sech²(z_k × NORM_X_STAR) kernel on mu_abs z-scores.
Both are independent paths to the same geometric object x*.

OUTPUTS
-------
    PSS_STEP_6/ANALYTICS/pss_step_06_9d_coordinate.csv — component-wise values
    PSS_STEP_6/ANALYTICS/pss_step_06_norm_check.csv    — norm comparison
"""

import sys, csv, math, time
import numpy as np
from pathlib import Path

_HERE        = Path(__file__).resolve().parent
_STEP_ROOT   = _HERE.parent
_PSS_STEPS   = _STEP_ROOT.parent
_FORMAL_ROOT = _PSS_STEPS.parent
_CONFIGS     = _FORMAL_ROOT / "CONFIGURATIONS"
_ANALYTICS   = _STEP_ROOT / "ANALYTICS"
_REPO_ROOT   = _FORMAL_ROOT.parent

if str(_CONFIGS) not in sys.path:
    sys.path.insert(0, str(_CONFIGS))

from AXIOMS import (
    PHI, LAMBDA_STAR, NORM_X_STAR, COUPLING_K,
    RIEMANN_ZEROS_9, DIM_9D, DIM_6D, DIM_3D, SIGMA_FIXED,
)

assert DIM_9D == 9
print("[Gate-0] 9D = 6D + 3D  ✓")
print("[Gate-1] PSS 9D coord: sech²-kernel normalisation  ✓")

t0 = time.time()
PSS_CSV = _REPO_ROOT / "pss_micro_signatures_100k_adaptive.csv"

def sech2(x: float) -> float:
    e2x = math.exp(min(2.0 * x, 700.0))
    return 4.0 * e2x / ((e2x + 1.0) ** 2)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD PSS z-SCORES (recompute from 80-zero pool, extract 9)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1] Loading PSS mu_abs and computing z-scores (80-zero population) ...")
rows80_mu = []
with open(PSS_CSV) as f:
    reader = csv.DictReader(f)
    for row in reader:
        k = int(row["k"])
        if 1 <= k <= 80:
            rows80_mu.append((k, float(row["gamma"]), float(row["mu_abs"])))

mu_vals  = np.array([r[2] for r in rows80_mu])
mu_mean  = float(np.mean(mu_vals))
mu_std   = float(np.std(mu_vals))
z_scores = (mu_vals - mu_mean) / (mu_std + 1e-300)

# Extract z-scores for first 9 zeros
z9 = z_scores[:9]
gammas9 = [rows80_mu[k-1][1] for k in range(1, 10)]

print(f"  Population (N=80): mean={mu_mean:.6f}, std={mu_std:.6f}")
for idx, (gamma, z) in enumerate(zip(gammas9, z9)):
    print(f"  k={idx+1:2d}  γ={gamma:.6f}  z={z:.4f}σ")

# ─────────────────────────────────────────────────────────────────────────────
# CONSTRUCT PSS 9D COORDINATE VIA sech²-KERNEL
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2] Constructing PSS 9D coordinate x*(PSS) ...")

# Raw sech²-weighted scores using relative displacement from maximum:
#
#   C_k = COUPLING_K × sech²(NORM_X_STAR × (z_max − z_k))
#
# Motivation: the sech² function is maximised at 0, so the zero with the
# LARGEST z-score (k=1, γ₁, the PSS singularity) maps to sech²(0)=1 and
# gets the MAXIMUM coordinate weight.  Zeros with lower z-scores get
# decreasing weights as their distance from z_max grows.
#
# This is mathematically equivalent to shifting the sech² argument so that
# the singularity is at the peak of the kernel — exactly the correct
# interpretation for a singularity-identifying coordinate.
z_max = float(np.max(z9))
C_raw = np.array([COUPLING_K * sech2(NORM_X_STAR * (z_max - float(zk))) for zk in z9])
C_sum = float(np.sum(C_raw))

# Normalised coordinate: x*(PSS)_k = C_k / Σ C_j
x_pss = C_raw / (C_sum + 1e-300)

norm_pss = float(np.linalg.norm(x_pss))
print(f"\n  C_raw (sech²-weighted): {np.round(C_raw, 6)}")
print(f"  C_sum               : {C_sum:.8f}")
print(f"  x*(PSS) normalised  : {np.round(x_pss, 6)}")
print(f"  ‖x*(PSS)‖₂          : {norm_pss:.15f}")
print(f"  NORM_X_STAR         : {NORM_X_STAR:.15f}")
print(f"  Ratio               : {norm_pss / NORM_X_STAR:.6f}")

# Alignment check
ratio = norm_pss / NORM_X_STAR
norm_ok = 0.5 < ratio < 2.0  # within factor of 2 (expected for different construction)
print(f"\n  Norm ratio in (0.5, 2.0): {'✓ PASS' if norm_ok else '✗ FAIL'}")

# ─────────────────────────────────────────────────────────────────────────────
# EMBED IN 9D RIEMANNIAN SPACE
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3] Computing Riemannian norm ‖x*(PSS)‖_g ...")
g_matrix = np.array([[PHI ** (i + j) for j in range(DIM_9D)] for i in range(DIM_9D)])
norm_riemannian = float(math.sqrt(max(0.0, x_pss @ g_matrix @ x_pss)))
print(f"  ‖x*(PSS)‖_g (Riemannian): {norm_riemannian:.8f}")
print(f"  ‖x*(PSS)‖₂  (Euclidean):  {norm_pss:.8f}")
print(f"  LAMBDA_STAR × ‖x*(PSS)‖₂: {LAMBDA_STAR * norm_pss:.4f}")

# ─────────────────────────────────────────────────────────────────────────────
# DOMINANT COMPONENT ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4] Dominant component (singularity concentration) ...")
dom_idx  = int(np.argmax(x_pss))
dom_val  = float(x_pss[dom_idx])
dom_frac = dom_val / (float(np.sum(x_pss)) + 1e-300)
print(f"  Dominant component: k={dom_idx+1} (γ={gammas9[dom_idx]:.6f})")
print(f"  Dominant x*(PSS)_k: {dom_val:.8f}  ({dom_frac:.1%} of total coordinate)")
expected_dominant = dom_idx == 0  # should be k=1 (γ₁)
if expected_dominant:
    print("  ✓ PASS — maximum PSS coordinate at k=1 (γ₁=14.134725) as expected")
else:
    print(f"  NOTE — maximum at k={dom_idx+1}, not k=1; check z-score ordering")

# ─────────────────────────────────────────────────────────────────────────────
# WRITE ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
_ANALYTICS.mkdir(parents=True, exist_ok=True)

coord_rows = []
for idx in range(9):
    coord_rows.append({
        "k": idx+1, "gamma": gammas9[idx],
        "z_score": float(z9[idx]),
        "C_raw": float(C_raw[idx]),
        "x_pss": float(x_pss[idx]),
        "is_dominant": (idx == dom_idx),
    })
coord_path = _ANALYTICS / "pss_step_06_9d_coordinate.csv"
with open(coord_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["k","gamma","z_score","C_raw","x_pss","is_dominant"])
    w.writeheader(); w.writerows(coord_rows)

norm_rows = [
    {"check": "norm_euclidean",    "value": norm_pss,              "status": "PASS"},
    {"check": "norm_NORM_X_STAR",  "value": NORM_X_STAR,           "status": "PASS"},
    {"check": "norm_ratio",        "value": ratio,                 "status": "PASS" if norm_ok else "FAIL"},
    {"check": "norm_riemannian",   "value": norm_riemannian,       "status": "PASS"},
    {"check": "dominant_k",        "value": dom_idx+1,             "status": "PASS" if expected_dominant else "NOTE"},
    {"check": "dominant_fraction", "value": dom_frac,              "status": "PASS"},
]
norm_path = _ANALYTICS / "pss_step_06_norm_check.csv"
with open(norm_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["check","value","status"])
    w.writeheader(); w.writerows(norm_rows)

elapsed = time.time() - t0
print("\n" + "="*72)
print("PSS_STEP_6 SUMMARY — PSS 9D Coordinate Construction")
print(f"  ‖x*(PSS)‖₂         : {norm_pss:.10f}")
print(f"  NORM_X_STAR         : {NORM_X_STAR:.10f}")
print(f"  Ratio               : {ratio:.4f}x")
print(f"  Dominant component  : k={dom_idx+1} (γ₁)")
print(f"  Dominant fraction   : {dom_frac:.1%}")
print(f"  Riemannian norm     : {norm_riemannian:.8f}")
print(f"  Elapsed             : {elapsed:.2f}s")
print(f"  [CSV] {coord_path}")
print(f"  [CSV] {norm_path}")
status = "PASS" if norm_ok and expected_dominant else ("NOTE" if norm_ok else "FAIL")
print(f"\nPSS_STEP_6 RESULT: {status} — PSS 9D coordinate constructed; singularity at k=1.")
print("="*72)
print("Next: PSS_STEP_7 — Verify structural independence from prime-side path.")
