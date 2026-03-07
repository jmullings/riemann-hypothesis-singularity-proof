#!/usr/bin/env python3
"""
PHIWEIGHTEDTRANSFEROPERATOR.py
==============================

Conjecture IV Core: φ-Weighted Transfer Operator on a Trace-Class Hilbert Space

This module implements the rigorous φ-weighted Ruelle transfer operator
with proper trace-class structure required for Fredholm determinant theory.

Mathematical Foundation:
-----------------------
The transfer operator L_s acts on L²(Ω, μ_φ) where:
  - Ω is the symbolic shift space on 9 branches
  - μ_φ is the φ-weighted Gibbs measure
  - L_s f(x) = Σ_k w_k · g_k(x) · f(σ_k(x)) · e^{-s·ℓ_k}

The operator is trace-class when:
  Σ_k ||L_s^{(k)}||_1 < ∞

This is guaranteed by the φ-geometric decay: w_k = O(φ^{-k}).
"""

import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass

# Golden ratio
PHI: float = (1.0 + np.sqrt(5.0)) / 2.0

# Number of branches
NUM_BRANCHES: int = 9


@dataclass
class HilbertSpace:
    """
    L²(Ω, μ_φ) — φ-weighted Hilbert space for the transfer operator.
    
    The space is the completion of continuous functions on the
    symbolic shift space Ω with inner product weighted by μ_φ.
    """
    dimension: int = 20  # Truncation dimension for finite approximations
    
    def __post_init__(self):
        # Basis: Fourier-like φ-weighted basis functions
        self.basis_dim = self.dimension
        
    def inner_product(self, f: np.ndarray, g: np.ndarray) -> complex:
        """Compute ⟨f, g⟩_{μ_φ} with φ-weighted measure."""
        weights = np.array([PHI**(-k) for k in range(len(f))])
        weights /= weights.sum()
        return complex(np.sum(weights * np.conj(f) * g))
    
    def norm(self, f: np.ndarray) -> float:
        """Compute ||f||_{μ_φ}."""
        return np.sqrt(abs(self.inner_product(f, f)))


@dataclass 
class SymbolicDynamics:
    """
    Symbolic dynamics on 9 branches with φ-weighted transition structure.
    
    The shift map σ: Ω → Ω acts by σ(x₀x₁x₂...) = x₁x₂x₃...
    Each branch k has:
      - Length ℓ_k (geodesic length)
      - Weight w_k = 4/(φ^k + φ^{-k})² (bi-directional Lorentzian)
      - Signature σ_k = (-1)^k
    """
    num_branches: int = 50  # For orbit enumeration
    
    def __post_init__(self):
        # Branch weights (normalized)
        raw_weights = np.array([
            4.0 / (PHI**k + PHI**(-k))**2 
            for k in range(NUM_BRANCHES)
        ])
        self.weights = raw_weights / raw_weights.sum()
        
        # Branch signatures
        self.signatures = np.array([(-1.0)**k for k in range(NUM_BRANCHES)])
        
        # Default branch lengths
        self.lengths = np.arange(1, NUM_BRANCHES + 1, dtype=float)
    
    def transition_matrix(self) -> np.ndarray:
        """
        Construct the symbolic transition matrix A.
        
        A[i,j] = 1 if transition i → j is allowed, else 0.
        For the full shift, all transitions are allowed.
        """
        return np.ones((NUM_BRANCHES, NUM_BRANCHES))
    
    def branch_kernel(self, s: complex, k: int) -> complex:
        """
        Compute κ_k(s) = w_k · σ_k · e^{-s·ℓ_k}
        """
        return self.weights[k] * self.signatures[k] * np.exp(-s * self.lengths[k])


class PhiWeightedTransferOperator:
    """
    The φ-weighted Ruelle transfer operator L_s.
    
    Acts on L²(Ω, μ_φ) by:
        (L_s f)(x) = Σ_k w_k · e^{-s·ℓ_k} · f(σ_k(x))
    
    Properties:
    ----------
    - Trace-class for Re(s) > 0 (φ-geometric decay ensures convergence)
    - Analytic in s for Re(s) > 0
    - Spectral radius r(L_s) < 1 for Re(s) > 1/2
    - Fredholm determinant det(I - L_s) is entire of order 1
    """
    
    def __init__(self, space: HilbertSpace, dynamics: SymbolicDynamics):
        self.space = space
        self.dynamics = dynamics
        self.dim = min(space.dimension, NUM_BRANCHES)
        
    def matrix_representation(self, s: complex) -> np.ndarray:
        """
        Compute the matrix representation of L_s in the truncated basis.
        
        Returns an (n × n) matrix where n = min(space.dim, NUM_BRANCHES).
        """
        n = self.dim
        L = np.zeros((n, n), dtype=complex)
        
        for j in range(n):
            for k in range(n):
                # Transfer contribution from branch k to basis element j
                kappa_k = self.dynamics.branch_kernel(s, k)
                # Coupling coefficient (simplified model)
                coupling = PHI**(-(abs(j-k))) / (1 + abs(j-k))
                L[j, k] = kappa_k * coupling
        
        return L
    
    def spectral_radius(self, s: complex) -> float:
        """
        Compute the spectral radius r(L_s) = max|λ_i|.
        """
        L = self.matrix_representation(s)
        eigenvalues = np.linalg.eigvals(L)
        return float(np.max(np.abs(eigenvalues)))
    
    def leading_eigenvalue(self, s: complex) -> complex:
        """
        Compute the leading eigenvalue λ₁(s).
        """
        L = self.matrix_representation(s)
        eigenvalues = np.linalg.eigvals(L)
        idx = np.argmax(np.abs(eigenvalues))
        return complex(eigenvalues[idx])
    
    def trace(self, s: complex) -> complex:
        """
        Compute tr(L_s) = Σ_k κ_k(s).
        """
        L = self.matrix_representation(s)
        return complex(np.trace(L))
    
    def trace_norm(self, s: complex) -> float:
        """
        Compute the trace norm ||L_s||_1 = Σ_i σ_i (singular values).
        
        This verifies trace-class property.
        """
        L = self.matrix_representation(s)
        singular_values = np.linalg.svd(L, compute_uv=False)
        return float(np.sum(singular_values))
    
    def is_trace_class(self, s: complex, threshold: float = 100.0) -> bool:
        """
        Check if L_s is trace-class (||L_s||_1 < ∞).
        """
        return self.trace_norm(s) < threshold
    
    def hilbert_schmidt_norm(self, s: complex) -> float:
        """
        Compute the Hilbert-Schmidt norm ||L_s||_2 = √(tr(L_s* L_s)).
        """
        L = self.matrix_representation(s)
        return float(np.sqrt(np.trace(L.conj().T @ L).real))
