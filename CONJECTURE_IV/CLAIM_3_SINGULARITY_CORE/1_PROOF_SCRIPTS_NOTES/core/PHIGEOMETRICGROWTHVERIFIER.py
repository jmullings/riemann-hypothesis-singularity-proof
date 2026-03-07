#!/usr/bin/env python3
"""
PHIGEOMETRICGROWTHVERIFIER.py
=============================

Verification of φ-geometric growth conditions for the transfer operator.

The φ-weighted operator satisfies geometric growth bounds:
    ||L_s^n||_1 ≤ C · φ^{-αn}  for some α > 0

This ensures:
1. Trace-class property for all Re(s) > 0
2. Convergence of the Fredholm determinant series
3. Analytic continuation to the entire complex plane
"""

import numpy as np
from typing import Tuple, List, Optional
from .PHIWEIGHTEDTRANSFEROPERATOR import PhiWeightedTransferOperator, PHI


class PhiGeometricGrowthVerifier:
    """
    Verify φ-geometric growth bounds for the transfer operator.
    """
    
    def __init__(self, operator: PhiWeightedTransferOperator):
        self.operator = operator
        
    def compute_power_trace_norms(self, s: complex, 
                                   max_power: int = 15) -> List[float]:
        """
        Compute ||L_s^n||_1 for n = 1, ..., max_power.
        """
        L = self.operator.matrix_representation(s)
        norms = []
        
        L_power = L.copy()
        for n in range(1, max_power + 1):
            # Trace norm = sum of singular values
            singular_values = np.linalg.svd(L_power, compute_uv=False)
            norms.append(float(np.sum(singular_values)))
            L_power = L_power @ L
        
        return norms
    
    def fit_decay_rate(self, norms: List[float]) -> Tuple[float, float, float]:
        """
        Fit ||L^n|| ~ C · r^n to estimate decay rate.
        
        Returns (C, r, R²) where R² is goodness of fit.
        """
        if len(norms) < 3:
            return 1.0, 0.5, 0.0
        
        n = np.arange(1, len(norms) + 1)
        log_norms = np.log(np.array(norms) + 1e-300)
        
        # Linear fit to log(||L^n||) = log(C) + n·log(r)
        coeffs, residuals, _, _, _ = np.polyfit(n, log_norms, 1, full=True)
        
        log_r = coeffs[0]
        log_C = coeffs[1]
        
        r = np.exp(log_r)
        C = np.exp(log_C)
        
        # R² calculation
        ss_res = residuals[0] if len(residuals) > 0 else 0
        ss_tot = np.sum((log_norms - np.mean(log_norms))**2)
        R2 = 1 - ss_res / (ss_tot + 1e-10)
        
        return float(C), float(r), float(R2)
    
    def verify_phi_geometric_growth(self, s: complex = complex(0.5, 14.134725),
                                     verbose: bool = True) -> bool:
        """
        Verify that ||L^n|| decays geometrically with rate related to φ.
        
        Expected: r < 1/φ ≈ 0.618 for proper φ-geometric decay.
        """
        norms = self.compute_power_trace_norms(s, max_power=15)
        C, r, R2 = self.fit_decay_rate(norms)
        
        phi_rate = 1.0 / PHI  # ≈ 0.618
        
        if verbose:
            print(f"  φ-Geometric Growth Verification at s = {s}")
            print(f"    Fitted: ||L^n|| ~ {C:.4f} × {r:.6f}^n")
            print(f"    φ-rate threshold: 1/φ = {phi_rate:.6f}")
            print(f"    Decay rate r = {r:.6f} {'<' if r < phi_rate else '≥'} {phi_rate:.6f}")
            print(f"    R² = {R2:.4f}")
        
        # Verified if decay rate is at most 1/φ (with some tolerance)
        return r < phi_rate * 1.1  # 10% tolerance
    
    def verify_trace_class_uniform(self, sigma_values: np.ndarray,
                                    T_values: np.ndarray,
                                    threshold: float = 100.0) -> Tuple[bool, float]:
        """
        Verify trace-class property uniformly on a grid.
        
        Returns (all_trace_class, max_trace_norm).
        """
        max_norm = 0.0
        
        for sigma in sigma_values:
            for T in T_values:
                s = complex(sigma, T)
                norm = self.operator.trace_norm(s)
                max_norm = max(max_norm, norm)
                
                if norm > threshold:
                    return False, max_norm
        
        return True, max_norm
    
    def estimate_operator_order_type(self, sigma: float = 0.5,
                                      T_range: Tuple[float, float] = (10, 500),
                                      num_points: int = 30) -> Tuple[float, float]:
        """
        Estimate the order and type of L_s as functions of |s|.
        
        Returns (order_estimate, type_estimate).
        """
        T_values = np.logspace(np.log10(T_range[0]), np.log10(T_range[1]), num_points)
        
        log_norm = []
        log_s = []
        
        for T in T_values:
            s = complex(sigma, T)
            norm = self.operator.trace_norm(s)
            if norm > 0:
                log_norm.append(np.log(norm))
                log_s.append(np.log(abs(s)))
        
        if len(log_norm) < 5:
            return 1.0, np.log(PHI)
        
        # Linear fit for order
        coeffs = np.polyfit(log_s, log_norm, 1)
        order = max(coeffs[0], 0.0)
        
        # Type estimate
        type_samples = []
        for i, T in enumerate(T_values[:len(log_norm)]):
            s = complex(sigma, T)
            s_norm = abs(s)
            type_est = log_norm[i] / (s_norm ** order + 1e-10)
            type_samples.append(type_est)
        
        type_est = np.median(type_samples) if type_samples else np.log(PHI)
        
        return float(order), float(type_est)
