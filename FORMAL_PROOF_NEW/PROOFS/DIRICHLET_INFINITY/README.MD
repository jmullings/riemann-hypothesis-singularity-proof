# DIRICHLET_INFINITY_SERIES.py — Step 7 Dirichlet Polynomial Wave Evaluation

**Author:** Jason Mullings · BetaPrecision.com  
**Date:** March 15, 2026  
**Purpose:** Independent, high-precision evaluation of the single open inequality in the σ-selectivity proof chain

---

## What This Script Does

This script provides a standalone, high-precision numerical evaluation of
the central inequality in Step 7 of the 12-step RH proof chain:

    Re⟨TD²b, b⟩  =  ⟨TDb, Db⟩  −  (1/4π) ∫ Λ″_H(τ) |D₀(T₀+τ)|² dτ  ≥  0

It implements finite Dirichlet polynomials D₀ and D₁ with the correct
weights n^{-1/2} and log(n), uses the sech² Mellin kernel Λ_H and its
second derivative Λ″_H, and numerically approximates both the PSD term
and the cross-term correction via trapezoidal quadrature at arbitrary
precision (default 50 decimal digits via mpmath).

This is the **one inequality** that, if proved analytically for all T₀
and N, completes the Riemann Hypothesis via the σ-selectivity framework.

---

## Mathematical Background

### The Objects

**Dirichlet polynomial (partial sum of ζ at σ = 1/2):**

    D₀(T; N) = Σ_{n=1}^{N} n^{-1/2} e^{-iT ln n}

This is S_N(1/2, T), the partial sum that approximates ζ(1/2 + iT) via
the Riemann-Siegel approximate functional equation. It is NOT equal to
ζ(1/2 + iT) — the Dirichlet series diverges on the critical line. The
connection to ζ is through the RS bridge (a proved theorem), not through
direct summation.

**Multiplicative derivative:**

    D₁(T; N) = -i Σ_{n=1}^{N} (ln n) n^{-1/2} e^{-iT ln n}

This is the derivative ∂D₀/∂T, which corresponds to the weighted
Dirichlet polynomial with coefficients (ln n) n^{-1/2}.

**Sech² Mellin kernel:**

    Λ_H(τ) = 2 sech²(Hτ)

This is the Mellin symbol of the sech²-weighted operator T_H, proved
in Phase 15 to satisfy Λ_H(τ) = 2π sech²(τ/H) in the Phase 15/16/17
normalisation. The script uses the equivalent form Λ_H(t) = 2 sech²(Ht).

**Second derivative:**

    Λ″_H(τ) = 2 × [4H² sech²(Hτ) tanh²(Hτ) − 2H² sech⁴(Hτ)]

This changes sign at |τ| = (1/H) arccosh(√(3/2)), creating an inner
negative region and outer positive tails. The integral ∫ Λ″_H dτ = 0
(boundary terms vanish), which is critical for the mean-zero rewriting
trick in the MV roadmap.

### The Three Quantities

**PSD term (always ≥ 0 by Parseval):**

    ⟨TDb, Db⟩ = (1/2π) ∫ Λ_H(τ) |D₁(T₀+τ)|² dτ

This is proved non-negative for every finite N via the Parseval identity
(Phase 16 FPE.7): since Λ_H(τ) ≥ 0 and |D₁|² ≥ 0, the integrand is
non-negative everywhere.

**Cross-term correction:**

    (1/4π) ∫ Λ″_H(τ) |D₀(T₀+τ)|² dτ

This involves the signed second derivative Λ″_H weighted by the energy
|D₀|². Because Λ″_H changes sign, this integral can be positive or
negative. The cross-term identity (Phase 16 FPE.8) proves:

    Re⟨TD²b, b⟩ = ⟨TDb, Db⟩ − (1/4π) ∫ Λ″_H |D₀|² dτ

**Central Step 7 quantity:**

    Re⟨TD²b, b⟩ = PSD term − cross-term correction

Step 7 requires this to be ≥ 0 for all T₀ and N.

### Why This Matters

The 12-step proof chain reduces RH to this single inequality:

    Steps 1–6: PROVED (exact algebra + Parseval + PSD)
    Step 7:    Re⟨TD²b, b⟩ ≥ 0  ← THIS SCRIPT EVALUATES
    Steps 8–12: PROVED (given Step 7)

