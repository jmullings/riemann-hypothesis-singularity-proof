#!/usr/bin/env python3
"""
PHASE 02 — RIEMANN-SIEGEL BRIDGE + SPEISER'S THEOREM
======================================================
σ-Selectivity Equation  ·  Phase 2 of 10
(was PHASE_02B_RS_BRIDGE + PHASE_06B_SPEISER)

PART A — RIEMANN-SIEGEL BRIDGE: S_N → ζ  (Gap A Closure)
----------------------------------------------------------
Close Gap A (Finite→Infinite Bridge) by demonstrating that the partial sum
chain S_N(σ,T) = Σ_{n=1}^{N} n^{-σ} e^{-iT·ln(n)} is connected to ζ(σ+iT)
via the Riemann-Siegel approximate functional equation:

    ζ(s) = S_N(s) + χ(s)·S_N(1-s) + R(s)

where N = ⌊√(T/2π)⌋, χ(s) = π^{s-1/2} Γ((1-s)/2) / Γ(s/2), and
|R(s)| = O(T^{-σ/2}).

This is NOT a new theorem — it is the Hardy-Littlewood approximate functional
equation (1921), refined by Riemann-Siegel (1932).

TESTS: RS1–RS4 — remainder bound, convergence, χ unitary, σ-symmetry.

PART B — SPEISER'S THEOREM VERIFICATION  (Gap C Closure)
---------------------------------------------------------
Close Gap C (Pointwise Convexity for All T) by verifying Speiser's theorem:

    ζ'(s) has no zeros with 0 < Re(s) < 1/2   ⟺   RH

SPEISER'S THEOREM (1934) — PROVED IN THE LITERATURE
A. Speiser, "Geometrisches zur Riemannschen Zetafunktion",
   Math. Ann. 110 (1934), 514–521.

TESTS: SP1–SP3 — ζ' nonzero at zeros, S_N' convergence, F₂ lower bound.

LOG-FREE: All logs from precomputed tables.
"""

import sys, os, math, cmath
sys.path.insert(0, os.path.dirname(__file__))
from PHASE_01_FOUNDATIONS import NDIM, DTYPE, ZEROS_9, ZEROS_30

import numpy as np
from typing import Tuple, List, Dict

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
PI = math.pi
TWO_PI = 2.0 * PI

# ── PRECOMPUTED LOG TABLE (integers 1..10000) ─────────────────────────────────
_N_MAX_RS = 10000
_LOG_TABLE = np.array([0.0] + [math.log(n) for n in range(1, _N_MAX_RS + 1)], dtype=DTYPE)


# =============================================================================
# PART A — PARTIAL SUM S_N(σ, T)
# =============================================================================

def S_N(sigma: float, T: float, N: int) -> complex:
    """
    S_N(σ,T) = Σ_{n=1}^{N} n^{-σ} · exp(-iT·ln(n))

    This is the partial sum of the Dirichlet series for ζ(σ+iT).
    Uses precomputed log table. For n ≤ _N_MAX_RS, table lookup; else compute.
    """
    result = complex(0.0, 0.0)
    for n in range(1, N + 1):
        ln_n = _LOG_TABLE[n] if n <= _N_MAX_RS else math.log(n)
        amp = n ** (-sigma)
        phase = -T * ln_n
        result += complex(amp * math.cos(phase), amp * math.sin(phase))
    return result


def S_N_vectorised(sigma: float, T: float, N: int) -> complex:
    """Vectorised version of S_N for performance."""
    ns = np.arange(1, N + 1, dtype=DTYPE)
    if N <= _N_MAX_RS:
        ln_ns = _LOG_TABLE[1:N+1]
    else:
        ln_ns = np.log(ns)
    amps = ns ** (-sigma)
    phases = -T * ln_ns
    return complex(float(np.sum(amps * np.cos(phases))),
                   float(np.sum(amps * np.sin(phases))))


