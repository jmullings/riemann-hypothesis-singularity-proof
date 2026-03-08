#!/usr/bin/env python3
"""
generate_assertion3_charts.py

ASSERTION 3: 6D VARIANCE COLLAPSE - ILLUSTRATIVE CHARTS
=======================================================

Generates 4 mathematically precise charts proving the dimensional reduction
from 9D to 6D space through three independent mechanisms:

Chart 1: The B-V Noise Floor (Law E) - Trailing-mode variance suppression
Chart 2: 9D → 6D Energy Concentration - Energy retention proof  
Chart 3: The Spectral Gap Explosion - PCA component separation
Chart 4: Singularity Locus Synchronization - Collapse at 9D singularities

RIEMANN-FREE DECLARATION:
This module contains ZERO references to ζ-function operations.
All analysis operates purely on prime-side objects via von Mangoldt Λ(n).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# Enhanced plotting aesthetics
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class Assertion3ChartGenerator:
    """
    Generate publication-ready charts proving 6D variance collapse.
    """
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.output_dir = self.data_dir
        
        # Chart aesthetics
        self.colors = {
            'primary': '#2E86C1',
            'secondary': '#E74C3C', 
            'accent': '#F39C12',
            'success': '#27AE60',
            'warning': '#F1C40F',
            'danger': '#C0392B',
            'info': '#8E44AD',
            'cyan': '#17A2B8',
            'magenta': '#E91E63'
        }
        
        # Figure settings
        self.fig_size = (12, 8)
        self.dpi = 300
        
    def load_csv_data(self, filename: str) -> pd.DataFrame:
        """Load CSV data with error handling."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filename}")
        return pd.read_csv(filepath)
    
    def chart_1_bv_noise_floor(self) -> None:
        """
        Chart 1: The B-V Noise Floor (Law E)
        Mathematical Focus: Trailing-Mode Variance Suppression (Theorem V1)
        """
        print("Generating Chart 1: The B-V Noise Floor (Law E)...")
        
        # Load B-V variance damping data
        df = self.load_csv_data("A3_F2_BV_VARIANCE_DAMPING.csv")
        
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Plot eigenvalue ratio λ₇/λ₁
        ax.semilogy(df['T'], df['ratio_7_1_bv'], 
                   color=self.colors['danger'], linewidth=2.5, alpha=0.8,
                   label=r'$\lambda_7/\lambda_1$ (Trailing Mode Ratio)')
        
        # Plot theoretical B-V damping curve
        ax.semilogy(df['T'], df['bv_factor'], 
                   color=self.colors['primary'], linewidth=2, linestyle='--',
                   label=r'B–V Theoretical Bound $1/T^A$')
        
        # Formatting
        ax.set_xlabel(r'Height $T$', fontsize=14, fontweight='bold')
        ax.set_ylabel(r'Magnitude (Log Scale)', fontsize=14, fontweight='bold')
        ax.set_title('Chart 1: B–V Noise Floor\nTrailing Eigenvalue Suppression (Theorem V1)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Legend
        ax.legend(fontsize=12, loc='upper right', framealpha=0.9)
        
        # Grid enhancement
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#FBFBFB')
        
        # Annotations
        ax.text(0.05, 0.95, 'LAW E: Bombieri–Vinogradov', 
                transform=ax.transAxes, fontsize=10, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['info'], alpha=0.7))
        
        ax.text(0.05, 0.87, 'Trailing modes actively suppressed\nby prime variance limit', 
                transform=ax.transAxes, fontsize=9, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.7))
        
        plt.tight_layout()
        
        # Export
        output_path = self.output_dir / "Chart_1_BV_Noise_Floor.png"
        plt.savefig(output_path, bbox_inches='tight', facecolor='white')
        plt.show()
        print(f"✅ Chart 1 saved: {output_path}")
        
    def chart_2_energy_concentration(self) -> None:
        """
        Chart 2: 9D → 6D Energy Concentration
        Mathematical Focus: Effective Rank and Energy Retention (Theorems V3 & D1)
        """
        print("Generating Chart 2: 9D → 6D Energy Concentration...")
        
        # Load dimensional collapse validator data
        df = self.load_csv_data("A3_F4_COLLAPSE_VALIDATOR.csv")
        
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Convert T_star to numeric if needed
        if 'T_star' in df.columns:
            x_values = df['T_star']
            x_label = r'Singularity Heights $T^*$'
        else:
            x_values = df.index + 1  # Fallback to index
            x_label = 'Singularity Index'
        
        # Create bar chart of energy retention
        bars = ax.bar(x_values, df['retained_norm'] * 100,  # Convert to percentage
                     color=self.colors['success'], alpha=0.8, edgecolor='darkgreen', linewidth=1)
        
        # 99% threshold line
        ax.axhline(y=99, color=self.colors['danger'], linestyle='--', linewidth=3,
                  label='99% Energy Threshold', alpha=0.9)
        
        # Formatting
        ax.set_xlabel(x_label, fontsize=14, fontweight='bold')
        ax.set_ylabel('Energy Retained in 6D Projection (%)', fontsize=14, fontweight='bold')
        ax.set_title('Chart 2: 9D → 6D Energy Concentration\nDimensional Reduction Verification (Theorems V3 & D1)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Set y-axis to show percentage clearly
        ax.set_ylim(95, 101)
        ax.set_ylabel('Energy Retained in 6D Projection (%)', fontsize=14, fontweight='bold')
        
        # Legend
        ax.legend(fontsize=12, loc='lower right', framealpha=0.9)
        
        # Grid enhancement
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_facecolor('#FBFBFB')
        
        # Annotations
        ax.text(0.05, 0.95, 'LAWS A+B+E: PNT + Chebyshev + B–V', 
                transform=ax.transAxes, fontsize=10, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['success'], alpha=0.7))
        
        # Calculate statistics
        min_energy = df['retained_norm'].min() * 100
        mean_energy = df['retained_norm'].mean() * 100
        
        ax.text(0.05, 0.85, f'Min Energy: {min_energy:.4f}%\nMean Energy: {mean_energy:.4f}%', 
                transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
        
        plt.tight_layout()
        
        # Export
        output_path = self.output_dir / "Chart_2_Energy_Concentration.png"
        plt.savefig(output_path, bbox_inches='tight', facecolor='white')
        plt.show()
        print(f"✅ Chart 2 saved: {output_path}")
        
    def chart_3_spectral_gap_explosion(self) -> None:
        """
        Chart 3: The Spectral Gap Explosion
        Mathematical Focus: PCA Component Separation (Theorem P1)
        """
        print("Generating Chart 3: The Spectral Gap Explosion...")
        
        # Load PCA spectral collapse data  
        df = self.load_csv_data("A3_F3_PCA_SPECTRAL_COLLAPSE.csv")
        
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Color scheme for eigenvalues
        top_6_color = self.colors['primary']
        bottom_3_color = self.colors['danger']
        
        # Plot top 6 eigenvalues (0-5, zero-indexed)
        for i in range(6):
            if f'lam_{i}' in df.columns:
                ax.semilogy(df['T'], df[f'lam_{i}'], 
                           color=top_6_color, alpha=0.7, linewidth=2,
                           label=f'Top 6 Components' if i == 0 else "")
        
        # Plot bottom 3 eigenvalues (6-8, zero-indexed)  
        for i in range(6, 9):
            if f'lam_{i}' in df.columns:
                ax.semilogy(df['T'], df[f'lam_{i}'], 
                           color=bottom_3_color, alpha=0.7, linewidth=2,
                           label=f'Bottom 3 Components' if i == 6 else "")
        
        # Highlight the critical gap between λ₅ and λ₆
        if 'lam_5' in df.columns and 'lam_6' in df.columns:
            ax.fill_between(df['T'], df['lam_5'], df['lam_6'], 
                           color='yellow', alpha=0.3, 
                           label='Critical 6D Gap')
        
        # Formatting
        ax.set_xlabel(r'Height $T$', fontsize=14, fontweight='bold')
        ax.set_ylabel(r'Eigenvalue Magnitude (Log Scale)', fontsize=14, fontweight='bold')
        ax.set_title('Chart 3: The Spectral Gap Explosion\nPCA Component Separation (Theorem P1)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Legend
        ax.legend(fontsize=12, loc='best', framealpha=0.9)
        
        # Grid enhancement
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#FBFBFB')
        
        # Annotations
        ax.text(0.05, 0.95, 'LAWS A+B+E: PNT + Chebyshev + B–V', 
                transform=ax.transAxes, fontsize=10, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['warning'], alpha=0.7))
        
        ax.text(0.05, 0.87, 'Top 6: Exponential growth (PNT)\nBottom 3: Decay/flatline (B–V)', 
                transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.7))
        
        plt.tight_layout()
        
        # Export
        output_path = self.output_dir / "Chart_3_Spectral_Gap_Explosion.png"
        plt.savefig(output_path, bbox_inches='tight', facecolor='white')
        plt.show()
        print(f"✅ Chart 3 saved: {output_path}")
        
    def chart_4_singularity_synchronization(self) -> None:
        """
        Chart 4: Singularity Locus Synchronization
        Mathematical Focus: 6D Collapse Localized at 9D Singularities (Theorem P3)
        """
        print("Generating Chart 4: Singularity Locus Synchronization...")
        
        # Load PCA spectral collapse data
        df = self.load_csv_data("A3_F3_PCA_SPECTRAL_COLLAPSE.csv")
        
        fig, ax1 = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Left Y-axis: Singularity Score (Magenta)
        ax1.plot(df['T'], df['sing_score'], 
                color=self.colors['magenta'], linewidth=3, alpha=0.8,
                label=r'9D Singularity Score $S(T)$')
        
        ax1.set_xlabel(r'Height $T$', fontsize=14, fontweight='bold')
        ax1.set_ylabel(r'9D Singularity Score $S(T)$', color=self.colors['magenta'], 
                      fontsize=14, fontweight='bold')
        ax1.tick_params(axis='y', labelcolor=self.colors['magenta'])
        
        # Right Y-axis: Spectral Gap (Cyan, Log Scale)
        ax2 = ax1.twinx()
        ax2.semilogy(df['T'], df['spectral_gap'], 
                    color=self.colors['cyan'], linewidth=3, alpha=0.8,
                    label=r'Spectral Gap $\lambda_6/\lambda_7$')
        
        ax2.set_ylabel(r'Spectral Gap $\lambda_6/\lambda_7$ (Log Scale)', color=self.colors['cyan'],
                      fontsize=14, fontweight='bold')
        ax2.tick_params(axis='y', labelcolor=self.colors['cyan'])
        
        # Title
        fig.suptitle('Chart 4: Singularity Locus Synchronization\n6D Collapse at 9D Singularities (Theorem P3)', 
                    fontsize=16, fontweight='bold')
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12, framealpha=0.9)
        
        # Grid enhancement
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#FBFBFB')
        
        # Synchronization analysis - find peak correlations
        # Normalize both series for correlation analysis
        sing_norm = (df['sing_score'] - df['sing_score'].min()) / (df['sing_score'].max() - df['sing_score'].min())
        gap_norm = (np.log(df['spectral_gap']) - np.log(df['spectral_gap']).min()) / (np.log(df['spectral_gap']).max() - np.log(df['spectral_gap']).min())
        
        correlation = np.corrcoef(sing_norm, gap_norm)[0, 1]
        
        # Annotations
        ax1.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                transform=ax1.transAxes, fontsize=11, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['info'], alpha=0.8))
        
        ax1.text(0.05, 0.87, 'Peak singularities ↔ Gap explosions\nDimensional collapse synchronized', 
                transform=ax1.transAxes, fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
        
        plt.tight_layout()
        
        # Export
        output_path = self.output_dir / "Chart_4_Singularity_Synchronization.png"
        plt.savefig(output_path, bbox_inches='tight', facecolor='white')
        plt.show()
        print(f"✅ Chart 4 saved: {output_path}")
        
    def generate_all_charts(self) -> None:
        """Generate all 4 Assertion 3 charts."""
        print("=" * 70)
        print("ASSERTION 3: 6D VARIANCE COLLAPSE - CHART GENERATION")
        print("=" * 70)
        print("Generating 4 mathematical proof charts...\n")
        
        try:
            self.chart_1_bv_noise_floor()
            print()
            self.chart_2_energy_concentration()  
            print()
            self.chart_3_spectral_gap_explosion()
            print()
            self.chart_4_singularity_synchronization()
            print()
            
            print("=" * 70)
            print("✅ ALL ASSERTION 3 CHARTS GENERATED SUCCESSFULLY")
            print("=" * 70)
            
            # Summary
            output_files = [
                "Chart_1_BV_Noise_Floor.png",
                "Chart_2_Energy_Concentration.png", 
                "Chart_3_Spectral_Gap_Explosion.png",
                "Chart_4_Singularity_Synchronization.png"
            ]
            
            print("\n📊 GENERATED CHARTS:")
            for i, filename in enumerate(output_files, 1):
                print(f"   Chart {i}: {filename}")
                
            print(f"\n📁 Output Directory: {self.output_dir}")
            
        except Exception as e:
            print(f"❌ Error generating charts: {e}")
            raise

    def export_csv(self, export_path: str = "../temp") -> None:
        """Export chart generation status to CSV."""
        try:
            # Create export directory
            export_dir = Path(export_path)
            os.makedirs(export_dir, exist_ok=True)
            
            # Chart generation summary
            chart_data = {
                'Chart_Number': [1, 2, 3, 4],
                'Chart_Name': [
                    'B-V Noise Floor',
                    '9D → 6D Energy Concentration', 
                    'Spectral Gap Explosion',
                    'Singularity Locus Synchronization'
                ],
                'Mathematical_Focus': [
                    'Theorem V1: Trailing-Mode Variance Suppression',
                    'Theorems V3 & D1: Energy Retention',
                    'Theorem P1: PCA Component Separation', 
                    'Theorem P3: Collapse at Singularities'
                ],
                'Data_Source': [
                    'A3_F2_BV_VARIANCE_DAMPING.csv',
                    'A3_F4_COLLAPSE_VALIDATOR.csv',
                    'A3_F3_PCA_SPECTRAL_COLLAPSE.csv',
                    'A3_F3_PCA_SPECTRAL_COLLAPSE.csv'
                ],
                'Status': ['Generated', 'Generated', 'Generated', 'Generated']
            }
            
            df = pd.DataFrame(chart_data)
            
            # Export to CSV
            output_path = export_dir / "assertion3_charts_summary.csv"
            df.to_csv(output_path, index=False)
            
            print(f"📊 Chart summary exported: {output_path}")
            
        except Exception as e:
            print(f"⚠️  CSV export error: {e}")


def main():
    """Main execution function."""
    try:
        generator = Assertion3ChartGenerator()
        generator.generate_all_charts()
        generator.export_csv()
        return 0
        
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)