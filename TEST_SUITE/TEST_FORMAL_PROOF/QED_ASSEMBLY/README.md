# QED_ASSEMBLY Test Suite

Unit tests for all scripts referenced in `FORMAL_PROOF_NEW/QED_ASSEMBLY/AIREADME.md`.

## Structure

```
QED_ASSEMBLY/
├── run_all_qed_assembly_tests.py   # Master test runner
├── README.md                        # This file
├── PARTS/                           # Tests for PART_01 through PART_10
│   ├── test_part_01_rh_statement.py
│   ├── test_part_02_pss_sech2_framework.py
│   ├── test_part_03_prime_side_curvature.py
│   ├── test_part_04_classical_backbone.py
│   ├── test_part_05_montgomery_vaughan.py
│   ├── test_part_06_mellin_mean_decomposition.py
│   ├── test_part_07_mv_sech2_antisymmetrisation.py
│   ├── test_part_08_uniform_curvature_bound.py
│   ├── test_part_09_rs_bridge.py
│   └── test_part_10_qed_assembly.py
├── QED/                             # Tests for QED/ subdirectory scripts
│   ├── test_full_proof.py           # Theorems A–D assembly
│   ├── test_gap_1_rs_bridge.py      # GAP 1: RS cross-term suppression
│   ├── test_gap_2_uniform_bound.py  # GAP 2: Uniform curvature bound
│   └── test_gap_3_unconditional_density.py  # GAP 3: Weil contradiction
└── STANDALONE/                      # Tests for standalone QED_ASSEMBLY scripts
    ├── test_claim_scan.py           # CLAIM_SCAN.py
    ├── test_mellin_mean_value_closure.py  # MELLIN_MEAN_VALUE_CLOSURE.py
    └── test_mv_sech2_variant.py     # MV_SECH2_VARIANT.py
```

## Coverage Map (AIREADME.md → Test)

| AIREADME Reference | Source Script | Test File |
|---|---|---|
| PART 1 (Cranium) | `PART_01_RH_STATEMENT.py` | `PARTS/test_part_01_rh_statement.py` |
| PART 2 (Pes Sinister) | `PART_02_PSS_SECH2_FRAMEWORK.py` | `PARTS/test_part_02_pss_sech2_framework.py` |
| PART 3 (Pes Dexter) | `PART_03_PRIME_SIDE_CURVATURE.py` | `PARTS/test_part_03_prime_side_curvature.py` |
| PART 4 (Brachium Sinistrum) | `PART_04_CLASSICAL_BACKBONE.py` | `PARTS/test_part_04_classical_backbone.py` |
| PART 5 (Brachium Dextrum) | `PART_05_MONTGOMERY_VAUGHAN.py` | `PARTS/test_part_05_montgomery_vaughan.py` |
| PART 6 (Columna Vertebralis) | `PART_06_MELLIN_MEAN_DECOMPOSITION.py` | `PARTS/test_part_06_mellin_mean_decomposition.py` |
| PART 7 (Pulmo) | `PART_07_MV_SECH2_ANTISYMMETRISATION.py` | `PARTS/test_part_07_mv_sech2_antisymmetrisation.py` |
| PART 8 (Cor) | `PART_08_UNIFORM_CURVATURE_BOUND.py` | `PARTS/test_part_08_uniform_curvature_bound.py` |
| PART 9 (Pelvis) | `PART_09_RS_BRIDGE.py` | `PARTS/test_part_09_rs_bridge.py` |
| PART 10 (Corpus Completum) | `PART_10_QED_ASSEMBLY.py` | `PARTS/test_part_10_qed_assembly.py` |
| Theorems A–D | `QED/FULL_PROOF.py` | `QED/test_full_proof.py` |
| GAP 1 (RS Bridge) | `QED/GAP_1_RS_BRIDGE.py` | `QED/test_gap_1_rs_bridge.py` |
| GAP 2 (Uniform Bound) | `QED/GAP_2_UNIFORM_BOUND.py` | `QED/test_gap_2_uniform_bound.py` |
| GAP 3 (Unconditional Density) | `QED/GAP_3_UNCONDITIONAL_DENSITY.py` | `QED/test_gap_3_unconditional_density.py` |
| CLAIM_SCAN | `CLAIM_SCAN.py` | `STANDALONE/test_claim_scan.py` |
| Mellin Mean Value | `MELLIN_MEAN_VALUE_CLOSURE.py` | `STANDALONE/test_mellin_mean_value_closure.py` |
| MV SECH² Variant | `MV_SECH2_VARIANT.py` | `STANDALONE/test_mv_sech2_variant.py` |

## Test Categories

Each test file follows a consistent pattern:

| Category | Description | Speed |
|---|---|---|
| **T1 — Syntax** | Script compiles without syntax errors | Fast |
| **T2 — Runtime** | Script runs to completion (exit 0, output checks) | Slow |
| **T3 — Functions** | Key functions exist and are callable | Fast |
| **T4+** | Domain-specific checks (identities, bounds, results) | Varies |

## Usage

```bash
# Run all QED_ASSEMBLY tests
cd TEST_SUITE/TEST_FORMAL_PROOF/QED_ASSEMBLY/
python3 run_all_qed_assembly_tests.py -v

# Run only PART tests
python3 run_all_qed_assembly_tests.py --parts-only -v

# Run only QED/ tests
python3 run_all_qed_assembly_tests.py --qed-only -v

# Run only standalone tests
python3 run_all_qed_assembly_tests.py --standalone-only -v

# Run individual test files
python3 -m pytest PARTS/test_part_06_mellin_mean_decomposition.py -v
python3 -m unittest QED/test_full_proof.py -v
```

## Timing Notes

- **PART 8** is the slowest PART (~288s) due to dense T₀ grid scanning
- **PART 10** runs all 9 PARTs sequentially (~290s total)
- **CLAIM_SCAN** is intensive (~2 min)
- All other tests complete in < 30s individually

## Date

16 March 2026
