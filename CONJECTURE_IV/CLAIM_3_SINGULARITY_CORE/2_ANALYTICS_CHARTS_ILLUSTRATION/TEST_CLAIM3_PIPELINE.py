"""
TEST_CLAIM3_PIPELINE.py
=======================

Quick test of Claim 3 analytics pipeline with small dataset.

Verifies the vectorized ψ(T) computation, 9D curvature extraction,
and geodesic criterion before running full analysis.

Usage: python TEST_CLAIM3_PIPELINE.py
"""

import numpy as np
import logging
import os
import sys
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Get script directory for proper path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def check_main_csvs_exist():
    """Check if main CSV data files exist."""
    csv_dir = os.path.join(SCRIPT_DIR, "csv_data")
    expected_files = [
        'psi_profiles.csv', 'magnitude_at_zeros.csv', 'curvature_9d.csv',
        'geodesic_criterion.csv', 'phase_velocity.csv', 'persistence_ratios.csv',
        'z80_discriminant.csv'
    ]
    
    missing = []
    for filename in expected_files:
        filepath = os.path.join(csv_dir, filename)
        if not os.path.exists(filepath):
            missing.append(filename)
    
    return missing

def generate_main_csvs():
    """Generate main CSV files using BUILD_CLAIM3_DATA."""
    logger.info("Main CSV files missing - generating them now...")
    
    # Import and run the main data builder
    from BUILD_CLAIM3_DATA import main as build_main
    build_main()

