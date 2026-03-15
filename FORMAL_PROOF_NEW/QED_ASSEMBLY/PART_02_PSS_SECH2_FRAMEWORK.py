#!/usr/bin/env python3
"""
PART 2 — Feet (1): PSS:SECH² Prime-Side Framework
===================================================
Define the PSS:SECH² prime-side model: Dirichlet polynomial
coefficients b_n, the sech² vertical weight, and its Fourier
transform ŵ_H(ω). All objects here are classical prime sums
viewed through the sech² lens.

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
# DEFINITIONS
# ═════════════════════════════════════════════════════════════════════════

def Lambda_H(tau, H=H_STAR):
    """Λ_H(τ) = 2π sech²(τ/H)."""
    u = tau / H
    if abs(u) > 300:
        return 0.0
    return 2.0 * PI / (math.cosh(u) ** 2)


def w_hat_H(omega, H=H_STAR):
    """ŵ_H(ω) = πH²ω / sinh(πHω/2), ŵ_H(0) = 2H."""
    return sech2_fourier(omega, H)


def build_bn(T0, sigma, N):
    """b_n = n^{-σ} e^{i T₀ ln n}. Coefficients of D₀."""
    ns   = np.arange(1, N + 1, dtype=DTYPE)
    ln_n = _LN[1:N + 1]
    amp  = ns ** (-sigma)
    return amp * (np.cos(T0 * ln_n) + 1j * np.sin(T0 * ln_n))


def D_k(t, k, sigma, N):
    """D_k(t) = Σ_{n=1}^N (ln n)^k n^{-σ-it}."""
    ns   = np.arange(1, N + 1, dtype=DTYPE)
    ln_n = _LN[1:N + 1]
    amp  = (ln_n ** k) * ns ** (-sigma)
    phase = t * ln_n
    re = float(np.dot(amp, np.cos(phase)))
    im = -float(np.dot(amp, np.sin(phase)))
    return complex(re, im)


# ═════════════════════════════════════════════════════════════════════════
# VERIFICATION 1: Fourier transform properties
# ═════════════════════════════════════════════════════════════════════════

def verify_fourier_properties(H=H_STAR):
    """Verify key properties of ŵ_H(ω)."""
    print(f"\n  ── Verification 1: ŵ_H properties ──")
    print(f"  H = {H}")

    # (a) ŵ_H(0) = 2H
    w0 = w_hat_H(0.0, H)
    err_0 = abs(w0 - 2 * H)
    print(f"  ŵ_H(0) = {w0:.10f},  expected 2H = {2*H:.10f},"
          f"  error = {err_0:.2e}  {'✓' if err_0 < 1e-12 else '✗'}")

    # (b) ŵ_H(ω) ≥ 0 for all ω (PSD kernel)
    omegas = np.linspace(-20.0, 20.0, 10000)
    min_val = min(w_hat_H(float(w), H) for w in omegas)
    print(f"  min ŵ_H(ω) over [-20,20] = {min_val:.2e}"
          f"  {'≥ 0 ✓' if min_val >= -1e-15 else '< 0 ✗'}")

    # (c) Exponential decay: ŵ_H(ω) ~ 2πH²|ω| e^{-πH|ω|/2} for large ω
    test_omega = 4.0
    actual = w_hat_H(test_omega, H)
    approx = 2 * PI * H**2 * test_omega * math.exp(-PI * H * test_omega / 2)
    ratio = actual / max(approx, 1e-30)
    print(f"  ŵ_H({test_omega}) = {actual:.6e},"
          f"  2πH²ω·e^{{-πHω/2}} = {approx:.6e},"
          f"  ratio = {ratio:.6f}")

    # (d) Verify Parseval: ∫Λ_H(τ) dτ = 2πH · ∫sech²(u) du = 2πH · 2H = 4πH²
    #     Actually ∫Λ_H dτ = 2π ∫ sech²(τ/H) dτ = 2π · 2H = 4πH
    n_quad = 10000
    tau_arr = np.linspace(-50.0, 50.0, n_quad)
    dtau = 100.0 / (n_quad - 1)
    integral = sum(Lambda_H(float(t), H) for t in tau_arr) * dtau
    expected = 4 * PI * H
    err_int = abs(integral - expected) / expected
    print(f"  ∫Λ_H dτ = {integral:.8f},  expected 4πH = {expected:.8f},"
          f"  rel err = {err_int:.2e}  {'✓' if err_int < 1e-4 else '✗'}")

    # (e) Verify ∫Λ″_H dτ = 0 (mean-zero for second derivative)
    integral_Lpp = 0.0
    for tau in tau_arr:
        u = float(tau) / H
        if abs(u) > 300:
            continue
        s2 = 1.0 / (math.cosh(u) ** 2)
        lpp = (2.0 * PI / (H * H)) * s2 * (4.0 - 6.0 * s2)
        integral_Lpp += lpp
    integral_Lpp *= dtau
    print(f"  ∫Λ″_H dτ = {integral_Lpp:.2e}"
          f"  {'≈ 0 ✓' if abs(integral_Lpp) < 1e-6 else '✗'}")

    return (err_0 < 1e-12 and min_val >= -1e-15
            and err_int < 1e-4 and abs(integral_Lpp) < 1e-6)


# ═════════════════════════════════════════════════════════════════════════
# VERIFICATION 2: Kernel PSD-ness (discrete check)
# ═════════════════════════════════════════════════════════════════════════

def verify_kernel_psd(N=50, H=H_STAR):
    """Verify that K_{n,m} = ŵ_H(ln(n/m)) is positive semi-definite."""
    print(f"\n  ── Verification 2: kernel PSD-ness ──")
    print(f"  N = {N}, H = {H}")

    ln_n = _LN[1:N + 1]
    K = np.empty((N, N), dtype=DTYPE)
    for i in range(N):
        for j in range(N):
            K[i, j] = w_hat_H(float(ln_n[i] - ln_n[j]), H)

    eigvals = np.linalg.eigvalsh(K)
    min_eig = float(np.min(eigvals))
    n_neg   = int(np.sum(eigvals < -1e-10))

    print(f"  Min eigenvalue = {min_eig:.6e}")
    print(f"  Negative eigenvalues (< -1e-10): {n_neg}")
    psd = min_eig >= -1e-10
    print(f"  K is PSD: {'✓' if psd else '✗'}")

    return psd


# ═════════════════════════════════════════════════════════════════════════
# VERIFICATION 3: Dirichlet polynomial identities
# ═════════════════════════════════════════════════════════════════════════

def verify_dirichlet_identities(T0=14.134725, N=30):
    """Verify D_k identities: ∂_t D₀ = -i D₁, ∂²_t |D₀|² formula."""
    print(f"\n  ── Verification 3: Dirichlet polynomial identities ──")
    print(f"  T₀ = {T0:.6f}, N = {N}")

    dt = 1e-6
    d0   = D_k(T0,     0, SIGMA, N)
    d0p  = D_k(T0 + dt, 0, SIGMA, N)
    d0m  = D_k(T0 - dt, 0, SIGMA, N)
    d1   = D_k(T0,     1, SIGMA, N)
    d2   = D_k(T0,     2, SIGMA, N)

    # ∂_t D₀ = -i D₁
    deriv_num = (d0p - d0m) / (2 * dt)
    deriv_ana = -1j * d1
    err1 = abs(deriv_num - deriv_ana) / max(abs(deriv_ana), 1e-30)
    print(f"  ∂_t D₀ ≈ -i D₁: rel err = {err1:.2e}"
          f"  {'✓' if err1 < 1e-4 else '✗'}")

    # ∂²_t |D₀|² = 2|D₁|² - 2 Re(D̄₀ D₂)
    phi0 = abs(d0)**2
    phip = abs(d0p)**2
    phim = abs(d0m)**2
    d2_phi_num = (phip - 2 * phi0 + phim) / (dt**2)
    d2_phi_ana = 2 * abs(d1)**2 - 2 * (d0.conjugate() * d2).real
    err2 = abs(d2_phi_num - d2_phi_ana) / max(abs(d2_phi_ana), 1e-30)
    print(f"  ∂²_t|D₀|² = 2|D₁|²−2Re(D̄₀D₂): rel err = {err2:.2e}"
          f"  {'✓' if err2 < 5e-3 else '✗'}")

    return err1 < 1e-4 and err2 < 5e-3


# ═════════════════════════════════════════════════════════════════════════
def main():
    print("""
  ═══════════════════════════════════════════════════════════════
  PART 2 — FEET (1): PSS:SECH² PRIME-SIDE FRAMEWORK
  ═══════════════════════════════════════════════════════════════

  DEFINITIONS:
    Λ_H(τ) = 2π sech²(τ/H)           sech² window
    ŵ_H(ω) = πH²ω / sinh(πHω/2)     Fourier transform of sech²
    b_n    = n^{-σ} e^{iT₀ ln n}     Dirichlet coefficients
    D_k(t) = Σ (ln n)^k b_n e^{-it ln n}

  KEY PROPERTIES:
    • ŵ_H(0) = 2H = 3  (total mass of sech²)
    • ŵ_H(ω) ≥ 0 for all ω  (PSD kernel)
    • ŵ_H(ω) ~ 2πH²|ω| e^{-πH|ω|/2}  (exponential decay)
    • ∫Λ_H dτ = 4πH = 6π
    • ∫Λ″_H dτ = 0  (mean-zero second derivative)
""")

    r1 = verify_fourier_properties()
    r2 = verify_kernel_psd()
    r3 = verify_dirichlet_identities()

    all_pass = r1 and r2 and r3
    print(f"\n  PART 2 RESULT: {'ALL PASS ✓' if all_pass else 'FAILURES ✗'}")
    return all_pass


if __name__ == '__main__':
    main()
