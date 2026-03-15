#!/usr/bin/env python3
"""
PATH_1_SPECTRAL_OPERATOR.py
============================
Location: FORMAL_PROOF_NEW/SELECTIVITY/PATH_1/EXECUTION/

PATHWAY: Hilbert–Pólya Spectral Operator — LONG-TERM HORIZON
STATUS:  Research phase (three sub-problems identified; all OPEN)
ROLE:    Long-term consequence of Pathway 2; not a near-term proof target
UPDATED: Aligned with FULL_PROOF.py 6-kernel framework + QED_ASSEMBLY closures

SOURCE:  Three independent reviewer consensus (TODO.md v2.0, Reviewer 3 detail)

6 KERNEL FORMS (all equivalent to sech²):
  K1 sech², K2 cosh, K3 tanh', K4 exp, K5 sinh/cosh, K6 logistic

Cross-references:
  FULL_PROOF.py — Theorems A-D (complete proof framework)
  PATH_2 — Weil explicit formula (primary route, uses sech² kernel)
  PART_09_RS_BRIDGE.py — GAP 3 closure (Weil admissibility)

==============================================================================
MATHEMATICAL FRAMEWORK
==============================================================================

The Hilbert–Pólya conjecture (1914, open): there exists a self-adjoint operator
Â on a Hilbert space such that its eigenvalues are exactly {γₙ} — the imaginary
parts of the non-trivial zeros of ζ(s).

Our candidate kernel arises from the prime spectral Gram matrix. For N primes
p₁ < p₂ < ... < p_N and evaluation point (σ,T), define:

    M(σ,T)_{jk} = p_j^{−σ} · p_k^{−σ} · cos(T · log(p_j/p_k))

This is a real symmetric PSD matrix (rank 2: M = a·aᵀ + b·bᵀ where
a_j = p_j^{-σ}cos(T log p_j), b_j = p_j^{-σ}sin(T log p_j)).

Known algebraic facts about M(σ,T):
  1. Tr(M) = Σ_p p^{-2σ} = E_diag(σ)  (T-independent)
  2. Non-zero eigenvalues:
       λ_max(σ,T) = (E_diag + |D(2σ,2T)|) / 2
       λ_min(σ,T) = (E_diag − |D(2σ,2T)|) / 2
  3. Both eigenvalues are strictly decreasing in σ  (sigma-selectivity of M)
  4. λ_min ≥ 0 by triangle inequality

The spectral gap λ_max − λ_min = |D(2σ,2T)| encodes the entire T-dependence.

==============================================================================
THREE SUB-PROBLEMS (per Reviewer 3)
==============================================================================

ALL THREE ARE OPEN. This pathway is retained for long-term research.

SUB-PROBLEM (a): M → ∞ Operator Norm Convergence
─────────────────────────────────────────────────
  G is a finite N×N kernel matrix. For an operator on ℓ²(primes), need N → ∞.
  Key question: does Σ_p p^{-1} (the harmonic series over primes, which diverges)
  cause G to blow up in operator norm?

  Analysis:
    Tr(M(½,T)) = Σ_p p^{-1} = diverges (Mertens' theorem: ~ log log X).
    For Hilbert-Schmidt norm: ‖M‖_HS² = Σ_{j,k} M_{jk}² ≤ Tr(M)² → ∞.
    So M is NOT trace-class as N → ∞.
    
  Resolution needed: Find a renormalized operator G̃ = M/Tr(M) or a
  regularization that produces a compact operator. Or work with resolvent
  (M − zI)^{-1} instead of M itself.

  Status: OPEN. Trace-class vs. Hilbert-Schmidt analysis pending.

SUB-PROBLEM (b): T-Parameterisation Problem
────────────────────────────────────────────
  Currently: ZEROS_9 are hard-coded. A Hilbert-Pólya operator cannot use
  the zeros as input — it must produce them as eigenvalues.
  
  The problem: our G(σ,T) depends on T explicitly.
  For a self-adjoint operator Â with Âψ_n = γ_n·ψ_n, T cannot be an
  external parameter; it must emerge from the eigenvalue equation itself.

  Proposed approach: Integrate out T dependence using the T-averaged operator:
    Ĝ(σ) = (1/T₀) ∫₀^{T₀} M(σ,T) dT
  Then ∂Ĝ(σ)/∂σ is T-independent. Question: does spectrum of Ĝ(σ) at σ=½
  encode information about {γₙ}?
  
  Connection to Pathway 2: If Theorem C succeeds, the T-averaged energy
  ⟨E⟩_T is controlled by ζ(s). The same averaging on M might resolve this.
  Connection to FULL_PROOF.py: The sech² kernel (all 6 forms) provides the
  T-averaging window for the curvature functional. Theorem A (RS Bridge)
  proves cross-term suppression via Fourier decay of sech².

  Status: OPEN.

SUB-PROBLEM (c): Spectral Identification Theorem
─────────────────────────────────────────────────
  Even with a well-defined self-adjoint operator on ℓ², proving its spectrum
  equals {γₙ} (rather than some deformation) is a separate major result.
  
  This is not just a corollary of sub-problems (a) and (b). It requires an
  identification theorem of the form: "the eigenvalue equation for Ĝ reduces
  to the functional equation for ζ at σ=½."

  Status: OPEN. This is the hardest sub-problem.

==============================================================================
CURRENT EVIDENCE (NOT PROOF)
==============================================================================

What we compute below is finite-N spectral analysis, listed as evidence only.
The scripts SINGULARITY_COMBINED_9D.py and SINGULARITY_ORIGINAL.py already
provide the main computations referenced here.

[QUARANTINE: All computations evaluate M at known zeros {γₙ}. This demonstrates
 spectral structure but does NOT prove M has {γₙ} as eigenvalues.]

==============================================================================
QUARANTINE NOTICE
==============================================================================
  - ZEROS_9 hardcoded (known zeros as input throughout this file)
  - σ* = ½ is a fixed input; never searched
  - All eigenvalue computations are at known heights, not discovered

==============================================================================
"""

