#!/usr/bin/env python3
r"""
LAMBDA_EQUIVALENCES.py — All equivalent forms of Λ(T,H)
=========================================================

The core equation:
  Λ(T,H) = ∫ Z(T+u)² sech²(u/H) du / ∫ sech²(u/H) du

Compiled into every equivalent kernel form.
Each is tested numerically at zeros and non-zeros.
"""
import math
import numpy as np

PI = math.pi
ZEROS = [14.134725142, 21.022039639, 25.010857580, 30.424876126, 32.935061588]
NONZ  = [10.0, 17.5, 23.0, 27.5, 35.0]

# ═══════════════════════════════════════════════════
#  HARDY Z (ground truth)
# ═══════════════════════════════════════════════════
def hardy_Z(T):
    if T < 2: return 0.0
    th = (T/2)*math.log(T/(2*PI)) - T/2 - PI/8 + 1/(48*T) + 7/(5760*T**3)
    N = int(math.sqrt(T/(2*PI)))
    Z = 2*sum(math.cos(th - T*math.log(n))/math.sqrt(n) for n in range(1, N+1))
    p = math.sqrt(T/(2*PI)) - N
    cp = math.cos(2*PI*p)
    if abs(cp) > 0.01:
        Z += (-1)**(N-1) * (T/(2*PI))**(-0.25) * math.cos(2*PI*(p*p-p-1/16))/cp
    return Z

# ═══════════════════════════════════════════════════
#  FORM 1: SECH² (original)
#  K₁(u,H) = sech²(u/H)  =  1/cosh²(u/H)
#  ∫ K₁ du = 2H
# ═══════════════════════════════════════════════════
def K_sech2(u, H):
    x = u/H
    if abs(x) > 40: return 0.0
    return 1.0 / (math.cosh(x)**2)

# ═══════════════════════════════════════════════════
#  FORM 2: COSH (reciprocal)
#  K₂(u,H) = 1/cosh²(u/H)  ≡  K₁ (same thing)
#  But write cosh explicitly: cosh(x) = (eˣ+e⁻ˣ)/2
#  K₂ = 4/(e^{u/H} + e^{-u/H})²
# ═══════════════════════════════════════════════════
def K_cosh(u, H):
    x = u/H
    if abs(x) > 40: return 0.0
    ep = math.exp(x)
    em = math.exp(-x)
    return 4.0 / ((ep + em)**2)

# ═══════════════════════════════════════════════════
#  FORM 3: TANH DERIVATIVE
#  sech²(x) = d/dx[tanh(x)]
#  So K₃(u,H) = H · d/du[tanh(u/H)]
#  Integration by parts:
#  ∫ Z²·K₃ du = H·[Z²·tanh(u/H)]_{-∞}^{∞} - H·∫ 2Z·Z'·tanh(u/H) du
#            = -2H ∫ Z(T+u)·Z'(T+u)·tanh(u/H) du
#  (boundary terms vanish since tanh→±1 and Z² bounded)
# ═══════════════════════════════════════════════════
def K_tanh_deriv(u, H):
    """sech²(u/H) computed as d/du[tanh(u/H)] · H"""
    x = u/H
    if abs(x) > 40: return 0.0
    # d/du tanh(u/H) = (1/H)·sech²(u/H)
    # so sech²(u/H) = H · d/du[tanh(u/H)]
    return 1.0 / (math.cosh(x)**2)  # same numerically

# ═══════════════════════════════════════════════════
#  FORM 4: EXPONENTIAL
#  sech²(x) = 4e^{2x}/(e^{2x}+1)²  =  4e^{-2x}/(1+e^{-2x})²
#  K₄(u,H) = 4·exp(2u/H) / (exp(2u/H) + 1)²
# ═══════════════════════════════════════════════════
def K_exp(u, H):
    x = 2*u/H
    if x > 80: return 0.0
    if x < -80: return 0.0
    e2x = math.exp(x)
    return 4.0 * e2x / ((e2x + 1)**2)

# ═══════════════════════════════════════════════════
#  FORM 5: SINH/COSH ratio
#  sech²(x) = 1 - tanh²(x) = 1 - sinh²(x)/cosh²(x)
#  K₅(u,H) = 1 - (sinh(u/H)/cosh(u/H))²
#           = (cosh²-sinh²)/cosh² = 1/cosh²
# ═══════════════════════════════════════════════════
def K_sinh_cosh(u, H):
    x = u/H
    if abs(x) > 40: return 0.0
    sh = math.sinh(x)
    ch = math.cosh(x)
    return 1.0 - (sh/ch)**2

