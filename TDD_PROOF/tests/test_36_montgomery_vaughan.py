#!/usr/bin/env python3
"""
test_36_montgomery_vaughan.py — Montgomery-Vaughan Large Sieve Bound Tests

PURPOSE: Verify the rigorous MV large sieve inequality implementations
in engine/montgomery_vaughan.py, and confirm that gravity_functional.py
and holy_grail.py use properly-grounded bounds rather than ad hoc heuristics.

MATHEMATICAL TARGET:
  - mv_dirichlet_l2_bound(N, T, δβ) = (T + 2πN) · Σ_{n≤N} n^{−1−2δβ}
  - mv_large_sieve_inequality(N, Q)  = N + Q²
  - mv_large_sieve_factor(N)         = 1 / (1 + log(N)/2)  ∈ (0,1]
  - Bound holds numerically: ∫|D_N|² dt ≤ (T + 2πN)·Σ|aₙ|²

COVERAGE: 4 test classes × 4 tests = 16 tests
"""

import pytest
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# §1 — Classical MV Inequality Forms
# ─────────────────────────────────────────────────────────────────────────────

class TestMVClassicalInequalities:
    """Test the classical (N + Q²) large sieve inequality form."""

    def test_large_sieve_inequality_positive_definite(self):
        """(N + Q²) is strictly positive for all N, Q ≥ 1."""
        from engine.montgomery_vaughan import mv_large_sieve_inequality
        for N in [1, 5, 20, 100]:
            for Q in [1, 3, 10, 50]:
                val = mv_large_sieve_inequality(N, Q)
                assert val > 0, f"Factor negative: N={N}, Q={Q}"
                assert np.isfinite(val), f"Factor infinite: N={N}, Q={Q}"

    def test_large_sieve_scales_quadratically_with_Q(self):
        """(N + Q²) grows as Q² for large Q (N fixed)."""
        from engine.montgomery_vaughan import mv_large_sieve_inequality
        N = 10
        # For Q ≫ sqrt(N): factor ≈ Q²
        Q1, Q2 = 100, 200
        f1 = mv_large_sieve_inequality(N, Q1)
        f2 = mv_large_sieve_inequality(N, Q2)
        # Double Q → ≈ quadruple factor
        ratio = f2 / f1
        assert 3.9 <= ratio <= 4.1, f"Q-scaling ratio {ratio:.4f} not near 4"

    def test_large_sieve_factor_exceeds_N(self):
        """(N + Q²) ≥ N for all Q ≥ 1."""
        from engine.montgomery_vaughan import mv_large_sieve_inequality
        for N in [5, 20, 60]:
            for Q in [1, 5, 10]:
                val = mv_large_sieve_inequality(N, Q)
                assert val >= N, f"(N+Q²) < N: N={N}, Q={Q}, val={val}"

    def test_dirichlet_l2_sum_positive_for_all_N(self):
        """Σ_{n≤N} n^{−1−2δβ} > 0 for all N ≥ 1 and δβ ≥ 0."""
        from engine.montgomery_vaughan import dirichlet_l2_sum
        for N in [1, 5, 10, 50, 200]:
            for db in [0.0, 0.01, 0.1, 0.5]:
                val = dirichlet_l2_sum(N, db)
                assert val > 0, f"L² sum ≤ 0: N={N}, δβ={db}"
                assert np.isfinite(val), f"L² sum infinite: N={N}, δβ={db}"


# ─────────────────────────────────────────────────────────────────────────────
# §2 — Dirichlet L² Bound Properties
# ─────────────────────────────────────────────────────────────────────────────

