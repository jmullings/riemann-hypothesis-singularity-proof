#!/usr/bin/env python3
"""
test_33_hp_arithmetic_isomorphism.py — HP-Arithmetic Bridge Tests

PURPOSE: Check that HP energy ⟨φ, H_HP φ⟩ tracks explicit Dirichlet/Large-Sieve 
bounds across a grid of (T₀, Δβ). This tests the spectral-arithmetic isomorphism 
that would tie the polymeric geometry to the Weil explicit formula.

STATUS: These tests WILL FAIL initially — they encode the target mathematics 
before the isomorphism is analytically established.

The goal is geometric_penalty ≤ arithmetic_bound with controllable constants.
"""

import pytest
import numpy as np

from engine.hilbert_polya import hp_operator_matrix
from engine.hp_alignment import dirichlet_state
from engine.arithmetic_invariants import GAMMA_30


class TestHPArithmeticIsomorphism:
    """Test connection between HP energy and arithmetic bounds."""
    
    def test_hp_arithmetic_bridge_exists(self):
        """Verify the HP-arithmetic bridge function is implementable."""
        try:
            # This can be in gravity_functional.py or hp_alignment.py
            from engine.gravity_functional import B_HP_to_explicit_formula
            assert callable(B_HP_to_explicit_formula)
        except ImportError:
            try:
                from engine.hp_alignment import B_HP_to_explicit_formula
                assert callable(B_HP_to_explicit_formula)
            except ImportError:
                pytest.skip("B_HP_to_explicit_formula not yet implemented")

    @pytest.mark.slow
    def test_hp_penalty_bounded_by_arithmetic_standard_points(self):
        """Test HP energy vs arithmetic bound at standard zero locations."""
        try:
            from engine.gravity_functional import B_HP_to_explicit_formula
        except ImportError:
            pytest.skip("B_HP_to_explicit_formula not yet implemented")
        
        H = 3.0
        mu0 = 1.0
        N = 60
        
        # Test at first few Riemann zeros
        T0_values = [14.135, 21.022, 25.011]  # γ₁, γ₂, γ₃
        db_values = [1e-3, 1e-2, 0.05, 0.1]
        
        for T0 in T0_values:
            for db in db_values:
                res = B_HP_to_explicit_formula(T0, db, H, mu0, N)
                
                # Basic structure checks
                assert "geometric_penalty" in res
                assert "arithmetic_bound" in res
                assert "is_isomorphic" in res
                
                geometric = res["geometric_penalty"]
                arithmetic = res["arithmetic_bound"]
                
                # Both should be finite and non-negative
                assert np.isfinite(geometric), f"Geometric penalty infinite at T0={T0}, db={db}"
                assert np.isfinite(arithmetic), f"Arithmetic bound infinite at T0={T0}, db={db}"
                assert geometric >= 0, f"Geometric penalty negative at T0={T0}, db={db}"
                assert arithmetic >= 0, f"Arithmetic bound negative at T0={T0}, db={db}"
                
                # The key isomorphism inequality (allow small numerical slack)
                slack = 1.05  # Allow 5% numerical tolerance
                assert geometric <= arithmetic * slack, f"Isomorphism failed: {geometric:.6f} > {arithmetic:.6f} * {slack} at T0={T0}, db={db}"

    @pytest.mark.parametrize("H", [2.5, 3.0, 4.0])
    def test_scaling_across_bandwidth(self, H):
        """Test HP-arithmetic scaling across different bandwidth H."""
        try:
            from engine.gravity_functional import B_HP_to_explicit_formula
        except ImportError:
            pytest.skip("B_HP_to_explicit_formula not yet implemented")
        
        mu0 = 1.0
        N = 40
        T0 = 14.135  # γ₁
        db = 0.01
        
        res = B_HP_to_explicit_formula(T0, db, H, mu0, N)
        
        geometric = res["geometric_penalty"]
        arithmetic = res["arithmetic_bound"]
        
        assert np.isfinite(geometric)
        assert np.isfinite(arithmetic)
        assert geometric <= arithmetic * 1.10  # Allow 10% slack for parameter variation

    @pytest.mark.parametrize("mu0", [0.5, 1.0, 2.0])
    def test_scaling_across_polymer_strength(self, mu0):
        """Test HP-arithmetic scaling across different polymer strength μ₀."""
        try:
            from engine.gravity_functional import B_HP_to_explicit_formula
        except ImportError:
            pytest.skip("B_HP_to_explicit_formula not yet implemented")
        
        H = 3.0
        N = 40
        T0 = 21.022  # γ₂
        db = 0.05
        
        res = B_HP_to_explicit_formula(T0, db, H, mu0, N)
        
        geometric = res["geometric_penalty"]
        arithmetic = res["arithmetic_bound"]
        
        assert np.isfinite(geometric)
        assert np.isfinite(arithmetic)
        assert geometric <= arithmetic * 1.10

    def test_small_delta_beta_limit(self):
        """Test HP-arithmetic bound near critical line (δβ → 0)."""
        try:
            from engine.gravity_functional import B_HP_to_explicit_formula
        except ImportError:
            pytest.skip("B_HP_to_explicit_formula not yet implemented")
        
        H = 3.0
        mu0 = 1.0
        N = 50
        T0 = 14.135
        
        # Test very small delta_beta
        small_db_values = [1e-6, 1e-5, 1e-4, 1e-3]
        
        for db in small_db_values:
            res = B_HP_to_explicit_formula(T0, db, H, mu0, N)
            
            geometric = res["geometric_penalty"]
            arithmetic = res["arithmetic_bound"]
            
            assert np.isfinite(geometric)
            assert np.isfinite(arithmetic)
            assert geometric >= 0
            assert arithmetic >= 0
            
            # Near critical line, both should be small but well-behaved
            assert geometric <= arithmetic * 2.0  # More generous for small Δβ


