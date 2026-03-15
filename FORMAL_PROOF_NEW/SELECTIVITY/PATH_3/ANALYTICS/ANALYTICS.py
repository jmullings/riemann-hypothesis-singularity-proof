#!/usr/bin/env python3
"""
FORMAL_PROOF_NEW/SELECTIVITY/PATH_3/ANALYTICS/ANALYTICS.py
==========================================================

**STATUS: ANALYTICAL SUPPORT — March 14, 2026** 
**Purpose: Charts and illustrations for PATH_3 Li Coefficients / Dual-Probe analysis**
**Protocols: P1-P5 compliant analytical visualization**

This module provides analytical visualization for the Li coefficients and dual-probe
pathway, showing Li positivity, Pearson correlation analysis, 9D coordinate structure,
and GUE alignment trends (all marked as supporting evidence only).

=============================================================================
VISUALIZATIONS PROVIDED
=============================================================================

1. Li Coefficients: λₙ positivity verification using 9-zero truncation [QUARANTINE]
2. Dual Probe Analysis: F₂_k vs C_k correlation and independence verification
3. 9D Coordinate Structure: Normalized coordinates and radius analysis  
4. GUE Alignment: 1/√k convergence analysis and φ-curvature scaling
5. Statistical Independence: Pearson ρ ≈ 0.063 visualization
6. Pathway 2→3 Bridge: sech² approximation strategy illustration

=============================================================================
Author : Jason Mullings
Date   : March 14, 2026  
Version: 1.0.0
=============================================================================
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Any
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import math

# Add parent directories to path for imports
current_dir = Path(__file__).parent
execution_dir = current_dir.parent / "EXECUTION"
configs_dir = current_dir.parent.parent.parent / "CONFIGURATIONS"

sys.path.insert(0, str(execution_dir))
sys.path.insert(0, str(configs_dir))

try:
    from PATH_3_LI_DUAL_PROBE import (
        li_coefficients_table, F2_probe1, probe2_sech2_angle,
        pearson_rho, compute_9d_coordinates, compute_9d_radius,
        phi_curvature_scale, gue_1_over_sqrt_k_check,
        LAMBDA_STAR, PHI, COUPLING_K, ZEROS_9
    )
    IMPORTS_OK = True
except ImportError as e:
    print(f"Warning: PATH_3 imports failed: {e}")
    IMPORTS_OK = False

# ============================================================================
# ANALYTICAL VISUALIZATION FUNCTIONS
# ============================================================================

def plot_li_coefficients() -> None:
    """
    Li coefficient positivity analysis using 9-zero truncation.
    [QUARANTINE: uses known zeros as input - verification only]
    """
    if not IMPORTS_OK:
        print("Skipping Li coefficients plot - imports failed")
        return
        
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Panel 1: Li coefficients λₙ
    li_table = li_coefficients_table(n_max=12)
    n_vals = [item[0] for item in li_table]
    lambda_vals = [item[1] for item in li_table]
    
    bars = ax1.bar(n_vals, lambda_vals, color='blue', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('n')
    ax1.set_ylabel('λₙ')
    ax1.set_title('Li Coefficients λₙ > 0 Verification [QUARANTINE]')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.axhline(y=0, color='red', linestyle='--', linewidth=2, label='λₙ = 0 (RH boundary)')
    
    # Add value annotations for small n
    for i, (bar, val) in enumerate(zip(bars[:6], lambda_vals[:6])):
        height = bar.get_height()
        ax1.annotate(f'{val:.3f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=8)
    
    ax1.legend()
    
    # Panel 2: Li coefficient scaling
    ax2.semilogy(n_vals, lambda_vals, 'bo-', linewidth=2, markersize=6, label='λₙ (9-zero truncation)')
    ax2.set_xlabel('n')
    ax2.set_ylabel('λₙ (log scale)')
    ax2.set_title('Li Coefficient Scaling')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Panel 3: Zero truncation effect
    zero_counts = [3, 5, 7, 9]
    lambda_1_values = []
    for zeros in zero_counts:
        # Approximate λ₁ using different zero counts
        lambda_1_approx = 2 * sum(1 - (1 - 1/(0.5 + 1j*ZEROS_9[k])).real for k in range(zeros))
        lambda_1_values.append(lambda_1_approx)
    
    ax3.plot(zero_counts, lambda_1_values, 'ro-', linewidth=2, markersize=8, label='λ₁ vs zero count')
    ax3.set_xlabel('Number of zeros used')
    ax3.set_ylabel('λ₁ approximation')
    ax3.set_title('Truncation Effect on λ₁')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Panel 4: QUARANTINE warning
    ax4.axis('off')
    quarantine_text = """LI COEFFICIENTS STATUS:
    
