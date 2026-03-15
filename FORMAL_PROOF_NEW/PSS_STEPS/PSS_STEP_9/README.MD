# PSS_STEP_9 — Dual Singularity Convergence

## Purpose
The **critical cross-authentication step**.

Both proof paths must independently pinpoint the same object: a singularity at
`γ₁ = 14.134725`. This step computes the statistical evidence from each path
and measures their joint probability.

## Two Independent Signals
| Signal | Source | Definition |
|--------|--------|-----------|
| `z_PSS(T)` | PSS:SECH² path | z-score of mu_abs(T) over 80-zero population |
| `z_prime(T)` | Prime-side path | z-score of C_proxy(T) over 80-zero population |

### Expected values at k = 1 (γ₁)
```
z_PSS(γ₁)   ≈ +5.90σ
z_prime(γ₁) ≈ +2.55σ
```

## Convergence Criteria
| Criterion | Test | Result |
|-----------|------|--------|
| CR1 | PSS signal at k=1: z_PSS ≥ 2.5 | Expected PASS |
| CR2 | Prime signal at k=1: z_prime ≥ 2.5 | Expected PASS |
| CR3 | Both peak simultaneously at k=1 | Expected PASS |
| CR4 | Independence: ρ(F₂, mu_abs) < 0.3 | Expected PASS (ρ ≈ 0.063) |

## Joint Probability
```
p_PSS   ≈ P(Z ≥ 5.90) ≈ 1.8 × 10⁻⁹
p_prime ≈ P(Z ≥ 2.55) ≈ 0.0054
p_joint = p_PSS × p_prime ≈ 9.7 × 10⁻¹²
```
Under independence, a joint result this extreme would occur with probability < 10⁻¹¹.

## Execution Script
```
EXECUTION/PSS_STEP_09_DUAL_CONVERGENCE.py
```
*Note: This script recalculates C_proxy for 80 zeros using 500 primes — expected runtime ~30–60 s.*

## Output CSVs
| File | Description |
|------|-------------|
| `pss_step_09_dual_convergence.csv` | 80-row table: k, z_pss, z_prime, delta |
| `pss_step_09_path_summary.csv`     | Path-level summary: z scores, rho, verdict |

## Protocol Compliance
- **P1–P5** ✓
- C_proxy uses exact `math.log(p)` phases ✓
- N_eff = 500 for both paths ✓

## Dependency
- `pss_micro_signatures_100k_adaptive.csv` for mu_abs (80 rows).
- Prime numbers up to p₅₀₀ = 3571 computed internally.
