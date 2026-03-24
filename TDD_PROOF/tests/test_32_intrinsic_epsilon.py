#!/usr/bin/env python3
"""
test_32_intrinsic_epsilon.py — Intrinsic ε Derivation Tests

PURPOSE: Force a precise scaling law for ε(H,μ₀,N) to emerge from
dimensional analysis and Dirichlet variance, not grid-search.

STATUS: These tests WILL FAIL initially — they encode the target
mathematics before the analytic derivation exists.

The goal is to find ε_intrinsic such that:
  0.1 ≤ ε_intrinsic / ε_empirical ≤ 10.0

This provides a quantitative target for developing the analytic bound.
"""

import pytest
import numpy as np

from engine.holy_grail import compact_domain_epsilon
from engine.hilbert_polya import hp_operator_matrix
from engine.hp_alignment import dirichlet_state


class TestIntrinsicEpsilonScaling:
    """Test intrinsic epsilon derivation against empirical grid-search."""
    
    def test_intrinsic_epsilon_function_exists(self):
        """Verify the intrinsic epsilon function is implementable."""
        # This should import without error once implemented
        try:
            from engine.holy_grail import intrinsic_epsilon_derivation
            assert callable(intrinsic_epsilon_derivation)
        except ImportError:
            pytest.skip("intrinsic_epsilon_derivation not yet implemented")
    
    @pytest.mark.slow
    def test_matches_grid_search_scaling_standard_params(self):
        """Test intrinsic vs empirical epsilon for standard parameters."""
        try:
            from engine.holy_grail import intrinsic_epsilon_derivation
        except ImportError:
            pytest.skip("intrinsic_epsilon_derivation not yet implemented")
        
        H = 3.0
        mu0 = 1.0
        N = 60
        
        # Empirical epsilon (ground truth from grid-search)
        H_hp = hp_operator_matrix(N, mu0=mu0)
        compact = compact_domain_epsilon(H, N, H_hp,
                                        db_range=(0.005, 0.35),
                                        T0_range=(0.0, 80.0),
                                        n_db=10, n_T0=10)
        eps_emp = compact["epsilon_0"]
        
        # Dirichlet variance proxy at reference point
        T0_ref = 14.135
        phi = dirichlet_state(T0_ref, N, delta_beta=0.01)
        dir_var = float(np.real(np.vdot(phi, phi)))
        
        # Intrinsic derivation (DRAFT implementation)
        eps_intr = intrinsic_epsilon_derivation(H, mu0, N, dir_var)
        
        # Scaling relationship check (order-of-magnitude agreement)
        assert eps_intr > 0, "Intrinsic epsilon must be positive"
        assert np.isfinite(eps_intr), "Intrinsic epsilon must be finite"
        
        scaling_ratio = eps_intr / eps_emp
        assert 0.1 <= scaling_ratio <= 10.0, f"Scaling ratio {scaling_ratio:.3f} outside target range"
    
    @pytest.mark.parametrize("H", [2.0, 3.0, 4.0])
    @pytest.mark.parametrize("mu0", [0.5, 1.0, 2.0])
    def test_scaling_consistency_across_parameters(self, H, mu0):
        """Test intrinsic epsilon scaling across different H and μ₀."""
        try:
            from engine.holy_grail import intrinsic_epsilon_derivation
        except ImportError:
            pytest.skip("intrinsic_epsilon_derivation not yet implemented")
        
        N = 40  # Smaller N for parametric test
        
        # Reference Dirichlet variance
        T0_ref = 21.022
        phi = dirichlet_state(T0_ref, N, delta_beta=0.05)
        dir_var = float(np.real(np.vdot(phi, phi)))
        
        eps_intr = intrinsic_epsilon_derivation(H, mu0, N, dir_var)
        
        # Check dimensional scaling expectations
        assert eps_intr > 0
        assert np.isfinite(eps_intr)
        
        # Should scale roughly as 1/H² (Bochner scale)
        if H > 1.5:
            assert eps_intr < 100.0  # Reasonable upper bound
        
        # Should scale roughly as 1/μ₀² (polymeric scale)
        if mu0 < 0.8:
            assert eps_intr > 0.001  # Reasonable lower bound

    def test_dirichlet_variance_sensitivity(self):
        """Test that intrinsic epsilon responds to Dirichlet variance."""
        try:
            from engine.holy_grail import intrinsic_epsilon_derivation
        except ImportError:
            pytest.skip("intrinsic_epsilon_derivation not yet implemented")
        
        H = 3.0
        mu0 = 1.0
        N = 30
        
        # Two different variance levels
        low_var = 0.1
        high_var = 1.0
        
        eps_low = intrinsic_epsilon_derivation(H, mu0, N, low_var)
        eps_high = intrinsic_epsilon_derivation(H, mu0, N, high_var)
        
        assert eps_low > 0
        assert eps_high > 0
        assert eps_high > eps_low  # Higher variance should need larger coupling


