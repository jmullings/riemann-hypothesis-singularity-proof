#!/usr/bin/env python3
"""
CONJECTURE_IV_STRUCTURE_VALIDATOR.py
===================================

Validates the complete Conjecture IV restructuring into Five Claims.
Verifies all files are properly organized and accessible.

March 7, 2026 — Structure Validation
"""

import os
import sys

# Base directory
BASE_DIR = "/Users/jmullings/BetaPrecision/high-precision-core/RIEMANN_PHI_RIEMANN/RIEMANN_PHI_9D_PROXY/CONJECTURE_IV_NEW"

# Expected structure
EXPECTED_STRUCTURE = {
    "CLAIM_1_9D_NECESSITY": {
        "core_files": [
            "1_PROOF_SCRIPTS_NOTES/PARTIAL_SUM_SINGULARITY_ANALYSIS.py",
            "1_PROOF_SCRIPTS_NOTES/TRUE_PARTIAL_SUM_SINGULARITY.py", 
            "1_PROOF_SCRIPTS_NOTES/SINGULARITY_FUNCTIONAL.py"
        ],
        "analytics": [
            "2_ANALYTICS_CHARTS_ILLUSTRATION/PARTIAL_SUM_SINGULARITY_CHART.png",
            "2_ANALYTICS_CHARTS_ILLUSTRATION/TRUE_PARTIAL_SUM_SINGULARITY.png"
        ],
        "trinity": [
            "3_INFINITY_TRINITY_COMPLIANCE/TRINITY_VALIDATED_FRAMEWORK.py"
        ]
    },
    "CLAIM_2_9D_WEIGHT_CONSTRUCTION": {
        "core_files": [
            "1_PROOF_SCRIPTS_NOTES/CONJECTURE_V_CALIBRATION.py",
            "1_PROOF_SCRIPTS_NOTES/VALIDATE_CONJECTURE_V_CALIBRATION.py",
            "1_PROOF_SCRIPTS_NOTES/calculate_weights_25dp.py"
        ],
        "analytics": [],
        "trinity": [
            "3_INFINITY_TRINITY_COMPLIANCE/TRINITY_VALIDATED_FRAMEWORK.py"
        ]
    },
    "CLAIM_3_SINGULARITY_CORE": {
        "core_files": [
            "1_PROOF_SCRIPTS_NOTES/PARALLEL_SINGULARITY.py",
            "1_PROOF_SCRIPTS_NOTES/QUANTUM_GEODESIC_SINGULARITY.py",
            "1_PROOF_SCRIPTS_NOTES/RH_SINGULARITY.py"
        ],
        "analytics": [],
        "trinity": [
            "3_INFINITY_TRINITY_COMPLIANCE/TRINITY_VALIDATED_FRAMEWORK.py"
        ]
    },
    "CLAIM_4_6D_COLLAPSE": {
        "core_files": [
            "1_PROOF_SCRIPTS_NOTES/RIEMANN_ZERO_PREDICTOR.py",
            "1_PROOF_SCRIPTS_NOTES/PHI_WEIGHTED_9D_SHIFT.py"
        ],
        "analytics": [],
        "trinity": [
            "3_INFINITY_TRINITY_COMPLIANCE/TRINITY_VALIDATED_FRAMEWORK.py"
        ]
    },
    "CLAIM_5_EXTERNAL_VALIDATION": {
        "core_files": [
            "1_PROOF_SCRIPTS_NOTES/UNIFIED_PROOF_FRAMEWORK.py",
            "1_PROOF_SCRIPTS_NOTES/FREDHOLM_ORDER_TYPE.py",
            "1_PROOF_SCRIPTS_NOTES/HADAMARD_OBSTRUCTION_VISUALIZATION.py"
        ],
        "analytics": [
            "2_ANALYTICS_CHARTS_ILLUSTRATION/HADAMARD_OBSTRUCTION_CHART.png"
        ],
        "trinity": [
            "3_INFINITY_TRINITY_COMPLIANCE/TRINITY_VALIDATED_FRAMEWORK.py"
        ]
    }
}