If Step 7 holds for all T₀ and N, then:
- R ≥ −4M₂ (Step 8, from Steps 5+7)
- F̄₂ ≥ 0 (Step 9, averaged convexity)
- Smoothed contradiction yields zero-free region (Steps 10–12)
- RH follows for T₀ ≥ T_min

---

## Important Caveats

### What this script IS

- A high-precision numerical evaluator for Step 7 at individual (H, N, T₀)
- A diagnostic tool for scanning parameter space
- An independent cross-check against the Phase 07/17 verification suite
- Evidence-gathering for the MV roadmap

### What this script IS NOT

- A proof of Step 7 (numerical evaluation at finitely many points ≠ proof)
- A claim that ζ(1/2+iT) equals the Dirichlet series (it doesn't — the
  series diverges on the critical line)
- A substitute for the analytical mean-value bound needed to close A3

### The Dirichlet series convergence issue

The infinite Dirichlet series Σ n^{-s} converges only for Re(s) > 1.
At σ = 1/2, the series DIVERGES. The finite polynomial D₀(T; N) is an
approximation whose connection to ζ(1/2+iT) is established through the
Riemann-Siegel approximate functional equation (a proved theorem), NOT
through term-by-term convergence. The Step 7 inequality operates on
finite polynomials D₀ and D₁ for each fixed N. The RS bridge then
connects these finite-N results to statements about ζ.

---

## Usage

### Prerequisites

```bash
pip install numpy mpmath
```

### Basic Evaluation

```bash
python3 DIRICHLET_INFINITY_SERIES.py
```

Output:
```
DIRICHLET_INFINITY_SERIES.py
H = 1.5 N = 50 T0 = 30.0
PSD term <TDb,Db> ≈ 1.8818...
Correction term (1/(4π))∫Λ_H''|D0|^2 ≈ 0.5796...
Re⟨T D^2 b, b⟩ ≈ 1.3022...   (real part ≈ 1.3022...)
```

### Parameter Scan (Step 7 Diagnostic)

```python
import numpy as np
from DIRICHLET_INFINITY_SERIES import central_step7

H = 1.5
N = 50
for T0 in np.linspace(10, 100, 20):
    psd, corr, val = central_step7(T0, N, H)
    print(f"T0={T0:6.1f}  Re<TD²b,b>={float(val.real):+.6f}  "
          f"PSD={float(psd.real):.4f}  corr={float(corr.real):+.4f}")
```

### RS-Matched Scan (N = ⌊√(T₀/2π)⌋)

```python
import math
for T0 in [100, 400, 1000, 5000, 10000]:
    N_RS = max(5, int(math.sqrt(T0 / (2 * math.pi))))
    psd, corr, val = central_step7(T0, N_RS, 1.5)
    print(f"T0={T0:>6}  N_RS={N_RS:>4}  Re<TD²b,b>={float(val.real):+.6f}")
```

### Adjustable Parameters

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `H` | 1.5 | Sech² bandwidth (safe zone: π−2 < H < 2) |
| `N` | 50 | Dirichlet polynomial truncation |
| `T0` | 30.0 | Height parameter |
| `tau_max` | 10.0 | Integration window half-width (≥ 6/H recommended) |
| `num_tau` | 2001 | Quadrature points (odd for symmetry) |
| `mp.mp.dps` | 50 | Decimal digits of precision |

---

## Functions

### `D0(T, N)`
Dirichlet polynomial D₀(T) = Σ_{n≤N} n^{-1/2} e^{-iT ln n}.
Returns an mpmath complex number.

### `D1(T, N)`
Multiplicative derivative D₁(T) = -i Σ_{n≤N} (ln n) n^{-1/2} e^{-iT ln n}.
Returns an mpmath complex number.

### `Lambda_H(t, H)`
Mellin kernel Λ_H(t) = 2 sech²(Ht). Returns an mpmath real number.

### `Lambda_H_dd(t, H)`
Second derivative Λ″_H(t). Returns an mpmath real number.
Changes sign at |t| = (1/H) arccosh(√(3/2)) ≈ 0.659 for H = 1.5.

### `psd_term(T0, N, H, tau_max, num_tau)`
Evaluates ⟨TDb, Db⟩ = (1/2π) ∫ Λ_H(τ) |D₁(T₀+τ)|² dτ.
Always ≥ 0 by Parseval (proved).