class TestIntrinsicEpsilonMathematicalProperties:
    """Test mathematical properties of intrinsic epsilon derivation."""
    
    def test_dimensional_analysis_consistency(self):
        """Verify dimensional analysis gives sensible results."""
        try:
            from engine.holy_grail import intrinsic_epsilon_derivation
        except ImportError:
            pytest.skip("intrinsic_epsilon_derivation not yet implemented")
        
        # Test dimensional scaling H⁻² × μ₀⁻² × variance
        H1, H2 = 2.0, 4.0
        mu1, mu2 = 1.0, 2.0
        var = 1.0
        N = 50
        
        eps1 = intrinsic_epsilon_derivation(H1, mu1, N, var)
        eps2 = intrinsic_epsilon_derivation(H2, mu2, N, var)
        
        # H scaling: ε ∝ H⁻²
        expected_H_scaling = (H1/H2)**2
        # μ₀ scaling: ε ∝ μ₀⁻²  
        expected_mu_scaling = (mu2/mu1)**2
        expected_ratio = expected_H_scaling * expected_mu_scaling
        
        actual_ratio = eps1 / eps2
        # Allow factor of 2 tolerance for dimensional analysis
        assert 0.5 * expected_ratio <= actual_ratio <= 2.0 * expected_ratio

    def test_continuity_at_reference_point(self):
        """Test continuity of intrinsic epsilon near reference parameters."""
        try:
            from engine.holy_grail import intrinsic_epsilon_derivation
        except ImportError:
            pytest.skip("intrinsic_epsilon_derivation not yet implemented")
        
        H_ref = 3.0
        mu0_ref = 1.0
        N = 40
        var_ref = 0.5
        
        eps_ref = intrinsic_epsilon_derivation(H_ref, mu0_ref, N, var_ref)
        
        # Small perturbations
        h = 0.1
        eps_H_plus = intrinsic_epsilon_derivation(H_ref + h, mu0_ref, N, var_ref)
        eps_mu_plus = intrinsic_epsilon_derivation(H_ref, mu0_ref + h, N, var_ref) 
        eps_var_plus = intrinsic_epsilon_derivation(H_ref, mu0_ref, N, var_ref + h)
        
        # Check continuity (changes should be small)
        assert abs(eps_H_plus - eps_ref) < abs(eps_ref)
        assert abs(eps_mu_plus - eps_ref) < abs(eps_ref)
        assert abs(eps_var_plus - eps_ref) < abs(eps_ref)


@pytest.mark.slow
class TestEpsilonConvergenceProperties:
    """Test convergence and limiting behavior of intrinsic epsilon."""
    
    def test_large_N_scaling(self):
        """Test epsilon behavior as N increases."""
        try:
            from engine.holy_grail import intrinsic_epsilon_derivation
        except ImportError:
            pytest.skip("intrinsic_epsilon_derivation not yet implemented")
        
        H = 3.0
        mu0 = 1.0
        var = 0.5
        
        N_values = [20, 40, 60, 80]
        eps_values = [intrinsic_epsilon_derivation(H, mu0, N, var) for N in N_values]
        
        # All should be positive and finite
        for eps in eps_values:
            assert eps > 0
            assert np.isfinite(eps)
        
        # Should show some convergence pattern (not necessarily monotonic)
        ratios = [eps_values[i+1]/eps_values[i] for i in range(len(eps_values)-1)]
        for ratio in ratios:
            assert 0.1 <= ratio <= 10.0  # Bounded variation

    def test_critical_parameter_limits(self):
        """Test behavior near critical parameter values."""
        try:
            from engine.holy_grail import intrinsic_epsilon_derivation
        except ImportError:
            pytest.skip("intrinsic_epsilon_derivation not yet implemented")
        
        N = 50
        var = 1.0
        
        # Near H = 2 (convergence boundary for Mellin)
        H_crit = 2.0 + 1e-6
        mu0 = 1.0
        eps_H_crit = intrinsic_epsilon_derivation(H_crit, mu0, N, var)
        assert eps_H_crit > 0
        assert np.isfinite(eps_H_crit)
        
        # Small μ₀ (large polymeric scale)
        H = 3.0
        mu0_small = 0.1
        eps_mu_small = intrinsic_epsilon_derivation(H, mu0_small, N, var)
        assert eps_mu_small > 0
        assert eps_mu_small < 1000.0  # Should not blow up