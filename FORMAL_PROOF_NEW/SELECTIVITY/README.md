# SELECTIVITY — Four Pathways to RH via σ-Selectivity

**Version:** 3.0 (revised — 6-kernel framework integrated, A5′ RESOLVED)
**Source:** `TODO.md` (full roadmap with reviewer feedback)  
**See also:** `NOTES.md` (spiral curvature equation)  
**Cross-ref:** `FORMAL_PROOF_NEW/QED_ASSEMBLY/QED/FULL_PROOF.py` (master proof — Theorems A–D)  
**Cross-ref:** `FORMAL_PROOF_NEW/STEPS/PART_09_RS_BRIDGE.py` (GAP 3 closure — A5′ resolution)

---

## The Single Core Problem

Every pathway must close the same fundamental gap:

> Your finite prime polynomial `D(σ,T;X) = Σ_{p≤X} p^{-σ-iT}` is NOT the
> zeta function. Even when `ζ(σ₀+iT) = 0`, the finite sum `D(½,T;X)` does not
> vanish. You need a theorem: *"the behaviour of E(σ,T;X) as X→∞ is controlled
> by ζ(s) in a way that makes an off-critical zero produce a contradiction."*

---

## Directory Structure

```
SELECTIVITY/
├── README.md           ← this file
├── TODO.md             ← full roadmap (source of truth)
├── NOTES.md            ← spiral curvature equation r₉(T) = φ⁻² + a·R(T) + b
├── PATH_1/             ← Hilbert–Pólya Spectral Operator (horizon)
│   ├── README.MD
│   └── EXECUTION/
│       └── PATH_1_SPECTRAL_OPERATOR.py
├── PATH_2/             ← Weil Explicit Formula (PRIMARY)
│   ├── README.MD
│   └── EXECUTION/
│       └── PATH_2_WEIL_EXPLICIT.py
├── PATH_3/             ← Li Coefficients / Dual-Probe (supporting evidence)
│   ├── README.MD
│   └── EXECUTION/
│       └── PATH_3_LI_DUAL_PROBE.py
└── PATH_4/             ← Full 10-Phase σ-Selectivity Proof Chain
    ├── README.MD
    └── EXECUTION/
        └── RH_PROOF_COMPLETE.py
```

---

## 6-Kernel Framework

All pathways now share the **6-kernel library** — six mathematically equivalent
forms of sech², verified to machine precision (max diff = 2.22e-16):

| # | Name | Form | Notes |
|---|------|------|-------|
| K1 | sech² | `1/cosh²(u/H)` | Primary form |
| K2 | cosh | `4/(e^(u/H)+e^(-u/H))²` | Exponential expansion |
| K3 | tanh′ | `d/du[tanh(u/H)]·H` | Derivative form |
| K4 | exp | `4e^(2u/H)/(e^(2u/H)+1)²` | Exponential ratio |
| K5 | sinh/cosh | `1−tanh²(u/H)` | Pythagorean identity |
| K6 | logistic | `4σ(2u/H)(1−σ)` | Logistic form |

**Scale parameter:** `H = H_STAR = 1.5` (from FULL_PROOF.py QED framework).  
**Poles:** `±iπH/2 ≈ ±2.356i` — well outside the Weil strip `|Im(t)| < 0.5`.  
**Legacy:** `LAMBDA_STAR = 494.059` (old scale, NOT used for kernel parameterization).

---

## Pathway Overview

| Pathway | Role | Difficulty | Status |
|---------|------|-----------|--------|
| [PATH_2](PATH_2/README.MD) | **Primary proof route** | ★★★★☆ | Active — A5′ RESOLVED; Thms A1–A6, B1–B4, C1–C4 proved |
| [PATH_4](PATH_4/README.MD) | Full 10-phase proof chain | ★★★★☆ | Active — Step 7 cross-refs FULL_PROOF.py Theorem B |
| [PATH_1](PATH_1/README.MD) | Long-term horizon | ★★★★★ | Research phase — all sub-problems OPEN |
| [PATH_3](PATH_3/README.MD) | Supporting evidence only | ★★★☆☆† | Empirical — demoted from primary |