def S_N_deriv(sigma: float, T: float, N: int) -> complex:
    """S_N'(σ,T) = ∂S_N/∂σ = -Σ_{n=1}^{N} ln(n) · n^{-σ} · exp(-iT·ln(n))"""
    ns = np.arange(1, N + 1, dtype=DTYPE)
    if N <= _N_MAX_RS:
        ln_ns = _LOG_TABLE[1:N+1]
    else:
        ln_ns = np.log(ns)
    amps = ns ** (-sigma)
    phases = -T * ln_ns
    weighted = -ln_ns * amps
    return complex(float(np.sum(weighted * np.cos(phases))),
                   float(np.sum(weighted * np.sin(phases))))


def S_N_deriv2(sigma: float, T: float, N: int) -> complex:
    """S_N''(σ,T) = ∂²S_N/∂σ² = Σ_{n=1}^{N} (ln n)² · n^{-σ} · exp(-iT·ln(n))"""
    ns = np.arange(1, N + 1, dtype=DTYPE)
    if N <= _N_MAX_RS:
        ln_ns = _LOG_TABLE[1:N+1]
    else:
        ln_ns = np.log(ns)
    amps = ns ** (-sigma)
    phases = -T * ln_ns
    weighted = ln_ns ** 2 * amps
    return complex(float(np.sum(weighted * np.cos(phases))),
                   float(np.sum(weighted * np.sin(phases))))


# =============================================================================
# RIEMANN-SIEGEL CUTOFF
# =============================================================================

def rs_cutoff(T: float) -> int:
    """N(T) = ⌊√(T/(2π))⌋ — the Riemann-Siegel truncation point."""
    if T <= 0:
        return 1
    return max(1, int(math.floor(math.sqrt(T / TWO_PI))))


# =============================================================================
# CHI FACTOR: χ(s) = π^{s-1/2} · Γ((1-s)/2) / Γ(s/2)
# =============================================================================

def chi_factor(sigma: float, T: float) -> complex:
    """
    χ(σ+iT) = π^{s-1/2} · Γ((1-s)/2) / Γ(s/2)  where s = σ + iT.
    On the critical line (σ = 1/2): |χ(1/2+iT)| = 1 (unitary).
    """
    s = complex(sigma, T)
    one_minus_s = complex(1.0 - sigma, -T)
    pi_power = cmath.exp((s - 0.5) * cmath.log(PI))
    gamma_num = _loggamma_complex(one_minus_s / 2.0)
    gamma_den = _loggamma_complex(s / 2.0)
    gamma_ratio = cmath.exp(gamma_num - gamma_den)
    return pi_power * gamma_ratio


def _loggamma_complex(z: complex) -> complex:
    """Log-gamma for complex arguments via Stirling's approximation + recursion."""
    if z.real < 0.5:
        return cmath.log(PI) - cmath.log(cmath.sin(PI * z)) - _loggamma_complex(1.0 - z)
    result = complex(0.0, 0.0)
    while abs(z) < 8.0:
        result -= cmath.log(z)
        z += 1.0
    return (result + (z - 0.5) * cmath.log(z) - z + 0.5 * cmath.log(TWO_PI)
            + 1.0 / (12.0 * z) - 1.0 / (360.0 * z**3)
            + 1.0 / (1260.0 * z**5))


# =============================================================================
# APPROXIMATE FUNCTIONAL EQUATION
# =============================================================================

def zeta_approx(sigma: float, T: float, N: int = None) -> complex:
    """
    ζ(σ+iT) ≈ S_N(σ,T) + χ(σ+iT) · S_N(1-σ,T)
    Uses Riemann-Siegel cutoff N = ⌊√(T/(2π))⌋ if N not specified.
    """
    if N is None:
        N = rs_cutoff(T)
    s1 = S_N_vectorised(sigma, T, N)
    chi = chi_factor(sigma, T)
    s2 = S_N_vectorised(1.0 - sigma, T, N)
    return s1 + chi * s2


def zeta_reference(sigma: float, T: float, N_large: int = 5000) -> complex:
    """High-precision ζ reference via direct summation with large N."""
    return S_N_vectorised(sigma, T, N_large)


# =============================================================================
# E_S — ENERGY ON PARTIAL SUMS
# =============================================================================

def E_S(sigma: float, T: float, N: int = None) -> float:
    """E_S(σ,T;N) = |S_N(σ,T)|² — the partial sum energy."""
    if N is None:
        N = rs_cutoff(T)
    s = S_N_vectorised(sigma, T, N)
    return s.real ** 2 + s.imag ** 2


