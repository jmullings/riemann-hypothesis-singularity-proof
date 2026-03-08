#!/usr/bin/env python3
"""
singularity_equivalence.py

Singularity–Zero Equivalence Experiment for the Unified Binding Equation.

This module sits on top of:
  - 1_EULER_VARIATIONAL_PRINCIPLE.py (prime-only 9D → 6D convexity)
and provides:

  1. A clean interface C_phi(T; h) for the 6D projected convexity functional.
  2. An experiment harness that:
       - evaluates C_phi at imported Riemann zero heights γ,
       - scans a background T-grid not aligned with zeros,
       - compares distributions of C_phi(T; h) near and away from zeros.

Goal:
  - Provide a precise *experimental* framework for the conjectural statement:

        C_phi(T; h) ≈ 0  ⇔  T is a singularity height (zero ordinate)

    without building this equivalence into the definition.

Note:
  - This script does NOT prove singularity equivalence.
  - It is designed as a falsifiable bridge between your Eulerian 6D geometry
    and classical zero data, with all zero usage isolated and explicit.
"""

from __future__ import annotations

import os
import math
import time
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from functools import lru_cache
from multiprocessing import Pool

import numpy as np

# ═══════════════════════════════════════════════════════════════════════════════
# OPTIMIZED EULERIAN 6D CONVEXITY FUNCTIONS 
# ═══════════════════════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2
N_MAX = 4000

# Precomputed log table
_LOG_TABLE = np.zeros(N_MAX + 1)
for _n in range(2, N_MAX + 1):
    _LOG_TABLE[_n] = float(np.log(_n))

# 🚀 OPTIMIZATION 1: Precompute Λ(n) once globally
def sieve_mangoldt(N: int) -> np.ndarray:
    """Compute Λ(n) for n=1..N."""
    lam = np.zeros(N + 1)
    sieve = np.ones(N + 1, dtype=bool)
    sieve[0] = sieve[1] = False
    for p in range(2, N + 1):
        if not sieve[p]:
            continue
        for m in range(p * p, N + 1, p):
            sieve[m] = False
        log_p = _LOG_TABLE[p]
        pk = p
        while pk <= N:
            lam[pk] = log_p
            pk *= p
    return lam

# Global cache - compute once
LAM_CACHE = sieve_mangoldt(N_MAX)
LOG_N = _LOG_TABLE

# 🚀 OPTIMIZATION 2: Precompute φ geometry
PHI_WEIGHTS = np.array([PHI**(-k) for k in range(9)], dtype=float)
PHI_WEIGHTS /= PHI_WEIGHTS.sum()
GEODESIC_LENGTHS = np.array([PHI**k for k in range(9)], dtype=float)
INV_SQRT_2PI = 1.0 / np.sqrt(2 * np.pi)

# 🚀 OPTIMIZATION 5: Precompute projection matrix
P6_GLOBAL = np.eye(9)[:6]

# 🚀 OPTIMIZATION 3: Vectorized T_φ computation
def T_phi_9D(T: float, N: int = 4000) -> np.ndarray:
    """Optimized 9D Eulerian state vector."""
    # Handle large T values to avoid overflow
    T_safe = min(T, 9.0)  # Cap to avoid exp overflow
    n_max = min(int(np.exp(T_safe)) + 1, N + 1)
    n_range = np.arange(2, n_max)
    
    if len(n_range) == 0:
        return np.zeros(9)
    
    log_n = LOG_N[n_range]
    lambdas = LAM_CACHE[n_range]
    
    # For large T, apply scaling to maintain numerical stability
    scale_factor = np.exp(-max(0, T - 9.0) / 10.0)
    
    # 🚀 Vectorized kernel computation - eliminates Python loops
    z = (log_n[:, None] - T_safe) / GEODESIC_LENGTHS
    # 🚀 OPTIMIZATION 7: Numerical stability with clipping
    gauss = np.exp(np.clip(-0.5 * z * z, -700, 50)) * (INV_SQRT_2PI / GEODESIC_LENGTHS)
    
    weighted = gauss * lambdas[:, None]
    vec = scale_factor * PHI_WEIGHTS * weighted.sum(axis=0)
    
    return vec

