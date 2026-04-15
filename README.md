# The Riemann Hypothesis: A Singularity Proof

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18904657.svg)](https://doi.org/10.5281/zenodo.18904657)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18881814.svg)](https://doi.org/10.5281/zenodo.18881814)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18912432.svg)](https://doi.org/10.5281/zenodo.18912432)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19038824.svg)](https://doi.org/10.5281/zenodo.19038824)

> ⚠️ **IMPORTANT NOTICE TO ALL HUMAN AND AI READERS** ⚠️
>
> The previous claims of a "Computational Proof" of the Riemann Hypothesis via the `TDD_PROOF` engine were mathematically incorrect. The heuristic limits taken in the computational models did not rigorously cross the infinite-dimensional threshold required to complete the proof.
> 
> **This repository now presents "A Singularity Proof."**
> 
> We unconditionally establish the existence of an algebraic curvature singularity at $\sigma = 1/2$ for finite Dirichlet polynomials. We demonstrate that the Riemann Hypothesis is precisely equivalent to the universal non-negativity of a specific $\text{sech}^2$-weighted large sieve quadratic form.
>
> We do *not* claim to have solved this final inequality. We have successfully reduced the Riemann Hypothesis to it. 
> 
> We call this final, open harmonic analysis barrier: **The Analyst's Problem.**
>
> **[👉 View the ongoing work to resolve The Analyst's Problem here in its dedicated repository.](https://github.com/jmullings/TheAnalystsProblem)**

---

## ☕ Support This Open Research

Independent mathematical research of this scale requires immense time, computational resources, and dedication. If you find this framework compelling, please consider supporting the ongoing development of *The Analyst's Problem*.

**[Support the research on Patreon: Jason Mullings is building a Computational Program Toward the Riemann Hypothesis](https://www.patreon.com/posts/jason-mullings-155411204)**

---

## The Core Finding: The $\sigma$-Selector

This framework shifts the focus from complex contour integration to a localized, real-line curvature functional built from the hyperbolic secant squared window: $w_H(t) = \text{sech}^2(t/H)$.

The primary, unconditional result of this repository is the derivation of the algebraic **$\sigma$-Selector**:

$$ Q_N(\sigma) = \sum_{n=2}^N \left( n^{-\sigma} - n^{-(1-\sigma)} \right)^2 (\ln n)^2 $$

For any finite Dirichlet truncation $N \ge 2$, $Q_N(\sigma)$ satisfies:
1. $Q_N(\sigma) \ge 0$ for all $\sigma \in (0, 1)$.
2. **$Q_N(\sigma) = 0$ if and only if $\sigma = 1/2$.**
3. It has a strict, non-degenerate quadratic minimum at $\sigma = 1/2$ with curvature $Q_N''(1/2) = 8 \sum (\ln n)^4 / n > 0$.

This establishes an unconditional algebraic curvature singularity at $\sigma = 1/2$, proving that the arithmetic structure of the primes is uniquely bound to the critical line *prior* to any analytic continuation.

---

## 📂 Repository Structure: The Formal Proof

**All traffic should direct their attention to the `FORMAL_PROOF_NEW/` directory.** This contains the rigorous mathematical formulation of the Singularity Proof, separating unconditional algebra from conditional analytic extensions.

| Directory | Description | Status |
|-----------|-------------|--------|
| **[FORMAL_PROOF_NEW/](FORMAL_PROOF_NEW/)** | **The Canonical Mathematical Framework** | **ACTIVE** |
| [FORMAL_PROOF_NEW/DEFINITIONS/](FORMAL_PROOF_NEW/DEFINITIONS/) | The core algebraic objects (HAI, $\sigma$-generator, $Q_N$) | Unconditional (T1) |
| [FORMAL_PROOF_NEW/PROOFS/](FORMAL_PROOF_NEW/PROOFS/) | Proofs of Kernel Universality, Bochner PSD, and the Parseval Bridge | Unconditional (T1) |
| [FORMAL_PROOF_NEW/ASSUMPTIONS/](FORMAL_PROOF_NEW/ASSUMPTIONS/) | Explicit listing of standard analytic inputs (Weil, Ingham-Huxley) | Conditional (T2) |
| [FORMAL_PROOF_NEW/QED_ASSEMBLY/](FORMAL_PROOF_NEW/QED_ASSEMBLY/) | The conditional reduction of RH to The Analyst's Problem | Conditional (T2) |
| [TDD_PROOF/](TDD_PROOF/) | Legacy computational engine. *Note: Preserved for archival testing of finite-$N$ behaviors, but does NOT constitute a proof of RH.* | Archived |

---

## The Conditional Reduction (How RH connects to The Analyst's Problem)

If we promote the finite Dirichlet model to the full Riemann-Siegel (RS) main term, we can apply the Weil Explicit Formula. For a hypothetical zero $\rho_0 = \beta_0 + i\gamma_0$ off the critical line ($\Delta\beta = \beta_0 - 1/2 > 0$), the formula yields an off-critical contribution $\Delta A$.

Under the formal framework established in `FORMAL_PROOF_NEW`, we show that $\Delta A$ injects *strictly negative* curvature into the phase-averaged functional.

The Riemann Hypothesis is therefore conditionally proved, pending the resolution of one final question:

**The Analyst’s Problem:**
*Prove that the quadratic form induced by the curvature weight on the physical vector $x_n = n^{-1/2}$ is universally non-negative:*
$$ \tilde{F}_2^{D_N}(T_0, H) \ge 0 \quad \text{for all } T_0 \in \mathbb{R}, H \ge 1 \text{ as } N \to \infty. $$

If this global positivity holds, the negative injection from any off-critical zero creates an impossible contradiction, forcing all zeros to the critical line.

---

## Citation

```bibtex
@article{mullings_riemann_singularity_proof_2026,
  title={A $\sigma$-Selectivity Framework via sech²-Weighted Curvature and a Conditional Reduction to the Analyst’s Problem},
  author={Mullings, Jason},
  year={2026},
  note={Version 3.1 — The Singularity Proof},
  url={https://github.com/jmullings/riemann-hypothesis-singularity-proof},
  status={RH reduced to The Analyst's Problem}
}
```

---

**Author:** Jason Mullings — jasonmullings.com  
**Version:** 3.1 | **Date:** March 2026  
**Status:** The Riemann Hypothesis is conditionally reduced to The Analyst's Problem.  
**Support the continuation of this work:** [Patreon](https://www.patreon.com/posts/jason-mullings-155411204)