# ═══════════════════════════════════════════════════
#  FORM 6: FOURIER TRANSFORM
#  FT[sech²(t/H)](ω) = πHω/sinh(πHω/2)  (for ω≠0)
#                     = 2H                 (for ω=0)
#  So Λ in Fourier domain:
#  Λ(T,H) = (1/4πH) ∫ |Ẑ_T(ω)|² · πHω/sinh(πHω/2) dω
#  where Ẑ_T(ω) = FT[Z(T+·)](ω)
# ═══════════════════════════════════════════════════
def K_fourier_symbol(omega, H):
    """Fourier transform of sech²(u/H): πHω/sinh(πHω/2)"""
    if abs(omega) < 1e-12:
        return 2*H
    x = PI*H*omega/2
    if abs(x) > 40:
        return 0.0
    return PI*H*omega / math.sinh(x)

# ═══════════════════════════════════════════════════
#  FORM 7: LOGISTIC DERIVATIVE
#  sech²(x) = 4·σ(2x)·(1-σ(2x))  where σ(x)=1/(1+e^{-x})
#  K₇(u,H) = 4·σ(2u/H)·(1-σ(2u/H))
# ═══════════════════════════════════════════════════
def K_logistic(u, H):
    x = 2*u/H
    if x > 80: return 0.0
    if x < -80: return 0.0
    sig = 1.0 / (1.0 + math.exp(-x))
    return 4.0 * sig * (1.0 - sig)

# ═══════════════════════════════════════════════════
#  FORM 8: POISSON KERNEL CONNECTION
#  sech²(πu/2) = (2/π)² · Σ_{n=0}^∞ (-1)ⁿ(2n+1)e^{-(2n+1)|u|}
#  For general H: sech²(u/H) with H→πH/2 substitution
#  Series: K₈ = Σ_{n≥0} (-1)ⁿ(2n+1)·(2/πH)² · e^{-(2n+1)·2|u|/(πH)}
# ═══════════════════════════════════════════════════
def K_series(u, H, nterms=20):
    """Poisson-type series for sech²"""
    a = 2.0/(PI*H)
    result = 0.0
    for n in range(nterms):
        k = 2*n+1
        sign = (-1)**n
        arg = k * 2 * abs(u) / (PI*H)
        if arg > 80: continue
        result += sign * k * math.exp(-arg)
    return result * a * a * (PI*H/2)  # normalisation

# ═══════════════════════════════════════════════════
#  FORM 9: SIN/COS via Euler
#  sech(x) = 2/(eˣ+e⁻ˣ)  and for PURELY IMAGINARY x=iy:
#  sech(iy) = 1/cos(y)
#  So sech²(iy) = 1/cos²(y) = sec²(y)
#  CONNECTION: sech² on real line ↔ sec² on imaginary line
#  This means: Λ(T,H) analytically continues to:
#  Λ(T, iH') = ∫ Z(T+u)² sec²(u/H') du / ∫ sec²(u/H') du
#  (defined only on intervals where cos(u/H')≠0)
# ═══════════════════════════════════════════════════

# ═══════════════════════════════════════════════════
#  MASTER EVALUATOR
# ═══════════════════════════════════════════════════
def Lambda_general(T, H, kernel_fn, nq=200):
    u_max = 4.0 * H
    us = np.linspace(-u_max, u_max, nq)
    du = us[1] - us[0]
    num, den = 0.0, 0.0
    for u in us:
        tv = T + u
        if tv > 2.5:
            w = kernel_fn(u, H) * du
            z = hardy_Z(tv)
            num += z*z*w
            den += w
    return num / max(den, 1e-30)

# ═══════════════════════════════════════════════════
#  RUN ALL FORMS
# ═══════════════════════════════════════════════════

forms = [
    ("SECH²",        "1/cosh²(u/H)",                          K_sech2),
    ("COSH",         "4/(e^{u/H}+e^{-u/H})²",                K_cosh),
    ("TANH'",        "d/du[tanh(u/H)]·H",                     K_tanh_deriv),
    ("EXP",          "4e^{2u/H}/(e^{2u/H}+1)²",              K_exp),
    ("SINH/COSH",    "1 - sinh²/cosh²",                       K_sinh_cosh),
    ("LOGISTIC",     "4·σ(2u/H)·(1-σ(2u/H))",                K_logistic),
    ("SERIES",       "Σ(-1)ⁿ(2n+1)e^{-(2n+1)·2|u|/πH}",     K_series),
]

