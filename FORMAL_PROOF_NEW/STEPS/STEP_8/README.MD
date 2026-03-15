# STEP_8 — Verify 100% UBE convexity at zeros

## Execution Script

| File | Description | Status |
|------|-------------|--------|
| `EXECUTION/STEP_08_SIGMA_CURVATURE_BRIDGE.py` | Verify 100% UBE convexity at zeros; document open gaps B6 and B7 | ⬜️ NOT YET EXECUTED |

## Folder Layout

```
STEP_8/
├── EXECUTION/
│   └── STEP_08_SIGMA_CURVATURE_BRIDGE.py
├── ANALYTICS/
│   └── (outputs written here after execution)
├── TRINITY/
│   └── INDEX.MD  (protocol compliance record)
└── README.MD     (this file)
```

## Protocol Compliance

Before marking ✅ complete, the execution script must pass:

- **P1** No `log()` as primary operator
- **P2** Computation initialised in 9D (9×9 golden metric tensor)
- **P3** Riemann-φ weights used (no MKM tonnage)
- **P4** Bit-Size Axioms obeyed (BS-1 … BS-5)
- **P5** Trinity validator + unit tests both PASS
