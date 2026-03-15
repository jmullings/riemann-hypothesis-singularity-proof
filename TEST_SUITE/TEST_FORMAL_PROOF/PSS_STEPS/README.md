# PSS_STEPS Test Suite

This directory contains unit tests for all PSS_STEP scripts in the FORMAL_PROOF_NEW/PSS_STEPS folder.

## Test Structure

Each PSS_STEP has corresponding unit tests:

- **PSS_STEP_1** → [test_pss_step_01_axioms_ground.py](PSS_STEP_1/EXECUTION/test_pss_step_01_axioms_ground.py)
- **PSS_STEP_2** → [test_pss_step_02_micro_signatures.py](PSS_STEP_2/EXECUTION/test_pss_step_02_micro_signatures.py) 
- **PSS_STEP_3** → [test_pss_step_03_verify_definitions.py](PSS_STEP_3/EXECUTION/test_pss_step_03_verify_definitions.py)
- **PSS_STEP_4** → [test_pss_step_04_sigma_star.py](PSS_STEP_4/EXECUTION/test_pss_step_04_sigma_star.py)
- **PSS_STEP_5** → [test_pss_step_05_sech2_singularity.py](PSS_STEP_5/EXECUTION/test_pss_step_05_sech2_singularity.py)
- **PSS_STEP_6** → [test_pss_step_06_9d_coordinate.py](PSS_STEP_6/EXECUTION/test_pss_step_06_9d_coordinate.py)
- **PSS_STEP_7** → [test_pss_step_07_independence.py](PSS_STEP_7/EXECUTION/test_pss_step_07_independence.py)
- **PSS_STEP_8** → [test_pss_step_08_bridge_verification.py](PSS_STEP_8/EXECUTION/test_pss_step_08_bridge_verification.py)
- **PSS_STEP_9** → [test_pss_step_09_dual_convergence.py](PSS_STEP_9/EXECUTION/test_pss_step_09_dual_convergence.py)
- **PSS_STEP_10** → [test_pss_step_10_proof_chain.py](PSS_STEP_10/EXECUTION/test_pss_step_10_proof_chain.py)

## Test Categories

Each PSS step test includes:

1. **Syntax Tests**: Verifies the Python script compiles without syntax errors
2. **Runtime Tests**: Ensures the script runs to completion with exit code 0
3. **Output Tests**: Validates required output files are generated
4. **Step-Specific Tests**: Validates functionality specific to each step

## Running Tests

### Run All PSS Tests
```bash
python -m pytest TEST_SUITE/TEST_FORMAL_PROOF/PSS_STEPS/ -v
```

### Run Individual Step Tests
```bash
python -m pytest TEST_SUITE/TEST_FORMAL_PROOF/PSS_STEPS/PSS_STEP_1/EXECUTION/test_pss_step_01_axioms_ground.py -v
```

### Run All FORMAL_PROOF Tests (Regular STEPS + PSS_STEPS)
```bash
python -m pytest TEST_SUITE/TEST_FORMAL_PROOF/ -v
```

## Recent Test Results

### PSS_STEPS Tests
- **35 tests passed** ✅ (March 13, 2026)
- Coverage: All 10 PSS_STEP scripts have full test coverage

### Regular STEPS Tests  
- **150 tests passed** ✅ (March 13, 2026)
- Coverage: All 10 STEP scripts have comprehensive test coverage

### Total
- **185 tests passed** ✅
- **0 failures** 
- All scripts in FORMAL_PROOF_NEW have corresponding unit tests

## Test Dependencies

Tests require:
- Python 3.11+
- pytest
- Access to FORMAL_PROOF_NEW/CONFIGURATIONS/AXIOMS.py
- PSS CSV file: `pss_micro_signatures_100k_adaptive.csv`

## Automated Testing

The test suite automatically:
- Verifies script syntax
- Runs each script and checks exit codes
- Validates output file generation
- Checks mathematical invariants
- Ensures AXIOMS integration works

## Maintenance

Tests are designed to be:
- **Self-contained**: Each test is independent
- **Robust**: Handle missing dependencies gracefully  
- **Fast**: Complete in ~6-11 seconds
- **Informative**: Clear failure messages with debug output