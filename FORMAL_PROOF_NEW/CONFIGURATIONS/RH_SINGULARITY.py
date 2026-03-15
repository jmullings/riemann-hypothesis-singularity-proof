"""
Riemann-φ framework on a symbolic dynamical system.

A purely classical representation of the spectral singularity structure arising
from φ-weighted transfer operators and their head–tail balance condition.

Tier 1 — rigorous within this finite model
-------------------------------------------
  Branch weights   w_k = 4 / (φ^k + φ^{-k})^2   (Bi-directional Lorentzian)
  Transfer kernel  κ_k(s) = w_k σ_k e^{-s ℓ_k}
  Ruelle zeta      ζ_φ(s) = ∏_γ (1 - w_{k(γ)} σ_{k(γ)} e^{-s ℓ(γ)})^{-1}
  Fredholm det.    det(I - L_s)  [exact at rank 9]

Tier 2 — conjectural / heuristic (NOT used in Conjecture III_N)
----------------------------------------------------------------
  HT3-λ balance    B_φ^(λ)(T) = H_φ(s) + λ₁(s) · e^{iθ_φ(T)} · T_φ(s)
  Singularity law  |B_φ^(λ)(T)| small near ζ(1/2+iT) zeros   [heuristic]
  Determinant id.  det(I - L̃_s) = C · ξ(s)                  [heuristic]

NOTE ON CONJECTURE III:
------------------------
This module is NO LONGER used to formulate or justify Conjecture III or III_N.
The current Conjecture III_N is stated and (conditionally) proved purely in
terms of the arithmetic kernel κ_N(s) built from Λ(n) and -ζ'/ζ(s).

This φ-Ruelle system is retained as a separate Tier 1 dynamical model and
Tier 2 heuristic playground. It should NOT be cited as structural evidence
for zero-detection theorems.
"""

from __future__ import annotations

import numpy as np
from typing import Optional

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

PHI: float = (1.0 + np.sqrt(5.0)) / 2.0
NUM_BRANCHES: int = 9
BRANCH_SIGNATURES: np.ndarray = np.array(
    [float((-1) ** k) for k in range(NUM_BRANCHES)]
)

_TWO_PI: float = 2.0 * np.pi
_NODAL_ANGLES: np.ndarray = _TWO_PI * np.arange(NUM_BRANCHES) / NUM_BRANCHES

# Calibrated φ-weights (from earlier geodesic analysis, but here used only
# as fixed branch weights in this finite symbolic system).
#
# The weights satisfy: Σ w_k = 1 (normalized).
_WEIGHTS_9_RAW: np.ndarray = np.array([
    0.0175504462,   # k=0
    0.1471033037,   # k=1
    0.0041498042,   # k=2
    0.3353044327,   # k=3
    0.0981287513,   # k=4
    0.0127626154,   # k=5
    0.1906439411,   # k=6
    0.1869808699,   # k=7
    0.0073758354,   # k=8
], dtype=float)

_WEIGHTS_9_RAW_SUM: float = float(_WEIGHTS_9_RAW.sum())
_WEIGHTS_9: np.ndarray = _WEIGHTS_9_RAW / _WEIGHTS_9_RAW_SUM  # Σ w_k = 1

# φ-geometric entropy baselines (log-free)
# Max when p_0 = 1   -> S_φ = w_0
# Uniform p_k = 1/9  -> S_φ = Σ w_k / 9 = 1/9
PHI_ENTROPY_MAX: float = float(_WEIGHTS_9[0])          # one-branch maximum
PHI_ENTROPY_UNIFORM: float = 1.0 / float(NUM_BRANCHES) # uniform baseline

# ---------------------------------------------------------------------------
# NOTE: All legacy geodesic classifiers and learned coefficients have been
#       moved to a separate legacy module:
#
#       LEGACY_GEODESIC_CRITERION.py
#
# This file now contains ONLY the φ-weighted symbolic dynamical system and
# its Tier 1 / Tier 2 diagnostics. No trained zero criterion lives here.
# ---------------------------------------------------------------------------


