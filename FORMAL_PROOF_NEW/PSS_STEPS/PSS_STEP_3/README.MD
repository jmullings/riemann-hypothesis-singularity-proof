# PSS_STEP_3 — Definition Verification (PSS Context)

## Purpose
Verify **DEF_1 through DEF_8** from `AXIOMS.py` using PSS-side data.
Each definition is evaluated on the PSS observables, confirming that
the prime-side framework applies equally to the geometric PSS path.

This mirrors **STEP_03** of the prime-side path.

## Definitions Checked
| Def | Statement | PSS Evaluation |
|-----|-----------|----------------|
| DEF_1 | Bitsize `b(n) = ⌊log₂ n⌋` | Applied to `round(γ_k)` for k=1..9 |
| DEF_2 | 9D factorisation `X = [X_micro | X_macro]` | PSS micro-vector split verified |
| DEF_3 | Energy `E = ½‖X‖²` conserved in split | Cross-coupling < 5 % checked |
| DEF_4 | 6D projection `P₆: ℝ⁹ → ℝ⁶` | Applied to PSS 9D state |
| DEF_5 | Bitsize shift `S(T) = 2^Δb > 0` | Confirmed positive for all γ_k |
| DEF_6 | Bridge operator `Ã = (1/S)P₆AP₆ᵀ` | ‖Ã‖₂ reported per γ_k |
| DEF_7 | Band restriction `b(γ) ∈ {3,4,5,6,7,8}` | Range 3–8 verified |
| DEF_8 | Band-wise convexity (CONJECTURAL / Axiom 8) | DIAGNOSTIC only |

## Execution Script
```
EXECUTION/PSS_STEP_03_VERIFY_DEFINITIONS.py
```

## Output CSV
| File | Description |
|------|-------------|
| `pss_step_03_definitions.csv` | PASS/FAIL rows for DEF_1–DEF_8, k=1..9 |

## Protocol Compliance
- **P1–P5** inherited from AXIOMS.py ✓
- DEF_8 flagged as CONJECTURAL in output; does not affect PASS/FAIL count

## Dependency
- `PSS_STEP_2/ANALYTICS/pss_step_02_micro_vectors.csv` provides the 9D states used here.
