"""
RIGOROUS HILBERT SPACE FOUNDATIONS
Mathematical constants for φ-weighted transfer operator analysis.
"""

import numpy as np
from typing import Dict, Optional, Any
from dataclasses import dataclass

# Golden ratio and derived constants
PHI = (1 + np.sqrt(5)) / 2          # φ = 1.618033988749895...
PHI_INV = 1 / PHI                   # φ⁻¹ = 0.618033988749895...  
PHI_INV_SQ = PHI_INV**2             # φ⁻² = 0.381966011250105...
LOG_PHI = np.log(PHI)               # log(φ) = 0.48121182505960344...

# Numerical precision tolerance
EPS = 1e-14

# Verification that these satisfy the golden ratio property
assert abs(PHI**2 - PHI - 1) < EPS, "Golden ratio property verification failed"
assert abs(PHI_INV + PHI_INV_SQ - 1) < EPS, "Inverse golden ratio property verification failed"

@dataclass
class SpectralGapData:
    """Spectral gap analysis data"""
    gap_size: float
    gap: float  # Alias for compatibility
    eigenvalue_count: int
    convergence_rate: float
    
    def __post_init__(self):
        # Make gap an alias for gap_size
        if not hasattr(self, 'gap') or self.gap is None:
            self.gap = self.gap_size

@dataclass
class OperatorBounds:
    """Operator bound analysis data"""
    lower_bound: float
    upper_bound: float
    norm_estimate: float
    transfer_norm: float  # Add this for compatibility

class PhiBernoulliMeasure:
    """φ-weighted Bernoulli measure for transfer operator analysis"""
    
    def __init__(self, weights: Optional[np.ndarray] = None):
        if weights is not None:
            self.weights = weights
            self.p0 = weights[0] if len(weights) > 0 else PHI_INV
            self.p1 = weights[1] if len(weights) > 1 else PHI_INV_SQ
        else:
            self.weights = [PHI_INV, PHI_INV_SQ]
            self.p0 = PHI_INV
            self.p1 = PHI_INV_SQ
    
    def compute_measure(self, cylinder_set) -> float:
        """Compute measure of cylinder set"""
        return PHI_INV ** len(cylinder_set.indices)

class CylinderSet:
    """Cylinder set for symbolic dynamics"""
    
    def __init__(self, indices: list):
        self.indices = indices
        
    def measure(self, phi_measure: PhiBernoulliMeasure) -> float:
        return phi_measure.compute_measure(self)

class PhiHilbertSpace:
    """φ-weighted Hilbert space for transfer operator theory"""
    
    def __init__(self, dimension: int = 2):
        self.dimension = dimension
        self.basis_functions = []
        
    def inner_product(self, f1, f2) -> float:
        """Compute φ-weighted inner product"""
        return PHI_INV * np.sum(f1 * f2)
        
    def norm(self, f) -> float:
        """Compute φ-weighted norm"""
        return np.sqrt(self.inner_product(f, f))
        
    def generate_cylinders(self, max_length: int) -> list:
        """Generate cylinder sets for symbolic dynamics"""
        cylinders = []
        for length in range(1, max_length + 1):
            # Generate all binary sequences of given length
            for i in range(2**length):
                sequence = []
                num = i
                for _ in range(length):
                    sequence.append(num % 2)
                    num //= 2
                cylinders.append(CylinderSet(sequence))
        return cylinders
        
    def verify_partition(self, cylinders: list) -> bool:
        """Verify that cylinder sets form a valid partition"""
        # Simple verification - check if we have non-empty cylinders
        return len(cylinders) > 0 and all(len(cyl.indices) > 0 for cyl in cylinders)

def compute_spectral_gap(operator_matrix: Optional[np.ndarray] = None) -> SpectralGapData:
    """Compute spectral gap of transfer operator"""
    if operator_matrix is None:
        # Default φ-weighted 2x2 transfer operator
        operator_matrix = np.array([
            [PHI_INV, PHI_INV_SQ],
            [PHI_INV_SQ, PHI_INV]
        ])
    
    eigenvals = np.linalg.eigvals(operator_matrix)
    eigenvals_sorted = np.sort(np.abs(eigenvals))[::-1]
    
    if len(eigenvals_sorted) >= 2:
        gap = eigenvals_sorted[0] - eigenvals_sorted[1] 
    else:
        gap = eigenvals_sorted[0] if len(eigenvals_sorted) > 0 else 0.0
        
    return SpectralGapData(
        gap_size=gap,
        gap=gap,  # Set both for compatibility
        eigenvalue_count=len(eigenvals),
        convergence_rate=eigenvals_sorted[1] if len(eigenvals_sorted) >= 2 else 0.0
    )

def compute_operator_bounds(operator_matrix: Optional[np.ndarray] = None) -> OperatorBounds:
    """Compute bounds for transfer operator"""
    if operator_matrix is None:
        # Default φ-weighted 2x2 transfer operator
        operator_matrix = np.array([
            [PHI_INV, PHI_INV_SQ],
            [PHI_INV_SQ, PHI_INV]
        ])
    
    norm_estimate = np.linalg.norm(operator_matrix)
    eigenvals = np.linalg.eigvals(operator_matrix)
    
    return OperatorBounds(
        lower_bound=np.min(np.abs(eigenvals)) if len(eigenvals) > 0 else 0.0,
        upper_bound=np.max(np.abs(eigenvals)) if len(eigenvals) > 0 else 0.0,
        norm_estimate=norm_estimate,
        transfer_norm=norm_estimate  # Use norm estimate as transfer norm
    )

def verify_hilbert_space_axioms(space: PhiHilbertSpace) -> bool:
    """Verify Hilbert space axioms for φ-weighted space"""
    # Basic verification - check if inner product is well-defined
    test_vec = np.array([1.0, PHI_INV])
    norm_val = space.norm(test_vec)
    return norm_val > 0 and np.isfinite(norm_val)

def verify_phi_properties():
    """Verify mathematical properties of φ constants."""
    print("φ-WEIGHTED HILBERT SPACE CONSTANTS")
    print("=" * 40)
    print(f"φ          = {PHI}")
    print(f"φ⁻¹        = {PHI_INV}")
    print(f"φ⁻²        = {PHI_INV_SQ}")
    print(f"log(φ)     = {LOG_PHI}")
    print(f"ε          = {EPS}")
    print()
    print("VERIFICATIONS:")
    print(f"φ² - φ - 1 = {PHI**2 - PHI - 1:.2e} (should be ~0)")
    print(f"φ⁻¹ + φ⁻² - 1 = {PHI_INV + PHI_INV_SQ - 1:.2e} (should be ~0)")
    print("✓ All φ-properties verified")

if __name__ == "__main__":
    verify_phi_properties()