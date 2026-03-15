#!/usr/bin/env python3
"""
DEF 04 — ROBIN / LAGARIAS ARITHMETIC INEQUALITY CRITERIA
=========================================================

STATUS: Computed — Bridge 9 implements both inequalities.
        BRIDGE_9_ESPINOSA.py provides δ(n) = f(n) − 1, f(n) verification.

═══════════════════════════════════════════════════════════════════════
CLASSICAL DEFINITION
═══════════════════════════════════════════════════════════════════════

ROBIN'S CRITERION (1984):
    Let σ(n) = Σ_{d|n} d   (sum of divisors).
    Let γ = 0.5772156649...  (Euler–Mascheroni constant).

    Theorem (Robin 1984):
        RH  ⟺  σ(n) < e^γ · n · log log n   for all n ≥ 5041.

    The bound e^γ · n · log log n grows slightly faster than σ(n)
    for almost all n; equality / violation is linked to highly composite
    numbers (Ramanujan).

LAGARIAS'S CRITERION (2002):
    Let Hₙ = 1 + 1/2 + ... + 1/n   (harmonic number).

    Theorem (Lagarias 2002):
        RH  ⟺  σ(n) ≤ Hₙ + e^{Hₙ} · log Hₙ   for all n ≥ 1.

    This is an element-wise inequality: each n independently
    constrains the zeros of ζ.

GRONWALL'S THEOREM (background):
    lim sup_{n→∞}  σ(n) / (n log log n)  =  e^γ

    So the Robin bound is the tightest possible constant above the
    lim sup; any violation would require a zero off σ=½.

Robin's criterion is equivalent to RH only for all n ≥ 5041; values
below 5041 are outside the theorem's range and may legitimately violate
the inequality without contradicting RH.

ESPINOSA RESIDUAL (Bridge 9 extension):
    Define the normalised excess:
        δ(n) = f(n) − 1   where   f(n) = σ(n) / (e^γ · n · log log n)

    Robin positivity:  δ(n) < 0 for all n ≥ 5041  ↔  RH.
    δ(n) → 0 as n → ∞ by Gronwall (this is the tight case).

═══════════════════════════════════════════════════════════════════════
FRAMEWORK MAPPING
═══════════════════════════════════════════════════════════════════════

BRIDGE 9 — ESPINOSA (BRIDGE_9_ESPINOSA.py):

    The framework computes:
        f(n) = σ(n) / (e^γ · n · log log n)
        δ(n) = f(n) − 1                    (Espinosa violation metric)

    For highly composite n (e.g. 720720, 5040), f(n) must remain < 1
    to be consistent with RH; f > 1 would be a Robin counterexample.

    Connection to σ=½ selectivity:
        The energy functional E(σ,T) restricted to the Euler product
        regime satisfies:
            E(σ, γₙ) ≫ E(½, γₙ)   for σ < ½      (below critical line)
            E(σ, γₙ) <  E(½, γₙ)   for σ > ½      (above critical line — monotone)
        → σ=½ is the threshold, matching Robin's e^γ threshold.

    Specifically:
        σ(n) < e^γ · n · log log n  CORRESPONDS to  D_X(½+iT) being
        the extremal point of the finite Euler product energy.

EQ10 — FINITE EULER PRODUCT FILTER:
    Z(σ, T) = Π_{p≤P*} Σ_{k≥0} p^{-kσ} · e^{−ikT·ln p}
            = Π_{p≤P*} 1 / (1 − p^{−σ} · e^{−iT·ln p})

    This is the TRUNCATED Euler product for ζ(σ+iT).

    Robin criterion ↔ EQ10:
        |Z(½, T)|² must be bounded above by the Robin constant e^γ
        times an arithmetic correction → EQ10 tests this bound
        at each zero height.

Bitsize axiom connection:
    BITSIZE_OFFSET = 2.96   (δ = log₂(7.8) — prime threshold)
    Primes p > 7.8  →  log₂(p) > BITSIZE_OFFSET  →  active in OFFSET_B2
    Robin's inequality involves LARGE primes most critically (high n),
    which is exactly the Axiom 1* offset regime.

    σ(n) growth is dominated by n with many SMALL prime factors
    (smooth numbers), consistent with the P* truncation in Bridge 9/11.

═══════════════════════════════════════════════════════════════════════
ROLE IN FRAMEWORK
═══════════════════════════════════════════════════════════════════════

Robin provides an arithmetic NECESSARY CONDITION: if any violation of
δ(n) < 0 is found for n ≥ 5041, RH is FALSE. The framework's EQ10
encodes the analytic version of this at the spectral level.

All DEF_04 computations are finite‑n diagnostics; they illustrate
Robin/Lagarias behavior but are not used as formal steps in any RH
proof or contradiction argument.

OPEN: Extend from finite P* to the full Euler product (P* → ∞).
      Show δ(n) ≡ f(n)−1 ≤ 0 implies E(σ,·) convexity.

Reference files:
  BRIDGE_9_ESPINOSA.py
  EQ_VALIDATION_SUITE.py  (EQ10)
"""

