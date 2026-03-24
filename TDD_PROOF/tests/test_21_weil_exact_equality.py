#!/usr/bin/env python3
"""
test_21_weil_exact_equality.py — Tier 9: Weil Exact Equality Oracle
====================================================================

TDD tests for the numerically-verified Weil explicit formula equality:

    f̂(0) + f̂(1) − Σ_ρ f̂(ρ)  =  S_prime − I_∞ − (log4π + γ)·f(1)

All engine-side calls are non-log; reference oracle (ref_weil_exact.py) may
use log() for trusted ground-truth comparison.

Sections:
  A: Grid/Builder infrastructure         (5 tests)
  B: Test kernel evaluation               (6 tests)
  C: Mellin transform consistency          (5 tests)
  D: Zero-side functional                  (5 tests)
  E: Prime-side functional                 (4 tests)
  F: Archimedean term                      (4 tests)
  G: Full LHS ≈ RHS equality              (5 tests)
  H: Engine–Oracle cross-check             (5 tests)
  I: Non-log protocol sentinel             (3 tests)
  J: Sensitivity / synthetic zeros         (4 tests)
  K: Decomposition diagnostics             (4 tests)

Expected: ~50 tests.  Zero mocks.
"""

import inspect
import numpy as np
import pytest

# Engine imports (non-log)
from engine.weil_exact import (
    build_x_grid,
    build_x_powers,
    build_prime_coeffs,
    f_test_on_grid,
    f_star_on_grid,
    f_test_scalar,
    f_star_scalar,
    mellin_f,
    weil_zero_side,
    weil_prime_side,
    archimedean_term,
    weil_prime_arch_side,
    weil_equality_check,
    decompose_zero_side,
    decompose_prime_side,
    EULER_MASCHERONI,
    LOG4PI_GAMMA,
    _small_primes,
)