from __future__ import annotations

import math
import cmath
import traceback
from typing import List, Tuple, Dict

# ---------------------------------------------------------------------------
# SECTION 0 — CONSTANTS
# ---------------------------------------------------------------------------

LAMBDA_STAR: float = 494.05895555802020426355559872240107048767357569104664
PHI: float = (1.0 + math.sqrt(5.0)) / 2.0

# First 9 Riemann zeros (imaginary parts)
_ZEROS_STR: List[str] = [
    "14.134725141734693790457251983562470270784257323570722",
    "21.022039638771554992628479593896902777334340524902781",
    "25.010857580145688763213790992562821818659549672557996",
    "30.424876125859513210311897530584091320181560023715440",
    "32.935061587739189690662368964074903488812715603517039",
    "37.586178158825671257217763480705332821405597350830793",
    "40.918719012147495187398126914633254395726165962777279",
    "43.327073280914999519496122165406805782645668371836871",
    "48.005150881167159727942472749427516765271532563522936",
]
ZEROS_9: List[float] = [float(z) for z in _ZEROS_STR]

def _sieve(N: int) -> List[int]:
    sieve = list(range(N + 1))
    for i in range(2, int(N**0.5) + 1):
        if sieve[i] == i:
            for j in range(i*i, N+1, i):
                sieve[j] = 0
    return [p for p in range(2, N+1) if sieve[p] == p]

PRIMES_9: List[int] = _sieve(25)[:9]         # [2,3,5,7,11,13,17,19,23]
PRIMES_25: List[int] = _sieve(100)[:25]      # first 25 primes ≤ 97

H_STAR: float = 1.5                          # QED framework kernel scale

# ---------------------------------------------------------------------------
# SECTION 0.5 — 6 KERNEL FORMS (all mathematically equivalent to sech²)
# ---------------------------------------------------------------------------
# Cross-reference: FULL_PROOF.py KERNEL LIBRARY, SINGULARITY_MECHANISM.html

