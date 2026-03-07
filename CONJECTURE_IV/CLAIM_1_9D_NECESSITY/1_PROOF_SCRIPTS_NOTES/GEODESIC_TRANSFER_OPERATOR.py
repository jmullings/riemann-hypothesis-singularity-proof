"""
GEODESIC TRANSFER OPERATOR
==========================

φ-weighted transfer operator on geodesic space for Conjecture IV.

This module implements the 9D φ-weighted transfer operator L_s that acts
on functions over a geodesic phase space. The operator is defined via:

    (L_s f)(x) = Σ_k w_k(φ) · σ_k · e^{-s·ℓ_k} · f(g_k^{-1}(x))

where:
    - w_k(φ) = φ-dependent weights (golden ratio balanced)
    - σ_k = signature factors for orientation  
    - ℓ_k = geodesic lengths (hyperbolic, computed from prime orbits)
    - g_k = geodesic shift maps on phase space

Date: March 2026
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
import math


# =============================================================================
# CONSTANTS (LOG-FREE, PRECOMPUTED)
# =============================================================================

PHI: float = (1.0 + math.sqrt(5.0)) / 2.0  # Golden ratio ≈ 1.618033988749895
PHI_INV: float = PHI - 1.0                  # 1/φ = φ - 1 ≈ 0.618033988749895
LOG_PHI: float = 0.4812118250596034         # ln(φ), precomputed

# Operator type constants for Hadamard analysis
TYPE_XI: float = 1.0         # ξ(s) has order 1, type O(|s|·log|s|)
TYPE_PHI_OPERATOR: float = 0.5  # φ-operator has smaller type (the obstruction)


# =============================================================================
# PRECOMPUTED LOG TABLE (AVOID LOG CALLS)
# =============================================================================

_LOG_TABLE_SIZE = 100000
_LOG_TABLE: np.ndarray = np.log(np.arange(1, _LOG_TABLE_SIZE + 1, dtype=np.float64))


def precomputed_log(n: int) -> float:
    """
    Return ln(n) using precomputed table for small n, direct for large n.
    """
    if n <= 0:
        return float('-inf')
    if n <= _LOG_TABLE_SIZE:
        return _LOG_TABLE[n - 1]
    return math.log(n)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class OperatorBoundData:
    """Data capturing operator norm bounds and growth estimates."""
    trace_bound: float
    spectral_radius_bound: float
    growth_type: float  # Hadamard growth type
    growth_order: float  # Hadamard order
    is_finite_rank: bool = False
    
    
@dataclass
class SpectralData:
    """Spectral decomposition data for the transfer operator."""
    eigenvalues: np.ndarray
    spectral_radius: float
    trace: complex
    determinant: complex
    

# =============================================================================
# HILBERT SPACE (MINIMAL STUB)
# =============================================================================

class L2GeodesicSpace:
    """
    L²(Ω, μ_φ) - Hilbert space of square-integrable functions
    on geodesic phase space with φ-weighted measure.
    """
    
    def __init__(self, dimension: int = 100):
        self.dimension = dimension
        
    def inner_product(self, f: np.ndarray, g: np.ndarray) -> complex:
        """Compute ⟨f, g⟩ = ∫ f*(x) g(x) dμ_φ(x)."""
        return np.vdot(f, g)
    
    def norm(self, f: np.ndarray) -> float:
        """Compute ||f|| = sqrt(⟨f, f⟩)."""
        return np.sqrt(np.real(self.inner_product(f, f)))


# =============================================================================
# GEODESIC DATA
# =============================================================================

@dataclass
class GeodesicData:
    """Data for a single primitive geodesic."""
    index: int
    length: float           # ℓ_k (hyperbolic length)
    weight: float           # w_k (φ-balanced weight)
    signature: int          # σ_k ∈ {-1, +1}
    curvature_9d: np.ndarray  # 9D curvature invariants


def generate_geodesic_data(
    num_geodesics: int,
    genus: int = 2
) -> List[GeodesicData]:
    """
    Generate geodesic data for a genus-g surface.
    
    Uses prime orbit theorem asymptotics:
        N(L) ~ e^L / L  as L → ∞
        
    Lengths are derived from:
        ℓ_k = ln(p_k) where p_k is the k-th prime
    """
    geodesics = []
    
    # Generate first num_geodesics primes for length data
    primes = _sieve_primes(num_geodesics * 10)[:num_geodesics]
    
    for k, p in enumerate(primes):
        # Length from prime
        length = precomputed_log(p)
        
        # φ-balanced weight: w_k = φ^{-k/N} * (1 + 1/(k+1))
        weight = PHI_INV ** (k / num_geodesics) * (1.0 + 1.0 / (k + 1))
        
        # Alternating signature
        signature = 1 if k % 2 == 0 else -1
        
        # 9D curvature: synthetic based on length and index
        curvature = _compute_9d_curvature(k, length, genus)
        
        geodesics.append(GeodesicData(
            index=k,
            length=length,
            weight=weight,
            signature=signature,
            curvature_9d=curvature
        ))
    
    return geodesics


def _sieve_primes(limit: int) -> List[int]:
    """Sieve of Eratosthenes for primes up to limit."""
    if limit < 2:
        return []
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    return [i for i, is_prime in enumerate(sieve) if is_prime]


def _compute_9d_curvature(k: int, length: float, genus: int) -> np.ndarray:
    """
    Compute 9D curvature invariants for geodesic k.
    
    The 9 components represent:
        [0-2]: Sectional curvatures (3 independent)
        [3-5]: Ricci curvature components (3)
        [6]:   Scalar curvature
        [7]:   φ-torsion
        [8]:   Geodesic deviation
    """
    curvature = np.zeros(9)
    
    # Sectional curvatures (negative, hyperbolic)
    base_curvature = -1.0 / (1.0 + length)
    curvature[0] = base_curvature * (1.0 + 0.1 * np.sin(k * PHI))
    curvature[1] = base_curvature * (1.0 + 0.1 * np.cos(k * PHI))
    curvature[2] = base_curvature * (1.0 + 0.1 * np.sin(k * PHI + 1))
    
    # Ricci components
    ricci_scale = -2.0 * (genus - 1) / (1.0 + length**2)
    curvature[3] = ricci_scale * (1.0 + 0.05 * k / (k + 1))
    curvature[4] = ricci_scale * (1.0 - 0.05 * k / (k + 1))
    curvature[5] = ricci_scale
    
    # Scalar curvature
    curvature[6] = sum(curvature[3:6])
    
    # φ-torsion (modulated by golden ratio)
    curvature[7] = PHI_INV ** (k + 1) * np.sin(length * PHI)
    
    # Geodesic deviation
    curvature[8] = np.exp(-length * PHI_INV) * (1.0 + 0.1 * np.cos(k))
    
    return curvature


# =============================================================================
# GEODESIC TRANSFER OPERATOR
# =============================================================================

class GeodesicTransferOperator:
    """
    The φ-weighted transfer operator L_s on geodesic phase space.
    
    ACTION:
        (L_s f)(x) = Σ_k w_k · σ_k · e^{-s·ℓ_k} · f(T_k^{-1}(x))
    
    SPECTRAL PROPERTIES:
        - Trace: Tr(L_s) = Σ_k w_k · σ_k · e^{-s·ℓ_k}
        - Spectral radius: ρ(L_s) ≤ Σ_k |w_k| · e^{-Re(s)·ℓ_k}
        
    PARAMETERS:
        genus: Genus of the underlying surface
        geodesics: List of geodesic data
        H: The Hilbert space L²(Ω, μ_φ)
    """
    
    def __init__(
        self,
        genus: int = 2,
        num_geodesics: int = 100
    ):
        self.genus = genus
        self.geodesics = generate_geodesic_data(num_geodesics, genus)
        self.H = L2GeodesicSpace(dimension=num_geodesics)
        
    @property
    def num_branches(self) -> int:
        return len(self.geodesics)
    
    def branch_kernel(self, k: int, s: complex) -> complex:
        """
        Compute the k-th branch kernel κ_k(s) = w_k · σ_k · e^{-s·ℓ_k}.
        """
        if k >= len(self.geodesics):
            return 0.0j
        
        g = self.geodesics[k]
        # κ_k(s) = w_k · σ_k · exp(-s · ℓ_k)
        return g.weight * g.signature * np.exp(-s * g.length)
    
    def compute_trace(self, s: complex, max_branches: Optional[int] = None) -> complex:
        """
        Compute Tr(L_s) = Σ_k κ_k(s).
        """
        n = min(max_branches, self.num_branches) if max_branches else self.num_branches
        return sum(self.branch_kernel(k, s) for k in range(n))
    
    def compute_trace_powers(
        self,
        s: complex,
        max_power: int,
        max_branches: Optional[int] = None
    ) -> List[complex]:
        """
        Compute traces Tr(L_s^n) for n = 1, 2, ..., max_power.
        
        Uses the formula for trace of powers via primitive geodesic sums.
        For simplicity, we use the approximation:
            Tr(L_s^n) ≈ Σ_k κ_k(s)^n · (weight corrections)
        """
        n_branches = min(max_branches, self.num_branches) if max_branches else self.num_branches
        traces = []
        
        for n in range(1, max_power + 1):
            trace_n = 0.0j
            for k in range(n_branches):
                kappa = self.branch_kernel(k, s)
                # Contribution from n-fold covering
                trace_n += kappa ** n * PHI_INV ** (n - 1)
            traces.append(trace_n)
        
        return traces
    
    def apply_truncated(
        self,
        f: np.ndarray,
        s: complex,
        max_branches: Optional[int] = None
    ) -> np.ndarray:
        """
        Apply L_s to function f using truncated branch sum.
        
        Returns (L_s f) approximated in finite dimension.
        """
        n = min(max_branches, self.num_branches) if max_branches else self.num_branches
        dim = len(f)
        
        result = np.zeros(dim, dtype=complex)
        
        for k in range(min(n, dim)):
            kappa = self.branch_kernel(k, s)
            # Simplified action: diagonal in geodesic basis
            if k < dim:
                result[k] = kappa * f[k]
        
        # Add off-diagonal mixing (models geodesic flow)
        for k in range(1, min(n, dim)):
            mixing = PHI_INV ** k * 0.1
            if k < dim - 1:
                result[k] += mixing * f[k - 1] * self.branch_kernel(k, s)
                result[k - 1] += mixing * f[k] * self.branch_kernel(k - 1, s)
        
        return result
    
    def spectral_radius_bound(self, sigma: float) -> float:
        """
        Compute upper bound on spectral radius for Re(s) = σ.
        
        ρ(L_s) ≤ Σ_k |w_k| · e^{-σ·ℓ_k}
        """
        return sum(
            g.weight * np.exp(-sigma * g.length)
            for g in self.geodesics
        )
    
    def get_operator_bounds(self, s: complex) -> OperatorBoundData:
        """
        Compute operator bounds for analysis.
        """
        sigma = s.real
        trace = self.compute_trace(s)
        rho_bound = self.spectral_radius_bound(sigma)
        
        return OperatorBoundData(
            trace_bound=abs(trace),
            spectral_radius_bound=rho_bound,
            growth_type=TYPE_PHI_OPERATOR,
            growth_order=1.0,
            is_finite_rank=False
        )
    
    def get_spectral_data(
        self,
        s: complex,
        num_eigenvalues: int = 20
    ) -> SpectralData:
        """
        Compute approximate spectral data.
        
        Uses eigenvalues of truncated matrix representation.
        """
        dim = min(num_eigenvalues, self.num_branches)
        
        # Build truncated matrix
        M = np.zeros((dim, dim), dtype=complex)
        for k in range(dim):
            M[k, k] = self.branch_kernel(k, s)
            # Off-diagonal terms
            if k > 0:
                mixing = PHI_INV ** k * 0.1
                M[k, k-1] = mixing * self.branch_kernel(k, s)
                M[k-1, k] = mixing * self.branch_kernel(k-1, s)
        
        eigenvalues = np.linalg.eigvals(M)
        
        return SpectralData(
            eigenvalues=eigenvalues,
            spectral_radius=np.max(np.abs(eigenvalues)),
            trace=np.trace(M),
            determinant=np.linalg.det(M)
        )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_geodesic_operator(
    genus: int = 2,
    num_geodesics: int = 100
) -> GeodesicTransferOperator:
    """
    Factory function to create a geodesic transfer operator.
    
    Parameters
    ----------
    genus : int
        Genus of the underlying Riemann surface (default: 2)
    num_geodesics : int
        Number of geodesic branches in the operator sum (default: 100)
    
    Returns
    -------
    GeodesicTransferOperator
        Configured transfer operator
    """
    return GeodesicTransferOperator(genus=genus, num_geodesics=num_geodesics)


# =============================================================================
# TESTING
# =============================================================================

def test_operator():
    """Test the geodesic transfer operator."""
    print("=" * 60)
    print("GEODESIC TRANSFER OPERATOR TEST")
    print("=" * 60)
    
    # Create operator
    L = create_geodesic_operator(genus=2, num_geodesics=100)
    
    # Test at s = 0.5 + 14.134i (near first Riemann zero)
    s = complex(0.5, 14.134725)
    
    print(f"\nOperator parameters:")
    print(f"  Genus: {L.genus}")
    print(f"  Number of branches: {L.num_branches}")
    print(f"  Test point: s = {s}")
    
    # Compute trace
    trace = L.compute_trace(s)
    print(f"\nTrace Tr(L_s) = {trace:.6f}")
    
    # Compute first few branch kernels
    print("\nFirst 5 branch kernels:")
    for k in range(5):
        kappa = L.branch_kernel(k, s)
        print(f"  κ_{k}(s) = {kappa:.6f}")
    
    # Spectral data
    spec = L.get_spectral_data(s)
    print(f"\nSpectral radius ρ(L_s) ≈ {spec.spectral_radius:.6f}")
    
    # Bounds
    bounds = L.get_operator_bounds(s)
    print(f"Spectral radius bound: {bounds.spectral_radius_bound:.6f}")
    print(f"Growth type: {bounds.growth_type}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_operator()
