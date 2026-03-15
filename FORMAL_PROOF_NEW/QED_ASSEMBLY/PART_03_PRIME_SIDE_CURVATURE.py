#!/usr/bin/env python3
"""
PART 3 — Feet (2): Prime-Side Curvature Equation
==================================================
Write the prime-side curvature identity: the averaged second derivative
(curvature) of log|ζ| equals a prime-side expression involving the
b_n and ŵ_H(ln(n/m)).

Derives from: Mellin transform of weight + differentiation of explicit
formula. No assumptions beyond classical analytic continuation.

PROTOCOL: LOG-FREE | 9D-CENTRIC | BIT-SIZE TRACKED
Author:  Jason Mullings — BetaPrecision.com
Date:    14 March 2026
"""

import sys, os, math
import numpy as np

_ROOT = os.path.dirname(os.path.abspath(__file__))
_AI   = os.path.join(os.path.dirname(_ROOT), 'AI_PHASES')
sys.path.insert(0, _AI)

from PHASE_01_FOUNDATIONS        import DTYPE, PHI
from PHASE_06_ANALYTIC_CONVEXITY import sech2_fourier

PI     = math.pi
H_STAR = 1.5
SIGMA  = 0.5

_N_MAX = 10000
_LN    = np.array([0.0] + [math.log(n) for n in range(1, _N_MAX + 1)],
                  dtype=DTYPE)


# ═════════════════════════════════════════════════════════════════════════
# CORE IDENTITY
# ═════════════════════════════════════════════════════════════════════════

def curvature_identity(T0, N, H=H_STAR, sigma=SIGMA,
                       n_quad=2000, tau_max=8.0):
    """
    Verify the prime-side curvature identity:

      ∫ Λ_H(τ) ∂²_τ |D₀(T₀+τ)|² dτ  =  2M₁ − 2·cross

    where cross = Re∫ Λ_H D̄₀ D₂ dτ  and  M₁ = ∫ Λ_H |D₁|² dτ.

    LEFT SIDE:  computed by numerical second derivative.
    RIGHT SIDE: computed from D₁, D₂ directly.
    """
    ns    = np.arange(1, N + 1, dtype=DTYPE)
    ln_n  = _LN[1:N + 1]
    a0    = ns ** (-sigma)
    a1    = ln_n * a0
    a2    = (ln_n ** 2) * a0

    tau_arr = np.linspace(-tau_max, tau_max, n_quad, dtype=DTYPE)
    dtau    = 2.0 * tau_max / (n_quad - 1)

    u   = tau_arr / H
    lam = 2.0 * PI / np.cosh(u) ** 2

    # Compute M₁ and cross via D₁, D₂
    M1_acc    = 0.0
    cross_acc = 0.0

    for j in range(n_quad):
        if lam[j] < 1e-10:
            continue
        t     = T0 + float(tau_arr[j])
        phase = t * ln_n
        cos_p = np.cos(phase)
        sin_p = np.sin(phase)

        re0 = float(cos_p @ a0); im0 = -float(sin_p @ a0)
        re1 = float(cos_p @ a1); im1 = -float(sin_p @ a1)
        re2 = float(cos_p @ a2); im2 = -float(sin_p @ a2)

        M1_acc    += float(lam[j]) * (re1*re1 + im1*im1)
        cross_acc += float(lam[j]) * (re0*re2 + im0*im2)

    M1_acc    *= dtau
    cross_acc *= dtau

    rhs = 2 * M1_acc - 2 * cross_acc

    # Compute LHS: ∫ Λ_H ∂²|D₀|² dτ  via the IBP identity
    # After IBP twice: ∫ Λ″_H |D₀|² dτ = ∫ Λ_H ∂²|D₀|² dτ
    # So LHS = ∫ Λ″_H |D₀|² dτ

    s2  = 1.0 / np.cosh(u) ** 2
    lpp = (2.0 * PI / (H * H)) * s2 * (4.0 - 6.0 * s2)
    LppPhi = 0.0
    for j in range(n_quad):
        if abs(float(lpp[j])) < 1e-15:
            continue
        t     = T0 + float(tau_arr[j])
        phase = t * ln_n
        cos_p = np.cos(phase)
        sin_p = np.sin(phase)
        re0 = float(cos_p @ a0); im0 = -float(sin_p @ a0)
        LppPhi += float(lpp[j]) * (re0*re0 + im0*im0)
    LppPhi *= dtau

    lhs = LppPhi

    rel_err = abs(lhs - rhs) / max(abs(rhs), 1e-30)

    return {
        'M1': M1_acc, 'cross': cross_acc,
        'LHS': lhs, 'RHS': rhs,
        'rel_err': rel_err, 'match': rel_err < 5e-3,
    }