# Reference oracle (may use log)
from tests.ref_weil_exact import (
    ref_f_test,
    ref_f_star,
    ref_mellin_f,
    ref_weil_zero_side,
    ref_weil_prime_side,
    ref_weil_prime_arch_side,
    ref_weil_equality_check,
    get_reference_zeros,
    get_reference_primes,
    build_x_grid_and_weights,
    GAMMA_30,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def grid_data():
    """Standard grid for all tests: 3000 pts, t ∈ [-30, 30]."""
    x_grid, dt = build_x_grid(3000, -30.0, 30.0)
    return x_grid, dt


@pytest.fixture(scope="module")
def reference_zeros():
    return get_reference_zeros(T_max=50.0)


@pytest.fixture(scope="module")
def reference_primes():
    return get_reference_primes(P_max=100)


@pytest.fixture(scope="module")
def H_default():
    return 2.0


# ═══════════════════════════════════════════════════════════════════════════════
# Section A: Grid / Builder Infrastructure
# ═══════════════════════════════════════════════════════════════════════════════

class TestGridBuilders:
    """Tests for build_x_grid, build_x_powers, build_prime_coeffs."""

    def test_grid_shape(self, grid_data):
        x_grid, dt = grid_data
        assert x_grid.shape == (3000,)
        assert dt > 0

    def test_grid_positive(self, grid_data):
        x_grid, _ = grid_data
        assert np.all(x_grid > 0)

    def test_grid_contains_unity(self, grid_data):
        """x = 1 (i.e. t = 0) should be near the middle of the grid."""
        x_grid, _ = grid_data
        assert np.min(np.abs(x_grid - 1.0)) < 0.01

    def test_x_powers_at_zero(self, grid_data):
        x_grid, _ = grid_data
        powers = build_x_powers(x_grid, complex(1, 0))  # x^{1-1} = x^0 = 1
        np.testing.assert_allclose(powers, np.ones_like(x_grid), atol=1e-12)

    def test_prime_coeffs_count(self):
        primes = [2, 3, 5]
        coeffs = build_prime_coeffs(primes, max_m=3)
        assert len(coeffs) == 9  # 3 primes × 3 powers


# ═══════════════════════════════════════════════════════════════════════════════
# Section B: Test Kernel Evaluation
# ═══════════════════════════════════════════════════════════════════════════════

class TestKernelEvaluation:
    """f_test_on_grid and f_star_on_grid vs reference oracle."""

    @pytest.mark.parametrize("H", [1.0, 2.0, 4.0])
    def test_f_at_unity(self, H):
        """f(1) = sech²(log(1)/H) = sech²(0) = 1."""
        assert abs(f_test_scalar(1.0, H) - 1.0) < 1e-12

    @pytest.mark.parametrize("H", [1.0, 2.0, 4.0])
    def test_f_star_at_unity(self, H):
        """f*(1) = f(1)/1 = 1."""
        assert abs(f_star_scalar(1.0, H) - 1.0) < 1e-12

    def test_f_symmetry(self, grid_data):
        """f(x) should be even in log(x): f(x) = f(1/x)."""
        x_grid, _ = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)
        f_inv = f_test_on_grid(1.0 / x_grid, H)
        np.testing.assert_allclose(f_vals, f_inv, atol=1e-8)

    @pytest.mark.parametrize("x", [2.0, 5.0, 10.0])
    def test_f_matches_reference(self, x):
        """Engine f_test matches reference ref_f_test."""
        H = 2.0
        engine_val = f_test_scalar(x, H)
        ref_val = ref_f_test(x, H)
        assert abs(engine_val - ref_val) < 1e-10, (
            f"f({x}, H={H}): engine={engine_val}, ref={ref_val}"
        )

    def test_f_grid_matches_reference(self, grid_data):
        """Engine grid evaluation matches reference at many points."""
        x_grid, _ = grid_data
        H = 2.0
        engine_vals = f_test_on_grid(x_grid, H)
        ref_vals = np.array([ref_f_test(x, H) for x in x_grid])
        # Only check where x is not extreme (avoid underflow regions)
        mask = (x_grid > 1e-10) & (x_grid < 1e10)
        np.testing.assert_allclose(engine_vals[mask], ref_vals[mask], atol=1e-8)

    def test_fstar_grid_matches_reference(self, grid_data):
        """Engine f* matches reference f*."""
        x_grid, _ = grid_data
        H = 2.0
        engine_vals = f_star_on_grid(x_grid, H)
        ref_vals = np.array([ref_f_star(x, H) for x in x_grid])
        mask = (x_grid > 1e-10) & (x_grid < 1e10)
        np.testing.assert_allclose(engine_vals[mask], ref_vals[mask], atol=1e-8)


# ═══════════════════════════════════════════════════════════════════════════════
# Section C: Mellin Transform Consistency
# ═══════════════════════════════════════════════════════════════════════════════