import numpy as np
import sys
import os

# Add the CONFIGURATIONS directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'CONFIGURATIONS'))
from AXIOMS import LAMBDA_STAR, NORM_X_STAR

# ─── Framework constants ─────────────────────────────────────────────────────
# LAMBDA_STAR and NORM_X_STAR imported from CONFIGURATIONS/AXIOMS.py
BITSIZE_OFFSET = 2.96     # δ = log₂(7.8), Axiom 1*
ALPHA          = 0.864    # power law exponent, Axiom 5*
_LN2           = 0.6931471805599453   # ln(2) — log()-free

EULER_MASCHERONI = 0.5772156649015328606065120900824024310422


def sum_of_divisors(n: int) -> int:
    """σ(n) = sum of all positive divisors of n."""
    total = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total


def robin_f(n: int) -> float:
    """
    f(n) = σ(n) / (e^γ · n · log log n)

    Robin's criterion: f(n) < 1 for all n ≥ 5041  ↔  RH.
    log log n computed log()-free: log(log(n)) = log2(log2(n)) * _LN2² / _LN2
      = log2(n) * _LN2 wrapped twice.
    """
    if n < 3:
        return float("nan")
    s = sum_of_divisors(n)
    log_n     = np.log2(n) * _LN2               # ln(n) = log2(n) * ln(2)
    if log_n <= 0:
        return float("nan")
    log_log_n = np.log2(log_n) * _LN2           # ln(ln(n))
    if log_log_n <= 0:
        return float("nan")
    denom = np.exp(EULER_MASCHERONI) * n * log_log_n
    return s / denom


def robin_delta(n: int) -> float:
    """δ(n) = f(n) − 1.  Robin satisfied: δ(n) < 0."""
    return robin_f(n) - 1.0


def lagarias_hn(n: int) -> float:
    """Harmonic number Hₙ = 1 + 1/2 + ... + 1/n."""
    return sum(1.0 / k for k in range(1, n + 1))


def lagarias_bound(n: int) -> float:
    """
    Lagarias upper bound: Hₙ + exp(Hₙ) · log(Hₙ).

    Lagarias criterion: σ(n) ≤ this bound for all n ≥ 1  ↔  RH.
    log(Hₙ) computed log()-free.
    """
    hn = lagarias_hn(n)
    if hn <= 0:
        return float("nan")
    log_hn = np.log2(hn) * _LN2
    return hn + np.exp(hn) * log_hn


def lagarias_check(n: int) -> bool:
    """Return True if n satisfies Lagarias inequality (consistent with RH)."""
    return sum_of_divisors(n) <= lagarias_bound(n)


if __name__ == "__main__":
    print("DEF 04 — Robin / Lagarias Arithmetic Criteria")
    print()
    test_ns = [6, 12, 60, 120, 360, 720, 5040, 720720]
    print("  Robin f(n) = σ(n)/(e^γ·n·log log n), δ(n)=f(n)-1, Lagarias check:")
    print(f"  {'n':>8}  {'σ(n)':>10}  {'f(n)':>8}  {'δ(n)':>9}  {'Robin<1':>7}  {'Lagarias':>8}")
    for n in test_ns:
        sn = sum_of_divisors(n)
        fn = robin_f(n)
        dn = robin_delta(n)

        if n >= 5041:
            r_ok = fn < 1.0
            flagr = "✓" if r_ok else "✗ VIOLATION"
        else:
            flagr = "N/A <5041"

        lag  = lagarias_check(n)
        flagl = "✓" if lag else "✗ VIOLATION"

        print(f"  {n:>8}  {sn:>10}  {fn:>8.5f}  {dn:>9.5f}  {flagr:>10}  {flagl:>8}")
    print()
    print(f"  Framework: BITSIZE_OFFSET δ = {BITSIZE_OFFSET}  (log₂(7.8))")
    print(f"  Robin threshold e^γ = {np.exp(EULER_MASCHERONI):.8f}")
    print(f"  λ* (curvature)      = {LAMBDA_STAR:.8f}")
