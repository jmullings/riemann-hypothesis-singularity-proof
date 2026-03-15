# FORMAL_PROOF_NEW / PSS_STEPS

**Status:** 🔬 Mirror path — 10 independent PSS:SECH² proof steps  
**Date:** March 13, 2026  
**Author:** Jason Mullings  
**Purpose:** Construct an entirely independent PSS:SECH² singularity proof that reaches the same conclusion as the Prime-side STEPS, using the same Bridges, Sigmas, Definitions, and AXIOMS — but from the *geometric side* of the partial-sum spiral.

---

## Architecture: Two Paths, One Singularity

```
PRIME-SIDE PATH (STEPS/)              PSS:SECH² PATH (PSS_STEPS/)
────────────────────────              ────────────────────────────
STEP_1  AXIOMS ground              ↔  PSS_STEP_1  AXIOMS ground (PSS)
STEP_2  StateFactory primes        ↔  PSS_STEP_2  PSS micro-signature extraction
STEP_3  Definitions DEF_01–10      ↔  PSS_STEP_3  Definitions DEF_01–10 (PSS)
STEP_4  σ* via EQ variance min     ↔  PSS_STEP_4  σ* via EQ4 PSS minimisation
STEP_5  Curvature F₂ > 0           ↔  PSS_STEP_5  PSS:SECH² singularity z-score
STEP_6  10-EQ SVD consensus        ↔  PSS_STEP_6  PSS 9D coordinate construction
STEP_7  EQ singularity geometry    ↔  PSS_STEP_7  Structural independence (ρ≈0)
STEP_8  UBE convexity + DEF layer  ↔  PSS_STEP_8  Bridge verification (PSS side)
STEP_9  Bridge status / PATH A/B   ↔  PSS_STEP_9  Dual singularity convergence
STEP_10 Conditional proof chain    ↔  PSS_STEP_10 PSS:SECH² proof chain + cross-auth
                        │                              │
                        └──────────────────────────────┘
                                       ↓
                        BINDING/DUAL_PATH_CONVERGENCE.py
                   Both paths authenticate each other at γ₁=14.134725
```

---

## What the PSS:SECH² Path Proves (Independently)

The **PSS side** observable is the **partial-sum spiral** of the Dirichlet series over the first 500 primes evaluated at (σ=½, T=γₖ):

```
  z_j(T) = Σ_{p ≤ p_j}  p^{−½−iT}     j = 1, …, 500
```

The amplitude of this spiral — `mu_abs(γₖ)` — measures how far the walk
*departs from the origin* on average.  Under RH (σ=½), the spiral closes
compactly for almost every T.  At the zero heights γₖ, a **SECH² geometric
singularity** concentrates the entire spiral amplitude into the first few
basis vectors: a shock that is statistically independent of the prime-side
EQ-curvature signal (Pearson ρ ≈ 0).

The 10 PSS steps establish:

| PSS_STEP | Claim | Status |
|----------|-------|--------|
| 1 | AXIOMS constants correctly seeded; sech²(x) functional verified | FINITE |
| 2 | PSS micro-vectors (mu_abs, σ_abs, C_k, dist) well-defined at 9 zeros | FINITE |
| 3 | DEF_1–DEF_8 all hold under PSS interpretation | FINITE |
| 4 | σ*(T)=0.5 recovered from PSS EQ4 minimisation | FINITE |
| 5 | mu_abs z-score = +5.90σ at γ₁; genuine statistical singularity | FINITE |
| 6 | PSS 9D coord ‖x_PSS‖₂ ≈ NORM_X_STAR; sech²-kernel embedded | FINITE |
| 7 | ρ(PSS, prime) ≈ 0 — two signals are structurally independent | FINITE |
| 8 | BRIDGE_7 + BRIDGE_9 both verified from PSS perspective | FINITE+CONJ |
| 9 | Both singularities simultaneously pinpoint γ₁=14.134725 | FINITE |
| 10 | PSS proof skeleton assembled; dual-path cross-authentication | SKELETON |

---

## Shared Foundation

Both paths use **identical** axiom infrastructure:

- `FORMAL_PROOF_NEW/CONFIGURATIONS/AXIOMS.py` — sole source of constants
- `LAMBDA_STAR`, `NORM_X_STAR`, `COUPLING_K`, `PHI`
- `FactoredState9D`, `StateFactory`, `Projection6D`
- `BitsizeScaleFunctional`, `NormalizedBridgeOperator`
- 10 EQ-functionals: F₁(σ,T) … F₁₀(σ,T)
- BRIDGES B1–B10 (read-only references, not re-derived)
- DEFINITIONS DEF_1–DEF_8 (verified independently from PSS side)
- SIGMAS EQ1–EQ10 (verified independently via PSS energy)

---

## Data Dependency

```
PSS_STEPS/* ─── pss_micro_signatures_100k_adaptive.csv  (repo root, N=99,999 rows)
             ─── FORMAL_PROOF_NEW/CONFIGURATIONS/AXIOMS.py
             ─── FORMAL_PROOF_NEW/STEPS/*/ANALYTICS/*.csv  (read-only, cross-check)
```

---

## Running the PSS Path

```bash
cd FORMAL_PROOF_NEW/PSS_STEPS

python PSS_STEP_1/EXECUTION/PSS_STEP_01_AXIOMS_GROUND.py
python PSS_STEP_2/EXECUTION/PSS_STEP_02_MICRO_SIGNATURES.py
python PSS_STEP_3/EXECUTION/PSS_STEP_03_VERIFY_DEFINITIONS.py
python PSS_STEP_4/EXECUTION/PSS_STEP_04_SIGMA_STAR.py
python PSS_STEP_5/EXECUTION/PSS_STEP_05_SECH2_SINGULARITY.py
python PSS_STEP_6/EXECUTION/PSS_STEP_06_9D_COORDINATE.py
python PSS_STEP_7/EXECUTION/PSS_STEP_07_INDEPENDENCE.py
python PSS_STEP_8/EXECUTION/PSS_STEP_08_BRIDGE_VERIFICATION.py
python PSS_STEP_9/EXECUTION/PSS_STEP_09_DUAL_CONVERGENCE.py
python PSS_STEP_10/EXECUTION/PSS_STEP_10_PROOF_CHAIN.py

# Final dual-path authentication
python ../BINDING/DUAL_PATH_CONVERGENCE.py
```

All scripts run from the repo root or the PSS_STEPS directory.  No additional
environment setup beyond `numpy`, `mpmath`, `scipy` (optional).

---

## Open Gaps (Inherited from Shared Axiom Layer)

| Gap | Location | Impact |
|-----|----------|--------|
| Axiom 8 / BS-5: inverse bitshift not analytically proved | BRIDGE_7 | Both paths label this CONJECTURAL |
| X→∞ limit: spiral amplitude convergence as P_max→∞ | BRIDGE_9 | Finite computational evidence only |
| Hilbert-Pólya: σ(Ã)={γₙ} | FORMAL conjecture | Both paths inherit this open problem |

These gaps are **equal** on both sides — neither path gains an advantage,
and neither conceals a tautology.  The dual-path authentication in
`BINDING/DUAL_PATH_CONVERGENCE.py` logs every gap explicitly.