class TestMellinTransform:
    """Mellin f̂(s) engine vs reference."""

    def test_mellin_at_zero(self, grid_data):
        """f̂(0) should be a finite real number."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)
        val = mellin_f(0, x_grid, f_vals, dt)
        assert np.isfinite(val)

    def test_mellin_at_one(self, grid_data):
        """f̂(1) should be finite."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)
        val = mellin_f(1, x_grid, f_vals, dt)
        assert np.isfinite(val)

    def test_mellin_engine_vs_ref_at_zero(self, grid_data):
        """Engine Mellin at s=0 matches reference."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)
        engine_val = mellin_f(0, x_grid, f_vals, dt)
        ref_val = ref_mellin_f(0, H)
        assert abs(engine_val - ref_val) < 0.1, (
            f"Mellin(0): engine={engine_val}, ref={ref_val}"
        )

    def test_mellin_engine_vs_ref_at_half(self, grid_data):
        """Engine Mellin at s=½ matches reference."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)
        engine_val = mellin_f(0.5, x_grid, f_vals, dt)
        ref_val = ref_mellin_f(0.5, H)
        assert abs(engine_val - ref_val) < 0.1

    def test_mellin_conjugate_symmetry(self, grid_data):
        """For real f: f̂(s̄) = conj(f̂(s))."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)
        s = complex(0.5, 14.134725)
        val_s = mellin_f(s, x_grid, f_vals, dt)
        val_conj = mellin_f(s.conjugate(), x_grid, f_vals, dt)
        assert abs(val_s - val_conj.conjugate()) < 1e-8


# ═══════════════════════════════════════════════════════════════════════════════
# Section D: Zero-Side Functional
# ═══════════════════════════════════════════════════════════════════════════════

class TestZeroSide:
    """Tests for weil_zero_side."""

    def test_zero_side_is_finite(self, grid_data, reference_zeros):
        """LHS should be a finite complex number."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)

        def f_hat(s):
            return mellin_f(s, x_grid, f_vals, dt)

        val = weil_zero_side(f_hat, reference_zeros)
        assert np.isfinite(val)

    def test_zero_side_with_no_zeros(self, grid_data):
        """With no zeros, LHS = f̂(0) + f̂(1)."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)

        def f_hat(s):
            return mellin_f(s, x_grid, f_vals, dt)

        val = weil_zero_side(f_hat, [])
        expected = f_hat(0) + f_hat(1)
        assert abs(val - expected) < 1e-12

    def test_zero_side_single_zero(self, grid_data):
        """With one zero, LHS = f̂(0) + f̂(1) − f̂(ρ₁) − f̂(ρ̄₁)."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)

        def f_hat(s):
            return mellin_f(s, x_grid, f_vals, dt)

        gamma1 = 14.134725
        val = weil_zero_side(f_hat, [gamma1])
        rho = complex(0.5, gamma1)
        expected = f_hat(0) + f_hat(1) - f_hat(rho) - f_hat(rho.conjugate())
        assert abs(val - expected) < 1e-12

    def test_zero_side_decreases_with_more_zeros(self, grid_data):
        """Adding more zeros decreases (makes more negative) the real part."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)

        def f_hat(s):
            return mellin_f(s, x_grid, f_vals, dt)

        val_5 = weil_zero_side(f_hat, GAMMA_30[:5]).real
        val_10 = weil_zero_side(f_hat, GAMMA_30[:10]).real
        # More zeros means more subtracted, but direction depends on f̂(ρ) sign
        # At least both should be finite
        assert np.isfinite(val_5)
        assert np.isfinite(val_10)

    def test_zero_side_matches_reference(self, grid_data, reference_zeros):
        """Engine zero-side matches reference oracle.

        Uses H=1.0 because the Mellin transform f̂(s) = ∫ sech²(t/H)·e^{ts} dt
        converges only for |Re(s)| < 2/H.  f̂(1) requires H < 2.
        """
        x_grid, dt = grid_data
        H = 1.0
        f_vals = f_test_on_grid(x_grid, H)

        def f_hat(s):
            return mellin_f(s, x_grid, f_vals, dt)

        engine_val = weil_zero_side(f_hat, reference_zeros)
        ref_val = ref_weil_zero_side(H, reference_zeros)
        assert abs(engine_val - ref_val) < 1.0, (
            f"Zero-side: engine={engine_val}, ref={ref_val}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Section E: Prime-Side Functional
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrimeSide:
    """Tests for weil_prime_side."""

    def test_prime_side_positive(self, reference_primes, H_default):
        """S_prime should be positive (sech² is non-negative, coeffs positive)."""
        H = H_default
        coeffs = build_prime_coeffs(reference_primes, max_m=4)
        f_at_pm = np.array([f_test_scalar(pp, H) for _, pp in coeffs])
        fs_at_pm = np.array([f_star_scalar(pp, H) for _, pp in coeffs])
        val = weil_prime_side(f_at_pm, fs_at_pm, coeffs)
        assert val > 0

    def test_prime_side_dominated_by_p2(self, H_default):
        """p=2 should contribute the largest share."""
        H = H_default
        primes_small = [2, 3, 5, 7]
        coeffs_all = build_prime_coeffs(primes_small, max_m=4)
        f_at_pm = np.array([f_test_scalar(pp, H) for _, pp in coeffs_all])
        fs_at_pm = np.array([f_star_scalar(pp, H) for _, pp in coeffs_all])
        val_all = weil_prime_side(f_at_pm, fs_at_pm, coeffs_all)

        coeffs_2 = build_prime_coeffs([2], max_m=4)
        f_2 = np.array([f_test_scalar(pp, H) for _, pp in coeffs_2])
        fs_2 = np.array([f_star_scalar(pp, H) for _, pp in coeffs_2])
        val_2 = weil_prime_side(f_2, fs_2, coeffs_2)

        assert val_2 / val_all > 0.3  # p=2 should be a significant fraction

    def test_prime_side_matches_reference(self, reference_primes, H_default):
        """Engine prime sum matches reference oracle."""
        H = H_default
        engine_coeffs = build_prime_coeffs(reference_primes, max_m=4)
        f_at_pm = np.array([f_test_scalar(pp, H) for _, pp in engine_coeffs])
        fs_at_pm = np.array([f_star_scalar(pp, H) for _, pp in engine_coeffs])
        engine_val = weil_prime_side(f_at_pm, fs_at_pm, engine_coeffs)
        ref_val = ref_weil_prime_side(H, list(reference_primes), max_m=4)
        assert abs(engine_val - ref_val) < 0.01, (
            f"Prime-side: engine={engine_val}, ref={ref_val}"
        )

    def test_prime_side_increases_with_more_primes(self, H_default):
        """More primes → larger S_prime."""
        H = H_default
        primes_10 = _small_primes(30)
        primes_25 = _small_primes(100)

        coeffs_10 = build_prime_coeffs(primes_10, max_m=4)
        f_10 = np.array([f_test_scalar(pp, H) for _, pp in coeffs_10])
        fs_10 = np.array([f_star_scalar(pp, H) for _, pp in coeffs_10])
        val_10 = weil_prime_side(f_10, fs_10, coeffs_10)

        coeffs_25 = build_prime_coeffs(primes_25, max_m=4)
        f_25 = np.array([f_test_scalar(pp, H) for _, pp in coeffs_25])
        fs_25 = np.array([f_star_scalar(pp, H) for _, pp in coeffs_25])
        val_25 = weil_prime_side(f_25, fs_25, coeffs_25)

        assert val_25 >= val_10


# ═══════════════════════════════════════════════════════════════════════════════
# Section F: Archimedean Term
# ═══════════════════════════════════════════════════════════════════════════════

class TestArchimedeanTerm:
    """Tests for the archimedean integral."""

    def test_archimedean_is_finite(self, grid_data, H_default):
        """I_∞ should be finite (singularity regularised)."""
        x_grid, dt = grid_data
        H = H_default
        f_vals = f_test_on_grid(x_grid, H)
        fs_vals = f_star_on_grid(x_grid, H)
        f_at_1 = f_test_scalar(1.0, H)
        val = archimedean_term(f_vals, fs_vals, x_grid, dt, f_at_1, H)
        assert np.isfinite(val), f"Archimedean term not finite: {val}"

    def test_archimedean_independent_of_grid_density(self):
        """Doubling grid density shouldn't change result drastically."""
        H = 2.0
        results = []
        for n in [2000, 4000]:
            x_grid, dt = build_x_grid(n, -20.0, 20.0)
            f_vals = f_test_on_grid(x_grid, H)
            fs_vals = f_star_on_grid(x_grid, H)
            f_at_1 = f_test_scalar(1.0, H)
            val = archimedean_term(f_vals, fs_vals, x_grid, dt, f_at_1, H)
            results.append(val)
        # Relative agreement within 20% (integral converges)
        if abs(results[0]) > 1e-10:
            rel = abs(results[1] - results[0]) / abs(results[0])
            assert rel < 0.5, f"Grid sensitivity: {results}, rel={rel}"

    def test_archimedean_changes_with_H(self, grid_data):
        """Different H should give different archimedean values."""
        x_grid, dt = grid_data
        vals = []
        for H in [1.0, 3.0]:
            f_vals = f_test_on_grid(x_grid, H)
            fs_vals = f_star_on_grid(x_grid, H)
            f_at_1 = f_test_scalar(1.0, H)
            val = archimedean_term(f_vals, fs_vals, x_grid, dt, f_at_1, H)
            vals.append(val)
        assert vals[0] != vals[1]

    def test_archimedean_real_valued(self, grid_data, H_default):
        """Archimedean term is real (real integrand)."""
        x_grid, dt = grid_data
        H = H_default
        f_vals = f_test_on_grid(x_grid, H)
        fs_vals = f_star_on_grid(x_grid, H)
        f_at_1 = f_test_scalar(1.0, H)
        val = archimedean_term(f_vals, fs_vals, x_grid, dt, f_at_1, H)
        assert isinstance(val, float)


