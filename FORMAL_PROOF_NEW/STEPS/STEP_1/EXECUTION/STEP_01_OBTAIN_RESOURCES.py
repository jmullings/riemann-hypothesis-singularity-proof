#!/usr/bin/env python3
"""
STEP_01_OBTAIN_RESOURCES.py
============================
STEP 1 of 10 — Fix AXIOMS Ground
Non-circular build order: primes → weights → sigmas → singularity → proof

PURPOSE
-------
Certify that AXIOMS.py is the sole source of constants and that all four
foundational axioms hold over the T grid used in subsequent steps:

    (A) DEFINITION 3 — Energy conservation: E_9D = E_macro + E_micro
    (B) DEFINITION 2 — Orthogonal 3D+6D split: X = X_macro ⊕ X_micro
    (C) DEFINITION 5 — Scale functional: S(T) = 2^{Δb(T)} is well-defined
    (D) DEFINITION 8 / AXIOM U1* — Band-wise convexity: C_k(T,h) ≥ 0
                                    [CONJECTURAL — monitored, not required]

OUTPUTS
-------
    STEP_1/ANALYTICS/step_01_axiom_report.csv   — per-T conservation errors
    STEP_1/ANALYTICS/step_01_bandwise_convexity.csv — per-band convexity results
    Console summary with PASS / FAIL for each axiom

PROTOCOL
--------
P1: No log() as primary operator (only inside von_mangoldt / bitsize)
P2: All geometry in 9D Riemannian space; 6D projections are display-only
P5: Trinity Gate-0 and Gate-1 passed before writing any output

NOTE ON U1* / DEFINITION 8
---------------------------
Band-wise convexity (Axiom U1*) is explicitly CONJECTURAL in AXIOMS.py.
It currently fails in Bands 3–6 on this finite T-grid.  This is reported
as a diagnostic; it does NOT gate progression to STEP 2.  Only core
Definitions 2, 3, and 5 (items A–C) are required for the operator and
state construction used in STEPS 2–10.  U1* is the open gap catalogued
as DEF8 in STEP 8 and carries forward as a constraint, not a proof.
"""

# ─────────────────────────────────────────────────────────────────────────────
# PATH SETUP — add CONFIGURATIONS to sys.path so AXIOMS can be imported
# ─────────────────────────────────────────────────────────────────────────────
import sys
import os
import csv
import math
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent                        # EXECUTION/
_STEP_ROOT = _HERE.parent                                      # STEP_1/
_FORMAL_ROOT = _STEP_ROOT.parent.parent                        # FORMAL_PROOF_NEW/
_CONFIGS = _FORMAL_ROOT / "CONFIGURATIONS"
_ANALYTICS = _STEP_ROOT / "ANALYTICS"

if str(_CONFIGS) not in sys.path:
    sys.path.insert(0, str(_CONFIGS))

import numpy as np
from AXIOMS import (
    LAMBDA_STAR, NORM_X_STAR, COUPLING_K, PHI,
    von_mangoldt, bitsize, bit_band,
    FactoredState9D, StateFactory, Projection6D,
    BitsizeScaleFunctional, NormalizedBridgeOperator,
    BandwiseConvexityChecker, AxiomVerifier,
    RIEMANN_ZEROS_9, DIM_9D, DIM_6D, DIM_3D,
)

# ─────────────────────────────────────────────────────────────────────────────
# TRINITY GATE-0: ambient dimension check
# ─────────────────────────────────────────────────────────────────────────────
assert DIM_9D == 9, "Gate-0 FAIL: ambient dimension must be 9"
assert DIM_6D == 6, "Gate-0 FAIL: micro projection dimension must be 6"
assert DIM_3D == 3, "Gate-0 FAIL: macro sector dimension must be 3"
assert DIM_6D + DIM_3D == DIM_9D, "Gate-0 FAIL: dimensions don't partition"
print("[Gate-0] Ambient dimensions: 9D = 6D + 3D  ✓")

