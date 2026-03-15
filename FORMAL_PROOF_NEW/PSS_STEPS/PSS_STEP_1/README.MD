# PSS_STEP_1 — AXIOMS Ground (PSS Context)

## Mirror of: STEP_1 — Obtain resources: environment smoke-test, prime list, zero list, singularity bootstrap

## Execution Script

| File | Description | Status |
|------|-------------|--------|
| `EXECUTION/PSS_STEP_01_AXIOMS_GROUND.py` | AXIOMS ground for PSS:SECH² path — verify constants, sech²(x) functional form, PSS data loaded, energy coupling E=k·sech²(shift) verified | ⬜️ NOT YET EXECUTED |

## What This Step Establishes

- AXIOMS.py is the sole source of truth for both paths (P5 compliance)
- sech²(x) = 4e^(2x)/(e^(2x)+1)² computes correctly for all shift values
- Energy coupling E = COUPLING_K × sech²(shift) satisfies DEF_3 in PSS context
- PSS CSV is accessible with the correct 8-column schema
- All 9 Riemann zero heights are representable as PSS spiral evaluations
- TRINITY Gate-0 and Gate-1 pass before any output is written

## Folder Layout

```
PSS_STEP_1/
├── EXECUTION/
│   └── PSS_STEP_01_AXIOMS_GROUND.py
├── ANALYTICS/
│   └── (outputs written here after execution)
├── TRINITY/
│   └── INDEX.MD  (protocol compliance record)
└── README.MD     (this file)
```

## Output CSVs

| File | Columns | Purpose |
|------|---------|---------|
| `pss_step_01_axiom_report.csv` | check, value, status, note | Per-axiom verification results |
| `pss_step_01_sech2_sample.csv` | gamma, shift, sech2_val, energy, expected_energy | Sech² functional check for 9 zeros |

## Protocol Compliance

Before marking ✅ complete, the execution script must pass:

- **P1** No `log()` as primary operator (permitted only inside `bitsize()`)
- **P2** Computation initialised in 9D (9×9 golden metric tensor)
- **P3** Riemann-φ weights used (no MKM or ad-hoc weights)
- **P4** Bit-Size Axioms obeyed (BS-1 … BS-5)
- **P5** Trinity Gate-0 + Gate-1 both PASS before any output