class TestMVDirichletL2Bound:
    """Test structural properties of mv_dirichlet_l2_bound(N, T, δβ)."""

    def test_mv_bound_positive(self):
        """Bound (T + 2πN) · Σ|aₙ|² is strictly positive."""
        from engine.montgomery_vaughan import mv_dirichlet_l2_bound
        for N in [10, 30, 60]:
            for T in [5.0, 14.0, 50.0]:
                for db in [0.0, 0.05, 0.2]:
                    val = mv_dirichlet_l2_bound(N, T, db)
                    assert val > 0, f"Bound ≤ 0: N={N}, T={T}, db={db}"
                    assert np.isfinite(val)

    def test_mv_bound_increases_with_N(self):
        """Larger N → larger MV bound (more terms in L² sum)."""
        from engine.montgomery_vaughan import mv_dirichlet_l2_bound
        T, db = 20.0, 0.01
        b10 = mv_dirichlet_l2_bound(10, T, db)
        b30 = mv_dirichlet_l2_bound(30, T, db)
        b60 = mv_dirichlet_l2_bound(60, T, db)
        assert b10 < b30 < b60, f"Bounds not monotone in N: {b10:.4f}, {b30:.4f}, {b60:.4f}"

    def test_mv_bound_increases_with_T(self):
        """Larger T → larger MV bound (factor T + 2πN grows)."""
        from engine.montgomery_vaughan import mv_dirichlet_l2_bound
        N, db = 30, 0.01
        b5  = mv_dirichlet_l2_bound(N, 5.0,  db)
        b20 = mv_dirichlet_l2_bound(N, 20.0, db)
        b50 = mv_dirichlet_l2_bound(N, 50.0, db)
        assert b5 < b20 < b50, f"Bounds not monotone in T: {b5:.4f}, {b20:.4f}, {b50:.4f}"

    def test_mv_bound_decreases_with_delta_beta(self):
        """Larger δβ → smaller Dirichlet L² sum → smaller bound."""
        from engine.montgomery_vaughan import mv_dirichlet_l2_bound
        N, T = 30, 20.0
        b0   = mv_dirichlet_l2_bound(N, T, 0.0)
        b01  = mv_dirichlet_l2_bound(N, T, 0.1)
        b05  = mv_dirichlet_l2_bound(N, T, 0.5)
        assert b0 > b01 > b05, f"Bounds not monotone in δβ: {b0:.4f}, {b01:.4f}, {b05:.4f}"


# ─────────────────────────────────────────────────────────────────────────────
# §3 — Arithmetic Binding Properties
# ─────────────────────────────────────────────────────────────────────────────

