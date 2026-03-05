#!/usr/bin/env python3
"""
EXPLICIT_FORMULA_KERNEL.PY
==========================

ARITHMETIC KERNEL DERIVED FROM THE EXPLICIT FORMULA
This module provides the correct arithmetic foundation for Conjecture III.

Mathematical Foundation:
------------------------
The von Mangoldt explicit formula connects primes to zeros:

    ψ(x) = x - Σ_ρ x^ρ/ρ - ζ'(0)/ζ(0) - ½ log(1 - x^{-2})

where ρ runs over ALL nontrivial zeros of ζ(s).

The key object is the logarithmic derivative:

    -ζ'/ζ(s) = Σ_{n≥1} Λ(n)/n^s     (Re(s) > 1)

where Λ(n) = log p if n = p^k (von Mangoldt function), else 0.

This module computes:
    κ_N(s) = Σ_{n≤N} Λ(n) · w(n) · n^{-s}

which approximates -ζ'/ζ(s) with regularization w(n).

CRITICAL INSIGHT:
-----------------
- Λ(n) carries ALL arithmetic content (prime locations)
- Pure φ-geometry WITHOUT Λ(n) fails (p=0.844 holdout failure)
- Geometry must be DERIVED from arithmetic, not compared to it
"""

import numpy as np
from typing import Tuple, Optional, List, Union
from functools import lru_cache
import warnings


