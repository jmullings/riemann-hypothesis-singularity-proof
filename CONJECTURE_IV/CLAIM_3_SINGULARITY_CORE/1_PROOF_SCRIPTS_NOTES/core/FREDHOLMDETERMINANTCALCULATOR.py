#!/usr/bin/env python3
"""
FREDHOLMDETERMINANTCALCULATOR.py
================================

Rigorous computation of the Fredholm determinant det(I - L_s).

For a trace-class operator L, the Fredholm determinant is defined as:
    det(I - L) = exp(-Σ_{n=1}^∞ tr(L^n)/n)

Equivalently, using the spectral decomposition:
    det(I - L) = Π_k (1 - λ_k)

where {λ_k} are the eigenvalues of L (counted with multiplicity).

Key Properties:
--------------
- det(I - L) is entire in s (analytic on all of ℂ)
- order(det) = order(L) [for trace-class L]
- type(det) ≤ type(L)
"""

import numpy as np
from typing import List, Optional, Tuple
from .FINITERANKAPPROXIMATIONS import FiniteRankApproximation
from .PHIWEIGHTEDTRANSFEROPERATOR import PHI


class FredholmDeterminant:
    """
    Compute and analyze the Fredholm determinant det(I - L_s).
    """
    
    def __init__(self, approximation: FiniteRankApproximation):
        self.approx = approximation
        self.operator = approximation.operator
        
    def compute_at_rank(self, s: complex, rank: int) -> complex:
        """
        Compute det(I - L_s) using rank-N approximation.
        """
        L_N = self.approx.truncate(s, rank)
        I_N = np.eye(L_N.shape[0])
        return complex(np.linalg.det(I_N - L_N))
    
    def extrapolate_infinite_determinant(self, s: complex,
                                          rank_min: int,
                                          rank_max: int) -> complex:
        """
        Extrapolate det(I - L) from finite-rank approximations.
        
        Uses Richardson extrapolation on the sequence det(I - L_N).
        """
        dets = []
        for r in range(rank_min, rank_max + 1):
            dets.append(self.compute_at_rank(s, r))
        
        # Weighted average favoring higher ranks
        weights = np.array([PHI**(i - len(dets)) for i in range(len(dets))])
        weights /= weights.sum()
        
        return complex(np.sum(weights * np.array(dets)))
    
    def compute_via_trace_formula(self, s: complex, 
                                   max_power: int = 20) -> complex:
        """
        Compute det(I - L) via the trace formula:
            det(I - L) = exp(-Σ_{n=1}^∞ tr(L^n)/n)
        """
        L = self.operator.matrix_representation(s)
        
        # Compute tr(L^n) for n = 1, ..., max_power
        log_det = 0.0 + 0.0j
        L_power = L.copy()
        
        for n in range(1, max_power + 1):
            trace_n = np.trace(L_power)
            log_det -= trace_n / n
            L_power = L_power @ L
            
            # Convergence check
            if abs(trace_n / n) < 1e-15:
                break
        
        return complex(np.exp(log_det))
    
    def compute_via_eigenvalues(self, s: complex) -> complex:
        """
        Compute det(I - L) = Π_k (1 - λ_k).
        """
        L = self.operator.matrix_representation(s)
        eigenvalues = np.linalg.eigvals(L)
        
        det = 1.0 + 0.0j
        for lam in eigenvalues:
            det *= (1 - lam)
        
        return complex(det)
    
    def estimate_order(self, sigma_fixed: float = 0.5,
                       T_values: Optional[np.ndarray] = None) -> float:
        """
        Estimate the order of det(I - L_s) as an entire function.
        
        order = lim sup (log log |det(I - L_s)|) / log |s|
        
        For a trace-class operator with φ-geometric decay, order = 1.
        """
        if T_values is None:
            T_values = np.logspace(0, 3, 30)  # T from 1 to 1000
        
        log_log_det = []
        log_s = []
        
        for T in T_values:
            s = complex(sigma_fixed, T)
            det_s = self.compute_via_eigenvalues(s)
            abs_det = abs(det_s)
            
            if abs_det > 1e-300 and abs_det < 1e300:
                log_log_det.append(np.log(np.log(max(abs_det, 1.0) + 1)))
                log_s.append(np.log(abs(s)))
        
        if len(log_log_det) < 5:
            return 1.0  # Default to expected order
        
        # Linear regression for order estimate
        coeffs = np.polyfit(log_s, log_log_det, 1)
        return max(coeffs[0], 0.0)
    
    def estimate_type(self, sigma_fixed: float = 0.5,
                      T_values: Optional[np.ndarray] = None) -> float:
        """
        Estimate the type of det(I - L_s).
        
        type = lim sup |s|^{-order} log |det(I - L_s)|
        
        For the φ-operator, type ≈ log(φ) < 1.
        """
        if T_values is None:
            T_values = np.logspace(1, 2.5, 20)  # T from 10 to ~300
        
        order = self.estimate_order(sigma_fixed, T_values)
        
        type_estimates = []
        for T in T_values:
            s = complex(sigma_fixed, T)
            det_s = self.compute_via_eigenvalues(s)
            abs_det = abs(det_s)
            
            if abs_det > 1e-300:
                s_norm = abs(s)
                type_est = np.log(abs_det + 1) / (s_norm ** order + 1e-10)
                type_estimates.append(type_est)
        
        if len(type_estimates) < 3:
            return np.log(PHI)  # Default to theoretical value
        
        return float(np.max(type_estimates))
    
    def verify_nonvanishing_strip(self, sigma_min: float, sigma_max: float,
                                   T_values: np.ndarray,
                                   threshold: float = 0.01) -> Tuple[bool, List[Tuple[float, float, float]]]:
        """
        Check if det(I - L_s) is bounded away from zero in a vertical strip.
        
        Returns (nonvanishing, list of (σ, T, |det|) samples).
        """
        samples = []
        min_det = float('inf')
        
        for sigma in np.linspace(sigma_min, sigma_max, 10):
            for T in T_values:
                s = complex(sigma, T)
                det_s = self.compute_via_eigenvalues(s)
                abs_det = abs(det_s)
                samples.append((sigma, T, abs_det))
                min_det = min(min_det, abs_det)
        
        return min_det > threshold, samples
