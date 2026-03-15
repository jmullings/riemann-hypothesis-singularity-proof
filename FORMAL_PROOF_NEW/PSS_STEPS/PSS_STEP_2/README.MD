# PSS_STEP_2 — PSS Micro-Signature State Construction

## Purpose
Build a 9D `FactoredState9D` for each of the first 9 Riemann zero heights from the
pre-computed Prime Spiral Statistics (PSS) micro-signatures CSV.

This mirrors **STEP_02** of the prime-side path, but the 9D vector components are
assembled from geometric observables (`mu_abs`, `sigma_abs`, `C_k_norm`, `dist_from_center`)
rather than from Mangoldt-weighted sums.

## What It Computes
| Sub-vector | Dimension | Components |
|-----------|-----------|-----------|
| X_micro   | 6D        | μ_abs, σ_abs, C_k_norm, dist_center, μ·σ, C_k·dist |
| X_macro   | 3D        | b(γ), S(T)=2^Δb, φ^b(γ) |
| X_full    | 9D        | [X_micro | X_macro] (FactoredState9D) |

Energy conservation is checked:  `E_9D ≈ E_micro(6D) + E_macro(3D)`  (cross-coupling < 5 %).

## Data Source
- `pss_micro_signatures_100k_adaptive.csv` (repo root, 100 000 rows, N_eff = 500)
- Columns used: `k, gamma, mu_abs, sigma_abs, C_k_norm, dist_from_center`

## Execution Script
```
EXECUTION/PSS_STEP_02_MICRO_SIGNATURES.py
```

## Output CSVs (written to `ANALYTICS/`)
| File | Description |
|------|-------------|
| `pss_step_02_micro_vectors.csv` | 9D coordinates for k = 1..9 |
| `pss_step_02_energy.csv`        | Energy balance DEF_3 check for k = 1..9 |

## Protocol Compliance
- **P1** No `log()` as primary operator ✓ (bitsize uses `floor(log2)` internally)
- **P2** 9D Riemannian geometry ✓ (g_ij = φ^(i+j))
- **P3** Riemann-φ weighting ✓ (φ^b(γ) in macro sub-vector)
- **P4** Bitsize primary coordinate b(γ) = ⌊log₂ γ⌋ ✓
- **P5** Trinity Gate-0 / Gate-1 passed ✓

## Dependency
Assumes `PSS_STEP_1/ANALYTICS/pss_step_01_axiom_report.csv` is present (AXIOMS validated).
