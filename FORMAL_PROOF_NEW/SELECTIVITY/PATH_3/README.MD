# PATH_3: Li Coefficients / Dual-Probe Structure — SUPPORTING EVIDENCE

**Status:** Empirical verification only (demoted from primary)  
**Difficulty as primary:** ★★★☆☆ (deceptive — hides the hard parts)  
**Value as supporting evidence:** ★★★★★  
**Reviewer consensus:** Two of three — "trap as primary proof route"

---

## DEMOTION NOTICE

This pathway was demoted from primary to supporting evidence after three
independent mathematical reviews. Two key problems:

1. **Statistical-algebraic gap** — Pearson ρ ≈ 0.063 between finite probe
   sequences is experimental. Pure mathematics requires deterministic algebraic
   statements.

2. **No known F₂ → λₙ map** — Li coefficients are defined via contour
   integrals of ξ(s). Our F₂_k are local σ-curvatures of a truncated prime
   polynomial. No formula in the literature maps one to the other.

## What This Pathway Contains

### Section 1: Li Coefficients (Verified)
Li's criterion: RH ↔ λₙ > 0 for all n, where
```
λₙ = Σ_ρ [1 − (1 − 1/ρ)ⁿ]  ≈  2 Σₖ Re[1 − (1 − 1/ρₖ)ⁿ]  (9-zero truncation)
```
λ₁..λ₁₂ > 0 verified. **[QUARANTINE: uses known zeros; not proof of Li's criterion]**

### Section 2: Dual Probe
- **Probe 1:** F₂_k = ∂²E/∂σ²(½, γₖ) — σ-curvature at critical line
- **Probe 2:** C_k = SECH²-weighted turning angle of partial-sum trajectory
- **Pearson ρ ≈ 0.063** — near-zero correlation = statistical independence
- This is evidence that two different mathematical lenses independently
  detect σ=½ as special. **[QUARANTINE: empirical diagnostic only]**

### Section 3: 9D Coordinate Structure
- Normalised coordinates xₖ = F₂_k / Σ F₂_j
- R₉ ≈ 0.338 vs φ⁻² ≈ 0.382 (the golden ratio curvature scale)
- Spiral curvature equation (from NOTES.md): `r₉(T) = φ⁻² + a·R(T) + b`
- GUE consistency: 1/√k convergence suggests random matrix theory connection
- **[QUARANTINE: observational only]**

### Section 4: Natural Bridge to Pathway 2
If Pathway 2 succeeds, Li positivity follows if `sech²(α·t)` can approximate
the Li test functions `h_n(γ) = Re[1 − (1 − 1/(½+iγ))ⁿ]` in the admissibility
class. **This is the correct research direction — derive from Pathway 2, not standalone.**

## Execution Script

```
EXECUTION/PATH_3_LI_DUAL_PROBE.py
```

Run with: `python3 EXECUTION/PATH_3_LI_DUAL_PROBE.py`

Outputs:
- Li coefficient table λ₁..λ₁₂
- Dual probe F₂_k and C_k values, Pearson ρ
- 9D coordinate structure and GUE alignment
- Pathway 2→3 bridge explanation

## Paper Role

This material belongs in **Part III (Structural Discovery)** of the paper, not in
the analytic proof chain. It shows the empirical motivation for the proof
strategy and frames the findings within the broader literature (GUE, RMT, Li).

## References

- Li (1997), *The positivity of a sequence of numbers and the Riemann hypothesis*
- Odlyzko (1987), *On the distribution of spacings between zeros of the zeta function*
- Montgomery (1973), *The pair correlation of zeros of the zeta function*
