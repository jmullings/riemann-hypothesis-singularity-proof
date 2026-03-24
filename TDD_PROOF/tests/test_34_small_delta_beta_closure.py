#!/usr/bin/env python3
"""
test_34_small_delta_beta_closure.py

TDD test for small-Δβ formal closure using pure Weil/sech² spine.

OBJECTIVE: Prove that for any hypothetical off-critical zero at ½ + iγ₀ + Δβ 
(where Δβ > 0 is small), the refined Weil explicit formula with γ₀-dependent
oscillations can force the Rayleigh quotient λ*(γ₀) > 4/H² for appropriately
chosen H, thus sealing the crack without HP scaffolding.

KEY TESTS:
1. γ₀-dependent Weil formula produces correct oscillatory behavior
2. Optimal H selection algorithm works
3. Closure condition can be satisfied for test cases
4. Grid scan shows reasonable success rates
5. Strict certificates can be generated

STATUS: DESIGNED TO FAIL INITIALLY - These tests establish mathematical
targets for rigorous closure implementation.
"""

import sys
import os

# Add the parent directory to the path so we can import from engine/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import numpy as np
from unittest.mock import patch

from engine.offcritical import (
    weil_delta_A_gamma0_dependent,
    optimal_H_for_closure,
    weil_closure_test_single,
    scan_closure_grid,
    closure_certificate_strict,
)


class TestGamma0DependentWeilFormula(unittest.TestCase):
    """Test the γ₀-dependent Weil explicit formula implementation."""
    
    def test_gamma0_oscillation_behavior(self):
        """Test that cos(2πγ₀/H) factor produces expected oscillations."""
        H = 5.0
        delta_beta = 0.01
        
        # Sample γ₀ values that should give cos = +1, -1, 0
        gamma_plus = 0.0        # cos(0) = +1
        gamma_minus = H / 2     # cos(π) = -1  
        gamma_zero = H / 4      # cos(π/2) = 0
        
        delta_A_plus = weil_delta_A_gamma0_dependent(gamma_plus, delta_beta, H)
        delta_A_minus = weil_delta_A_gamma0_dependent(gamma_minus, delta_beta, H)  
        delta_A_zero = weil_delta_A_gamma0_dependent(gamma_zero, delta_beta, H)
        
        # Check oscillation pattern
        self.assertAlmostEqual(delta_A_plus, -delta_A_minus, places=12,
                             msg="cos oscillation should flip sign between γ=0 and γ=H/2")
        self.assertAlmostEqual(abs(delta_A_zero), 0.0, places=10,
                             msg="cos oscillation should vanish at γ=H/4")
        
        # Check base formula structure (should match reference computation)
        base_val_expected = -2 * np.pi * (H**2) * (delta_beta**3) / np.sin(np.pi * H * delta_beta / 2)
        self.assertAlmostEqual(delta_A_plus / np.cos(0), base_val_expected, places=8,
                             msg="Base Weil formula should match theoretical prediction")
    
    def test_small_delta_beta_scaling(self):
        """Test Δβ² scaling behavior of the γ₀-dependent formula (small HΔβ limit)."""
        H = 3.0
        gamma_0 = 14.135  # Choose to get cos ≈ 1 for consistent sign
        
        delta_betas = [0.1, 0.01, 0.001]
        delta_A_values = []
        
        for db in delta_betas:
            delta_A = weil_delta_A_gamma0_dependent(gamma_0, db, H)
            delta_A_values.append(delta_A)
        
        # For small HΔβ: ΔA ≈ -4HΔβ² · cos(2πγ₀/H)
        # Check quadratic scaling: ratio should be ~(db₁/db₂)²  
        ratio_10x = abs(delta_A_values[1] / delta_A_values[0])  # 0.01/0.1 = 0.1
        ratio_100x = abs(delta_A_values[2] / delta_A_values[1])  # 0.001/0.01 = 0.1
        
        expected_ratio = (0.1)**2  # = 0.01 for quadratic scaling
        self.assertAlmostEqual(ratio_10x, expected_ratio, places=2,
                             msg="10x smaller Δβ should give ~100x smaller |ΔA| (quadratic)")
        self.assertAlmostEqual(ratio_100x, expected_ratio, places=2,
                             msg="100x smaller Δβ should maintain quadratic scaling")
    
    def test_H_dependence_structure(self):
        """Test that H enters the formula correctly (accounting for cos oscillations)."""
        # Choose γ₀ and H values to avoid rapid cosine oscillations
        gamma_0 = 0.0  # cos(0) = 1 for all H
        delta_beta = 0.02  # Small enough for linear regime
        
        H_values = [3.0, 6.0, 9.0]
        delta_A_values = []
        
        for H in H_values:
            delta_A = weil_delta_A_gamma0_dependent(gamma_0, delta_beta, H)
            delta_A_values.append(delta_A)
        
        # For small HΔβ, ΔA ≈ -4HΔβ² · cos(2πγ₀/H) = -4HΔβ² when γ₀=0
        # So ΔA should scale linearly with H
        ratio_2x = abs(delta_A_values[1] / delta_A_values[0])  # H=6 vs H=3
        ratio_3x = abs(delta_A_values[2] / delta_A_values[0])  # H=9 vs H=3
        
        self.assertAlmostEqual(ratio_2x, 2.0, places=1,
                             msg="Doubling H should double |ΔA| when γ₀=0")
        self.assertAlmostEqual(ratio_3x, 3.0, places=1,
                             msg="Tripling H should triple |ΔA| when γ₀=0")