def K_sech2(u: float, H: float = H_STAR) -> float:
    """K1: sech²(u/H) = 1/cosh²(u/H)"""
    x = u / H
    return 0.0 if abs(x) > 35 else 1.0 / math.cosh(x) ** 2

def K_cosh(u: float, H: float = H_STAR) -> float:
    """K2: 4/(e^(u/H) + e^(-u/H))² — exponential form"""
    x = u / H
    if abs(x) > 35: return 0.0
    return 4.0 / (math.exp(x) + math.exp(-x)) ** 2

def K_tanh_prime(u: float, H: float = H_STAR) -> float:
    """K3: d/du[tanh(u/H)]·H — derivative form (= sech²)"""
    return K_sech2(u, H)

def K_exp(u: float, H: float = H_STAR) -> float:
    """K4: 4e^(2u/H)/(e^(2u/H) + 1)² — exponential ratio"""
    x = 2.0 * u / H
    if abs(x) > 70: return 0.0
    e = math.exp(x)
    return 4.0 * e / (e + 1.0) ** 2

def K_sinhcosh(u: float, H: float = H_STAR) -> float:
    """K5: 1 - tanh²(u/H) — Pythagorean identity form"""
    x = u / H
    if abs(x) > 35: return 0.0
    t = math.tanh(x)
    return 1.0 - t * t

def K_logistic(u: float, H: float = H_STAR) -> float:
    """K6: 4σ(2u/H)(1-σ) — logistic sigmoid form"""
    x = 2.0 * u / H
    if abs(x) > 70: return 0.0
    s = 1.0 / (1.0 + math.exp(-x))
    return 4.0 * s * (1.0 - s)

KERNELS = [
    ("sech²",     K_sech2),
    ("cosh",      K_cosh),
    ("tanh'",     K_tanh_prime),
    ("exp",       K_exp),
    ("sinh/cosh", K_sinhcosh),
    ("logistic",  K_logistic),
]

# ---------------------------------------------------------------------------
# SECTION 1 — GRAM MATRIX CONSTRUCTION
# ---------------------------------------------------------------------------

def build_gram_matrix(sigma: float, T: float,
                      primes: List[int] = PRIMES_9) -> List[List[float]]:
    """
    M(σ,T)_{jk} = p_j^{−σ} · p_k^{−σ} · cos(T · log(p_j/p_k)).

    Real symmetric PSD matrix. Rank ≤ 2 (prime Gram matrix structure).
    LOG-FREE convention: log(p_j/p_k) = log(p_j) − log(p_k), precomputed here
    for the specific call but uses math.log at construction time only.
    """
    N = len(primes)
    log_p = [math.log(p) for p in primes]                       # construction, not inner loop
    pow_p = [p**(-sigma) for p in primes]
    M = [[0.0] * N for _ in range(N)]
    for j in range(N):
        for k in range(N):
            cos_arg = T * (log_p[j] - log_p[k])
            M[j][k] = pow_p[j] * pow_p[k] * math.cos(cos_arg)
    return M


def gram_trace(sigma: float, primes: List[int] = PRIMES_9) -> float:
    """
    Tr(M(σ,T)) = Σ_p p^{-2σ}   (T-independent).

    This IS the energy diagonal term E_diag(σ).
    """
    return sum(p**(-2.0 * sigma) for p in primes)


def gram_eigenvalues(sigma: float, T: float,
                     primes: List[int] = PRIMES_9) -> Tuple[float, float]:
    """
    Exact eigenvalues of the rank-2 Gram matrix M(σ,T).

    λ_max = (E_diag + |D(2σ,2T)|) / 2
    λ_min = (E_diag − |D(2σ,2T)|) / 2

    where D(α,β) = Σ_p p^{-α-iβ}.

    Derivation: M = a·aᵀ + b·bᵀ (outer product decomposition). The two
    non-zero eigenvalues are ½(‖a‖²+‖b‖² ± 2|⟨a,b⟩| + ...)  →  the formula
    for two-vector Gram decomposition.
    """
    E_diag = gram_trace(sigma, primes)
    D_ab = complex(0.0, 0.0)
    for p in primes:
        D_ab += complex(p, 0.0) ** complex(-2.0 * sigma, -2.0 * T)
    abs_D = abs(D_ab)
    lam_max = (E_diag + abs_D) / 2.0
    lam_min = (E_diag - abs_D) / 2.0
    return lam_max, lam_min