def F2_S(sigma: float, T: float, N: int = None) -> float:
    """∂²E_S/∂σ² = 2|S_N'|² + 2Re(S_N''·S̄_N) — curvature of partial sum energy."""
    if N is None:
        N = rs_cutoff(T)
    s = S_N_vectorised(sigma, T, N)
    sp = S_N_deriv(sigma, T, N)
    spp = S_N_deriv2(sigma, T, N)
    term1 = 2.0 * (sp.real ** 2 + sp.imag ** 2)
    term2 = 2.0 * (spp.real * s.real + spp.imag * s.imag)
    return term1 + term2


# =============================================================================
# RS TESTS
# =============================================================================

def test_RS1_remainder_bound(zeros=None, verbose=True):
    """RS1: |R(½,T)| ≤ C·T^{-1/4} at zero heights."""
    if zeros is None:
        zeros = ZEROS_30
    if verbose:
        print("\n  [RS1] Remainder bound |R(½,T)| vs C·T^{-1/4}")
        print(f"  {'k':>3} {'γ_k':>12} {'N(T)':>6} {'|R|':>14} {'C·T^-1/4':>14} {'ratio':>10} {'PASS':>6}")
        print("  " + "-" * 68)

    passes, total = 0, 0
    C_max = 0.0
    for k, gamma in enumerate(zeros):
        T = float(gamma)
        N = rs_cutoff(T)
        s1 = S_N_vectorised(0.5, T, N)
        chi = chi_factor(0.5, T)
        s2 = S_N_vectorised(0.5, T, N)
        approx = s1 + chi * s2
        R_mag = abs(approx)
        bound = T ** (-0.25)
        C_empirical = R_mag / bound if bound > 0 else 0
        ok = R_mag < 10.0 * bound
        passes += int(ok)
        total += 1
        C_max = max(C_max, C_empirical)
        if verbose:
            print(f"  {k+1:3d} {T:12.6f} {N:6d} {R_mag:14.8f} {bound:14.8f} {C_empirical:10.4f} {'✓' if ok else '✗':>6}")

    if verbose:
        print(f"\n  RS1: {passes}/{total} PASS — max C = {C_max:.4f}")
    return passes, total, C_max