class TestOptimalHSelection(unittest.TestCase):
    """Test the optimal H selection algorithm for closure conditions."""
    
    def test_H_scaling_with_delta_beta(self):
        """Test that H ∼ 1/Δβ scaling works as expected (with bounds)."""
        gamma_0 = 14.135
        scaling_factor = 1.0
        
        # Use moderate Δβ values to avoid hitting bounds
        delta_betas = [0.2, 0.1, 0.05]
        H_values = []
        
        for db in delta_betas:
            H_opt = optimal_H_for_closure(db, gamma_0, scaling_factor=scaling_factor)
            H_values.append(H_opt)
        
        # Check inverse relationship: H₁ * Δβ₁ ≈ H₂ * Δβ₂ (within bounds)
        products = [H_values[i] * delta_betas[i] for i in range(3)]
        
        # Allow some variation due to bounds enforcement
        max_variation = max(products) / min(products)
        self.assertLess(max_variation, 2.0,
                       msg="H * Δβ products should be reasonably consistent")
        
        # Check that smaller Δβ gives larger H
        self.assertGreater(H_values[1], H_values[0] * 0.9,
                          msg="Smaller Δβ should generally give larger H")
        self.assertGreater(H_values[2], H_values[1] * 0.9,
                          msg="Even smaller Δβ should give even larger H")
    
    def test_H_bounds_enforcement(self):
        """Test that H stays within practical bounds."""
        gamma_0 = 14.135
        
        # Very small Δβ should hit upper bound
        delta_beta_tiny = 1e-8
        H_tiny = optimal_H_for_closure(delta_beta_tiny, gamma_0)
        self.assertLessEqual(H_tiny, 100.0, msg="H should not exceed max bound")
        
        # Large Δβ should hit lower bound  
        delta_beta_large = 1.0
        H_large = optimal_H_for_closure(delta_beta_large, gamma_0, base_H=3.0)
        self.assertGreaterEqual(H_large, 3.0, msg="H should not go below base_H")
        
        # Zero/negative Δβ should return base_H
        H_zero = optimal_H_for_closure(0.0, gamma_0, base_H=5.0)
        self.assertEqual(H_zero, 5.0, msg="H(Δβ=0) should return base_H")


