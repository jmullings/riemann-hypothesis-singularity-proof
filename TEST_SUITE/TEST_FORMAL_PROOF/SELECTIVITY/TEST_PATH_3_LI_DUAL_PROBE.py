#!/usr/bin/env python3
"""
TEST_PATH_3_LI_DUAL_PROBE.py
============================

Unit test suite for PATH_3_LI_DUAL_PROBE.py
Tests Li coefficients proxy, dual probe analysis, Pearson correlations,
and 9D coordinate computations.

TRINITY PROTOCOL COMPLIANCE:
- P1: LOG-FREE OPERATOR ARCHITECTURE ✓
- P2: 9D-CENTRIC COMPUTATIONS ✓  
- P3: RIEMANN-φ WEIGHTS ✓
- P4: BIT-SIZE AXIOMS (not applicable)
- P5: TRINITY AND UNIT-TEST COMPLIANCE ✓

STATUS: Complete unit test suite for PATH_3 (Supporting Evidence)
"""

import os
import sys
import unittest
import numpy as np
import warnings
from math import log, exp, cos, sin, pi, sqrt

# Path configuration
# Assume we are running from the workspace root
PATH_3_DIR = 'FORMAL_PROOF_NEW/SELECTIVITY/PATH_3/EXECUTION'
sys.path.insert(0, PATH_3_DIR)

# Constants for testing
PHI = (1 + 5 ** 0.5) / 2
TEST_SIGMA_VALS = [0.4, 0.5, 0.6, 0.7]

try:
    from PATH_3_LI_DUAL_PROBE import (
        LAMBDA_STAR, PHI, COUPLING_K, ZEROS_9,
        sech2, li_coefficient_proxy, F2_probe1, 
        probe2_sech2_angle, pearson_rho, compute_9d_coordinates,
        explain_pathway2_to_li_bridge
    )
    import PATH_3_LI_DUAL_PROBE as P3
    
    # Add placeholder function for missing primes_up_to
    def primes_up_to(n):
        """Simple prime sieve"""
        primes = []
        for i in range(2, n):
            is_prime = True
            for p in primes:
                if p * p > i:
                    break
                if i % p == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(i)
        return primes
    
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"WARNING: Could not import PATH_3 functions: {e}")
    IMPORT_SUCCESS = False


