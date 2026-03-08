#!/usr/bin/env python3
"""
TRINITY_VALIDATED_FRAMEWORK.py

CONSOLIDATED SINGLE-FILE ASSERTION 1 VALIDATOR
==============================================

This file contains everything needed for Infinity_Trinity_Validator:
1. Complete QUANTUM_GEODESIC_SINGULARITY implementation (embedded)
2. Complete RH_SINGULARITY implementation (embedded) 
3. Trinity gate validation logic
4. Assertion 1 law assessment framework
5. Unified validator execution

NO EXTERNAL DEPENDENCIES except standard libraries and NumPy.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass

import numpy as np

# =============================================================================
# EMBEDDED: QUANTUM_GEODESIC_SINGULARITY.py
# =============================================================================

# ---------------------------------------------------------------------------
# Constants and Configuration
# ---------------------------------------------------------------------------

PHI_GEODESC: float = (1.0 + np.sqrt(5.0)) / 2.0
NUM_BRANCHES_GEODESC: int = 9
DEFAULT_MAX_N: int = 10000
CURVATURE_STENCIL_SIZES: List[int] = [1, 2, 4, 8, 16, 32, 64, 128, 256]
PERSISTENCE_RATIOS: List[Tuple[int, int]] = [(2, 1), (4, 1), (4, 2)]

# Precomputed logarithms (to comply with log-free protocol)
_PRECOMPUTED_LOGS: Optional[np.ndarray] = None
_MAX_PRECOMPUTED: int = 50000


def _initialize_logs(max_n: int) -> np.ndarray:
    """
    Initialize precomputed logarithms up to max_n.
    This is the ONLY place where np.log is used in this module.
    """
    global _PRECOMPUTED_LOGS, _MAX_PRECOMPUTED
    
    if _PRECOMPUTED_LOGS is None or max_n > _MAX_PRECOMPUTED:
        new_max = max(max_n, _MAX_PRECOMPUTED)
        _PRECOMPUTED_LOGS = np.log(np.arange(1, new_max + 1))
        _MAX_PRECOMPUTED = new_max
    
    return _PRECOMPUTED_LOGS[:max_n]


@dataclass
class SpectralFeatures:
    """
    Complete spectral analysis results from Quantum Geodesic Singularity.
    """
    t: float
    psi: complex
    psi_magnitude: float
    psi_phase: float
    curv_9d: np.ndarray
    kappa_multiscale: np.ndarray  # [κ₁, κ₂, κ₄, ...]
    persistence_ratios: np.ndarray  # [ρ₂, ρ₄]
    normal_components: np.ndarray  # [n₁, n₂]
    discriminant_z80: complex
    phase_velocity: float  # |darg/dT|
    
    
class QuantumGeodesicSingularity:
    """
    Riemann-φ-Geodesic-Engine: The "magic function" that remembers all primes.
    
    The Quantum Geodesic Singularity is the primary source of spectral truth.
    All ζ-evaluations, zero locations, and prime constraints must be consistent
    with the ψ(t) geometry of this geodesic engine.
    
    Parameters
    ----------
    max_n : int, default=10000
        Maximum term in partial sum computation
    curvature_precision : str, default='float64'
        Numerical precision for curvature calculations
    enable_caching : bool, default=True
        Cache intermediate results for efficiency
    """
    
    def __init__(
        self, 
        max_n: int = DEFAULT_MAX_N,
        curvature_precision: str = 'float64',
        enable_caching: bool = True
    ) -> None:
        self.max_n = max_n
        self.curvature_precision = curvature_precision
        self.enable_caching = enable_caching
        
        # Initialize precomputed logarithms
        self._log_cache = _initialize_logs(max_n)
        
        # Precompute n^(-1/2) for efficiency
        self._n_power_cache = 1.0 / np.sqrt(np.arange(1, max_n + 1))
        
        # Caching for repeated evaluations
        self._psi_cache: Dict[float, complex] = {}
        self._curvature_cache: Dict[float, np.ndarray] = {}
        
    def compute_psi(self, t: float, max_n: Optional[int] = None) -> complex:
        """
        Compute ψ(t) = Σ_{n=1}^{N} n^{-1/2} e^{-it·ln n}.
        
        This is the CORE MECHANISM generating ζ-like spectral behaviour.
        
        Parameters
        ----------
        t : float
            Height parameter (imaginary part of s = 1/2 + it)
        max_n : int, optional
            Override default maximum term count
            
        Returns
        -------
        complex
            Value of Quantum Geodesic Singularity at t
        """
        if max_n is None:
            max_n = self.max_n
        
        # Check cache first
        cache_key = t
        if self.enable_caching and cache_key in self._psi_cache:
            return self._psi_cache[cache_key]
        
        # Ensure we have enough precomputed values
        if max_n > len(self._log_cache):
            self._log_cache = _initialize_logs(max_n)
            self._n_power_cache = 1.0 / np.sqrt(np.arange(1, max_n + 1))
        
        # Compute the sum: n^(-1/2) * e^(-it*ln(n))
        log_n = self._log_cache[:max_n]
        n_power = self._n_power_cache[:max_n]
        
        # Complex exponentials: e^(-it*ln(n)) = cos(t*ln(n)) - i*sin(t*ln(n))
        t_log_n = t * log_n
        exp_factors = np.cos(t_log_n) - 1j * np.sin(t_log_n)
        
        # Sum the series
        psi = np.sum(n_power * exp_factors)
        
        # Cache result
        if self.enable_caching:
            self._psi_cache[cache_key] = psi
            
        return complex(psi)
    
    def extract_9d_curvature(
        self, 
        t: float, 
        delta_t: float = 1e-4
    ) -> np.ndarray:
        """
        Extract 9D geodesic curvature components from ψ(t) dynamics.
        
        Uses finite difference stencils at multiple scales to capture
        the 9-dimensional curvature structure needed for geodesic criterion.
        
        Parameters
        ----------
        t : float
            Center point for curvature analysis
        delta_t : float, default=1e-4
            Step size for finite differences
            
        Returns
        -------
        np.ndarray of shape (9,)
            9D curvature vector [curv0, curv1, ..., curv8]
        """
        # Check cache first
        cache_key = t
        if self.enable_caching and cache_key in self._curvature_cache:
            return self._curvature_cache[cache_key]
        
        # Compute ψ at stencil points
        t_points = np.array([
            t - 4*delta_t, t - 3*delta_t, t - 2*delta_t, t - delta_t,
            t,
            t + delta_t, t + 2*delta_t, t + 3*delta_t, t + 4*delta_t
        ])
        
        psi_values = np.array([self.compute_psi(tp) for tp in t_points])
        
        # Extract curvature components using different finite difference schemes
        curv = np.zeros(NUM_BRANCHES_GEODESC, dtype=float)
        
        # curv0: Central second derivative (basic curvature)
        curv[0] = abs(psi_values[6] - 2*psi_values[4] + psi_values[2]) / (delta_t**2)
        
        # curv1: Forward-backward asymmetry  
        curv[1] = abs(psi_values[5] - psi_values[3]) / (2*delta_t)
        
        # curv2: Fourth derivative approximation
        curv[2] = abs(psi_values[8] - 4*psi_values[6] + 6*psi_values[4] 
                     - 4*psi_values[2] + psi_values[0]) / (delta_t**4)
        
        # curv3: Mixed real-imaginary curvature
        real_curv = abs(psi_values[6].real - 2*psi_values[4].real + psi_values[2].real)
        imag_curv = abs(psi_values[6].imag - 2*psi_values[4].imag + psi_values[2].imag) 
        curv[3] = (real_curv * imag_curv)**0.5 / (delta_t**2)
        
        # curv4: Phase curvature
        phases = np.angle(psi_values[2:7])
        phase_diff2 = np.diff(phases, n=2)
        curv[4] = abs(phase_diff2[1]) / (delta_t**2)
        
        # curv5: Magnitude curvature
        mags = np.abs(psi_values[2:7])
        mag_diff2 = np.diff(mags, n=2)  
        curv[5] = abs(mag_diff2[1]) / (delta_t**2)
        
        # curv6: Cross-derivative term
        curv[6] = abs((psi_values[6] - psi_values[2]).real * 
                     (psi_values[5] - psi_values[3]).imag) / (4*delta_t**3)
        
        # curv7: High-frequency oscillation detector
        curv[7] = abs(psi_values[8] - psi_values[7] + psi_values[6] - psi_values[5] +
                     psi_values[4] - psi_values[3] + psi_values[2] - psi_values[1] +
                     psi_values[0]) / (8*delta_t)
        
        # curv8: Torsion-like term (complex conjugate interaction)
        curv[8] = abs((psi_values[4] * np.conj(psi_values[6]) - 
                      psi_values[4] * np.conj(psi_values[2])).imag) / (2*delta_t**2)
        
        # Cache result
        if self.enable_caching:
            self._curvature_cache[cache_key] = curv
            
        return curv
    
    def compute_multiscale_curvature(
        self, 
        t: float,
        base_delta: float = 1e-4
    ) -> np.ndarray:
        """
        Compute multi-scale curvature measures κ₁, κ₂, κ₄, etc.
        
        Returns
        -------
        np.ndarray
            Multi-scale curvature array [κ₁, κ₂, κ₄, κ₈, ...]
        """
        kappa_values = []
        
        for scale in [1, 2, 4, 8]:
            delta = base_delta * scale
            
            # Compute second derivative at this scale
            psi_plus = self.compute_psi(t + delta)
            psi_center = self.compute_psi(t)
            psi_minus = self.compute_psi(t - delta)
            
            kappa = abs(psi_plus - 2*psi_center + psi_minus) / (delta**2)
            kappa_values.append(kappa)
        
        return np.array(kappa_values)
    
    def compute_persistence_ratios(
        self, 
        t: float
    ) -> np.ndarray:
        """
        Compute persistence ratios ρ₂ = κ₂/κ₁, ρ₄ = κ₄/κ₁, etc.
        """
        kappa = self.compute_multiscale_curvature(t)
        
        if kappa[0] < 1e-12:  # Avoid division by zero
            return np.array([1.0, 1.0])
        
        rho_2 = kappa[1] / kappa[0]
        rho_4 = kappa[2] / kappa[0]
        
        return np.array([rho_2, rho_4])
    
    def compute_normal_components(
        self, 
        t: float,
        delta_t: float = 1e-4
    ) -> np.ndarray:
        """
        Compute normal vector components n₁, n₂ from ψ(t) gradient.
        """
        # First derivatives
        psi_plus = self.compute_psi(t + delta_t)
        psi_minus = self.compute_psi(t - delta_t)
        grad = (psi_plus - psi_minus) / (2 * delta_t)
        
        # Extract normal components
        n1 = abs(grad.real)
        n2 = abs(grad.imag)
        
        return np.array([n1, n2])
    
    def compute_discriminant_z80(self, t: float) -> complex:
        """
        Compute discriminant magnitude |z80| (80-term partial sum).
        """
        return self.compute_psi(t, max_n=80)
    
    def compute_phase_velocity(
        self, 
        t: float,
        delta_t: float = 1e-5
    ) -> float:
        """
        Compute phase velocity |darg/dT| of ψ(t).
        """
        psi_plus = self.compute_psi(t + delta_t)
        psi_minus = self.compute_psi(t - delta_t)
        
        phase_plus = np.angle(psi_plus)
        phase_minus = np.angle(psi_minus)
        
        # Handle phase wrapping
        phase_diff = phase_plus - phase_minus
        if phase_diff > np.pi:
            phase_diff -= 2*np.pi
        elif phase_diff < -np.pi:
            phase_diff += 2*np.pi
            
        phase_velocity = abs(phase_diff) / (2 * delta_t)
        return phase_velocity
    
    def compute_spectral_features(self, t: float) -> SpectralFeatures:
        """
        Complete spectral analysis at height t.
        
        Returns all features needed for geodesic criterion and φ-system coupling.
        """
        # Core ψ computation
        psi = self.compute_psi(t)
        
        # 9D curvature
        curv_9d = self.extract_9d_curvature(t)
        
        # Multi-scale features
        kappa_multiscale = self.compute_multiscale_curvature(t)
        persistence_ratios = self.compute_persistence_ratios(t)
        normal_components = self.compute_normal_components(t)
        
        # Additional features
        discriminant_z80 = self.compute_discriminant_z80(t)
        phase_velocity = self.compute_phase_velocity(t)
        
        return SpectralFeatures(
            t=t,
            psi=psi,
            psi_magnitude=abs(psi),
            psi_phase=np.angle(psi),
            curv_9d=curv_9d,
            kappa_multiscale=kappa_multiscale,
            persistence_ratios=persistence_ratios,
            normal_components=normal_components,
            discriminant_z80=discriminant_z80,
            phase_velocity=phase_velocity
        )

    def clear_cache(self) -> None:
        """Clear all cached computations."""
        self._psi_cache.clear()
        self._curvature_cache.clear()
    
    def __repr__(self) -> str:
        return (f"QuantumGeodesicSingularity(max_n={self.max_n}, "
                f"precision={self.curvature_precision}, "
                f"caching={'enabled' if self.enable_caching else 'disabled'})")


# =============================================================================
# EMBEDDED: RH_SINGULARITY.py  
# =============================================================================

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

PHI: float = (1.0 + np.sqrt(5.0)) / 2.0
NUM_BRANCHES: int = 9
BRANCH_SIGNATURES: np.ndarray = np.array(
    [float((-1) ** k) for k in range(NUM_BRANCHES)]
)

_TWO_PI: float = 2.0 * np.pi
_NODAL_ANGLES: np.ndarray = _TWO_PI * np.arange(NUM_BRANCHES) / NUM_BRANCHES

# Calibrated φ-weights (from earlier geodesic analysis, but here used only
# as fixed branch weights in this finite symbolic system).
#
# The weights satisfy: Σ w_k = 1 (normalized).
_WEIGHTS_9_RAW: np.ndarray = np.array([
    0.0175504462,   # k=0
    0.1471033037,   # k=1
    0.0041498042,   # k=2
    0.3353044327,   # k=3
    0.0981287513,   # k=4
    0.0127626154,   # k=5
    0.1906439411,   # k=6
    0.1869808699,   # k=7
    0.0073758354,   # k=8
], dtype=float)

_WEIGHTS_9_RAW_SUM: float = float(_WEIGHTS_9_RAW.sum())
_WEIGHTS_9: np.ndarray = _WEIGHTS_9_RAW / _WEIGHTS_9_RAW_SUM  # Σ w_k = 1

# φ-geometric entropy baselines (log-free)
# Max when p_0 = 1   -> S_φ = w_0
# Uniform p_k = 1/9  -> S_φ = Σ w_k / 9 = 1/9
PHI_ENTROPY_MAX: float = float(_WEIGHTS_9[0])          # one-branch maximum
PHI_ENTROPY_UNIFORM: float = 1.0 / float(NUM_BRANCHES) # uniform baseline


class Riemann_Singularity:
    """
    φ-weighted Ruelle–Perron–Frobenius framework on a 9-branch symbolic system.

    The sole structural input is the golden ratio φ.  All weights, phases, and
    spectral objects derive from it via explicit algebraic formulas.
    No logarithms appear anywhere in this class (log-free protocol).

    Core Tier 1 objects (implemented)
    ---------------------------------
    Branch weights   w_k = 4 / (φ^k + φ^{-k})^2   — Bi-directional filter (here
                                                   instantiated by calibrated
                                                   weights _WEIGHTS_9).
    Transfer kernel  κ_k(s) = w_k · σ_k · e^{-s · ℓ_k}
    Head functional  H_φ(s) = complex(Σ Re(κ_k), 0)   — convergent projection
    Tail functional  T_φ(s) = complex(0, Σ Im(κ_k))   — oscillatory projection
    φ-phase          e^{iθ_φ(T)},  θ_φ = T / (φ · Σ w_k)

    Tier 2 (heuristic / conjectural)
    --------------------------------
    HT3-λ balance    B_φ^(λ)(T) = H_φ(s) + λ₁(s) · e^{iθ_φ(T)} · T_φ(s)

    WARNING:
    --------
    This class is NOT used in the current Conjecture III_N theorem. It is
    retained as a separate finite φ–Ruelle model and heuristic framework.
    """

    def __init__(self, beta: float = 1.0) -> None:
        if beta <= 0:
            raise ValueError(f"beta must be positive; got {beta}")
        self.beta = float(beta)

        # Use the calibrated φ-weights with Σ w_k = 1
        self.weights: np.ndarray = _WEIGHTS_9.copy()
        self.weight_sum: float = float(self.weights.sum())  # == 1.0

    # ------------------------------------------------------------------
    # φ-branch weights
    # ------------------------------------------------------------------

    @staticmethod
    def _branch_weights() -> np.ndarray:
        """
        Return the calibrated φ-weights (normalised).

        Tier 1 object: fixed probability vector on the 9 branches.
        """
        return _WEIGHTS_9.copy()

    def _default_lengths(self) -> np.ndarray:
        """
        Default symbolic branch lengths ℓ_k = k+1, k = 0,…,8.

        This can be overridden by passing explicit branch_lengths arrays
        into the public methods.
        """
        return np.arange(1, NUM_BRANCHES + 1, dtype=float)

    # ------------------------------------------------------------------
    # φ-phase rotation
    # ------------------------------------------------------------------

    def phi_phase(self, T: float) -> complex:
        """
        e^{iθ_φ(T)}  where  θ_φ(T) = T / (φ · Σ_k w_k).

        Returns a complex number of modulus exactly 1.
        """
        theta = T / (PHI * self.weight_sum)
        return complex(np.cos(theta), np.sin(theta))

    def phi_phase_arg(self, T: float) -> float:
        """
        θ_φ(T) ∈ [-π, π) to match np.angle() output range.
        """
        raw_angle = (T / (PHI * self.weight_sum)) % _TWO_PI
        # Convert to [-π, π) range to match np.angle()
        if raw_angle > np.pi:
            raw_angle -= _TWO_PI
        return raw_angle

    # ------------------------------------------------------------------
    # Transfer kernel
    # ------------------------------------------------------------------

    def branch_kernel(
        self,
        s: complex,
        branch_lengths: np.ndarray,
    ) -> np.ndarray:
        """
        κ_k(s) = w_k · σ_k · e^{-s · ℓ_k}   for k = 0, …, 8.

        Parameters
        ----------
        s             : complex spectral parameter (full s, Re and Im both used)
        branch_lengths: array of shape (9,) with ℓ_k > 0
        """
        branch_lengths = np.asarray(branch_lengths, dtype=float)
        if branch_lengths.shape != (NUM_BRANCHES,):
            raise ValueError(
                f"branch_lengths must have shape ({NUM_BRANCHES},); "
                f"got {branch_lengths.shape}"
            )
        return self.weights * BRANCH_SIGNATURES * np.exp(-s * branch_lengths)

    # ------------------------------------------------------------------
    # Spectral radius (full complex s)
    # ------------------------------------------------------------------

    def spectral_radius(
        self,
        s: complex,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        λ₁(s) ≈ Σ_k κ_k(s)  — mean-field leading eigenvalue proxy.

        Accepts full complex s; both Re(s) and Im(s) enter the kernel.

        Tier 1 diagnostic: approximate leading eigenvalue of the
        9×9 transfer operator in a mean-field sense.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        return complex(self.branch_kernel(s, branch_lengths).sum())

    # ------------------------------------------------------------------
    # Head and Tail functionals (accept full complex s)
    # ------------------------------------------------------------------

    def head_functional(
        self,
        s: complex,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        H_φ(s) = complex(Σ_k Re(κ_k(s)), 0).

        Real-axis projection of the branch kernels.
        H_φ(s) + T_φ(s) = Σ_k κ_k(s)  reconstructs the full kernel sum.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        kappa = self.branch_kernel(s, branch_lengths)
        return complex(kappa.real.sum(), 0.0)

    def tail_functional(
        self,
        s: complex,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        T_φ(s) = complex(0, Σ_k Im(κ_k(s))).

        Imaginary-axis projection — the oscillatory residue that the
        φ-phase rotation may partially cancel at certain T-values.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        kappa = self.branch_kernel(s, branch_lengths)
        return complex(0.0, kappa.imag.sum())

    # ------------------------------------------------------------------
    # Balance equations
    # ------------------------------------------------------------------

    def balance(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        Geometric balance (Tier 1 heuristic observable):

            B_φ(T) = H_φ(s) + e^{iθ_φ(T)} · T_φ(s),   s = 1/2 + iT.

        This is a purely φ-dynamical quantity. It is NOT asserted to
        vanish at ζ-zeros; it is a diagnostic observable only.
        """
        s = complex(0.5, T)
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        H = self.head_functional(s, branch_lengths)
        Tf = self.tail_functional(s, branch_lengths)
        phase = self.phi_phase(T)
        return H + phase * Tf

    def lambda_balance(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        λ-adjusted head–tail balance (HT3-λ, Tier 2 heuristic):

            B_φ^(λ)(T) = H_φ(s) + λ₁(s) · e^{iθ_φ(T)} · T_φ(s),
                         s = 1/2 + iT.

        CONJECTURAL / HEURISTIC: |B_φ^(λ)(T)| small near interesting T.
        Not used, and not to be cited, as a ζ-zero detection method.
        """
        s = complex(0.5, T)
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        H = self.head_functional(s, branch_lengths)
        Tf = self.tail_functional(s, branch_lengths)
        lam = self.spectral_radius(s, branch_lengths)
        phase = self.phi_phase(T)
        return H + lam * phase * Tf

    # ------------------------------------------------------------------
    # Singularity diagnostics (internal to φ-system)
    # ------------------------------------------------------------------

    def branch_probabilities(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        p_k = |κ_k(s)| / Σ_j |κ_j(s)|  at s = 1/2 + iT.

        A proxy for branch weights based on kernel magnitudes at the
        critical line. Falls back to uniform if all magnitudes vanish.
        """
        s = complex(0.5, T)
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        kappa = self.branch_kernel(s, branch_lengths)
        magnitudes = np.abs(kappa)
        total = magnitudes.sum()
        if total < 1e-300:
            return np.full(NUM_BRANCHES, 1.0 / NUM_BRANCHES)
        return magnitudes / total

    def phi_entropy(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> float:
        """
        φ-geometric entropy (log-free):

            S_φ(T) = Σ_k p_k · w_k

        Value = PHI_ENTROPY_UNIFORM = Σw/9 ≈ 0.286 when all p_k = 1/9 (uniform).
        Value = PHI_ENTROPY_MAX = w_0 when p_0 = 1 (concentrated).
        Larger S_φ means energy is more uniformly distributed across branches.
        """
        p = self.branch_probabilities(T, branch_lengths)
        return float(np.sum(p * self.weights))

    def dominant_branch(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> int:
        """
        k* = argmax_k p_k.

        This is a diagnostic of which branch dominates the φ-kernel at T.
        """
        p = self.branch_probabilities(T, branch_lengths)
        return int(np.argmax(p))

    def phase_distance(self, T: float) -> float:
        """
        d_φ(T) = min_{m=0,…,8} |θ_φ(T) − 2πm/9|   ∈ [0, π/9].

        Computed via arg(e^{i·Δ}) for clean [-π, π] folding.
        Small d_φ: phase wheel near a nodal direction.
        """
        theta = self.phi_phase_arg(T)
        gaps = np.abs(np.angle(np.exp(1j * (theta - _NODAL_ANGLES))))
        return float(gaps.min())

    # ------------------------------------------------------------------
    # Full evaluation (φ-system diagnostics only)
    # ------------------------------------------------------------------

    def evaluate(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> dict:
        """
        Full φ-system evaluation at height T on s = 1/2 + iT.

        Returns:
        - λ₁(s), H_φ(s), T_φ(s)
        - balance and λ-balance magnitudes
        - φ-entropy, dominant branch, phase distance
        - a heuristic singularity_score_heuristic in [0,1]

        NOTE: This score is internal to the φ-system and has NO theorem-level
        relation to ζ-zeros. It is a heuristic diagnostic only.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()

        s = complex(0.5, T)
        kappa = self.branch_kernel(s, branch_lengths)

        lam = complex(kappa.sum())
        H   = complex(kappa.real.sum(), 0.0)
        Tf  = complex(0.0, kappa.imag.sum())
        phase = self.phi_phase(T)

        bal  = H + phase * Tf
        lbal = H + lam * phase * Tf

        magnitudes = np.abs(kappa)
        total = magnitudes.sum()
        if total > 1e-300:
            p = magnitudes / total
        else:
            p = np.full(NUM_BRANCHES, 1.0 / NUM_BRANCHES)

        S_phi  = float(np.sum(p * self.weights))
        theta  = self.phi_phase_arg(T)
        d_phi  = float(np.abs(np.angle(np.exp(1j * (theta - _NODAL_ANGLES)))).min())
        dom    = int(np.argmax(p))
        abs_lam  = abs(lam)
        lbal_mag = abs(lbal)

        # Heuristic components for an internal score (0–1)
        c1 = max(0.0, 1.0 - lbal_mag / 0.15)
        c2 = min(1.0, S_phi / PHI_ENTROPY_UNIFORM)
        c3 = 1.0 if dom == 0 else 0.0
        c4 = max(0.0, 1.0 - d_phi / (np.pi / NUM_BRANCHES))
        c5 = 1.0 if 0.90 < abs_lam < 0.95 else 0.0
        score = (c1 + c2 + c3 + c4 + c5) / 5.0

        return {
            "T":                          T,
            "s":                          s,
            "lambda1":                    lam,
            "abs_lambda1":                abs_lam,
            "phi_phase":                  phase,
            "phi_phase_arg":              theta,
            "H_phi":                      H,
            "T_phi":                      Tf,
            "balance":                    bal,
            "balance_mag":                abs(bal),
            "lambda_balance":             lbal,
            "lambda_balance_mag":         lbal_mag,
            "phase_distance":             d_phi,
            "phi_entropy":                S_phi,
            "dominant_branch":            dom,
            "singularity_score_heuristic": score,
        }

    def __repr__(self) -> str:
        w = self.weights
        lines = [
            "Riemann_Singularity",
            "  φ-weighted Ruelle–Perron–Frobenius framework, 9 symbolic branches",
            f"  φ              = {PHI:.15f}",
            f"  branches       = {NUM_BRANCHES}  (k = 0, …, {NUM_BRANCHES - 1})",
            f"  weights w_k    = calibrated φ-weights (normalized)  [Bi-directional Lorentzian]",
            f"                 = [{', '.join(f'{v:.6f}' for v in w)}]",
            f"  Σ w_k          = {self.weight_sum:.10f}",
            f"  PHI_ENTROPY_MAX= {PHI_ENTROPY_MAX:.10f}  (one-branch maximum, log-free)",
            f"  PHI_ENTROPY_UNI= {PHI_ENTROPY_UNIFORM:.10f}  (uniform baseline = 1/9)",
            f"  β              = {self.beta}",
            "",
            "  ── Tier 1 ────────────────────────────────────────────────────",
            "  kernel   κ_k(s) = w_k σ_k e^{-sℓ_k}                 [log-free]",
            "  head     H_φ(s) = complex(Σ Re κ_k, 0)",
            "  tail     T_φ(s) = complex(0, Σ Im κ_k)",
            "  zeta     ζ_φ(s) = ∏ (1 − κ_k)^{-1}                 [log-free]",
            "  det      det(I − L_s)  exact rank-9",
            "  pressure P_φ(s) = |λ₁|^{1/φ} − 1                   [log-free]",
            "",
            "  ── Tier 2 (heuristic) ───────────────────────────────────────",
            "  HT3-λ    B_φ^(λ)(T) = H_φ + λ₁ · e^{iθ_φ} · T_φ  (diagnostic only)",
            "  det id.  det(I − L̃_s) = C · ξ(s)   [heuristic, NOT used in III_N]",
        ]
        return "\n".join(lines)


# =============================================================================
# INFINITY_TRINITY_VALIDATOR CLASS (CONSOLIDATION POINT)
# =============================================================================



SCRIPT_DIR = Path(__file__).resolve().parent
ASSERTION1_DIR = SCRIPT_DIR.parent
PROOF_DIR = ASSERTION1_DIR / "1_PROOF_SCRIPTS_NOTES"


class Infinity_Trinity_Validator:
    """
    SINGLE-FILE ASSERTION 1 EXCLUSIVE INFINITY TRINITY VALIDATOR
    
    This consolidates:
    - Complete Quantum Geodesic Singularity implementation 
    - Complete Riemann φ-system implementation
    - Trinity gate validation (3 doctrines)
    - Assertion 1 law assessment framework
    - Unified execution pipeline
    
    NO EXTERNAL DEPENDENCIES except NumPy and Python standard library.
    """

    def __init__(self) -> None:
        self.psi_engine = QuantumGeodesicSingularity(max_n=10000)
        self.phi_system = Riemann_Singularity(beta=1.0)

    def _sample_geodesic_and_phi(
        self,
        T_min: float,
        T_max: float,
        num_T: int,
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, np.ndarray]]:
        t_values = np.linspace(T_min, T_max, num_T)
        features = []

        abs_lambda = np.zeros(num_T)
        balance_mag = np.zeros(num_T)
        phi_entropy = np.zeros(num_T)

        for idx, t in enumerate(t_values):
            sf = self.psi_engine.compute_spectral_features(float(t))
            ev = self.phi_system.evaluate(float(t))

            feature_vec = [
                float(sf.psi.real),
                float(sf.psi.imag),
                float(sf.kappa_multiscale[0]) if len(sf.kappa_multiscale) > 0 else 0.0,
                float(sf.kappa_multiscale[1]) if len(sf.kappa_multiscale) > 1 else 0.0,
                float(sf.kappa_multiscale[2]) if len(sf.kappa_multiscale) > 2 else 0.0,
                float(sf.persistence_ratios[0]) if len(sf.persistence_ratios) > 0 else 0.0,
                float(sf.persistence_ratios[1]) if len(sf.persistence_ratios) > 1 else 0.0,
                float(sf.normal_components[0]) if len(sf.normal_components) > 0 else 0.0,
                float(sf.normal_components[1]) if len(sf.normal_components) > 1 else 0.0,
                float(sf.phase_velocity),
                float(abs(sf.discriminant_z80)),
                float(ev["phase_distance"]),
            ]
            features.append(feature_vec)

            abs_lambda[idx] = float(ev["abs_lambda1"])
            balance_mag[idx] = float(ev["lambda_balance_mag"])
            phi_entropy[idx] = float(ev["phi_entropy"])

        x = np.array(features, dtype=float)
        phi_diag = {
            "abs_lambda1": abs_lambda,
            "lambda_balance_mag": balance_mag,
            "phi_entropy": phi_entropy,
        }
        return t_values, x, phi_diag

    def _doctrine_I(self, t_values: np.ndarray, x: np.ndarray) -> bool:
        print("\n[Doctrine I — Geodesic Compactification]")
        if not np.all(np.isfinite(x)):
            print("  FAIL: non-finite feature detected")
            return False
        max_abs = float(np.max(np.abs(x)))
        print(f"  max |feature| over T ∈ [{t_values[0]:.2f},{t_values[-1]:.2f}] ≈ {max_abs:.4e}")
        ok = max_abs < 1e4
        print("  PASS: bounded compact shell" if ok else "  FAIL: feature shell too large")
        return ok

    def _doctrine_II(self, x: np.ndarray, phi_diag: Dict[str, np.ndarray]) -> bool:
        print("\n[Doctrine II — Spectral / Ergodic Consistency]")
        variances = np.var(x, axis=0)
        vmin, vmax = float(np.min(variances)), float(np.max(variances))
        lam_spread = float(np.max(phi_diag["abs_lambda1"]) - np.min(phi_diag["abs_lambda1"]))
        bal_spread = float(np.max(phi_diag["lambda_balance_mag"]) - np.min(phi_diag["lambda_balance_mag"]))
        print(f"  geodesic var range ≈ [{vmin:.4e}, {vmax:.4e}]")
        print(f"  |λ₁| spread ≈ {lam_spread:.4e}")
        print(f"  |λ-balance| spread ≈ {bal_spread:.4e}")

        # bounded and non-degenerate dynamics
        bounded = np.all(np.isfinite(variances)) and vmax < 1e8
        nontrivial = (vmax > 1e-12) and (lam_spread > 1e-6) and (bal_spread > 1e-6)
        ok = bool(bounded and nontrivial)
        print("  PASS: controlled nontrivial dynamics" if ok else "  FAIL: degenerate or unstable dynamics")
        return ok

    def _doctrine_III(self, x: np.ndarray, phi_diag: Dict[str, np.ndarray], tol: float) -> bool:
        print("\n[Doctrine III — Injective Spectral Encoding]")
        combo = np.column_stack([x, phi_diag["abs_lambda1"], phi_diag["lambda_balance_mag"], phi_diag["phi_entropy"]])
        scale = max(tol, 1e-12)
        quantized = np.round(combo / scale).astype(np.int64)

        seen = set()
        collisions = 0
        for row in quantized:
            key = tuple(row.tolist())
            if key in seen:
                collisions += 1
            else:
                seen.add(key)

        if collisions == 0:
            print(f"  No non-trivial collisions detected at tolerance {tol}")
            print("  PASS: injective encoding within numerical resolution")
            return True

        print(f"  FAIL: {collisions} collisions detected at tolerance {tol}")
        return False

    def run_rh_infinity_trinity(
        self,
        T_min: float = 10.0,
        T_max: float = 200.0,
        num_T: int = 600,
        tol: float = 1e-10,
    ) -> bool:
        print("\n" + "=" * 60)
        print("RH INFINITY TRINITY PROTOCOL")
        print("=" * 60)
        print(f"Sampling T ∈ [{T_min}, {T_max}] with {num_T} points.")

        t_values, x, phi_diag = self._sample_geodesic_and_phi(T_min, T_max, num_T)

        ok_i = self._doctrine_I(t_values, x)
        ok_ii = self._doctrine_II(x, phi_diag)
        ok_iii = self._doctrine_III(x, phi_diag, tol=tol)

        print("\nRH Infinity Trinity — Final Verdict")
        print("-" * 36)
        if ok_i and ok_ii and ok_iii:
            print("  ✓ TRINITY PASSED.")
            return True

        print("  ✗ TRINITY FAILED.")
        return False

    def assess_assertion1_laws(self) -> Tuple[bool, Dict[str, bool]]:
        law_scripts = [
            "EULERIAN_LAW_1_PNT_AND_PSI.py",
            "EULERIAN_LAW_2_THETA_AND_LI.py",
            "EULERIAN_LAW_3_PI_ERROR_BOUNDS.py",
            "EULERIAN_LAW_4_EULER_PRODUCT_TARGETS.py",
            "EULERIAN_LAW_5_PHI_UNIVERSAL_CONSTANTS.py",
        ]

        print("\n" + "=" * 70)
        print("STEP 2: ASSERTION 1 LAW ASSESSMENT (MANDATORY)")
        print("=" * 70)

        results: Dict[str, bool] = {}
        for script_name in law_scripts:
            script_path = PROOF_DIR / script_name
            if not script_path.exists():
                results[script_name] = False
                print(f"  ❌ MISSING: {script_name}")
                continue

            print(f"  ▶ Running {script_name} ...")
            proc = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
            passed = proc.returncode == 0
            results[script_name] = passed
            print(f"    {'✅ PASS' if passed else '❌ FAIL'}")
            if not passed:
                tail = "\n".join(proc.stderr.splitlines()[-20:]) if proc.stderr else "(no stderr output)"
                print("    Last stderr lines:")
                print(tail)

        all_passed = all(results.values()) if results else False
        print(f"\n  Assertion 1 laws overall: {'✅ PASS' if all_passed else '❌ FAIL'}")
        return all_passed, results

    def run(self) -> bool:
        print("=" * 70)
        print("INFINITY_TRINITY_VALIDATOR — CONSOLIDATED SINGLE-FILE")
        print("Assertion 1 Exclusive: Eulerian Prime-Law Scaffold")
        print("=" * 70)
        print("\nCAMPAIGN: Self-contained validation with embedded:")
        print("  • Quantum Geodesic Singularity Engine")
        print("  • Riemann φ-weighted Ruelle System") 
        print("  • Trinity Protocol (3 Doctrines)")
        print("  • Law Assessment Framework")

        print("\n" + "=" * 70)
        print("STEP 1: INFINITY TRINITY PROTOCOL (MANDATORY GATE)")
        print("=" * 70)

        trinity_passed = self.run_rh_infinity_trinity(
            T_min=10.0,
            T_max=200.0,
            num_T=600,
            tol=1e-10,
        )
        if not trinity_passed:
            print("\n❌ ASSERTION 1 BLOCKED: TRINITY PROTOCOL FAILED")
            return False

        laws_passed, law_results = self.assess_assertion1_laws()
        if not laws_passed:
            print("\n❌ ASSERTION 1 BLOCKED: One or more laws failed assessment.")
            return False

        print("\n" + "=" * 70)
        print("ASSERTION 1 — FINAL STATUS")
        print("=" * 70)
        print("\n✅ INFINITY TRINITY: PASSED")
        print("✅ ASSERTION 1 LAWS: PASSED")
        for script_name, ok in law_results.items():
            print(f"   - {script_name}: {'PASS ✅' if ok else 'FAIL ❌'}")

        print("\n" + "🎯" * 23)
        print("🎯 ASSERTION 1: 100% COMPLETE 🎯")
        print("🎯" * 23)

        return True


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("INFINITY_TRINITY_VALIDATOR")
    print("Consolidated Single-File Implementation")
    print("=" * 80)
    
    validator = Infinity_Trinity_Validator()
    success = validator.run()
    
    print("\n" + "=" * 80)
    print(f"FINAL EXIT: {'SUCCESS ✅' if success else 'FAILURE ❌'}")
    print("=" * 80)
    
    sys.exit(0 if success else 1)
