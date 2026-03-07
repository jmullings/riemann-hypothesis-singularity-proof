#!/usr/bin/env python3
"""
FINITERANKAPPROXIMATIONS.py
===========================

Finite-rank approximations of the φ-weighted transfer operator.

For a trace-class operator L, we approximate by finite-rank operators L_N
such that ||L - L_N||_1 → 0 as N → ∞.

The key property is:
    det(I - L_N) → det(I - L) uniformly on compacts.
"""

import numpy as np
from typing import List, Tuple
from .PHIWEIGHTEDTRANSFEROPERATOR import PhiWeightedTransferOperator, PHI


class FiniteRankApproximation:
    """
    Finite-rank approximation scheme for the transfer operator.
    
    Uses truncation to the first N singular values/vectors.
    """
    
    def __init__(self, operator: PhiWeightedTransferOperator):
        self.operator = operator
        
    def truncate(self, s: complex, rank: int) -> np.ndarray:
        """
        Compute rank-N truncation of L_s.
        
        Uses SVD: L = U Σ V* → L_N = U_N Σ_N V_N*
        """
        L = self.operator.matrix_representation(s)
        
        # SVD
        U, sigma, Vh = np.linalg.svd(L, full_matrices=False)
        
        # Truncate to rank
        r = min(rank, len(sigma))
        U_r = U[:, :r]
        sigma_r = sigma[:r]
        Vh_r = Vh[:r, :]
        
        # Reconstruct
        L_N = U_r @ np.diag(sigma_r) @ Vh_r
        return L_N
    
    def approximation_error(self, s: complex, rank: int) -> float:
        """
        Compute ||L - L_N||_1 (trace norm of the tail).
        """
        L = self.operator.matrix_representation(s)
        L_N = self.truncate(s, rank)
        
        diff = L - L_N
        singular_values = np.linalg.svd(diff, compute_uv=False)
        return float(np.sum(singular_values))
    
    def extrapolate_eigenvalue(self, s: complex, 
                                ranks: List[int]) -> complex:
        """
        Richardson extrapolation of the leading eigenvalue.
        
        Uses sequence of approximations at different ranks to
        estimate the infinite-dimensional limit.
        """
        eigenvalues = []
        for r in ranks:
            L_r = self.truncate(s, r)
            evs = np.linalg.eigvals(L_r)
            idx = np.argmax(np.abs(evs))
            eigenvalues.append(evs[idx])
        
        # Simple averaging (could use Aitken Δ² for better convergence)
        return complex(np.mean(eigenvalues))
    
    def determinant_sequence(self, s: complex, 
                             max_rank: int) -> List[complex]:
        """
        Compute det(I - L_N) for N = 1, 2, ..., max_rank.
        
        The sequence should converge to det(I - L).
        """
        dets = []
        for r in range(1, max_rank + 1):
            L_r = self.truncate(s, r)
            I_r = np.eye(L_r.shape[0])
            det_r = np.linalg.det(I_r - L_r)
            dets.append(complex(det_r))
        return dets
    
    def verify_convergence(self, s: complex, 
                           ranks: List[int],
                           tol: float = 0.01) -> Tuple[bool, float]:
        """
        Verify that det(I - L_N) converges as N → ∞.
        
        Returns (converged, final_variation).
        """
        dets = []
        for r in ranks:
            L_r = self.truncate(s, r)
            I_r = np.eye(L_r.shape[0])
            dets.append(np.linalg.det(I_r - L_r))
        
        # Check variation in last few values
        if len(dets) < 3:
            return False, 1.0
        
        recent = np.abs(dets[-3:])
        variation = np.std(recent) / (np.mean(recent) + 1e-10)
        
        return variation < tol, float(variation)