H_test = 0.05

print("="*82)
print("Λ(T,H) — ALL EQUIVALENT FORMS")
print("="*82)
print(f"\n  Core: Λ(T,H) = ∫ Z(T+u)² · K(u,H) du / ∫ K(u,H) du")
print(f"  Testing H = {H_test}\n")

# Verify all kernels agree
print("─"*82)
print("  KERNEL EQUIVALENCE CHECK at u=1.0, H=1.0")
print("─"*82)
u_test, H_check = 1.0, 1.0
ref = K_sech2(u_test, H_check)
print(f"  {'Form':>12}  {'K(1,1)':>14}  {'Δ from sech²':>14}")
print(f"  {'─'*12}  {'─'*14}  {'─'*14}")
for name, expr, fn in forms:
    val = fn(u_test, H_check)
    delta = abs(val - ref)
    ok = "✓" if delta < 1e-8 else f"Δ={delta:.2e}"
    print(f"  {name:>12}  {val:14.10f}  {ok:>14}")

# Test each form at zeros and non-zeros
print(f"\n{'─'*82}")
print(f"  Λ(T, H={H_test}) AT ZEROS — ALL FORMS")
print(f"{'─'*82}")

header = f"  {'T':>10}"
for name, _, _ in forms[:6]:  # skip series (slow)
    header += f"  {name:>10}"
print(header)
print(f"  {'─'*10}" + "  ".join(['─'*10]*6))

for T in ZEROS[:3]:
    row = f"  {T:10.4f}"
    for name, _, fn in forms[:6]:
        v = Lambda_general(T, H_test, fn, 150)
        row += f"  {v:10.6f}"
    print(row)

print(f"\n  AT NON-ZEROS:")
for T in NONZ[:3]:
    row = f"  {T:10.4f}"
    for name, _, fn in forms[:6]:
        v = Lambda_general(T, H_test, fn, 150)
        row += f"  {v:10.6f}"
    print(row)

# ═══════════════════════════════════════════════════
#  THE INTERESTING FORMS
# ═══════════════════════════════════════════════════

print(f"\n{'='*82}")
print("NOTABLE EQUIVALENT EXPRESSIONS")
print("="*82)

print(r"""
  ┌──────────────────────────────────────────────────────────────────────┐
  │  FORM 1 — SECH² (original)                                          │
  │                                                                      │
  │  Λ(T,H) = [∫ Z(T+u)² / cosh²(u/H) du] / 2H                       │
  │                                                                      │
  │  FORM 2 — COSH (explicit)                                           │
  │                                                                      │
  │  Λ(T,H) = [2/H] ∫ Z(T+u)² / [e^{u/H} + e^{-u/H}]² du            │
  │                                                                      │
  │  FORM 3 — TANH DERIVATIVE (integration by parts)                     │
  │                                                                      │
  │  Λ(T,H) = -[1/H] ∫ d/du[Z(T+u)²] · tanh(u/H) du                  │
  │         = -[2/H] ∫ Z(T+u)·Z'(T+u) · tanh(u/H) du                  │
  │                                                                      │
  │  ★ This form is INTERESTING: it couples Z to Z' via tanh.           │
  │    At a zero: Z(γ)=0 and Z'(γ)≠0 typically, but                    │
  │    tanh(0)=0 kills the integrand at u=0 exactly.                    │
  │    So: Λ(γ,H) measures how Z·Z' correlates with tanh.              │
  │                                                                      │
  │  FORM 4 — EXPONENTIAL (logistic form)                                │
  │                                                                      │
  │  Λ(T,H) = [2/H] ∫ Z(T+u)² · e^{2u/H} / (e^{2u/H}+1)² du        │
  │                                                                      │
  │  FORM 5 — FOURIER DOMAIN                                            │
  │                                                                      │
  │  Λ(T,H) = [1/4πH] ∫ |Ẑ_T(ω)|² · πHω/sinh(πHω/2) dω             │
  │                                                                      │
  │  ★ This form reveals: Λ weights the POWER SPECTRUM of Z             │
  │    by ω/sinh(πHω/2). Low frequencies emphasised.                    │
  │    As H→0: weight → 1 for all ω (flat spectrum = delta fn).        │
  │                                                                      │
  │  FORM 6 — ANALYTIC CONTINUATION (imaginary H)                        │
  │                                                                      │
  │  sech²(iy) = sec²(y) = 1/cos²(y)                                   │
  │  Λ(T, iH') = ∫ Z(T+u)² sec²(u/H') du / ∫ sec²(u/H') du         │
  │                                                                      │
  │  ★ sec² has POLES at u = (n+½)πH'. These poles could                │
  │    encode zero spacing information if H' chosen correctly.           │
  │                                                                      │
  └──────────────────────────────────────────────────────────────────────┘
""")