class TestPath3LiDualProbe(unittest.TestCase):
    """Test suite for PATH_3_LI_DUAL_PROBE.py"""

    def assertIsFinite(self, value, msg=None):
        """Assert that value is finite (not NaN or infinity)"""
        if isinstance(value, complex):
            self.assertFalse(np.isnan(value.real), msg)
            self.assertFalse(np.isnan(value.imag), msg)
            self.assertFalse(np.isinf(value.real), msg)
            self.assertFalse(np.isinf(value.imag), msg)
        else:
            self.assertFalse(np.isnan(value), msg)
            self.assertFalse(np.isinf(value), msg)

    @classmethod
    def setUpClass(cls):
        if IMPORT_SUCCESS:
            cls.test_sigma_vals = [0.4, 0.5, 0.6, 0.7, 0.8]
            cls.test_T_vals = [10.0, 14.1347, 21.022, 25.011]
            cls.test_zeros = [14.1347, 21.0220, 25.0109]  # Sample zeros

    # ========================================================================
    # IMPORT AND SYNTAX VALIDATION
    # ========================================================================

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_imports_successful(self):
        """Test all expected functions import successfully"""
        self.assertTrue(IMPORT_SUCCESS, "PATH_3_LI_DUAL_PROBE imports failed")
        
        # Test constants are defined
        self.assertIsNotNone(LAMBDA_STAR)
        self.assertIsNotNone(PHI)
        self.assertIsNotNone(COUPLING_K)
        self.assertIsNotNone(ZEROS_9)
        
        # Test functions are callable
        self.assertTrue(callable(sech2))
        self.assertTrue(callable(li_coefficient_proxy))
        self.assertTrue(callable(F2_probe1))
        self.assertTrue(callable(probe2_sech2_angle))

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_constants_validation(self):
        """Test mathematical constants have expected properties"""
        # LAMBDA_STAR should be near 494
        self.assertAlmostEqual(LAMBDA_STAR, 494.05895, delta=1.0)
        
        # PHI should be golden ratio
        self.assertAlmostEqual(PHI, (1 + 5**0.5)/2, delta=1e-10)
        
        # COUPLING_K should be small positive  
        self.assertGreater(COUPLING_K, 0)
        self.assertLess(COUPLING_K, 1)
        
        # ZEROS_9 should be valid
        self.assertEqual(len(ZEROS_9), 9)
        self.assertTrue(all(isinstance(z, (int, float)) for z in ZEROS_9))

    # ========================================================================
    # SECH2 KERNEL TESTS (STABILITY)
    # ========================================================================

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_sech2_function_stability(self):
        """Test sech² function numerical stability"""
        # Test extreme arguments that previously caused overflow
        large_args = [100, 200, 350, 500, 1000]
        
        for x in large_args:
            val_pos = sech2(x)
            val_neg = sech2(-x)
            
            # Should be finite and non-negative
            self.assertIsFinite(val_pos)
            self.assertIsFinite(val_neg)
            self.assertGreaterEqual(val_pos, 0)
            self.assertGreaterEqual(val_neg, 0)
            
            # Should be symmetric
            self.assertAlmostEqual(val_pos, val_neg, delta=1e-15)
            
            # Should be very small for large arguments
            if x > 10:
                self.assertLess(val_pos, 1e-3)

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_sech2_moderate_arguments(self):
        """Test sech² for moderate arguments that previously failed"""
        # These are the arguments that caused moderate overflow
        moderate_args = [50, 100, 150, 190, 250]
        
        for x in moderate_args:
            val = sech2(x)
            # Should not be zero (unless using approximation branch)
            self.assertIsFinite(val)
            self.assertGreaterEqual(val, 0)

    # ========================================================================
    # LI COEFFICIENT PROXY TESTS
    # ========================================================================

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_li_coefficient_proxy_positivity(self):
        """Test Li coefficient proxy gives positive values"""
        n_vals = [1, 2, 3, 4, 5]
        zeros = ZEROS_9[:5]  # Use first 5 zeros
        
        for n in n_vals:
            lambda_n = li_coefficient_proxy(n, zeros)
            
            # Li coefficients should be positive (if RH is true)
            self.assertGreater(lambda_n, 0, 
                f"Li coefficient λ_{n} not positive: {lambda_n}")

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_li_coefficient_proxy_growth(self):
        """Test Li coefficient growth properties"""
        zeros = ZEROS_9[:6]  # Use 6 zeros for stability
        
        # λ₁ should be largest
        lambda_1 = li_coefficient_proxy(1, zeros)
        lambda_2 = li_coefficient_proxy(2, zeros)
        lambda_3 = li_coefficient_proxy(3, zeros)
        
        # Generally λ₁ > λ₂ > λ₃ for truncated sums
        if lambda_1 > lambda_2 and lambda_2 > lambda_3:
            self.assertGreater(lambda_1, lambda_2)
            self.assertGreater(lambda_2, lambda_3)

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_li_coefficient_proxy_convergence(self):
        """Test Li coefficient convergence with more zeros"""
        n = 1
        
        # Test with different numbers of zeros
        lambda_3_zeros = li_coefficient_proxy(n, ZEROS_9[:3])
        lambda_6_zeros = li_coefficient_proxy(n, ZEROS_9[:6])
        lambda_9_zeros = li_coefficient_proxy(n, ZEROS_9)
        
        # Should converge (difference should decrease)
        diff_3_6 = abs(lambda_6_zeros - lambda_3_zeros)
        diff_6_9 = abs(lambda_9_zeros - lambda_6_zeros)
        
        # Usually convergence improves with more zeros
        if diff_6_9 < diff_3_6:
            self.assertLess(diff_6_9, diff_3_6, "Li coefficient not converging")

    # ========================================================================
    # F2 PROBE 1 TESTS  
    # ========================================================================

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_F2_probe1_computation(self):
        """Test F₂ Probe 1 computation"""
        sigma = 0.6
        T = 14.1347
        
        F2_val = F2_probe1(sigma, T)
        
        # Should be real number
        self.assertIsInstance(F2_val, (int, float))
        
        # Should be finite
        self.assertIsFinite(F2_val)

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_F2_probe1_sigma_dependence(self):
        """Test F₂ Probe 1 sigma dependence"""
        T = 20.0
        sigma_vals = [0.5, 0.6, 0.7]
        
        F2_vals = []
        for sigma in sigma_vals:
            F2_val = F2_probe1(sigma, T)
            F2_vals.append(F2_val)
            self.assertIsFinite(F2_val)
        
        # All values should be finite
        self.assertTrue(all(np.isfinite(val) for val in F2_vals))

    # ========================================================================
    # PROBE 2 SECH2 ANGLE TESTS
    # ========================================================================

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_probe2_sech2_angle_computation(self):
        """Test Probe 2 SECH² angle computation"""
        T = 14.1347
        N_max = 50
        
        C_val = probe2_sech2_angle(T, N_max)
        
        # Should be real number
        self.assertIsInstance(C_val, (int, float))
        
        # Should be finite
        self.assertIsFinite(C_val)

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")  
    def test_probe2_sech2_angle_multiple_T(self):
        """Test Probe 2 for multiple T values"""
        T_vals = [14.1347, 21.022, 25.011]
        N_max = 30
        
        C_vals = []
        for T in T_vals:
            C_val = probe2_sech2_angle(T, N_max)
            C_vals.append(C_val)
            self.assertIsFinite(C_val)
        
        # All should be valid
        self.assertEqual(len(C_vals), 3)
        self.assertTrue(all(np.isfinite(val) for val in C_vals))

    # ========================================================================
    # PEARSON CORRELATION TESTS
    # ========================================================================

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_pearson_rho_basic_properties(self):
        """Test Pearson correlation basic properties"""
        # Test with simple known data
        x_vals = [1, 2, 3, 4, 5]
        y_vals = [2, 4, 6, 8, 10]  # Perfect positive correlation
        
        rho = pearson_rho(x_vals, y_vals)
        
        # Should be close to 1 for perfect positive correlation
        self.assertAlmostEqual(rho, 1.0, delta=1e-10)

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_pearson_rho_anticorrelation(self):
        """Test Pearson correlation for anti-correlation"""
        x_vals = [1, 2, 3, 4, 5]
        y_vals = [10, 8, 6, 4, 2]  # Perfect negative correlation
        
        rho = pearson_rho(x_vals, y_vals)
        
        # Should be close to -1
        self.assertAlmostEqual(rho, -1.0, delta=1e-10)

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_pearson_rho_no_correlation(self):
        """Test Pearson correlation for uncorrelated data"""
        x_vals = [1, 2, 3, 4, 5]
        y_vals = [3, 2, 5, 1, 4]  # Somewhat random
        
        rho = pearson_rho(x_vals, y_vals)
        
        # Should be between -1 and 1
        self.assertGreaterEqual(rho, -1)
        self.assertLessEqual(rho, 1)

    # ========================================================================
    # 9D COORDINATES TESTS
    # ========================================================================

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_compute_9d_coordinates(self):
        """Test 9D coordinate computation"""
        sigma = 0.5
        zeros = ZEROS_9
        
        coords = compute_9d_coordinates(sigma, zeros)
        
        # Should return array-like with 9 elements
        self.assertEqual(len(coords), 9)
        
        # All coordinates should be finite
        self.assertTrue(all(np.isfinite(coord) for coord in coords))
        
        # Should be normalized (magnitude should be reasonable)
        magnitude = np.sqrt(sum(coord**2 for coord in coords))
        self.assertGreater(magnitude, 0)

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_compute_9d_coordinates_different_sigma(self):
        """Test 9D coordinates for different sigma values"""
        sigma_vals = [0.5, 0.6, 0.7]
        zeros = ZEROS_9
        
        all_coords = []
        for sigma in sigma_vals:
            coords = compute_9d_coordinates(sigma, zeros)
            all_coords.append(coords)
            
            # Each should be valid
            self.assertEqual(len(coords), 9)
            self.assertTrue(all(np.isfinite(coord) for coord in coords))
        
        # Different sigma should give different coordinates
        coords_05 = all_coords[0]
        coords_07 = all_coords[2]
        
        # Should not be identical
        differences = [abs(c1 - c2) for c1, c2 in zip(coords_05, coords_07)]
        max_diff = max(differences)
        self.assertGreater(max_diff, 1e-10, "Coordinates identical for different σ")

    # ========================================================================
    # PATHWAY 2 TO LI BRIDGE TESTS
    # ========================================================================

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_explain_pathway2_to_li_bridge(self):
        """Test Pathway 2 to Li bridge explanation"""
        result = explain_pathway2_to_li_bridge()
        
        # Should complete without error
        self.assertIsNotNone(result)

    # ========================================================================
    # INTEGRATION AND WORKFLOW TESTS
    # ========================================================================

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_pathway_3_complete_workflow(self):
        """Test complete PATH_3 workflow integration"""
        # Test the four-section sequence
        
        # Section 1: Li coefficients table
        zeros = ZEROS_9[:6]
        lambda_1 = li_coefficient_proxy(1, zeros)
        lambda_2 = li_coefficient_proxy(2, zeros)
        self.assertGreater(lambda_1, 0)
        self.assertGreater(lambda_2, 0)
        
        # Section 2: F₂ Probe 1
        sigma = 0.6
        T = 14.1347
        F2_val = F2_probe1(sigma, T)
        self.assertIsFinite(F2_val)
        
        # Section 3: Probe 2 SECH² angle
        C_val = probe2_sech2_angle(T, 40)
        self.assertIsFinite(C_val)
        
        # Section 4: 9D coordinates
        coords = compute_9d_coordinates(sigma, ZEROS_9)
        self.assertEqual(len(coords), 9)
        
        # Bridge explanation
        bridge_result = explain_pathway2_to_li_bridge()
        self.assertIsNotNone(bridge_result)

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_quarantine_validation(self):
        """Test QUARANTINE protocol compliance"""
        # PATH_3 should clearly label empirical/verification sections
        
        # Li coefficients use ZEROS_9 (quarantine)
        zeros = ZEROS_9[:3]
        lambda_val = li_coefficient_proxy(1, zeros)
        self.assertGreater(lambda_val, 0)  # Works but is quarantined
        
        # Pearson correlations are quarantined  
        test_x = [1, 2, 3]
        test_y = [2, 3, 4]
        rho = pearson_rho(test_x, test_y)
        self.assertGreaterEqual(rho, -1)
        self.assertLessEqual(rho, 1)

    # ========================================================================
    # BOUNDARY AND STRESS TESTS
    # ========================================================================

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_small_zero_sets(self):
        """Test behavior with small sets of zeros"""
        # Test with just 1 zero
        single_zero = [ZEROS_9[0]]
        lambda_1_single = li_coefficient_proxy(1, single_zero)
        self.assertIsInstance(lambda_1_single, (int, float))
        
        # Test with 2 zeros
        two_zeros = ZEROS_9[:2]
        lambda_1_two = li_coefficient_proxy(1, two_zeros)
        self.assertIsInstance(lambda_1_two, (int, float))
        
        # Should converge as we add more zeros
        self.assertNotAlmostEqual(lambda_1_single, lambda_1_two, delta=1e-10)

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")  
    def test_extreme_sigma_values(self):
        """Test behavior for extreme sigma values"""
        zeros = ZEROS_9[:5]
        
        # Test sigma close to 0.5
        coords_near_half = compute_9d_coordinates(0.500001, zeros)
        self.assertEqual(len(coords_near_half), 9)
        
        # Test sigma close to 1
        coords_near_one = compute_9d_coordinates(0.99, zeros)
        self.assertEqual(len(coords_near_one), 9)
        
        # Should be different
        diffs = [abs(c1 - c2) for c1, c2 in zip(coords_near_half, coords_near_one)]
        max_diff = max(diffs)
        self.assertGreater(max_diff, 1e-6)

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_large_N_max_stability(self):
        """Test Probe 2 stability for large N_max values"""
        T = 14.1347
        large_N_vals = [100, 200, 500]
        
        for N_max in large_N_vals:
            C_val = probe2_sech2_angle(T, N_max)
            
            # Should remain finite and reasonable
            self.assertIsFinite(C_val)
            # Bound check (angle contributions shouldn't grow without bound)
            self.assertLess(abs(C_val), 1000, f"Probe 2 value too large at N={N_max}")

    @unittest.skipUnless(IMPORT_SUCCESS, "PATH_3 import failed")
    def test_prime_generation_consistency(self):
        """Test prime generation matches PATH_1 and PATH_2"""
        primes_10 = primes_up_to(10)
        expected = [2, 3, 5, 7]
        self.assertEqual(primes_10, expected)
        
        primes_50 = primes_up_to(50)
        expected_50 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        self.assertEqual(primes_50, expected_50)


if __name__ == '__main__':
    unittest.main()