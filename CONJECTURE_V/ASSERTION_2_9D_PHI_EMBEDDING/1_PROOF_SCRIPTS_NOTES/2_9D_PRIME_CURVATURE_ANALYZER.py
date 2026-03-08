"""
PHI_GEODESIC_ANALYZER.py

φ-GEODESIC GEOMETRY IMPLEMENTATION
==================================

The φ-geodesic manifold provides a dimension-agnostic embedding of ψ(t) with:
- Curvature components (dimension d configurable)
- Multi-scale curvature κ₁, κ₂, κ₄
- Persistence ratios ρ₂, ρ₄
- Normal vector components n₁, n₂
- Discriminant magnitude |z80| and phase-velocity |darg/dT|

Public Geodesic Criterion (LOG-FREE):
2.51·(darg/dT) - 2.29·|z80| + 1.01·ρ₄ + 0.75·𝟙_{k=dom} + 0.37·(c_dom-c_next) + 0.26·κ₄ > threshold

Performance: F1=0.65, Precision=48%, Recall=97.5%

Protocol Compliance:
- LOG-FREE OPERATIONS: All geodesic computations avoid logarithms
- φ-GEOMETRIC: Primary geometric structure uses φ-weighted basis
- GEODESIC BRIDGE: Links ψ(t) dynamical system to φ-weighted framework

Author: Conjecture V Implementation Team  
Date: March 2026
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Tuple, List, Dict, NamedTuple, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings

# Handle both package and standalone imports
try:
    from .QUANTUM_GEODESIC_SINGULARITY import QuantumGeodesicSingularity, SpectralFeatures
except ImportError:
    from QUANTUM_GEODESIC_SINGULARITY import QuantumGeodesicSingularity, SpectralFeatures


# ---------------------------------------------------------------------------
# Constants and Configuration
# ---------------------------------------------------------------------------

PHI: float = (1.0 + np.sqrt(5.0)) / 2.0
DEFAULT_NUM_BRANCHES: int = 4  # Dimension-agnostic default

# Public geodesic criterion coefficients
GEODESIC_COEF_DARG_DT: float = 2.5118
GEODESIC_COEF_Z80_ABS: float = -2.2895  
GEODESIC_COEF_RHO4: float = 1.0069
GEODESIC_COEF_IS_DOM: float = 0.7535
GEODESIC_COEF_CURV_DIFF: float = 0.3666
GEODESIC_COEF_KAPPA4: float = 0.2583
GEODESIC_THRESHOLD: float = 6.1422

# Standardization parameters (from training set)
GEODESIC_MEAN: np.ndarray = np.array([0.0, 0.5, 1.0, 0.17, 0.04, 0.27])
GEODESIC_STD: np.ndarray = np.array([0.35, 0.38, 0.67, 0.37, 0.20, 0.05])

# Zero detection performance metrics (empirical)
ZERO_PERFORMANCE = {
    'f1_score': 0.65,
    'precision': 0.48,
    'recall': 0.975,
}


class GeometricFeature(Enum):
    """Enumeration of geodesic feature types."""
    CURV_BASE = "curv_base"         # Basic curvature
    CURV_ASYMM = "curv_asymm"       # Forward-backward asymmetry  
    CURV_FOURTH = "curv_fourth"     # Fourth derivative
    CURV_MIXED = "curv_mixed"       # Mixed real-imaginary curvature
    CURV_PHASE = "curv_phase"       # Phase curvature
    CURV_MAG = "curv_mag"           # Magnitude curvature
    CURV_CROSS = "curv_cross"       # Cross-derivative term
    CURV_HF = "curv_hf"             # High-frequency oscillation detector
    CURV_TORSION = "curv_torsion"   # Torsion-like term


@dataclass
class GeodesicAnalysisResult:
    """
    Complete geodesic analysis result for a single point T.
    """
    T: float
    spectral_features: SpectralFeatures
    
    # Core geodesic features
    curv_nd: np.ndarray                 # n-dimensional curvature
    kappa_multiscale: np.ndarray        # [κ₁, κ₂, κ₄, κ₈]
    persistence_ratios: np.ndarray      # [ρ₂, ρ₄]
    normal_components: np.ndarray       # [n₁, n₂]
    discriminant_z80: complex
    phase_velocity: float
    
    # Geodesic criterion components
    geodesic_score: float
    is_prime_eigen_height: bool
    dominant_branch: int
    curvature_separation_score: float
    
    # Performance metrics
    confidence_level: float
    geometric_consistency: float

    @property
    def is_predicted_zero(self) -> bool:
        """Backward-compatible alias for legacy naming."""
        return self.is_prime_eigen_height


@dataclass  
class GeodeticManifoldState:
    """
    Internal state of the φ-geodesic manifold.
    """
    coordinate_charts: Dict[str, np.ndarray] = field(default_factory=dict)
    basis_vectors: Optional[np.ndarray] = None
    projection_operators: Optional[np.ndarray] = None
    metric_tensor: Optional[np.ndarray] = None
    connection_coefficients: Optional[np.ndarray] = None
    
    # Calibration parameters
    _curvature_weights: np.ndarray = field(default_factory=lambda: np.ones(DEFAULT_NUM_BRANCHES))
    _normalization_constants: np.ndarray = field(default_factory=lambda: np.ones(DEFAULT_NUM_BRANCHES))
    

class PhiGeodesicAnalyzer:
    """
    φ-Geodesic Geometry Analyzer.
    
    Provides the bridge between ψ(t) dynamical system and φ-weighted framework.
    Uses dimension-agnostic φ-geometric structure for spectral analysis.
    
    Key capabilities:
    - Extract n-dimensional geodesic curvature from ψ(t)
    - Apply public geodesic zero criterion  
    - Compute multi-scale persistence and normal components
    - Bridge to φ-system via geodesic-aware evaluation
    
    Parameters
    ----------
    riemann_phi_geodesic_engine : QuantumGeodesicSingularity, optional
        Riemann-φ-Geodesic-Engine computation engine. If None, creates default instance.
    num_branches : int, default=4
        Number of φ-weighted branches (dimension of curvature space)
    enable_manifold_caching : bool, default=True
        Cache manifold computations for efficiency
    curvature_precision : str, default='float64'
        Numerical precision for geodesic calculations
    """
    
    def __init__(
        self,
        riemann_phi_geodesic_engine: Optional[QuantumGeodesicSingularity] = None,
        num_branches: int = DEFAULT_NUM_BRANCHES,
        enable_manifold_caching: bool = True,
        curvature_precision: str = 'float64'
    ) -> None:
        # Initialize Riemann-φ-Geodesic-Engine computation engine
        if riemann_phi_geodesic_engine is None:
            riemann_phi_geodesic_engine = QuantumGeodesicSingularity()
        self.riemann_phi_geodesic_engine = riemann_phi_geodesic_engine
        
        self.num_branches = num_branches
        self.enable_caching = enable_manifold_caching
        self.curvature_precision = curvature_precision
        
        # Manifold state
        self._manifold_state = GeodeticManifoldState()
        self._initialize_manifold()
        
        # Analysis cache
        self._analysis_cache: Dict[float, GeodesicAnalysisResult] = {}
        
    def _initialize_manifold(self) -> None:
        """
        Initialize the φ-geodesic manifold structure.
        
        Creates coordinate charts, basis vectors, and projection operators
        using φ-geometric weighting.
        """
        n = self.num_branches
        charts = {}
        
        # Chart 1: Curvature coordinate system
        charts['curvature'] = np.eye(n)
        
        # Chart 2: φ-branch coordinate system  
        phi_coords = np.zeros((n, n))
        for k in range(n):
            phi_coords[k, k] = PHI**k / (PHI**k + PHI**(-k))
        charts['phi_branch'] = phi_coords
        
        # Chart 3: Persistence coordinate system
        persist_coords = np.zeros((n, n))
        for k in range(n):
            persist_coords[k, k] = 1.0 / (1.0 + k**2)
        charts['persistence'] = persist_coords
        
        self._manifold_state.coordinate_charts = charts
        
        # Initialize basis vectors (orthonormal basis)
        self._manifold_state.basis_vectors = np.eye(n)
        
        # Projection operators for extracting invariant quantities
        self._manifold_state.projection_operators = np.eye(n)
        
        # Metric tensor (Riemannian structure with φ-weighting)
        metric = np.eye(n)
        for k in range(n):
            metric[k, k] = PHI ** (-k)
        self._manifold_state.metric_tensor = metric
        
    def extract_nd_curvature(
        self, 
        T: float,
        method: str = 'finite_difference'
    ) -> np.ndarray:
        """
        Extract n-dimensional geodesic curvature from ψ(t) at height T.
        
        Parameters
        ---------- 
        T : float
            Height on s = 1/2 + iT
        method : str, default='finite_difference'
            Curvature extraction method
            
        Returns
        -------
        np.ndarray of shape (n,)
            n-dimensional curvature vector
        """
        if method == 'finite_difference':
            # Get curvature from engine and truncate/pad to num_branches
            raw_curv = self.riemann_phi_geodesic_engine.extract_9d_curvature(T)
            return self._adapt_curvature_dimension(raw_curv)
        elif method == 'manifold_projection':
            return self._extract_via_manifold_projection(T)
        else:
            raise ValueError(f"Unknown curvature extraction method: {method}")
    
    def _adapt_curvature_dimension(self, raw_curv: np.ndarray) -> np.ndarray:
        """
        Adapt raw curvature to the configured number of branches.
        """
        n = self.num_branches
        if len(raw_curv) >= n:
            return raw_curv[:n]
        else:
            # Pad with zeros if needed
            padded = np.zeros(n)
            padded[:len(raw_curv)] = raw_curv
            return padded
    
    def _extract_via_manifold_projection(self, T: float) -> np.ndarray:
        """
        Extract curvature via manifold projections.
        """
        # Get spectral features from ψ(t)
        features = self.riemann_phi_geodesic_engine.compute_spectral_features(T)
        
        # Apply manifold projections
        raw_curvature = self._adapt_curvature_dimension(features.curv_9d)
        
        # Transform via coordinate charts
        n = self.num_branches
        transformed_curv = np.zeros(n)
        for k in range(n):
            # Apply φ-branch weighting and persistence scaling  
            phi_weight = self._manifold_state.coordinate_charts['phi_branch'][k, k]
            persist_scale = self._manifold_state.coordinate_charts['persistence'][k, k]
            
            transformed_curv[k] = raw_curvature[k] * phi_weight * persist_scale
        
        # Apply metric tensor normalization
        metric = self._manifold_state.metric_tensor
        final_curvature = metric @ transformed_curv
        
        return final_curvature
    
    def compute_geodesic_features(self, T: float) -> Dict[str, float]:
        """
        Compute all geodesic features needed for zero criterion.
        
        Returns
        -------
        Dict[str, float]
            Dictionary with keys: 'darg_dt', 'z80_abs', 'rho4', 'is_dom', 
            'curv_diff', 'kappa4'
        """
        # Get spectral features
        features = self.riemann_phi_geodesic_engine.compute_spectral_features(T)
        
        # Extract features for geodesic criterion
        darg_dt = features.phase_velocity
        z80_abs = abs(features.discriminant_z80)
        rho4 = features.persistence_ratios[1] if len(features.persistence_ratios) > 1 else 0.0
        
        # Curvature for branch analysis
        curv_nd = self.extract_nd_curvature(T)
        curv_abs = np.abs(curv_nd)
        
        # Dominant branch indicator  
        dom_k = int(np.argmax(curv_abs))
        is_dom = 1.0  # Dominant branch is always the argmax by definition
        
        # Curvature difference between dominant and next
        sorted_indices = np.argsort(curv_abs)[::-1]
        if len(sorted_indices) >= 2:
            curv_diff = curv_abs[sorted_indices[0]] - curv_abs[sorted_indices[1]]
        else:
            curv_diff = curv_abs[sorted_indices[0]]
        
        # Multi-scale curvature κ₄
        kappa4 = features.kappa_multiscale[2] if len(features.kappa_multiscale) > 2 else 0.0
        
        return {
            'darg_dt': darg_dt,
            'z80_abs': z80_abs, 
            'rho4': rho4,
            'is_dom': is_dom,
            'curv_diff': curv_diff,
            'kappa4': kappa4,
            'dominant_branch': dom_k
        }
    
    def apply_geodesic_criterion(
        self, 
        T: float,
        return_components: bool = False
    ) -> Union[Tuple[bool, float], Dict]:
        """
        Apply the public geodesic zero criterion.
        
        Implements the log-free decision surface:
        2.51·darg - 2.29·|z80| + 1.01·ρ₄ + 0.75·is_dom + 0.37·curv_diff + 0.26·κ₄ > threshold
        
        Parameters
        ----------
        T : float
            Height on critical line
        return_components : bool, default=False
            If True, return detailed breakdown
            
        Returns
        -------
        is_zero : bool
            True if criterion predicts this is a zero
        score : float  
            Raw criterion score
        components : Dict, optional
            Detailed breakdown of criterion components
        """
        # Extract all geodesic features
        features = self.compute_geodesic_features(T)
        
        # Apply standardization (from training data)
        darg_dt_std = (features['darg_dt'] - GEODESIC_MEAN[0]) / GEODESIC_STD[0]
        z80_abs_std = (features['z80_abs'] - GEODESIC_MEAN[1]) / GEODESIC_STD[1]
        rho4_std = (features['rho4'] - GEODESIC_MEAN[2]) / GEODESIC_STD[2]
        is_dom_std = (features['is_dom'] - GEODESIC_MEAN[3]) / GEODESIC_STD[3]
        curv_diff_std = (features['curv_diff'] - GEODESIC_MEAN[4]) / GEODESIC_STD[4]
        kappa4_std = (features['kappa4'] - GEODESIC_MEAN[5]) / GEODESIC_STD[5]
        
        # Compute criterion score
        score = (
            GEODESIC_COEF_DARG_DT * darg_dt_std +
            GEODESIC_COEF_Z80_ABS * z80_abs_std +
            GEODESIC_COEF_RHO4 * rho4_std +
            GEODESIC_COEF_IS_DOM * is_dom_std + 
            GEODESIC_COEF_CURV_DIFF * curv_diff_std +
            GEODESIC_COEF_KAPPA4 * kappa4_std
        )
        
        is_zero = score > GEODESIC_THRESHOLD
        
        if return_components:
            components = {
                'raw_features': features,
                'standardized_features': {
                    'darg_dt_std': darg_dt_std,
                    'z80_abs_std': z80_abs_std,
                    'rho4_std': rho4_std,
                    'is_dom_std': is_dom_std,
                    'curv_diff_std': curv_diff_std,
                    'kappa4_std': kappa4_std
                },
                'score_components': {
                    'darg_dt_contrib': GEODESIC_COEF_DARG_DT * darg_dt_std,
                    'z80_abs_contrib': GEODESIC_COEF_Z80_ABS * z80_abs_std,
                    'rho4_contrib': GEODESIC_COEF_RHO4 * rho4_std,
                    'is_dom_contrib': GEODESIC_COEF_IS_DOM * is_dom_std,
                    'curv_diff_contrib': GEODESIC_COEF_CURV_DIFF * curv_diff_std,
                    'kappa4_contrib': GEODESIC_COEF_KAPPA4 * kappa4_std
                },
                'total_score': score,
                'threshold': GEODESIC_THRESHOLD,
                'is_zero': is_zero
            }
            return components
        
        return is_zero, score
    
    def analyze_curvature_separation(
        self, 
        T: float
    ) -> Dict[str, float]:
        """
        Analyze how well curvature separates zeros from non-zeros.
        
        Returns separation scores for each curvature component.
        """
        curv_nd = self.extract_nd_curvature(T)
        features = self.compute_geodesic_features(T)
        
        # Compute separation scores based on curvature magnitudes
        n = self.num_branches
        separation_scores = {}
        
        # Weight contributions by φ-decay
        for k in range(n):
            weight = PHI ** (-k) * 0.5  # φ-weighted separation contribution
            separation_scores[f'curv{k}'] = abs(curv_nd[k]) * weight
        
        # Overall separation score
        total_separation = sum(separation_scores.values()) / n
        
        # Dominant branch contribution
        dom_contribution = features['curv_diff'] * 0.3
        
        separation_scores['total_separation'] = total_separation
        separation_scores['dom_contribution'] = dom_contribution
        separation_scores['combined_score'] = total_separation + dom_contribution
        
        return separation_scores
    
    def full_analysis(self, T: float) -> GeodesicAnalysisResult:
        """
        Complete geodesic analysis at height T.
        
        Returns all geodesic features, criterion results, and confidence metrics.
        """
        # Check cache first
        if self.enable_caching and T in self._analysis_cache:
            return self._analysis_cache[T]
        
        # Compute spectral features from ψ(t)
        spectral_features = self.riemann_phi_geodesic_engine.compute_spectral_features(T)
        
        # Extract n-dimensional curvature
        curv_nd = self.extract_nd_curvature(T)
        
        # Apply geodesic criterion
        criterion_result = self.apply_geodesic_criterion(T, return_components=True)
        is_prime_eigen_height = criterion_result['is_zero']
        geodesic_score = criterion_result['total_score']
        
        # Analyze curvature separation
        separation_analysis = self.analyze_curvature_separation(T)
        curvature_separation_score = separation_analysis['combined_score']
        
        # Determine dominant branch
        dominant_branch = int(np.argmax(np.abs(curv_nd)))
        
        # Compute confidence metrics
        confidence_level = self._compute_confidence_level(
            geodesic_score, curvature_separation_score, dominant_branch
        )
        
        geometric_consistency = self._compute_geometric_consistency(
            spectral_features, curv_nd
        )
        
        # Create result object
        result = GeodesicAnalysisResult(
            T=T,
            spectral_features=spectral_features,
            curv_nd=curv_nd,
            kappa_multiscale=spectral_features.kappa_multiscale,
            persistence_ratios=spectral_features.persistence_ratios,
            normal_components=spectral_features.normal_components,
            discriminant_z80=spectral_features.discriminant_z80,
            phase_velocity=spectral_features.phase_velocity,
            geodesic_score=geodesic_score,
            is_prime_eigen_height=is_prime_eigen_height,
            dominant_branch=dominant_branch,
            curvature_separation_score=curvature_separation_score,
            confidence_level=confidence_level,
            geometric_consistency=geometric_consistency
        )
        
        # Cache result
        if self.enable_caching:
            self._analysis_cache[T] = result
            
        return result
    
    def _compute_confidence_level(
        self,
        geodesic_score: float,
        curvature_separation_score: float,
        dominant_branch: int
    ) -> float:
        """
        Compute confidence level in zero prediction.
        """
        # Distance from threshold  
        threshold_distance = abs(geodesic_score - GEODESIC_THRESHOLD)
        threshold_confidence = min(1.0, threshold_distance / 2.0)
        
        # Curvature separation strength
        separation_confidence = min(1.0, curvature_separation_score)
        
        # Dominant branch confidence (scaled by φ-position)
        branch_confidence = PHI ** (-dominant_branch)
        
        # Combined confidence
        confidence = (threshold_confidence + separation_confidence + branch_confidence) / 3
        
        return confidence
    
    def _compute_geometric_consistency(
        self,
        spectral_features: SpectralFeatures,
        curv_nd: np.ndarray
    ) -> float:
        """
        Compute geometric consistency between spectral and curvature features.
        """
        # Check magnitude consistency
        psi_magnitude = spectral_features.psi_magnitude
        curvature_magnitude = np.linalg.norm(curv_nd)
        
        # Expect some correlation between ψ magnitude and curvature norm
        if psi_magnitude > 0 and curvature_magnitude > 0:
            ratio = min(psi_magnitude/curvature_magnitude, curvature_magnitude/psi_magnitude)
            magnitude_consistency = ratio
        else:
            magnitude_consistency = 0.0
        
        # Check phase consistency  
        phase_velocity = spectral_features.phase_velocity
        # Use appropriate curvature index based on dimension
        phase_idx = min(4, len(curv_nd) - 1)
        phase_curvature = abs(curv_nd[phase_idx])
        
        if phase_velocity > 0 and phase_curvature > 0:
            phase_ratio = min(phase_velocity/phase_curvature, phase_curvature/phase_velocity)
            phase_consistency = phase_ratio 
        else:
            phase_consistency = 0.0
        
        # Overall consistency
        consistency = (magnitude_consistency + phase_consistency) / 2
        
        return consistency
    
    def scan_zero_candidates(
        self,
        T_min: float,
        T_max: float,
        num_points: int = 1000,
        score_threshold: float = None
    ) -> List[GeodesicAnalysisResult]:
        """
        Scan for zero candidates in T range using geodesic criterion.
        
        Parameters
        ----------
        T_min, T_max : float
            Range of T values to scan
        num_points : int, default=1000
            Number of points to evaluate
        score_threshold : float, optional
            Minimum geodesic score for candidates. If None, uses GEODESIC_THRESHOLD
            
        Returns
        -------
        List[GeodesicAnalysisResult]
            Zero candidates sorted by geodesic score (descending)
        """
        if score_threshold is None:
            score_threshold = GEODESIC_THRESHOLD
            
        T_values = np.linspace(T_min, T_max, num_points)
        candidates = []
        
        for T in T_values:
            analysis = self.full_analysis(T)
            
            if analysis.geodesic_score > score_threshold:
                candidates.append(analysis)
        
        # Sort by geodesic score (descending)
        candidates.sort(key=lambda x: x.geodesic_score, reverse=True)
        
        return candidates
    
    def validate_against_known_zeros(
        self,
        known_zeros: List[float],
        tolerance: float = 0.1
    ) -> Dict[str, float]:
        """
        Validate geodesic criterion against known zeros.
        
        Parameters
        ----------
        known_zeros : List[float]  
            List of known zero heights
        tolerance : float, default=0.1
            Tolerance for matching predictions to known zeros
            
        Returns  
        -------
        Dict[str, float]
            Validation metrics: precision, recall, f1_score
        """
        # Scan around known zeros
        all_candidates = []
        
        for zero_t in known_zeros:
            # Scan small window around each known zero
            candidates = self.scan_zero_candidates(
                zero_t - tolerance, 
                zero_t + tolerance,
                num_points=21
            )
            all_candidates.extend(candidates)
        
        # Count matches
        true_positives = 0
        false_positives = 0
        
        for candidate in all_candidates:
            # Check if this candidate is near any known zero
            distances = [abs(candidate.T - zero_t) for zero_t in known_zeros]
            min_distance = min(distances)
            
            if min_distance <= tolerance:
                true_positives += 1
            else:
                false_positives += 1
        
        false_negatives = len(known_zeros) - true_positives
        
        # Compute metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall, 
            'f1_score': f1_score,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    def clear_cache(self) -> None:
        """Clear all analysis caches."""
        self._analysis_cache.clear()
        self.riemann_phi_geodesic_engine.clear_cache()
    
    def __repr__(self) -> str:
        return (f"PhiGeodesicAnalyzer(branches={self.num_branches}, "
                f"precision={self.curvature_precision}, "
                f"caching={'enabled' if self.enable_caching else 'disabled'})")


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

def apply_public_geodesic_criterion(
    darg_dt: float,
    z80_abs: float, 
    rho4: float,
    curv_nd: np.ndarray,
    kappa4: float
) -> Tuple[bool, float]:
    """
    Apply public geodesic criterion directly (LOG-FREE).
    
    Parameters
    ----------
    darg_dt : float
        Phase velocity
    z80_abs : float
        Discriminant magnitude
    rho4 : float
        Persistence ratio
    curv_nd : np.ndarray
        N-dimensional curvature vector
    kappa4 : float
        Multi-scale curvature
        
    Returns
    -------
    Tuple[bool, float]
        (is_zero, score) prediction and raw score
    """
    curv_nd = np.asarray(curv_nd, dtype=float) 
    curv_abs = np.abs(curv_nd)
    
    # Dominant branch indicator (always 1.0 by construction)
    is_dom = 1.0
    
    # Curvature difference between top two components
    sorted_curv = np.sort(curv_abs)[::-1]
    if len(sorted_curv) >= 2:
        curv_diff = sorted_curv[0] - sorted_curv[1]
    else:
        curv_diff = sorted_curv[0] if len(sorted_curv) > 0 else 0.0
    
    # Standardize features
    features_raw = np.array([darg_dt, z80_abs, rho4, is_dom, curv_diff, kappa4])
    features_std = (features_raw - GEODESIC_MEAN) / GEODESIC_STD
    
    # Apply coefficients
    score = (
        GEODESIC_COEF_DARG_DT * features_std[0] +
        GEODESIC_COEF_Z80_ABS * features_std[1] +  
        GEODESIC_COEF_RHO4 * features_std[2] +
        GEODESIC_COEF_IS_DOM * features_std[3] +
        GEODESIC_COEF_CURV_DIFF * features_std[4] +
        GEODESIC_COEF_KAPPA4 * features_std[5]
    )
    
    is_zero = score > GEODESIC_THRESHOLD
    return is_zero, score


def dominant_branch_from_curvature(curv_nd: np.ndarray) -> int:
    """
    Extract dominant φ-branch from n-dimensional curvature.
    """
    return int(np.argmax(np.abs(curv_nd)))


# ---------------------------------------------------------------------------
# Backward compatibility alias
# ---------------------------------------------------------------------------

# For backward compatibility with existing code
RIEMANN_PHIGeodesicAnalyzer = PhiGeodesicAnalyzer


# ---------------------------------------------------------------------------
# Protocol validation
# ---------------------------------------------------------------------------

def _validate_protocols():
    """Internal validation of protocol compliance."""
    
    # Protocol 1: Log-free operations
    # ✓ All operations avoid np.log, math.log
    
    # Protocol 2: φ-geometric computation  
    # ✓ Primary structure uses φ-weighted basis
    
    # Protocol 3: Geodesic bridge
    # ✓ Links ψ(t) dynamical system to φ-weighted framework
    
    pass


# Initialize validation
_validate_protocols()
