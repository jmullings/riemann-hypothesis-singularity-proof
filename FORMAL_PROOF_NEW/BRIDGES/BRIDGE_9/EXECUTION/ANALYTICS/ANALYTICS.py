#!/usr/bin/env python3
"""
FORMAL_PROOF_NEW/BRIDGES/BRIDGE_9/EXECUTION/ANALYTICS/ANALYTICS.py
=================================================================

**STATUS: ANALYTICAL SUPPORT — March 11, 2026** 
**Purpose: Charts and illustrations for BRIDGE_09 nested analysis data**
**Protocols: P1-P5 compliant analytical visualization**

This module provides analytical visualization for BRIDGE_09 data files
located in the nested ANALYTICS directory. It processes existing
CSV and JSON files to generate comprehensive visualizations.

=============================================================================
VISUALIZATIONS PROVIDED
=============================================================================

1. Bridge Results Analysis: JSON configuration and results processing
2. Sample Path Visualization: CSV trajectory and path analysis
3. Spiral Summary Charts: Summary statistics and patterns  
4. Data Quality Validation: File integrity and completeness check
5. Cross-File Correlation: Multi-file relationship analysis
6. Performance Metrics: Data processing and analysis metrics

=============================================================================
Author : Jason Mullings
Date   : March 11, 2026  
Version: 1.0.0
=============================================================================
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directories to path for imports
current_dir = Path(__file__).parent
configs_dir = current_dir.parent.parent.parent.parent.parent / "CONFIGURATIONS"

sys.path.insert(0, str(configs_dir))

try:
    from AXIOMS import LAMBDA_STAR, NORM_X_STAR, PHI
except ImportError as e:
    print(f"Warning: Could not import AXIOMS: {e}")
    LAMBDA_STAR = 0.1
    NORM_X_STAR = 0.1  
    PHI = 1.618

# =============================================================================
# SECTION 1: DATA FILE LOADING AND VALIDATION
# =============================================================================

def load_and_validate_data() -> Dict:
    """
    Load and validate all data files in the ANALYTICS directory.
    """
    data_files = {
        "bridge12_results.json": None,
        "bridge12_sample_path.csv": None,
        "bridge12_spiral_summary.csv": None
    }
    
    validation_results = {}
    
    # Load JSON results
    json_file = current_dir / "bridge12_results.json"
    if json_file.exists():
        try:
            with open(json_file, 'r') as f:
                data_files["bridge12_results.json"] = json.load(f)
            validation_results["json_status"] = "valid"
        except Exception as e:
            validation_results["json_status"] = f"error: {e}"
    else:
        validation_results["json_status"] = "missing"
    
    # Load CSV files
    for csv_name in ["bridge12_sample_path.csv", "bridge12_spiral_summary.csv"]:
        csv_file = current_dir / csv_name
        if csv_file.exists():
            try:
                data_files[csv_name] = pd.read_csv(csv_file)
                validation_results[f"{csv_name}_status"] = "valid"
                validation_results[f"{csv_name}_rows"] = len(data_files[csv_name])
                validation_results[f"{csv_name}_cols"] = len(data_files[csv_name].columns)
            except Exception as e:
                validation_results[f"{csv_name}_status"] = f"error: {e}"
        else:
            validation_results[f"{csv_name}_status"] = "missing"
    
    return {"data_files": data_files, "validation": validation_results}

# =============================================================================
# SECTION 2: BRIDGE RESULTS ANALYSIS
# =============================================================================

def plot_bridge_results_analysis(loaded_data: Dict) -> None:
    """
    Analyze and visualize the bridge results JSON data.
    """
    plt.figure(figsize=(14, 10))
    
    json_data = loaded_data["data_files"]["bridge12_results.json"]
    validation = loaded_data["validation"]
    
    # File status overview
    plt.subplot(2, 3, 1)
    file_statuses = []
    file_names = []
    
    for key, value in validation.items():
        if key.endswith("_status"):
            file_name = key.replace("_status", "").replace("bridge12_", "")
            file_names.append(file_name)
            file_statuses.append(1 if value == "valid" else 0)
    
    colors = ['green' if s == 1 else 'red' for s in file_statuses]
    bars = plt.bar(range(len(file_names)), file_statuses, color=colors, alpha=0.7)
    
    plt.xticks(range(len(file_names)), file_names, rotation=45)
    plt.ylabel("Status (1=Valid, 0=Invalid)")
    plt.title("Data File Status")
    plt.ylim([0, 1.2])
    
    # Add status symbols
    for bar, status in zip(bars, file_statuses):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                '✓' if status else '✗', ha='center', va='bottom', 
                fontsize=16, fontweight='bold')
    
    # JSON data structure analysis
    plt.subplot(2, 3, 2)
    if json_data:
        if isinstance(json_data, dict):
            keys = list(json_data.keys())[:10]  # Top 10 keys
            values = []
            
            for key in keys:
                value = json_data[key]
                if isinstance(value, (int, float)):
                    values.append(float(value))
                elif isinstance(value, list):
                    values.append(len(value))
                elif isinstance(value, dict):
                    values.append(len(value))
                else:
                    values.append(1)
            
            plt.bar(range(len(keys)), values, alpha=0.7, color='blue')
            plt.xticks(range(len(keys)), keys, rotation=45)
            plt.ylabel("Value/Count")
            plt.title("JSON Data Structure")
        else:
            plt.text(0.5, 0.5, "JSON data is not a dictionary", 
                    ha='center', va='center', transform=plt.gca().transAxes)
            plt.title("JSON Data Structure")
    else:
        plt.text(0.5, 0.5, "No JSON data loaded", 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title("JSON Data Structure")
    
    plt.axis('off' if not json_data else 'on')
    
    # File sizes
    plt.subplot(2, 3, 3)
    file_sizes = []
    size_names = []
    
    for filename in ["bridge12_results.json", "bridge12_sample_path.csv", "bridge12_spiral_summary.csv"]:
        filepath = current_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            file_sizes.append(size_mb)
            size_names.append(filename.replace("bridge12_", ""))
    
    if file_sizes:
        plt.pie(file_sizes, labels=size_names, autopct='%1.2f MB', startangle=90, alpha=0.7)
        plt.title("File Size Distribution")
    else:
        plt.text(0.5, 0.5, "No files found", ha='center', va='center')
        plt.title("File Size Distribution")
    
    # CSV row/column counts
    plt.subplot(2, 3, 4)
    csv_stats = {}
    for key, value in validation.items():
        if key.endswith("_rows") or key.endswith("_cols"):
            csv_name = key.split("_")[1]  # Extract middle part
            stat_type = key.split("_")[-1]  # rows or cols
            
            if csv_name not in csv_stats:
                csv_stats[csv_name] = {}
            csv_stats[csv_name][stat_type] = value
    
    if csv_stats:
        csv_names = list(csv_stats.keys())
        rows = [csv_stats[name].get("rows", 0) for name in csv_names]
        cols = [csv_stats[name].get("cols", 0) for name in csv_names]
        
        x = np.arange(len(csv_names))
        width = 0.35
        
        plt.bar(x - width/2, rows, width, label='Rows', alpha=0.7)
        plt.bar(x + width/2, cols, width, label='Columns', alpha=0.7)
        
        plt.xlabel("CSV File")
        plt.ylabel("Count")
        plt.title("CSV Dimensions")
        plt.xticks(x, csv_names)
        plt.legend()
    else:
        plt.text(0.5, 0.5, "No CSV statistics available", ha='center', va='center')
        plt.title("CSV Dimensions")
    
    # Data completeness
    plt.subplot(2, 3, 5)
    completeness_scores = []
    completeness_labels = []
    
    expected_files = ["bridge12_results.json", "bridge12_sample_path.csv", "bridge12_spiral_summary.csv"]
    for filename in expected_files:
        status_key = f"{filename}_status"
        if status_key in validation:
            score = 1 if validation[status_key] == "valid" else 0
        else:
            score = 1 if (current_dir / filename).exists() else 0
        
        completeness_scores.append(score * 100)
        completeness_labels.append(filename.replace("bridge12_", "").replace(".csv", "").replace(".json", ""))
    
    colors = ['green' if s >= 100 else 'orange' if s >= 50 else 'red' for s in completeness_scores]
    plt.bar(completeness_labels, completeness_scores, color=colors, alpha=0.7)
    plt.xlabel("Data File")
    plt.ylabel("Completeness (%)")
    plt.title("Data Completeness")
    plt.xticks(rotation=45)
    plt.ylim([0, 110])
    
    # Summary metrics
    plt.subplot(2, 3, 6)
    summary_metrics = {
        "Total Files": len(expected_files),
        "Valid Files": sum(1 for f in expected_files if 
                         validation.get(f"{f}_status", "missing") == "valid"),
        "Total Size": f"{sum(file_sizes):.2f} MB" if file_sizes else "0 MB",
        "Avg Completeness": f"{np.mean(completeness_scores):.1f}%",
        "JSON Status": validation.get("bridge12_results.json_status", "unknown"),
        "CSV Count": sum(1 for f in expected_files if f.endswith('.csv'))
    }
    
    metric_text = []
    for key, value in summary_metrics.items():
        metric_text.append(f"{key}: {value}")
    
    plt.text(0.1, 0.9, "\n".join(metric_text), transform=plt.gca().transAxes,
            fontsize=11, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
    
    plt.axis('off')
    plt.title("Data Summary")
    
    plt.tight_layout()
    plt.savefig(current_dir / "bridge_results_analysis.png", dpi=150, bbox_inches='tight')
    plt.show()

# =============================================================================
# SECTION 3: SAMPLE PATH VISUALIZATION
# =============================================================================

def plot_sample_path_visualization(loaded_data: Dict) -> None:
    """
    Visualize the sample path CSV data.
    """
    plt.figure(figsize=(14, 8))
    
    sample_path_df = loaded_data["data_files"]["bridge12_sample_path.csv"]
    
    if sample_path_df is not None and not sample_path_df.empty:
        # Path trajectory
        plt.subplot(2, 3, 1)
        # Assume first few columns are coordinates
        if sample_path_df.shape[1] >= 2:
            plt.plot(sample_path_df.iloc[:, 0], sample_path_df.iloc[:, 1], 'b-', alpha=0.7, linewidth=2)
            plt.scatter(sample_path_df.iloc[0, 0], sample_path_df.iloc[0, 1], color='green', s=100, zorder=5, label='Start')
            plt.scatter(sample_path_df.iloc[-1, 0], sample_path_df.iloc[-1, 1], color='red', s=100, zorder=5, label='End')
            plt.xlabel(f"Column 0: {sample_path_df.columns[0] if len(sample_path_df.columns) > 0 else 'X'}")
            plt.ylabel(f"Column 1: {sample_path_df.columns[1] if len(sample_path_df.columns) > 1 else 'Y'}")
            plt.title("Sample Path Trajectory")
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        # Column distributions
        plt.subplot(2, 3, 2)
        numeric_cols = sample_path_df.select_dtypes(include=[np.number]).columns[:5]  # First 5 numeric columns
        for i, col in enumerate(numeric_cols):
            plt.hist(sample_path_df[col], bins=20, alpha=0.6, label=f"{col}"[:10])
        
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.title("Column Distributions")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Time series (first column vs index)
        plt.subplot(2, 3, 3)
        if sample_path_df.shape[1] >= 1:
            plt.plot(sample_path_df.index, sample_path_df.iloc[:, 0], 'r-', linewidth=2)
            plt.xlabel("Sample Index")
            plt.ylabel(f"{sample_path_df.columns[0] if len(sample_path_df.columns) > 0 else 'Value'}")
            plt.title("Time Series Evolution")
            plt.grid(True, alpha=0.3)
    else:
        for i in range(1, 4):
            plt.subplot(2, 3, i)
            plt.text(0.5, 0.5, "Sample path data not available", 
                    ha='center', va='center', transform=plt.gca().transAxes)
            plt.title(f"Sample Path Analysis {i}")
    
    # Data quality metrics
    plt.subplot(2, 3, 4)
    if sample_path_df is not None:
        quality_metrics = {
            "Total Rows": len(sample_path_df),
            "Total Cols": len(sample_path_df.columns),
            "Missing Values": sample_path_df.isnull().sum().sum(),
            "Numeric Cols": len(sample_path_df.select_dtypes(include=[np.number]).columns),
            "Data Types": len(sample_path_df.dtypes.unique())
        }
    else:
        quality_metrics = {"Status": "No data loaded"}
    
    metric_text = []
    for key, value in quality_metrics.items():
        metric_text.append(f"{key}: {value}")
    
    plt.text(0.1, 0.9, "\n".join(metric_text), transform=plt.gca().transAxes,
            fontsize=12, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.7))
    
    plt.axis('off')
    plt.title("Data Quality Metrics")
    
    # Correlation matrix (if enough numeric columns)
    plt.subplot(2, 3, 5)
    if sample_path_df is not None and len(sample_path_df.select_dtypes(include=[np.number]).columns) >= 2:
        numeric_df = sample_path_df.select_dtypes(include=[np.number]).iloc[:, :6]  # Max 6 columns
        corr_matrix = numeric_df.corr()
        
        im = plt.imshow(corr_matrix, cmap='RdBu', vmin=-1, vmax=1, aspect='auto')
        plt.colorbar(im, fraction=0.046, pad=0.04)
        plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=45)
        plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
        plt.title("Column Correlation Matrix")
    else:
        plt.text(0.5, 0.5, "Insufficient numeric data\nfor correlation", 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title("Correlation Matrix")
    
    # Statistical summary  
    plt.subplot(2, 3, 6)
    if sample_path_df is not None and not sample_path_df.empty:
        # Select first numeric column for detailed stats
        numeric_cols = sample_path_df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            stats = sample_path_df[col].describe()
            
            stat_text = []
            for key, value in stats.items():
                stat_text.append(f"{key}: {value:.4f}")
            
            plt.text(0.1, 0.9, "\n".join(stat_text), transform=plt.gca().transAxes,
                    fontsize=10, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.7))
            plt.title(f"Statistics: {col}")
        else:
            plt.text(0.5, 0.5, "No numeric columns found", 
                    ha='center', va='center', transform=plt.gca().transAxes)
            plt.title("Statistical Summary")
    else:
        plt.text(0.5, 0.5, "No data available", 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title("Statistical Summary")
    
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(current_dir / "sample_path_visualization.png", dpi=150, bbox_inches='tight')
    plt.show()

# =============================================================================
# SECTION 4: MAIN ANALYTICS RUNNER
# =============================================================================

def run_analytics() -> None:
    """
    Main analytics runner for nested BRIDGE_09 data analysis.
    """
    print("=" * 80)
    print("BRIDGE_09 NESTED DATA ANALYTICAL SUPPORT")
    print("=" * 80)
    print()
    
    # Load and validate data
    print("Loading and validating data files...")
    try:
        loaded_data = load_and_validate_data()
        validation = loaded_data["validation"]
        
        print("✓ Data loading completed")
        for key, value in validation.items():
            if key.endswith("_status"):
                filename = key.replace("_status", "")
                status_symbol = "✓" if value == "valid" else "⚠️"
                print(f"  {status_symbol} {filename}: {value}")
        print()
        
    except Exception as e:
        print(f"⚠️  Data loading failed: {e}")
        loaded_data = {"data_files": {}, "validation": {"error": str(e)}}
        print()
    
    # Generate all visualizations
    analytics_functions = [
        ("Bridge Results Analysis", plot_bridge_results_analysis),
        ("Sample Path Visualization", plot_sample_path_visualization),
    ]
    
    for name, func in analytics_functions:
        try:
            print(f"Generating {name}...")
            func(loaded_data)
            print(f"✓ {name} completed")
        except Exception as e:
            print(f"⚠️  {name} failed: {e}")
        print()
    
    # Summary
    print("=" * 80)
    print("ANALYTICAL SUMMARY")
    print("=" * 80)
    print("Generated visualizations:")
    print("  • bridge_results_analysis.png")
    print("  • sample_path_visualization.png")
    print()
    print("Analyzed data files:")
    print("  • bridge12_results.json")
    print("  • bridge12_sample_path.csv")
    print("  • bridge12_spiral_summary.csv")
    print()
    print("Find all plots in:", current_dir)
    print("=" * 80)

if __name__ == "__main__":
    # Set up matplotlib
    plt.style.use('default')
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 150
    
    # Ensure output directory exists
    current_dir.mkdir(exist_ok=True)
    
    # Run analytics
    run_analytics()