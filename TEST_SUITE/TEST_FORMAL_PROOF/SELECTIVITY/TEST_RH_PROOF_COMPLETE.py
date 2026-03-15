#!/usr/bin/env python3
"""
TEST_RH_PROOF_COMPLETE.py
=========================

Comprehensive unit test suite for RH_PROOF_COMPLETE.py
Tests the complete σ-Selectivity proof implementation covering all 10 phases.

This test suite validates:
- Module import and basic constants
- Phase-specific function availability  
- Key mathematical invariants across phases
- Proof chain integration
- Computational results consistency

TRINITY PROTOCOL COMPLIANCE:
- P1: LOG-FREE OPERATOR ARCHITECTURE ✓
- P2: 9D-CENTRIC COMPUTATIONS ✓  
- P3: RIEMANN-φ WEIGHTS ✓
- P4: BIT-SIZE AXIOMS ✓
- P5: TRINITY AND UNIT-TEST COMPLIANCE ✓

STATUS: Complete unit test suite for unified RH_PROOF_COMPLETE.py
"""

import os
import sys
import unittest
import numpy as np
import warnings
import importlib.util
from math import log, exp, cos, sin, pi, sqrt, cosh

# Path configuration - RH_PROOF_COMPLETE.py location
RH_PROOF_PATH = '../../../FORMAL_PROOF_NEW/SELECTIVITY/PATH_COMPLETE/EXECUTION/RH_PROOF_COMPLETE.py'

