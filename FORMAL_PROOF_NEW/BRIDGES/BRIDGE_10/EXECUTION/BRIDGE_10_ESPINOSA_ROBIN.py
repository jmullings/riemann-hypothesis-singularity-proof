#!/usr/bin/env python3
"""
BRIDGE_9_ESPINOSA.py — Robin Inequalities & σ-Selectivity
==========================================================

Second independent prime-side signal for zero detection via multiplicative
arithmetic. Connects Robin's bound σ(n) < e^γ · n · log log n to the
additive C_φ(T;h) machinery via the σ-selectivity test.

ZKZ-compliant design: Phase 1 uses only prime arithmetic and multiplicative
functions. Phase 2 compares results against known zeros.
"""

import math
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import csv


@dataclass
class EspinosaSample:
    """Single sample point for Espinosa residual analysis."""
    T: float
    n: int           # n = floor(e^T) for connection to zero heights
    sigma_n: int     # divisor function σ(n)
    f_n: float       # f(n) = σ(n)/(e^γ · n · log log n)
    delta_n: float   # δ(n) = f(n) - 1 (Espinosa residual)
    cphi_normalized: float  # C_φ(T;h)/N_φ(T)² from additive side
    is_anomaly: bool        # |δ(n)| > threshold or C_φ anomalous


class EspinosaEngine:
    """
    Robin inequality and Espinosa residual calculator.
    
    Implements:
    - f(n) = σ(n)/(e^γ · n · log log n)
    - Robin (1984): f(n) < 1 for all n > 5040 ↔ RH
    - σ-selectivity test: evaluate at n = ⌊p^σ · e^T⌋ for various σ
    """
    
    def __init__(self):
        self.gamma = 0.5772156649015329  # Euler-Mascheroni constant
        self.exp_gamma = math.exp(self.gamma)
        self.primes = self._generate_primes(10000)  # Cache for factorization
    
    def _generate_primes(self, limit: int) -> List[int]:
        """Generate primes up to limit using sieve."""
        if limit < 2:
            return []
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, limit + 1, i):
                    sieve[j] = False
        return [i for i, is_prime in enumerate(sieve) if is_prime]
    
    def sigma(self, n: int) -> int:
        """Compute σ(n) = sum of divisors via prime factorization."""
        if n <= 1:
            return 1 if n == 1 else 0
        
        result = 1
        temp_n = n
        
        for p in self.primes:
            if p * p > temp_n:
                break
            if temp_n % p == 0:
                alpha = 0
                while temp_n % p == 0:
                    temp_n //= p
                    alpha += 1
                # σ_factor = (p^(α+1) - 1)/(p - 1)
                result *= (p**(alpha + 1) - 1) // (p - 1)
        
        # Handle remaining prime factor
        if temp_n > 1:
            result *= (temp_n + 1)
        
        return result
    
    def f_robin(self, n: int) -> float:
        """
        Compute f(n) = σ(n)/(e^γ · n · log log n).
        Robin's theorem: f(n) < 1 for all n > 5040 iff RH is true.
        """
        if n <= 1:
            return float('inf')
        if n <= math.e:
            return float('inf')  # log log n undefined
        
        log_log_n = math.log(math.log(n))
        if log_log_n <= 0:
            return float('inf')
        
        sigma_n = self.sigma(n)
        denominator = self.exp_gamma * n * log_log_n
        return sigma_n / denominator
    
    def espinosa_residual(self, n: int) -> float:
        """δ(n) = f(n) - 1 (Espinosa residual)."""
        return self.f_robin(n) - 1.0
    
    def multiplicative_epicycle(self, n: int) -> float:
        """
        σ(n)/n = Π_{p|n} (1 + 1/p + ... + 1/p^a) 
        This is the multiplicative Euler product evaluated at s=1.
        """
        if n <= 1:
            return 1.0
        return self.sigma(n) / n
    
    def sigma_selective_test(self, T: float, sigma_values: List[float]) -> Dict[float, Tuple[int, float]]:
        """
        Compute n = ⌊p^σ · e^T⌋ and δ(n) for various σ values.
        Key test: is δ(n) < 0 only for σ = 1/2?
        """
        results = {}
        base_exp_T = math.exp(T)
        
        for sigma in sigma_values:
            # Use the largest available prime for scaling
            p_factor = self.primes[-1] ** sigma if self.primes else 2.0 ** sigma
            n = int(p_factor * base_exp_T)
            if n <= 5040:  # Below Robin's threshold
                n = 5041  # Force above threshold
            
            delta = self.espinosa_residual(n)
            results[sigma] = (n, delta)
        
        return results
    
    def compute_cphi_surrogate(self, T: float, h: float = 0.05) -> float:
        """
        Surrogate for C_φ(T;h)/N_φ(T)² using multiplicative arithmetic.
        This provides the additive side comparison for covariance analysis.
        """
        # Simple multiplicative approximation based on prime gaps near T
        n = int(math.exp(T))
        sigma_ratio = self.multiplicative_epicycle(n)
        
        # Heuristic connection to curvature via second differences
        n_minus = max(1, int(math.exp(T - h)))
        n_plus = int(math.exp(T + h))
        
        sigma_minus = self.multiplicative_epicycle(n_minus)
        sigma_plus = self.multiplicative_epicycle(n_plus)
        
        second_diff = sigma_plus + sigma_minus - 2 * sigma_ratio
        normalization = max(1e-8, sigma_ratio ** 2)
        
        return second_diff / normalization