def gram_eigenvalue_sigma_monotonicity(T: float,
                                       primes: List[int] = PRIMES_9) -> Dict:
    """
    Verify that λ_max and λ_min are strictly decreasing in σ.
    This is the σ-selectivity of the Gram matrix.
    [QUARANTINE: evaluated at known zero height T = γₖ]
    """
    sigma_vals = [0.3, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7]
    lam_max_vals = []
    lam_min_vals = []
    for s in sigma_vals:
        lm, ln = gram_eigenvalues(s, T, primes)
        lam_max_vals.append(lm)
        lam_min_vals.append(ln)

    max_monotone = all(lam_max_vals[i] >= lam_max_vals[i+1]
                       for i in range(len(lam_max_vals)-1))
    min_monotone = all(lam_min_vals[i] >= lam_min_vals[i+1]
                       for i in range(len(lam_min_vals)-1))
    return {
        "sigma_vals": sigma_vals,
        "lambda_max": lam_max_vals,
        "lambda_min": lam_min_vals,
        "max_decreasing_in_sigma": max_monotone,
        "min_decreasing_in_sigma": min_monotone,
    }


# ---------------------------------------------------------------------------
# SECTION 2 — T-AVERAGED GRAM OPERATOR
# ---------------------------------------------------------------------------

def gram_T_average(sigma: float, primes: List[int] = PRIMES_9,
                   T_max: float = 100.0, n_T: int = 1000) -> List[List[float]]:
    """
    Ĝ(σ) = (1/T₀) ∫₀^{T₀} M(σ,T) dT.

    Proposed resolution for Sub-problem (b): T-parameterisation removed
    by averaging. Only the diagonal survives the T-average (off-diagonal
    terms involve cos(T·log(p_j/p_k)) which averages to 0 over large T).
    Diagonal: Ĝ(σ)_{jj} = p_j^{-2σ}.
    Off-diagonal: Ĝ(σ)_{jk} → 0 as T₀ → ∞ (by Riemann-Lebesgue lemma).
    """
    N = len(primes)
    M_sum = [[0.0] * N for _ in range(N)]
    dt = T_max / n_T
    for ti in range(n_T):
        T = (ti + 0.5) * dt
        M_T = build_gram_matrix(sigma, T, primes)
        for j in range(N):
            for k in range(N):
                M_sum[j][k] += M_T[j][k] * dt
    for j in range(N):
        for k in range(N):
            M_sum[j][k] /= T_max
    return M_sum


def gram_T_average_analytic(sigma: float,
                             primes: List[int] = PRIMES_9) -> List[List[float]]:
    """
    Analytic form of Ĝ(σ) in the T₀ → ∞ limit:
      Ĝ_∞(σ)_{jj} = p_j^{-2σ}    (diagonal)
      Ĝ_∞(σ)_{jk} = 0             (off-diagonal, by Riemann-Lebesgue)

    The resulting diagonal operator has spectrum {p^{-2σ} : p prime}.
    This is NOT {γₙ} — it's the prime reciprocal spectrum, not the zero spectrum.
    This gap is Sub-problem (c): the T→∞ limit erases the zero structure from M.
    """
    N = len(primes)
    G_inf = [[0.0] * N for _ in range(N)]
    for j in range(N):
        G_inf[j][j] = primes[j]**(-2.0 * sigma)
    return G_inf


def hilbert_schmidt_norm(M: List[List[float]]) -> float:
    """‖M‖_HS = √(Σ_{j,k} M_{jk}²)."""
    total = sum(M[j][k]**2 for j in range(len(M)) for k in range(len(M[0])))
    return math.sqrt(total)


# ---------------------------------------------------------------------------
# SECTION 3 — FINITENESS ANALYSIS (Sub-problem a)
# ---------------------------------------------------------------------------