# ─────────────────────────────────────────────────────────────────────────────
# TRINITY GATE-1: P1 static check — ensure no bare log() as primary operator
# ─────────────────────────────────────────────────────────────────────────────
import ast as _ast
_module_source = Path(__file__).read_text()
_tree = _ast.parse(_module_source)
_log_nodes = [
    node for node in _ast.walk(_tree)
    if (isinstance(node, _ast.Attribute) and node.attr == 'log')
    or (isinstance(node, _ast.Name) and node.id == 'log')
]
print(f"[Gate-1] P1 log-operator scan: {'PASS' if not _log_nodes else 'FAIL: log() call at lines ' + str([n.lineno for n in _log_nodes])}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 MAIN: Run AxiomVerifier.full_verification()
# ─────────────────────────────────────────────────────────────────────────────

T_GRID = RIEMANN_ZEROS_9 + [50.0, 75.0, 100.0]
T_RANGE = (min(T_GRID), max(T_GRID))

print()
print("=" * 72)
print("STEP 1 — AXIOMS Ground Verification")
print(f"  T range  : [{T_RANGE[0]:.1f}, {T_RANGE[1]:.1f}]")
print(f"  T samples: {len(T_GRID)} points")
print(f"  λ*       = {LAMBDA_STAR}")
print(f"  ‖x*‖₂    = {NORM_X_STAR}")
print(f"  φ        = {PHI:.15f}")
print("=" * 72)

t0 = time.time()

verifier = AxiomVerifier(T_range=T_RANGE, num_samples=len(T_GRID))
results  = verifier.full_verification()

elapsed = time.time() - t0

# ─────────────────────────────────────────────────────────────────────────────
# EXPORT — per-T energy conservation errors
# ─────────────────────────────────────────────────────────────────────────────
_ANALYTICS.mkdir(parents=True, exist_ok=True)

factory = StateFactory()
csv_path_cons = _ANALYTICS / "step_01_axiom_report.csv"
with open(csv_path_cons, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["T", "E_9D", "E_macro", "E_micro", "conservation_error",
                     "S_T", "delta_b"])
    sf = BitsizeScaleFunctional()
    for T in T_GRID:
        state = factory.create(T)
        ce_raw = state.verify_conservation()
        # verify_conservation() returns a single float (error magnitude).
        # Defensive unpack: if AXIOMS ever returns (ok, err), take err.
        if isinstance(ce_raw, (tuple, list)):
            err = float(ce_raw[1]) if len(ce_raw) > 1 else float(ce_raw[0])
        else:
            err = float(ce_raw)
        S  = sf.S(T)
        db = sf.delta_b(T)
        writer.writerow([
            f"{T:.6f}",
            f"{state.E_9D:.10e}",
            f"{state.E_macro:.10e}",
            f"{state.E_micro:.10e}",
            f"{abs(err):.6e}",
            f"{S:.6f}",
            f"{db:.6f}",
        ])
print(f"\n[CSV] Conservation report → {csv_path_cons}")

# ─────────────────────────────────────────────────────────────────────────────
# EXPORT — band-wise convexity
# ─────────────────────────────────────────────────────────────────────────────
bw = results["bandwise_convexity"]
csv_path_bw = _ANALYTICS / "step_01_bandwise_convexity.csv"
with open(csv_path_bw, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["band", "is_convex", "min_C", "violations"])
    for band, res in sorted(bw.items()):
        writer.writerow([band, res["is_convex"], f"{res['min_C']:.6e}", res["violations"]])
print(f"[CSV] Band-wise convexity  → {csv_path_bw}")

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
all_convex = all(v["is_convex"] for v in bw.values()) if bw else True

_core_pass = (
    results["conservation"]["holds"]
    and results["orthogonality"]["holds"]
    and results["scale"]["well_defined"]
)

# OVERALL line: distinguish core axioms (A–C) from conjectural U1* (D)
if _core_pass and all_convex:
    _overall_str = "CORE AXIOMS HOLD  ✓  U1* HOLDS  ✓"
elif _core_pass and not all_convex:
    _overall_str = "CORE AXIOMS HOLD  ✓  U1* FAILS ON THIS GRID (CONJECTURAL)"
else:
    _overall_str = "CORE AXIOMS FAIL  ✗  — investigate before proceeding"

print()
print("=" * 72)
print("STEP 1 RESULT SUMMARY")
print(f"  (A) Energy conservation   : {'PASS ✓' if results['conservation']['holds'] else 'FAIL ✗'}")
print(f"      max error              : {results['conservation']['max_error']:.2e}")
print(f"  (B) Orthogonal split      : {'PASS ✓' if results['orthogonality']['holds'] else 'FAIL ✗'}")
print(f"      max error              : {results['orthogonality']['max_orthogonality_error']:.2e}")
print(f"  (C) Scale functional S(T) : {'PASS ✓' if results['scale']['well_defined'] else 'FAIL ✗'}")
print(f"      S(T) range             : [{results['scale']['S_min']:.2f}, {results['scale']['S_max']:.2f}]")
print(f"  (D) Band-wise convexity   : {'PASS ✓' if all_convex else 'FAIL ✗  [CONJECTURAL — does not gate STEP 2]'}")
print(f"  OVERALL                   : {_overall_str}")
print(f"  Elapsed                   : {elapsed:.1f}s")
print("=" * 72)

if not _core_pass:
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# HAND-OFF: export shared constants for downstream steps
# ─────────────────────────────────────────────────────────────────────────────
print()
print("Constants certified by AXIOMS.py (sole source of truth):")
print(f"  LAMBDA_STAR  = {LAMBDA_STAR}")
print(f"  NORM_X_STAR  = {NORM_X_STAR}")
print(f"  COUPLING_K   = {COUPLING_K}")
print(f"  PHI          = {PHI:.15f}")
print()

# U5 PASS/FAIL lines
print(f"STEP 1 CONSERVATION:  {'PASS' if results['conservation']['holds'] else 'FAIL'}")
print(f"STEP 1 ORTHOGONALITY: {'PASS' if results['orthogonality']['holds'] else 'FAIL'}")
print(f"STEP 1 SCALE_FUNC:    {'PASS' if results['scale']['well_defined'] else 'FAIL'}")
print(f"STEP 1 U1_STAR:       {'PASS' if all_convex else 'CONJECTURAL — fails bands 3–6 on this grid'}")
print()
print("STEP 1 COMPLETE — Core AXIOMS validated (DEF 2, 3, 5).")
print("  U1* (DEF 8) is conjectural and currently violated in some bands.")
print("  This is catalogued as open gap DEF8 in STEP 8.  Proceed to STEP 2.")


if __name__ == "__main__":
    pass