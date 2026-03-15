# PATH_1: Hilbert–Pólya Spectral Operator — LONG-TERM HORIZON

**Status:** Research phase (all three sub-problems OPEN)  
**Difficulty:** ★★★★★  
**Reviewer consensus:** All three — "extremely hard; not a near-term strategy"

---

## Summary

The Hilbert–Pólya conjecture (1914, open): construct a self-adjoint operator
whose eigenvalues are exactly the imaginary parts `{γₙ}` of the non-trivial
Riemann zeros.

Our candidate kernel is the prime spectral Gram matrix:
```
M(σ,T)_{jk} = p_j^{-σ} · p_k^{-σ} · cos(T · log(p_j/p_k))
```
This is PSD, rank-2, with analytic eigenvalues known in closed form.
**σ-selectivity** — both eigenvalues strictly decrease as σ increases —
is PROVED algebraically for finite N.

## Three Open Sub-Problems

| Sub-problem | Description | Status |
|-------------|-------------|--------|
| (a) | Gram operator trace-class convergence | OPEN |
| (b) | T-parameterisation (matrix depends on T; operator cannot) | OPEN |
| (c) | Spectral identification: spec(Ĝ) = {γₙ} | OPEN |

**Sub-problem (a):** `Tr(M(½)) = Σ p^{-1}` diverges (Mertens). M is not
trace-class at σ=½. Needs renormalisation or resolvent formulation.

**Sub-problem (b):** T-averaging collapses M to diagonal operator with
spectrum `{p^{-1}}` — the prime zeta function, NOT the zero spectrum.
A T-independent kernel encoding the zeros is needed.

**Sub-problem (c):** Even with (a)+(b) resolved, a separate identification
theorem is required. Most difficult sub-problem.

## Execution Script

```
EXECUTION/PATH_1_SPECTRAL_OPERATOR.py
```

Run with: `python3 EXECUTION/PATH_1_SPECTRAL_OPERATOR.py`

Outputs:
- Trace growth analysis at σ=½ (demonstrates divergence)
- T-averaged operator structure (shows diagonal collapse)
- σ-monotonicity of eigenvalues at known zero heights [QUARANTINE]
- Status table for all three sub-problems

## Pathway 2 Connection

All three reviewers agree: solve Pathway 2 first. If Theorem C (truncation
control) succeeds, the Hilbert–Pólya operator may emerge naturally as the
generator of the associated dynamical system — the explicit formula already
provides a spectral interpretation of ζ's zeros through test functions.

## References

- Hilbert–Pólya heuristic (1914); Odlyzko–Snaith (2001)
- Connes (1999), *Trace formula in noncommutative geometry and the zeros of the Riemann zeta function*
- Berry–Keating (1999), `xp` Hamiltonian
