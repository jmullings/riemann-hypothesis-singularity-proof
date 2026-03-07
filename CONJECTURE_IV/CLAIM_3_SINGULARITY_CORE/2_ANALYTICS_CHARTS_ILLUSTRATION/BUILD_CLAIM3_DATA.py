"""
BUILD_CLAIM3_DATA.py
====================

Build CSV data for Claim 3: Singularity Core Mechanism Architecture

This script analyzes the ψ(T) partial sum chain and 9D geodesic curvature
structure at Riemann zeros and non-zeros to demonstrate:

1. ψ(T) magnitude profiles - vector collapse at zeros
2. 9D curvature component analysis 
3. Geodesic criterion performance (precision/recall)
4. Phase velocity and persistence ratio analysis
5. Discriminant |z80| distribution

Outputs CSV files for publication-quality figure generation.

VECTORIZED IMPLEMENTATION: ~100x speedup over loop-based version.

Author: CLAIM_3_SINGULARITY_CORE Analytics
Date: March 2026
"""

from __future__ import annotations

import numpy as np
import csv
import os
import sys
import time
from typing import List, Tuple, Dict
from dataclasses import dataclass
from scipy import stats
import logging

# Add parent directory to path for importing proof scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROOF_SCRIPTS_DIR = os.path.join(SCRIPT_DIR, "..", "1_PROOF_SCRIPTS_NOTES")
sys.path.insert(0, PROOF_SCRIPTS_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

PHI: float = (1.0 + np.sqrt(5.0)) / 2.0
LOG_PHI: float = np.log(PHI)
NUM_BRANCHES: int = 9

# First 100 Riemann zeros (Odlyzko)
RIEMANN_ZEROS = np.array([
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005150, 49.773832,
    52.970321, 56.446247, 59.347044, 60.831778, 65.112544,
    67.079810, 69.546401, 72.067157, 75.704690, 77.144840,
    79.337375, 82.910381, 84.735493, 87.425274, 88.809111,
    92.491899, 94.651344, 95.870634, 98.831194, 101.317851,
    103.725538, 105.446623, 107.168611, 111.029535, 111.874659,
    114.320220, 116.226680, 118.790782, 121.370125, 122.946829,
    124.256818, 127.516683, 129.578704, 131.087688, 133.497737,
    134.756509, 138.116042, 139.736208, 141.123707, 143.111846,
    146.000982, 147.422765, 150.053520, 150.925257, 153.024693,
    156.112909, 157.597591, 158.849988, 161.188964, 163.030709,
    165.537069, 167.184439, 169.094515, 169.911976, 173.411536,
    174.754191, 176.441434, 178.377407, 179.916484, 182.207078,
    184.874467, 185.598783, 187.228922, 189.416158, 192.026656,
    193.079726, 195.265396, 196.876481, 198.015310, 201.264751,
    202.493594, 204.189671, 205.394697, 207.906258, 209.576509,
    211.690862, 213.347919, 214.547044, 216.169538, 219.067596,
    220.714918, 221.430705, 224.007000, 224.983324, 227.421444,
    229.337413, 231.250188, 231.987235, 233.693404, 236.524230,
])

# Non-zero T values for comparison (midpoints between zeros)
NON_ZEROS = (RIEMANN_ZEROS[:-1] + RIEMANN_ZEROS[1:]) / 2

# Output directory
OUTPUT_DIR = "csv_data"

# Analysis parameters
PSI_MAX_N: int = 10000  # Terms in partial sum
SIGMA_RANGE = np.linspace(0.1, 0.9, 81)  # For profile plots
DELTA_T: float = 1e-4  # Step size for derivatives

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AnalysisResults:
    """Complete analysis results for CSV export."""
    psi_profiles: List[Dict]
    magnitude_at_zeros: List[Dict]
    curvature_9d: List[Dict]
    geodesic_criterion: List[Dict]
    phase_velocity: List[Dict]
    persistence_ratios: List[Dict]
    z80_discriminant: List[Dict]

# ============================================================================
# VECTORIZED PSI COMPUTATION
# ============================================================================

# Precompute logarithms once
_LOG_N_CACHE: np.ndarray = None
_N_POWER_CACHE: np.ndarray = None

def _initialize_caches(max_n: int):
    """Initialize precomputed arrays for vectorized ψ computation."""
    global _LOG_N_CACHE, _N_POWER_CACHE
    if _LOG_N_CACHE is None or len(_LOG_N_CACHE) < max_n:
        n = np.arange(1, max_n + 1)
        _LOG_N_CACHE = np.log(n)
        _N_POWER_CACHE = 1.0 / np.sqrt(n)

def compute_psi_vectorized(T_values: np.ndarray, max_n: int = PSI_MAX_N) -> np.ndarray:
    """
    Compute ψ(T) = Σ n^(-1/2) e^(-iT·ln n) for multiple T values.
    
    VECTORIZED: Computes all T values simultaneously.
    
    Parameters
    ----------
    T_values : np.ndarray
        Array of T values (heights)
    max_n : int
        Number of terms in partial sum
        
    Returns
    -------
    np.ndarray
        Complex array of ψ values, shape (len(T_values),)
    """
    _initialize_caches(max_n)
    
    log_n = _LOG_N_CACHE[:max_n]     # Shape: (max_n,)
    n_power = _N_POWER_CACHE[:max_n]  # Shape: (max_n,)
    
    # Broadcasting: T_values[:, None] @ log_n[None, :] -> (num_T, max_n)
    T = T_values[:, None]  # Shape: (num_T, 1)
    t_log_n = T * log_n    # Shape: (num_T, max_n)
    
    # Complex exponential
    exp_factors = np.exp(-1j * t_log_n)  # Shape: (num_T, max_n)
    
    # Weighted sum along n axis
    psi = np.sum(n_power * exp_factors, axis=1)  # Shape: (num_T,)
    
    return psi

def compute_psi_at_sigma_T(sigma_values: np.ndarray, T: float, max_n: int = PSI_MAX_N) -> np.ndarray:
    """
    Compute ψ(σ + iT) for varying σ at fixed T.
    
    This demonstrates the σ-profile of the partial sum magnitude.
    
    Returns
    -------
    np.ndarray
        Complex array of ψ values at each σ
    """
    _initialize_caches(max_n)
    
    log_n = _LOG_N_CACHE[:max_n]
    n = np.arange(1, max_n + 1)
    
    # For each σ: ψ(σ + iT) = Σ n^(-σ) e^(-iT·ln n)
    sigma = sigma_values[:, None]  # Shape: (num_sigma, 1)
    
    # n^(-σ) for all σ and n
    n_power_sigma = n[None, :] ** (-sigma)  # Shape: (num_sigma, max_n)
    
    # e^(-iT·ln n) - same for all σ
    exp_factors = np.exp(-1j * T * log_n)  # Shape: (max_n,)
    
    # Sum
    psi = np.sum(n_power_sigma * exp_factors, axis=1)  # Shape: (num_sigma,)
    
    return psi

# ============================================================================
# VECTORIZED 9D CURVATURE
# ============================================================================

def compute_9d_curvature_vectorized(T_values: np.ndarray, delta_t: float = DELTA_T) -> np.ndarray:
    """
    Extract 9D geodesic curvature for multiple T values.
    
    Uses finite difference stencils at multiple scales.
    
    Returns
    -------
    np.ndarray
        Shape (len(T_values), 9) curvature matrix
    """
    num_T = len(T_values)
    curvature = np.zeros((num_T, NUM_BRANCHES), dtype=float)
    
    # Compute ψ at stencil points for all T
    # Stencil: T - 4h, T - 3h, T - 2h, T - h, T, T + h, T + 2h, T + 3h, T + 4h
    offsets = np.array([-4, -3, -2, -1, 0, 1, 2, 3, 4]) * delta_t
    
    # Create grid of all evaluation points
    T_grid = T_values[:, None] + offsets[None, :]  # Shape: (num_T, 9)
    T_flat = T_grid.flatten()
    
    # Compute ψ at all points
    psi_flat = compute_psi_vectorized(T_flat)
    psi_stencil = psi_flat.reshape(num_T, 9)  # Shape: (num_T, 9)
    
    # Extract curvature components (indices: 0,1,2,3,4,5,6,7,8 -> -4h,...,+4h)
    # curv0: Central second derivative
    curvature[:, 0] = np.abs(psi_stencil[:, 6] - 2*psi_stencil[:, 4] + psi_stencil[:, 2]) / (delta_t**2)
    
    # curv1: Forward-backward asymmetry
    curvature[:, 1] = np.abs(psi_stencil[:, 5] - psi_stencil[:, 3]) / (2*delta_t)
    
    # curv2: Fourth derivative
    curvature[:, 2] = np.abs(psi_stencil[:, 8] - 4*psi_stencil[:, 6] + 6*psi_stencil[:, 4] 
                            - 4*psi_stencil[:, 2] + psi_stencil[:, 0]) / (delta_t**4)
    
    # curv3: Mixed real-imaginary
    real_curv = np.abs(psi_stencil[:, 6].real - 2*psi_stencil[:, 4].real + psi_stencil[:, 2].real)
    imag_curv = np.abs(psi_stencil[:, 6].imag - 2*psi_stencil[:, 4].imag + psi_stencil[:, 2].imag)
    curvature[:, 3] = np.sqrt(real_curv * imag_curv) / (delta_t**2)
    
    # curv4: Phase curvature
    phases = np.angle(psi_stencil[:, 2:7])  # Shape: (num_T, 5)
    phase_diff1 = np.diff(phases, axis=1)
    # Handle phase wrapping
    phase_diff1 = np.where(phase_diff1 > np.pi, phase_diff1 - 2*np.pi, phase_diff1)
    phase_diff1 = np.where(phase_diff1 < -np.pi, phase_diff1 + 2*np.pi, phase_diff1)
    phase_diff2 = np.diff(phase_diff1, axis=1)
    curvature[:, 4] = np.abs(phase_diff2[:, 1]) / (delta_t**2)
    
    # curv5: Magnitude curvature
    mags = np.abs(psi_stencil[:, 2:7])
    mag_diff2 = np.diff(np.diff(mags, axis=1), axis=1)
    curvature[:, 5] = np.abs(mag_diff2[:, 1]) / (delta_t**2)
    
    # curv6: Cross-derivative
    curvature[:, 6] = np.abs((psi_stencil[:, 6] - psi_stencil[:, 2]).real * 
                            (psi_stencil[:, 5] - psi_stencil[:, 3]).imag) / (4*delta_t**3)
    
    # curv7: High-frequency oscillation
    curvature[:, 7] = np.abs(np.sum(psi_stencil * np.array([1,-1,1,-1,1,-1,1,-1,1]), axis=1)) / (8*delta_t)
    
    # curv8: Torsion-like
    curvature[:, 8] = np.abs((psi_stencil[:, 4] * np.conj(psi_stencil[:, 6]) - 
                             psi_stencil[:, 4] * np.conj(psi_stencil[:, 2])).imag) / (2*delta_t**2)
    
    return curvature

# ============================================================================
# VECTORIZED SPECTRAL FEATURES
# ============================================================================

def compute_phase_velocity_vectorized(T_values: np.ndarray, delta_t: float = 1e-5) -> np.ndarray:
    """Compute |darg/dT| for multiple T values."""
    T_plus = T_values + delta_t
    T_minus = T_values - delta_t
    
    psi_plus = compute_psi_vectorized(T_plus)
    psi_minus = compute_psi_vectorized(T_minus)
    
    phase_plus = np.angle(psi_plus)
    phase_minus = np.angle(psi_minus)
    
    phase_diff = phase_plus - phase_minus
    # Handle wrapping
    phase_diff = np.where(phase_diff > np.pi, phase_diff - 2*np.pi, phase_diff)
    phase_diff = np.where(phase_diff < -np.pi, phase_diff + 2*np.pi, phase_diff)
    
    return np.abs(phase_diff) / (2 * delta_t)

def compute_z80_discriminant_vectorized(T_values: np.ndarray) -> np.ndarray:
    """Compute |z80| discriminant for multiple T values."""
    return np.abs(compute_psi_vectorized(T_values, max_n=80))

def compute_persistence_ratios_vectorized(T_values: np.ndarray, base_delta: float = DELTA_T) -> np.ndarray:
    """
    Compute persistence ratios ρ₂ = κ₂/κ₁, ρ₄ = κ₄/κ₁.
    
    Returns
    -------
    np.ndarray
        Shape (len(T_values), 2) with [ρ₂, ρ₄] for each T
    """
    num_T = len(T_values)
    scales = [1, 2, 4]
    kappa = np.zeros((num_T, len(scales)))
    
    psi_center = compute_psi_vectorized(T_values)
    
    for i, scale in enumerate(scales):
        delta = base_delta * scale
        psi_plus = compute_psi_vectorized(T_values + delta)
        psi_minus = compute_psi_vectorized(T_values - delta)
        kappa[:, i] = np.abs(psi_plus - 2*psi_center + psi_minus) / (delta**2)
    
    # Avoid division by zero
    kappa_1 = np.where(kappa[:, 0] < 1e-12, 1e-12, kappa[:, 0])
    
    rho_2 = kappa[:, 1] / kappa_1
    rho_4 = kappa[:, 2] / kappa_1
    
    return np.column_stack([rho_2, rho_4])

# ============================================================================
# GEODESIC CRITERION
# ============================================================================

# Coefficients from logistic regression (see RH_SINGULARITY.py)
GEODESIC_COEF = np.array([2.5118, -2.2895, 1.0069, 0.7535, 0.3666, 0.2583])
GEODESIC_THRESHOLD = 6.1422
GEODESIC_MEAN = np.array([0.0, 0.5, 1.0, 0.17, 0.04, 0.27])
GEODESIC_STD = np.array([0.35, 0.38, 0.67, 0.37, 0.20, 0.05])

def apply_geodesic_criterion_vectorized(
    darg_dt: np.ndarray,
    z80_abs: np.ndarray,
    rho4: np.ndarray,
    curv_9d: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply geodesic zero criterion to multiple T values.
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (is_zero_predicted, criterion_score) for each T
    """
    # Determine dominant branch (k=6 indicator)
    is_k6 = (np.argmax(curv_9d[:, 3:8], axis=1) == 3).astype(float)  # k=6 is index 3 in [3,4,5,6,7]
    
    # curv6 - curv7 difference
    curv67_diff = curv_9d[:, 6] - curv_9d[:, 7]
    
    # κ₄ from curvature matrix (curv2 approximates this)
    kappa4 = curv_9d[:, 2] * (DELTA_T**2)  # Rescale
    
    # Build feature matrix
    features = np.column_stack([darg_dt, z80_abs, rho4, is_k6, curv67_diff, kappa4])
    
    # Standardize
    features_std = (features - GEODESIC_MEAN) / GEODESIC_STD
    
    # Compute criterion score
    score = np.sum(features_std * GEODESIC_COEF, axis=1)
    
    is_zero_pred = score > GEODESIC_THRESHOLD
    
    return is_zero_pred, score

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_psi_profiles(zeros: np.ndarray, non_zeros: np.ndarray) -> List[Dict]:
    """
    Analysis 1: ψ(σ + iT) magnitude profiles.
    
    Demonstrates vector collapse at zeros vs extended values off-zeros.
    """
    logger.info("Analyzing ψ(T) profiles...")
    
    results = []
    
    # Sample a few T values from each category
    sample_zeros = zeros[:5]
    sample_non_zeros = non_zeros[:5]
    
    for T in sample_zeros:
        psi_values = compute_psi_at_sigma_T(SIGMA_RANGE, T)
        for i, sigma in enumerate(SIGMA_RANGE):
            results.append({
                'T': T,
                'sigma': sigma,
                'abs_psi': np.abs(psi_values[i]),
                'is_zero': True
            })
    
    for T in sample_non_zeros:
        psi_values = compute_psi_at_sigma_T(SIGMA_RANGE, T)
        for i, sigma in enumerate(SIGMA_RANGE):
            results.append({
                'T': T,
                'sigma': sigma,
                'abs_psi': np.abs(psi_values[i]),
                'is_zero': False
            })
    
    return results

def analyze_magnitude_at_zeros(zeros: np.ndarray, non_zeros: np.ndarray) -> List[Dict]:
    """
    Analysis 2: |ψ(T)| at zeros vs non-zeros.
    """
    logger.info("Analyzing |ψ(T)| distribution...")
    
    all_T = np.concatenate([zeros, non_zeros])
    is_zero = np.concatenate([np.ones(len(zeros), dtype=bool), np.zeros(len(non_zeros), dtype=bool)])
    
    psi_values = compute_psi_vectorized(all_T)
    magnitudes = np.abs(psi_values)
    
    results = []
    for i, T in enumerate(all_T):
        results.append({
            'T': T,
            'abs_psi': magnitudes[i],
            'is_zero': is_zero[i]
        })
    
    return results

def analyze_9d_curvature(zeros: np.ndarray, non_zeros: np.ndarray) -> List[Dict]:
    """
    Analysis 3: 9D curvature component comparison.
    """
    logger.info("Analyzing 9D curvature (vectorized)...")
    
    all_T = np.concatenate([zeros, non_zeros])
    is_zero = np.concatenate([np.ones(len(zeros), dtype=bool), np.zeros(len(non_zeros), dtype=bool)])
    
    curvature = compute_9d_curvature_vectorized(all_T)
    
    results = []
    for i, T in enumerate(all_T):
        for k in range(NUM_BRANCHES):
            results.append({
                'T': T,
                'k': k,
                'curvature': curvature[i, k],
                'is_zero': is_zero[i]
            })
    
    return results

def analyze_geodesic_criterion(zeros: np.ndarray, non_zeros: np.ndarray) -> List[Dict]:
    """
    Analysis 4: Geodesic criterion performance.
    """
    logger.info("Analyzing geodesic criterion (vectorized)...")
    
    all_T = np.concatenate([zeros, non_zeros])
    is_zero_true = np.concatenate([np.ones(len(zeros), dtype=bool), np.zeros(len(non_zeros), dtype=bool)])
    
    # Compute all features
    darg_dt = compute_phase_velocity_vectorized(all_T)
    z80_abs = compute_z80_discriminant_vectorized(all_T)
    persistence = compute_persistence_ratios_vectorized(all_T)
    rho4 = persistence[:, 1]
    curvature = compute_9d_curvature_vectorized(all_T)
    
    # Apply criterion
    is_zero_pred, scores = apply_geodesic_criterion_vectorized(darg_dt, z80_abs, rho4, curvature)
    
    results = []
    for i, T in enumerate(all_T):
        results.append({
            'T': T,
            'is_zero_true': is_zero_true[i],
            'is_zero_predicted': is_zero_pred[i],
            'criterion_score': scores[i],
            'darg_dt': darg_dt[i],
            'z80_abs': z80_abs[i],
            'rho4': rho4[i]
        })
    
    return results

def analyze_phase_velocity(zeros: np.ndarray, non_zeros: np.ndarray) -> List[Dict]:
    """
    Analysis 5: Phase velocity |darg/dT| distribution.
    """
    logger.info("Analyzing phase velocity (vectorized)...")
    
    all_T = np.concatenate([zeros, non_zeros])
    is_zero = np.concatenate([np.ones(len(zeros), dtype=bool), np.zeros(len(non_zeros), dtype=bool)])
    
    phase_vel = compute_phase_velocity_vectorized(all_T)
    
    results = []
    for i, T in enumerate(all_T):
        results.append({
            'T': T,
            'phase_velocity': phase_vel[i],
            'is_zero': is_zero[i]
        })
    
    return results

def analyze_persistence_ratios(zeros: np.ndarray, non_zeros: np.ndarray) -> List[Dict]:
    """
    Analysis 6: Persistence ratios ρ₂, ρ₄.
    """
    logger.info("Analyzing persistence ratios (vectorized)...")
    
    all_T = np.concatenate([zeros, non_zeros])
    is_zero = np.concatenate([np.ones(len(zeros), dtype=bool), np.zeros(len(non_zeros), dtype=bool)])
    
    persistence = compute_persistence_ratios_vectorized(all_T)
    
    results = []
    for i, T in enumerate(all_T):
        results.append({
            'T': T,
            'rho2': persistence[i, 0],
            'rho4': persistence[i, 1],
            'is_zero': is_zero[i]
        })
    
    return results

def analyze_z80_discriminant(zeros: np.ndarray, non_zeros: np.ndarray) -> List[Dict]:
    """
    Analysis 7: |z80| discriminant distribution.
    """
    logger.info("Analyzing |z80| discriminant (vectorized)...")
    
    all_T = np.concatenate([zeros, non_zeros])
    is_zero = np.concatenate([np.ones(len(zeros), dtype=bool), np.zeros(len(non_zeros), dtype=bool)])
    
    z80 = compute_z80_discriminant_vectorized(all_T)
    
    results = []
    for i, T in enumerate(all_T):
        results.append({
            'T': T,
            'z80_abs': z80[i],
            'is_zero': is_zero[i]
        })
    
    return results

# ============================================================================
# CSV EXPORT
# ============================================================================

def ensure_output_dir():
    """Ensure output directory exists."""
    output_path = os.path.join(SCRIPT_DIR, OUTPUT_DIR)
    os.makedirs(output_path, exist_ok=True)
    return output_path

def export_results(results: AnalysisResults):
    """Export all analysis results to CSV files."""
    output_path = ensure_output_dir()
    
    # 1. psi_profiles.csv
    with open(os.path.join(output_path, "psi_profiles.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['T', 'sigma', 'abs_psi', 'is_zero'])
        writer.writeheader()
        writer.writerows(results.psi_profiles)
    
    # 2. magnitude_at_zeros.csv
    with open(os.path.join(output_path, "magnitude_at_zeros.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['T', 'abs_psi', 'is_zero'])
        writer.writeheader()
        writer.writerows(results.magnitude_at_zeros)
    
    # 3. curvature_9d.csv
    with open(os.path.join(output_path, "curvature_9d.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['T', 'k', 'curvature', 'is_zero'])
        writer.writeheader()
        writer.writerows(results.curvature_9d)
    
    # 4. geodesic_criterion.csv
    with open(os.path.join(output_path, "geodesic_criterion.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['T', 'is_zero_true', 'is_zero_predicted', 
                                               'criterion_score', 'darg_dt', 'z80_abs', 'rho4'])
        writer.writeheader()
        writer.writerows(results.geodesic_criterion)
    
    # 5. phase_velocity.csv
    with open(os.path.join(output_path, "phase_velocity.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['T', 'phase_velocity', 'is_zero'])
        writer.writeheader()
        writer.writerows(results.phase_velocity)
    
    # 6. persistence_ratios.csv
    with open(os.path.join(output_path, "persistence_ratios.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['T', 'rho2', 'rho4', 'is_zero'])
        writer.writeheader()
        writer.writerows(results.persistence_ratios)
    
    # 7. z80_discriminant.csv
    with open(os.path.join(output_path, "z80_discriminant.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['T', 'z80_abs', 'is_zero'])
        writer.writeheader()
        writer.writerows(results.z80_discriminant)
    
    logger.info(f"Results exported to {output_path}/")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution: build all CSV data for Claim 3.
    
    Pipeline (vectorized):
    1. Use precomputed Riemann zeros and interpolated non-zeros
    2. Run all vectorized analyses
    3. Export CSV
    
    Expected runtime: ~10-30 seconds
    """
    start_time = time.time()
    
    logger.info("Building Claim 3 CSV data (VECTORIZED PIPELINE)...")
    logger.info(f"Zeros: {len(RIEMANN_ZEROS)}, Non-zeros: {len(NON_ZEROS)}")
    
    # Run all analyses
    psi_profiles = analyze_psi_profiles(RIEMANN_ZEROS, NON_ZEROS)
    magnitude_at_zeros = analyze_magnitude_at_zeros(RIEMANN_ZEROS, NON_ZEROS)
    curvature_9d = analyze_9d_curvature(RIEMANN_ZEROS, NON_ZEROS)
    geodesic_criterion = analyze_geodesic_criterion(RIEMANN_ZEROS, NON_ZEROS)
    phase_velocity = analyze_phase_velocity(RIEMANN_ZEROS, NON_ZEROS)
    persistence_ratios = analyze_persistence_ratios(RIEMANN_ZEROS, NON_ZEROS)
    z80_discriminant = analyze_z80_discriminant(RIEMANN_ZEROS, NON_ZEROS)
    
    # Compile results
    results = AnalysisResults(
        psi_profiles=psi_profiles,
        magnitude_at_zeros=magnitude_at_zeros,
        curvature_9d=curvature_9d,
        geodesic_criterion=geodesic_criterion,
        phase_velocity=phase_velocity,
        persistence_ratios=persistence_ratios,
        z80_discriminant=z80_discriminant
    )
    
    # Export to CSV
    export_results(results)
    
    total_time = time.time() - start_time
    logger.info(f"Analysis complete! Total time: {total_time:.2f}s")
    
    # Print summary statistics
    logger.info("")
    logger.info("=== SUMMARY STATISTICS ===")
    
    # Geodesic criterion performance
    gc_data = geodesic_criterion
    true_pos = sum(1 for r in gc_data if r['is_zero_true'] and r['is_zero_predicted'])
    false_pos = sum(1 for r in gc_data if not r['is_zero_true'] and r['is_zero_predicted'])
    true_neg = sum(1 for r in gc_data if not r['is_zero_true'] and not r['is_zero_predicted'])
    false_neg = sum(1 for r in gc_data if r['is_zero_true'] and not r['is_zero_predicted'])
    
    precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
    recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    logger.info(f"Geodesic Criterion Performance:")
    logger.info(f"  Precision: {precision:.2%}")
    logger.info(f"  Recall: {recall:.2%}")
    logger.info(f"  F1 Score: {f1:.2%}")

if __name__ == "__main__":
    main()