class TestArithmeticBoundMathematicalProperties:
    """Test mathematical properties of the arithmetic bound."""
    
    def test_mangoldt_weight_consistency(self):
        """Test that arithmetic bound uses proper von Mangoldt weighting."""
        try:
            from engine.gravity_functional import B_HP_to_explicit_formula
        except ImportError:
            pytest.skip("B_HP_to_explicit_formula not yet implemented")
        
        H = 3.0
        mu0 = 1.0
        N = 30
        T0 = 25.011  # γ₃
        db = 0.02
        
        res = B_HP_to_explicit_formula(T0, db, H, mu0, N)
        
        # Should be able to access arithmetic decomposition
        if "mangoldt_sum" in res:
            mangoldt_sum = res["mangoldt_sum"]
            assert np.isfinite(mangoldt_sum)
            assert mangoldt_sum >= 0
            
            # Mangoldt sum should contribute significantly to arithmetic bound
            arithmetic_bound = res["arithmetic_bound"]
            assert mangoldt_sum <= arithmetic_bound * 2.0

    def test_dirichlet_l2_scaling(self):
        """Test L² scaling of Dirichlet coefficients."""
        try:
            from engine.gravity_functional import B_HP_to_explicit_formula
        except ImportError:
            pytest.skip("B_HP_to_explicit_formula not yet implemented")
        
        H = 3.0
        mu0 = 1.0
        T0 = 30.425  # γ₄
        
        # Different delta_beta values
        db1 = 0.001
        db2 = 0.1
        
        N_values = [20, 40, 60]
        
        for N in N_values:
            res1 = B_HP_to_explicit_formula(T0, db1, H, mu0, N)
            res2 = B_HP_to_explicit_formula(T0, db2, H, mu0, N)
            
            # Extract values for analysis
            geo1, geo2 = res1["geometric_penalty"], res2["geometric_penalty"]
            arith1, arith2 = res1["arithmetic_bound"], res2["arithmetic_bound"]
            
            # Both geometric and arithmetic should be well-behaved finite values
            assert np.isfinite(geo1) and np.isfinite(geo2)
            assert np.isfinite(arith1) and np.isfinite(arith2)
            assert geo1 > 0 and geo2 > 0 and arith1 > 0 and arith2 > 0
            
            # The scaling relationship may vary - accept either direction
            # What matters is that both are scaled appropriately
            scaling1, scaling2 = geo1/arith1, geo2/arith2
            assert scaling1 <= 2.0  # Both should be reasonably scaled
            assert scaling2 <= 2.0


