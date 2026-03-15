# PSS_STEP_6 — PSS 9D Normalised Coordinate Construction

## Purpose
Construct the **normalised PSS 9D coordinate** `x*(PSS)` using the sech²-kernel:

```
C_k   = K · sech²(|z_k| · x*)
x*(PSS)_k = C_k / Σ_j C_j       (normalised)
```

where `z_k` is the mu_abs z-score from PSS_STEP_5 and `x*` = `NORM_X_STAR` from AXIOMS.py.

This mirrors **STEP_06** (SVD consensus matrix) from the prime-side, but the coordinate
is assembled entirely from sech²-transformed PSS z-scores — a distinct algebraic path.

## What It Verifies
1. `‖x*(PSS)‖₂` is comparable to `NORM_X_STAR` (ratio test: 0.5–2.0)
2. Riemannian norm `‖x*(PSS)‖_g = √(x*(PSS)ᵀ · G · x*(PSS))` is computed
3. The dominant component `k = argmax x*(PSS)_k` should be **k = 1** (γ₁)
4. Energy concentration: fraction of total energy in component k=1

## Execution Script
```
EXECUTION/PSS_STEP_06_9D_COORDINATE.py
```

## Output CSVs
| File | Description |
|------|-------------|
| `pss_step_06_9d_coordinate.csv` | 9-row table: k, z_k, C_k, x_star_k |
| `pss_step_06_norm_check.csv`    | Norm comparison: Euclidean, Riemannian, ratio |

## Protocol Compliance
- **P2** 9D Riemannian metric g_ij = φ^(i+j) ✓
- **P3** φ-kernel enters via g_ij ✓
- **P4** b(γ) enters z_k via PSS_STEP_5 ✓

## Dependency
- `pss_step_05_pss_singularity.csv` for z-scores k=1..80.
