# PATH_2: Weil Explicit Formula — PRIMARY PROOF ROUTE

**Status:** Active  
**Difficulty:** ★★★★☆  
**Reviewer consensus:** All three reviewers — "most viable pathway"

---

## Summary

The Weil explicit formula is the proven mathematical machinery for translating
prime sums into statements about zeros of ζ(s). This is the native language of
our existing Dirichlet polynomial computations.

Your codebase already builds the infrastructure: `D_sigma()` in
`SINGULARITY_ORIGINAL.py` computes exactly `D̃(σ,T;X) = Σ log(p)·p^{-σ-iT}` —
the correctly-weighted polynomial that the Weil formula requires.

## The Three Theorems

| Theorem | Name | Status |
|---------|------|--------|
| A | Kernel Admissibility | A1–A4 PROVED; A5' (strip condition) OPEN |
| B | Weight Correction | B1, B4 PROVED; B2 verified numerically; B5 OPEN |
| C | Truncation Control | C1–C4 PROVED; C5, C6 OPEN (crux) |

**Theorem A** — `sech²(LAMBDA_STAR·t)` satisfies: even ✓, real-valued ✓,
Fourier transform `ĥ(ω) ≥ 0` ✓, `‖ĥ‖₁ = 2π` ✓. Strip holomorphicity
`|Im(t)| < π/(2α) ≈ 0.003` falls short of the standard Weil requirement
`|Im(t)| < 1/2`. Resolution: distributional explicit formula.

**Theorem B** — Re-weighting `D → D̃ = Σ log(p)·p^{-σ-iT}` matches the Weil
prime-sum weights exactly. The second derivative `∂²Ẽ/∂σ²` is large and
positive at σ=½ (verified numerically at 9 zeros).

**Theorem C (crux)** — The T-averaged energy `⟨Ẽ⟩_T ≈ Σ log²(p)·p^{-2σ}`
has strictly positive curvature `4·Σ log⁴(p)·p^{-2σ}` at σ=½, uniformly in X.
The missing step (C5–C6): connect the prime sum to ζ(s) via the explicit
formula to force σ=½ as the unique critical point as X → ∞.

## Execution Script

```
EXECUTION/PATH_2_WEIL_EXPLICIT.py
```

Run with: `python3 EXECUTION/PATH_2_WEIL_EXPLICIT.py`

Outputs:
- Theorem A verification (ĥ ≥ 0, L¹, strip analysis)
- Theorem B verification (log-weighted polynomial, F₂ > 0 at 9 zeros)
- Theorem C verification (MV estimate, curvature positivity)
- Status table: PROVED vs OPEN for each sub-claim

## Connection to Existing Codebase

| Existing script | Role in PATH_2 |
|----------------|----------------|
| `SINGULARITY_ORIGINAL.py` | `D_sigma()` = −D̃, `F2()` = ∂²Ẽ/∂σ² |
| `ZEROS_VS_SIGMAS.py` | `_sech2()` kernel, `_E_PSS()` |
| `EQ6_WEIL_EXPLICIT_POSITIVITY.py` | Weil functional positivity (SIGMA_6) |
| `DUAL_PATH_CONVERGENCE.py` | T-averaging infrastructure |

## Priority Next Steps

1. Resolve A5' using distributional/Rudin-type explicit formula
2. Prove B5: analytic positivity of ∂²Ẽ/∂σ² for all X, T
3. Connect C to the classical explicit formula (C5): this is the crux

## References

- Iwaniec–Kowalski, *Analytic Number Theory*, Chapter 5 (explicit formula)
- Montgomery (1971), mean value theorem for Dirichlet polynomials
- Vaughan (1980), large sieve inequality
- Weil (1952), *Sur les formules explicites de la théorie des nombres premiers*
