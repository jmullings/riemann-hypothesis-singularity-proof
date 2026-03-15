#!/usr/bin/env python3
"""
FORMAL_PROOF_NEW/SELECTIVITY/PATH_2/ANALYTICS/ANALYTICS.py
==========================================================

**STATUS: ANALYTICAL SUPPORT — March 14, 2026** 
**Purpose: Charts and illustrations for PATH_2 Weil Explicit Formula analysis**
**Protocols: P1-P5 compliant analytical visualization**

This module provides analytical visualization for the Weil Explicit Formula
pathway, showing kernel properties, weight corrections, T-averaging behavior,
and the three theorem verification results.

=============================================================================
VISUALIZATIONS PROVIDED
=============================================================================

1. Theorem A Verification: sech² kernel properties and Fourier transform
2. Theorem B Analysis: log-weighted polynomial and curvature behavior  
3. Theorem C Trends: T-averaged energy and Montgomery-Vaughan estimates
4. Strip Condition: holomorphicity analysis and A5' gap visualization
5. Weight Comparison: D vs D̃ energy profiles across sigma
6. Open Problems: Visual summary of A5', B5, C5-C6 gaps

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
    from PATH_2_WEIL_EXPLICIT import (
        verify_theorem_a, verify_theorem_b, verify_theorem_c,
        h_kernel, h_kernel_fourier, sech2, 
        D_tilde, E_tilde, F2_tilde,
        mv_average_analytic, d2_mv_d_sigma2,
        LAMBDA_STAR, PHI, ZEROS_9, PRIMES_100,
        POLE_STRIP_WIDTH, WEIL_STRIP_REQ
    )
    IMPORTS_OK = True
except ImportError as e:
    print(f"Warning: PATH_2 imports failed: {e}")
    IMPORTS_OK = False

# ============================================================================
# ANALYTICAL VISUALIZATION FUNCTIONS
# ============================================================================

def plot_kernel_properties() -> None:
    """
    Theorem A visualization: sech² kernel and its Fourier transform.
    Shows evenness, positivity, decay, and strip condition gap.
    """
    if not IMPORTS_OK:
        print("Skipping kernel properties plot - imports failed")
        return
        
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Panel 1: sech²(αt) kernel
    t_vals = np.linspace(-5, 5, 1000)
    h_vals = [h_kernel(t) for t in t_vals]
    
    ax1.plot(t_vals, h_vals, 'b-', linewidth=2, label=f'h(t) = sech²({LAMBDA_STAR:.0f}·t)')
    ax1.set_xlabel('t')
    ax1.set_ylabel('h(t)')
    ax1.set_title('Theorem A1-A2: sech² Kernel (Even + Real)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Panel 2: Fourier transform ĥ(ω)
    omega_vals = np.linspace(0, 1000, 500)
    h_hat_vals = [h_kernel_fourier(w) for w in omega_vals]
    
    ax2.semilogy(omega_vals, h_hat_vals, 'r-', linewidth=2, label='ĥ(ω) = (π/α²)·|ω|·csch(π|ω|/2α)')
    ax2.set_xlabel('ω')
    ax2.set_ylabel('ĥ(ω)')
    ax2.set_title('Theorem A3-A4: Fourier Transform (≥0 + L¹)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Panel 3: Strip condition gap
    strip_data = ['Standard Weil\nRequirement', 'Our sech²\nKernel', 'Gap Width']
    strip_values = [WEIL_STRIP_REQ, POLE_STRIP_WIDTH, WEIL_STRIP_REQ - POLE_STRIP_WIDTH]
    colors = ['green', 'orange', 'red']
    
    bars = ax3.bar(strip_data, strip_values, color=colors, alpha=0.7)
    ax3.set_ylabel('Strip Width')
    ax3.set_title('Theorem A5\': Strip Condition Gap')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value annotations
    for bar, val in zip(bars, strip_values):
        height = bar.get_height()
        ax3.annotate(f'{val:.4f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords='offset points', ha='center', va='bottom')
    
    # Panel 4: Status summary
    ax4.axis('off')
    status_text = """THEOREM A STATUS:
    