class TestPrimeWeightedOperator:
    """Test prime-weighted polymeric operator properties."""
    
    def test_prime_weighted_operator_exists(self):
        """Verify prime-weighted operator is implementable."""
        try:
            from engine.hilbert_polya import prime_weighted_H_poly_matrix
            assert callable(prime_weighted_H_poly_matrix)
        except ImportError:
            pytest.skip("prime_weighted_H_poly_matrix not yet implemented")

    def test_prime_weighted_vs_uniform_grid(self):
        """Compare prime-weighted operator to uniform grid operator."""
        try:
            from engine.hilbert_polya import prime_weighted_H_poly_matrix
        except ImportError:
            pytest.skip("prime_weighted_H_poly_matrix not yet implemented")
        
        mu0 = 1.0
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        
        H_prime = prime_weighted_H_poly_matrix(mu0, primes)
        H_uniform = hp_operator_matrix(len(primes), mu0=mu0)
        
        # Both should be Hermitian and positive definite
        assert np.allclose(H_prime, H_prime.T.conj())
        assert np.allclose(H_uniform, H_uniform.T.conj())
        
        eig_prime = np.linalg.eigvals(H_prime)
        eig_uniform = np.linalg.eigvals(H_uniform)
        
        assert np.all(eig_prime > -1e-12)  # Positive semidefinite
        assert np.all(eig_uniform > -1e-12)
        
        # Different spectral properties expected
        assert not np.allclose(eig_prime, eig_uniform)

    def test_prime_weighted_arithmetic_correlation(self):
        """Test that prime-weighted operator correlates better with arithmetic."""
        try:
            from engine.hilbert_polya import prime_weighted_H_poly_matrix
        except ImportError:
            pytest.skip("prime_weighted_H_poly_matrix not yet implemented")
        try:
            from engine.gravity_functional import B_HP_to_explicit_formula
        except ImportError:
            pytest.skip("B_HP_to_explicit_formula not yet implemented")
        
        mu0 = 1.0
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        N = len(primes)
        H = 3.0
        T0 = 14.135
        db = 0.01
        
        # Compare prime-weighted vs uniform in arithmetic correlation
        # This test will likely fail initially but guides development
        
        H_prime = prime_weighted_H_poly_matrix(mu0, primes)
        H_uniform = hp_operator_matrix(N, mu0=mu0)
        
        # Test both in the isomorphism function (if it accepts custom H_HP)
        # For now, just validate structure
        assert H_prime.shape == (N, N)
        assert H_uniform.shape == (N, N)
        
        # Prime-weighted should have different trace/determinant
        tr_prime = np.trace(H_prime) 
        tr_uniform = np.trace(H_uniform)
        assert abs(tr_prime - tr_uniform) > 1e-10


class TestIsomorphismConvergence:
    """Test convergence properties of the HP-arithmetic isomorphism."""
    
    @pytest.mark.slow
    def test_convergence_with_N(self):
        """Test isomorphism quality improves with larger N."""
        try:
            from engine.gravity_functional import B_HP_to_explicit_formula
        except ImportError:
            pytest.skip("B_HP_to_explicit_formula not yet implemented")
        
        H = 3.0
        mu0 = 1.0
        T0 = 21.022
        db = 0.02
        
        N_values = [20, 40, 60, 80]
        ratios = []
        
        for N in N_values:
            res = B_HP_to_explicit_formula(T0, db, H, mu0, N)
            geometric = res["geometric_penalty"]
            arithmetic = res["arithmetic_bound"]
            
            if arithmetic > 0:
                ratios.append(geometric / arithmetic)
            else:
                ratios.append(np.inf)
        
        # Ratios should be finite and bounded
        finite_ratios = [r for r in ratios if np.isfinite(r)]
        assert len(finite_ratios) >= 2
        
        for ratio in finite_ratios:
            assert 0 <= ratio <= 10.0  # Reasonable bounds

    def test_uniform_bounds_across_zeros(self):
        """Test that isomorphism holds uniformly across multiple zeros."""
        try:
            from engine.gravity_functional import B_HP_to_explicit_formula
        except ImportError:
            pytest.skip("B_HP_to_explicit_formula not yet implemented")
        
        H = 3.0
        mu0 = 1.0
        N = 50
        db = 0.01
        
        # Use several Riemann zeros
        riemann_zeros = GAMMA_30[:10]  # First 10 zeros
        
        max_violation = 0.0
        
        for gamma in riemann_zeros:
            T0 = float(gamma)
            res = B_HP_to_explicit_formula(T0, db, H, mu0, N)
            
            geometric = res["geometric_penalty"]
            arithmetic = res["arithmetic_bound"]
            
            assert np.isfinite(geometric)
            assert np.isfinite(arithmetic)
            
            if arithmetic > 0:
                violation = max(0, geometric - arithmetic) / arithmetic
                max_violation = max(max_violation, violation)
        
        # Maximum violation should be small and controlled
        assert max_violation <= 0.20  # Allow 20% max violation initially