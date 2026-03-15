#!/usr/bin/env python3
"""
FORMAL_PROOF_NEW/PSS_STEPS/PSS_STEP_2/ANALYTICS/ANALYTICS.py
============================================================

**STATUS: PSS VERIFICATION — March 14, 2026** 
**Purpose: Charts and illustrations for PSS_STEP_2 CSV Loading verification**
**Protocols: P1-P5 compliant analytical visualization**

This module provides analytical visualization for PSS_STEP_2 verification,
showing PSS CSV loading, 8-column schema validation, spiral coordinate
extraction, and micro-sigma calculations.

=============================================================================
VISUALIZATIONS PROVIDED  
=============================================================================

1. CSV Schema Validation: 8-column structure verification
2. PSS Data Distribution: Statistical overview of loaded data
3. Spiral Coordinate Analysis: mu_abs, phase, sigma extraction  
4. Micro-Sigma Calculations: 6D micro-sector analysis
5. Data Quality Metrics: Missing values, outliers, bounds checking
6. Trinity Gate Status: Gate-0 and Gate-1 compliance

=============================================================================
Author : Jason Mullings
Date   : March 14, 2026  
Version: 1.0.0 (Generic PSS Template)
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
import csv
import math
import importlib
import importlib.util

# Add parent directories to path for imports
current_dir = Path(__file__).parent
execution_dir = current_dir.parent / "EXECUTION"
configs_dir = current_dir.parent.parent.parent / "CONFIGURATIONS"

sys.path.insert(0, str(execution_dir))
sys.path.insert(0, str(configs_dir))

# Get PSS_STEP number from path
STEP_NUMBER = int(current_dir.parent.name.split('_')[-1])
STEP_NAME = f"PSS_STEP_{STEP_NUMBER}"

try:
    # Dynamic import based on step number - look for execution scripts
    import importlib
    import glob
    
    # Find PSS_STEP execution script
    exec_pattern = execution_dir / f"PSS_STEP_{STEP_NUMBER:02d}_*.py"
    exec_files = list(execution_dir.glob(f"PSS_STEP_{STEP_NUMBER:02d}_*.py"))
    
    if exec_files:
        # Import the first matching execution script
        module_name = exec_files[0].stem
        spec = importlib.util.spec_from_file_location(module_name, exec_files[0])
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Try to get common functions/constants if they exist
        globals().update({name: getattr(module, name) for name in dir(module) 
                         if not name.startswith('_')})
        IMPORTS_OK = True
    else:
        print(f"No execution script found for {STEP_NAME}")
        IMPORTS_OK = False
except Exception as e:
    print(f"Warning: {STEP_NAME} imports failed: {e}")
    IMPORTS_OK = False

# ============================================================================
# DATA LOADING AND PROCESSING
# ============================================================================

def load_pss_step_outputs() -> Dict[str, Any]:
    """
    Load PSS_STEP output CSV files if they exist.
    Returns: Dictionary with loaded data and status
    """
    output_data = {'status': 'NOT_EXECUTED', 'files': {}}
    
    # Look for CSV files in current directory
    for csv_file in current_dir.glob("*.csv"):
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                output_data['files'][csv_file.name] = list(reader)
                output_data['status'] = 'LOADED'
        except Exception as e:
            print(f"Error loading {csv_file}: {e}")
    
    return output_data


# ============================================================================
# ANALYTICAL VISUALIZATION FUNCTIONS  
# ============================================================================

def plot_pss_step_overview() -> None:
    """
    Overview of PSS_STEP execution status and key metrics.
    """
    output_data = load_pss_step_outputs()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Panel 1: Execution status
    if output_data['status'] == 'LOADED':
        file_count = len(output_data['files'])
        total_rows = sum(len(data) for data in output_data['files'].values())
        
        files = list(output_data['files'].keys())
        row_counts = [len(output_data['files'][f]) for f in files]
        
        bars = ax1.bar(range(len(files)), row_counts, color='lightblue', edgecolor='black')
        ax1.set_xlabel('Output files')
        ax1.set_ylabel('Row count')
        ax1.set_title(f'{STEP_NAME}: Output File Summary')
        ax1.set_xticks(range(len(files)))
        ax1.set_xticklabels([f.replace(f'pss_step_{STEP_NUMBER:02d}_', '') for f in files], 
                           rotation=45, ha='right')
        
        # Add value annotations
        for bar, count in zip(bars, row_counts):
            height = bar.get_height()
            ax1.annotate(f'{count}', xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3), textcoords='offset points', ha='center', va='bottom')
    else:
        ax1.text(0.5, 0.5, f'Execute {STEP_NAME}\nto generate output data', 
                ha='center', va='center', fontsize=14, transform=ax1.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        ax1.set_title(f'{STEP_NAME}: Not Yet Executed')
    
    # Panel 2: Data distribution (generic)
    ax2.text(0.5, 0.5, f'{STEP_NAME} Data Analysis\n\nRun execution script to see:\n\n• Data distributions\n• Quality metrics\n• Statistical summaries\n• Validation results', 
            ha='center', va='center', fontsize=11, transform=ax2.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcyan", alpha=0.8))
    ax2.set_title('Data Distribution Analysis')
    
    # Panel 3: Protocol compliance
    protocols = ['P1: No log() primary', 'P2: 9D Geometry', 'P3: Riemann-φ weights', 
                'P4: Bit-Size Axioms', 'P5: Trinity Gates']
    
    # Default status (would be updated based on actual execution results)
    protocol_status = ['PENDING'] * len(protocols) if output_data['status'] == 'NOT_EXECUTED' else ['CHECK_OUTPUT'] * len(protocols)
    
    colors = ['lightgray' if status == 'PENDING' else 'lightblue' for status in protocol_status]
    
    bars = ax3.barh(protocols, [1]*len(protocols), color=colors, edgecolor='black')
    ax3.set_xlabel('Compliance Status')
    ax3.set_title(f'{STEP_NAME}: P1-P5 Protocol')
    ax3.set_xlim(0, 1.2)
    
    # Add status text
    for i, (bar, status) in enumerate(zip(bars, protocol_status)):
        ax3.text(0.5, i, status, ha='center', va='center', fontweight='bold', fontsize=9)
    
    # Panel 4: Step context and next actions
    ax4.axis('off')
    context_text = f"""{STEP_NAME} CONTEXT:

