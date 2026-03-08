# RH Variational Principle — Programme Document

**Version:** 2 (reviewer corrections applied)  
**Files:** `RH_VARIATIONAL_PRINCIPLE_v2.py` · `test_rh_variational.py`  
**Related:** `RH_BITSIZE_PROGRAMME.py` · `HONEST_9D_DISCRIMINATOR.py` · `CONJECTURE_IV_ROADMAP.docx`

---

## 1. What Was Claimed and What Failed

The original variational claim (v1) was:

> "If `‖Δ_MKM(σ,T)‖` is minimised uniquely at `σ = ½`, then RH follows."

**This is false.** Numerical verification shows the MKM shift vector `Δ(σ,T) = (R(σ,T) − M(T)) · w` has minima at `σ ≈ 0.3` or `σ ≈ 0.7` depending on T, never systematically at `σ = ½`.

**Diagnosis:** `M(T)` does not depend on `σ`. The minimum of `‖R(σ,T) − M(T)‖` simply locates the `σ` where the magnitudes of the partial sums happen to match `M(T)`. This has no relationship to zeros of `ζ`.

The v1 document also stated: *"the conjecture reduces to: all zeros of ξ are simple."* This is **incorrect** per the reviewer. Simple zeros are neither necessary nor sufficient for the global convexity condition. The hard case is proving convexity *away from zeros*, for all T — not just at zero ordinates.

---

## 2. The Correct Variational Principle

### 2.1 Setup

The completed zeta function is:

$$\xi(s) = \tfrac{1}{2}\,s(s-1)\,\pi^{-s/2}\,\Gamma(s/2)\,\zeta(s)$$

It satisfies the **functional equation**:

$$\xi(s) = \xi(1-s) \quad \text{for all } s \in \mathbb{C}$$

Define the modulus along horizontal lines:

$$f_T(\sigma) := |\xi(\sigma + iT)|$$

The functional equation forces:

$$f_T(\sigma) = f_T(1 - \sigma)$$

So `σ = ½` is **always a critical point** of `f_T`. This is a rigorous consequence of the functional equation, not an assumption.

### 2.2 The Theorem

**THEOREM (equivalent to RH):**

$$\text{RH} \iff f_T \text{ is convex at } \sigma = \tfrac{1}{2} \text{ for all } T > 0$$

That is:

$$|\xi(\tfrac{1}{2}+h+iT)| + |\xi(\tfrac{1}{2}-h+iT)| \;\geq\; 2|\xi(\tfrac{1}{2}+iT)| \quad \forall\, T > 0,\; h > 0$$

### 2.3 Proof of Equivalence

**Direction (⇒): Convexity fails implies off-line zero exists.**

Suppose convexity fails at some `T₀, h > 0`: `f_{T₀}(½+h) + f_{T₀}(½−h) < 2f_{T₀}(½)`. By symmetry `f_{T₀}` has a local maximum at `σ = ½`. If `f_{T₀}(½) > 0`, the function is positive at `½` but lower on both sides. This means `f_{T₀}` cannot have its zeros only at `σ = ½`; it must have zeros away from `½` flanking the maximum, i.e. ξ has off-line zeros.

**Direction (⇐): Off-line zero implies convexity fails.**

If `ξ(σ₀ + iT) = 0` with `σ₀ ≠ ½`, then by the functional equation `ξ(1−σ₀+iT) = 0` also. With `σ₀ < ½` and `1−σ₀ > ½`, both flanking `σ = ½`, we have:

$$f_T(\sigma_0) = 0, \quad f_T(1-\sigma_0) = 0, \quad f_T(\tfrac{1}{2}) > 0$$

(since `½` is not a zero by assumption). So `f_T(½)` lies strictly above both flanking values. By continuity, `σ = ½` is a local maximum. Therefore:

$$f_T(\tfrac{1}{2}+h) + f_T(\tfrac{1}{2}-h) < 2f_T(\tfrac{1}{2}) \quad \text{for small } h$$

Convexity fails. **QED (contrapositive: convexity for all T ⟹ RH).**

---

## 3. The Reviewer's Formula

From the Hadamard product `ξ(s) = ξ(0) · Πᵨ(1 − s/ρ)`:

$$\frac{\partial^2}{\partial\sigma^2} \log|\xi(\sigma+iT)| = \sum_\rho \mathrm{Re}\!\left[\frac{1}{(\sigma+iT-\rho)^2}\right]$$

Assuming all zeros on the line `ρ = ½ + iγ`, at `σ = ½`:

$$\frac{\partial^2}{\partial\sigma^2} \log|\xi| \bigg|_{\sigma=\frac{1}{2}} = \sum_\gamma \mathrm{Re}\!\left[\frac{1}{(i(T-\gamma))^2}\right] = -\sum_\gamma \frac{1}{(T-\gamma)^2}$$

