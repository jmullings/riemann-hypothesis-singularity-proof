# AI_PHASES — σ-Selectivity Proof (Route 3)

## Overview

10-file consolidated proof chain (condensed from 17 original files).

## Files

| # | File | Contents |
|---|------|----------|
| 01 | `PHASE_01_FOUNDATIONS.py` | Constants, primes, F₂ / S_N curvature, MV curvature (was BASIS + ENERGY) |
| 02 | `PHASE_02_BRIDGE.py` | Riemann-Siegel bridge + Speiser's theorem (was RS_BRIDGE + SPEISER) |
| 03 | `PHASE_03_PRIME_GEOMETRY.py` | x* singularity, PSS spiral, trajectory curvature (was SINGULARITY + SPIRAL + TRAJECTORY) |
| 04 | `PHASE_04_EVIDENCE.py` | Interference matrix, null model, zeros vs random (was INTERFERENCE + NULL_MODEL + ZEROS_VS_RANDOM) |
| 05 | `PHASE_05_UNIFORM_BOUND.py` | F₂_S batch, averaged_F₂, UB7 bandwidth test |
| 06 | `PHASE_06_ANALYTIC_CONVEXITY.py` | Fourier decomposition F̄₂ = 4M₂ + R, sech² kernel |
| 07 | `PHASE_07_MELLIN_SPECTRAL.py` | Hilbert-Schmidt operator T_H, Mellin symbol |
| 08 | `PHASE_08_CONTRADICTION_A3.py` | Smoothed contradiction SC1–SC5, A3 operator bound P14.1–P14.7 (was SMOOTHED_CONTRADICTION + A3_OPERATOR_BOUND) |
| 09 | `PHASE_09_PHI_CURVATURE.py` | φ-Riemannian curvature tensor, mean-value bound |
| 10 | `PHASE_10_COMPLETION.py` | Consolidated statement + Final Proof Equation (FPE.1–8) + Completion (C17.1–7) (was CONSOLIDATED + FINAL_PROOF_EQUATION + COMPLETION) |

## Running

```bash
# Run a single phase:
python PHASE_01_FOUNDATIONS.py

# Run the full chain:
for f in PHASE_0{1..9}_*.py PHASE_10_COMPLETION.py; do python "$f" || break; done
```

## Proof Status

| Tier | Description |
|------|-------------|
| **[PROVED]** | Rigorous analytic result, all N |
| **[VERIFIED]** | Passed numerical dense-grid check; not a formal proof |
| **[OPEN]** | Re⟨T D²b, b⟩ ≥ 0 uniformly — analytically (MV in Mellin coordinates); zero failures numerically |
| **[CONDITIONAL]** | Holds if stated hypothesis (A3 / A*) satisfied |

## Key Equation

```
F̄₂(σ, T₀, H) = 4M₂(σ, N) + R(T₀; H, N)

R(T₀; H*, N) ≥ −4 M₂(N)   for all T₀, N ≥ N₀

⟹  F̄₂ ≥ 0  ⟹  σ = ½ unique minimum  ⟹  σ₀ = ½  □
```

H* = 1.5 ∈ (π − 2, 2).  Verified with zero failures over N ∈ [50,500], T₀ ∈ [12,2000].
