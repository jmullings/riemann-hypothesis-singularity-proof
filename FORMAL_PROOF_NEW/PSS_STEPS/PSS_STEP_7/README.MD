# PSS_STEP_7 — Structural Independence Verification

## Purpose
Confirm that the PSS:SECH² singularity signal is **structurally independent**
of the prime-side curvature signal `F₂(½, γ_k)`.

Two singularity signals pointing to the same γ₁ are only meaningful if they
arise from different algebraic objects. This step measures that independence
quantitatively.

## Independence Test
The Pearson correlation coefficient is computed between:
- **Vector A** (prime-side): `F₂(½, γ_k)` — second derivative of |D(σ,T)|² at σ=½
- **Vector B** (PSS-side): `mu_abs(γ_k)` — mean prime-spiral amplitude

```
ρ = corr(F₂, mu_abs)   for k = 1..9
```

### Expected Result
`ρ ≈ +0.063`  (weak positive; structurally independent)

### Thresholds
| |ρ| | Classification |
|--------|----------------|
| < 0.2  | STRONGLY INDEPENDENT |
| 0.2–0.3| WEAKLY INDEPENDENT |
| ≥ 0.3  | CORRELATED — review |

## SVD Check
A 9×2 joint matrix `M = [A | B]` is formed. Its SVD is computed.
The ratio σ₂/σ₁ (second/first singular value) should be close to 1,
indicating the two columns span orthogonal directions.

## Execution Script
```
EXECUTION/PSS_STEP_07_INDEPENDENCE.py
```

## Output CSVs
| File | Description |
|------|-------------|
| `pss_step_07_independence.csv` | k-by-k table of F₂ vs mu_abs |
| `pss_step_07_stats.csv`        | Pearson ρ, SVD ratio, PASS/FAIL |

## Protocol Compliance
- **P1** log only inside bitsize ✓
- Prime-side F₂ uses 100 primes (a small finite set — not full prime measure)

## Dependency
- `pss_micro_signatures_100k_adaptive.csv` for mu_abs.
- Primes up to p₁₀₀ = 541 computed internally by the script.