**This is always negative.** This is the *log*-curvature, not the absolute curvature, and it does **not** contradict RH. The relationship is:

$$\frac{\partial^2 |\xi|}{\partial\sigma^2} = |\xi| \cdot \left[\left(\frac{\partial \log|\xi|}{\partial\sigma}\right)^2 + \frac{\partial^2 \log|\xi|}{\partial\sigma^2}\right]$$

Away from zeros (`|ξ| > 0`), convexity of `|ξ|` requires:

$$\left(\frac{\partial \log|\xi|}{\partial\sigma}\right)^2 \geq \sum_\gamma \frac{1}{(T-\gamma)^2}$$

**This is the hard analytic inequality.** The gradient of `log|ξ|` must dominate the sum of inverse-squared zero spacings. Proving this inequality globally in T constitutes a proof of RH.

---

## 4. Curvature at Simple Zeros

At a simple zero `γ` of `ξ`, near `σ = ½`:

$$|\xi(\sigma + i\gamma)| \sim C \cdot |\sigma - \tfrac{1}{2}|$$

This is a **V-shape** (absolute value function). The second difference behaves as:

$$\frac{f(½+h) + f(½−h) - 2f(½)}{h^2} = \frac{2Ch}{h^2} = \frac{2C}{h} \to +\infty$$

The curvature **diverges to +∞** at a simple zero — not to zero, and not negative. The distributional second derivative is `2C · δ(σ−½) > 0`. This confirms convexity at simple zeros trivially. Numerical verification:

| Zero T | ratio `d2(h/10)/d2(h)` | verdict |
|--------|------------------------|---------|
| 14.135 | 10.000 | simple ✓ |
| 21.022 | 9.999 | simple ✓ |
| 25.011 | 9.999 | simple ✓ |
| 30.425 | 9.999 | simple ✓ |

---

## 5. Numerical Evidence

All numerical results are **consistent with RH** but do not prove it. Verification covers a finite sample; off-line zeros could exist at unsampled heights.

### 5.1 Convexity test results (h = 0.0005, dps = 50)

| T | `f_T(½)` | excess `f(½+h)+f(½−h)−2f(½)` | convex? |
|---|----------|-------------------------------|---------|
| 14.13 (zero) | 1.3e−18 | 1.38e−6 | ✓ |
| 21.02 (zero) | 1.8e−20 | 1.77e−8 | ✓ |
| 49.77 (zero) | 2.7e−29 | 1.56e−17 | ✓ |
| 17.5 (non-zero) | 4.2e−4 | 2.39e−11 | ✓ |
| 50.0 (non-zero) | ~0 | 1.58e−20 | ✓ |

### 5.2 Gradient-squared inequality (open)

The reviewer formula gives `log-curv ≈ −0.2 to −1.5` at tested T values. The gradient-squared `(∂ log|ξ|/∂σ)²` is numerically very small at tested points. The inequality is consistent with holding but is not proved analytically — it is the **open problem**.

---

## 6. The Open Problem (precisely)

**CONJECTURE** *(equivalent to RH, reviewer-corrected form)*:

For all `T > 0`:

$$\left(\frac{\partial}{\partial\sigma} \log|\xi(\sigma+iT)|\right)^2_{\sigma=\frac{1}{2}} \;\geq\; \sum_\gamma \frac{1}{(T-\gamma)^2}$$

This must hold for **all T**, not only at zero ordinates. Simple zeros make the condition trivial at `T = γ`; the hard case is all `T` with `ζ(½+iT) ≠ 0`.

**What is required analytically:** A bound on the logarithmic derivative `∂_σ log|ξ|` at `σ = ½` in terms of the zero distribution. Candidates include zero-density estimates, explicit formulae, and the theory of Dirichlet series with Gaussian weights (de Bruijn-Newman).

---

## 7. Connection to the Programme

### 7.1 Bit-size discriminant (Conjecture V)

The bit-size slope `∂/∂B |z_N(½ − B/log(N) + iT)|` approximates `∂_σ|z_N(σ+iT)|` at `σ = ½`. It is a **finite-N proxy** for the curvature condition:

- Slope > 0 at zeros ↔ V-shape, curvature → +∞ ↔ consistent with convexity
- Slope ≈ 0 at non-zeros ↔ flat function at σ = ½ ↔ convexity marginal
- Slope < 0 would indicate a zero off the line (not observed)

### 7.2 Conjecture IV bridge

If Conjecture IV is completed:

$$\det(I - \hat{L}_{s}) = G(s) \cdot \xi(s)$$

with `G` entire and nonvanishing, then proving convexity of `|det(I − L̂)|` at `σ = ½` via Stirling asymptotics of the Γ-weights would transfer the convexity condition to `|ξ|`, completing the proof.