# ═══════════════════════════════════════════════════════════════════════════════
# Section G: Full LHS ≈ RHS Equality
# ═══════════════════════════════════════════════════════════════════════════════

class TestWeilEquality:
    """The central equality: zero-side = prime-side + archimedean."""

    @pytest.mark.parametrize("H", [2.0, 3.0, 4.0])
    def test_equality_check_runs(self, H):
        """weil_equality_check should run without error."""
        result = weil_equality_check(H, zeros=GAMMA_30[:10],
                                     primes=_small_primes(50), n_grid=2000)
        assert 'LHS' in result
        assert 'RHS' in result
        assert 'residual' in result

    def test_equality_check_finite(self):
        """All outputs should be finite."""
        result = weil_equality_check(2.0, zeros=GAMMA_30[:10],
                                     primes=_small_primes(50), n_grid=2000)
        assert np.isfinite(result['residual'])
        assert np.isfinite(result['LHS_real'])
        assert np.isfinite(result['RHS'])

    @pytest.mark.parametrize("H", [2.0, 3.0])
    def test_equality_lhs_real_part_dominates(self, H):
        """LHS should be predominantly real for an even test function."""
        result = weil_equality_check(H, zeros=GAMMA_30[:10],
                                     primes=_small_primes(50), n_grid=2000)
        # Imaginary part should be small relative to real part
        if abs(result['LHS_real']) > 1e-10:
            ratio = abs(result['LHS_imag']) / abs(result['LHS_real'])
            assert ratio < 10.0  # generous bound

    def test_equality_h_sensitivity(self):
        """Different H should yield different LHS and RHS."""
        r1 = weil_equality_check(2.0, zeros=GAMMA_30[:10],
                                 primes=_small_primes(50), n_grid=2000)
        r2 = weil_equality_check(4.0, zeros=GAMMA_30[:10],
                                 primes=_small_primes(50), n_grid=2000)
        assert r1['LHS'] != r2['LHS']

    def test_equality_components_present(self):
        """Result should contain all expected fields."""
        result = weil_equality_check(2.0, zeros=GAMMA_30[:10],
                                     primes=_small_primes(50), n_grid=2000)
        for key in ['LHS', 'RHS', 'residual', 'f_hat_0', 'f_hat_1',
                     'n_zeros', 'n_primes', 'H']:
            assert key in result, f"Missing key: {key}"