class VonMangoldtFunction:
    """
    The von Mangoldt function Λ(n):
        Λ(n) = log p  if n = p^k for prime p, k ≥ 1
        Λ(n) = 0      otherwise
    
    This is the fundamental arithmetic object from which all Conjecture III
    constructions must derive.
    """
    
    def __init__(self, N_max: int = 10000):
        """
        Precompute Λ(n) for n ≤ N_max using sieve.
        
        Args:
            N_max: Maximum n for which to compute Λ(n)
        """
        self.N_max = N_max
        self._compute_mangoldt()
    
    def _compute_mangoldt(self):
        """Sieve-based computation of Λ(n)."""
        self.values = np.zeros(self.N_max + 1, dtype=np.float64)
        
        # Sieve of Eratosthenes for primes
        is_prime = np.ones(self.N_max + 1, dtype=bool)
        is_prime[0] = is_prime[1] = False
        
        for p in range(2, int(np.sqrt(self.N_max)) + 1):
            if is_prime[p]:
                is_prime[p*p::p] = False
        
        # For each prime p, set Λ(p^k) = log(p)
        for p in range(2, self.N_max + 1):
            if is_prime[p]:
                log_p = np.log(p)
                pk = p
                while pk <= self.N_max:
                    self.values[pk] = log_p
                    pk *= p
        
        # Cache nonzero indices for fast evaluation
        self._nonzero_indices = np.where(self.values > 0)[0]
        self._nonzero_values = self.values[self._nonzero_indices]
        self._log_n = np.log(self._nonzero_indices)
        self._n_half = self._nonzero_indices ** (-0.5)
    
    def __call__(self, n: int) -> float:
        """Evaluate Λ(n)."""
        if n <= 0 or n > self.N_max:
            return 0.0
        return self.values[n]
    
    def nonzero_terms(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return (indices, values) for n where Λ(n) > 0."""
        return self._nonzero_indices, self._nonzero_values


class PsiPartialSum:
    """
    The ψ(t) partial sum from CONJECTURE_V:
    
        ψ_N(t) = Σ_{n≤N} n^{-1/2} · e^{-it·ln(n)}
    
    This is the fundamental object that encodes zero information through
    its phase and magnitude behavior. The von Mangoldt Λ(n) weighted version
    provides additional arithmetic structure.
    
    At Riemann zeros:
    - |ψ_N(t)| tends to be small (cancellation)
    - Phase arg(ψ_N(t)) changes rapidly
    - darg/dT is elevated
    
    This class provides the ψ(t) engine consistent with CONJECTURE_V.
    """
    
    def __init__(self, N: int = 100):
        """Initialize partial sum with N terms."""
        self.N = N
        self._n = np.arange(1, N + 1, dtype=float)
        self._n_half = self._n ** (-0.5)
        self._log_n = np.log(self._n)
    
    def evaluate(self, T: float) -> complex:
        """
        Evaluate ψ_N(T) = Σ_{n≤N} n^{-1/2} · e^{-iT·ln(n)}.
        
        Args:
            T: Imaginary part of s = 1/2 + iT
            
        Returns:
            Complex partial sum value
        """
        phases = -T * self._log_n
        return np.sum(self._n_half * np.exp(1j * phases))
    
    def magnitude(self, T: float) -> float:
        """Return |ψ_N(T)|."""
        return abs(self.evaluate(T))
    
    def phase(self, T: float) -> float:
        """Return arg(ψ_N(T)) ∈ [-π, π)."""
        return np.angle(self.evaluate(T))
    
    def phase_derivative(self, T: float, delta: float = 0.01) -> float:
        """
        Compute darg/dT using central differences.
        
        This is a key discriminator for zeros - zeros have high |darg/dT|.
        """
        phase_plus = self.phase(T + delta)
        phase_minus = self.phase(T - delta)
        
        # Handle phase wrapping
        diff = phase_plus - phase_minus
        if diff > np.pi:
            diff -= 2 * np.pi
        elif diff < -np.pi:
            diff += 2 * np.pi
            
        return diff / (2 * delta)


class RegularizedArithmeticKernel:
    """
    The regularized arithmetic kernel κ_N(s) derived from the explicit formula.
    
    κ_N(s) = Σ_{n≤N} Λ(n) · w_N(n) · n^{-s}
    
    where w_N(n) is a regularization weight ensuring N-stability.
    
    This also provides the ψ(t) partial sum for consistency with CONJECTURE_V.
    
    Available regularizations:
        - 'sharp':       w(n) = 1 if n ≤ N, 0 otherwise
        - 'exponential': w(n) = exp(-n/N)
        - 'smooth':      w(n) = (1 - n/N)^2 for n < N
        - 'cesaro':      w(n) = 1 - n/N for n < N (Cesàro mean)
    """
    
    def __init__(self, 
                 N: int = 1000, 
                 regularization: str = 'exponential',
                 mangoldt: Optional[VonMangoldtFunction] = None):
        """
        Initialize arithmetic kernel with cutoff N.
        
        Args:
            N: Arithmetic cutoff (number of terms)
            regularization: Type of regularization weight
            mangoldt: Pre-computed von Mangoldt function (creates new if None)
        """
        self.N = N
        self.regularization = regularization
        
        # Use provided or create new von Mangoldt
        if mangoldt is None:
            self.mangoldt = VonMangoldtFunction(N_max=max(N, 10000))
        else:
            if mangoldt.N_max < N:
                warnings.warn(f"Mangoldt N_max={mangoldt.N_max} < N={N}, extending")
                self.mangoldt = VonMangoldtFunction(N_max=N)
            else:
                self.mangoldt = mangoldt
        
        # Also create ψ(t) partial sum for CONJECTURE_V consistency
        self.psi = PsiPartialSum(N=min(N, 100))  # 100 terms is optimal for psi
        
        self._setup_vectorized()
    
    def _setup_vectorized(self):
        """Set up vectorized computation arrays."""
        indices, values = self.mangoldt.nonzero_terms()
        
        # Filter to n ≤ N
        mask = indices <= self.N
        self._indices = indices[mask]
        self._values = values[mask]
        
        # Precompute invariants
        self._log_n = np.log(self._indices)
        self._n_half = self._indices ** (-0.5)
        
        # Compute regularization weights
        self._weights = self._compute_weights(self._indices)
    
    def _compute_weights(self, n_array: np.ndarray) -> np.ndarray:
        """Compute regularization weights for array of n values."""
        if self.regularization == 'sharp':
            return np.ones_like(n_array, dtype=float)
        elif self.regularization == 'exponential':
            return np.exp(-n_array / self.N)
        elif self.regularization == 'smooth':
            return np.maximum(0, (1 - n_array / self.N)) ** 2
        elif self.regularization == 'cesaro':
            return np.maximum(0, 1 - n_array / self.N)
        else:
            raise ValueError(f"Unknown regularization: {self.regularization}")
    
    def evaluate(self, s: complex) -> complex:
        """
        Evaluate κ_N(s) = Σ_{n≤N} Λ(n) · w(n) · n^{-s}.
        
        Args:
            s: Complex argument (typically Re(s) = 1/2)
            
        Returns:
            Complex value of the regularized kernel
        """
        # n^{-s} = n^{-Re(s)} · exp(-i·Im(s)·log(n))
        n_real_part = self._indices ** (-s.real)
        phases = -s.imag * self._log_n
        n_powers = n_real_part * np.exp(1j * phases)
        
        return np.sum(self._values * self._weights * n_powers)
    
    def evaluate_at_half(self, T: float) -> complex:
        """
        Evaluate κ_N(1/2 + iT) efficiently.
        
        This is the critical line evaluation used for zero detection.
        """
        phases = -T * self._log_n
        result = np.sum(self._values * self._weights * self._n_half * np.exp(1j * phases))
        return result
    
    def evaluate_reciprocal(self, T: float) -> complex:
        """
        Evaluate F_N(T) = 1/κ_N(1/2 + iT).
        
        This transforms poles at zeros into zeros at zeros,
        aligning singularities with the Fredholm determinant criterion.
        """
        kappa = self.evaluate_at_half(T)
        if abs(kappa) < 1e-12:
            return complex(1e12, 0)
        return 1.0 / kappa
    
    def magnitude(self, T: float) -> float:
        """
        Compute |κ_N(1/2 + iT)|.
        
        Large values indicate proximity to a Riemann zero.
        """
        return abs(self.evaluate_at_half(T))
    
    def phase(self, T: float) -> float:
        """
        Compute arg(κ_N(1/2 + iT)).
        
        Phase unwrapping can detect zero crossings.
        """
        kappa = self.evaluate_at_half(T)
        return np.angle(kappa)
    
    def psi_80(self, T: float) -> complex:
        """
        Evaluate 80-term partial sum ψ_80(T) for CONJECTURE_V consistency.
        
        This is the key object from QUANTUM_GEODESIC_SINGULARITY.PY.
        """
        return self.psi.evaluate(T)
    
    def psi_80_magnitude(self, T: float) -> float:
        """Return |ψ_80(T)| - small values indicate proximity to zeros."""
        return self.psi.magnitude(T)
    
    def darg_dt(self, T: float, delta: float = 0.01) -> float:
        """
        Compute phase velocity darg/dT.
        
        This is a key discriminator: zeros have HIGH |darg/dT|.
        """
        return self.psi.phase_derivative(T, delta)


class ExplicitFormulaZeroLocator:
    """
    Zero locator based on the explicit formula.
    
    Instead of finding zeros of ζ(s), we find singularities of κ_N(s),
    which are the same as poles of -ζ'/ζ(s), which are the zeros of ζ(s).
    
    The method is:
    1. Scan for local maxima of |κ_N(1/2 + iT)|
    2. Refine using phase analysis
    3. Validate against known zeros (for testing)
    """
    
    def __init__(self, N: int = 2000, regularization: str = 'exponential'):
        """Initialize zero locator with arithmetic parameters."""
        self.mangoldt = VonMangoldtFunction(N_max=max(N, 10000))
        self.N = N
        self.regularization = regularization
    
    def create_kernel(self, N: Optional[int] = None) -> RegularizedArithmeticKernel:
        """Create kernel with specified or default N."""
        return RegularizedArithmeticKernel(
            N=N or self.N,
            regularization=self.regularization,
            mangoldt=self.mangoldt
        )
    
    def locate_zeros(self, T_min: float, T_max: float,
                     resolution: int = 500,
                     threshold_percentile: float = 90) -> List[float]:
        """
        Locate approximate zeros in [T_min, T_max].
        
        Returns list of T values where |κ_N(1/2 + iT)| has local maxima
        above the threshold percentile.
        """
        kernel = self.create_kernel()
        
        T_grid = np.linspace(T_min, T_max, resolution)
        magnitudes = np.array([kernel.magnitude(T) for T in T_grid])
        
        threshold = np.percentile(magnitudes, threshold_percentile)
        
        # Find local maxima above threshold
        zeros = []
        for i in range(1, len(magnitudes) - 1):
            if magnitudes[i] > magnitudes[i-1] and magnitudes[i] > magnitudes[i+1]:
                if magnitudes[i] > threshold:
                    zeros.append(T_grid[i])
        
        return zeros
    
    def refine_zero(self, T_approx: float, window: float = 1.0,
                    resolution: int = 100) -> float:
        """
        Refine a zero estimate using higher resolution search.
        
        Args:
            T_approx: Approximate zero location
            window: Search window half-width
            resolution: Number of points in refinement
            
        Returns:
            Refined T value
        """
        kernel = self.create_kernel()
        
        T_grid = np.linspace(T_approx - window, T_approx + window, resolution)
        magnitudes = np.array([kernel.magnitude(T) for T in T_grid])
        
        return T_grid[np.argmax(magnitudes)]
    
    def N_stability_test(self, T_target: float, 
                         N_values: List[int] = None) -> dict:
        """
        Test N-stability for a specific zero estimate.
        
        As N increases, the zero estimate should converge.
        
        Args:
            T_target: Known/estimated zero location
            N_values: List of N values to test
            
        Returns:
            Dict with N values, estimates, and convergence diagnostics
        """
        if N_values is None:
            N_values = [100, 500, 1000, 2000, 5000]
        
        estimates = []
        for N in N_values:
            kernel = self.create_kernel(N=N)
            # Find peak in small window around target
            T_grid = np.linspace(T_target - 2, T_target + 2, 200)
            mags = [kernel.magnitude(T) for T in T_grid]
            estimates.append(T_grid[np.argmax(mags)])
        
        # Compute convergence metric
        diffs = [abs(estimates[i+1] - estimates[i]) for i in range(len(estimates)-1)]
        converging = all(diffs[i] >= diffs[i+1] for i in range(len(diffs)-1)) if len(diffs) > 1 else True
        
        return {
            'N_values': N_values,
            'estimates': estimates,
            'differences': diffs,
            'converging': converging,
            'final_estimate': estimates[-1]
        }


# First 100 Riemann zeros for validation (NOT used in kernel construction)
RIEMANN_ZEROS_100 = [
    14.134725142, 21.022039639, 25.010857580, 30.424876126, 32.935061588,
    37.586178159, 40.918719012, 43.327073281, 48.005150881, 49.773832478,
    52.970321478, 56.446247697, 59.347044003, 60.831778525, 65.112544048,
    67.079810529, 69.546401711, 72.067157674, 75.704690699, 77.144840069,
    79.337375020, 82.910380854, 84.735492981, 87.425274613, 88.809111208,
    92.491899271, 94.651344041, 95.870634228, 98.831194218, 101.317851006,
    103.725538040, 105.446623052, 107.168611184, 111.029535543, 111.874659177,
    114.320220915, 116.226680321, 118.790782866, 121.370125002, 122.946829294,
    124.256818554, 127.516683880, 129.578704200, 131.087688531, 133.497737203,
    134.756509753, 138.116042055, 139.736208952, 141.123707404, 143.111845808,
    146.000982487, 147.422765343, 150.053520421, 150.925257612, 153.024693811,
    156.112909294, 157.597591818, 158.849988171, 161.188964138, 163.030709687,
    165.537069188, 167.184439978, 169.094515416, 169.911976480, 173.411536520,
    174.754191523, 176.441434298, 178.377407776, 179.916484020, 182.207078484,
    184.874467848, 185.598783678, 187.228922584, 189.416158656, 192.026656361,
    193.079726604, 195.265396680, 196.876481841, 198.015309676, 201.264751944,
    202.493594514, 204.189671803, 205.394697202, 207.906258888, 209.576509717,
    211.690862595, 213.347919360, 214.547044783, 216.169538508, 219.067596349,
    220.714918839, 221.430705555, 224.007000255, 224.983324670, 227.421444280,
    229.337413306, 231.250188700, 231.987235253, 233.693404179, 236.524229666,
]


def validate_kernel(N: int = 2000, num_zeros: int = 20) -> dict:
    """
    Validate the arithmetic kernel against known zeros.
    
    This is a diagnostic function to verify the kernel correctly
    identifies zero locations via pole detection.
    """
    print(f"Validating arithmetic kernel (N={N}) against {num_zeros} known zeros...")
    
    locator = ExplicitFormulaZeroLocator(N=N)
    
    results = []
    zeros_to_test = RIEMANN_ZEROS_100[:num_zeros]
    
    for i, gamma in enumerate(zeros_to_test):
        # Get estimate from our kernel
        estimated = locator.refine_zero(gamma, window=2.0, resolution=200)
        error = abs(estimated - gamma)
        
        results.append({
            'true_zero': gamma,
            'estimated': estimated,
            'error': error
        })
        
        print(f"  Zero {i+1}: true={gamma:.6f}, est={estimated:.6f}, err={error:.4f}")
    
    mean_error = np.mean([r['error'] for r in results])
    max_error = np.max([r['error'] for r in results])
    
    print(f"\nMean error: {mean_error:.4f}")
    print(f"Max error:  {max_error:.4f}")
    
    return {
        'N': N,
        'num_zeros': num_zeros,
        'results': results,
        'mean_error': mean_error,
        'max_error': max_error
    }


if __name__ == "__main__":
    print("=" * 60)
    print("EXPLICIT FORMULA KERNEL MODULE")
    print("=" * 60)
    print()
    
    # Demo: Create kernel and evaluate
    print("1. Creating regularized arithmetic kernel (N=2000)...")
    kernel = RegularizedArithmeticKernel(N=2000, regularization='exponential')
    
    # Evaluate at first few zeros
    print("\n2. Kernel magnitude at known zeros:")
    for gamma in RIEMANN_ZEROS_100[:5]:
        mag = kernel.magnitude(gamma)
        print(f"   |κ_N(1/2 + i·{gamma:.2f})| = {mag:.2f}")
    
    # Evaluate away from zeros
    print("\n3. Kernel magnitude away from zeros:")
    for T in [14.0, 17.0, 20.0, 22.0, 24.0]:
        mag = kernel.magnitude(T)
        print(f"   |κ_N(1/2 + i·{T:.2f})| = {mag:.2f}")
    
    # Locate zeros
    print("\n4. Zero locator demonstration:")
    locator = ExplicitFormulaZeroLocator(N=2000)
    found_zeros = locator.locate_zeros(10, 50, resolution=400)
    print(f"   Found {len(found_zeros)} potential zeros in [10, 50]")
    print(f"   Locations: {[f'{z:.2f}' for z in found_zeros]}")
    
    # N-stability test
    print("\n5. N-stability test for γ₁ = 14.135:")
    result = locator.N_stability_test(14.135)
    for N, est in zip(result['N_values'], result['estimates']):
        print(f"   N={N:5d}: estimate = {est:.6f}")
    print(f"   Converging: {'✅' if result['converging'] else '❌'}")
    
    # Full validation
    print("\n6. Full kernel validation:")
    validate_kernel(N=2000, num_zeros=10)
