# PSS_STEP_5 — PSS:SECH² Singularity Detection

## Purpose
Detect the **PSS:SECH² Singularity** — the anomalous concentration of prime-spiral
amplitude (`mu_abs`) at the first Riemann zero `γ₁ = 14.134725`.

This is the **core PSS claim**: the distribution of `mu_abs(γ_k)` over the first
80 zeros is normal except for an extreme outlier at k = 1 with z-score ≈ **+5.90σ**.

This mirrors **STEP_05** (variational curvature F₂ > 0) from the prime-side, but
operates entirely on the PSS observable `mu_abs`.

## Five Detection Criteria
| Criterion | Test | Pass Threshold |
|-----------|------|----------------|
| C1 | z-score at k=1 exceeds 2.5σ | z ≥ 2.5 |
| C2 | k=1 is the global maximum of z-scores | rank = 1 |
| C3 | z-score at k=1 exceeds 5.0σ (strong) | z ≥ 5.0 |
| C4 | No other zero exceeds 2.5σ (uniqueness) | max(z_{k≥2}) < 2.5 |
| C5 | mu_abs decays from Q1 to Q4 (monotone) | Q1 > Q4 |

All 5 must pass for SINGULARITY_CONFIRMED status.

## Expected Key Result
```
k = 1,  gamma = 14.134725,  mu_abs ≈ 0.666,  z = +5.90σ
```

## Execution Script
```
EXECUTION/PSS_STEP_05_SECH2_SINGULARITY.py
```

## Output CSVs
| File | Description |
|------|-------------|
| `pss_step_05_pss_singularity.csv` | Full 80-row z-score table |
| `pss_step_05_summary.csv`         | 5-criterion PASS/FAIL summary |

## Protocol Compliance
- **P1–P5** ✓  — All PSS data; no prime-side variance used here.

## Dependency
- Reads 80 rows from `pss_micro_signatures_100k_adaptive.csv`.
- Independent of STEP_04; can run standalone after PSS_STEP_1.