A1 (Even): ✓ PROVED analytically
A2 (Real): ✓ PROVED analytically  
A3 (ĥ≥0): ✓ PROVED analytically
A4 (L¹):   ✓ PROVED analytically
A5 (Strip): VERIFIED (0.00318)
A5':       ⚠ OPEN — distributional formula needed

CRITICAL BRIDGE: sech² kernel requires
distributional Weil explicit formula"""
    
    ax4.text(0.05, 0.95, status_text, transform=ax4.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(current_dir / 'theorem_a_kernel_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_weight_correction() -> None:
    """
    Theorem B visualization: log-weighted polynomial vs uniform weights.
    Shows D vs D̃ energy profiles and curvature behavior.
    """
    if not IMPORTS_OK:
        print("Skipping weight correction plot - imports failed")
        return
        
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Panel 1: Energy comparison D vs D̃
    sigma_range = np.linspace(0.3, 0.8, 50)
    T_test = ZEROS_9[0]  # use first zero for comparison
    
    E_uniform = [E_tilde(s, T_test) for s in sigma_range]  # Actually this uses log weights already
    # We need to simulate uniform weights for comparison
    E_uniform_approx = [sum(p**(-2*s) for p in PRIMES_100[:25]) for s in sigma_range]
    
    ax1.semilogy(sigma_range, E_uniform_approx, 'b-', linewidth=2, label='E(σ,T) uniform weights')  
    ax1.semilogy(sigma_range, E_uniform, 'r-', linewidth=2, label='Ẽ(σ,T) log weights')
    ax1.axvline(0.5, color='black', linestyle='--', alpha=0.5, label='σ = ½')
    ax1.set_xlabel('σ')
    ax1.set_ylabel('Energy (log scale)')
    ax1.set_title('Theorem B: Weight Correction Effect')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Panel 2: F₂ curvature at known zeros
    f2_values = []
    zero_labels = []
    for i, T in enumerate(ZEROS_9[:6]):  # First 6 zeros for clarity
        f2 = F2_tilde(0.5, T)
        f2_values.append(f2)
        zero_labels.append(f'γ_{i+1}')
    
    bars = ax2.bar(zero_labels, f2_values, color='purple', alpha=0.7)
    ax2.set_ylabel('∂²Ẽ/∂σ² at σ=½')
    ax2.set_title('Theorem B2: Curvature at Known Zeros [QUARANTINE]')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value annotations
    for bar, val in zip(bars, f2_values):
        height = bar.get_height()
        ax2.annotate(f'{val:.0f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords='offset points', ha='center', va='bottom')
    
    # Panel 3: Montgomery-Vaughan T-averaged energy
    mv_values = [mv_average_analytic(s) for s in sigma_range]
    ax3.semilogy(sigma_range, mv_values, 'g-', linewidth=2, label='⟨Ẽ(σ;X)⟩_T ≈ Σ log²(p)·p^{-2σ}')
    ax3.axvline(0.5, color='black', linestyle='--', alpha=0.5, label='σ = ½')
    ax3.set_xlabel('σ')
    ax3.set_ylabel('T-averaged Energy')
    ax3.set_title('Theorem C1: Montgomery-Vaughan Estimate')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Panel 4: Curvature behavior
    d2_values = [d2_mv_d_sigma2(s) for s in sigma_range]
    ax4.semilogy(sigma_range, d2_values, 'm-', linewidth=2, label='∂²⟨Ẽ⟩/∂σ² = 4·Σ log⁴(p)·p^{-2σ}')
    ax4.axvline(0.5, color='black', linestyle='--', alpha=0.5, label='σ = ½')
    ax4.set_xlabel('σ')
    ax4.set_ylabel('T-averaged Curvature')
    ax4.set_title('Theorem C2/C4: Curvature Positivity (Monotone Decreasing)')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig(current_dir / 'theorem_bc_weight_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_open_problems_summary() -> None:
    """
    Visual summary of the four open problems in PATH_2.
    Shows the conditional proof structure and remaining gaps.
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.axis('off')
    
    # Define theorem status
    theorems = {
        'A1-A4': {'status': 'PROVED', 'color': 'green', 'desc': 'Kernel properties\n(even, ≥0, L¹)'},
        'A5\'': {'status': 'OPEN', 'color': 'red', 'desc': 'Distributional formula\n(strip 0.003 < 0.5)'},
        'B1,B4': {'status': 'PROVED', 'color': 'green', 'desc': 'Weight matching\n(log(p) weights)'},
        'B2': {'status': 'VERIFIED', 'color': 'orange', 'desc': 'Curvature ∂²Ẽ/∂σ²>0\n[QUARANTINE: 9 zeros]'},
        'B5': {'status': 'OPEN', 'color': 'red', 'desc': 'Averaged curvature\n(analytic proof)'},
        'C1-C4': {'status': 'PROVED', 'color': 'green', 'desc': 'MV estimates\n(T-averaging)'},
        'C5': {'status': 'OPEN', 'color': 'red', 'desc': 'Explicit formula bridge\n(D̃ → ζ as X→∞)'},
        'C6': {'status': 'OPEN', 'color': 'red', 'desc': 'Off-critical contradiction\n(THE CRUX)'},
    }
    
    # Create boxes for each theorem
    y_positions = np.linspace(0.8, 0.2, len(theorems))
    x_positions = [0.15, 0.35, 0.15, 0.35, 0.55, 0.15, 0.35, 0.55]
    
    for i, (thm, data) in enumerate(theorems.items()):
        x = x_positions[i]
        y = y_positions[i] if i < 4 else y_positions[i-4]
        
        # Color coding
        if data['status'] == 'PROVED':
            facecolor = 'lightgreen'
            edgecolor = 'green'
        elif data['status'] == 'VERIFIED':
            facecolor = 'lightyellow' 
            edgecolor = 'orange'
        else:  # OPEN
            facecolor = 'lightcoral'
            edgecolor = 'red'
        
        # Create fancy box
        box = FancyBboxPatch((x-0.08, y-0.06), 0.16, 0.12,
                            boxstyle="round,pad=0.01",
                            facecolor=facecolor, edgecolor=edgecolor,
                            linewidth=2)
        ax.add_patch(box)
        
        # Add theorem label
        ax.text(x, y+0.03, thm, ha='center', va='center', fontweight='bold', fontsize=12)
        ax.text(x, y-0.02, data['status'], ha='center', va='center', fontsize=10)
        
        # Add description to the side
        ax.text(x+0.12, y, data['desc'], ha='left', va='center', fontsize=9)
    
    # Add title and summary
    ax.text(0.5, 0.95, 'PATH_2: Weil Explicit Formula — Conditional Proof Status', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Add conditional statement
    conditional_text = """CONDITIONAL FRAMEWORK:
IF A5' + B5 + C5 + C6 could be solved,
THEN PATH_2 would yield a proof of RH.

CURRENT STATUS: 6/10 components proved
OPEN PROBLEMS: 4 critical gaps remain"""
    
    ax.text(0.75, 0.45, conditional_text, ha='left', va='center', fontsize=11,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color='lightgreen', label='PROVED'),
        mpatches.Patch(color='lightyellow', label='VERIFIED [QUARANTINE]'),  
        mpatches.Patch(color='lightcoral', label='OPEN')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig(current_dir / 'path2_status_summary.png', dpi=300, bbox_inches='tight')
    plt.show()


def run_all_analytics() -> None:
    """
    Main function to run all PATH_2 analytics and generate visualizations.
    """
    print("=" * 60)
    print("PATH_2 ANALYTICS: Weil Explicit Formula Visualizations")
    print("=" * 60)
    
    if not IMPORTS_OK:
        print("ERROR: Cannot import PATH_2 execution script.")
        print("Please ensure PATH_2_WEIL_EXPLICIT.py is working correctly.")
        return
    
    try:
        print("\n1. Generating Theorem A (Kernel Properties) analysis...")
        plot_kernel_properties()
        
        print("\n2. Generating Theorem B & C (Weight Correction) analysis...")
        plot_weight_correction()
        
        print("\n3. Generating Open Problems summary...")
        plot_open_problems_summary()
        
        print(f"\n✓ All visualizations saved to: {current_dir}")
        print("  - theorem_a_kernel_analysis.png")
        print("  - theorem_bc_weight_analysis.png")  
        print("  - path2_status_summary.png")
        
    except Exception as e:
        print(f"ERROR in analytics generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_analytics()