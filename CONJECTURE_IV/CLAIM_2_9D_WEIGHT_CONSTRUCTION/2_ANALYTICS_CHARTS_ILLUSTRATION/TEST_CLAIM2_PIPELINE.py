"""
TEST_CLAIM2_PIPELINE.py
======================

Quick test of Claim 2 analytics pipeline with subset of data.

This script runs the full analysis pipeline on a small number of zeros
to verify everything is working before running the full 99,999 zero analysis.

If main CSV files are missing, it will generate them automatically.

Usage: python TEST_CLAIM2_PIPELINE.py
"""

import numpy as np
import logging
import os
import csv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Get script directory for proper path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def check_main_csvs_exist():
    """Check if main CSV data files exist."""
    csv_dir = os.path.join(SCRIPT_DIR, "csv_data")
    expected_files = [
        'phi_weight_fit.csv', 'branch_balance.csv', 'total_balance.csv',
        'weight_profile_windows.csv', 'weight_sensitivity.csv', 'torus_distribution.csv'
    ]
    
    missing = []
    for filename in expected_files:
        filepath = os.path.join(csv_dir, filename)
        if not os.path.exists(filepath):
            missing.append(filename)
    
    return missing

def generate_main_csvs():
    """Generate main CSV files using BUILD_CLAIM2_DATA."""
    logger.info("Main CSV files missing - generating them now...")
    logger.info("This may take 10-30 minutes for 99,999 zeros...")
    
    # Import and run the main data builder
    from BUILD_CLAIM2_DATA import main as build_main
    build_main()