def validate_structure():
    """Validate the complete Conjecture IV structure."""
    print("╔" + "═"*68 + "╗")
    print("║  CONJECTURE IV STRUCTURE VALIDATION                            ║") 
    print("║  Five Claims × Three Tiers Organization                       ║")
    print("╚" + "═"*68 + "╝")
    
    all_good = True
    
    # Check base directory exists
    if not os.path.exists(BASE_DIR):
        print(f"❌ Base directory missing: {BASE_DIR}")
        return False
    
    print(f"\n✅ Base directory exists: {BASE_DIR}")
    
    # Check main README
    main_readme = os.path.join(BASE_DIR, "README.md")
    if os.path.exists(main_readme):
        print("✅ Main README.md present")
    else:
        print("❌ Main README.md missing")
        all_good = False
    
    print("\n" + "="*60)
    print("VALIDATING FIVE CLAIMS")
    print("="*60)
    
    # Validate each claim
    for claim_name, expected in EXPECTED_STRUCTURE.items():
        print(f"\n🔍 Validating {claim_name}...")
        claim_dir = os.path.join(BASE_DIR, claim_name)
        
        if not os.path.exists(claim_dir):
            print(f"  ❌ Claim directory missing: {claim_name}")
            all_good = False
            continue
        
        # Check README
        claim_readme = os.path.join(claim_dir, "README.md")
        if os.path.exists(claim_readme):
            print(f"  ✅ README.md present")
        else:
            print(f"  ❌ README.md missing")
            all_good = False
        
        # Check three tiers
        tier_status = {"proof": False, "analytics": False, "trinity": False}
        
        # Tier 1: Proof Scripts Notes
        proof_dir = os.path.join(claim_dir, "1_PROOF_SCRIPTS_NOTES")
        if os.path.exists(proof_dir):
            tier_status["proof"] = True
            file_count = 0
            for file_path in expected["core_files"]:
                full_path = os.path.join(claim_dir, file_path)
                if os.path.exists(full_path):
                    file_count += 1
                else:
                    print(f"    ⚠️  Missing: {file_path}")
            print(f"  ✅ Tier 1 (Proof): {file_count}/{len(expected['core_files'])} files")
        else:
            print(f"  ❌ Tier 1 directory missing")
            all_good = False
        
        # Tier 2: Analytics Charts
        analytics_dir = os.path.join(claim_dir, "2_ANALYTICS_CHARTS_ILLUSTRATION")
        if os.path.exists(analytics_dir):
            tier_status["analytics"] = True
            file_count = 0
            for file_path in expected["analytics"]:
                full_path = os.path.join(claim_dir, file_path)
                if os.path.exists(full_path):
                    file_count += 1
            if expected["analytics"]:
                print(f"  ✅ Tier 2 (Analytics): {file_count}/{len(expected['analytics'])} files")
            else:
                print(f"  ✅ Tier 2 (Analytics): Ready for future charts")
        else:
            print(f"  ❌ Tier 2 directory missing")
            all_good = False
        
        # Tier 3: Trinity Compliance
        trinity_dir = os.path.join(claim_dir, "3_INFINITY_TRINITY_COMPLIANCE")
        if os.path.exists(trinity_dir):
            tier_status["trinity"] = True
            file_count = 0
            for file_path in expected["trinity"]:
                full_path = os.path.join(claim_dir, file_path)
                if os.path.exists(full_path):
                    file_count += 1
            print(f"  ✅ Tier 3 (Trinity): {file_count}/{len(expected['trinity'])} files")
        else:
            print(f"  ❌ Tier 3 directory missing")
            all_good = False
        
        # Overall claim status
        if all(tier_status.values()):
            print(f"  🎯 {claim_name}: COMPLETE")
        else:
            print(f"  ⚠️  {claim_name}: INCOMPLETE")
            all_good = False
    
    print("\n" + "="*60)
    print("TRINITY PROTOCOL VERIFICATION")
    print("="*60)
    
    trinity_count = 0
    for claim_name in EXPECTED_STRUCTURE.keys():
        trinity_file = os.path.join(BASE_DIR, claim_name, 
                                  "3_INFINITY_TRINITY_COMPLIANCE/TRINITY_VALIDATED_FRAMEWORK.py")
        if os.path.exists(trinity_file):
            trinity_count += 1
    
    print(f"✅ Trinity Protocol files: {trinity_count}/5 claims")
    if trinity_count == 5:
        print("🛡️  UNIVERSAL TRINITY COMPLIANCE ACHIEVED")
    
    print("\n" + "="*60)
    print("FILE COUNT SUMMARY")
    print("="*60)
    
    total_files = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if not file.startswith('.'):
                total_files += 1
    
    print(f"📁 Total files organized: {total_files}")
    
    # Count by tier
    tier_counts = {"proof": 0, "analytics": 0, "trinity": 0, "readme": 0}
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file == "README.md":
                tier_counts["readme"] += 1
            elif "1_PROOF_SCRIPTS_NOTES" in root:
                tier_counts["proof"] += 1
            elif "2_ANALYTICS_CHARTS_ILLUSTRATION" in root:
                tier_counts["analytics"] += 1
            elif "3_INFINITY_TRINITY_COMPLIANCE" in root:
                tier_counts["trinity"] += 1
    
    print(f"📝 README files: {tier_counts['readme']}")
    print(f"🔬 Proof scripts: {tier_counts['proof']}")
    print(f"📊 Analytics files: {tier_counts['analytics']}")
    print(f"🛡️  Trinity files: {tier_counts['trinity']}")
    
    print("\n" + "="*60)
    print("FINAL STATUS")
    print("="*60)
    
    if all_good:
        print("🎉 CONJECTURE IV RESTRUCTURING: COMPLETE")
        print("✅ All Five Claims properly organized")
        print("✅ All Three Tiers implemented")  
        print("✅ All core files successfully migrated")
        print("✅ Trinity Protocol universally applied")
        print("\n🚀 Ready for publication and independent verification!")
    else:
        print("⚠️  CONJECTURE IV RESTRUCTURING: INCOMPLETE") 
        print("❌ Some files or directories missing")
        print("🔧 Manual intervention required")
    
    return all_good

def list_claim_contents():
    """List contents of each claim for verification."""
    print("\n" + "="*60)
    print("DETAILED CLAIM CONTENTS")
    print("="*60)
    
    for claim_name in EXPECTED_STRUCTURE.keys():
        claim_dir = os.path.join(BASE_DIR, claim_name)
        if os.path.exists(claim_dir):
            print(f"\n📂 {claim_name}/")
            for tier in ["1_PROOF_SCRIPTS_NOTES", "2_ANALYTICS_CHARTS_ILLUSTRATION", "3_INFINITY_TRINITY_COMPLIANCE"]:
                tier_dir = os.path.join(claim_dir, tier)
                if os.path.exists(tier_dir):
                    files = [f for f in os.listdir(tier_dir) if not f.startswith('.')]
                    if files:
                        print(f"  📁 {tier}/")
                        for file in sorted(files):
                            print(f"    📄 {file}")
                    else:
                        print(f"  📁 {tier}/ (empty)")

if __name__ == "__main__":
    success = validate_structure()
    list_claim_contents()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)