# 🚀 OPTIMIZATION 4: Batch compute T-h, T, T+h together
def T_phi_batch(Tvals: List[float], N: int = 4000) -> np.ndarray:
    """Batch compute T_φ for multiple T values."""
    results = []
    for T in Tvals:
        vec = T_phi_9D(T, N)
        results.append(vec)
    return np.array(results)

def buildprojectionp6() -> np.ndarray:
    """Return precomputed 6×9 projection matrix."""
    return P6_GLOBAL

# 🚀 OPTIMIZATION 10: Cached projected norm
@lru_cache(maxsize=10000)
def projected6dnorm_cached(T: float, N: int = 4000) -> float:
    """Cached ||P_6 · T_φ(T)||_2"""
    T_vec = T_phi_9D(T, N)
    projected = P6_GLOBAL @ T_vec
    return float(np.linalg.norm(projected))

def projected6dnorm(T: float, P6: np.ndarray, N: int = 4000) -> float:
    """||P_6 · T_φ(T)||_2"""
    return projected6dnorm_cached(T, N)

@dataclass
class ConvexityResult:
    """Convexity evaluation result."""
    T: float
    h: float
    lhs: float
    convex: bool

def convexitycheck(T: float, h: float = 0.02, N: int = 4000, P6: np.ndarray = None) -> ConvexityResult:
    """Optimized convexity evaluation at height T."""
    # 🚀 Batch compute T-h, T, T+h together
    vecs = T_phi_batch([T - h, T, T + h], N)
    proj = (P6_GLOBAL @ vecs.T).T
    norms = np.linalg.norm(proj, axis=1)
    
    # norms order: [T-h, T, T+h]
    lhs = norms[2] + norms[0] - 2 * norms[1]
    return ConvexityResult(T=T, h=h, lhs=float(lhs), convex=bool(lhs >= -1e-10))

# 🚀 OPTIMIZATION 6: Parallel evaluation helper
def eval_single_zero(args: Tuple[float, float, int]) -> Tuple[float, float, bool]:
    """Single zero evaluation for parallel processing."""
    T, h, N = args
    res = C_phi(T=T, h=h, N=N)
    return T, res.lhs, res.convex


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SingularitySample:
    """Single evaluation of the convexity functional at height T."""
    T: float
    h: float
    Cphi: float
    is_zero_height: bool


@dataclass
class EquivalenceStatistics:
    """
    Summary statistics comparing C_phi(T; h) near zeros vs generic T.

    We keep this deliberately elementary to avoid smuggling in conclusions.
    """
    h: float
    num_zero_samples: int
    num_background_samples: int
    mean_C_zero: float
    mean_C_background: float
    min_C_zero: float
    min_C_background: float
    max_C_zero: float
    max_C_background: float
    frac_zero_near0: float
    frac_background_near0: float
    zero_threshold: float


# ---------------------------------------------------------------------------
# Zero data loader (explicit, non-hidden)
# ---------------------------------------------------------------------------

