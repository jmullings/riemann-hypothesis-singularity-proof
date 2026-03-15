# PSS_STEP_4 — σ* = ½ Localisation via EQ4 (PSS:SECH² Frame)

## Purpose
Recover the critical line coordinate **σ* = ½** from the PSS side, using the
PSS energy functional **EQ4**:

```
E_PSS(σ, T) = K · sech²(|σ − ½| · Λ* · mu_abs(T))
```

Because `sech²(x)` is strictly maximised at `x = 0`, the energy is maximised
(and EQ4 residual minimised) uniquely when `σ = ½`.

This mirrors **STEP_04** of the prime-side path (variance-minimisation of EQ),
but uses a completely different algebraic object — the spiral amplitude `mu_abs(T)`.

## Mathematical Statement
For each γ_k:
1. Grid-search σ ∈ [0,1] with 2001 points
2. Compute `residual(σ) = |E_PSS(σ,T) − E_PSS(½,T)|`
3. Verify `argmin residual = 0.5 ± 0.001`
4. Analytic confirmation: `∂E/∂σ|_{σ=½} = 0` and `∂²E/∂σ²|_{σ=½} < 0`

## Execution Script
```
EXECUTION/PSS_STEP_04_SIGMA_STAR.py
```

## Output CSV
| File | Description |
|------|-------------|
| `pss_step_04_sigma_star.csv` | `k, gamma, sigma_star, residual, status` for k=1..9 |

## Expected Result
All 9 rows should show `sigma_star = 0.5000`, `residual ≈ 0.0`, `status = PASS`.
This is analytic (sech² property), not a numerical approximation.

## Protocol Compliance
- **P1** No `log()` primary ✓  (only inside sech² via mpmath)
- **P2** 9D geometry backing the shift ✓
- **P4** mu_abs derived from b(n)-sorted spiral amplitudes ✓

## Dependency
- Reads `mu_abs` directly from `pss_micro_signatures_100k_adaptive.csv` — no prime-side data.