class TestClosureConditionSingle(unittest.TestCase):
    """Test closure condition evaluation at single points."""
    
    def test_on_critical_line_always_closed(self):
        """Test that Δβ = 0 always satisfies closure condition."""
        gamma_0 = 14.135
        delta_beta = 0.0
        H = 3.0
        
        result = weil_closure_test_single(gamma_0, delta_beta, H)
        
        self.assertTrue(result['closure_achieved'], 
                       msg="On-critical line should always be closed")
        self.assertTrue(result['on_critical_line'],
                       msg="Should detect on-critical case")
        self.assertEqual(result['violation_margin'], 0.0,
                       msg="No violation margin on critical line")
    
    def test_very_small_delta_beta_behavior(self):
        """Test behavior for very small but nonzero Δβ."""
        gamma_0 = 14.135
        H = 3.0
        
        # Test decreasing Δβ values
        delta_betas = [0.1, 0.01, 0.001, 0.0001]
        margins = []
        
        for db in delta_betas:
            result = weil_closure_test_single(gamma_0, db, H)
            margins.append(result['violation_margin'])
        
        # As Δβ → 0, violation margin should approach some limit
        # (could be positive or negative depending on the specifics)
        self.assertTrue(all(isinstance(m, (int, float)) for m in margins),
                       msg="All margins should be numeric")
        self.assertTrue(len(set(np.sign(margins))) <= 2,
                       msg="Margins should have consistent sign pattern")
    
    def test_optimal_vs_fixed_H_comparison(self):
        """Test that optimal H selection can improve closure success."""
        gamma_0 = 21.022
        delta_beta = 0.05
        
        # Test with fixed H = 3.0
        result_fixed = weil_closure_test_single(gamma_0, delta_beta, H=3.0)
        
        # Test with optimal H
        result_optimal = weil_closure_test_single(gamma_0, delta_beta, H=None)
        
        # Optimal H should give at least as good (or better) violation margin
        self.assertGreaterEqual(result_optimal['violation_margin'], 
                               result_fixed['violation_margin'] - 1e-10,
                               msg="Optimal H should not be worse than fixed H")
        
        # Record the H values used
        self.assertIsInstance(result_optimal['H_used'], (int, float))
        self.assertEqual(result_fixed['H_used'], 3.0)


class TestClosureGridScan(unittest.TestCase):
    """Test grid scanning for closure conditions."""
    
    def test_basic_grid_scan_structure(self):
        """Test that grid scanning returns proper data structure."""
        gamma_values = [14.135, 21.022, 25.011]
        delta_beta_values = [0.1, 0.01, 0.001]
        
        result = scan_closure_grid(gamma_values, delta_beta_values, H_strategy='fixed')
        
        # Check return format
        self.assertIn('closure_matrix', result)
        self.assertIn('failed_points', result) 
        self.assertIn('success_rate', result)
        self.assertIn('total_points', result)
        
        # Check shape
        expected_shape = (len(gamma_values), len(delta_beta_values))
        self.assertEqual(result['closure_matrix'].shape, expected_shape)
        self.assertEqual(result['total_points'], 9)  # 3x3 grid
        
        # Check success rate bounds
        self.assertGreaterEqual(result['success_rate'], 0.0)
        self.assertLessEqual(result['success_rate'], 1.0)
    
    def test_different_H_strategies(self):
        """Test different H selection strategies."""
        gamma_values = [14.135, 21.022]
        delta_beta_values = [0.01, 0.001]
        
        # Test fixed strategy
        result_fixed = scan_closure_grid(gamma_values, delta_beta_values, 
                                       H_strategy='fixed')
        
        # Test optimal strategy  
        result_optimal = scan_closure_grid(gamma_values, delta_beta_values,
                                        H_strategy='optimal')
        
        # Test custom H value
        result_custom = scan_closure_grid(gamma_values, delta_beta_values,
                                        H_strategy=5.0)
        
        # All should complete successfully
        self.assertIsInstance(result_fixed['success_rate'], (int, float))
        self.assertIsInstance(result_optimal['success_rate'], (int, float))
        self.assertIsInstance(result_custom['success_rate'], (int, float))
    
    def test_closure_success_expectations(self):
        """Test expectations about closure success rates."""
        # Test case designed to have some successes and failures
        gamma_values = np.linspace(10, 30, 5)
        delta_beta_values = [0.1, 0.01, 0.001]
        
        result = scan_closure_grid(gamma_values, delta_beta_values, 
                                 H_strategy='optimal')
        
        # Expect that optimal H strategy achieves some closure successes
        # NOTE: This test may initially fail - indicates need for algorithm improvement
        self.assertGreater(result['success_rate'], 0.0,
                          msg="Optimal H strategy should achieve some closures")
        
        # Failed points should have detailed diagnostics
        if result['failed_points']:
            first_failure = result['failed_points'][0]
            required_keys = ['gamma_0', 'delta_beta', 'H_used', 'violation_margin']
            for key in required_keys:
                self.assertIn(key, first_failure,
                            msg=f"Failed point should include {key}")