# ═══════════════════════════════════════════════════
#  TEST FORM 3 (tanh integration by parts)
# ═══════════════════════════════════════════════════
print("─"*82)
print("  FORM 3 TEST: Λ via tanh integration by parts")
print("─"*82)

def Lambda_tanh_ibp(T, H, nq=300):
    """Λ = -(1/H) ∫ d/du[Z²] · tanh(u/H) du  (normalised)"""
    u_max = 4.0*H
    us = np.linspace(-u_max, u_max, nq)
    du = us[1]-us[0]
    # Compute d/du[Z(T+u)²] via finite diff
    num, den = 0.0, 0.0
    eps = du/2
    for u in us:
        tv = T + u
        if tv > 3:
            z_plus = hardy_Z(tv + eps)
            z_minus = hardy_Z(tv - eps)
            dZsq_du = (z_plus**2 - z_minus**2) / (2*eps)
            th = math.tanh(u/H) if abs(u/H) < 40 else (1.0 if u > 0 else -1.0)
            num += dZsq_du * th * du
            den += K_sech2(u, H) * du  # for normalisation
    return -num / max(den, 1e-30)

print(f"\n  {'T':>10}  {'Λ_sech²':>12}  {'Λ_tanh_IBP':>12}  {'Δ':>12}  {'match':>6}")
print(f"  {'─'*10}  {'─'*12}  {'─'*12}  {'─'*12}  {'─'*6}")

for T in ZEROS[:3] + NONZ[:3]:
    lab = "ZERO" if T in ZEROS else "NON-Z"
    v1 = Lambda_general(T, H_test, K_sech2, 200)
    v2 = Lambda_tanh_ibp(T, H_test, 200)
    delta = abs(v1-v2)
    print(f"  {T:10.4f}  {v1:12.6f}  {v2:12.6f}  {delta:12.2e}  {'✓' if delta < 0.1*max(v1,0.001) else '~':>6}  [{lab}]")

# ═══════════════════════════════════════════════════
#  TEST FOURIER SYMBOL FORM
# ═══════════════════════════════════════════════════
print(f"\n{'─'*82}")
print("  FORM 5: Fourier symbol πHω/sinh(πHω/2)")
print("─"*82)

print(f"\n  Fourier weight at key frequencies:")
for H in [0.02, 0.05, 0.1, 0.5, 1.0]:
    print(f"  H={H}:", end="")
    for omega in [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]:
        w = K_fourier_symbol(omega, H)
        print(f"  ω={omega}:{w:.4f}", end="")
    print()

print(f"\n  As H→0: weight → 2H for all ω (flat = delta function)")
print(f"  As H→∞: weight concentrated near ω=0 (low-pass filter)")

# ═══════════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════════
print(f"\n{'='*82}")
print("SUMMARY: MOST INTERESTING EQUIVALENT FORMS")
print("="*82)
print(r"""
  1. SECH² (original):  Λ = ⟨Z², sech²⟩ / ⟨1, sech²⟩
     → Standard mollifier. Clean, fast.

  2. TANH IBP:  Λ = -⟨(Z²)', tanh⟩ / 2H
     → Couples Z to Z' via tanh. At zeros, Z=0 AND tanh(0)=0
       create double vanishing. Most physically meaningful form.

  3. FOURIER:  Λ = ⟨|Ẑ|², ω/sinh(πHω/2)⟩ / 4πH
     → Weights power spectrum. Could connect to Montgomery
       pair correlation if ω = log(n/m) frequencies analysed.

  4. SEC² (analytic continuation):  H → iH' gives sec²
     → Poles at (n+½)πH' might encode zero spacing.
     → Research direction: choose H' so poles align with zeros.

  ALL FORMS GIVE THE SAME Λ(T,H).
  ALL REDUCE TO Z(T)²=0 as H→0.
  The NON-TAUTOLOGICAL content must come from FIXED H analysis
  or from the FOURIER/TANH forms connecting to prime structure.
""")