class TestRHProofComplete(unittest.TestCase):
    """Test suite for the complete RH proof implementation"""

    @classmethod
    def setUpClass(cls):
        """Load the RH_PROOF_COMPLETE module once for all tests"""
        cls.module_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), RH_PROOF_PATH))
        
        if not os.path.exists(cls.module_path):
            raise FileNotFoundError(f"RH_PROOF_COMPLETE.py not found at {cls.module_path}")
        
        try:
            spec = importlib.util.spec_from_file_location('rh_proof', cls.module_path)
            cls.rh_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.rh_module)
            cls.import_success = True
        except Exception as e:
            cls.import_success = False
            cls.import_error = str(e)

    def test_00_module_import(self):
        """Test that the module imports successfully"""
        self.assertTrue(self.import_success, 
                       f"Failed to import RH_PROOF_COMPLETE.py: {getattr(self, 'import_error', 'Unknown error')}")

    def test_01_basic_constants(self):
        """Test that essential mathematical constants are defined correctly"""
        rh = self.rh_module
        
        # Basic mathematical constants
        self.assertAlmostEqual(rh.PI, pi, places=10)
        self.assertAlmostEqual(rh.TWO_PI, 2*pi, places=10)
        self.assertEqual(rh.NDIM, 9)
        self.assertAlmostEqual(rh.PHI, (1 + sqrt(5))/2, places=10)
        self.assertAlmostEqual(rh.H_STAR, 1.5, places=10)
        
        # φ-related constants  
        self.assertAlmostEqual(rh.IPHI2, 1/rh.PHI**2, places=10)
        
        # 9-prime basis
        expected_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        self.assertTrue(hasattr(rh, 'P'))
        np.testing.assert_array_equal(rh.P, expected_primes)
        
        # Riemann zeros (first few)
        self.assertTrue(hasattr(rh, 'ZEROS_9'))
        self.assertEqual(len(rh.ZEROS_9), 9)
        # Check first zero is approximately correct
        self.assertAlmostEqual(rh.ZEROS_9[0], 14.1347251417346937904572519835625, places=5)

    def test_02_phase_functions_exist(self):
        """Test that key functions from all 10 phases are available"""
        rh = self.rh_module
        
        # Phase 01 - Foundations
        essential_functions = [
            'build_phi_metric', 'D_complex', 'E_energy', 'F2_curvature', 'F2_vector_9D',
            # Phase 02 - Bridge & Speiser  
            'S_N_vectorised', 'zeta_approx', 'run_rs_bridge', 'run_speiser',
            # Phase 03 - Prime Geometry
            'compute_x_star_F', 'compute_x_star_G', 'compute_x_star_phi', 'pss_curvature',
            # Phase 04 - Evidence
            'null_distribution', 'run_comparison', 
            # Phase 05 - Uniform Bound
            'F2_S_batch', 'averaged_F2', 'sech2_kernel', 'run_phase_05',
            # Phase 06 - Analytic Convexity  
            'sech2_fourier', 'mv_diagonal', 'fourier_formula_F2bar', 'run_phase_06',
            # Phase 07 - Mellin Spectral
            'build_TH_full', 'mellin_symbol_analytic', 'run_phase_07',
            # Phase 08 - Contradiction & A3
            'averaged_energy', 'run_phase_08',
            # Phase 09 - φ-Curvature  
            'build_b', 'build_Db', 'test_theorem_inequality', 'run_phase_09',
            # Phase 10 - Completion
            'run_consolidated', 'run_phase_10',
            # Master runner
            'run_complete_proof'
        ]
        
        for func_name in essential_functions:
            with self.subTest(function=func_name):
                self.assertTrue(hasattr(rh, func_name), 
                               f"Function {func_name} not found in module")
                self.assertTrue(callable(getattr(rh, func_name)),
                               f"{func_name} is not callable")

    def test_03_phi_metric_properties(self):
        """Test φ-metric construction and properties"""
        rh = self.rh_module
        
        G_PHI = rh.build_phi_metric()
        
        # Check dimensions
        self.assertEqual(G_PHI.shape, (9, 9))
        
        # Check φ-metric property: G[i,j] = φ^(i+j+2) (1-indexed)
        for i in range(9):
            for j in range(9):
                expected = rh.PHI ** (i + j + 2)  # 1-indexed in mathematics  
                self.assertAlmostEqual(G_PHI[i, j], expected, places=10)
        
        # Check symmetry
        np.testing.assert_array_almost_equal(G_PHI, G_PHI.T, decimal=12)
        
        # Check positive definiteness (all eigenvalues > 0)
        eigenvals = np.linalg.eigvals(G_PHI)
        self.assertTrue(np.all(eigenvals > 0), "φ-metric must be positive definite")

    def test_04_energy_functional_basic(self):
        """Test basic energy functional computation"""
        rh = self.rh_module
        
        # Test D complex at σ=0.5, T=0
        D_val = rh.D_complex(0.5, 0.0)
        self.assertIsInstance(D_val, complex)
        
        # Energy should be real and positive
        E_val = rh.E_energy(0.5, 0.0)
        self.assertIsInstance(E_val, (int, float))
        self.assertGreater(E_val, 0)
        
        # Test at a known zero (should be smaller but not exactly 0 due to finite precision)
        gamma1 = float(rh.ZEROS_9[0])  
        E_at_zero = rh.E_energy(0.5, gamma1)
        E_away_zero = rh.E_energy(0.5, gamma1 + 1.0)
        # Energy should be smaller near zeros
        self.assertLess(E_at_zero, E_away_zero)

    def test_05_curvature_positivity(self):
        """Test F₂ curvature positivity at known zeros"""
        rh = self.rh_module
        
        # Test F₂ vector at Riemann zeros
        F2_vector = rh.F2_vector_9D(0.5, rh.ZEROS_9)
        
        # All components should be positive (this is a key result)
        self.assertEqual(len(F2_vector), 9)
        for i, f2_val in enumerate(F2_vector):
            with self.subTest(zero_index=i):
                self.assertGreater(f2_val, 0, 
                                 f"F₂({rh.ZEROS_9[i]:.4f}) = {f2_val} should be positive")
        
        # Total should match expected range
        total_f2 = float(np.sum(F2_vector))
        self.assertGreater(total_f2, 10)    # Much larger than 0
        self.assertLess(total_f2, 10000)    # But not unreasonably large

    def test_06_sech2_properties(self):
        """Test sech² kernel and Fourier transform properties"""
        rh = self.rh_module
        
        H = 1.0
        
        # Test sech² kernel at different points
        w_0 = rh.sech2_kernel(np.array([0.0]), 0.0, H)[0]
        w_1 = rh.sech2_kernel(np.array([H]), 0.0, H)[0]  
        w_inf = rh.sech2_kernel(np.array([10*H]), 0.0, H)[0]
        
        # Properties: peak at 0, decaying
        self.assertAlmostEqual(w_0, 1.0, places=10)  # sech²(0) = 1
        self.assertLess(w_1, w_0)  # decaying  
        self.assertLess(w_inf, 0.01)  # nearly zero far away
        
        # Test Fourier transform properties
        omega_vals = [0.0, 0.5, 1.0, 2.0]
        for omega in omega_vals:
            with self.subTest(omega=omega):
                wh_val = rh.sech2_fourier(omega, H)
                self.assertGreater(wh_val, 0)  # Always positive
                
        # ŵ_H(0) = 2H
        wh_0 = rh.sech2_fourier(0.0, H)
        self.assertAlmostEqual(wh_0, 2*H, places=10)

    def test_07_averaged_convexity(self):
        """Test averaged F₂ convexity for small examples"""
        rh = self.rh_module  
        
        H = 0.5
        T0 = 50.0  # Away from zeros
        N = 100    # Small for fast testing
        
        # Averaged F₂ should be positive
        F2_avg = rh.averaged_F2(T0, H, 0.5, N, n_quad=200)  
        self.assertGreater(F2_avg, 0, "Averaged F₂ must be positive")
        
        # Test batch computation consistency
        T_array = np.array([T0, T0+1, T0+2])
        F2_batch = rh.F2_S_batch(0.5, T_array, N)
        
        self.assertEqual(len(F2_batch), 3)
        # All should be real
        for f2 in F2_batch:
            self.assertIsInstance(float(f2), float)

    def test_08_mellin_spectral_basic(self):
        """Test Mellin spectral operator construction"""
        rh = self.rh_module
        
        H = 1.0
        N = 20  # Small for testing
        
        # Build T_H matrix
        T_matrix = rh.build_TH_full(H, N)
        
        # Check properties
        self.assertEqual(T_matrix.shape, (N, N))
        
        # Should be symmetric
        np.testing.assert_array_almost_equal(T_matrix, T_matrix.T, decimal=10)
        
        # Should be positive semidefinite
        eigenvals = np.linalg.eigvals(T_matrix)
        self.assertTrue(np.all(eigenvals >= -1e-10), "T_H should be PSD")
        
        # Diagonal elements should be 2H (ŵ_H(0) = 2H)
        diag_vals = np.diag(T_matrix)
        np.testing.assert_array_almost_equal(diag_vals, 2*H, decimal=10)

    def test_09_cross_term_identity(self):
        """Test cross-term identity (FPE.8) on small example"""
        rh = self.rh_module
        
        T0 = 20.0
        N = 30
        H = 1.0
        sigma = 0.5
        
        # Build required objects
        b, Db, D2b = rh._build_vectors(T0, sigma, N)
        T_matrix = rh.build_TH_full(H, N)
        
        # LHS: Re⟨TD²b,b⟩
        lhs = float(np.real(np.conj(b) @ (T_matrix @ D2b)))
        
        # RHS components: ⟨TDb,Db⟩ and ∫Λ″|D₀|² correction
        term1 = float(np.real(np.conj(Db) @ (T_matrix @ Db)))
        
        # For testing, approximate the integral with a simple sum
        tau_range = H * 10  # ±10H
        n_tau = 100
        tau_vals = np.linspace(-tau_range, tau_range, n_tau)
        dtau = 2 * tau_range / (n_tau - 1)
        
        correction = 0.0
        for tau in tau_vals:
            Lambda_pp = rh._Lambda_H_pp(tau, H)
            D0_sq = rh._D0_squared(T0, tau, sigma, N)
            correction += Lambda_pp * D0_sq * dtau
        
        term2 = correction / (4 * pi)
        rhs = term1 - term2
        
        # Check identity (within numerical precision)
        rel_error = abs(lhs - rhs) / max(abs(lhs), 1e-15)
        self.assertLess(rel_error, 1e-4, f"Cross-term identity: LHS={lhs:.6f}, RHS={rhs:.6f}")

    def test_10_montgomery_vaughan_diagonal(self):
        """Test Montgomery-Vaughan diagonal computation"""
        rh = self.rh_module
        
        sigma = 0.5
        N_vals = [20, 50, 100]
        
        for N in N_vals:
            with self.subTest(N=N):
                M2 = rh.mv_diagonal(sigma, N)
                
                # Should be positive  
                self.assertGreater(M2, 0)
                
                # Should grow roughly as (ln N)³/3
                if N >= 50:
                    expected_order = (log(N)**3) / 3
                    ratio = M2 / expected_order
                    self.assertGreater(ratio, 0.1)  # Not too small
                    self.assertLess(ratio, 10.0)    # Not too large

    def test_11_lambda_h_properties(self):
        """Test Mellin symbol Λ_H(τ) and its derivatives"""
        rh = self.rh_module
        
        H = rh.H_STAR
        tau_vals = [-2*H, -H, 0, H, 2*H, 5*H]
        
        for tau in tau_vals:
            with self.subTest(tau=tau):
                # Λ_H(τ) > 0 for all τ  
                Lambda_val = rh._Lambda_H(tau, H)
                self.assertGreater(Lambda_val, 0)
                
                # Λ_H(0) = 2π
                if abs(tau) < 1e-10:
                    self.assertAlmostEqual(Lambda_val, 2*pi, places=8)
        
        # Test Λ″_H mean-zero property numerically
        tau_range = 10 * H
        n_tau = 1000
        tau_arr = np.linspace(-tau_range, tau_range, n_tau)
        dtau = 2 * tau_range / (n_tau - 1)
        
        Lambda_pp_vals = np.array([rh._Lambda_H_pp(tau, H) for tau in tau_arr])
        integral = np.trapz(Lambda_pp_vals, dx=dtau)
        
        # Should be very close to 0 (mean-zero property)
        self.assertLess(abs(integral), 1e-6, "∫Λ″_H dτ should be ≈ 0")

    def test_12_proof_chain_consistency(self):
        """Test that key proof chain results are consistent"""
        rh = self.rh_module
        
        # F₂ at zeros should be positive (Phase 01 result)
        F2_zeros = rh.F2_vector_9D(0.5, rh.ZEROS_9)
        total_F2 = float(np.sum(F2_zeros))
        self.assertGreater(total_F2, 0, "Total F₂ at zeros must be positive")
        
        # Averaged convexity should hold (Phase 05 result)
        H = 0.5  # Above critical bandwidth
        T0 = 100.0  # Away from zeros
        F2_avg = rh.averaged_F2(T0, H, 0.5, 200, n_quad=500)
        self.assertGreater(F2_avg, 0, "Averaged F₂ must be positive for H ≥ H_c")
        
        # R should be ≥ -4M₂ (Phase 08 result)
        N = 100
        M2 = rh.mv_diagonal(0.5, N)
        F2_fourier, _, R = rh.fourier_formula_F2bar(T0, rh.H_STAR, 0.5, N)
        
        self.assertGreater(R + 4*M2, -1e-10, "R ≥ -4M₂ inequality must hold")
        self.assertAlmostEqual(F2_fourier, 4*M2 + R, places=8, 
                               msg="F̄₂ = 4M₂ + R decomposition")

    def test_13_master_runner_available(self):
        """Test that the master runner function is callable"""
        rh = self.rh_module
        
        # Check run_complete_proof exists and is callable
        self.assertTrue(hasattr(rh, 'run_complete_proof'))
        self.assertTrue(callable(rh.run_complete_proof))
        
        # Check individual phase runners exist
        phase_runners = [
            'run_rs_bridge', 'run_speiser', 'run_phase_05', 'run_phase_06',
            'run_phase_07', 'run_phase_08', 'run_phase_09', 'run_phase_10'
        ]
        
        for runner in phase_runners:
            with self.subTest(runner=runner):
                self.assertTrue(hasattr(rh, runner), f"Phase runner {runner} missing")
                self.assertTrue(callable(getattr(rh, runner)), f"{runner} not callable")

    def test_14_shared_constants_consistency(self):
        """Test that shared constants are properly deduplicated and consistent"""
        rh = self.rh_module
        
        # Check log table exists and is reasonable
        self.assertTrue(hasattr(rh, '_LOG_TABLE'))
        log_table = rh._LOG_TABLE
        
        # Should start with 0.0 for index 0
        self.assertAlmostEqual(log_table[0], 0.0, places=15)
        
        # Check a few known values
        self.assertAlmostEqual(log_table[1], 0.0, places=15)      # log(1) = 0
        self.assertAlmostEqual(log_table[2], log(2), places=15)   # log(2)
        self.assertAlmostEqual(log_table[10], log(10), places=15) # log(10)
        
        # Check CONT_NORM calculation
        expected_cont_norm = 2*pi - 2*rh.H_STAR
        self.assertAlmostEqual(rh.CONT_NORM, expected_cont_norm, places=10)

if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)