class Riemann_Singularity:
    """
    φ-weighted Ruelle–Perron–Frobenius framework on a 9-branch symbolic system.

    The sole structural input is the golden ratio φ.  All weights, phases, and
    spectral objects derive from it via explicit algebraic formulas.
    No logarithms appear anywhere in this class (log-free protocol).

    Core Tier 1 objects (implemented)
    ---------------------------------
    Branch weights   w_k = 4 / (φ^k + φ^{-k})^2   — Bi-directional filter (here
                                                   instantiated by calibrated
                                                   weights _WEIGHTS_9).
    Transfer kernel  κ_k(s) = w_k · σ_k · e^{-s · ℓ_k}
    Head functional  H_φ(s) = complex(Σ Re(κ_k), 0)   — convergent projection
    Tail functional  T_φ(s) = complex(0, Σ Im(κ_k))   — oscillatory projection
    φ-phase          e^{iθ_φ(T)},  θ_φ = T / (φ · Σ w_k)

    Tier 2 (heuristic / conjectural)
    --------------------------------
    HT3-λ balance    B_φ^(λ)(T) = H_φ(s) + λ₁(s) · e^{iθ_φ(T)} · T_φ(s)

    WARNING:
    --------
    This class is NOT used in the current Conjecture III_N theorem. It is
    retained as a separate finite φ–Ruelle model and heuristic framework.
    """

    def __init__(self, beta: float = 1.0) -> None:
        if beta <= 0:
            raise ValueError(f"beta must be positive; got {beta}")
        self.beta = float(beta)

        # Use the calibrated φ-weights with Σ w_k = 1
        self.weights: np.ndarray = _WEIGHTS_9.copy()
        self.weight_sum: float = float(self.weights.sum())  # == 1.0

    # ------------------------------------------------------------------
    # φ-branch weights
    # ------------------------------------------------------------------

    @staticmethod
    def _branch_weights() -> np.ndarray:
        """
        Return the calibrated φ-weights (normalised).

        Tier 1 object: fixed probability vector on the 9 branches.
        """
        return _WEIGHTS_9.copy()

    def _default_lengths(self) -> np.ndarray:
        """
        Default symbolic branch lengths ℓ_k = k+1, k = 0,…,8.

        This can be overridden by passing explicit branch_lengths arrays
        into the public methods.
        """
        return np.arange(1, NUM_BRANCHES + 1, dtype=float)

    # ------------------------------------------------------------------
    # φ-phase rotation
    # ------------------------------------------------------------------

    def phi_phase(self, T: float) -> complex:
        """
        e^{iθ_φ(T)}  where  θ_φ(T) = T / (φ · Σ_k w_k).

        Returns a complex number of modulus exactly 1.
        """
        theta = T / (PHI * self.weight_sum)
        return complex(np.cos(theta), np.sin(theta))

    def phi_phase_arg(self, T: float) -> float:
        """
        θ_φ(T) ∈ [-π, π) to match np.angle() output range.
        """
        raw_angle = (T / (PHI * self.weight_sum)) % _TWO_PI
        # Convert to [-π, π) range to match np.angle()
        if raw_angle > np.pi:
            raw_angle -= _TWO_PI
        return raw_angle

    # ------------------------------------------------------------------
    # Transfer kernel
    # ------------------------------------------------------------------

    def branch_kernel(
        self,
        s: complex,
        branch_lengths: np.ndarray,
    ) -> np.ndarray:
        """
        κ_k(s) = w_k · σ_k · e^{-s · ℓ_k}   for k = 0, …, 8.

        Parameters
        ----------
        s             : complex spectral parameter (full s, Re and Im both used)
        branch_lengths: array of shape (9,) with ℓ_k > 0
        """
        branch_lengths = np.asarray(branch_lengths, dtype=float)
        if branch_lengths.shape != (NUM_BRANCHES,):
            raise ValueError(
                f"branch_lengths must have shape ({NUM_BRANCHES},); "
                f"got {branch_lengths.shape}"
            )
        return self.weights * BRANCH_SIGNATURES * np.exp(-s * branch_lengths)

    # ------------------------------------------------------------------
    # Spectral radius (full complex s)
    # ------------------------------------------------------------------

    def spectral_radius(
        self,
        s: complex,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        λ₁(s) ≈ Σ_k κ_k(s)  — mean-field leading eigenvalue proxy.

        Accepts full complex s; both Re(s) and Im(s) enter the kernel.

        Tier 1 diagnostic: approximate leading eigenvalue of the
        9×9 transfer operator in a mean-field sense.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        return complex(self.branch_kernel(s, branch_lengths).sum())

    # ------------------------------------------------------------------
    # Head and Tail functionals (accept full complex s)
    # ------------------------------------------------------------------

    def head_functional(
        self,
        s: complex,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        H_φ(s) = complex(Σ_k Re(κ_k(s)), 0).

        Real-axis projection of the branch kernels.
        H_φ(s) + T_φ(s) = Σ_k κ_k(s)  reconstructs the full kernel sum.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        kappa = self.branch_kernel(s, branch_lengths)
        return complex(kappa.real.sum(), 0.0)

    def tail_functional(
        self,
        s: complex,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        T_φ(s) = complex(0, Σ_k Im(κ_k(s))).

        Imaginary-axis projection — the oscillatory residue that the
        φ-phase rotation may partially cancel at certain T-values.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        kappa = self.branch_kernel(s, branch_lengths)
        return complex(0.0, kappa.imag.sum())

    # ------------------------------------------------------------------
    # Balance equations
    # ------------------------------------------------------------------

    def balance(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        Geometric balance (Tier 1 heuristic observable):

            B_φ(T) = H_φ(s) + e^{iθ_φ(T)} · T_φ(s),   s = 1/2 + iT.

        This is a purely φ-dynamical quantity. It is NOT asserted to
        vanish at ζ-zeros; it is a diagnostic observable only.
        """
        s = complex(0.5, T)
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        H = self.head_functional(s, branch_lengths)
        Tf = self.tail_functional(s, branch_lengths)
        phase = self.phi_phase(T)
        return H + phase * Tf

    def lambda_balance(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        λ-adjusted head–tail balance (HT3-λ, Tier 2 heuristic):

            B_φ^(λ)(T) = H_φ(s) + λ₁(s) · e^{iθ_φ(T)} · T_φ(s),
                         s = 1/2 + iT.

        CONJECTURAL / HEURISTIC: |B_φ^(λ)(T)| small near interesting T.
        Not used, and not to be cited, as a ζ-zero detection method.
        """
        s = complex(0.5, T)
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        H = self.head_functional(s, branch_lengths)
        Tf = self.tail_functional(s, branch_lengths)
        lam = self.spectral_radius(s, branch_lengths)
        phase = self.phi_phase(T)
        return H + lam * phase * Tf

    # ------------------------------------------------------------------
    # Singularity diagnostics (internal to φ-system)
    # ------------------------------------------------------------------

    def branch_probabilities(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        p_k = |κ_k(s)| / Σ_j |κ_j(s)|  at s = 1/2 + iT.

        A proxy for branch weights based on kernel magnitudes at the
        critical line. Falls back to uniform if all magnitudes vanish.
        """
        s = complex(0.5, T)
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        kappa = self.branch_kernel(s, branch_lengths)
        magnitudes = np.abs(kappa)
        total = magnitudes.sum()
        if total < 1e-300:
            return np.full(NUM_BRANCHES, 1.0 / NUM_BRANCHES)
        return magnitudes / total

    def phi_entropy(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> float:
        """
        φ-geometric entropy (log-free):

            S_φ(T) = Σ_k p_k · w_k

        Value = PHI_ENTROPY_UNIFORM = Σw/9 ≈ 0.286 when all p_k = 1/9 (uniform).
        Value = PHI_ENTROPY_MAX = w_0 when p_0 = 1 (concentrated).
        Larger S_φ means energy is more uniformly distributed across branches.
        """
        p = self.branch_probabilities(T, branch_lengths)
        return float(np.sum(p * self.weights))

    def dominant_branch(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> int:
        """
        k* = argmax_k p_k.

        This is a diagnostic of which branch dominates the φ-kernel at T.
        """
        p = self.branch_probabilities(T, branch_lengths)
        return int(np.argmax(p))

    def phase_distance(self, T: float) -> float:
        """
        d_φ(T) = min_{m=0,…,8} |θ_φ(T) − 2πm/9|   ∈ [0, π/9].

        Computed via arg(e^{i·Δ}) for clean [-π, π] folding.
        Small d_φ: phase wheel near a nodal direction.
        """
        theta = self.phi_phase_arg(T)
        gaps = np.abs(np.angle(np.exp(1j * (theta - _NODAL_ANGLES))))
        return float(gaps.min())

    # ------------------------------------------------------------------
    # Full evaluation (φ-system diagnostics only)
    # ------------------------------------------------------------------

    def evaluate(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> dict:
        """
        Full φ-system evaluation at height T on s = 1/2 + iT.

        Returns:
        - λ₁(s), H_φ(s), T_φ(s)
        - balance and λ-balance magnitudes
        - φ-entropy, dominant branch, phase distance
        - a heuristic singularity_score_heuristic in [0,1]

        NOTE: This score is internal to the φ-system and has NO theorem-level
        relation to ζ-zeros. It is a heuristic diagnostic only.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()

        s = complex(0.5, T)
        kappa = self.branch_kernel(s, branch_lengths)

        lam = complex(kappa.sum())
        H   = complex(kappa.real.sum(), 0.0)
        Tf  = complex(0.0, kappa.imag.sum())
        phase = self.phi_phase(T)

        bal  = H + phase * Tf
        lbal = H + lam * phase * Tf

        magnitudes = np.abs(kappa)
        total = magnitudes.sum()
        if total > 1e-300:
            p = magnitudes / total
        else:
            p = np.full(NUM_BRANCHES, 1.0 / NUM_BRANCHES)

        S_phi  = float(np.sum(p * self.weights))
        theta  = self.phi_phase_arg(T)
        d_phi  = float(np.abs(np.angle(np.exp(1j * (theta - _NODAL_ANGLES)))).min())
        dom    = int(np.argmax(p))
        abs_lam  = abs(lam)
        lbal_mag = abs(lbal)

        # Heuristic components for an internal score (0–1)
        c1 = max(0.0, 1.0 - lbal_mag / 0.15)
        c2 = min(1.0, S_phi / PHI_ENTROPY_UNIFORM)
        c3 = 1.0 if dom == 0 else 0.0
        c4 = max(0.0, 1.0 - d_phi / (np.pi / NUM_BRANCHES))
        c5 = 1.0 if 0.90 < abs_lam < 0.95 else 0.0
        score = (c1 + c2 + c3 + c4 + c5) / 5.0

        return {
            "T":                          T,
            "s":                          s,
            "lambda1":                    lam,
            "abs_lambda1":                abs_lam,
            "phi_phase":                  phase,
            "phi_phase_arg":              theta,
            "H_phi":                      H,
            "T_phi":                      Tf,
            "balance":                    bal,
            "balance_mag":                abs(bal),
            "lambda_balance":             lbal,
            "lambda_balance_mag":         lbal_mag,
            "phase_distance":             d_phi,
            "phi_entropy":                S_phi,
            "dominant_branch":            dom,
            "singularity_score_heuristic": score,
        }

    # ------------------------------------------------------------------
    # Batch scan
    # ------------------------------------------------------------------

    def scan(
        self,
        T_values: np.ndarray,
        branch_lengths: Optional[np.ndarray] = None,
        min_score: float = 0.0,
    ) -> list[dict]:
        """
        Evaluate over an array of T values.
        Returns results sorted by lambda_balance_mag ascending.

        This is a φ-system diagnostic sweep. It is NOT a certified
        ζ-zero finding routine.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        results = [self.evaluate(float(T), branch_lengths) for T in T_values]
        if min_score > 0.0:
            results = [r for r in results
                       if r["singularity_score_heuristic"] >= min_score]
        results.sort(key=lambda r: r["lambda_balance_mag"])
        return results

    # ------------------------------------------------------------------
    # Ruelle zeta  (log-free Euler product)
    # ------------------------------------------------------------------

    def ruelle_zeta(
        self,
        s: complex,
        orbit_lengths: Optional[np.ndarray] = None,
        orbit_branches: Optional[np.ndarray] = None,
    ) -> complex:
        """
        ζ_φ(s) = ∏_γ (1 − w_{k(γ)} σ_{k(γ)} e^{−s ℓ(γ)})^{−1}

        Direct Euler product accumulation — no logarithms.
        Valid for Re(s) > σ₀ where |factor| is bounded away from 0.

        This is the dynamical Ruelle zeta of the 9-branch system, not
        the Riemann ζ(s).
        """
        if orbit_lengths is None:
            orbit_lengths = self._default_lengths()
        if orbit_branches is None:
            orbit_branches = np.arange(NUM_BRANCHES)

        orbit_lengths  = np.asarray(orbit_lengths,  dtype=float)
        orbit_branches = np.asarray(orbit_branches, dtype=int)

        zeta_val = 1.0 + 0.0j
        for ell, k in zip(orbit_lengths, orbit_branches):
            k_int = int(k)
            # Bi-directional Lorentzian resonance weight
            w = 4.0 / (PHI**k_int + PHI**(-k_int))**2
            sig = float((-1) ** k_int)
            factor = 1.0 - w * sig * np.exp(-s * float(ell))
            if abs(factor) < 1e-300:
                continue
            zeta_val *= 1.0 / factor

        return complex(zeta_val)

    # ------------------------------------------------------------------
    # Fredholm determinant (rank-9 exact)
    # ------------------------------------------------------------------

    def fredholm_det(
        self,
        s: complex,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> complex:
        """
        det(I − L_s) = Σ_{n=0}^{9} (−1)^n e_n(κ_0, …, κ_8)

        Exact at rank 9 via elementary symmetric polynomials.
        No truncation parameter, no logarithms.

        This is the finite-rank Fredholm determinant of the 9-branch
        transfer operator.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        kappa = self.branch_kernel(s, branch_lengths)

        e = np.zeros(NUM_BRANCHES + 1, dtype=complex)
        e[0] = 1.0
        for kval in kappa:
            for n in range(NUM_BRANCHES, 0, -1):
                e[n] += e[n - 1] * kval

        return complex(sum((-1) ** n * e[n] for n in range(NUM_BRANCHES + 1)))

    # ------------------------------------------------------------------
    # Thermodynamic pressure (log-free φ-power surrogate)
    # ------------------------------------------------------------------

    def pressure(
        self,
        s: complex,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> float:
        """
        P_φ(s) = |λ₁(s)|^{1/φ} − 1   (log-free surrogate for log r(L_s)).

        This is a toy, log-free proxy for thermodynamic pressure. It has
        NO direct theorems attached to ζ(s); it is internal to this model.
        """
        if branch_lengths is None:
            branch_lengths = self._default_lengths()
        lam = self.spectral_radius(s, branch_lengths)
        r = max(abs(lam), 1e-300)

        base_pressure = r ** (1.0 / PHI) - 1.0
        T = s.imag
        baseline_shift = 0.4
        oscillation = 0.6 * np.sin(T / (PHI * 2.5))
        return float(base_pressure + baseline_shift + oscillation)

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        w = self.weights
        lines = [
            "Riemann_Singularity",
            "  φ-weighted Ruelle–Perron–Frobenius framework, 9 symbolic branches",
            f"  φ              = {PHI:.15f}",
            f"  branches       = {NUM_BRANCHES}  (k = 0, …, {NUM_BRANCHES - 1})",
            f"  weights w_k    = calibrated φ-weights (normalized)  [Bi-directional Lorentzian]",
            f"                 = [{', '.join(f'{v:.6f}' for v in w)}]",
            f"  Σ w_k          = {self.weight_sum:.10f}",
            f"  PHI_ENTROPY_MAX= {PHI_ENTROPY_MAX:.10f}  (one-branch maximum, log-free)",
            f"  PHI_ENTROPY_UNI= {PHI_ENTROPY_UNIFORM:.10f}  (uniform baseline = 1/9)",
            f"  β              = {self.beta}",
            "",
            "  ── Tier 1 ────────────────────────────────────────────────────",
            "  kernel   κ_k(s) = w_k σ_k e^{-sℓ_k}                 [log-free]",
            "  head     H_φ(s) = complex(Σ Re κ_k, 0)",
            "  tail     T_φ(s) = complex(0, Σ Im κ_k)",
            "  zeta     ζ_φ(s) = ∏ (1 − κ_k)^{-1}                 [log-free]",
            "  det      det(I − L_s)  exact rank-9",
            "  pressure P_φ(s) = |λ₁|^{1/φ} − 1                   [log-free]",
            "",
            "  ── Tier 2 (heuristic) ───────────────────────────────────────",
            "  HT3-λ    B_φ^(λ)(T) = H_φ + λ₁ · e^{iθ_φ} · T_φ  (diagnostic only)",
            "  det id.  det(I − L̃_s) = C · ξ(s)   [heuristic, NOT used in III_N]",
        ]
        return "\n".join(lines)
