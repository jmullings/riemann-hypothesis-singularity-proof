# SIGMA_1 — EQ1: Global ξ convexity

## Execution Script

| File | Description | Status |
|------|-------------|--------|
| `EXECUTION/EQ1_GLOBAL_CONVEXITY_XI.py` | EQ1: Global ξ convexity — second differences ≥ 0 across critical strip | ⬜️ NOT YET EXECUTED |

## Folder Layout

```
SIGMA_1/
├── EXECUTION/
│   └── EQ1_GLOBAL_CONVEXITY_XI.py
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