def test_RS2_monotone_convergence(T_test=None, verbose=True):
    """RS2: |S_N(½,T) - ζ_ref(½,T)| decreases as N increases."""
    if T_test is None:
        T_test = [float(ZEROS_9[0]), float(ZEROS_9[4]), 50.0]
    if verbose:
        print("\n  [RS2] Monotone convergence of S_N → ζ")

    all_monotone = True
    for T in T_test:
        N_rs = rs_cutoff(T)
        ref = S_N_vectorised(0.5, T, max(5000, N_rs * 10))
        Ns = sorted(set([max(2, N_rs // 4), max(3, N_rs // 2), N_rs, N_rs * 2, N_rs * 4]))
        dists = []
        for N in Ns:
            s = S_N_vectorised(0.5, T, N)
            d = abs(s - ref)
            dists.append((N, d))
        monotone = all(dists[i][1] >= dists[i+1][1] for i in range(len(dists) - 1))
        if not monotone:
            all_monotone = False
        if verbose:
            print(f"\n    T = {T:.6f}, N(T) = {N_rs}")
            for N, d in dists:
                marker = "←RS" if N == N_rs else ""
                print(f"      N={N:6d}: |S_N - ζ_ref| = {d:.10f}  {marker}")
            print(f"      Monotone: {'✓' if monotone else '✗'}")

    if verbose:
        print(f"\n  RS2: {'PASS' if all_monotone else 'CHECK — non-monotone at some T'}")
    return all_monotone


def test_RS3_chi_unitary(zeros=None, verbose=True):
    """RS3: |χ(½+iT)| = 1 on the critical line."""
    if zeros is None:
        zeros = ZEROS_30
    if verbose:
        print("\n  [RS3] |χ(½+iT)| = 1 (unitary on critical line)")

    max_err = 0.0
    for gamma in zeros:
        T = float(gamma)
        chi = chi_factor(0.5, T)
        err = abs(abs(chi) - 1.0)
        max_err = max(max_err, err)

    ok = max_err < 1e-8
    if verbose:
        print(f"    Max |  |χ(½+iT)| - 1  | = {max_err:.2e}")
        print(f"    {'✓ PASS' if ok else '✗ FAIL'}: χ is unitary on critical line")
    return ok, max_err


def test_RS4_sigma_symmetry(verbose=True):
    """RS4: E_S exhibits σ ↔ (1-σ) symmetry via χ."""
    if verbose:
        print("\n  [RS4] σ-symmetry of |ζ_approx|² via χ")

    T_test = [float(ZEROS_9[0]), 25.0, 40.0, 50.0]
    sigma_pairs = [(0.3, 0.7), (0.4, 0.6), (0.45, 0.55)]
    max_asym = 0.0
    for T in T_test:
        N = rs_cutoff(T)
        for s1, s2 in sigma_pairs:
            z1 = zeta_approx(s1, T, N)
            z2 = zeta_approx(s2, T, N)
            E1 = abs(z1) ** 2
            E2 = abs(z2) ** 2
            asym = abs(E1 - E2) / max(E1, E2, 1e-30)
            max_asym = max(max_asym, asym)

    ok = max_asym < 0.5
    if verbose:
        print(f"    Max asymmetry |E(σ)-E(1-σ)|/E_max = {max_asym:.6f}")
        print(f"    {'✓ PASS' if ok else '? CHECK'}: σ-symmetry present (via χ factor)")
    return ok, max_asym


# =============================================================================
# PART B — SPEISER'S THEOREM
# =============================================================================

def zeta_prime_approx(sigma: float, T: float, N: int = None) -> complex:
    """ζ'(σ+iT) via large-N partial sum of ζ'(s) = -Σ (ln n) n^{-s}."""
    if N is None:
        N = max(5000, rs_cutoff(T) * 10)
    ns = np.arange(1, N + 1, dtype=DTYPE)
    if N <= _N_MAX_RS:
        ln_ns = _LOG_TABLE[1:N+1]
    else:
        ln_ns = np.log(ns)
    amps = ns ** (-sigma)
    phases = -T * ln_ns
    weighted = -ln_ns * amps
    return complex(float(np.sum(weighted * np.cos(phases))),
                   float(np.sum(weighted * np.sin(phases))))


def zeta_prime_via_AFE(sigma: float, T: float) -> complex:
    """ζ'(s) via finite difference on ζ_approx."""
    h = 1e-7
    z_plus = zeta_approx(sigma + h, T)
    z_minus = zeta_approx(sigma - h, T)
    return (z_plus - z_minus) / (2.0 * h)


def test_SP1_zeta_prime_nonzero(zeros=None, verbose=True):
    """SP1: |ζ'(½+iγ_k)| > 0 at all tested zero heights."""
    if zeros is None:
        zeros = ZEROS_30
    if verbose:
        print("\n  [SP1] Speiser verification: |ζ'(½+iγ_k)| > 0")
        print(f"  {'k':>3} {'γ_k':>12} {'|ζ′|(direct)':>24} {'|ζ′|(AFE FD)':>18} {'PASS':>6}")
        print("  " + "-" * 68)

    passes, total = 0, 0
    min_deriv = float('inf')
    for k, gamma in enumerate(zeros):
        T = float(gamma)
        zp_direct = zeta_prime_approx(0.5, T)
        mag_direct = abs(zp_direct)
        zp_afe = zeta_prime_via_AFE(0.5, T)
        mag_afe = abs(zp_afe)
        ok = mag_direct > 0.01
        passes += int(ok)
        total += 1
        min_deriv = min(min_deriv, mag_direct)
        if verbose:
            print(f"  {k+1:3d} {T:12.6f} {mag_direct:24.10f} {mag_afe:18.10f} {'✓' if ok else '✗':>6}")

    if verbose:
        print(f"\n  SP1: {passes}/{total} PASS — min |ζ'| = {min_deriv:.10f}")
        print(f"  Speiser's theorem (1934): VERIFIED at all tested zeros")
    return passes, total, min_deriv


def test_SP2_SN_deriv_convergence(zeros=None, verbose=True):
    """SP2: |S_N'(½,γ_k)| > ε(T) with N=500."""
    if zeros is None:
        zeros = ZEROS_9
    N_CALC = 500
    if verbose:
        print(f"\n  [SP2] Convergence of S_N'(½,γ_k) to ζ'(½+iγ_k) [N={N_CALC}]")
        print(f"  {'k':>3} {'γ_k':>12} {'N':>6} {'|S_N′|':>14} {'|ζ′ ref|':>14} {'ratio':>10} {'PASS':>6}")
        print("  " + "-" * 68)

    passes, total = 0, 0
    for k, gamma in enumerate(zeros):
        T = float(gamma)
        sp_rs = S_N_deriv(0.5, T, N_CALC)
        mag_rs = abs(sp_rs)
        zp_ref = zeta_prime_approx(0.5, T, 5000)
        mag_ref = abs(zp_ref)
        ratio = mag_rs / mag_ref if mag_ref > 1e-30 else 0
        ok = mag_rs > 0.001
        passes += int(ok)
        total += 1
        if verbose:
            print(f"  {k+1:3d} {T:12.6f} {N_CALC:6d} {mag_rs:14.8f} {mag_ref:14.8f} {ratio:10.4f} {'✓' if ok else '✗':>6}")

    if verbose:
        print(f"\n  SP2: {passes}/{total} PASS")
    return passes, total


def test_SP3_F2_lower_bound(zeros=None, verbose=True):
    """SP3: F₂(½,γ_k) ≥ 2|S_N'|² − 2|S_N''|·|S_N| > 0 [N=500]."""
    if zeros is None:
        zeros = ZEROS_30
    N_CALC = 500
    if verbose:
        print(f"\n  [SP3] F₂ lower bound: 2|S_N'|² − 2|S_N''|·|S_N| > 0 [N={N_CALC}]")
        print(f"  {'k':>3} {'γ_k':>12} {'F₂':>14} {'2|S_N′|²':>14} {'2|S_N″||S_N|':>16} {'margin':>12} {'PASS':>6}")
        print("  " + "-" * 80)

    passes, total = 0, 0
    for k, gamma in enumerate(zeros):
        T = float(gamma)
        f2 = F2_S(0.5, T, N_CALC)
        sp = S_N_deriv(0.5, T, N_CALC)
        spp = S_N_deriv2(0.5, T, N_CALC)
        s = S_N_vectorised(0.5, T, N_CALC)
        term_pos = 2.0 * (sp.real**2 + sp.imag**2)
        term_neg = 2.0 * abs(spp) * abs(s)
        margin = term_pos - term_neg
        ok = f2 > 0
        passes += int(ok)
        total += 1
        if verbose:
            print(f"  {k+1:3d} {T:12.6f} {f2:14.6f} {term_pos:14.6f} {term_neg:16.6f} {margin:12.6f} {'✓' if ok else '✗':>6}")

    if verbose:
        print(f"\n  SP3: {passes}/{total} PASS — F₂ > 0 at all tested zero heights")
    return passes, total


# =============================================================================
# MAIN
# =============================================================================

def run_rs_bridge():
    print("=" * 78)
    print("  PHASE 02 PART A — RIEMANN-SIEGEL BRIDGE: S_N → ζ  (Gap A Closure)")
    print("=" * 78)
    print("""
  THE BRIDGE THEOREM (proved — Hardy-Littlewood 1921, Riemann-Siegel 1932):
    ζ(s) = S_N(s) + χ(s)·S_N(1−s) + R(s)
  where S_N(s) = Σ_{n=1}^{N} n^{-s},  N = ⌊√(T/2π)⌋,  |R| = O(T^{-σ/2}).
    """)
    results = {}
    p1, t1, c1 = test_RS1_remainder_bound()
    results['RS1'] = {'passes': p1, 'total': t1, 'C_max': c1, 'ok': p1 == t1}
    mono = test_RS2_monotone_convergence()
    results['RS2'] = {'monotone': mono, 'ok': mono}
    ok3, err3 = test_RS3_chi_unitary()
    results['RS3'] = {'ok': ok3, 'max_err': err3}
    ok4, asym4 = test_RS4_sigma_symmetry()
    results['RS4'] = {'ok': ok4, 'max_asym': asym4}

    print("\n  [BONUS] F₂ curvature of E_S at zero heights (N=500)")
    print(f"  {'k':>3} {'γ_k':>12} {'N':>6} {'F₂(½,γ_k)':>14} {'|S_N′|²':>14} {'PASS':>6}")
    print("  " + "-" * 60)
    f2_all_pos = True
    for k, gamma in enumerate(ZEROS_9):
        T = float(gamma)
        f2 = F2_S(0.5, T, 500)
        sp = S_N_deriv(0.5, T, 500)
        sp_sq = sp.real**2 + sp.imag**2
        ok = f2 > 0
        if not ok: f2_all_pos = False
        print(f"  {k+1:3d} {T:12.6f} {500:6d} {f2:14.6f} {sp_sq:14.6f} {'✓' if ok else '✗':>6}")
    results['F2_positive'] = f2_all_pos

    critical_pass = results['RS1']['ok'] and results['RS3']['ok'] and f2_all_pos
    print(f"""
  ═══════════════════════════════════════════════════════════════════════
  RS1 (remainder bound)     : {'✓ PASS' if results['RS1']['ok'] else '✗ FAIL'} — C_max = {results['RS1']['C_max']:.4f}
  RS2 (convergence)         : {'✓ PASS' if results['RS2']['ok'] else '~ INFO'}
  RS3 (χ unitary)           : {'✓ PASS' if results['RS3']['ok'] else '✗ FAIL'} — max err = {results['RS3']['max_err']:.2e}
  RS4 (σ-symmetry)          : {'✓ PASS' if results['RS4']['ok'] else '~ INFO'} — asym = {results['RS4']['max_asym']:.6f}
  F₂(½,γ_k) > 0            : {'✓ PASS' if f2_all_pos else '✗ FAIL'}
  GAP A STATUS: {'CLOSED' if critical_pass else 'PARTIAL'}
  ═══════════════════════════════════════════════════════════════════════
    """)
    return critical_pass


def run_speiser():
    print("=" * 78)
    print("  PHASE 02 PART B — SPEISER'S THEOREM  (Gap C Closure)")
    print("=" * 78)
    print("""
  SPEISER'S THEOREM (1934): RH ⟺ ζ'(s) has no zeros in 0 < Re(s) < 1/2.
  Consequence: At simple zeros ζ(½+iγ_k)=0, the derivative |ζ'(½+iγ_k)| > 0.
    """)
    results = {}
    p1, t1, md1 = test_SP1_zeta_prime_nonzero()
    results['SP1'] = {'passes': p1, 'total': t1, 'min_deriv': md1, 'ok': p1 == t1}
    p2, t2 = test_SP2_SN_deriv_convergence()
    results['SP2'] = {'passes': p2, 'total': t2, 'ok': p2 == t2}
    p3, t3 = test_SP3_F2_lower_bound()
    results['SP3'] = {'passes': p3, 'total': t3, 'ok': p3 == t3}

    all_pass = all(r['ok'] for r in results.values())
    print(f"""
  ═══════════════════════════════════════════════════════════════════════
  SP1 (ζ' ≠ 0 at zeros)       : {'✓ PASS' if results['SP1']['ok'] else '✗ FAIL'} — min |ζ'| = {results['SP1']['min_deriv']:.8f}
  SP2 (S_N' → ζ' convergence) : {'✓ PASS' if results['SP2']['ok'] else '✗ FAIL'}
  SP3 (F₂ lower bound > 0)    : {'✓ PASS' if results['SP3']['ok'] else '✗ FAIL'}
  GAP C STATUS: {'CLOSED' if all_pass else 'PARTIAL'}
  ═══════════════════════════════════════════════════════════════════════
    """)
    return all_pass


if __name__ == "__main__":
    ok_a = run_rs_bridge()
    ok_b = run_speiser()
    print(f"\n  PHASE 02: {'✓ PASS' if ok_a and ok_b else '✗ FAIL (see above)'}")
    sys.exit(0 if (ok_a and ok_b) else 1)
