# SELECTIVITY Pathway Unit Tests

This directory contains comprehensive unit tests for the three mathematical pathways implementing SELECTIVITY-based σ-selectivity proofs in `FORMAL_PROOF_NEW/SELECTIVITY/`.

## Test Structure

```
TEST_SUITE/TEST_FORMAL_PROOF/SELECTIVITY/
├── README.md                              # This file
├── run_all_selectivity_tests.py          # Master test runner 
├── TEST_PATH_1_SPECTRAL_OPERATOR.py      # Tests for PATH_1 (Hilbert-Pólya)
├── TEST_PATH_2_WEIL_EXPLICIT.py          # Tests for PATH_2 (Weil formula)
└── TEST_PATH_3_LI_DUAL_PROBE.py          # Tests for PATH_3 (Li coefficients)
```

## Test Coverage

### PATH_1: Spectral Operator Tests
**Target**: `FORMAL_PROOF_NEW/SELECTIVITY/PATH_1/EXECUTION/PATH_1_SPECTRAL_OPERATOR.py`

**Test Categories**:
- Import/syntax validation
- Constant verification (LAMBDA_STAR, PHI, COUPLING_K, ZEROS_9)
- Gram matrix construction and properties
- Eigenvalue analysis and σ-monotonicity  
- Trace growth analysis (divergence detection)
- σ-selectivity proof outline
- Mathematical validation (primes, Dirichlet kernel, F₂ curvature)
- Boundary condition tests
- Large parameter stability

**Key Validations**:
- Gram matrix symmetry and diagonal structure
- Eigenvalue decreasing monotonicity with σ
- Trace divergence at σ = 1/2
- Numerical stability for large T values

### PATH_2: Weil Explicit Tests  
**Target**: `FORMAL_PROOF_NEW/SELECTIVITY/PATH_2/EXECUTION/PATH_2_WEIL_EXPLICIT.py`

**Test Categories**:
- Import/syntax validation
- sech² kernel function properties and stability  
- Fourier transform h_kernel_fourier validation
- **Theorem A** (Kernel Admissibility): evenness, reality, non-negativity, L¹ norm
- **Theorem B** (Log-weighted Polynomial): D̃ functions, F₂ curvature
- **Theorem C** (Truncation Control): Montgomery-Vaughan estimates, curvature
- Critical line behavior (σ = 1/2)
- Large/small parameter stability

**Key Validations**:
- sech² numerical stability (no overflow for |x| ≤ 500)
- Two-branch formula correctness for extreme arguments
- Theorem A: ‖ĥ‖₁ = 2π (independent of α)
- Theorem B: F₂ > 0 validation
- Theorem C: Montgomery-Vaughan monotonicity

### PATH_3: Li Dual Probe Tests
**Target**: `FORMAL_PROOF_NEW/SELECTIVITY/PATH_3/EXECUTION/PATH_3_LI_DUAL_PROBE.py`

**Test Categories**:
- Import/syntax validation  
- sech² stability tests (inherited fixes from PATH_2)
- Li coefficient proxy positivity and convergence
- F₂ Probe 1 computation validation
- Probe 2 SECH² angle analysis
- Pearson correlation properties
- 9D coordinate computation
- Pathway 2→Li bridge explanation
- QUARANTINE protocol compliance

**Key Validations**:
- Li coefficients λₙ > 0 for n = 1,2,...,12
- Probe correlation analysis (Pearson ρ ≈ 0.245)
- 9D coordinate normalization and σ-dependence
- QUARANTINE labelling for empirical sections

## Trinity Protocol Compliance

All tests validate Trinity Protocol compliance:
- **P1**: LOG-FREE OPERATOR ARCHITECTURE ✓
- **P2**: 9D-CENTRIC COMPUTATIONS ✓  
- **P3**: RIEMANN-φ WEIGHTS ✓
- **P4**: BIT-SIZE AXIOMS (not applicable for unit tests)
- **P5**: TRINITY AND UNIT-TEST COMPLIANCE ✓

## Usage

### Run All Tests
```bash
python3 TEST_SUITE/TEST_FORMAL_PROOF/SELECTIVITY/run_all_selectivity_tests.py
```

### Run Individual Test Suites
```bash
# PATH_1 only
python3 -m unittest TEST_SUITE.TEST_FORMAL_PROOF.SELECTIVITY.TEST_PATH_1_SPECTRAL_OPERATOR

# PATH_2 only  
python3 -m unittest TEST_SUITE.TEST_FORMAL_PROOF.SELECTIVITY.TEST_PATH_2_WEIL_EXPLICIT

# PATH_3 only
python3 -m unittest TEST_SUITE.TEST_FORMAL_PROOF.SELECTIVITY.TEST_PATH_3_LI_DUAL_PROBE
```

### Run Specific Test Classes
```bash
# Example: Test only Gram matrix functionality
python3 -c "import unittest; from TEST_PATH_1_SPECTRAL_OPERATOR import TestPath1SpectralOperator; unittest.main(module=None, testLoader=unittest.TestLoader().loadTestsFromTestCase(TestPath1SpectralOperator))"
```

## Test Dependencies

**Required Imports**:
- `numpy` (numerical computations)
- `math` (basic mathematical functions)
- `unittest` (test framework)

**Target Modules**:
- `PATH_1_SPECTRAL_OPERATOR` 
- `PATH_2_WEIL_EXPLICIT`
- `PATH_3_LI_DUAL_PROBE`

**Test Data**:
- First 9 Riemann zeros (ZEROS_9): ["14.1347", "21.0220", ...] 
- LAMBDA_STAR ≈ 494.05895
- PHI = (1 + √5)/2 ≈ 1.618
- Small prime lists for validation

## Expected Test Results

**Successful Run**:
- All imports succeed
- Constants validate to expected mathematical values
- Function computations complete without overflow/NaN
- Theorem validations pass where analytically proved
- QUARANTINE sections properly labelled

**Known OPEN items** (expected to remain open):
- **PATH_1**: Sub-problems a,b,c (Hilbert-Pólya conjecture)
- **PATH_2**: A5' (strip condition), B5 (analytic curvature), C5-C6 (explicit formula bridge)
- **PATH_3**: All sections marked as supporting evidence only

## Numerical Stability

**Critical Fixes Tested**:
- **sech² overflow**: Two-branch formula for |x| > 10 prevents exp(2|x|) overflow
- **Fourier L¹ norm**: Analytic result ‖ĥ‖₁ = 2π (independent of α)  
- **Montgomery-Vaughan**: Correct monotonic decreasing behavior
- **Large parameter**: Stability for T > 100, σ close to boundaries

## Test Philosophy

These tests validate:
1. **Mathematical Correctness**: Constants, formulas, and bounds
2. **Numerical Stability**: No overflow, NaN, or infinite results  
3. **Theoretical Consistency**: Symmetries, monotonicity, convergence
4. **Implementation Quality**: Imports, error handling, edge cases
5. **Documentation**: Trinity compliance, QUARANTINE labelling

The tests mirror the actual mathematical content of each pathway while ensuring robust numerical implementation.

---

**Status**: Complete unit test coverage for all three SELECTIVITY pathways.  
**Last Updated**: March 13, 2026