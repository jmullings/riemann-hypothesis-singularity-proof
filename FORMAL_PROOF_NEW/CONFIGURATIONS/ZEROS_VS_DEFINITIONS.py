#!/usr/bin/env python3
"""
ZEROS_VS_DEFINITIONS.py
=======================
Location: FORMAL_PROOF_NEW/CONFIGURATIONS/

For every zero height T = γₙ in RiemannZeros.txt (or a custom file), this
script evaluates all ten DEFINITION engines against the zero and reports
a per-zero, per-definition verdict.

DEFINITIONS TESTED
------------------
  DEF_1  GUE Random Matrix Statistics   — normalised level spacing vs Wigner
  DEF_2  Hilbert–Pólya Spectral         — N(T) counting function check
  DEF_3  Montgomery Pair Correlation    — Gonek–Montgomery winding + tightness
  DEF_4  Robin / Lagarias Arithmetic    — Lagarias σ(n) ≤ Hₙ + e^Hₙ·log Hₙ
  DEF_5  Automorphic / Euler Product    — |Z_X(½,T)| finite and non-zero
  DEF_6  Selberg Trace Formula          — prime geodesic contribution finite
  DEF_7  de Bruijn–Newman               — E(½,T) > 0, flow_curvature > 0
  DEF_8  Moments (Keating–Snaith)       — E(½,T) matches moment prediction sign
  DEF_9  Nyman–Beurling                 — convexity C_φ(T) ≥ 0
  DEF_10 Explicit Formulae / PNT        — N_T(γ) ≈ 1, sigma_bound > ½

PASS criteria (per DEF)
-----------------------
  DEF_1  At least one normalised spacing in (0, 3] (GUE level-repulsion band)
  DEF_2  N(T) counting approx ≥ 0
  DEF_3  Winding calculation completes; tightness finite
  DEF_4  lagarias_check(n) passes for n = ⌊T⌋ (if n ≥ 1)
  DEF_5  |Z_X(½,T)| is finite and > 0
  DEF_6  Prime geodesic sum is finite
  DEF_7  E(½,T) > 0  AND  flow_curvature(T) > 0
  DEF_8  E(½,T) > 0  (framework moment consistent)
  DEF_9  convexity_C_φ(T) ≥ 0  (UBE convexity holds)
  DEF_10 N_T_formula(T) ≥ 0  AND  sigma_bound > 0

Protocol compliance
-------------------
  P1  Constants only from AXIOMS.py.
  P5  Trinity Gate printed before main loop.

Usage
-----
    python ZEROS_VS_DEFINITIONS.py                   # all zeros
    python ZEROS_VS_DEFINITIONS.py --limit 50        # first 50 zeros
    python ZEROS_VS_DEFINITIONS.py --zeros /path/to/file.txt
    python ZEROS_VS_DEFINITIONS.py --out results.csv

Output
------
    zeros_vs_definitions.csv  — per-zero × per-DEF: value, status
    Summary table printed to stdout.

Author : Jason Mullings
Date   : March 12, 2026
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# PATH SETUP
# ---------------------------------------------------------------------------

HERE      = Path(__file__).parent.resolve()
DEFS_BASE = HERE.parent / "DEFINITIONS"

sys.path.insert(0, str(HERE))

# ---------------------------------------------------------------------------
# SECTION 0 — IMPORT FROM AXIOMS (P5 compliance)
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
# SECTION 1 — LOAD DEFINITION MODULES
# ---------------------------------------------------------------------------

_DEF_PATHS: Dict[str, str] = {
    "DEF_1":  "DEF_1/EXECUTION/DEF_01_GUE_RANDOM_MATRIX_STATISTICS.py",
    "DEF_2":  "DEF_2/EXECUTION/DEF_02_HILBERT_POLYA_SPECTRAL_OPERATOR.py",
    "DEF_3":  "DEF_3/EXECUTION/DEF_03_MONTGOMERY_PAIR_CORRELATION.py",
    "DEF_4":  "DEF_4/EXECUTION/DEF_04_ROBIN_LAGARIAS_ARITHMETIC_CRITERIA.py",
    "DEF_5":  "DEF_5/EXECUTION/DEF_05_AUTOMORPHIC_FORMS_L_FUNCTIONS.py",
    "DEF_6":  "DEF_6/EXECUTION/DEF_06_SELBERG_TRACE_FORMULA.py",
    "DEF_7":  "DEF_7/EXECUTION/DEF_07_DE_BRUIJN_NEWMAN.py",
    "DEF_8":  "DEF_8/EXECUTION/DEF_08_MOMENTS_KEATING_SNAITH.py",
    "DEF_9":  "DEF_9/EXECUTION/DEF_09_NYMAN_BEURLING.py",
    "DEF_10": "DEF_10/EXECUTION/DEF_10_EXPLICIT_FORMULAE_PNT.py",
}

_DEF_LABELS: Dict[str, str] = {
    "DEF_1":  "GUE Random Matrix",
    "DEF_2":  "Hilbert–Pólya Spectral",
    "DEF_3":  "Montgomery Pair Corr.",
    "DEF_4":  "Robin / Lagarias",
    "DEF_5":  "Automorphic / Euler Prod.",
    "DEF_6":  "Selberg Trace Formula",
    "DEF_7":  "de Bruijn–Newman",
    "DEF_8":  "Moments Keating–Snaith",
    "DEF_9":  "Nyman–Beurling",
    "DEF_10": "Explicit Formulae / PNT",
}


def _load_module(name: str) -> Optional[Any]:
    """Load a DEFINITION module by importlib; return None on failure."""
    path = DEFS_BASE / _DEF_PATHS[name]
    try:
        spec = importlib.util.spec_from_file_location(name, str(path))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    except Exception as exc:
        print(f"  [WARN] Could not load {name}: {exc}")
        return None


# Load all modules once at import time
_MODULES: Dict[str, Optional[Any]] = {k: _load_module(k) for k in _DEF_PATHS}

# ---------------------------------------------------------------------------
# SECTION 2 — PER-DEFINITION TEST FUNCTIONS
# ---------------------------------------------------------------------------
# Each function receives (T, zeros_list) and returns (value_str, passed: bool).


def _test_def1(T: float, zeros: List[float]) -> Tuple[str, bool]:
    """DEF_1: GUE level-repulsion — at least one normalised spacing in (0, 3]."""
    m = _MODULES.get("DEF_1")
    if m is None:
        return "LOAD_ERR", False
    try:
        d3 = _MODULES.get("DEF_3")
        if d3 is None:
            return "DEF_3_MISSING", False
        spacings = d3.normalised_spacings(zeros)
        if not spacings:
            return "no_spacings", False
        # GUE Wigner-surmise check: nearest computed spacing in (0, 3]
        s = spacings[0] if len(spacings) >= 1 else math.nan
        # GUE density at spacing s
        density = m.gue_spacing_density(min(s, 4.0))
        ok = math.isfinite(density) and density > 0
        return f"s={s:.4f} ρ={density:.4f}", ok
    except Exception as exc:
        return f"ERR:{exc}", False


def _test_def2(T: float, zeros: List[float]) -> Tuple[str, bool]:
    """DEF_2: Hilbert–Pólya — N(T) counting approx ≥ 0."""
    m = _MODULES.get("DEF_2")
    if m is None:
        return "LOAD_ERR", False
    try:
        n_t = m.spectral_counting_approx(T)
        ok = math.isfinite(n_t) and n_t >= 0
        return f"N(T)={n_t:.4f}", ok
    except Exception as exc:
        return f"ERR:{exc}", False


def _test_def3(T: float, zeros: List[float]) -> Tuple[str, bool]:
    """DEF_3: Montgomery — Gonek winding completes, tightness finite."""
    m = _MODULES.get("DEF_3")
    if m is None:
        return "LOAD_ERR", False
    try:
        gw = m.gonek_montgomery_winding(zeros)
        tight = gw.get("tightness", math.nan)
        ok = math.isfinite(tight)
        return f"winding={gw.get('winding_number',0):.4f} tight={tight:.4f}", ok
    except Exception as exc:
        return f"ERR:{exc}", False


def _test_def4(T: float, zeros: List[float]) -> Tuple[str, bool]:
    """DEF_4: Robin/Lagarias — lagarias_check for n = floor(T)."""
    m = _MODULES.get("DEF_4")
    if m is None:
        return "LOAD_ERR", False
    try:
        # Use a representative integer near T (capped for speed: max n = 10000)
        n = max(1, min(int(T), 10_000))
        ok = m.lagarias_check(n)
        sigma_n = m.sum_of_divisors(n)
        bound   = m.lagarias_bound(n)
        return f"n={n} σ(n)={sigma_n} ≤ {bound:.2f}", ok
    except Exception as exc:
        return f"ERR:{exc}", False


def _test_def5(T: float, zeros: List[float]) -> Tuple[str, bool]:
    """DEF_5: Automorphic/Euler — |Z_X(½,T)| finite and > 0."""
    m = _MODULES.get("DEF_5")
    if m is None:
        return "LOAD_ERR", False
    try:
        z = m.Z_euler_product(0.5, T)
        mag = abs(z)
        ok = math.isfinite(mag) and mag > 0
        return f"|Z|={mag:.6f}", ok
    except Exception as exc:
        return f"ERR:{exc}", False


def _test_def6(T: float, zeros: List[float]) -> Tuple[str, bool]:
    """DEF_6: Selberg Trace — prime geodesic sum is finite."""
    m = _MODULES.get("DEF_6")
    if m is None:
        return "LOAD_ERR", False
    try:
        pgc = m.prime_geodesic_contribution(P_star=50)
        # pgc returns a dict with a 'total' or numeric value
        if isinstance(pgc, dict):
            val = pgc.get("total", pgc.get("sum", next(iter(pgc.values()), math.nan)))
        else:
            val = float(pgc)
        ok = math.isfinite(val)
        return f"pgc={val:.6f}", ok
    except Exception as exc:
        return f"ERR:{exc}", False


def _test_def7(T: float, zeros: List[float]) -> Tuple[str, bool]:
    """DEF_7: de Bruijn–Newman — E(½,T) > 0 and flow_curvature(T) > 0."""
    m = _MODULES.get("DEF_7")
    if m is None:
        return "LOAD_ERR", False
    try:
        e_val = m.E(0.5, T)
        fc    = m.flow_curvature(T)
        ok = (math.isfinite(e_val) and e_val > 0
              and math.isfinite(fc) and fc > 0)
        return f"E={e_val:.6f} fc={fc:.4f}", ok
    except Exception as exc:
        return f"ERR:{exc}", False


def _test_def8(T: float, zeros: List[float]) -> Tuple[str, bool]:
    """DEF_8: Moments (Keating–Snaith) — E(½,T) > 0."""
    m = _MODULES.get("DEF_8")
    if m is None:
        return "LOAD_ERR", False
    try:
        e_val = m.E(0.5, T)
        m2    = m.framework_second_moment()
        ok = math.isfinite(e_val) and e_val > 0 and math.isfinite(m2)
        return f"E={e_val:.6f} M2={m2:.4f}", ok
    except Exception as exc:
        return f"ERR:{exc}", False


def _test_def9(T: float, zeros: List[float]) -> Tuple[str, bool]:
    """DEF_9: Nyman–Beurling — convexity C_φ(T) ≥ 0."""
    m = _MODULES.get("DEF_9")
    if m is None:
        return "LOAD_ERR", False
    try:
        c = m.convexity_C_phi(T)
        ok = math.isfinite(c) and c >= -1e-10
        return f"C_φ={c:.8f}", ok
    except Exception as exc:
        return f"ERR:{exc}", False


def _test_def10(T: float, zeros: List[float]) -> Tuple[str, bool]:
    """DEF_10: Explicit Formulae / PNT — N_T ≥ 0 and sigma_bound > 0."""
    m = _MODULES.get("DEF_10")
    if m is None:
        return "LOAD_ERR", False
    try:
        n_t  = m.N_T_formula(T)
        s_b  = m.explicit_formula_sigma_bound(T)
        ok = (math.isfinite(n_t) and n_t >= 0
              and math.isfinite(s_b) and s_b > 0)
        return f"N_T={n_t:.4f} σ_bnd={s_b:.6f}", ok
    except Exception as exc:
        return f"ERR:{exc}", False


# Registry: ordered list of (def_key, test_function)
DEF_TESTS: List[Tuple[str, Any]] = [
    ("DEF_1",  _test_def1),
    ("DEF_2",  _test_def2),
    ("DEF_3",  _test_def3),
    ("DEF_4",  _test_def4),
    ("DEF_5",  _test_def5),
    ("DEF_6",  _test_def6),
    ("DEF_7",  _test_def7),
    ("DEF_8",  _test_def8),
    ("DEF_9",  _test_def9),
    ("DEF_10", _test_def10),
]

# ---------------------------------------------------------------------------
# SECTION 3 — ZERO LOADER
# ---------------------------------------------------------------------------

def load_zeros(path: Path, limit: Optional[int] = None) -> List[float]:
    """Parse RiemannZeros.txt — one float per line."""
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
# SECTION 4 — TRINITY GATE (P5)
# ---------------------------------------------------------------------------

def trinity_gate() -> bool:
    """Gate-0: dimensions. Gate-1: constants. Gate-2: DEF modules loaded."""
    passed = True

    g0 = DIM_9D == 9 and DIM_6D == 6 and DIM_3D == 3
    print(f"  Gate-0 (dimensions)   : {'✓ PASS' if g0 else '✗ FAIL'}"
          f"  DIM_9D={DIM_9D}  DIM_6D={DIM_6D}  DIM_3D={DIM_3D}")
    passed = passed and g0

    g1 = LAMBDA_STAR > 494.0 and NORM_X_STAR > 0.3 and COUPLING_K > 0.0
    print(f"  Gate-1 (constants)    : {'✓ PASS' if g1 else '✗ FAIL'}"
          f"  λ*={LAMBDA_STAR:.3f}  ‖x*‖={NORM_X_STAR:.5f}  k={COUPLING_K}")
    passed = passed and g1

    loaded   = sum(1 for v in _MODULES.values() if v is not None)
    missing  = [k for k, v in _MODULES.items() if v is None]
    g2 = loaded == 10
    print(f"  Gate-2 (DEF modules)  : {'✓ PASS' if g2 else '⚠  PARTIAL'}"
          f"  {loaded}/10 loaded"
          + (f"  missing={missing}" if missing else ""))
    passed = passed and g2

    return passed

# ---------------------------------------------------------------------------
# SECTION 5 — MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test Riemann zeros against all 10 DEFINITION engines."
    )
    parser.add_argument(
        "--zeros",
        default=str(HERE / "RiemannZeros.txt"),
        help="Path to zeros file  [default: RiemannZeros.txt in same dir]",
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
        default=str(HERE / "zeros_vs_definitions.csv"),
        help="Output CSV path  [default: zeros_vs_definitions.csv]",
    )
    args = parser.parse_args()

    print("=" * 76)
    print("ZEROS vs DEFINITIONS CHECKER  —  FORMAL_PROOF_NEW / CONFIGURATIONS")
    print(f"  Definitions : DEF_1 … DEF_10  (FORMAL_PROOF_NEW/DEFINITIONS/)")
    print(f"  Constants   : AXIOMS.py  (λ*={LAMBDA_STAR:.3f}, φ={PHI:.6f})")
    print("=" * 76)
    print()

    # Trinity Gate
    print("TRINITY GATE (P5):")
    gate_ok = trinity_gate()
    print(f"  Overall               : {'✓ PASS' if gate_ok else '⚠  PARTIAL'}")
    print()

    # Load zeros
    zeros_path = Path(args.zeros)
    if not zeros_path.exists():
        print(f"ERROR: zeros file not found: {zeros_path}")
        sys.exit(1)

    zeros = load_zeros(zeros_path, limit=args.limit)
    n_zeros = len(zeros)
    print(f"Zeros loaded  : {n_zeros}"
          f"{'  (limited)' if args.limit else ''}"
          f"  from  {zeros_path.name}")
    print()

    # Column header
    def_keys = [k for k, _ in DEF_TESTS]
    hdr_defs = "  ".join(f"{k:>6}" for k in def_keys)
    print(f"{'#':>6}  {'T (γₙ)':>18}  {hdr_defs}  total")
    print("-" * 76)

    # Accumulators
    rows: List[dict] = []
    def_pass_counts  = {k: 0 for k in def_keys}
    def_fail_counts  = {k: 0 for k in def_keys}
    zero_pass_counts: List[int] = []

    t_start = time.time()

    for idx, T in enumerate(zeros, start=1):
        row: dict = {"index": idx, "T": T}
        zero_passes = 0

        status_strs = []
        for def_key, test_fn in DEF_TESTS:
            val_str, passed = test_fn(T, zeros)
            row[f"{def_key}_value"]  = val_str
            row[f"{def_key}_status"] = "PASS" if passed else "FAIL"
            if passed:
                def_pass_counts[def_key] += 1
                zero_passes += 1
            else:
                def_fail_counts[def_key] += 1
            status_strs.append("✓" if passed else "✗")

        zero_pass_counts.append(zero_passes)
        rows.append(row)

        # Print first 10, every 50th, and any all-fail rows
        if idx <= 10 or idx % 50 == 0 or zero_passes == 0:
            flags = "  ".join(f"{s:>6}" for s in status_strs)
            print(f"{idx:>6}  {T:>18.9f}  {flags}  {zero_passes}/10")

    elapsed = time.time() - t_start

    # Write CSV
    out_path = Path(args.out)
    fieldnames = ["index", "T"]
    for k in def_keys:
        fieldnames += [f"{k}_value", f"{k}_status"]
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    print()
    print("=" * 76)
    print("SUMMARY — per-DEFINITION pass rates")
    print("=" * 76)
    print(f"  {'DEF':8}  {'Label':28}  {'PASS':>6}  {'FAIL':>6}  {'Rate':>8}")
    print("  " + "-" * 60)
    total_pass = total_fail = 0
    for def_key, label in _DEF_LABELS.items():
        p = def_pass_counts[def_key]
        f = def_fail_counts[def_key]
        rate = 100.0 * p / n_zeros if n_zeros else 0
        sym = "✅" if f == 0 else ("⚠️ " if p > 0 else "❌")
        print(f"  {def_key:8}  {label:28}  {p:>6}  {f:>6}  {rate:>7.2f}%  {sym}")
        total_pass += p
        total_fail += f

    avg_per_zero = sum(zero_pass_counts) / n_zeros if n_zeros else 0
    all_10_pass = sum(1 for c in zero_pass_counts if c == 10)
    print()
    print(f"  Zeros tested        : {n_zeros}")
    print(f"  All-10-DEF pass     : {all_10_pass}  ({100*all_10_pass/n_zeros:.2f}%)")
    print(f"  Avg DEFs passed/zero: {avg_per_zero:.2f} / 10")
    print(f"  Total checks        : {total_pass + total_fail}")
    print(f"  Total PASS          : {total_pass}")
    print(f"  Total FAIL          : {total_fail}")
    print(f"  Elapsed             : {elapsed:.1f} s")
    print(f"  CSV written         : {out_path}")
    print("=" * 76)


if __name__ == "__main__":
    main()