### `cross_term(T0, N, H, tau_max, num_tau)`
Evaluates (1/4π) ∫ Λ″_H(τ) |D₀(T₀+τ)|² dτ.
Can be positive or negative (signed projection).

### `central_step7(T0, N, H, tau_max, num_tau)`
Returns `(psd, corr, value)` where `value = psd - corr` is
Re⟨TD²b, b⟩. Step 7 requires `value ≥ 0`.

---

## Relationship to the Phase Stack

This script provides an independent, mpmath-precision cross-check of
the computations performed in the Phase 07/16/17 verification suite
(which uses numpy/scipy at float64 precision).

| Phase Stack | This Script | Purpose |
|-------------|-------------|---------|
| Phase 07 Test 4 | `central_step7()` | Step 7 inequality |
| Phase 07 Test 5 | `psd_term()` / `cross_term()` | MV ratio c(H) |
| Phase 16 FPE.8 | Identity verified | Cross-term decomposition |
| Phase 17 C17.5 | `central_step7()` scan | Dense verification |

The Phase stack operates at float64 (~16 digits). This script operates
at 50 digits by default, providing independent confirmation that the
results are not floating-point artifacts.

---

## Connection to the Pöschl-Teller Potential

The kernel Λ_H(t) = 2 sech²(Ht) is mathematically identical to the
**Pöschl-Teller potential** in quantum scattering theory — an exactly
solvable Schrödinger potential whose bound-state spectrum produces
hyperbolic secant squared wavefunctions. This connection to an
integrable quantum system may explain the clean spectral structure
observed in the Phase 15 Mellin diagonalisation and the robustly
positive numerics throughout the verification suite.

The connection to Montgomery's pair-correlation function for ζ zeros
(noted in the review) is also potentially significant: the sech² kernel
naturally suppresses high-frequency correlations in exactly the way that
the GUE pair-correlation conjecture predicts for zero spacings.

---

## Verified Results

At the reference point (H=1.5, N=50, T₀=30):

| Quantity | Value | Status |
|----------|-------|--------|
| PSD term ⟨TDb,Db⟩ | 1.88177 | Positive (proved) |
| Cross-term correction | 0.57957 | Smaller than PSD |
| Re⟨TD²b, b⟩ | **1.30220** | **Positive** ✓ |
| Ratio corr/PSD | 0.308 | Well below threshold of 1.0 |

Across all tested (T₀, N) configurations in the Phase stack:

| Test | Scope | Failures |
|------|-------|----------|
| Phase 07 Test 4 | 21 (T₀, N) pairs | 0 |
| Phase 07 Test 5 | 12 MV ratio checks | 0 (max = 0.232) |
| Phase 17 C17.5 | 2000 evaluations | 0 (margin ≥ 0.226) |

---

## What Would Close Step 7

The script evaluates the inequality numerically. To **prove** it
analytically requires showing:

    ⟨TDb, Db⟩  ≥  (1/4π) ∫ Λ″_H(τ) |D₀(T₀+τ)|² dτ

for all T₀ ∈ ℝ and all N ∈ ℕ. The Montgomery-Vaughan roadmap:

1. **Mean-zero rewriting**: Since ∫ Λ″_H dτ = 0, the correction integral
   equals ∫ Λ″_H (|D₀|² − C) dτ for any constant C. This removes the
   bulk contribution and isolates the fluctuation.

2. **Weighted mean-value estimate**: Show |fluctuation| ≤ c(H) × PSD
   integral with c(H) < 1. Phase 07 Test 5 measures c(H) = 0.232 at
   the worst tested point — a factor of 4× below what's needed.

3. **Uniformity**: Extend the bound to all T₀ and N via Mellin scale
   invariance and the exponential decay of ŵ_H in the far region.

The MV ratio of 0.232 (vs threshold 1.0) provides substantial room
for an analytical proof — even a factor-of-4 loss in the bounding
argument would still close the gap.

---

## Citation

If referencing this work:

> Mullings, J. (2026). *Reduction of the Riemann Hypothesis to a
> Dirichlet Polynomial Mean-Value Inequality via σ-Selective Averaged
> Convexity.* BetaPrecision.com.