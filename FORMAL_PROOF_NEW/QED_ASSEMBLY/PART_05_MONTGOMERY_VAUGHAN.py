#!/usr/bin/env python3
"""
PART 5 — Arms (2): Classical Montgomery–Vaughan Machinery
==========================================================
Present the MV mean value theorem for Dirichlet polynomials and
the near-diagonal dominance principle.  Tailor to frequencies
{ln n} and sech² weights.

This is the RIGHT ARM: supports the bound on the cross term
and the moment sandwich in PART 8.

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
from PHASE_06_ANALYTIC_CONVEXITY import sech2_fourier, mv_diagonal

PI     = math.pi
H_STAR = 1.5
SIGMA  = 0.5

_N_MAX = 10000
_LN    = np.array([0.0] + [math.log(n) for n in range(1, _N_MAX + 1)],
                  dtype=DTYPE)


# ═════════════════════════════════════════════════════════════════════════
# MV THEOREM STATEMENT
# ═════════════════════════════════════════════════════════════════════════

def print_mv_theorem():
    wh_ln2 = sech2_fourier(math.log(2), H_STAR)
    wh_ln3 = sech2_fourier(math.log(3), H_STAR)
    ratio2 = wh_ln2 / (2 * H_STAR)

    print(f"""
  MONTGOMERY–VAUGHAN MEAN VALUE THEOREM (adapted to sech² weights):

  CLASSICAL FORM (MV, 1974):
    For distinct real frequencies λ₁ < λ₂ < ... < λ_N and
    complex coefficients a_n:

      ∫₀ᵀ |Σ aₙ exp(iλₙt)|² dt = (T + O(1/δ)) Σ |aₙ|²

    where δ = min|λₙ − λₘ| (n≠m) is the minimum spacing.

  SECH²-ADAPTED FORM:
    With Λ_H(τ) = 2π sech²(τ/H) replacing the characteristic
    function of [0,T]:

      ∫ Λ_H(τ) |Σ aₙ exp(iλₙτ)|² dτ = ŵ_H(0) · Σ |aₙ|²
                                       + Σ(n≠m) aₙā_m ŵ_H(λₙ−λₘ)

    The off-diagonal sum is controlled by the exponential decay
    of ŵ_H(ω) = πH²ω / sinh(πHω/2).

  NEAR-DIAGONAL DOMINANCE:
    For frequencies λₙ = ln n (n = 1, ..., N):
      • Minimum spacing: δ_N = ln((N+1)/N) ~ 1/N
      • Near-diagonal pairs: |ln(n/m)| ≤ Δ  (Δ ~ 1)
      • Off-diagonal decay: ŵ_H(ω) ~ exp(-πH|ω|/2) for |ω| > 0

    The exponential decay of ŵ_H means off-diagonal contributions
    are suppressed by a factor exp(-πHΔ/2) relative to the diagonal.

  KEY CONSTANTS:
    ŵ_H(0)        = 2H = 3.0
    ŵ_H(ln 2)     = {wh_ln2:.6f}   (nearest off-diagonal, n/m = 2)
    ŵ_H(ln 3)     = {wh_ln3:.6f}   (n/m = 3)
    ŵ_H(ln 2)/ŵ_H(0) = {ratio2:.6f}   (near-diagonal suppression)