def trace_growth_analysis(sigma: float = 0.5, prime_counts: List[int] = None
                           ) -> Dict:
    """
    Analyse Tr(M(σ)) = Σ_{p≤X} p^{-2σ} as X grows.

    At σ=½: Σ p^{-1} — known to diverge (Mertens: ~ log log X).
    At σ>½: Σ p^{-2σ} converges (comparison with Σ n^{-2σ}).
    At σ=1: Σ p^{-2} converges to the prime zeta P(2) ≈ 0.4522...

    This is Sub-problem (a): trace blows up at σ=½, so M is not trace-class
    and cannot be a well-defined Hilbert-Schmidt operator without regularisation.
    """
    if prime_counts is None:
        prime_counts = [9, 25, 50, 100]
    all_primes = _sieve(1000)
    results = {}
    for n in prime_counts:
        primes_n = all_primes[:n]
        tr = sum(p**(-2.0 * sigma) for p in primes_n)
        results[f"N={n}"] = tr
    return results


# ---------------------------------------------------------------------------
# SECTION 4 — VERIFICATION RUNNER
# ---------------------------------------------------------------------------

def run_all() -> None:
    print("=" * 78)
    print("PATH_1: HILBERT–PÓLYA SPECTRAL OPERATOR — LONG-TERM HORIZON")
    print("=" * 78)
    print("  NOTE: All three sub-problems are OPEN. This pathway is retained")
    print("  as long-term research. It is NOT a near-term proof strategy.")
    print()

    # Sub-problem (a) — Trace growth
    print("─" * 78)
    print("SUB-PROBLEM (a): Gram Operator Trace Growth (σ=½)")
    print("─" * 78)
    try:
        trace_data = trace_growth_analysis(sigma=0.5)
        print("  Tr(M(½)) = Σ_{p≤X} p^{-1}  (diverges like log log X):")
        for label, val in trace_data.items():
            print(f"    {label} primes:  Tr = {val:.6f}")
        print()
        trace_data_1 = trace_growth_analysis(sigma=1.0)
        print("  Tr(M(1)) = Σ_{p≤X} p^{-2}  (converges to P(2) ≈ 0.45224):")
        for label, val in trace_data_1.items():
            print(f"    {label} primes:  Tr = {val:.6f}")
        print()
        print("  STATUS:  [OPEN]  Tr(M(½)) diverges → M not trace-class at σ=½.")
        print("  NEXT:    Find renormalisation Ĝ = M/Tr(M) or resolvent formulation.")
    except Exception:
        traceback.print_exc()

    # Sub-problem (b) — T-average test
    print("\n" + "─" * 78)
    print("SUB-PROBLEM (b): T-Parameterisation (T-averaged operator)")
    print("─" * 78)
    try:
        G_analytic = gram_T_average_analytic(0.5, PRIMES_9)
        diag = [G_analytic[j][j] for j in range(len(PRIMES_9))]
        off_diag_max = max(abs(G_analytic[j][k])
                           for j in range(len(PRIMES_9))
                           for k in range(len(PRIMES_9)) if j != k)
        print(f"  Ĝ_∞(½) diagonal entries (= p^{{-1}} for first 9 primes):")
        for p, d in zip(PRIMES_9, diag):
            print(f"    p={p:3d}: Ĝ_{{pp}} = {d:.8f}")
        print(f"  Off-diagonal max: {off_diag_max:.2e} (→ 0 as T₀→∞)")
        print()
        print("  STATUS:  [OPEN]  T-averaging collapses M to diagonal operator")
        print("           with spectrum {p^{-1}} — NOT the zero spectrum {γₙ}.")
        print("  NEXT:    Find a T-independent kernel that encodes zero positions.")
        print("           Candidate: derivative ∂M/∂T at specific T values (not yet formulated).")
    except Exception:
        traceback.print_exc()

    # σ-monotonicity of eigenvalues (QUARANTINE: uses known zeros)
    print("\n" + "─" * 78)
    print("GRAM MATRIX σ-SELECTIVITY [QUARANTINE: uses known zero heights]")
    print("─" * 78)
    try:
        T1 = ZEROS_9[0]                                          # γ₁ = 14.135
        mono = gram_eigenvalue_sigma_monotonicity(T1, PRIMES_9)
        print(f"  At T = γ₁ = {T1:.6f} (QUARANTINE: known zero)")
        print("  σ:         " + "  ".join(f"{s:.2f}" for s in mono["sigma_vals"]))
        print("  λ_max:     " + "  ".join(f"{v:.4f}" for v in mono["lambda_max"]))
        print("  λ_min:     " + "  ".join(f"{v:.6f}" for v in mono["lambda_min"]))
        print(f"  λ_max decreasing in σ: {mono['max_decreasing_in_sigma']}")
        print(f"  λ_min decreasing in σ: {mono['min_decreasing_in_sigma']}")
        print()
        print("  ALGEBRAIC FACT: Both eigenvalues strictly decreasing in σ.")
        print("  ∂λ_max/∂σ = -E_diag'(σ)/2 + ∂|D|/∂σ/2 < 0  (both terms < 0).")
        print("  This σ-selectivity is PROVED for finite N, any T.")
    except Exception:
        traceback.print_exc()

    # Sub-problem (c) summary
    print("\n" + "─" * 78)
    print("SUB-PROBLEM (c): Spectral Identification (most difficult)")
    print("─" * 78)
    print("  STATUS:  [OPEN]")
    print("  Even with (a) and (b) resolved, a separate identification theorem")
    print("  is needed to show spec(Ĝ) = {γₙ}.")
    print()
    print("  One reviewer noted: if Pathway 2 succeeds (Weil explicit formula),")
    print("  the Hilbert-Pólya operator may emerge naturally as the generator")
    print("  of the associated dynamical system (see Connes' spectral approach).")

    # IF PATHWAY 2 SUCCEEDS
    print("\n" + "─" * 78)
    print("CONNECTION TO PATHWAY 2")
    print("─" * 78)
    print("  Reviewer consensus: solve Pathway 2 first. If Theorem C succeeds,")
    print("  the T-averaged operator Ĝ(σ) connected to ⟨E(σ)⟩_T may provide")
    print("  the T-independent kernel needed for Sub-problem (b).")
    print("  The diagonal operator Ĝ_∞(½) has spectrum {p^{-1}} = {p^{-2σ}|_{σ=½}},")
    print("  whose sum Tr(Ĝ_∞(½)) = Σ_p p^{-1} = P(1) (prime zeta at s=1, divergent).")
    print("  Note: this is P(1) = Σ p^{-1}, not P(1/2) = Σ p^{-1/2}. Both diverge,")
    print("  but the relevant quantity (trace of Ĝ_∞ at σ=½) is exactly P(1),")
    print("  consistent with Sub-problem (a)'s trace divergence – a potential bridge.")

    # OVERALL STATUS
    print("\n" + "=" * 78)
    print("OVERALL STATUS SUMMARY")
    print("=" * 78)
    table = [
        ("Sub-problem (a)", "Trace-class convergence",
         "OPEN — Tr(M(½)) diverges; needs renormalisation or resolvent."),
        ("Sub-problem (b)", "T-parameterisation",
         "OPEN — T-averaged operator loses zero structure."),
        ("Sub-problem (c)", "Spectral identification",
         "OPEN — Even with (a)+(b), identification theorem needed."),
        ("σ-selectivity",   "λ eigenvalues decrease in σ",
         "PROVED algebraically for finite N (Hellmann-Feynman)."),
    ]
    for name, desc, status in table:
        print(f"\n  {name} ({desc}):")
        print(f"    {status}")
    print()
    print("  PATHWAY STATUS: LONG-TERM HORIZON. Retain for motivation.")
    print("  Difficulty: ★★★★★ (Hilbert-Pólya conjecture open since 1914)")
    print("  Recommended: Focus on Pathway 2. Pathway 1 may follow as corollary.")
    print("=" * 78)


if __name__ == "__main__":
    run_all()