class TestMVArithmeticBinding:
    """Test the MV bound connection to HP-arithmetic isomorphism."""

    def test_mv_bound_exceeds_raw_l2_sum(self):
        """(T + 2πN) · Σ|aₙ|² ≥ Σ|aₙ|² since (T + 2πN) ≥ 1."""
        from engine.montgomery_vaughan import mv_dirichlet_l2_bound, dirichlet_l2_sum
        for N in [10, 30, 60]:
            for T in [5.0, 20.0]:
                for db in [0.0, 0.05]:
                    raw = dirichlet_l2_sum(N, db)
                    bound = mv_dirichlet_l2_bound(N, T, db)
                    assert bound >= raw, f"MV bound < L² sum: {bound:.4f} < {raw:.4f}"

    def test_mv_large_sieve_factor_in_unit_interval(self):
        """Dampening factor f_MV(N) ∈ (0, 1] for all N ≥ 2."""
        from engine.montgomery_vaughan import mv_large_sieve_factor
        for N in [2, 5, 10, 20, 40, 100, 500]:
            f = mv_large_sieve_factor(N)
            assert 0.0 < f <= 1.0, f"Factor outside (0,1]: N={N}, f={f:.6f}"
            assert np.isfinite(f)

    def test_von_mangoldt_l2_sum_positive(self):
        """Σ Λ(n)²/n > 0 for N ≥ 2 (at least n=2 contributes log(2)²/2)."""
        from engine.montgomery_vaughan import mv_von_mangoldt_l2_sum
        for N in [2, 5, 10, 30, 60]:
            val = mv_von_mangoldt_l2_sum(N)
            assert val > 0, f"Von Mangoldt L² sum ≤ 0 for N={N}"
            assert np.isfinite(val), f"Von Mangoldt L² sum infinite for N={N}"

    def test_mv_large_sieve_factor_decreases_with_N(self):
        """f_MV(N) is strictly decreasing: larger N → stronger dampening."""
        from engine.montgomery_vaughan import mv_large_sieve_factor
        N_vals = [5, 10, 20, 40, 80]
        factors = [mv_large_sieve_factor(N) for N in N_vals]
        for i in range(len(factors) - 1):
            assert factors[i] > factors[i+1], (
                f"Factor not decreasing: f({N_vals[i]})={factors[i]:.4f} "
                f"≤ f({N_vals[i+1]})={factors[i+1]:.4f}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# §4 — Integration and Numerical Verification
# ─────────────────────────────────────────────────────────────────────────────

class TestMVIntegration:
    """Test MV module integration with the proof codebase and numeric validity."""

    def test_gravity_functional_uses_mv_bound(self):
        """B_HP_to_explicit_formula imports mv_dirichlet_l2_bound from MV module."""
        import ast
        import pathlib

        src = pathlib.Path(
            __file__
        ).parent.parent / "engine" / "gravity_functional.py"
        tree = ast.parse(src.read_text())

        # Check for `from .montgomery_vaughan import mv_dirichlet_l2_bound`
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if (node.module and 'montgomery_vaughan' in node.module
                        and any(alias.name == 'mv_dirichlet_l2_bound'
                                for alias in node.names)):
                    found = True
                    break
        assert found, "gravity_functional.py does not import mv_dirichlet_l2_bound"

    def test_holy_grail_uses_mv_factor(self):
        """intrinsic_epsilon_derivation imports mv_large_sieve_factor from MV module."""
        import ast
        import pathlib

        src = pathlib.Path(
            __file__
        ).parent.parent / "engine" / "holy_grail.py"
        tree = ast.parse(src.read_text())

        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if (node.module and 'montgomery_vaughan' in node.module
                        and any(alias.name == 'mv_large_sieve_factor'
                                for alias in node.names)):
                    found = True
                    break
        assert found, "holy_grail.py does not import mv_large_sieve_factor"

    def test_dirichlet_bound_holds_numerically(self):
        """
        Numerical verification: ∫|D_N(t)|² dt ≤ (T + 2πN) · Σ|aₙ|².

        Uses mv_verify_dirichlet_bound() to evaluate the inequality
        directly by quadrature for a small Dirichlet polynomial.
        """
        from engine.montgomery_vaughan import mv_verify_dirichlet_bound

        result = mv_verify_dirichlet_bound(
            T0=14.135,       # Near γ₁ Riemann zero
            N=10,            # Small N for speed
            delta_beta=0.01,
            T_window=10.0,
            n_points=300,
        )

        assert result['bound_holds'], (
            f"MV bound violated: ratio={result['ratio']:.4f} > 1.0 "
            f"(integral={result['numerical_integral']:.4e}, "
            f"bound={result['mv_upper_bound']:.4e})"
        )
        assert result['ratio'] <= 1.0, f"ratio={result['ratio']:.6f} exceeds 1"

    def test_mv_arithmetic_bound_positive_and_finite(self):
        """mv_arithmetic_bound returns a positive finite value."""
        from engine.montgomery_vaughan import mv_arithmetic_bound

        for T0 in [14.135, 21.022, 25.011]:
            for N in [20, 40, 60]:
                for db in [0.001, 0.05, 0.1]:
                    val = mv_arithmetic_bound(T0, N, H=3.0, delta_beta=db)
                    assert val > 0, f"mv_arithmetic_bound ≤ 0: T0={T0}, N={N}, db={db}"
                    assert np.isfinite(val), f"mv_arithmetic_bound infinite: T0={T0}, N={N}, db={db}"