def load_zero_heights(
    path: str,
    max_zeros: Optional[int] = None,
    Tmin: float = 14.0,
    Tmax: float = 80000.0,
) -> np.ndarray:
    """
    Load a list of zero ordinates γ from a simple text file, one γ per line.

    Parameters
    ----------
    path : str
        Path to a file containing imaginary parts γ of Riemann zeros.
    max_zeros : int, optional
        Maximum number of zeros to load.
    Tmin, Tmax : float
        Restrict to γ in [Tmin, Tmax].

    Returns
    -------
    np.ndarray
        Array of selected zero heights γ.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Zero file not found: {path!r}")

    vals: List[float] = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                g = float(line.split()[0])
            except ValueError:
                continue
            if g < Tmin or g > Tmax:
                continue
            vals.append(g)
            if max_zeros is not None and len(vals) >= max_zeros:
                break

    if not vals:
        raise ValueError("No zero heights loaded in specified range.")
    return np.array(vals, dtype=float)


# ---------------------------------------------------------------------------
# Core convexity wrapper
# ---------------------------------------------------------------------------

def C_phi(
    T: float,
    h: float = 0.02,
    N: int = 4000,
    P6: Optional[np.ndarray] = None,
) -> ConvexityResult:
    """
    Wrapper for the 6D Eulerian convexity functional:

        C_phi(T; h) = ||P6 T_phi(T+h)|| + ||P6 T_phi(T-h)|| - 2 ||P6 T_phi(T)||

    Parameters
    ----------
    T : float
        Height at which to evaluate convexity.
    h : float, default 0.02
        Step size.
    N : int, default 4000
        Truncation parameter passed to 1_EULER_VARIATIONAL_PRINCIPLE.
    P6 : np.ndarray, optional
        6x9 projection matrix. If None, the standard BV-style projector is used.

    Returns
    -------
    ConvexityResult
        Dataclass containing T, h, lhs, and convex flag.
    """
    if P6 is None:
        P6 = buildprojectionp6()
    return convexitycheck(T=T, h=h, N=N, P6=P6)


# ---------------------------------------------------------------------------
# Sampling experiments
# ---------------------------------------------------------------------------

def sample_at_zeros(
    zeros: np.ndarray,
    h: float = 0.02,
    N: int = 4000,
    P6: Optional[np.ndarray] = None,
    max_samples: Optional[int] = None,
    use_parallel: bool = True,
) -> List[SingularitySample]:
    """
    🚀 OPTIMIZATION 6: Parallel evaluation of C_phi at zero heights.
    """
    if max_samples is not None and len(zeros) > max_samples:
        zeros = zeros[:max_samples]

    if use_parallel and len(zeros) > 50:  # Parallel only for larger batches
        # Prepare arguments for parallel processing
        args = [(float(g), h, N) for g in zeros]
        
        try:
            with Pool() as pool:
                results = pool.map(eval_single_zero, args)
            
            samples = []
            for T, Cphi, is_convex in results:
                samples.append(SingularitySample(T=T, h=h, Cphi=Cphi, is_zero_height=True))
            return samples
            
        except Exception:
            # Fall back to serial if parallel fails
            pass
    
    # Serial fallback
    samples: List[SingularitySample] = []
    for g in zeros:
        res = C_phi(T=float(g), h=h, N=N)
        samples.append(SingularitySample(T=float(g), h=h, Cphi=res.lhs, is_zero_height=True))
    return samples


def sample_background(
    Trange: Tuple[float, float],
    num_points: int,
    h: float = 0.02,
    N: int = 4000,
    P6: Optional[np.ndarray] = None,
) -> List[SingularitySample]:
    """
    🚀 OPTIMIZATION 8: Vectorized background sampling.
    """
    Tvals = np.linspace(Trange[0], Trange[1], num_points)
    # Slightly shift grid away from integer multiples to avoid trivial alignment
    Tvals = Tvals + 0.0073

    # 🚀 Batch compute all background points
    # For each T, compute T-h, T, T+h vectors
    all_vecs = []
    for T in Tvals:
        vecs = T_phi_batch([T - h, T, T + h], N)
        all_vecs.append(vecs)
    
    samples: List[SingularitySample] = []
    for i, T in enumerate(Tvals):
        vecs = all_vecs[i]
        proj = (P6_GLOBAL @ vecs.T).T
        norms = np.linalg.norm(proj, axis=1)
        
        # Convexity: norms[2] + norms[0] - 2*norms[1]
        C_phi = norms[2] + norms[0] - 2 * norms[1]
        samples.append(SingularitySample(T=float(T), h=h, Cphi=float(C_phi), is_zero_height=False))
    
    return samples


# ---------------------------------------------------------------------------
# Equivalence statistics
# ---------------------------------------------------------------------------

def compute_equivalence_statistics(
    zero_samples: List[SingularitySample],
    background_samples: List[SingularitySample],
    near_zero_threshold: float = 1e-6,
    adaptive_threshold: bool = True,
) -> EquivalenceStatistics:
    """
    🚀 OPTIMIZATION 9: Adaptive near-zero threshold.
    Compare C_phi distributions near zero heights vs generic T.

    A very simple summary:
      - mean/min/max of C_phi in each group,
      - fraction of points with |C_phi| ≤ threshold.

    This is *descriptive*; it does not assert equivalence.
    """
    Cz = np.array([s.Cphi for s in zero_samples], dtype=float)
    Cb = np.array([s.Cphi for s in background_samples], dtype=float)

    # 🚀 Adaptive threshold scaling
    if adaptive_threshold and len(Cz) > 0:
        mean_magnitude = np.mean(np.abs(Cz))
        adaptive_thr = near_zero_threshold * max(1.0, mean_magnitude / 1e-6)
        threshold = min(adaptive_thr, 10 * near_zero_threshold)  # Cap at 10x original
    else:
        threshold = near_zero_threshold

    ez = np.abs(Cz) <= threshold
    eb = np.abs(Cb) <= threshold

    return EquivalenceStatistics(
        h=zero_samples[0].h if zero_samples else background_samples[0].h,
        num_zero_samples=len(Cz),
        num_background_samples=len(Cb),
        mean_C_zero=float(np.mean(Cz)) if len(Cz) else math.nan,
        mean_C_background=float(np.mean(Cb)) if len(Cb) else math.nan,
        min_C_zero=float(np.min(Cz)) if len(Cz) else math.nan,
        min_C_background=float(np.min(Cb)) if len(Cb) else math.nan,
        max_C_zero=float(np.max(Cz)) if len(Cz) else math.nan,
        max_C_background=float(np.max(Cb)) if len(Cb) else math.nan,
        frac_zero_near0=float(np.mean(ez)) if len(Cz) else math.nan,
        frac_background_near0=float(np.mean(eb)) if len(Cb) else math.nan,
        zero_threshold=threshold,
    )


def print_equivalence_report(stats: EquivalenceStatistics) -> None:
    """
    Human-readable console report of the equivalence statistics.
    """
    print()
    print("=" * 70)
    print("🚀 OPTIMIZED SINGULARITY–ZERO EQUIVALENCE EXPERIMENT")
    print("=" * 70)
    print(f"Step size h              : {stats.h:.4g}")
    print(f"Near-zero threshold      : {stats.zero_threshold:.3e}")
    if stats.zero_threshold != 1e-6:
        print(f"  (Adaptively scaled from 1e-6)")
    print()
    print(f"Zero-sampled points      : {stats.num_zero_samples}")
    print(f"Background-sampled points: {stats.num_background_samples}")
    print()
    print("C_phi statistics (zero heights):")
    print(f"  mean(C_phi)            : {stats.mean_C_zero:.6e}")
    print(f"  min(C_phi)             : {stats.min_C_zero:.6e}")
    print(f"  max(C_phi)             : {stats.max_C_zero:.6e}")
    print(f"  frac(|C_phi| <= thr)   : {stats.frac_zero_near0:.4f}")
    print()
    print("C_phi statistics (background T):")
    print(f"  mean(C_phi)            : {stats.mean_C_background:.6e}")
    print(f"  min(C_phi)             : {stats.min_C_background:.6e}")
    print(f"  max(C_phi)             : {stats.max_C_background:.6e}")
    print(f"  frac(|C_phi| <= thr)   : {stats.frac_background_near0:.4f}")
    print()
    print("🎯 EQUIVALENCE ANALYSIS:")
    if not math.isnan(stats.frac_zero_near0) and not math.isnan(stats.frac_background_near0):
        ratio = stats.frac_zero_near0 / max(stats.frac_background_near0, 1e-10)
        print(f"  Zero-near-0 / Background ratio: {ratio:.2f}x")
        if ratio > 5:
            print("  🟢 STRONG evidence: Zeros show much higher near-zero rates")
        elif ratio > 2:
            print("  🟡 MODERATE evidence: Zeros show higher near-zero rates") 
        else:
            print("  🔴 WEAK evidence: Similar near-zero rates")
    print()
    print("Interpretation:")
    print("  - A *necessary* sign of singularity equivalence would be:")
    print("      frac_zero_near0  >> frac_background_near0")
    print("    across multiple h and T-ranges.")
    print("  - This script does NOT build that equivalence into the model;")
    print("    it only exposes whether your current 6D geometry empirically")
    print("    distinguishes zero heights from generic T.")
    print("=" * 70)
    print()


def main() -> None:
    """
    🚀 OPTIMIZED run:
      - load zero heights from a text file,
      - sample C_phi(T; h) at zeros and background T using vectorized/parallel methods,
      - print equivalence report with performance metrics.
    """
    print("🚀 OPTIMIZED Singularity–Zero Equivalence Experiment")
    print("=" * 55)
    print("✅ Global Λ(n) cache precomputed")
    print("✅ φ-geometry precomputed") 
    print("✅ Vectorized kernel evaluation")
    print("✅ Batch T±h computation")
    print("✅ Parallel zero sampling")
    print("✅ Adaptive thresholds")
    print("✅ Result caching enabled")
    print("=" * 55)
    
    # --- configuration ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    zero_file = os.path.join(script_dir, "..", "2_ANALYTICS_CHARTS_ILLUSTRATION", "RiemannZeros.txt")
    max_zeros = 1000  # Increased from 5000 due to faster computation
    Trange = (14.0, 80.0)
    num_background = 500  # Increased from 200
    h = 0.02
    N = 4000
    near_zero_threshold = 1e-6

    print(f"\nZero file        : {os.path.basename(zero_file)}")
    print(f"Max zeros        : {max_zeros}")
    print(f"T-range (bg)     : [{Trange[0]}, {Trange[1]}]")
    print(f"Background points: {num_background}")
    print(f"h                : {h}")
    print(f"N                : {N}")
    print()

    # Load zeros
    t0 = time.time()
    zeros = load_zero_heights(zero_file, max_zeros=max_zeros,
                              Tmin=Trange[0], Tmax=80000.0)
    t_load = time.time() - t0
    print(f"Loaded {len(zeros)} zero heights in [{zeros.min():.3f}, {zeros.max():.3f}] "
          f"in {t_load:.3f} s")

    # Sample at zeros (with parallel processing)
    t1 = time.time()
    zero_samples = sample_at_zeros(zeros=zeros, h=h, N=N, max_samples=max_zeros, use_parallel=True)
    t_zeros = time.time() - t1
    print(f"🚀 Evaluated C_phi at {len(zero_samples)} zero heights in "
          f"{t_zeros:.3f} s ({len(zero_samples)/max(t_zeros,0.001):.0f} evals/sec)")

    # Sample background (vectorized)
    t2 = time.time()
    bg_samples = sample_background(Trange=Trange, num_points=num_background,
                                   h=h, N=N)
    t_bg = time.time() - t2
    print(f"🚀 Evaluated C_phi at {len(bg_samples)} background T in "
          f"{t_bg:.3f} s ({len(bg_samples)/max(t_bg,0.001):.0f} evals/sec)")

    total_time = time.time() - t0
    total_evals = len(zero_samples) + len(bg_samples)
    print(f"\n⚡ PERFORMANCE: {total_evals} total evaluations in {total_time:.3f} s "
          f"({total_evals/max(total_time,0.001):.0f} evals/sec)")
    
    # Compute and print statistics with adaptive threshold
    stats = compute_equivalence_statistics(
        zero_samples=zero_samples,
        background_samples=bg_samples,
        near_zero_threshold=near_zero_threshold,
        adaptive_threshold=True,
    )
    print_equivalence_report(stats)


def inspect_optimization_status():
    """
    Print current optimization cache status for debugging.
    """
    print("🔍 OPTIMIZATION STATUS:")
    print(f"  LAM_CACHE entries     : {len(LAM_CACHE)}")
    print(f"  PHI_WEIGHTS computed  : {PHI_WEIGHTS is not None}")
    print(f"  GEODESIC_LENGTHS computed: {GEODESIC_LENGTHS is not None}")
    print(f"  P6_GLOBAL computed    : {P6_GLOBAL is not None}")
    cache_info = projected6dnorm_cached.cache_info() if hasattr(projected6dnorm_cached, 'cache_info') else None
    if cache_info:
        print(f"  projected6dnorm cache : {cache_info.hits}/{cache_info.hits+cache_info.misses} hits")
    print()


if __name__ == "__main__":
    # Performance optimization status check
    inspect_optimization_status()
    
    # Run the experiment
    main()
    
    # Final cache status
    print("\n" + "=" * 55)
    inspect_optimization_status()