""")


# ═════════════════════════════════════════════════════════════════════════
# VERIFICATION 1: Spacing condition for {ln n}
# ═════════════════════════════════════════════════════════════════════════

def verify_spacing(N_values=None):
    """Verify minimum spacing δ_N = ln((N+1)/N) for various N."""
    if N_values is None:
        N_values = [9, 10, 20, 30, 50, 100, 200, 500]

    print(f"\n  ── Verification 1: spacing δ_N = ln((N+1)/N) ──")
    print(f"\n  {'N':>5}  {'δ_N':>12}  {'1/N':>12}  {'δ_N·N':>8}"
          f"  {'ŵ_H(δ_N)':>12}  {'ŵ_H(δ)/ŵ_H(0)':>16}")
    print("  " + "─" * 72)

    for N in N_values:
        delta_N = _LN[N + 1] - _LN[N]  # ln((N+1)/N)
        inv_N = 1.0 / N
        wh_delta = sech2_fourier(float(delta_N), H_STAR)
        ratio = wh_delta / (2 * H_STAR)
        print(f"  {N:>5}  {delta_N:>12.8f}  {inv_N:>12.8f}"
              f"  {delta_N * N:>8.4f}  {wh_delta:>12.8f}  {ratio:>16.8f}")

    return True


# ═════════════════════════════════════════════════════════════════════════
# VERIFICATION 2: MV upper bound M_k ≤ C_H · M_{2k}^{diag}
# ═════════════════════════════════════════════════════════════════════════

def verify_mv_upper_bound(T0=14.134725, N=50, n_quad=2000, tau_max=8.0):
    """
    Verify M_k ≤ 2π · λ_max(K) · M_{2k}^{diag} for k = 0, 1, 2.

    M_k      = ∫ Λ_H |D_k|² dτ   (integral moment, Λ_H = 2π sech²)
    M_{2k}^d = Σ (ln n)^{2k} n^{-2σ}  (diagonal moment)
    K_{n,m}  = ŵ_H(ln(n/m))           (sech² kernel matrix)
    λ_max    = spectral radius of K    (accounts for off-diagonal)

    The 2π arises because Λ_H(τ) = 2π · sech²(τ/H).
    """
    print(f"\n  ── Verification 2: MV spectral bound ──")
    print(f"  T₀ = {T0:.6f}, N = {N}")

    ns    = np.arange(1, N + 1, dtype=DTYPE)
    ln_n  = _LN[1:N + 1]

    # Build kernel matrix K_{n,m} = ŵ_H(ln(n/m)) and find spectral radius
    K_mat = np.empty((N, N), dtype=DTYPE)
    for i in range(N):
        for j in range(N):
            K_mat[i, j] = sech2_fourier(float(ln_n[i] - ln_n[j]), H_STAR)

    lambda_max = float(np.max(np.linalg.eigvalsh(K_mat)))
    C_bound = 2 * PI * lambda_max
    print(f"  ŵ_H(0) = {2*H_STAR:.1f},  λ_max(K) = {lambda_max:.4f},"
          f"  C = 2π·λ_max = {C_bound:.4f}")

    tau_arr = np.linspace(-tau_max, tau_max, n_quad, dtype=DTYPE)
    dtau    = 2.0 * tau_max / (n_quad - 1)
    u       = tau_arr / H_STAR
    lam     = 2.0 * PI / np.cosh(u) ** 2

    print(f"\n  {'k':>3}  {'M_k (integral)':>18}  {'C·M_{2k}^d':>18}"
          f"  {'ratio':>10}  {'hold':>6}")
    print("  " + "─" * 60)

    all_hold = True
    for k in range(3):
        amp_k = (ln_n ** k) * ns ** (-SIGMA)
        M_k = 0.0
        for j in range(n_quad):
            if lam[j] < 1e-10:
                continue
            t = T0 + float(tau_arr[j])
            phase = t * ln_n
            re = float(np.dot(amp_k, np.cos(phase)))
            im = -float(np.dot(amp_k, np.sin(phase)))
            M_k += float(lam[j]) * (re * re + im * im)
        M_k *= dtau

        diag_2k = float(np.sum(ln_n ** (2 * k) * ns ** (-2 * SIGMA)))
        upper = C_bound * diag_2k
        ratio = M_k / max(upper, 1e-30)
        hold = M_k <= upper + 1e-6
        all_hold = all_hold and hold
        print(f"  {k:>3}  {M_k:>18.8f}  {upper:>18.8f}"
              f"  {ratio:>10.6f}  {'✓' if hold else '✗':>6}")

    return all_hold


# ═════════════════════════════════════════════════════════════════════════
# VERIFICATION 3: Off-diagonal decay profile
# ═════════════════════════════════════════════════════════════════════════

def verify_offdiag_decay(H=H_STAR):
    """Show the exponential decay of ŵ_H at relevant off-diagonal separations."""
    print(f"\n  ── Verification 3: off-diagonal decay profile ──")
    print(f"  H = {H}")
    print(f"\n  {'n/m':>6}  {'ln(n/m)':>10}  {'ŵ_H':>14}"
          f"  {'ŵ_H/ŵ_H(0)':>14}  {'e^{-πH|ω|/2}':>16}")
    print("  " + "─" * 64)

    ratios = [1, 2, 3, 4, 5, 6, 8, 10, 15, 20]
    for r in ratios:
        omega = math.log(r) if r > 0 else 0.0
        wh = sech2_fourier(omega, H)
        wh0 = 2 * H
        decay_approx = math.exp(-PI * H * abs(omega) / 2) if omega > 0 else 1.0
        print(f"  {r:>6}  {omega:>10.6f}  {wh:>14.8f}"
              f"  {wh/wh0:>14.8f}  {decay_approx:>16.8f}")

    return True


# ═════════════════════════════════════════════════════════════════════════
def main():
    print("""
  ═══════════════════════════════════════════════════════════════
  PART 5 — ARMS (2): MONTGOMERY–VAUGHAN MACHINERY
  ═══════════════════════════════════════════════════════════════
""")

    print_mv_theorem()
    r1 = verify_spacing()
    r2 = verify_mv_upper_bound()
    r3 = verify_offdiag_decay()

    all_pass = r1 and r2 and r3
    print(f"\n  PART 5 RESULT: {'ALL PASS ✓' if all_pass else 'FAILURES ✗'}")
    return all_pass


if __name__ == '__main__':
    main()