✓ λₙ > 0 for n=1..12 (9-zero truncation)
⚠ QUARANTINE: Uses known zeros as input
⚠ NOT proof of Li's criterion
⚠ Requires ALL zeros, not finite truncation

DEMOTION RATIONALE:
• Statistical-algebraic gap
• No known F₂ₖ → λₙ map  
• Truncated sum insufficient

PATHWAY 2→3 BRIDGE:
If sech²(α·t) can approximate Li test
functions hₙ, then PATH_2 success → Li positivity"""
    
    ax4.text(0.05, 0.95, quarantine_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(current_dir / 'li_coefficients_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_dual_probe_correlation() -> None:
    """
    Dual probe analysis: F₂_k vs C_k correlation showing statistical independence.
    """
    if not IMPORTS_OK:
        print("Skipping dual probe plot - imports failed")
        return
        
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Panel 1: Probe 1 values (F₂_k)
    sigma_half = 0.5
    probe1_vals = [F2_probe1(sigma_half, T) for T in ZEROS_9]
    zero_indices = list(range(1, len(ZEROS_9) + 1))
    
    bars1 = ax1.bar(zero_indices, probe1_vals, color='blue', alpha=0.7, label='F₂_k (σ-curvature)')
    ax1.set_xlabel('Zero index k')
    ax1.set_ylabel('F₂_k')
    ax1.set_title('Probe 1: σ-Curvature at Critical Line [QUARANTINE]')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.legend()
    
    # Panel 2: Probe 2 values (C_k) - compute for first 5 zeros due to speed
    print("Computing Probe 2 values (may take a moment)...")
    probe2_vals = []
    for T in ZEROS_9[:5]:  # First 5 for speed
        c_k = probe2_sech2_angle(T, N_max=1000)  # Reduced N_max for speed
        probe2_vals.append(c_k)
    
    bars2 = ax2.bar(range(1, len(probe2_vals) + 1), probe2_vals, color='red', alpha=0.7, label='C_k (sech²-angle)')
    ax2.set_xlabel('Zero index k')
    ax2.set_ylabel('C_k')
    ax2.set_title('Probe 2: SECH²-Weighted Turning Angle [QUARANTINE]')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend()
    
    # Panel 3: Correlation scatter plot
    probe1_subset = probe1_vals[:len(probe2_vals)]  # Match lengths
    rho = pearson_rho(probe1_subset, probe2_vals)
    
    ax3.scatter(probe1_subset, probe2_vals, color='purple', s=100, alpha=0.7, edgecolors='black')
    ax3.set_xlabel('Probe 1 (F₂_k)')
    ax3.set_ylabel('Probe 2 (C_k)')
    ax3.set_title(f'Dual Probe Correlation: ρ = {rho:.6f}')
    ax3.grid(True, alpha=0.3)
    
    # Add correlation line if significant
    if abs(rho) > 0.1:
        z = np.polyfit(probe1_subset, probe2_vals, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(probe1_subset), max(probe1_subset), 100)
        ax3.plot(x_line, p(x_line), 'r--', alpha=0.8, label=f'Linear fit (ρ={rho:.3f})')
        ax3.legend()
    
    # Panel 4: Statistical independence interpretation
    ax4.axis('off')
    independence_text = f"""DUAL PROBE ANALYSIS:

Probe 1: F₂_k = ∂²E/∂σ² at σ=½, γₖ
Probe 2: C_k = SECH²-weighted turning angle

Pearson ρ ≈ {rho:.6f} (first {len(probe2_vals)} zeros)

|ρ| ≈ {abs(rho):.3f} << 1 indicates:
• Near-zero correlation
• Statistical INDEPENDENCE  
• Two different mathematical lenses
• Both detect σ=½ phenomenon independently

EMPIRICAL SIGNIFICANCE:
Powerful heuristic for universality of
σ=½ selectivity, but NOT algebraic theorem.

Cannot force λₙ > 0 via correlation."""
    
    ax4.text(0.05, 0.95, independence_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcyan", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(current_dir / 'dual_probe_correlation.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_9d_coordinate_structure() -> None:
    """
    9D coordinate structure and GUE alignment analysis.
    """
    if not IMPORTS_OK:
        print("Skipping 9D coordinate plot - imports failed")
        return
        
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Panel 1: Normalized 9D coordinates
    x_coords = compute_9d_coordinates(sigma=0.5, zeros=ZEROS_9)
    coord_indices = list(range(1, len(x_coords) + 1))
    
    bars = ax1.bar(coord_indices, x_coords, color='green', alpha=0.7, edgecolor='black')
    uniform_val = 1.0 / 9.0
    ax1.axhline(y=uniform_val, color='red', linestyle='--', linewidth=2, label=f'Uniform (1/9 = {uniform_val:.3f})')
    ax1.set_xlabel('Coordinate index k')
    ax1.set_ylabel('xₖ = F₂_k / Σ F₂_j')
    ax1.set_title('9D Normalized Coordinates [QUARANTINE]')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.legend()
    
    # Panel 2: φ-curvature scaling
    gue_data = gue_1_over_sqrt_k_check(x_coords)
    phi_c = phi_curvature_scale()
    R9 = gue_data['R9_radius']
    
    scaling_data = ['R₉ measured', 'φ⁻² scale', 'R₉/φ⁻²']
    scaling_values = [R9, phi_c, R9/phi_c]
    colors = ['blue', 'gold', 'purple']
    
    bars2 = ax2.bar(scaling_data, scaling_values, color=colors, alpha=0.7)
    ax2.set_ylabel('Value')
    ax2.set_title('φ-Curvature Scaling Analysis')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value annotations
    for bar, val in zip(bars2, scaling_values):
        height = bar.get_height()
        ax2.annotate(f'{val:.6f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords='offset points', ha='center', va='bottom')
    
    # Panel 3: GUE 1/√k analysis
    k_vals = np.array(coord_indices)
    theoretical_1_sqrt_k = 1.0 / np.sqrt(k_vals) / np.sqrt(9)  # Normalized
    deviations = np.abs(np.array(x_coords) - uniform_val)
    
    ax3.semilogy(k_vals, deviations, 'bo-', markersize=6, label='|xₖ - 1/9|')
    ax3.semilogy(k_vals, theoretical_1_sqrt_k, 'r--', linewidth=2, label='1/√k/√9 (theoretical)')
    ax3.set_xlabel('k')
    ax3.set_ylabel('Deviation (log scale)')
    ax3.set_title('GUE 1/√k Convergence Test')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Panel 4: Spiral curvature equation
    ax4.axis('off')
    spiral_text = f"""9D COORDINATE ANALYSIS:

R₉ = √(Σ xₖ²) = {R9:.6f}
φ⁻² = {phi_c:.6f}  
R₉/φ⁻² = {R9/phi_c:.6f}

Spiral Curvature Equation (NOTES.md):
r₉(T) = φ⁻² + a·R(T) + b

Where:
• φ⁻² ≈ {phi_c:.6f} (golden ratio scale)
• a ≈ -0.9, b ≈ 0.25 (fitted constants)

GUE CONSISTENCY:
1/√k structure observed but NOT verified.
Max |xₖ - 1/9| = {max(deviations):.6f}
Mean |xₖ - 1/9| = {np.mean(deviations):.6f}