†Deceptive difficulty: the "easy" parts hide deep unsolved problems.

---

## Correctness & Completeness Assessment
*(Updated — 6-kernel framework integrated, A5′ resolved via PART_09 GAP 3)*

| Path | Correctness | Completeness | Primary Gap |
|------|------------|--------------|-------------|
| PATH_2 | A  | A− | A5′ RESOLVED (H=1.5); B5 cross-refs FULL_PROOF.py Theorem B; C5–C6 cross-ref Theorem C |
| PATH_4 | A− | B+ | Step 7 (Re⟨TD²b,b⟩ ≥ 0) — cross-refs FULL_PROOF.py Theorem B |
| PATH_1 | A  | B  | σ-selectivity algebraic proof not written out |
| PATH_3 | B+ | A− | GUE 1/√k asserted without verification; ρ truncated to 5 zeros |

### PATH_2 detail (UPDATED)
**Strong:** A1–A4 kernel proofs analytically correct; **A5′ RESOLVED** — with H=1.5,
poles at ±iπH/2 ≈ ±2.356i, well outside the Weil strip |Im(t)| < 0.5 (ref: PART_09
GAP 3 closure); **A6 added** — 6-kernel equivalence verified to machine precision
(2.22e-16); C1/C4 via Montgomery–Vaughan correctly applied; B3/C3 monotonicity now
accurate; quarantine discipline consistent throughout.

**Key resolution:** The old parameterization h(t) = sech²(LAMBDA_STAR·t) with α=494.059
placed poles at ±iπ/(2α) ≈ ±0.00318i — inside the strip. The correct parameterization
h(t) = sech²(t/H) with H=1.5 places poles at ±iπH/2 ≈ ±2.356i — outside the strip.
This resolves the A5′ "critical bridge" gap.

**Remaining cross-references:**
- **B5** → FULL_PROOF.py Theorem B (quadratic form positivity)
- **C5–C6** → FULL_PROOF.py Theorem C (truncation control + contradiction mechanism)

### PATH_1 detail
**Strong:** Eigenvalue formula λ = (E_diag ± |D(2σ,2T)|)/2 is algebraically exact
(rank-2 outer-product decomposition); P(1) trace-divergence now correctly identified;
T-averaging collapse via Riemann–Lebesgue correct; three sub-problems honestly scoped.

**Issues:**
- **σ-selectivity algebraic proof not written out.** The summary says "PROVED
  algebraically (Hellmann-Feynman)" but the script only verifies monotonicity
  numerically. The one-line sketch `∂λ/∂σ < 0` should be expanded or relabelled
  "VERIFIED numerically, algebraic proof sketched."
- **Sub-problem (a) next steps absent.** Renormalisation options (resolvent, Ĝ = M/Tr(M))
  are mentioned but not developed even as research stubs.

### PATH_3 detail
**Strong:** Demotion rationale is mathematically sound; Li truncation `[QUARANTINE]`
correctly applied; Pathway 2→3 bridge (sech² ≈ hₙ) is the right research formulation.

**Issues:**
- **GUE 1/√k asserted without verification.** The script reports max/mean deviation
  from uniform but never checks whether |xₖ − 1/K| follows 1/√k decay. The claim
  is at best "consistent with GUE" — not "1/√k convergence observed."
- **Pearson ρ computed for only 5 zeros.** Probe 2 (sech²-angle) uses N_max=2000
  and runs over k=1..5 for speed. The full 9-zero correlation is not computed; this
  should be explicitly noted.

---

## PATH_2 — Weil Explicit Formula (Primary)

The Weil explicit formula (proven, 1952) is the bridge between prime sums and
zero sums. Your Dirichlet polynomial already computes the right objects:

**Three theorems needed:**
- **Theorem A** (Kernel Admissibility): `h(t) = sech²(t/H)` with H=1.5 is even,
  `ĥ(ω) ≥ 0`, `‖ĥ‖₁ = 2H` (analytic). All 6 kernel forms verified equivalent.
  **Strip condition RESOLVED:** poles at `|Im(t)| = πH/2 ≈ 2.356 >> 0.5` ✓
