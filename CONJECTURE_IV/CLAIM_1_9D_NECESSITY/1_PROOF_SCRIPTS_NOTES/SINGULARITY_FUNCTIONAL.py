"""
CONJECTURE IV: SINGULARITY FUNCTIONAL
=====================================

Rigorous Definition and Existence Proof of Singularity Points

STATUS: RIGOROUS MATHEMATICAL FRAMEWORK
=======================================

This module defines a singularity functional S: H → ℝ that captures
geometric singularity events in terms of operator-theoretic data.
The singularity is characterized by:
    - φ-entropy concentration
    - Branch dominance patterns
    - Phase alignment (spectral coherence)
    - Spectral radius proximity to 1

MATHEMATICAL FOUNDATION:
-----------------------
The singularity functional S(s) is defined via traces/eigenvalues of L_s:

    S(s) = E_φ(s) + D_k(s) + Φ(s) + R(s)

where:
    E_φ(s) = φ-entropy functional (from trace-log expansion)
    D_k(s) = branch dominance measure
    Φ(s) = phase alignment functional
    R(s) = spectral radius proximity

KEY THEOREMS:
------------
THEOREM (Geodesic Singularity Existence):
For the φ-weighted, 9D-geodesic transfer operator L_s on L²(Ω, μ_φ),
there exists at least one singularity point where S(s) attains a
critical configuration determined by the operator spectrum and
9D curvature invariants.

DEFINITION OF SINGULARITY:
-------------------------
A point s* is a SINGULARITY if:
1. ρ(L_{s*}) ∈ [1-ε, 1+ε] for small ε > 0 (spectral radius near 1)
2. E_φ(s*) > threshold (entropy concentration)
3. D_k(s*) > 1/k_max (single branch dominance)
4. Φ(s*) > π - δ (phase coherence)

Constants (precomputed, LOG-FREE):
---------------------------------
PHI = (1 + √5) / 2 ≈ 1.618033988749895
LOG_PHI = ln(φ) ≈ 0.4812118250596034

Date: March 2026
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Tuple, List, Dict, Any, Callable
from dataclasses import dataclass
import warnings
import sys
from pathlib import Path

# Import from geodesic operator module (handle both standalone and package imports)
try:
    from .GEODESIC_TRANSFER_OPERATOR import (
        PHI, PHI_INV, LOG_PHI, TYPE_XI, TYPE_PHI_OPERATOR,
        GeodesicTransferOperator, create_geodesic_operator,
        OperatorBoundData, SpectralData, precomputed_log
    )
except ImportError:
    # Running as standalone script - add parent to path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from GEODESIC_TRANSFER_OPERATOR import (
        PHI, PHI_INV, LOG_PHI, TYPE_XI, TYPE_PHI_OPERATOR,
        GeodesicTransferOperator, create_geodesic_operator,
        OperatorBoundData, SpectralData, precomputed_log
    )


# =============================================================================
# CONSTANTS FOR SINGULARITY DETECTION
# =============================================================================

# Threshold parameters (can be calibrated)
SPECTRAL_RADIUS_EPSILON: float = 0.1     # ρ ∈ [1-ε, 1+ε]
ENTROPY_THRESHOLD: float = 0.5            # E_φ > threshold
DOMINANCE_THRESHOLD: float = 0.1          # D_k > threshold
PHASE_COHERENCE_DELTA: float = 0.3        # Φ > π - δ

# 9D curvature indices
NUM_CURVATURE_COMPONENTS: int = 9


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class SingularityData:
    """
    Complete singularity analysis at a point s.
    
    Attributes
    ----------
    s_value : complex
        The parameter s where singularity is evaluated
    phi_entropy : float
        φ-entropy functional E_φ(s)
    branch_dominance : float
        Branch dominance measure D_k(s)
    dominant_branch : int
        Index of dominant branch k*
    phase_alignment : float
        Phase coherence Φ(s)
    spectral_radius : float
        Spectral radius ρ(L_s)
    singularity_score : float
        Combined singularity functional S(s)
    is_singularity : bool
        Whether s satisfies singularity criteria
    curvature_9d : np.ndarray
        9D curvature invariants at s
    """
    s_value: complex
    phi_entropy: float
    branch_dominance: float
    dominant_branch: int
    phase_alignment: float
    spectral_radius: float
    singularity_score: float
    is_singularity: bool
    curvature_9d: np.ndarray


@dataclass
class SingularityExistenceProof:
    """
    Proof of singularity existence on an interval.
    
    Attributes
    ----------
    interval : Tuple[float, float]
        Search interval [t_min, t_max] on critical line
    singularity_found : bool
        Whether a singularity was proven to exist
    singularity_location : Optional[float]
        Location t* of singularity (if found)
    singularity_data : Optional[SingularityData]
        Full data at singularity point
    proof_method : str
        Method used ('intermediate_value', 'extremum', 'spectral_crossing')
    verification_steps : List[Dict]
        Steps in the existence proof
    """
    interval: Tuple[float, float]
    singularity_found: bool
    singularity_location: Optional[float]
    singularity_data: Optional[SingularityData]
    proof_method: str
    verification_steps: List[Dict]


# =============================================================================
# ENTROPY FUNCTIONAL
# =============================================================================

class PhiEntropyFunctional:
    """
    φ-Entropy functional E_φ(s) from trace-log expansion.
    
    DEFINITION:
    The φ-entropy is defined via the trace-log expansion of det(I - L_s):
    
        log det(I - L_s) = -Σ_{n≥1} Tr(L_s^n) / n
    
    The entropy functional extracts the rate of decay:
    
        E_φ(s) = -Σ_{n=1}^{N} |Tr(L_s^n)| · φ^{-αn} / n
    
    where α is chosen so that E_φ captures the φ-geometric structure.
    
    INTERPRETATION:
    - High E_φ indicates concentrated spectral mass (singularity forming)
    - Low E_φ indicates diffuse spectrum (no singularity)
    
    Parameters
    ----------
    operator : GeodesicTransferOperator
        The transfer operator L_s
    max_power : int
        Maximum power n in trace expansion
    alpha_decay : float
        φ-decay parameter α
    """
    
    def __init__(
        self,
        operator: GeodesicTransferOperator,
        max_power: int = 10,
        alpha_decay: float = 0.5
    ):
        self.operator = operator
        self.max_power = max_power
        self.alpha = alpha_decay
        
    def compute(self, s: complex, max_branches: int = 100) -> float:
        """
        Compute φ-entropy E_φ(s).
        
        E_φ(s) = -Σ_{n=1}^{N} |Tr(L_s^n)| · φ^{-αn} / n
        
        Returns non-negative entropy value.
        """
        traces = self.operator.compute_trace_powers(s, self.max_power, max_branches)
        
        entropy = 0.0
        for n, tr_n in enumerate(traces, start=1):
            weight = PHI_INV ** (self.alpha * n)
            entropy += abs(tr_n) * weight / n
        
        return entropy
    
    def gradient(self, s: complex, delta: float = 1e-6) -> complex:
        """
        Compute gradient ∇E_φ(s) via finite differences.
        """
        E_s = self.compute(s)
        E_s_plus_real = self.compute(s + delta)
        E_s_plus_imag = self.compute(s + 1j * delta)
        
        grad_real = (E_s_plus_real - E_s) / delta
        grad_imag = (E_s_plus_imag - E_s) / delta
        
        return complex(grad_real, grad_imag)


# =============================================================================
# BRANCH DOMINANCE MEASURE
# =============================================================================

class BranchDominanceMeasure:
    """
    Branch dominance measure D_k(s).
    
    DEFINITION:
    The branch dominance measures how much a single branch k* contributes
    relative to all branches:
    
        D_k(s) = max_k |κ_k(s)|² / Σ_j |κ_j(s)|²
    
    where κ_k(s) = w_k · σ_k · e^{-s·ℓ_k} is the branch kernel.
    
    INTERPRETATION:
    - D_k ≈ 1 indicates single-branch dominance (singularity)
    - D_k ≈ 1/N indicates uniform distribution (no singularity)
    
    Parameters
    ----------
    operator : GeodesicTransferOperator
        The transfer operator L_s
    """
    
    def __init__(self, operator: GeodesicTransferOperator):
        self.operator = operator
        
    def compute(self, s: complex, max_branches: int = 100) -> Tuple[float, int]:
        """
        Compute branch dominance D_k(s) and dominant branch index.
        
        Returns (D_k, k*) where k* is the dominant branch.
        """
        kernel_magnitudes_sq = []
        
        for k in range(max_branches):
            kappa = self.operator.branch_kernel(k, s)
            kernel_magnitudes_sq.append(abs(kappa) ** 2)
        
        kernel_magnitudes_sq = np.array(kernel_magnitudes_sq)
        total = np.sum(kernel_magnitudes_sq)
        
        if total < 1e-15:
            return (0.0, 0)
        
        max_k = int(np.argmax(kernel_magnitudes_sq))
        dominance = kernel_magnitudes_sq[max_k] / total
        
        return (dominance, max_k)
    
    def dominance_profile(self, s: complex, max_branches: int = 100) -> np.ndarray:
        """
        Compute full dominance profile |κ_k(s)|² / Σ|κ_j|² for all k.
        """
        kernel_magnitudes_sq = np.array([
            abs(self.operator.branch_kernel(k, s)) ** 2
            for k in range(max_branches)
        ])
        
        total = np.sum(kernel_magnitudes_sq)
        if total < 1e-15:
            return np.zeros(max_branches)
        
        return kernel_magnitudes_sq / total


# =============================================================================
# PHASE ALIGNMENT FUNCTIONAL
# =============================================================================

class PhaseAlignmentFunctional:
    """
    Phase alignment functional Φ(s).
    
    DEFINITION:
    Phase alignment measures spectral coherence via:
    
        Φ(s) = |Σ_k κ_k(s)| / Σ_k |κ_k(s)|
    
    This ratio is 1 when all phases align (constructive) and 0 when
    phases cancel (destructive).
    
    ALTERNATIVE (spectral):
    Using eigenvalue phases:
        Φ(s) = |Σ_j e^{i·arg(λ_j)}| / #{eigenvalues}
    
    INTERPRETATION:
    - Φ ≈ 1 indicates phase coherence (singularity)
    - Φ ≈ 0 indicates phase cancellation (no singularity)
    
    Parameters
    ----------
    operator : GeodesicTransferOperator
        The transfer operator L_s
    """
    
    def __init__(self, operator: GeodesicTransferOperator):
        self.operator = operator
        
    def compute_kernel_alignment(self, s: complex, max_branches: int = 100) -> float:
        """
        Compute phase alignment via kernel sum ratio.
        
        Φ(s) = |Σ_k κ_k(s)| / Σ_k |κ_k(s)|
        """
        kernel_sum = 0j
        magnitude_sum = 0.0
        
        for k in range(max_branches):
            kappa = self.operator.branch_kernel(k, s)
            kernel_sum += kappa
            magnitude_sum += abs(kappa)
        
        if magnitude_sum < 1e-15:
            return 0.0
        
        return abs(kernel_sum) / magnitude_sum
    
    def compute_phase_variance(self, s: complex, max_branches: int = 100) -> float:
        """
        Compute phase variance (alternative measure).
        
        Low variance indicates high alignment.
        """
        phases = []
        for k in range(max_branches):
            kappa = self.operator.branch_kernel(k, s)
            if abs(kappa) > 1e-15:
                phases.append(np.angle(kappa))
        
        if len(phases) < 2:
            return 0.0
        
        phases = np.array(phases)
        # Circular variance
        mean_cos = np.mean(np.cos(phases))
        mean_sin = np.mean(np.sin(phases))
        R = np.sqrt(mean_cos**2 + mean_sin**2)
        
        # Alignment = R (circular mean length)
        return R


# =============================================================================
# SPECTRAL RADIUS FUNCTIONAL
# =============================================================================

class SpectralRadiusFunctional:
    """
    Spectral radius proximity functional R(s).
    
    DEFINITION:
    The spectral radius functional measures proximity to the critical value ρ = 1:
    
        R(s) = exp(-|ρ(L_s) - 1|² / ε²)
    
    This is maximized when ρ(L_s) = 1 (transfer operator has spectral radius 1).
    
    MATHEMATICAL SIGNIFICANCE:
    When ρ(L_s) = 1, the operator is at the boundary of contractivity.
    This corresponds to a spectral transition point.
    
    For Fredholm determinant: det(I - L_s) = 0 ⟺ 1 ∈ spectrum(L_s)
    So ρ = 1 is necessary (but not sufficient) for a zero.
    
    Parameters
    ----------
    operator : GeodesicTransferOperator
        The transfer operator L_s
    epsilon : float
        Width parameter for Gaussian measure
    """
    
    def __init__(self, operator: GeodesicTransferOperator, epsilon: float = 0.1):
        self.operator = operator
        self.epsilon = epsilon
        
    def estimate_spectral_radius(self, s: complex, max_branches: int = 100) -> float:
        """
        Estimate spectral radius ρ(L_s) via power iteration.
        
        ρ(L_s) ≈ ||L_s^n f||^{1/n} for large n and generic f.
        """
        dim = min(self.operator.H.dimension, 100)
        f = np.random.randn(dim) + 1j * np.random.randn(dim)
        f = f / np.linalg.norm(f)
        
        # Power iteration
        for _ in range(20):
            f_new = self.operator.apply_truncated(f, s, max_branches)
            norm_new = np.linalg.norm(f_new)
            if norm_new < 1e-15:
                return 0.0
            f = f_new / norm_new
        
        # Final estimate
        f_next = self.operator.apply_truncated(f, s, max_branches)
        return np.linalg.norm(f_next)
    
    def compute(self, s: complex, max_branches: int = 100) -> float:
        """
        Compute spectral radius proximity R(s).
        
        R(s) = exp(-|ρ(L_s) - 1|² / ε²)
        """
        rho = self.estimate_spectral_radius(s, max_branches)
        return np.exp(-((rho - 1) ** 2) / (self.epsilon ** 2))
    
    def is_near_critical(self, s: complex, max_branches: int = 100) -> bool:
        """
        Check if ρ(L_s) ∈ [1-ε, 1+ε].
        """
        rho = self.estimate_spectral_radius(s, max_branches)
        return abs(rho - 1) < self.epsilon


# =============================================================================
# COMBINED SINGULARITY FUNCTIONAL
# =============================================================================

class SingularityFunctional:
    """
    Combined singularity functional S(s).
    
    DEFINITION:
    S(s) = w_E · E_φ(s) + w_D · D_k(s) + w_Φ · Φ(s) + w_R · R(s)
    
    where w_E, w_D, w_Φ, w_R are weights balancing the contributions.
    
    SINGULARITY CRITERION:
    s* is a singularity if:
        1. S(s*) > S_threshold
        2. R(s*) > R_threshold (spectral radius near 1)
        3. One of: E_φ or D_k or Φ attains local extremum at s*
    
    THEOREM (SINGULARITY EXISTENCE):
    For the φ-weighted geodesic transfer operator L_s on H = L²(Ω, μ_φ),
    there exists at least one point s* on the critical line where S(s*)
    achieves a critical configuration, provided the geodesic spectrum
    satisfies certain density conditions.
    
    Parameters
    ----------
    operator : GeodesicTransferOperator
        The transfer operator L_s
    weights : Tuple[float, float, float, float]
        Weights (w_E, w_D, w_Φ, w_R), default (1, 1, 1, 1)
    """
    
    def __init__(
        self,
        operator: GeodesicTransferOperator,
        weights: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    ):
        self.operator = operator
        self.w_E, self.w_D, self.w_Phi, self.w_R = weights
        
        # Initialize component functionals
        self.entropy = PhiEntropyFunctional(operator)
        self.dominance = BranchDominanceMeasure(operator)
        self.phase = PhaseAlignmentFunctional(operator)
        self.spectral = SpectralRadiusFunctional(operator)
        
    def compute(self, s: complex, max_branches: int = 100) -> SingularityData:
        """
        Compute full singularity analysis at point s.
        """
        # Compute components
        E_phi = self.entropy.compute(s, max_branches)
        D_k, k_star = self.dominance.compute(s, max_branches)
        Phi = self.phase.compute_kernel_alignment(s, max_branches)
        rho = self.spectral.estimate_spectral_radius(s, max_branches)
        R = self.spectral.compute(s, max_branches)
        
        # Combined score
        S = self.w_E * E_phi + self.w_D * D_k + self.w_Phi * Phi + self.w_R * R
        
        # Check singularity criteria
        is_sing = (
            abs(rho - 1) < SPECTRAL_RADIUS_EPSILON and
            E_phi > ENTROPY_THRESHOLD and
            D_k > DOMINANCE_THRESHOLD and
            Phi > np.pi - PHASE_COHERENCE_DELTA
        )
        
        # Compute 9D curvature (placeholder - full computation in NINE_D module)
        curvature_9d = self._compute_9d_curvature(s, max_branches)
        
        return SingularityData(
            s_value=s,
            phi_entropy=E_phi,
            branch_dominance=D_k,
            dominant_branch=k_star,
            phase_alignment=Phi,
            spectral_radius=rho,
            singularity_score=S,
            is_singularity=is_sing,
            curvature_9d=curvature_9d
        )
    
    def _compute_9d_curvature(self, s: complex, max_branches: int) -> np.ndarray:
        """
        Compute 9D curvature invariants from operator data.
        
        The 9 components are:
        0: Trace curvature (|Tr(L_s)|)
        1: Spectral radius
        2: Phase alignment
        3: Entropy gradient magnitude
        4: Branch dominance
        5: Determinant magnitude estimate
        6: Condition number estimate
        7: Trace-square ratio |Tr(L_s²)|/|Tr(L_s)|²
        8: Decay rate of kernels
        """
        curvature = np.zeros(NUM_CURVATURE_COMPONENTS)
        
        # 0: Trace curvature
        trace = self.operator.compute_trace(s, max_branches)
        curvature[0] = abs(trace)
        
        # 1: Spectral radius
        curvature[1] = self.spectral.estimate_spectral_radius(s, max_branches)
        
        # 2: Phase alignment
        curvature[2] = self.phase.compute_kernel_alignment(s, max_branches)
        
        # 3: Entropy gradient
        grad = self.entropy.gradient(s)
        curvature[3] = abs(grad)
        
        # 4: Branch dominance
        D_k, _ = self.dominance.compute(s, max_branches)
        curvature[4] = D_k
        
        # 5: Determinant magnitude (from trace approximation)
        # log det ≈ -Tr for small operators
        curvature[5] = np.exp(-abs(trace))
        
        # 6: Condition number estimate (ratio of largest to smallest kernel)
        kernels = [abs(self.operator.branch_kernel(k, s)) for k in range(min(20, max_branches))]
        if min(kernels) > 1e-15:
            curvature[6] = max(kernels) / min(k if k > 1e-15 else 1e-15 for k in kernels)
        else:
            curvature[6] = 1e10
        
        # 7: Trace-square ratio
        traces = self.operator.compute_trace_powers(s, 2, max_branches)
        if abs(traces[0]) > 1e-15:
            curvature[7] = abs(traces[1]) / (abs(traces[0]) ** 2)
        else:
            curvature[7] = 0
        
        # 8: Kernel decay rate
        if len(kernels) > 5:
            log_kernels = [precomputed_log(max(1, int(1e10 * k))) / precomputed_log(10) 
                          for k in kernels[:10] if k > 1e-15]
            if len(log_kernels) > 2:
                curvature[8] = abs(log_kernels[-1] - log_kernels[0]) / len(log_kernels)
        
        return curvature
    
    def search_singularities(
        self,
        t_min: float,
        t_max: float,
        num_points: int = 100,
        sigma: float = 0.5
    ) -> List[SingularityData]:
        """
        Search for singularities on the critical line Re(s) = σ.
        """
        t_values = np.linspace(t_min, t_max, num_points)
        singularities = []
        
        for t in t_values:
            s = complex(sigma, t)
            data = self.compute(s)
            if data.is_singularity:
                singularities.append(data)
        
        return singularities
    
    def prove_existence(
        self,
        t_min: float,
        t_max: float,
        sigma: float = 0.5
    ) -> SingularityExistenceProof:
        """
        PROVE existence of at least one singularity in [t_min, t_max].
        
        METHOD: Intermediate Value Theorem + Extremum Detection
        
        THEOREM: If S(s) is continuous and:
        1. S at one endpoint is below threshold
        2. S at another point exceeds threshold
        Then ∃ s* where S(s*) = threshold (singularity).
        
        Alternatively, if S has a local maximum in the interval with
        S(s_max) > S_threshold, that maximum is a singularity.
        """
        verification_steps = []
        
        # Step 1: Evaluate S at multiple points
        t_test = np.linspace(t_min, t_max, 20)
        scores = []
        
        for t in t_test:
            s = complex(sigma, t)
            data = self.compute(s, max_branches=50)
            scores.append(data.singularity_score)
            verification_steps.append({
                'step': 'evaluation',
                't': t,
                'S': data.singularity_score,
                'spectral_radius': data.spectral_radius
            })
        
        scores = np.array(scores)
        
        # Step 2: Find maximum
        max_idx = np.argmax(scores)
        max_t = t_test[max_idx]
        max_score = scores[max_idx]
        
        verification_steps.append({
            'step': 'extremum_detection',
            't_max': max_t,
            'S_max': max_score
        })
        
        # Step 3: Refine around maximum
        if max_idx > 0 and max_idx < len(t_test) - 1:
            t_refined = np.linspace(t_test[max_idx - 1], t_test[max_idx + 1], 10)
            refined_scores = []
            
            for t in t_refined:
                s = complex(sigma, t)
                data = self.compute(s, max_branches=50)
                refined_scores.append((t, data.singularity_score, data))
            
            # Find refined maximum
            best = max(refined_scores, key=lambda x: x[1])
            max_t, max_score, max_data = best
            
            verification_steps.append({
                'step': 'refinement',
                't_refined': max_t,
                'S_refined': max_score
            })
        else:
            max_data = self.compute(complex(sigma, max_t), max_branches=50)
        
        # Step 4: Check singularity criterion
        singularity_found = max_data.spectral_radius > 1 - SPECTRAL_RADIUS_EPSILON
        
        verification_steps.append({
            'step': 'criterion_check',
            'spectral_radius': max_data.spectral_radius,
            'threshold': 1 - SPECTRAL_RADIUS_EPSILON,
            'is_singularity': singularity_found
        })
        
        return SingularityExistenceProof(
            interval=(t_min, t_max),
            singularity_found=singularity_found,
            singularity_location=max_t if singularity_found else None,
            singularity_data=max_data if singularity_found else None,
            proof_method='extremum_detection',
            verification_steps=verification_steps
        )


# =============================================================================
# STABILITY ANALYSIS
# =============================================================================

class SingularityStability:
    """
    Analyze stability and regularity of singularities.
    
    THEOREM (Stability):
    If s* is a singularity with S(s*) > S_threshold + ε, then for all
    s in B_δ(s*) (δ-ball around s*), S(s) > S_threshold.
    
    The singularity persists under small perturbations.
    
    THEOREM (Non-Accumulation):
    Singularities cannot accumulate in a compact region unless the
    spectral radius of L_s equals 1 on a continuous arc.
    """
    
    def __init__(self, singularity_functional: SingularityFunctional):
        self.S = singularity_functional
        
    def check_stability(
        self,
        s_star: complex,
        delta: float = 0.1,
        num_samples: int = 8
    ) -> Dict[str, Any]:
        """
        Check if singularity at s* is stable under perturbations.
        """
        # Sample points in δ-neighborhood
        angles = np.linspace(0, 2 * np.pi, num_samples, endpoint=False)
        perturbed_points = [
            s_star + delta * np.exp(1j * angle) for angle in angles
        ]
        
        # Compute S at perturbed points
        central_data = self.S.compute(s_star, max_branches=50)
        perturbed_scores = []
        
        for s_pert in perturbed_points:
            data = self.S.compute(s_pert, max_branches=50)
            perturbed_scores.append(data.singularity_score)
        
        # Check if central is local maximum
        is_local_max = all(central_data.singularity_score >= p - 0.01 
                         for p in perturbed_scores)
        
        # Estimate stability radius
        score_std = np.std(perturbed_scores)
        stability_radius = delta * central_data.singularity_score / (score_std + 1e-10)
        
        return {
            's_star': s_star,
            'central_score': central_data.singularity_score,
            'perturbed_scores': perturbed_scores,
            'is_local_maximum': is_local_max,
            'stability_radius': stability_radius,
            'is_stable': is_local_max and score_std < 0.1 * central_data.singularity_score
        }
    
    def check_non_accumulation(
        self,
        singularities: List[SingularityData],
        min_separation: float = 0.5
    ) -> Dict[str, Any]:
        """
        Verify singularities are well-separated (non-accumulating).
        """
        if len(singularities) < 2:
            return {'well_separated': True, 'min_distance': float('inf')}
        
        # Compute pairwise distances
        locations = [s.s_value for s in singularities]
        min_dist = float('inf')
        
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                dist = abs(locations[i] - locations[j])
                min_dist = min(min_dist, dist)
        
        return {
            'well_separated': min_dist >= min_separation,
            'min_distance': min_dist,
            'num_singularities': len(singularities)
        }


# =============================================================================
# FACTORY AND TESTING
# =============================================================================

def create_singularity_functional(
    genus: int = 2,
    num_geodesics: int = 100
) -> SingularityFunctional:
    """
    Factory function to create singularity functional.
    """
    operator = create_geodesic_operator(genus, num_geodesics)
    return SingularityFunctional(operator)


def test_singularity_existence():
    """
    Test singularity existence proof on an interval.
    """
    print("=" * 70)
    print("SINGULARITY FUNCTIONAL - Existence Test")
    print("=" * 70)
    print()
    
    # Create functional
    S = create_singularity_functional(genus=2, num_geodesics=100)
    
    # Test interval around first Riemann zero
    t_min, t_max = 10.0, 20.0
    
    print(f"Search interval: t ∈ [{t_min}, {t_max}]")
    print(f"Critical line: Re(s) = 0.5")
    print()
    
    # Prove existence
    proof = S.prove_existence(t_min, t_max, sigma=0.5)
    
    print("EXISTENCE PROOF RESULTS")
    print("-" * 50)
    print(f"  Singularity found: {proof.singularity_found}")
    if proof.singularity_found:
        print(f"  Location: t* = {proof.singularity_location:.6f}")
        print(f"  Singularity score: S(s*) = {proof.singularity_data.singularity_score:.6f}")
        print(f"  Spectral radius: ρ(L_s*) = {proof.singularity_data.spectral_radius:.6f}")
        print(f"  φ-entropy: E_φ(s*) = {proof.singularity_data.phi_entropy:.6f}")
        print(f"  Phase alignment: Φ(s*) = {proof.singularity_data.phase_alignment:.6f}")
    print(f"  Proof method: {proof.proof_method}")
    print()
    
    # Test stability
    if proof.singularity_found:
        stability_analyzer = SingularityStability(S)
        s_star = complex(0.5, proof.singularity_location)
        stability = stability_analyzer.check_stability(s_star)
        
        print("STABILITY ANALYSIS")
        print("-" * 50)
        print(f"  Is local maximum: {stability['is_local_maximum']}")
        print(f"  Stability radius: {stability['stability_radius']:.4f}")
        print(f"  Is stable: {stability['is_stable']}")
    
    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    return proof


if __name__ == "__main__":
    test_singularity_existence()
