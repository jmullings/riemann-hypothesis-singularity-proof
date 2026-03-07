"""
Calculate weights to 25 decimal places using Python's Decimal module.
"""
from decimal import Decimal, getcontext

# Set precision to 35 decimal places for calculations
getcontext().prec = 35

# Golden ratio to high precision
PHI = Decimal('1.6180339887498948482045868343656381')
NUM_BRANCHES = 9

# Original Conjecture V raw weights (from RH_SINGULARITY.py geodesic analysis)
CONJECTURE_V_WEIGHTS_RAW = [
    Decimal('0.0175504462'),
    Decimal('0.1471033037'),
    Decimal('0.0041498042'),
    Decimal('0.3353044327'),
    Decimal('0.0981287513'),
    Decimal('0.0127626154'),
    Decimal('0.1906439411'),
    Decimal('0.1869808699'),
    Decimal('0.0073758354'),
]

raw_sum = sum(CONJECTURE_V_WEIGHTS_RAW)
print(f"Raw sum: {raw_sum}")

# Normalized Conjecture V weights
print("\n" + "="*80)
print("CONJECTURE V WEIGHTS NORMALIZED (25 decimal places)")
print("="*80)
cv_weights_norm = [w / raw_sum for w in CONJECTURE_V_WEIGHTS_RAW]
for k, w in enumerate(cv_weights_norm):
    print(f"    Decimal('{str(w)[:27]}'),   # k={k}")

# Branch signatures
signatures = [Decimal((-1)**k) for k in range(NUM_BRANCHES)]

# Alternating sum of raw normalized weights
alt_sum_raw = sum(w * s for w, s in zip(cv_weights_norm, signatures))
print(f"\nAlternating sum (before calibration): {alt_sum_raw}")

# Calculate even and odd sums
even_sum = sum(cv_weights_norm[k] for k in [0, 2, 4, 6, 8])
odd_sum = sum(cv_weights_norm[k] for k in [1, 3, 5, 7])

print(f"\nEven sum (before): {even_sum}")
print(f"Odd sum (before):  {odd_sum}")

# Scale even and odd to both equal 0.5
target = Decimal('0.5')
even_scale = target / even_sum
odd_scale = target / odd_sum

# Apply scaling
calibrated = []
for k in range(NUM_BRANCHES):
    if k % 2 == 0:
        calibrated.append(cv_weights_norm[k] * even_scale)
    else:
        calibrated.append(cv_weights_norm[k] * odd_scale)

# Normalize to sum to 1
cal_sum = sum(calibrated)
calibrated_norm = [w / cal_sum for w in calibrated]

print("\n" + "="*80)
print("CALIBRATED BALANCED WEIGHTS (25 decimal places)")
print("="*80)
for k, w in enumerate(calibrated_norm):
    marker = "***" if k in [3, 6, 7] else "   "
    print(f"    Decimal('{str(w)[:27]}'),   # k={k} {marker}")

# Verify balance
alt_sum_cal = sum(w * s for w, s in zip(calibrated_norm, signatures))
even_sum_cal = sum(calibrated_norm[k] for k in [0, 2, 4, 6, 8])
odd_sum_cal = sum(calibrated_norm[k] for k in [1, 3, 5, 7])

print(f"\nVerification:")
print(f"  Alternating sum: {alt_sum_cal}")
print(f"  Even sum:        {even_sum_cal}")
print(f"  Odd sum:         {odd_sum_cal}")
print(f"  Total sum:       {sum(calibrated_norm)}")

# Also compute base φ-weights for comparison
print("\n" + "="*80)
print("BASE φ-WEIGHTS (25 decimal places)")
print("="*80)
phi_weights = [PHI**(-(k+1)) for k in range(NUM_BRANCHES)]
phi_sum = sum(phi_weights)
phi_norm = [w / phi_sum for w in phi_weights]
for k, w in enumerate(phi_norm):
    print(f"    Decimal('{str(w)[:27]}'),   # k={k}")

alt_sum_phi = sum(w * s for w, s in zip(phi_norm, signatures))
print(f"\nφ-weights alternating sum: {alt_sum_phi}")

# Output ready-to-use Python code
print("\n" + "="*80)
print("READY-TO-USE CODE (paste into CONJECTURE_V_CALIBRATION.py)")
print("="*80)
print("""
# Conjecture V geodesic-derived weights (25 decimal places)
# From RH_SINGULARITY.py empirical analysis on 2500 T-values with 81 true zeros
CONJECTURE_V_WEIGHTS = np.array([""")
for k, w in enumerate(cv_weights_norm):
    print(f"    {str(w)[:27]},   # k={k}")
print("])")

print("\n# Calibrated BALANCED weights (25 decimal places)")
print("# These achieve Σ w_k σ_k = 0 for spectral confinement")
print("CALIBRATED_BALANCED_WEIGHTS = np.array([")
for k, w in enumerate(calibrated_norm):
    marker = "# DOMINANT" if k in [3, 6, 7] else ""
    print(f"    {str(w)[:27]},   # k={k} {marker}")
print("])")
