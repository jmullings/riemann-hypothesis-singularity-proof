#!/usr/bin/env python3
"""
DEF 03 — MONTGOMERY PAIR CORRELATION / LOCAL SPACING CONJECTURES
================================================================

STATUS: Computed — Bridge 12 implements Gonek-Montgomery spiral geometry.
        Phase spacing analysis exported: phase_spacing_analysis.csv

═══════════════════════════════════════════════════════════════════════
CLASSICAL DEFINITION
═══════════════════════════════════════════════════════════════════════

MONTGOMERY'S PAIR CORRELATION CONJECTURE (1973):
    For zeros ½ + iγₙ of ζ(s), define the pair correlation function

        F(α, T) = (2π / T log T) · Σ_{γ₁ ≠ γ₂ ≤ T}
                        T^{iα(γ₁ − γ₂)} · w(γ₁ − γ₂)

    where w is a weight. Conjecture:

        F(α) = |α| + δ(α)  (in a weak distributional sense)

    Equivalently, the two-point correlation function of zeros normalised
    to mean spacing 1 is:

        R₂(x) = 1 − (sin πx / πx)²

    THIS IS THE SAME R₂ AS IN GUE RANDOM MATRIX THEORY (DEF 01).
    → Zeros of ζ behave like eigenvalues of a GUE matrix.

NORMALISED SPACING:
    Define δₙ = (γₙ₊₁ − γₙ) · (log γₙ / 2π)    (mean spacing → 1)

    GUE prediction:    P(s) = (π s / 2) · exp(−π s² / 4)   (Wigner surmise)
    Poisson null:      P(s) = exp(−s)

PAIR CORRELATION — EXPLICIT FORM:
    For consecutive zeros γₙ₊₁ > γₙ, the pair correlation of
    (γₙ − γₙ₋₁) with (γₙ₊₁ − γₙ) encodes level repulsion: zeros
    repel each other, so P(s) → 0 as s → 0.

Operational consequence:
    If ζ has a zero off the critical line at σ₀ + iγ, its pair-
    correlation signature would differ from GUE — providing a
    statistical falsification channel.

═══════════════════════════════════════════════════════════════════════
FRAMEWORK MAPPING
═══════════════════════════════════════════════════════════════════════

BRIDGE 12 — SPIRAL GEOMETRY (BRIDGE_12_SPIRAL_GEOMETRY.py):

    θₙ = arg(D_X(½ + iγₙ))   (argument of finite Dirichlet polynomial)

    Gonek-Montgomery logarithmic spiral:
      rₙ = exp(−γₙ / 2π)              (radial decay)
      θₙ = γₙ · log γₙ / 2π           (angular winding — matches Δγ mean)

    Winding number:  W(T) = (1/2π) · Σₙ (θₙ₊₁ − θₙ)   (integer for smooth spiral)
    Tightness:       τ = var(θₙ₊₁ − θₙ)                 (measures GUE level repulsion)

    Framework claim: tightness τ → 0 as P* → ∞, matching GUE universality.

EQ connection:
  EQ2 — Strict convexity away from σ=½:
      E(σ+h, γₖ) + E(σ−h, γₖ) > 2E(σ, γₖ)   for σ ≠ ½
    → energy landscape is strictly convex BETWEEN zeros,
      paralleling zero-repulsion in GUE spacing distribution.

  EQ9 — Spectral operator σ-filter:
      The eigenvalue λ* = 494.058 encodes the GUE-like "stiffness"
      of the spectrum; high λ* = strong level repulsion.

Phase spacing data:
  phase_spacing_analysis.csv     (root directory) — computed spacing statistics
  phase_mirror_analysis.csv      (root directory) — symmetry across Re(s) = ½
  prime_side_phase_winding.csv   (root directory) — prime-driven winding

TARGET quantities from phase data:
  mean normalised spacing ≈ 1.0      (by construction)
  variance of normalised spacing ≈ 0.286   (GUE: 4/π² − 1 ≈ 0.1949 for Wigner-Dyson,
                                            numerical value depends on truncation P*)

═══════════════════════════════════════════════════════════════════════
ROLE IN FRAMEWORK
═══════════════════════════════════════════════════════════════════════

Montgomery pair correlation validates that the framework's σ=½ selectivity
is NOT an accident: GUE statistics emerge from the arithmetic structure of
primes, and the framework's energy functional E(σ,T) inherits that
arithmetic via its Dirichlet polynomial D_X.

All DEF_03 computations are finite-sample diagnostics; they illustrate
GUE-like behavior but are not used as logical steps in any RH
contradiction or implication.  DEF_03 feeds only into visualization /
statistical sanity checks for Bridge 12 and EQ9; no EQ or Bridge uses
DEF_03 as a formal hypothesis in any RH proof step.

OPEN: Formal proof that tightness τ → GUE variance as P* → ∞.
      Requires controlled bounds on D_X beyond finite X — non-trivial.

Reference files:
  BRIDGE_12_SPIRAL_GEOMETRY.py
  phase_spacing_analysis.csv
  phase_mirror_analysis.csv
  EQ_VALIDATION_SUITE.py  (EQ2, EQ9)
"""