OBSERVATIONAL ONLY - not a theorem."""
    
    ax4.text(0.05, 0.95, spiral_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(current_dir / '9d_coordinate_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_pathway_status_summary() -> None:
    """
    Overall PATH_3 status and recommendations.
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.axis('off')
    
    # Create status boxes
    components = {
        'Li Coefficients\n(Numerical)': {'status': 'QUARANTINE', 'color': 'yellow', 'y': 0.8},
        'Dual Probe ρ\n(Empirical)': {'status': 'QUARANTINE', 'color': 'yellow', 'y': 0.65},  
        '9D GUE Structure\n(Observational)': {'status': 'QUARANTINE', 'color': 'yellow', 'y': 0.5},
        'Pathway 2→3 Bridge\n(Research Question)': {'status': 'OPEN', 'color': 'orange', 'y': 0.35},
    }
    
    for comp, data in components.items():
        y = data['y']
        
        if data['status'] == 'QUARANTINE':
            facecolor = 'lightyellow'
            edgecolor = 'orange'
        else:  # OPEN
            facecolor = 'lightcoral'
            edgecolor = 'red'
        
        box = FancyBboxPatch((0.1, y-0.06), 0.35, 0.12,
                            boxstyle="round,pad=0.01",
                            facecolor=facecolor, edgecolor=edgecolor,
                            linewidth=2)
        ax.add_patch(box)
        
        ax.text(0.275, y, comp, ha='center', va='center', fontweight='bold', fontsize=11)
        ax.text(0.5, y, data['status'], ha='left', va='center', fontsize=12, fontweight='bold')
    
    # Add title
    ax.text(0.5, 0.95, 'PATH_3: Li Coefficients / Dual-Probe — Supporting Evidence Only', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Add demotion explanation
    demotion_text = """DEMOTION RATIONALE (March 2026):
Two of three reviewers warned against leading with this pathway:

1. STATISTICAL-ALGEBRAIC GAP:
   Pearson ρ ≈ 0.063 is an experimental observation.
   Pure mathematics requires deterministic algebraic statements.
   
2. NO KNOWN F₂ → λₙ MAP:
   Li coefficients defined via contour integrals of ξ(s).
   F₂_k values are local σ-curvatures of truncated polynomial.
   No literature formula connects F₂_k to λₙ directly.

CORRECT USAGE:
✓ Part III of paper (empirical motivation)  
✗ Analytic proof chain

NATURAL UPGRADE PATH:
If PATH_2 succeeds → Li follows via sech² ≈ hₙ approximation"""
    
    ax.text(0.05, 0.25, demotion_text, ha='left', va='top', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color='lightyellow', label='QUARANTINE (verification only)'),
        mpatches.Patch(color='lightcoral', label='OPEN (research question)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig(current_dir / 'path3_status_summary.png', dpi=300, bbox_inches='tight')
    plt.show()


def run_all_analytics() -> None:
    """
    Main function to run all PATH_3 analytics and generate visualizations.
    """
    print("=" * 60)
    print("PATH_3 ANALYTICS: Li Coefficients / Dual-Probe Visualizations")
    print("=" * 60)
    
    if not IMPORTS_OK:
        print("ERROR: Cannot import PATH_3 execution script.")
        print("Please ensure PATH_3_LI_DUAL_PROBE.py is working correctly.")
        return
    
    try:
        print("\n1. Generating Li Coefficients analysis...")
        plot_li_coefficients()
        
        print("\n2. Generating Dual Probe correlation analysis...")
        plot_dual_probe_correlation()
        
        print("\n3. Generating 9D coordinate structure analysis...")
        plot_9d_coordinate_structure()
        
        print("\n4. Generating pathway status summary...")
        plot_pathway_status_summary()
        
        print(f"\n✓ All visualizations saved to: {current_dir}")
        print("  - li_coefficients_analysis.png")
        print("  - dual_probe_correlation.png")  
        print("  - 9d_coordinate_analysis.png")
        print("  - path3_status_summary.png")
        
    except Exception as e:
        print(f"ERROR in analytics generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_analytics()