class EspinosaBridge:
    """
    ZKZ-compliant bridge connecting Robin inequalities to zero detection.
    Phase 1: pure prime arithmetic, Phase 2: comparison with known zeros.
    """
    
    def __init__(self):
        self.engine = EspinosaEngine()
        self.samples: List[EspinosaSample] = []
    
    def phase_1_zkg_analysis(self, T_grid: List[float], anomaly_threshold: float = 0.1) -> None:
        """
        Phase 1: ZKZ-compliant analysis using only prime arithmetic.
        No zeros loaded, no ζ function calls.
        """
        print("Bridge 9 Phase 1: ZKZ-compliant Espinosa analysis")
        print(f"Analyzing {len(T_grid)} T values with threshold = {anomaly_threshold}")
        
        self.samples.clear()
        
        for T in T_grid:
            try:
                n = int(math.exp(T))
                sigma_n = self.engine.sigma(n)
                f_n = self.engine.f_robin(n)
                delta_n = self.engine.espinosa_residual(n)
                cphi_surrogate = self.engine.compute_cphi_surrogate(T)
                
                is_anomaly = (abs(delta_n) > anomaly_threshold or 
                             abs(cphi_surrogate) > anomaly_threshold)
                
                sample = EspinosaSample(
                    T=T, n=n, sigma_n=sigma_n, f_n=f_n, delta_n=delta_n,
                    cphi_normalized=cphi_surrogate, is_anomaly=is_anomaly
                )
                self.samples.append(sample)
                
                if is_anomaly:
                    print(f"  T={T:6.2f}: δ(n)={delta_n:8.5f}, C_φ*={cphi_surrogate:8.5f} [ANOMALY]")
                    
            except (ValueError, OverflowError) as e:
                print(f"  T={T:6.2f}: computation failed: {e}")
        
        anomaly_count = sum(1 for s in self.samples if s.is_anomaly)
        print(f"Phase 1 complete: {anomaly_count}/{len(self.samples)} anomalous samples")
    
    def sigma_selectivity_test(self, T_test_values: List[float]) -> Dict[float, Dict[float, float]]:
        """
        Test σ-selectivity: are Robin violations sharpest at σ = 1/2?
        Returns: {T: {sigma: delta_n}}
        """
        print("Bridge 9: σ-selectivity test")
        sigma_values = [0.4, 0.45, 0.5, 0.55, 0.6]
        results = {}
        
        for T in T_test_values:
            T_results = {}
            sigma_test = self.engine.sigma_selective_test(T, sigma_values)
            
            for sigma, (n, delta) in sigma_test.items():
                T_results[sigma] = delta
            
            results[T] = T_results
            
            # Find sharpest violation
            min_delta = min(T_results.values())
            min_sigma = min(T_results.keys(), key=lambda s: T_results[s])
            
            print(f"  T={T:6.2f}: sharpest δ={min_delta:8.5f} at σ={min_sigma}")
            
            # Check if minimum is at σ = 0.5
            sigma_half_delta = T_results.get(0.5, float('inf'))
            if abs(sigma_half_delta - min_delta) < 1e-6:
                print(f"    ✓ Sharp minimum at σ = 1/2")
            else:
                print(f"    ⚠ Minimum at σ = {min_sigma}, not 1/2")
        
        return results
    
    def phase_2_validation(self, zero_file: str = "RiemannZeros.txt") -> Dict[str, float]:
        """
        Phase 2: Compare anomaly locations against known Riemann zeros.
        Only called after Phase 1 is complete.
        """
        try:
            with open(zero_file, 'r') as f:
                known_zeros = [float(line.strip()) for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Warning: {zero_file} not found, skipping Phase 2 validation")
            return {}
        
        print(f"Bridge 9 Phase 2: Validation against {len(known_zeros)} known zeros")
        
        anomaly_T_values = [s.T for s in self.samples if s.is_anomaly]
        if not anomaly_T_values:
            print("No anomalies detected in Phase 1")
            return {"correlation": 0.0, "precision": 0.0, "recall": 0.0}
        
        # Find matches within tolerance
        tolerance = 2.0
        matches = 0
        for anomaly_T in anomaly_T_values:
            if any(abs(anomaly_T - zero) < tolerance for zero in known_zeros):
                matches += 1
        
        precision = matches / len(anomaly_T_values) if anomaly_T_values else 0.0
        recall = matches / len(known_zeros) if known_zeros else 0.0
        correlation = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        print(f"Validation results: {matches} matches out of {len(anomaly_T_values)} anomalies")
        print(f"  Precision: {precision:.3f}")
        print(f"  Recall:    {recall:.3f}")
        print(f"  F1-score:  {correlation:.3f}")
        
        return {
            "correlation": correlation,
            "precision": precision,
            "recall": recall,
            "matches": matches,
            "anomalies": len(anomaly_T_values),
            "known_zeros": len(known_zeros)
        }
    
    def export_analysis(self, csv_file: str = "bridge_9_espinosa_analysis.csv") -> None:
        """Export complete analysis to CSV for further study."""
        if not self.samples:
            print("No samples to export")
            return
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'T', 'n', 'sigma_n', 'f_n', 'delta_n', 'cphi_normalized', 'is_anomaly'
            ])
            
            for sample in self.samples:
                writer.writerow([
                    sample.T, sample.n, sample.sigma_n, sample.f_n,
                    sample.delta_n, sample.cphi_normalized, sample.is_anomaly
                ])
        
        print(f"Analysis exported to {csv_file}")


def main():
    """Demonstration of Bridge 9 Espinosa analysis."""
    print("=" * 60)
    print("BRIDGE 9: ESPINOSA — Robin Inequalities & σ-Selectivity")
    print("=" * 60)
    
    bridge = EspinosaBridge()
    
    # Phase 1: ZKZ analysis
    T_grid = [10 + 0.5 * i for i in range(80)]  # T in [10, 50]
    bridge.phase_1_zkg_analysis(T_grid, anomaly_threshold=0.05)
    
    # σ-selectivity test
    T_test = [14.13, 21.02, 25.01, 30.42]  # Near first few zeros
    sigma_results = bridge.sigma_selectivity_test(T_test)
    
    # Export results
    bridge.export_analysis()
    
    # Phase 2: validation against known zeros (if available)
    validation_results = bridge.phase_2_validation()
    
    print("\nBridge 9 analysis complete.")
    if validation_results:
        print(f"Zero correlation: {validation_results['correlation']:.3f}")


if __name__ == "__main__":
    main()