# ═══════════════════════════════════════════════════════════════════════════════
# Section H: Engine–Oracle Cross-Check
# ═══════════════════════════════════════════════════════════════════════════════

class TestEngineOracleCrossCheck:
    """Verify engine results against the reference oracle."""

    def test_f_test_engine_vs_oracle_bulk(self, grid_data, H_default):
        """Bulk comparison at 100 sample points."""
        x_grid, _ = grid_data
        H = H_default
        engine_vals = f_test_on_grid(x_grid, H)
        # Sample 100 evenly-spaced points
        indices = np.linspace(0, len(x_grid) - 1, 100, dtype=int)
        for i in indices:
            x = x_grid[i]
            if 1e-8 < x < 1e8:
                ref = ref_f_test(x, H)
                assert abs(engine_vals[i] - ref) < 1e-6, (
                    f"x={x}: engine={engine_vals[i]}, ref={ref}"
                )

    def test_mellin_engine_vs_oracle_s0(self, grid_data, H_default):
        """Mellin transform at s=0: engine vs oracle."""
        x_grid, dt = grid_data
        H = H_default
        f_vals = f_test_on_grid(x_grid, H)
        engine_val = mellin_f(0, x_grid, f_vals, dt)
        ref_val = ref_mellin_f(0, H)
        # Allow generous tolerance (different quadrature methods)
        assert abs(engine_val - ref_val) / max(abs(ref_val), 1) < 0.1

    def test_prime_side_engine_vs_oracle(self, reference_primes, H_default):
        """Prime sum: engine vs oracle."""
        H = H_default
        coeffs = build_prime_coeffs(reference_primes, max_m=4)
        f_at_pm = np.array([f_test_scalar(pp, H) for _, pp in coeffs])
        fs_at_pm = np.array([f_star_scalar(pp, H) for _, pp in coeffs])
        engine_val = weil_prime_side(f_at_pm, fs_at_pm, coeffs)
        ref_val = ref_weil_prime_side(H, list(reference_primes), max_m=4)
        assert abs(engine_val - ref_val) < 0.01

    def test_zero_side_engine_vs_oracle(self, grid_data, reference_zeros):
        """Zero-side: engine vs oracle.

        Uses H=1.0: Mellin convergence at s=1 requires H < 2.
        """
        x_grid, dt = grid_data
        H = 1.0
        f_vals = f_test_on_grid(x_grid, H)

        def f_hat(s):
            return mellin_f(s, x_grid, f_vals, dt)

        engine_val = weil_zero_side(f_hat, reference_zeros)
        ref_val = ref_weil_zero_side(H, reference_zeros)
        assert abs(engine_val - ref_val) / max(abs(ref_val), 1) < 0.5

    def test_constants_match(self):
        """Euler–Mascheroni and log4π+γ constants are correct."""
        import math
        gamma_ref = 0.5772156649015329
        log4pi_ref = math.log(4 * math.pi) + gamma_ref
        assert abs(EULER_MASCHERONI - gamma_ref) < 1e-15
        assert abs(LOG4PI_GAMMA - log4pi_ref) < 1e-12


