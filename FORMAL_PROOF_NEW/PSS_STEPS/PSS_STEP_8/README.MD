# PSS_STEP_8 — PSS Bridge Verification (B7 + B9)

## Purpose
Verify **BRIDGE_7** (inverse bitsize shift) and **BRIDGE_9** (Gonek–Montgomery
prime spiral) from the PSS frame.

This mirrors **STEP_09** (prime-side Bridges B1–B3) but applies the B7 and B9
constructions to PSS micro-vector data, ensuring the bridge operators are
consistent with PSS observables.

## Bridge Descriptions
### BRIDGE_7 — Inverse Bitsize Shift  (CONJECTURAL / BS-5)
```
X_micro_reconstructed = (1/S(T)) · P₆ · X_full
```
- Constructs X_micro from the full 9D state via 6D projection and bitsize scaling.
- Checks relative reconstruction error: `|X_micro − X_micro_reconstructed| / |X_micro|`
- Status label: **CONJECTURAL** (pending analytic proof of BS-5)

### BRIDGE_9 — Gonek–Montgomery Spiral  (OPEN / X→∞ limit)
```
R_spiral(T) = (1/P) · |Σ_{p≤P_max} e^{i·T·log(p)}|
```
- Computed with N_eff = 500 primes (p₅₀₀ = 3571)
- Phase uses exact formula `T × log(p)` — **not** a linear approximation
- Compared with `mu_abs(T)` from PSS CSV
- Status label: **OPEN** (X→∞ limit not proved; P_max = 500 is finite)

## Execution Script
```
EXECUTION/PSS_STEP_08_BRIDGE_VERIFICATION.py
```

## Output CSV
| File | Description |
|------|-------------|
| `pss_step_08_bridges.csv` | k, gamma, bridge, computed_value, csv_value, err, status |

## Important Notes
- BRIDGE_7 and BRIDGE_9 match at finite N — the open/conjectural status refers
  to the analytic X→∞ or proof-of-BS-5 gaps.
- These gaps are **shared** by both paths and explicitly catalogued.

## Protocol Compliance
- **P1** Only `log()` inside `math.log(p)` for exact phase ✓
- **P2–P5** ✓

## Dependency
- `pss_step_06_9d_coordinate.csv` for the 9D state.
- `pss_micro_signatures_100k_adaptive.csv` for `mu_abs` comparison.