class TestStrictClosureCertificate(unittest.TestCase):
    """Test strict closure certificate generation."""
    
    def test_certificate_structure(self):
        """Test that closure certificate has proper structure."""
        gamma_0 = 14.135
        delta_beta = 0.01
        
        cert = closure_certificate_strict(gamma_0, delta_beta, max_H=20.0, H_steps=10)
        
        # Check required fields
        required_fields = ['certificate_valid', 'best_H', 'best_margin', 'scan_results']
        for field in required_fields:
            self.assertIn(field, cert, msg=f"Certificate should include {field}")
        
        # Check scan results structure
        if cert['scan_results']:
            scan_point = cert['scan_results'][0]
            scan_fields = ['H', 'margin', 'lambda_eff', 'threshold', 'cosine_factor']
            for field in scan_fields:
                self.assertIn(field, scan_point, msg=f"Scan point should include {field}")
    
    def test_certificate_on_critical_line(self):
        """Test certificate for on-critical case (Δβ = 0)."""
        gamma_0 = 14.135
        delta_beta = 0.0
        
        cert = closure_certificate_strict(gamma_0, delta_beta)
        
        self.assertTrue(cert['certificate_valid'],
                       msg="Certificate should be valid on critical line")
        self.assertIn('reason', cert)
        self.assertEqual(cert['best_margin'], 0.0)
    
    def test_certificate_optimization(self):
        """Test that certificate finds the best H in the scan range."""
        gamma_0 = 21.022
        delta_beta = 0.02
        
        cert = closure_certificate_strict(gamma_0, delta_beta, max_H=50.0, H_steps=20)
        
        # Best H should correspond to best margin
        if cert['scan_results']:
            margins = [pt['margin'] for pt in cert['scan_results']]
            best_margin_in_scan = max(margins)
            
            self.assertAlmostEqual(cert['best_margin'], best_margin_in_scan, places=10,
                                 msg="Certificate should find the actual maximum margin")
            
            # Best H should be within the scan range  
            self.assertGreaterEqual(cert['best_H'], 3.0)
            self.assertLessEqual(cert['best_H'], 50.0)


class TestMathematicalConsistency(unittest.TestCase):
    """Test mathematical consistency of the closure framework."""
    
    def test_closure_vs_rayleigh_quotient(self):
        """Test consistency between closure test and raw Rayleigh quotient."""
        gamma_0 = 14.135
        delta_beta = 0.01
        H = 4.0
        
        # Get closure test result
        closure_result = weil_closure_test_single(gamma_0, delta_beta, H)
        
        # Manually compute threshold
        threshold_manual = 4.0 / (H**2)
        
        self.assertAlmostEqual(closure_result['lambda_threshold'], threshold_manual, places=12,
                             msg="Threshold computation should match manual calculation")
        
        # Check violation margin sign consistency
        margin = closure_result['violation_margin'] 
        lambda_eff = closure_result['lambda_eff']
        threshold = closure_result['lambda_threshold']
        
        self.assertAlmostEqual(margin, lambda_eff - threshold, places=12,
                             msg="Violation margin should equal λ_eff - threshold")
    
    def test_delta_A_limit_behavior(self):
        """Test limiting behavior of ΔA as Δβ → 0."""
        gamma_0 = 0.0  # Choose to avoid cosine complications
        H = 3.0
        
        # Compute ΔA for decreasing Δβ values
        delta_betas = np.logspace(-1, -6, 20)  # 0.1 down to 1e-6
        delta_A_values = []
        
        for db in delta_betas:
            delta_A = weil_delta_A_gamma0_dependent(gamma_0, db, H)
            delta_A_values.append(delta_A)
        
        # Check that ΔA → 0 as Δβ → 0 (with realistic tolerance)
        final_values = delta_A_values[-3:]  # Last 3 values (Δβ ~ 1e-5 to 1e-6)
        self.assertTrue(all(abs(val) < 1e-8 for val in final_values),
                       msg="ΔA should approach 0 as Δβ → 0 (within 1e-8)")
        
        # Check monotonic decrease (in absolute value) - with some tolerance for numerics
        abs_values = [abs(val) for val in delta_A_values]
        decreasing_violations = sum(1 for i in range(len(abs_values)-1) 
                                  if abs_values[i+1] > abs_values[i] * 1.2)
        self.assertLess(decreasing_violations, 3,
                       msg="ΔA magnitude should decrease mostly monotonically")


if __name__ == '__main__':
    # Configure test output
    import warnings
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    
    print("\n" + "="*80)
    print("TDD TEST: Small-Δβ Formal Closure (Pure Weil/sech² Spine)")
    print("="*80)
    print("OBJECTIVE: Verify that γ₀-dependent Weil oscillations can seal")
    print("           the small-Δβ crack without HP scaffolding.")
    print("STATUS: DESIGNED TO FAIL INITIALLY")
    print("="*80)
    
    # Run tests with detailed output
    unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromModule(sys.modules[__name__]))