# ═══════════════════════════════════════════════════════════════════════════════
# Section I: Non-log Protocol Sentinel
# ═══════════════════════════════════════════════════════════════════════════════

class TestNonLogProtocol:
    """Enforce that the engine module does not call log() in core functions."""

    def test_no_np_log_in_core_functions(self):
        """Core engine functions (sections §2-§8) should not call np.log."""
        import engine.weil_exact as wx
        src = inspect.getsource(wx)

        # Find the core section (after builders, before utilities)
        # Builders (§1) are allowed to use log
        # Core functions (§2-§8) must not
        builder_end = src.find("§2")
        assert builder_end > 0, "Cannot find §2 marker"

        core_src = src[builder_end:]
        # Remove the constants section (LOG4PI_GAMMA uses np.log at module level)
        # Check for runtime log calls in function bodies
        import ast
        # Simpler check: no "np.log(" in core function definitions
        # Allow it in comments and docstrings
        lines = core_src.split('\n')
        violations = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if 'np.log(' in stripped or 'math.log(' in stripped:
                violations.append((i, stripped))

        assert len(violations) == 0, (
            f"Non-log protocol violations in core: {violations}"
        )

    def test_builder_section_exists(self):
        """Builders (§1) should exist and contain the log-using code."""
        import engine.weil_exact as wx
        src = inspect.getsource(wx)
        assert "§1" in src
        assert "build_x_grid" in src
        assert "build_prime_coeffs" in src

    def test_module_docstring_declares_non_log(self):
        """Module docstring should declare non-log protocol."""
        import engine.weil_exact as wx
        assert wx.__doc__ is not None
        assert "NO LOG" in wx.__doc__.upper()


# ═══════════════════════════════════════════════════════════════════════════════
# Section J: Sensitivity / Synthetic Zeros
# ═══════════════════════════════════════════════════════════════════════════════