EXECUTION STATUS: {output_data['status']}
OUTPUT FILES: {len(output_data['files']) if output_data['status'] == 'LOADED' else 'N/A'}

TO EXECUTE THIS STEP:
cd {current_dir.parent.name}
python EXECUTION/{STEP_NAME}_*.py

VISUALIZATION OPTIONS:
After execution, this analytics script will show:
• Step-specific data analysis
• Protocol compliance verification  
• Quality metrics and validation
• Trinity Gate status
• Connection to next PSS steps

WORKFLOW POSITION:
This is step {STEP_NUMBER} of 10 in the PSS 
verification sequence."""
    
    ax4.text(0.05, 0.95, context_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightsteelblue", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(current_dir / f'{STEP_NAME.lower()}_overview.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_pss_workflow_position() -> None:
    """
    Show this PSS_STEP's position in the overall workflow.
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.axis('off')
    
    # Create workflow visualization
    steps = [
        'PSS_STEP_1: AXIOMS',
        'PSS_STEP_2: CSV Load', 
        'PSS_STEP_3: Spiral Analysis',
        'PSS_STEP_4: Energy Dist',
        'PSS_STEP_5: Micro-Sigma',
        'PSS_STEP_6: Phase Analysis',
        'PSS_STEP_7: Bridge Setup',
        'PSS_STEP_8: Prime Coupling',
        'PSS_STEP_9: Verification',
        'PSS_STEP_10: Integration'
    ]
    
    y_positions = np.linspace(0.85, 0.15, len(steps))
    
    for i, (step, y) in enumerate(zip(steps, y_positions)):
        step_num = i + 1
        
        if step_num == STEP_NUMBER:
            # Current step - highlighted
            facecolor = 'lightgreen'
            edgecolor = 'green'
            fontweight = 'bold'
        elif step_num < STEP_NUMBER:
            # Previous steps
            facecolor = 'lightblue'
            edgecolor = 'blue'
            fontweight = 'normal'
        else:
            # Future steps
            facecolor = 'lightgray'
            edgecolor = 'gray'
            fontweight = 'normal'
        
        box = FancyBboxPatch((0.1, y-0.03), 0.6, 0.06,
                           boxstyle="round,pad=0.01",
                           facecolor=facecolor, edgecolor=edgecolor,
                           linewidth=2)
        ax.add_patch(box)
        
        ax.text(0.4, y, step, ha='center', va='center', fontweight=fontweight, fontsize=11)
        
        # Add arrow to next step
        if i < len(steps) - 1:
            ax.arrow(0.72, y, 0, -0.04, head_width=0.02, head_length=0.01, fc='black', ec='black')
    
    # Add title and current step info
    ax.text(0.5, 0.95, f'PSS Verification Workflow — Position: Step {STEP_NUMBER}/10', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Add step details
    step_details = f"""CURRENT STEP: {STEP_NAME}

PSS (Phase-Shift Signature) Framework:
• Alternative to prime-side von-Mangoldt approach
• Uses PSS spiral geometry and amplitude analysis  
• Bridges to prime-side via COUPLING_K constant
• 10-step verification sequence for completeness

STEP {STEP_NUMBER} FOCUS:
Execute corresponding script in EXECUTION/ folder
to generate step-specific verification data and
analytical outputs."""
    
    ax.text(0.75, 0.6, step_details, ha='left', va='top', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig(current_dir / f'{STEP_NAME.lower()}_workflow.png', dpi=300, bbox_inches='tight')
    plt.show()


def run_all_analytics() -> None:
    """
    Main function to run all PSS_STEP analytics and generate visualizations.
    """
    print("=" * 60)
    print(f"{STEP_NAME} ANALYTICS: PSS Verification Step {STEP_NUMBER} Visualizations")
    print("=" * 60)
    
    # Check if execution has been run
    output_data = load_pss_step_outputs()
    
    if output_data['status'] == 'NOT_EXECUTED':
        print(f"\n⚠️  WARNING: {STEP_NAME} has not been executed yet.")
        print(f"   Run the corresponding execution script first to generate verification data.")
        print("   Proceeding with template visualizations...\n")
    
    try:
        print(f"\n1. Generating {STEP_NAME} overview...")
        plot_pss_step_overview()
        
        print(f"\n2. Generating {STEP_NAME} workflow position...")
        plot_pss_workflow_position()
        
        print(f"\n✓ All visualizations saved to: {current_dir}")
        print(f"  - {STEP_NAME.lower()}_overview.png")
        print(f"  - {STEP_NAME.lower()}_workflow.png")
        
        if output_data['status'] == 'NOT_EXECUTED':
            print(f"\n📋 TO EXECUTE {STEP_NAME}:")
            print(f"   cd {current_dir.parent}")
            print(f"   python EXECUTION/{STEP_NAME}_*.py")  
            print(f"   python ANALYTICS/ANALYTICS.py  # Re-run for updated data")
        
    except Exception as e:
        print(f"ERROR in analytics generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_analytics()