def export_test_results(results, test_dir):
    """Export test results to CSV files in the specified directory."""
    os.makedirs(test_dir, exist_ok=True)
    
    # 1. phi_weight_fit.csv
    with open(os.path.join(test_dir, "phi_weight_fit.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['k', 'w_theoretical', 'w_hat', 'w_hat_lower', 'w_hat_upper'])
        writer.writeheader()
        writer.writerows(results['phi_weight_fit'])
    
    # 2. branch_balance.csv
    with open(os.path.join(test_dir, "branch_balance.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['k', 'mean_Re_Sk', 'std_Re_Sk', 'mean_Im_Sk', 'std_Im_Sk'])
        writer.writeheader()
        writer.writerows(results['branch_balance'])
    
    # 3. total_balance.csv
    with open(os.path.join(test_dir, "total_balance.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['mean_Re_S', 'std_Re_S', 'mean_Im_S', 'std_Im_S'])
        writer.writeheader()
        writer.writerow(results['total_balance'])
    
    # 4. weight_profile_windows.csv
    with open(os.path.join(test_dir, "weight_profile_windows.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['window_id', 'k', 'alpha_k'])
        writer.writeheader()
        writer.writerows(results['weight_profile_windows'])
    
    # 5. weight_sensitivity.csv
    with open(os.path.join(test_dir, "weight_sensitivity.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['perturbation_id', 'eps_norm', 'J_value'])
        writer.writeheader()
        writer.writerows(results['weight_sensitivity'])
    
    # 6. torus_distribution.csv
    with open(os.path.join(test_dir, "torus_distribution.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['k', 'ks_statistic', 'mean_Vk', 'var_Vk', 'p_value'])
        writer.writeheader()
        writer.writerows(results['torus_distribution'])
    
    logger.info(f"Test results exported to {test_dir}/")

def test_pipeline():
    """Test the complete Claim 2 pipeline with small dataset."""
    
    logger.info("Testing Claim 2 analytics pipeline (VECTORIZED)...")
    
    # Import build script functions (vectorized API)
    try:
        from BUILD_CLAIM2_DATA import (
            load_riemann_zeros, compute_branch_matrix,
            analyze_phi_weight_fit, analyze_branch_balance,
            analyze_weight_profile_invariance, analyze_weight_sensitivity,
            analyze_torus_distribution, WINDOW_SIZE, NUM_PERTURBATIONS
        )
        import BUILD_CLAIM2_DATA
    except ImportError as e:
        logger.error(f"Could not import BUILD_CLAIM2_DATA: {e}")
        return False
    
    # Test with small dataset
    logger.info("Loading test dataset (100 zeros)...")
    zeros = load_riemann_zeros(max_zeros=100)
    
    if len(zeros) < 50:
        logger.error(f"Insufficient zeros loaded: {len(zeros)}")
        return False
    
    logger.info(f"Using {len(zeros)} zeros for testing")
    
    # Precompute branch matrix (vectorized - this is the key optimization)
    logger.info("Precomputing branch matrix...")
    branch_matrix = compute_branch_matrix(zeros)
    logger.info(f"  Branch matrix shape: {branch_matrix.shape}")
    
    # Test each analysis function (now using vectorized API)
    logger.info("Testing analysis functions...")
    
    try:
        # Test 1: φ-weight fit (reduced bootstrap iterations for speed)
        logger.info("  Testing φ-weight fit...")
        phi_weight_fit = analyze_phi_weight_fit(branch_matrix[:50], num_bootstrap=5)
        assert len(phi_weight_fit) == 9, "Weight fit should return 9 branches"
        
        # Test 2: Branch balance
        logger.info("  Testing branch balance...")
        branch_balance, total_balance = analyze_branch_balance(branch_matrix[:50])
        assert len(branch_balance) == 9, "Branch balance should return 9 branches"
        assert 'mean_Re_S' in total_balance, "Total balance missing required field"
        
        # Test 3: Weight profile (small window size)
        logger.info("  Testing weight profile invariance...")
        # Temporarily modify window size for testing
        original_window = BUILD_CLAIM2_DATA.WINDOW_SIZE
        BUILD_CLAIM2_DATA.WINDOW_SIZE = 25  # Use 25 zeros per window
        
        weight_profile = analyze_weight_profile_invariance(branch_matrix)
        assert len(weight_profile) > 0, "Weight profile should return data"
        
        # Restore original window size
        BUILD_CLAIM2_DATA.WINDOW_SIZE = original_window
        
        # Test 4: Sensitivity (fewer perturbations for speed)
        logger.info("  Testing weight sensitivity...")
        original_perturbations = BUILD_CLAIM2_DATA.NUM_PERTURBATIONS
        BUILD_CLAIM2_DATA.NUM_PERTURBATIONS = 5  # Reduce for testing
        
        weight_sensitivity = analyze_weight_sensitivity(branch_matrix[:30])
        assert len(weight_sensitivity) == 6, "Should have baseline + 5 perturbations"
        
        # Restore original perturbations
        BUILD_CLAIM2_DATA.NUM_PERTURBATIONS = original_perturbations
        
        # Test 5: Torus distribution
        logger.info("  Testing torus distribution...")
        torus_distribution = analyze_torus_distribution(branch_matrix[:50])
        assert len(torus_distribution) == 9, "Torus analysis should return 9 branches"
        
        logger.info("All analysis functions passed!")
        
        # Test CSV export with local function
        logger.info("Testing CSV export...")
        test_dir = os.path.join(SCRIPT_DIR, "test_csv_data")
        
        results = {
            'phi_weight_fit': phi_weight_fit,
            'branch_balance': branch_balance,
            'total_balance': total_balance,
            'weight_profile_windows': weight_profile,
            'weight_sensitivity': weight_sensitivity,
            'torus_distribution': torus_distribution
        }
        
        export_test_results(results, test_dir)
        
        # Verify files were created
        expected_files = [
            'phi_weight_fit.csv', 'branch_balance.csv', 'total_balance.csv',
            'weight_profile_windows.csv', 'weight_sensitivity.csv', 'torus_distribution.csv'
        ]
        
        all_present = True
        for filename in expected_files:
            filepath = os.path.join(test_dir, filename)
            if os.path.exists(filepath):
                logger.info(f"  ✓ {filename} created successfully")
            else:
                logger.error(f"  ✗ {filename} missing")
                all_present = False
        
        if not all_present:
            return False
        
        logger.info("CSV export successful!")
        
        # Test plotting (import check only)
        try:
            import PLOT_CLAIM2_FIGURES
            logger.info("✓ Plotting script imports successfully")
        except ImportError as e:
            logger.warning(f"Plotting script import issue: {e}")
        
        logger.info("="*50)
        logger.info("PIPELINE TEST SUCCESSFUL!")
        logger.info("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point - run tests and generate missing CSVs if needed."""
    
    # First check if main CSVs exist
    missing = check_main_csvs_exist()
    
    if missing:
        logger.info(f"Missing CSV files: {missing}")
        logger.info("Running pipeline test first...")
        
        # Run test to verify pipeline works
        test_success = test_pipeline()
        
        if test_success:
            logger.info("")
            logger.info("Pipeline test passed!")
            logger.info("")
            
            # Ask user if they want to generate full CSVs
            response = input("Generate full CSV data from 99,999 zeros? This takes 10-30 minutes. [y/N]: ")
            
            if response.lower() in ['y', 'yes']:
                generate_main_csvs()
                logger.info("")
                logger.info("Main CSV files generated successfully!")
                logger.info("You can now run: python PLOT_CLAIM2_FIGURES.py")
            else:
                logger.info("Skipping full data generation.")
                logger.info("To generate full data, run: python BUILD_CLAIM2_DATA.py")
        else:
            logger.error("Pipeline test failed - please fix issues before generating full data")
            return False
    else:
        logger.info("Main CSV files already exist. Running pipeline test...")
        test_success = test_pipeline()
        
        if test_success:
            logger.info("")
            logger.info("All systems ready!")
            logger.info("Run: python PLOT_CLAIM2_FIGURES.py to generate figures")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)