def test_pipeline():
    """Test the complete Claim 3 pipeline with small dataset."""
    
    logger.info("Testing Claim 3 analytics pipeline (VECTORIZED)...")
    
    # Import build script functions (vectorized API)
    try:
        from BUILD_CLAIM3_DATA import (
            compute_psi_vectorized, compute_9d_curvature_vectorized,
            compute_phase_velocity_vectorized, compute_z80_discriminant_vectorized,
            compute_persistence_ratios_vectorized, apply_geodesic_criterion_vectorized,
            RIEMANN_ZEROS, NON_ZEROS, NUM_BRANCHES
        )
    except ImportError as e:
        logger.error(f"Could not import BUILD_CLAIM3_DATA: {e}")
        return False
    
    # Test with small dataset
    logger.info("Testing with first 10 zeros and 10 non-zeros...")
    
    test_zeros = RIEMANN_ZEROS[:10]
    test_non_zeros = NON_ZEROS[:10]
    all_T = np.concatenate([test_zeros, test_non_zeros])
    
    logger.info(f"Test T values: {len(all_T)}")
    
    try:
        # Test 1: ψ(T) computation
        logger.info("  Testing ψ(T) computation...")
        start = time.time()
        psi_values = compute_psi_vectorized(all_T)
        psi_time = time.time() - start
        
        assert len(psi_values) == len(all_T), "ψ computation failed"
        assert np.all(np.isfinite(psi_values)), "ψ contains non-finite values"
        logger.info(f"    ✓ ψ(T) computed in {psi_time:.3f}s")
        logger.info(f"    |ψ| range: [{np.min(np.abs(psi_values)):.4f}, {np.max(np.abs(psi_values)):.4f}]")
        
        # Test 2: 9D curvature
        logger.info("  Testing 9D curvature extraction...")
        start = time.time()
        curvature = compute_9d_curvature_vectorized(all_T)
        curv_time = time.time() - start
        
        assert curvature.shape == (len(all_T), NUM_BRANCHES), "Curvature shape mismatch"
        assert np.all(np.isfinite(curvature)), "Curvature contains non-finite values"
        logger.info(f"    ✓ 9D curvature computed in {curv_time:.3f}s")
        logger.info(f"    Shape: {curvature.shape}")
        
        # Test 3: Phase velocity
        logger.info("  Testing phase velocity...")
        start = time.time()
        phase_vel = compute_phase_velocity_vectorized(all_T)
        pv_time = time.time() - start
        
        assert len(phase_vel) == len(all_T), "Phase velocity length mismatch"
        assert np.all(np.isfinite(phase_vel)), "Phase velocity contains non-finite values"
        logger.info(f"    ✓ Phase velocity computed in {pv_time:.3f}s")
        
        # Test 4: |z80| discriminant
        logger.info("  Testing |z80| discriminant...")
        start = time.time()
        z80 = compute_z80_discriminant_vectorized(all_T)
        z80_time = time.time() - start
        
        assert len(z80) == len(all_T), "|z80| length mismatch"
        logger.info(f"    ✓ |z80| computed in {z80_time:.3f}s")
        
        # Test 5: Persistence ratios
        logger.info("  Testing persistence ratios...")
        start = time.time()
        persistence = compute_persistence_ratios_vectorized(all_T)
        pr_time = time.time() - start
        
        assert persistence.shape == (len(all_T), 2), "Persistence shape mismatch"
        logger.info(f"    ✓ Persistence ratios computed in {pr_time:.3f}s")
        
        # Test 6: Geodesic criterion
        logger.info("  Testing geodesic criterion...")
        start = time.time()
        is_zero_pred, scores = apply_geodesic_criterion_vectorized(
            phase_vel, z80, persistence[:, 1], curvature
        )
        gc_time = time.time() - start
        
        assert len(is_zero_pred) == len(all_T), "Criterion prediction length mismatch"
        assert len(scores) == len(all_T), "Criterion score length mismatch"
        logger.info(f"    ✓ Geodesic criterion applied in {gc_time:.3f}s")
        
        # Summary
        total_time = psi_time + curv_time + pv_time + z80_time + pr_time + gc_time
        logger.info("")
        logger.info(f"All tests passed! Total time: {total_time:.3f}s")
        
        # Basic validation
        logger.info("")
        logger.info("=== QUICK VALIDATION ===")
        
        # Check that zeros have lower |ψ(T)| on average
        zeros_mag = np.abs(psi_values[:10])
        non_zeros_mag = np.abs(psi_values[10:])
        logger.info(f"Mean |ψ(T)| at zeros: {np.mean(zeros_mag):.4f}")
        logger.info(f"Mean |ψ(T)| off zeros: {np.mean(non_zeros_mag):.4f}")
        
        # Geodesic criterion stats
        zeros_scores = scores[:10]
        non_zeros_scores = scores[10:]
        logger.info(f"Mean criterion score at zeros: {np.mean(zeros_scores):.4f}")
        logger.info(f"Mean criterion score off zeros: {np.mean(non_zeros_scores):.4f}")
        
        # Predictions
        true_pos = np.sum(is_zero_pred[:10])
        false_pos = np.sum(is_zero_pred[10:])
        logger.info(f"True positives (zeros predicted as zeros): {true_pos}/10")
        logger.info(f"False positives (non-zeros predicted as zeros): {false_pos}/10")
        
        logger.info("")
        logger.info("=" * 50)
        logger.info("PIPELINE TEST SUCCESSFUL!")
        logger.info("=" * 50)
        
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
            response = input("Generate full CSV data? (100 zeros, ~30 seconds) [y/N]: ")
            
            if response.lower() in ['y', 'yes']:
                generate_main_csvs()
                logger.info("")
                logger.info("Main CSV files generated successfully!")
                logger.info("You can now run: python PLOT_CLAIM3_FIGURES.py")
            else:
                logger.info("Skipping full data generation.")
                logger.info("To generate full data, run: python BUILD_CLAIM3_DATA.py")
        else:
            logger.error("Pipeline test failed - please fix issues before generating full data")
            return False
    else:
        logger.info("Main CSV files already exist. Running pipeline test...")
        test_success = test_pipeline()
        
        if test_success:
            logger.info("")
            logger.info("All systems ready!")
            logger.info("Run: python PLOT_CLAIM3_FIGURES.py to generate figures")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