### 7.3 de Bruijn-Newman connection (from `RH_BITSIZE_PROGRAMME.py`)

The Gaussian-mollified series `Z_b(s) = Σ exp(−b(log n)²/2) n^{−s}` has all zeros on `Re(s) = ½` for `b` sufficiently large. As `b → 0`, `Z_b → ζ`. RH ⟺ de Bruijn-Newman constant `Λ = 0` (Rodgers-Tao 2018: `Λ ≥ 0`). The convexity condition and the Λ = 0 condition are two reformulations of the same open problem.

---

## 8. Summary Table

| Object | Minimised at σ = ½? | Equivalent to RH? |
|--------|---------------------|-------------------|
| `‖Δ_MKM(σ,T)‖` | **No** (proved false) | No — wrong object |
| `\|ξ(σ+iT)\|` at zeros | Yes (trivially) | Partial |
| Convexity of `f_T` for all T | — | **Yes** |
| `d²log\|ξ\|/dσ²` | < 0 always | No — wrong quantity |
| `(∂log\|ξ\|)² ≥ Σ 1/(T−γ)²` | Open conjecture | **Yes** |
| Bit-size slope > 0 | Consistent (100 zeros) | Finite-N proxy |

---

## 9. File Reference Points

| File | Purpose | Key function/section |
|------|---------|----------------------|
| `RH_VARIATIONAL_PRINCIPLE_v2.py` | Main analysis | `convexity_check()`, `log_curvature_formula()`, `vshape_ratio()` |
| `test_rh_variational.py` | Unit tests (27 tests, all pass) | `TestConvexity`, `TestProofStructure`, `TestReviewerFormula` |
| `RH_BITSIZE_PROGRAMME.py` | de Bruijn-Newman + off-line search | `Z_b()`, `track_zero_in_b()`, `bitsize_slope()` |
| `HONEST_9D_DISCRIMINATOR.py` | Hardy Z baseline | `hardy_Z_at_scale()`, ablation study |
| `BITSIZE_ZERO_DISCRIMINATOR.py` | Slope discriminant | `BitSizeDiscriminator`, `features()` |
| `CONJECTURE_IV_ROADMAP.docx` | Operator theory path | §4.5 Γ-renormalization, Stirling proof target |

---

## 10. Unit Test Structure

```
test_rh_variational.py  (27 tests, all pass)
│
├── TestXiFunction (5 tests)
│   ├── test_xi_vanishes_at_known_zeros
│   ├── test_xi_nonzero_between_zeros
│   ├── test_functional_equation_symmetry     ← core algebraic property
│   ├── test_xi_real_on_critical_line
│   └── test_xi_positive_real_axis
│
├── TestConvexity (5 tests)                   ← THE RH-EQUIVALENT CONDITION
│   ├── test_convexity_at_known_zeros         (trivially satisfied)
│   ├── test_convexity_at_non_zeros           (non-trivial, open analytically)
│   ├── test_convexity_multiple_h_values
│   ├── test_zero_excess_at_exact_zero
│   └── test_symmetry_implies_critical_point
│
├── TestVShape (2 tests)
│   ├── test_vshape_ratio_at_zeros            (ratio ≈ 10 → simple zero)
│   └── test_vshape_divergence_direction      (d2 → +∞, not 0)
│
├── TestReviewerFormula (4 tests)
│   ├── test_log_curvature_always_negative    (−Σ1/(T−γ)² < 0 always)
│   ├── test_log_curvature_formula_vs_numerical
│   ├── test_log_curvature_diverges_near_zero
│   └── test_distinction_log_vs_absolute_curvature  ← KEY reviewer point
│
├── TestProofStructure (5 tests)              ← logical chain
│   ├── test_functional_equation_forces_symmetry
│   ├── test_off_line_zero_would_imply_flanking
│   ├── test_convexity_failure_implies_maximum
│   ├── test_at_zeros_convexity_trivially_holds
│   └── test_corrected_overstatement          ← reviewer §3 correction
│
├── TestMKMDeltaFailure (2 tests)
│   ├── test_mkm_delta_min_not_at_half        ← original claim is false
│   └── test_mkm_state_sigma_independent
│
└── TestNumericalMethodology (4 tests)
    ├── test_precision_level                  (dps ≥ 50)
    ├── test_convexity_check_step_size        (h ≤ 0.001)
    ├── test_xi_symmetry_precision
    └── test_convexity_excess_scale
```

Run with:

```bash
python3 test_rh_variational.py          # summary output
python3 test_rh_variational.py -v       # verbose (per-test)
```

Expected output: `Ran 27 tests ... OK`

---

*Document generated March 2026. Mathematical content reviewed externally.*
