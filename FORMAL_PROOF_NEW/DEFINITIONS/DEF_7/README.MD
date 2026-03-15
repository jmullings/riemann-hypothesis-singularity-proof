# DEF_7 — De Bruijn–Newman flow

## Execution Script

| File | Description | Status |
|------|-------------|--------|
| `EXECUTION/DEF_07_DE_BRUIJN_NEWMAN.py` | De Bruijn–Newman flow; finite-difference step h=1e-5 for curvature accuracy | ⬜️ NOT YET EXECUTED |

## Folder Layout

```
DEF_7/
├── EXECUTION/
│   └── DEF_07_DE_BRUIJN_NEWMAN.py
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