# ═════════════════════════════════════════════════════════════════════════
# VERIFICATION: Identity across T₀ values
# ═════════════════════════════════════════════════════════════════════════

def verify_identity(N=50):
    """Verify ∫Λ″|D₀|² = 2M₁ − 2·cross at multiple T₀."""
    T0_vals = [14.13, 21.02, 25.01, 50.0, 100.0, 200.0, 500.0]

    print(f"\n  ── Curvature identity: ∫Λ″|D₀|² = 2M₁ − 2·cross ──")
    print(f"  N = {N}")
    print(f"\n  {'T₀':>10}  {'LHS (∫Λ″|D₀|²)':>18}  {'RHS (2M₁−2cross)':>18}"
          f"  {'rel err':>12}  {'match':>6}")
    print("  " + "─" * 72)

    all_pass = True
    for T0 in T0_vals:
        r = curvature_identity(T0, N)
        status = "✓" if r['match'] else "✗"
        if not r['match']:
            all_pass = False
        print(f"  {T0:>10.2f}  {r['LHS']:>18.8f}  {r['RHS']:>18.8f}"
              f"  {r['rel_err']:>12.2e}  {status:>6}")

    return all_pass


# ═════════════════════════════════════════════════════════════════════════
# VERIFICATION: Cross-term via discrete kernel form
# ═════════════════════════════════════════════════════════════════════════

def verify_cross_discrete(T0=14.134725, N=30, H=H_STAR):
    """
    Verify cross = Σ_{n,m} b_n b̄_m (ln m)² ŵ_H(ln(n/m))
    matches the integral form.
    """
    print(f"\n  ── Cross-term: integral vs discrete kernel ──")
    print(f"  T₀ = {T0:.6f}, N = {N}")

    # Discrete form
    ln_n = _LN[1:N + 1]
    ns   = np.arange(1, N + 1, dtype=DTYPE)
    amp  = ns ** (-SIGMA)
    phase = T0 * ln_n
    b = amp * (np.cos(phase) + 1j * np.sin(phase))
    L2b = (ln_n ** 2) * b

    cross_disc = 0.0
    for i in range(N):
        for j in range(N):
            omega = float(ln_n[i] - ln_n[j])
            wh = sech2_fourier(omega, H)
            cross_disc += float(np.real(np.conj(b[i]) * L2b[j] * wh))

    # Integral form (integrates Λ_H = 2π·sech², so includes factor 2π)
    r = curvature_identity(T0, N, H)
    cross_int = r['cross']

    # Discrete kernel uses sech2_fourier = FT of sech²(t/H).
    # Integral uses Λ_H = 2π·sech²(t/H), so FT[Λ_H] = 2π·sech2_fourier.
    cross_disc_scaled = 2 * PI * cross_disc

    rel_err = abs(cross_disc_scaled - cross_int) / max(abs(cross_int), 1e-30)
    print(f"  cross (discrete × 2π) = {cross_disc_scaled:.10f}")
    print(f"  cross (integral)      = {cross_int:.10f}")
    print(f"  rel err = {rel_err:.2e}  {'✓' if rel_err < 5e-3 else '✗'}")

    return rel_err < 5e-3


# ═════════════════════════════════════════════════════════════════════════
def main():
    print("""
  ═══════════════════════════════════════════════════════════════
  PART 3 — FEET (2): PRIME-SIDE CURVATURE EQUATION
  ═══════════════════════════════════════════════════════════════

  IDENTITY (via IBP + Dirichlet differentiation):

    ∫ Λ″_H(τ) |D₀(T₀+τ)|² dτ  =  2M₁ − 2·Re∫ Λ_H D̄₀D₂ dτ

  where:
    M₁   = ∫ Λ_H |D₁|² dτ           (first-moment energy)
    cross = Re∫ Λ_H D̄₀D₂ dτ         (cross term)

  SOURCE: Mellin transform of sech² weight + ∂²_t|D₀|² formula
  ASSUMPTIONS: None beyond standard analytic continuation.
""")

    r1 = verify_identity()
    r2 = verify_cross_discrete()

    all_pass = r1 and r2
    print(f"\n  PART 3 RESULT: {'ALL PASS ✓' if all_pass else 'FAILURES ✗'}")
    return all_pass


if __name__ == '__main__':
    main()