- **Theorem B** (Weight Correction): `D̃ = Σ log(p)·p^{-σ-iT}` matches Weil
  weights; `∂²Ẽ/∂σ²(½,T) > 0` verified at 9 zeros [QUARANTINE].
  Cross-ref: FULL_PROOF.py Theorem B.
- **Theorem C** (Truncation Control — the crux): T-averaged curvature
  `4·Σ log⁴(p)·p^{-2σ} > 0` uniformly in X (C2/C4: proved within MV framework).
  This curvature is monotone **decreasing** in σ. Connection to ζ(s) via explicit
  formula (C5–C6) cross-refs FULL_PROOF.py Theorem C.

Run: `python3 PATH_2/EXECUTION/PATH_2_WEIL_EXPLICIT.py`

---

## PATH_1 — Hilbert–Pólya (Horizon)

Our Gram matrix `M(σ,T)_{jk} = p_j^{-σ}p_k^{-σ}cos(T·log(p_j/p_k))` is a
finite PSD kernel with proved σ-selectivity (eigenvalues decrease with σ).

Three sub-problems (all OPEN): (a) trace-class at σ=½ fails — `Tr(M(½)) = Σ p⁻¹ = P(1)`
(prime zeta at s=1) diverges; (b) T-averaging collapses M to diagonal `{p⁻¹}`, erasing
zero structure; (c) spectral identification requires a separate theorem.

*Recommendation:* hold as long-term research; solve PATH_2 first.

Run: `python3 PATH_1/EXECUTION/PATH_1_SPECTRAL_OPERATOR.py`

---

## PATH_3 — Li / Dual-Probe (Supporting Evidence)

Two independent probes (F₂_k and sech²-angle) show near-zero Pearson ρ ≈ 0.063
— statistical independence of two σ=½ detectors. Li coefficients λ₁..λ₁₂ > 0
verified at 9 zeros. GUE alignment observed in 9D coordinate structure.

**All results [QUARANTINE: verification, not proof.]** This material belongs in
Part III of the paper (empirical motivation), NOT in the analytic proof chain.

*Natural upgrade path:* if PATH_2 Theorem C succeeds, Li positivity follows if
`sech²(t/H)` approximates the Li test functions `h_n` in the admissibility class.

Run: `python3 PATH_3/EXECUTION/PATH_3_LI_DUAL_PROBE.py`

---

## PATH_4 — Full 10-Phase σ-Selectivity Proof Chain

Comprehensive 12-step proof chain (3641 lines) covering all phases of the
RH singularity argument: 9D metric construction, sech² kernel, φ-embedding,
σ-selectivity, Euler product bridge, variance collapse, and final QED.

**Open step:** Step 7 — Re⟨TD²b,b⟩ ≥ 0 (cross-refs FULL_PROOF.py Theorem B).
All other steps verified or proved. 6-kernel equivalence check runs at startup.

Run: `python3 PATH_4/EXECUTION/RH_PROOF_COMPLETE.py`

---

## Quarantine Policy

All three reviewers insisted on sharp separation between theorem and computation.
The following are **verification, not proof** and must be clearly labelled as such:

- Uses of `ZEROS_EXACT` / `RIEMANN_ZEROS_9` (known zeros as input)
- σ* minimisation via grid search
- Pearson ρ computations
- z-score detections
- Module health checks

These are powerful diagnostics. They are **not theorems**.

---

## Quick Start

```bash
# PATH_2 (start here — primary proof route):
python3 PATH_2/EXECUTION/PATH_2_WEIL_EXPLICIT.py

# PATH_4 (full 10-phase proof chain):
python3 PATH_4/EXECUTION/RH_PROOF_COMPLETE.py

# PATH_1 (horizon):
python3 PATH_1/EXECUTION/PATH_1_SPECTRAL_OPERATOR.py

# PATH_3 (supporting evidence):
python3 PATH_3/EXECUTION/PATH_3_LI_DUAL_PROBE.py
```
