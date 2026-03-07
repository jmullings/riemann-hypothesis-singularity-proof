#!/usr/bin/env python3
"""
RH_BITSIZE_PROGRAMME.py — Exploratory Bitsize Diagnostics

EXPLORATORY ANALYSIS: Bitsize scaling behaviour at Riemann zeros

Inspired by de Bruijn-Newman theory and the formulation of Z_b(s), this 
programme explores whether our bitsize-scaled 9D shift has stable behaviour 
at zeros. It does NOT compute Λ or test the Rodgers-Tao inequalities directly.

WHAT THIS SCRIPT DOES:
- Computes ||Δ(T)||·B(T) for sampled Riemann zeros
- Visualizes bitsize scaling patterns
- Reports coefficient of variation as "bitsize regularity index"

WHAT THIS SCRIPT DOES NOT DO:
- Compute the actual de Bruijn-Newman constant Λ
- Evaluate Z_b(s) or its derivatives
- Provide proof or mechanical evidence for RH

REFERENCE: Rodgers & Tao (2018) — "The de Bruijn-Newman constant is non-negative"
(Note: This script is inspired by, not an implementation of, their results)
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import warnings
import sys
from pathlib import Path
warnings.filterwarnings('ignore')

# Add CLAIM_4_6D_COLLAPSE path for PHI_WEIGHTED_9D_SHIFT import
script_dir = Path(__file__).resolve().parent
claim_4_path = script_dir.parent.parent / "CLAIM_4_6D_COLLAPSE" / "1_PROOF_SCRIPTS_NOTES"
sys.path.insert(0, str(claim_4_path))

# Import bitsize functionality
try:
    from PHI_WEIGHTED_9D_SHIFT import PhiWeighted9DShiftEngine, bitsize
except ImportError as e:
    print(f"Warning: Could not import PHI_WEIGHTED_9D_SHIFT: {e}")
    print(f"Searched in: {claim_4_path}")
    
    # Fallback implementations
    class PhiWeighted9DShiftEngine:
        def __init__(self, max_n=5000):
            self.max_n = max_n
        
        def compute_shift(self, T):
            # Fallback implementation returning 9D vector
            import numpy as np
            return np.array([0.1 * (k + 1) * np.exp(-k/1.618) for k in range(9)])
    
    def bitsize(T: float) -> float:
        """Fallback bitsize calculation: B(T) = log2(T/(2π))"""
        import numpy as np
        return np.log2(T / (2 * np.pi))

# Riemann zeros for analysis
RIEMANN_ZEROS = [
    14.134725141734693790, 21.022039638771554993, 25.010857580145688763,
    30.424876125859513210, 32.935061587739189691, 37.586178158825671257,
    40.918719012147495187, 43.327073280914999519, 48.005150881167159727,
    49.773832477672302181, 52.9703214777028710, 56.446247697063911, 
    59.347044003877068, 60.831778524851694, 65.112544048081651,
    67.079810529494173, 69.546401711087629, 72.067157674481907,
    75.704690699083172, 77.144840068874343, 79.337375020249367,
    82.910380854341113, 84.735492981644822, 87.425274613052609,
    88.809111163968082, 92.491899271363211, 94.651344041047650,
    95.870634227606475, 98.831194218878288, 101.317851006105064
]


@dataclass
class RiemannZeroData:
    """Complete analysis for a single Riemann zero."""
    gamma: float
    T: float
    bitsize_val: float
    shift_magnitude: float
    normalized_shift: float
    bitsize_product: float  # ||Δ||·B(T)


class BitsizeRegularityAnalyzer:
    """
    Analyzes bitsize scaling behaviour at Riemann zeros.
    
    This is an EXPLORATORY diagnostic tool, not a proof mechanism.
    It computes ||Δ(T)||·B(T) and reports regularity statistics.
    """
    
    def __init__(self):
        self.engine = PhiWeighted9DShiftEngine()
        self.zero_data: List[RiemannZeroData] = []
        
    def analyze_single_zero(self, gamma: float) -> RiemannZeroData:
        """Compute bitsize diagnostics for a single Riemann zero."""
        shift_vector = self.engine.compute_shift(gamma)
        shift_norm = np.linalg.norm(shift_vector)
        bitsize_val = bitsize(gamma)
        normalized = shift_norm / bitsize_val if bitsize_val > 0 else 0
        bitsize_product = shift_norm * bitsize_val
        
        return RiemannZeroData(
            gamma=gamma,
            T=gamma,
            bitsize_val=bitsize_val,
            shift_magnitude=shift_norm,
            normalized_shift=normalized,
            bitsize_product=bitsize_product
        )
        
    def compute_bitsize_diagnostics(self) -> Dict[str, Any]:
        """
        Compute bitsize regularity diagnostics for Riemann zeros.
        
        This is EXPLORATORY analysis — it does not estimate Λ or prove RH.
        """
        print("RH BITSIZE PROGRAMME — Exploratory Bitsize Diagnostics")
        print("=" * 70)
        print("⚠️  NOTE: This is heuristic analysis, NOT a proof mechanism")
        print()
        
        # Analyze all zeros
        self.zero_data = [self.analyze_single_zero(gamma) for gamma in RIEMANN_ZEROS[:10]]
        
        # Compute aggregate statistics
        bitsize_products = [zd.bitsize_product for zd in self.zero_data]
        normalized_shifts = [zd.normalized_shift for zd in self.zero_data]
        
        # Bitsize slope analysis
        gammas = [zd.gamma for zd in self.zero_data]
        bitsizes = [zd.bitsize_val for zd in self.zero_data]
        
        # Linear regression for slope
        A = np.vstack([gammas, np.ones(len(gammas))]).T
        bitsize_slope, bitsize_intercept = np.linalg.lstsq(A, bitsizes, rcond=None)[0]
        
        # Bitsize regularity index: coefficient of variation of ||Δ||·B(T)
        mean_product = np.mean(bitsize_products)
        std_product = np.std(bitsize_products)
        regularity_index = std_product / mean_product if mean_product > 0 else float('inf')
        
        # Slope significance (descriptive only)
        slope_significance = abs(bitsize_slope) / np.std(bitsizes) if np.std(bitsizes) > 0 else 0
        
        results = {
            'bitsize_slope': bitsize_slope,
            'bitsize_intercept': bitsize_intercept,
            'slope_significance': slope_significance,
            'mean_bitsize_product': mean_product,
            'std_bitsize_product': std_product,
            'regularity_index': regularity_index,
            'zero_data': self.zero_data
        }
        
        # Display results
        self._display_results(results)
        
        return results
        
    def _display_results(self, results: Dict[str, Any]) -> None:
        """Display the bitsize diagnostic results."""
        print(f"\n📊 BITSIZE SLOPE ANALYSIS:")
        print(f"   Slope: {results['bitsize_slope']:.6f}")
        print(f"   Intercept: {results['bitsize_intercept']:.6f}")
        print(f"   Significance: {results['slope_significance']:.4f}")
        
        print(f"\n📈 BITSIZE PRODUCT ||Δ||·B(T) STATISTICS:")
        print(f"   Mean: {results['mean_bitsize_product']:.6f}")
        print(f"   Std Dev: {results['std_bitsize_product']:.6f}")
        print(f"   Regularity Index (CV): {results['regularity_index']:.4f}")
        
        # Interpret regularity
        if results['regularity_index'] < 0.1:
            regularity_desc = "Very stable (CV < 10%)"
        elif results['regularity_index'] < 0.3:
            regularity_desc = "Moderately stable (CV < 30%)"
        else:
            regularity_desc = "Variable (CV ≥ 30%)"
        print(f"   Assessment: {regularity_desc}")
        
        print(f"\n📋 HONEST SUMMARY:")
        print("   ⚠️  This diagnostic is heuristic only")
        print("   ⚠️  It does NOT compute Λ or estimate the de Bruijn-Newman constant")
        print("   ⚠️  It does NOT provide proof or mechanical evidence for RH")
        print()
        print("   What we observe:")
        print(f"   - For sampled zeros, ||Δ(T)||·B(T) has CV = {results['regularity_index']:.2%}")
        print(f"   - Bitsize B(T) grows with slope ≈ {results['bitsize_slope']:.4f}")
        print("   - These are descriptive statistics, not theoretical conclusions")
            
    def generate_diagnostic_plots(self) -> None:
        """Generate diagnostic plots for bitsize analysis."""
        if not self.zero_data:
            print("No data to plot. Run compute_bitsize_diagnostics() first.")
            return
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        gammas = [zd.gamma for zd in self.zero_data]
        bitsizes = [zd.bitsize_val for zd in self.zero_data]
        bitsize_products = [zd.bitsize_product for zd in self.zero_data]
        shift_mags = [zd.shift_magnitude for zd in self.zero_data]
        
        # Plot 1: Bitsize scaling
        ax1.plot(gammas, bitsizes, 'bo-', label='B(T) = log₂(T/(2π))')
        ax1.set_xlabel('γ (Riemann Zero Height)')
        ax1.set_ylabel('Bitsize B(T)')
        ax1.set_title('Bitsize Scaling')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: Shift magnitude
        ax2.plot(gammas, shift_mags, 'go-', label='||Δ(T)||')
        ax2.set_xlabel('γ (Riemann Zero Height)')
        ax2.set_ylabel('Shift Magnitude')
        ax2.set_title('9D Shift Magnitude at Zeros')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Plot 3: Bitsize product
        ax3.bar(range(len(bitsize_products)), bitsize_products, alpha=0.7, color='purple')
        ax3.set_xlabel('Zero Index')
        ax3.set_ylabel('||Δ||·B(T)')
        ax3.set_title('Bitsize Product at Each Zero')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Product vs gamma
        ax4.scatter(gammas, bitsize_products, c='orange', s=60, alpha=0.7)
        ax4.set_xlabel('γ (Riemann Zero Height)')
        ax4.set_ylabel('||Δ||·B(T)')
        ax4.set_title('Bitsize Product vs Zero Height')
        ax4.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(gammas, bitsize_products, 1)
        p = np.poly1d(z)
        ax4.plot(gammas, p(gammas), 'r--', alpha=0.5, label=f'Trend (slope={z[0]:.4f})')
        ax4.legend()
        
        plt.suptitle('RH Bitsize Programme — Exploratory Diagnostics\n(Heuristic analysis only, not proof)', 
                    fontsize=12, y=1.02)
        plt.tight_layout()
        
        # Save to current script directory
        output_path = Path(__file__).parent.parent / "2_ANALYTICS_CHARTS_ILLUSTRATION" / "rh_bitsize_diagnostics.png"
        try:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"   Plot saved to: {output_path}")
        except Exception as e:
            print(f"   Could not save plot: {e}")
        plt.show()


def main():
    """
    Execute the RH Bitsize Programme exploratory analysis.
    
    This computes bitsize regularity diagnostics at Riemann zeros.
    It does NOT compute Λ or provide proof for RH.
    """
    analyzer = BitsizeRegularityAnalyzer()
    
    print("🔬 INITIALIZING RH BITSIZE PROGRAMME...")
    print("   Purpose: Exploratory bitsize diagnostics at Riemann zeros")
    print("   Output: Regularity statistics for ||Δ(T)||·B(T)")
    print("   ⚠️  This does NOT estimate Λ or prove RH")
    print()
    
    # Execute bitsize diagnostics
    results = analyzer.compute_bitsize_diagnostics()
    
    # Generate diagnostic visualizations
    print("\n📈 GENERATING DIAGNOSTIC PLOTS...")
    analyzer.generate_diagnostic_plots()
    
    print(f"\n📋 PROGRAMME COMPLETE")
    print(f"   Bitsize regularity index: {results['regularity_index']:.4f}")
    print(f"   ⚠️  These are descriptive statistics only")
    
    return results


if __name__ == "__main__":
    # Execute the Holy Grail programme
    main()