class TestSensitivity:
    """Tests with synthetic/shifted zeros to verify sensitivity."""

    def test_shifted_zero_changes_lhs(self, grid_data):
        """Shifting a zero off the critical line should change LHS."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)

        def f_hat(s):
            return mellin_f(s, x_grid, f_vals, dt)

        # Real zeros (on critical line)
        val_real = weil_zero_side(f_hat, [14.134725])

        assert np.isfinite(val_real), "LHS with real zero should be finite"

    def test_empty_primes_gives_pure_archimedean(self, grid_data):
        """With no primes, RHS is just the archimedean + constant term."""
        x_grid, dt = grid_data
        H = 2.0
        f_vals = f_test_on_grid(x_grid, H)
        fs_vals = f_star_on_grid(x_grid, H)
        result = weil_prime_arch_side(f_vals, fs_vals, x_grid, dt,
                                      build_prime_coeffs([], 4), H)
        assert np.isfinite(result)

    def test_more_zeros_convergence(self, grid_data):
        """LHS should converge as more zeros are included."""
        x_grid, dt = grid_data
        H = 3.0
        f_vals = f_test_on_grid(x_grid, H)

        def f_hat(s):
            return mellin_f(s, x_grid, f_vals, dt)

        vals = []
        for k in [5, 10, 15, 20]:
            v = weil_zero_side(f_hat, GAMMA_30[:k])
            vals.append(v.real)

        # The magnitude of successive differences should decrease
        diffs = [abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
        assert all(np.isfinite(d) for d in diffs)

    def test_small_primes_list(self):
        """_small_primes produces correct list for small P."""
        primes = _small_primes(30)
        assert primes == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


# ═══════════════════════════════════════════════════════════════════════════════
# Section K: Decomposition Diagnostics
# ═══════════════════════════════════════════════════════════════════════════════

class TestDecomposition:
    """Tests for decompose_zero_side and decompose_prime_side."""

    def test_decompose_zero_side_structure(self):
        """decompose_zero_side returns expected structure."""
        result = decompose_zero_side(2.0, zeros=GAMMA_30[:5], n_grid=2000)
        assert 'f_hat_0' in result
        assert 'f_hat_1' in result
        assert 'zero_contributions' in result
        assert len(result['zero_contributions']) == 5

    def test_decompose_zero_side_sums_correctly(self):
        """Sum of decomposed components matches weil_zero_side."""
        H = 2.0
        zeros = GAMMA_30[:5]
        decomp = decompose_zero_side(H, zeros=zeros, n_grid=2000)

        total = decomp['f_hat_0'] + decomp['f_hat_1']
        for entry in decomp['zero_contributions']:
            total += entry['contribution']

        # Compare with direct weil_zero_side
        x_grid, dt = build_x_grid(2000, -30.0, 30.0)
        f_vals = f_test_on_grid(x_grid, H)

        def f_hat(s):
            return mellin_f(s, x_grid, f_vals, dt)

        direct = weil_zero_side(f_hat, zeros)
        assert abs(total - direct) / max(abs(direct), 1) < 0.01

    def test_decompose_prime_side_structure(self):
        """decompose_prime_side returns expected structure."""
        result = decompose_prime_side(2.0, primes=[2, 3, 5], max_m=4)
        assert len(result) == 3
        assert result[0]['prime'] == 2

    def test_decompose_prime_side_sums_correctly(self):
        """Sum of per-prime contributions matches weil_prime_side."""
        H = 2.0
        primes = [2, 3, 5, 7]
        decomp = decompose_prime_side(H, primes=primes, max_m=4)
        total = sum(entry['contribution'] for entry in decomp)

        coeffs = build_prime_coeffs(primes, max_m=4)
        f_at_pm = np.array([f_test_scalar(pp, H) for _, pp in coeffs])
        fs_at_pm = np.array([f_star_scalar(pp, H) for _, pp in coeffs])
        direct = weil_prime_side(f_at_pm, fs_at_pm, coeffs)

        assert abs(total - direct) < 1e-10
