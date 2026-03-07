"""
PLOT_CLAIM3_FIGURES.py
======================

Generate publication-quality figures for Claim 3: Singularity Core
Mechanism Architecture.

Reads CSV data from csv_data/ directory and generates:
1. Fig1: ψ(T) σ-profiles at zeros vs non-zeros
2. Fig2: |ψ(T)| distribution comparison
3. Fig3: 9D curvature heatmap by branch
4. Fig4: Geodesic criterion ROC and score distribution
5. Fig5: Phase velocity distribution
6. Fig6: Persistence ratio scatter plot
7. Fig7: |z80| discriminant comparison
8. Fig8: Summary dashboard

Author: CLAIM_3_SINGULARITY_CORE Analytics
Date: March 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Optional

# Get script directory for proper path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(SCRIPT_DIR, "csv_data")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "figures")

# PhD-quality matplotlib configuration
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'legend.fontsize': 9,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3,
})

# Color scheme
ZERO_COLOR = '#2E86AB'      # Blue for zeros
NON_ZERO_COLOR = '#E94F37'  # Red for non-zeros
CRITICAL_COLOR = '#F39C12'  # Gold for critical line
PHI_COLOR = '#8E44AD'       # Purple for φ-related

def ensure_output_dir():
    """Ensure output directory exists."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR

def load_csv(filename: str) -> Optional[pd.DataFrame]:
    """Load CSV file if it exists."""
    filepath = os.path.join(CSV_DIR, filename)
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    print(f"Warning: {filename} not found")
    return None

# ============================================================================
# FIGURE 1: ψ(T) σ-PROFILES
# ============================================================================

