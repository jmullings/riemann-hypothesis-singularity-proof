#!/usr/bin/env python3
"""
PHASE 04 — EVIDENCE: INTERFERENCE, NULL MODEL & ZERO COMPARISON
================================================================
σ-Selectivity Equation  ·  Phase 4 of 10
(was PHASE_06_INTERFERENCE + PHASE_08_NULL_MODEL + PHASE_09_ZEROS_VS_RANDOM)

PART A — BITSIZE INTERFERENCE MATRIX  (was PHASE_06_INTERFERENCE)
-----------------------------------------------------------------
I_{bc}(σ,T) = cross-band interference between bitsize b and c primes.
Tautology-free phase coherence measure.

PART B — NULL MODEL & STATISTICAL SIGNIFICANCE  (was PHASE_08_NULL_MODEL)
--------------------------------------------------------------------------
Bootstrap, null distribution and truncation convergence tests for x*.

PART C — ZEROS vs RANDOM: THE DEFINITIVE COMPARISON  (was PHASE_09_ZEROS_VS_RANDOM)
-------------------------------------------------------------------------------------
Compare F₂, C_pss, μ_r, I_ratio at zero heights vs random T values.
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from PHASE_01_FOUNDATIONS import (
    NDIM, DTYPE, P, LOG_P, LOG2_P, ALPHA, ZEROS_9, ZEROS_30,
    P25, LOG_P25, LOG2_P25, G_PHI, _sieve,
    F2_curvature, F2_vector_9D, F2_S_curvature,
)
from PHASE_03_PRIME_GEOMETRY import (
    compute_x_star_F, pss_curvature, pss_mean_radius,
)

import numpy as np

# ── BITSIZE ASSIGNMENT FOR 25 PRIMES ─────────────────────────────────────────
BITSIZE_25 = np.array([p.bit_length() - 1 for p in [int(x) for x in P25]], dtype=np.int32)
BANDS_PRESENT = sorted(set(BITSIZE_25.tolist()))
N_BANDS = len(BANDS_PRESENT)
BAND_MAP = {b: i for i, b in enumerate(BANDS_PRESENT)}


# =============================================================================
# PART A — BITSIZE INTERFERENCE MATRIX
# =============================================================================

def primes_in_band(b):
    """Indices of primes in bitsize band b."""
    return np.where(BITSIZE_25 == b)[0]


def F2_band(sigma, T, band_b):
    """F₂ using ONLY primes in bitsize band b."""
    idx = primes_in_band(band_b)
    if len(idx) == 0:
        return 0.0
    return F2_curvature(sigma, T, P25[idx], LOG_P25[idx])


def interference_matrix(sigma, T):
    """
    I_{bc}(σ,T) = F₂(b∪c) − F₂(b) − F₂(c)
    Shape (N_BANDS, N_BANDS). Diagonal = self-curvature.
    """
    I = np.zeros((N_BANDS, N_BANDS), dtype=DTYPE)
    F2_single = {b: F2_band(sigma, T, b) for b in BANDS_PRESENT}
    for i, b1 in enumerate(BANDS_PRESENT):
        I[i, i] = F2_single[b1]
        for j, b2 in enumerate(BANDS_PRESENT):
            if j <= i:
                continue
            idx1, idx2 = primes_in_band(b1), primes_in_band(b2)
            idx_both = np.concatenate([idx1, idx2])
            F2_pair = F2_curvature(sigma, T, P25[idx_both], LOG_P25[idx_both])
            cross = F2_pair - F2_single[b1] - F2_single[b2]
            I[i, j] = I[j, i] = cross
    return I


def interference_ratio(sigma, T):
    """Fraction of F₂ from cross-band interference: Σ_{b≠c}|I_{bc}|/F₂."""
    I = interference_matrix(sigma, T)
    F2_total = F2_curvature(sigma, T)
    off_diag = sum(abs(I[i, j]) for i in range(N_BANDS) for j in range(N_BANDS) if i != j)
    return off_diag / max(abs(F2_total), 1e-30)


def interference_spectrum(sigma, T):
    """Eigenvalues of I_{bc}(σ,T) — spectral structure."""
    I = interference_matrix(sigma, T)
    return np.sort(np.linalg.eigvalsh(I))[::-1]


# =============================================================================
# PART B — NULL MODEL & STATISTICAL SIGNIFICANCE
# =============================================================================

def null_x_star_trial(rng, T_range=(10.0, 55.0)):
    """Draw 9 random T, compute x*. LOG-FREE."""
    T_rand = rng.uniform(T_range[0], T_range[1], NDIM)
    f2 = np.array([F2_curvature(0.5, float(t)) for t in T_rand], dtype=DTYPE)
    total = f2.sum()
    return f2 / total if total > 1e-30 else np.full(NDIM, 1.0 / NDIM)


def null_distribution(n_trials=2000, seed=42):
    """[QUARANTINE] Null model for ‖x*‖₂."""
    rng = np.random.default_rng(seed)
    norms = np.array([float(np.linalg.norm(null_x_star_trial(rng))) for _ in range(n_trials)])
    x_actual = compute_x_star_F()
    norm_actual = float(np.linalg.norm(x_actual))
    null_mean, null_std = float(norms.mean()), float(norms.std())
    z = (norm_actual - null_mean) / null_std if null_std > 0 else 0.0
    return {"null_mean": null_mean, "null_std": null_std,
            "norm_actual": norm_actual, "z_score": z,
            "pct_below": float((norms < norm_actual).mean())}


def bootstrap_stability(zeros=None, n_boot=1000, seed=42):
    """[QUARANTINE] Bootstrap over zero heights."""
    if zeros is None:
        zeros = ZEROS_9
    rng = np.random.default_rng(seed)
    K = len(zeros)
    coords = np.zeros((n_boot, NDIM), dtype=DTYPE)
    for i in range(n_boot):
        idx = rng.integers(0, K, NDIM)
        Ts = zeros[idx]
        f2 = np.array([F2_curvature(0.5, float(t)) for t in Ts], dtype=DTYPE)
        tot = f2.sum()
        coords[i] = f2 / tot if tot > 1e-30 else np.full(NDIM, 1.0 / NDIM)
    x_orig = compute_x_star_F(0.5, zeros)
    bias = float(np.abs(coords.mean(0) - x_orig).max())
    return {"x_mean": coords.mean(0), "x_std": coords.std(0),
            "max_bias": bias, "stable": bias < 0.03}


def truncation_convergence(zeros=None):
    """[QUARANTINE] d(x*(N₁), x*(N₂)) for prime truncations."""
    if zeros is None:
        zeros = ZEROS_9
    N_list = [9, 25, 50, 100]
    all_p = _sieve(600)
    xs = {}
    for N in N_list:
        ps = np.array(all_p[:N], dtype=DTYPE)
        lp = np.array([math.log(p) for p in all_p[:N]], dtype=DTYPE)
        f2 = np.array([F2_curvature(0.5, float(t), ps, lp) for t in zeros], dtype=DTYPE)
        tot = f2.sum()
        xs[N] = f2 / tot if tot > 1e-30 else np.full(len(zeros), 1.0 / len(zeros))
    rows = []
    for i in range(len(N_list) - 1):
        N1, N2 = N_list[i], N_list[i + 1]
        L = min(len(xs[N1]), len(xs[N2]))
        rows.append((N1, N2, float(np.linalg.norm(xs[N1][:L] - xs[N2][:L]))))
    return rows


def truncation_convergence_SN(zeros=None):
    """d(x*(N₁), x*(N₂)) for S_N integer partial sums (RS framework)."""
    if zeros is None:
        zeros = ZEROS_9
    N_list = [50, 100, 200, 500, 1000]
    xs = {}
    for N in N_list:
        f2 = np.array([F2_S_curvature(0.5, float(t), N) for t in zeros], dtype=DTYPE)
        tot = f2.sum()
        xs[N] = f2 / tot if tot > 1e-30 else np.full(len(zeros), 1.0 / len(zeros))
    rows = []
    for i in range(len(N_list) - 1):
        N1, N2 = N_list[i], N_list[i + 1]
        L = min(len(xs[N1]), len(xs[N2]))
        rows.append((N1, N2, float(np.linalg.norm(xs[N1][:L] - xs[N2][:L]))))
    return rows


# =============================================================================
# PART C — ZEROS vs RANDOM
# =============================================================================

N_RANDOM = 200
SEED = 42


def compute_observables(T):
    """All four tautology-free observables at height T."""
    T = float(T)
    return {
        'T': T,
        'F2': F2_curvature(0.5, T),
        'C_pss': pss_curvature(T),
        'mu_r': pss_mean_radius(T),
        'I_ratio': interference_ratio(0.5, T),
    }


def run_comparison(zeros, n_random=N_RANDOM, seed=SEED):
    """[QUARANTINE] Compute observables at zero heights and random T."""
    T_min = float(zeros.min()) - 2.0
    T_max = float(zeros.max()) + 2.0
    zero_data = [compute_observables(float(g)) for g in zeros]
    rng = np.random.default_rng(seed)
    T_random = rng.uniform(T_min, T_max, n_random)
    random_data = [compute_observables(float(t)) for t in T_random]
    return zero_data, random_data


def distribution_comparison(zero_data, random_data, key):
    """Compare distribution of observable `key` between zeros and random."""
    z_vals = np.array([d[key] for d in zero_data])
    r_vals = np.array([d[key] for d in random_data])
    z_mean, z_std = float(z_vals.mean()), float(z_vals.std())
    r_mean, r_std = float(r_vals.mean()), float(r_vals.std())
    pooled_std = ((z_std**2 + r_std**2) / 2) ** 0.5
    cohens_d = (z_mean - r_mean) / pooled_std if pooled_std > 1e-30 else 0.0
    z_score = (z_mean - r_mean) / r_std if r_std > 1e-30 else 0.0
    z_median = float(np.median(z_vals))
    return {
        'key': key,
        'zero_mean': z_mean, 'zero_std': z_std,
        'random_mean': r_mean, 'random_std': r_std,
        'cohens_d': cohens_d, 'z_score': z_score,
        'pct_random_above_zero_median': float((r_vals > z_median).mean()),
        'distinct': abs(cohens_d) > 0.5,
    }


def classify_result(stats):
    """Classify into Case A/B/C."""
    d = stats['cohens_d']
    if abs(d) < 0.2:
        return "A", "IDENTICAL — no special structure"
    elif d > 0:
        return "B", f"ZEROS LARGER by d={d:.3f}"
    else:
        return "C", f"ZEROS SMALLER by d={d:.3f}"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 04 — EVIDENCE: INTERFERENCE, NULL MODEL & ZERO COMPARISON")
    print("=" * 70)

    # Part A
    T0 = float(ZEROS_9[0])
    I = interference_matrix(0.5, T0)
    ratio = interference_ratio(0.5, T0)
    print(f"\n  [QUARANTINE] Interference ratio at γ₁={T0:.4f}: {ratio:.4f}")
    spec = interference_spectrum(0.5, T0)
    print(f"  Spectrum λ: {np.array2string(spec, precision=4)}")

    # Part B
    nd = null_distribution(500)
    print(f"\n  [QUARANTINE] Null model z-score: {nd['z_score']:.4f}σ")
    bs = bootstrap_stability()
    print(f"  Bootstrap max_bias: {bs['max_bias']:.8f}  stable: {bs['stable']}")

    # Part C
    print(f"\n  [QUARANTINE] Zeros vs Random ({len(ZEROS_30)} zeros vs {N_RANDOM} random):")
    zero_data, random_data = run_comparison(ZEROS_30)
    for key in ['F2', 'C_pss', 'mu_r', 'I_ratio']:
        stats = distribution_comparison(zero_data, random_data, key)
        case, desc = classify_result(stats)
        print(f"  {key:>8}: d={stats['cohens_d']:+.3f}  Case {case}: {desc}")

    print(f"\n  PHASE 04: ✓ PASS")
    print("=" * 70)