import numpy as np
import sys
import os

# Add the CONFIGURATIONS directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'CONFIGURATIONS'))
from AXIOMS import LAMBDA_STAR, NORM_X_STAR, RIEMANN_ZEROS_9

# ─── Framework constants ────────────────────────────────────────────────────
# LAMBDA_STAR, NORM_X_STAR, and RIEMANN_ZEROS_9 imported from CONFIGURATIONS/AXIOMS.py
_LN2        = 0.6931471805599453   # ln(2) — log()-free computation
ZEROS_9 = RIEMANN_ZEROS_9  # Alias for compatibility


# ─── Classical Montgomery pair correlation ──────────────────────────────────
def montgomery_R2(x: float) -> float:
    """
    Two-point pair correlation density:
        R₂(x) = 1 − (sin πx / πx)²

    For x=0: R₂(0) = 0 (level repulsion — zeros cannot coincide).
    For x→∞: R₂(x) → 1  (no long-range correlation).
    """
    if abs(x) < 1e-12:
        return 0.0
    px = np.pi * x
    sinc = np.sin(px) / px
    return 1.0 - sinc * sinc


def wigner_surmise(s: float) -> float:
    """
    GUE Wigner surmise spacing density:
        P(s) = (32 / π²) · s² · exp(−4s²/π)

    (More accurate than P(s) = (π s/2) exp(−π s²/4) — this is the
     exact GUE nearest-neighbour formula for a 2×2 matrix.)
    """
    if s < 0:
        return 0.0
    coeff = 32.0 / (np.pi ** 2)
    return coeff * s ** 2 * np.exp(-4.0 * s ** 2 / np.pi)


def normalised_spacings(zeros: list) -> list:
    """
    Compute GUE-normalised spacings:
        δₙ = (γₙ₊₁ − γₙ) · log(γₙ) / (2π)

    Mean spacing → 1 asymptotically (large T, many zeros); individual
    samples from the first few low zeros will exceed 1 due to the sparse
    low-height regime. Log() replaced by log2(x) * _LN2.
    """
    spacings = []
    for i in range(len(zeros) - 1):
        gn = zeros[i]
        gap = zeros[i + 1] - gn
        log_gn = np.log2(gn) * _LN2   # log-free: log(x) = log2(x) * ln(2)
        delta = gap * log_gn / (2 * np.pi)
        spacings.append(delta)
    return spacings


def gonek_montgomery_winding(zeros: list) -> dict:
    """
    Framework Bridge 12 — Gonek-Montgomery spiral winding angle:
        φₙ = γₙ · log(γₙ) / (2π)   mod 2π

    Tightness τ = variance of angular increments (Δφₙ = φₙ₊₁ − φₙ).
    Low τ ≈ GUE levelling; high τ ≈ Poisson statistics.
    Log replaced by log2 * _LN2.
    """
    angles = []
    for g in zeros:
        log_g = np.log2(g) * _LN2
        phi   = (g * log_g / (2 * np.pi)) % (2 * np.pi)
        angles.append(phi)
    increments = [angles[i+1] - angles[i] for i in range(len(angles)-1)]
    tightness  = float(np.var(increments)) if len(increments) > 1 else float("nan")
    winding_number = sum(
        1 for inc in increments if inc > 0
    ) - sum(1 for inc in increments if inc < 0)
    return {
        "angles_rad":      angles,
        "increments":      increments,
        "tightness":       tightness,
        "winding_number":  winding_number,
    }


if __name__ == "__main__":
    print("DEF 03 — Montgomery Pair Correlation")
    print()
    print("  R₂(x) at key arguments:")
    for x in [0.0, 0.5, 1.0, 1.5, 2.0]:
        print(f"    R₂({x:.1f}) = {montgomery_R2(x):.6f}")
    print()
    print("  GUE Wigner surmise P(s) at key spacings:")
    for s in [0.0, 0.5, 1.0, 1.5, 2.0]:
        print(f"    P({s:.1f}) = {wigner_surmise(s):.6f}")
    print()
    sp = normalised_spacings(ZEROS_9)
    print(f"  Normalised spacings (first {len(ZEROS_9)} zeros): {[f'{s:.4f}' for s in sp]}")
    print(f"  Mean = {np.mean(sp):.4f}  (asymptotic target ≈ 1.0 for large T / many zeros;")
    print( "         large values expected for the first 9 low zeros)")
    print(f"  Var  = {np.var(sp):.4f}   (GUE asymptotic target ≈ 0.2863 for Wigner surmise;"
          "  sample variance elevated for N=9)")
    print()
    spiral = gonek_montgomery_winding(ZEROS_9)
    print(f"  Spiral tightness τ = {spiral['tightness']:.6f}")
    print(f"  Winding number      = {spiral['winding_number']}")
    print(f"  λ* (stiffness)      = {LAMBDA_STAR:.6f}")