def plot_psi_profiles():
    """
    Figure 1: ψ(σ + iT) magnitude profiles demonstrating vector collapse.
    
    Shows that |ψ(σ + iT)| reaches minimum at σ = 1/2 for zeros,
    demonstrating the "vector collapse" mechanism.
    """
    df = load_csv("psi_profiles.csv")
    if df is None:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Zeros
    ax = axes[0]
    zeros_df = df[df['is_zero'] == True]
    for T in zeros_df['T'].unique():
        subset = zeros_df[zeros_df['T'] == T]
        ax.plot(subset['sigma'], subset['abs_psi'], 
               label=f'γ ≈ {T:.2f}', alpha=0.8)
    
    ax.axvline(0.5, color=CRITICAL_COLOR, linestyle='--', linewidth=2, 
               label='Critical Line σ=1/2')
    ax.set_xlabel(r'$\sigma$ (Real Part)')
    ax.set_ylabel(r'$|\psi(\sigma + iT)|$')
    ax.set_title('At Riemann Zeros: Vector Collapse at σ=1/2')
    ax.legend(fontsize=8, loc='upper right')
    ax.set_xlim(0.1, 0.9)
    
    # Right: Non-zeros
    ax = axes[1]
    non_zeros_df = df[df['is_zero'] == False]
    for T in non_zeros_df['T'].unique():
        subset = non_zeros_df[non_zeros_df['T'] == T]
        ax.plot(subset['sigma'], subset['abs_psi'], 
               label=f'T ≈ {T:.2f}', alpha=0.8, linestyle='--')
    
    ax.axvline(0.5, color=CRITICAL_COLOR, linestyle='--', linewidth=2,
               label='Critical Line σ=1/2')
    ax.set_xlabel(r'$\sigma$ (Real Part)')
    ax.set_ylabel(r'$|\psi(\sigma + iT)|$')
    ax.set_title('Off Zeros: Extended Profile (No Collapse)')
    ax.legend(fontsize=8, loc='upper right')
    ax.set_xlim(0.1, 0.9)
    
    plt.suptitle(r'Figure 1: $\psi(T)$ Partial Sum Magnitude Profiles', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Fig1_Psi_Profiles.png"))
    plt.close()
    print("  ✓ Fig1_Psi_Profiles.png")

# ============================================================================
# FIGURE 2: |ψ(T)| DISTRIBUTION
# ============================================================================

def plot_magnitude_distribution():
    """
    Figure 2: Distribution of |ψ(T)| at zeros vs non-zeros.
    """
    df = load_csv("magnitude_at_zeros.csv")
    if df is None:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Box plot comparison
    ax = axes[0]
    zeros_mag = df[df['is_zero'] == True]['abs_psi']
    non_zeros_mag = df[df['is_zero'] == False]['abs_psi']
    
    bp = ax.boxplot([zeros_mag, non_zeros_mag], 
                    labels=['At Zeros', 'Off Zeros'],
                    patch_artist=True)
    bp['boxes'][0].set_facecolor(ZERO_COLOR)
    bp['boxes'][1].set_facecolor(NON_ZERO_COLOR)
    
    ax.set_ylabel(r'$|\psi(T)|$')
    ax.set_title('Magnitude Distribution: Zeros vs Non-Zeros')
    
    # Right: Scatter plot by T
    ax = axes[1]
    zeros_df = df[df['is_zero'] == True]
    non_zeros_df = df[df['is_zero'] == False]
    
    ax.scatter(zeros_df['T'], zeros_df['abs_psi'], 
              c=ZERO_COLOR, label='At Zeros', alpha=0.7, s=50)
    ax.scatter(non_zeros_df['T'], non_zeros_df['abs_psi'], 
              c=NON_ZERO_COLOR, label='Off Zeros', alpha=0.5, s=30)
    
    ax.set_xlabel('T (Imaginary Part)')
    ax.set_ylabel(r'$|\psi(T)|$')
    ax.set_title(r'$|\psi(T)|$ Along the Critical Line')
    ax.legend()
    
    plt.suptitle(r'Figure 2: Partial Sum Magnitude $|\psi(T)|$ Analysis', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Fig2_Magnitude_Distribution.png"))
    plt.close()
    print("  ✓ Fig2_Magnitude_Distribution.png")

# ============================================================================
# FIGURE 3: 9D CURVATURE HEATMAP
# ============================================================================

def plot_curvature_heatmap():
    """
    Figure 3: 9D curvature component comparison between zeros and non-zeros.
    """
    df = load_csv("curvature_9d.csv")
    if df is None:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Compute mean curvature by branch for zeros and non-zeros
    zeros_curv = df[df['is_zero'] == True].pivot_table(
        values='curvature', index='T', columns='k', aggfunc='first'
    )
    non_zeros_curv = df[df['is_zero'] == False].pivot_table(
        values='curvature', index='T', columns='k', aggfunc='first'
    )
    
    # Left: Zeros heatmap
    ax = axes[0]
    sns.heatmap(zeros_curv.head(20), ax=ax, cmap='YlOrRd', 
                cbar_kws={'label': 'Curvature'})
    ax.set_xlabel('Branch k')
    ax.set_ylabel('T (Zero Location)')
    ax.set_title('9D Curvature at Zeros')
    
    # Right: Non-zeros heatmap
    ax = axes[1]
    sns.heatmap(non_zeros_curv.head(20), ax=ax, cmap='YlOrRd',
                cbar_kws={'label': 'Curvature'})
    ax.set_xlabel('Branch k')
    ax.set_ylabel('T (Non-Zero Location)')
    ax.set_title('9D Curvature Off Zeros')
    
    plt.suptitle('Figure 3: 9D Geodesic Curvature Structure', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Fig3_Curvature_Heatmap.png"))
    plt.close()
    print("  ✓ Fig3_Curvature_Heatmap.png")

# ============================================================================
# FIGURE 4: GEODESIC CRITERION PERFORMANCE
# ============================================================================

def plot_geodesic_criterion():
    """
    Figure 4: Geodesic criterion classification performance.
    """
    df = load_csv("geodesic_criterion.csv")
    if df is None:
        return
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Left: Score distribution
    ax = axes[0]
    zeros_scores = df[df['is_zero_true'] == True]['criterion_score']
    non_zeros_scores = df[df['is_zero_true'] == False]['criterion_score']
    
    ax.hist(zeros_scores, bins=20, alpha=0.7, color=ZERO_COLOR, 
           label='Zeros', density=True)
    ax.hist(non_zeros_scores, bins=20, alpha=0.7, color=NON_ZERO_COLOR,
           label='Non-Zeros', density=True)
    ax.axvline(6.14, color='black', linestyle='--', linewidth=2,
              label='Threshold (6.14)')
    ax.set_xlabel('Criterion Score')
    ax.set_ylabel('Density')
    ax.set_title('Score Distribution')
    ax.legend()
    
    # Middle: Confusion matrix style
    ax = axes[1]
    tp = sum((df['is_zero_true'] == True) & (df['is_zero_predicted'] == True))
    fp = sum((df['is_zero_true'] == False) & (df['is_zero_predicted'] == True))
    tn = sum((df['is_zero_true'] == False) & (df['is_zero_predicted'] == False))
    fn = sum((df['is_zero_true'] == True) & (df['is_zero_predicted'] == False))
    
    conf_matrix = np.array([[tp, fn], [fp, tn]])
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', ax=ax,
               xticklabels=['Pred Zero', 'Pred Non-Zero'],
               yticklabels=['True Zero', 'True Non-Zero'])
    ax.set_title('Classification Results')
    
    # Right: Feature importance (scatter)
    ax = axes[2]
    ax.scatter(df['darg_dt'], df['z80_abs'], 
              c=df['is_zero_true'].map({True: ZERO_COLOR, False: NON_ZERO_COLOR}),
              alpha=0.6, s=40)
    ax.set_xlabel(r'Phase Velocity $|d\arg/dT|$')
    ax.set_ylabel(r'Discriminant $|z_{80}|$')
    ax.set_title('Feature Space Separation')
    
    # Add legend
    ax.scatter([], [], c=ZERO_COLOR, label='Zeros')
    ax.scatter([], [], c=NON_ZERO_COLOR, label='Non-Zeros')
    ax.legend()
    
    plt.suptitle('Figure 4: Geodesic Zero Criterion Performance (F1 ≈ 0.65)', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Fig4_Geodesic_Criterion.png"))
    plt.close()
    print("  ✓ Fig4_Geodesic_Criterion.png")

# ============================================================================
# FIGURE 5: PHASE VELOCITY
# ============================================================================

def plot_phase_velocity():
    """
    Figure 5: Phase velocity |darg/dT| distribution.
    """
    df = load_csv("phase_velocity.csv")
    if df is None:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Box plot
    ax = axes[0]
    zeros_pv = df[df['is_zero'] == True]['phase_velocity']
    non_zeros_pv = df[df['is_zero'] == False]['phase_velocity']
    
    bp = ax.boxplot([zeros_pv, non_zeros_pv], 
                   labels=['At Zeros', 'Off Zeros'],
                   patch_artist=True)
    bp['boxes'][0].set_facecolor(ZERO_COLOR)
    bp['boxes'][1].set_facecolor(NON_ZERO_COLOR)
    
    ax.set_ylabel(r'Phase Velocity $|d\arg\psi/dT|$')
    ax.set_title('Phase Velocity Distribution')
    
    # Right: Time series
    ax = axes[1]
    zeros_df = df[df['is_zero'] == True].sort_values('T')
    non_zeros_df = df[df['is_zero'] == False].sort_values('T')
    
    ax.scatter(zeros_df['T'], zeros_df['phase_velocity'], 
              c=ZERO_COLOR, label='At Zeros', alpha=0.7, s=50)
    ax.scatter(non_zeros_df['T'], non_zeros_df['phase_velocity'],
              c=NON_ZERO_COLOR, label='Off Zeros', alpha=0.5, s=30)
    
    ax.set_xlabel('T')
    ax.set_ylabel(r'$|d\arg\psi/dT|$')
    ax.set_title('Phase Velocity vs T')
    ax.legend()
    
    plt.suptitle('Figure 5: Phase Velocity Analysis', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Fig5_Phase_Velocity.png"))
    plt.close()
    print("  ✓ Fig5_Phase_Velocity.png")

# ============================================================================
# FIGURE 6: PERSISTENCE RATIOS
# ============================================================================

def plot_persistence_ratios():
    """
    Figure 6: Persistence ratios ρ₂, ρ₄ scatter plot.
    """
    df = load_csv("persistence_ratios.csv")
    if df is None:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: ρ₂ vs ρ₄ scatter
    ax = axes[0]
    zeros_df = df[df['is_zero'] == True]
    non_zeros_df = df[df['is_zero'] == False]
    
    ax.scatter(zeros_df['rho2'], zeros_df['rho4'], 
              c=ZERO_COLOR, label='At Zeros', alpha=0.7, s=50)
    ax.scatter(non_zeros_df['rho2'], non_zeros_df['rho4'],
              c=NON_ZERO_COLOR, label='Off Zeros', alpha=0.5, s=30)
    
    ax.set_xlabel(r'$\rho_2 = \kappa_2/\kappa_1$')
    ax.set_ylabel(r'$\rho_4 = \kappa_4/\kappa_1$')
    ax.set_title('Persistence Ratio Space')
    ax.legend()
    
    # Right: ρ₄ distribution
    ax = axes[1]
    zeros_rho4 = df[df['is_zero'] == True]['rho4']
    non_zeros_rho4 = df[df['is_zero'] == False]['rho4']
    
    ax.hist(zeros_rho4, bins=15, alpha=0.7, color=ZERO_COLOR,
           label='At Zeros', density=True)
    ax.hist(non_zeros_rho4, bins=15, alpha=0.7, color=NON_ZERO_COLOR,
           label='Off Zeros', density=True)
    
    ax.set_xlabel(r'$\rho_4 = \kappa_4/\kappa_1$')
    ax.set_ylabel('Density')
    ax.set_title(r'$\rho_4$ Distribution')
    ax.legend()
    
    plt.suptitle('Figure 6: Multi-Scale Persistence Ratios', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Fig6_Persistence_Ratios.png"))
    plt.close()
    print("  ✓ Fig6_Persistence_Ratios.png")

# ============================================================================
# FIGURE 7: |z80| DISCRIMINANT
# ============================================================================

def plot_z80_discriminant():
    """
    Figure 7: |z80| discriminant analysis.
    """
    df = load_csv("z80_discriminant.csv")
    if df is None:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Distribution comparison
    ax = axes[0]
    zeros_z80 = df[df['is_zero'] == True]['z80_abs']
    non_zeros_z80 = df[df['is_zero'] == False]['z80_abs']
    
    ax.hist(zeros_z80, bins=15, alpha=0.7, color=ZERO_COLOR,
           label='At Zeros', density=True)
    ax.hist(non_zeros_z80, bins=15, alpha=0.7, color=NON_ZERO_COLOR,
           label='Off Zeros', density=True)
    
    ax.set_xlabel(r'$|z_{80}|$ (80-term partial sum)')
    ax.set_ylabel('Density')
    ax.set_title(r'$|z_{80}|$ Distribution')
    ax.legend()
    
    # Right: vs T
    ax = axes[1]
    zeros_df = df[df['is_zero'] == True].sort_values('T')
    non_zeros_df = df[df['is_zero'] == False].sort_values('T')
    
    ax.scatter(zeros_df['T'], zeros_df['z80_abs'], 
              c=ZERO_COLOR, label='At Zeros', alpha=0.7, s=50)
    ax.scatter(non_zeros_df['T'], non_zeros_df['z80_abs'],
              c=NON_ZERO_COLOR, label='Off Zeros', alpha=0.5, s=30)
    
    ax.set_xlabel('T')
    ax.set_ylabel(r'$|z_{80}|$')
    ax.set_title(r'$|z_{80}|$ Discriminant vs T')
    ax.legend()
    
    plt.suptitle('Figure 7: 80-Term Partial Sum Discriminant', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Fig7_Z80_Discriminant.png"))
    plt.close()
    print("  ✓ Fig7_Z80_Discriminant.png")

# ============================================================================
# FIGURE 8: SUMMARY DASHBOARD
# ============================================================================

def plot_summary_dashboard():
    """
    Figure 8: Comprehensive summary dashboard.
    """
    fig = plt.figure(figsize=(16, 12))
    
    # Load all data
    gc_df = load_csv("geodesic_criterion.csv")
    pv_df = load_csv("phase_velocity.csv")
    pr_df = load_csv("persistence_ratios.csv")
    z80_df = load_csv("z80_discriminant.csv")
    
    if gc_df is None:
        return
    
    # Calculate metrics
    tp = sum((gc_df['is_zero_true'] == True) & (gc_df['is_zero_predicted'] == True))
    fp = sum((gc_df['is_zero_true'] == False) & (gc_df['is_zero_predicted'] == True))
    fn = sum((gc_df['is_zero_true'] == True) & (gc_df['is_zero_predicted'] == False))
    tn = sum((gc_df['is_zero_true'] == False) & (gc_df['is_zero_predicted'] == False))
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    # Top row: Main findings
    ax1 = fig.add_subplot(2, 3, 1)
    zeros_scores = gc_df[gc_df['is_zero_true'] == True]['criterion_score']
    non_zeros_scores = gc_df[gc_df['is_zero_true'] == False]['criterion_score']
    ax1.hist(zeros_scores, bins=15, alpha=0.7, color=ZERO_COLOR, label='Zeros')
    ax1.hist(non_zeros_scores, bins=15, alpha=0.7, color=NON_ZERO_COLOR, label='Non-Zeros')
    ax1.axvline(6.14, color='black', linestyle='--', label='Threshold')
    ax1.set_xlabel('Criterion Score')
    ax1.set_title('Geodesic Criterion Scores')
    ax1.legend(fontsize=8)
    
    # Confusion matrix
    ax2 = fig.add_subplot(2, 3, 2)
    conf_matrix = np.array([[tp, fn], [fp, tn]])
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', ax=ax2,
               xticklabels=['Pred +', 'Pred -'], yticklabels=['True +', 'True -'])
    ax2.set_title(f'Confusion Matrix\nF1={f1:.2f}, Prec={precision:.2f}, Rec={recall:.2f}')
    
    # Feature space
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.scatter(gc_df['darg_dt'], gc_df['z80_abs'], 
               c=gc_df['is_zero_true'].map({True: ZERO_COLOR, False: NON_ZERO_COLOR}),
               alpha=0.6, s=30)
    ax3.set_xlabel(r'$|d\arg/dT|$')
    ax3.set_ylabel(r'$|z_{80}|$')
    ax3.set_title('Feature Space')
    
    # Bottom row: Supporting evidence
    if pv_df is not None:
        ax4 = fig.add_subplot(2, 3, 4)
        bp = ax4.boxplot([pv_df[pv_df['is_zero']==True]['phase_velocity'],
                         pv_df[pv_df['is_zero']==False]['phase_velocity']],
                        labels=['Zeros', 'Non-Zeros'], patch_artist=True)
        bp['boxes'][0].set_facecolor(ZERO_COLOR)
        bp['boxes'][1].set_facecolor(NON_ZERO_COLOR)
        ax4.set_ylabel('Phase Velocity')
        ax4.set_title('Phase Velocity Separation')
    
    if pr_df is not None:
        ax5 = fig.add_subplot(2, 3, 5)
        ax5.scatter(pr_df[pr_df['is_zero']==True]['rho2'], 
                   pr_df[pr_df['is_zero']==True]['rho4'],
                   c=ZERO_COLOR, label='Zeros', alpha=0.7)
        ax5.scatter(pr_df[pr_df['is_zero']==False]['rho2'],
                   pr_df[pr_df['is_zero']==False]['rho4'],
                   c=NON_ZERO_COLOR, label='Non-Zeros', alpha=0.5)
        ax5.set_xlabel(r'$\rho_2$')
        ax5.set_ylabel(r'$\rho_4$')
        ax5.set_title('Persistence Ratios')
        ax5.legend(fontsize=8)
    
    if z80_df is not None:
        ax6 = fig.add_subplot(2, 3, 6)
        bp = ax6.boxplot([z80_df[z80_df['is_zero']==True]['z80_abs'],
                         z80_df[z80_df['is_zero']==False]['z80_abs']],
                        labels=['Zeros', 'Non-Zeros'], patch_artist=True)
        bp['boxes'][0].set_facecolor(ZERO_COLOR)
        bp['boxes'][1].set_facecolor(NON_ZERO_COLOR)
        ax6.set_ylabel(r'$|z_{80}|$')
        ax6.set_title(r'$|z_{80}|$ Discriminant')
    
    plt.suptitle('Figure 8: Claim 3 Singularity Core — Summary Dashboard', 
                fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Fig8_Summary_Dashboard.png"))
    plt.close()
    print("  ✓ Fig8_Summary_Dashboard.png")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all figures for Claim 3."""
    print("Generating Claim 3 figures...")
    
    ensure_output_dir()
    
    # Check if CSV directory exists
    if not os.path.exists(CSV_DIR):
        print(f"Error: CSV directory not found: {CSV_DIR}")
        print("Run BUILD_CLAIM3_DATA.py first to generate data.")
        return
    
    # Generate all figures
    plot_psi_profiles()
    plot_magnitude_distribution()
    plot_curvature_heatmap()
    plot_geodesic_criterion()
    plot_phase_velocity()
    plot_persistence_ratios()
    plot_z80_discriminant()
    plot_summary_dashboard()
    
    print("")
    print(f"All figures saved to: {OUTPUT_DIR}/")
    print("Done!")

if __name__ == "__main__":
    main()
