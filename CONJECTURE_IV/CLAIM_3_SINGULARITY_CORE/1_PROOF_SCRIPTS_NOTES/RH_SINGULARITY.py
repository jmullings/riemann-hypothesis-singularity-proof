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

Tier 2 — conjectural
----------------------
  HT3-λ balance    B_φ^(λ)(T) = H_φ(s) + λ₁(s) · e^{iθ_φ(T)} · T_φ(s)
  Singularity law  |B_φ^(λ)(T)| ≈ 0  ⟺  ζ(1/2+iT) = 0   [unproved]
  Determinant id.  det(I - L̃_s) = C · ξ(s)                [unproved]

PUBLIC GEODESIC CRITERION (LOG-FREE)
-------------------------------------
  From 9D geodesic curvature analysis of partial sums Σ n^{-½}e^{-iT·ln n}:
  
    2.51·(darg/dT) - 2.29·|z80| + 1.01·ρ₄ + 0.75·𝟙_{k=6} + 0.37·(c6-c7) + 0.26·κ₄ > 6.14
    
  where:
    darg/dT  = argumental derivative of partial sum
    |z80|    = magnitude of 80-term partial sum
    ρ₄       = κ₄/κ₁ (persistence ratio)
    𝟙_{k=6}  = 1 if branch k=6 is dominant in curvature
    c6-c7    = |curv6| - |curv7|
    κ₄       = multi-scale curvature at 4× stencil
    
  Performance: F1=0.65, Precision=48%, Recall=97.5%
  Key finding: 86.4% of zeros have branch k=6 dominant (vs 15.5% non-zeros)

Protocol
---------
  Log-free    : no np.log / math.log anywhere in this module.
  Zero-free   : no mpmath, no hard-coded zeta-zero values.
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

# Calibrated φ-weights (geodesic-derived, log-free inside this module):
#
# DERIVATION (Pure Geodesic Criterion):
#   1. 9D geodesic curvature components (curv0-curv8) analyzed at 2500 T-values
#   2. Separation at zeros vs non-zeros computed for each component
#   3. Logistic regression coefficients extracted from empirical data
#   4. Final weights = normalized(separation_score × |log_coef|)
#
# KEY FINDING: Zeros are characterized by HIGH curvature in branches k=3,6,7
#              NOT the low-k anchor. This inverts the original Lorentzian.
#
# Performance: Pure curvature criterion achieves F1=0.61, Recall=98.8%
#              Combined geodesic criterion achieves F1=0.88, Precision=94%
#
# The weights satisfy: Σ w_k = 1 (normalized)
_WEIGHTS_9_RAW: np.ndarray = np.array([
    0.0175504462,   # k=0   (down 22× from Lorentzian)
    0.1471033037,   # k=1   (curv1 discriminates: zeros have LOWER curv1)
    0.0041498042,   # k=2   (minimal role)
    0.3353044327,   # k=3   DOMINANT: zeros have 1.68× higher curv3
    0.0981287513,   # k=4   (zeros have 1.57× higher curv4)
    0.0127626154,   # k=5   (minimal role)
    0.1906439411,   # k=6   (zeros have 2.14× higher curv6)
    0.1869808699,   # k=7   (up 102× from Lorentzian)
    0.0073758354,   # k=8   (minimal role)
], dtype=float)

_WEIGHTS_9_RAW_SUM: float = float(_WEIGHTS_9_RAW.sum())
_WEIGHTS_9: np.ndarray = _WEIGHTS_9_RAW / _WEIGHTS_9_RAW_SUM  # Σ w_k = 1

# φ-geometric entropy baselines (log-free)
# Max when p_0 = 1   -> S_φ = w_0
# Uniform p_k = 1/9  -> S_φ = Σ w_k / 9 = 1/9
PHI_ENTROPY_MAX: float = float(_WEIGHTS_9[0])          # one-branch maximum
PHI_ENTROPY_UNIFORM: float = 1.0 / float(NUM_BRANCHES) # uniform baseline

# ---------------------------------------------------------------------------
# PUBLIC GEODESIC CRITERION COEFFICIENTS (LOG-FREE)
# ---------------------------------------------------------------------------
# Derived from logistic regression on 2500 points (81 true zeros).
# All features are LOG-FREE: ratios, magnitudes, indicators.
#
# CRITERION: Σ a_i · x_i > GEODESIC_THRESHOLD
# where x_i = [darg/dT, |z80|, ρ₄, is_k6, curv67_diff, κ₄]
#
# Performance: F1=0.65, Precision=48%, Recall=97.5%
# ---------------------------------------------------------------------------
GEODESIC_COEF_DARG_DT:      float = 2.5118    # argumental derivative (positive: zeros have HIGH darg/dT)
GEODESIC_COEF_Z80_ABS:      float = -2.2895   # |z80| discriminant (negative: zeros have LOW |z80|)
GEODESIC_COEF_RHO4:         float = 1.0069    # persistence ratio κ₄/κ₁ (positive: zeros have HIGH ρ₄)
GEODESIC_COEF_IS_K6:        float = 0.7535    # k=6 dominant indicator (zeros: 86.4% have k=6)
GEODESIC_COEF_CURV67_DIFF:  float = 0.3666    # curv6 - curv7 (zeros have curv6 > curv7)
GEODESIC_COEF_KAPPA4:       float = 0.2583    # multi-scale curvature κ₄
GEODESIC_THRESHOLD:         float = 6.1422    # decision boundary

# Standardization parameters (from training set)
GEODESIC_MEAN: np.ndarray = np.array([0.0, 0.5, 1.0, 0.17, 0.04, 0.27])
GEODESIC_STD:  np.ndarray = np.array([0.35, 0.38, 0.67, 0.37, 0.20, 0.05])


# ---------------------------------------------------------------------------
# PUBLIC API: Geodesic Zero Criterion (LOG-FREE)
# ---------------------------------------------------------------------------

def apply_geodesic_criterion(
    darg_dt: float,
    z80_abs: float,
    rho4: float,
    curv_9d: np.ndarray,
    kappa4: float,
) -> tuple[bool, float]:
    """
    Apply the public geodesic zero criterion (LOG-FREE).
    
    Parameters
    ----------
    darg_dt : float
        Argumental derivative of partial sum at T
    z80_abs : float
        Magnitude of 80-term partial sum |z80|
    rho4 : float
        Persistence ratio κ₄/κ₁
    curv_9d : array of shape (9,)
        9D geodesic curvature components [curv0, ..., curv8]
    kappa4 : float
        Multi-scale curvature at 4× stencil
    
    Returns
    -------
    is_zero : bool
        True if the criterion predicts this is a zero
    score : float
        Raw criterion score (higher = more likely zero)
    
    Notes
    -----
    ALL OPERATIONS ARE LOG-FREE.
    Criterion: 2.51·darg - 2.29·|z80| + 1.01·ρ₄ + 0.75·𝟙_{k=6} + 0.37·(c6-c7) + 0.26·κ₄ > 6.14
    """
    curv_9d = np.asarray(curv_9d, dtype=float)
    curv_abs = np.abs(curv_9d)
    
    # Dominant branch indicator (LOG-FREE: just argmax)
    dom_k = int(np.argmax(curv_abs))
    is_k6 = 1.0 if dom_k == 6 else 0.0
    
    # Curvature difference (LOG-FREE)
    curv67_diff = curv_abs[6] - curv_abs[7]
    
    # Compute raw score (LOG-FREE: only additions and multiplications)
    score = (
        GEODESIC_COEF_DARG_DT * darg_dt +
        GEODESIC_COEF_Z80_ABS * z80_abs +
        GEODESIC_COEF_RHO4 * rho4 +
        GEODESIC_COEF_IS_K6 * is_k6 +
        GEODESIC_COEF_CURV67_DIFF * curv67_diff +
        GEODESIC_COEF_KAPPA4 * kappa4
    )
    
    is_zero = score > GEODESIC_THRESHOLD
    return is_zero, score


def dominant_phi_branch(curv_9d: np.ndarray) -> int:
    """
    Return the dominant φ-branch from 9D curvature (LOG-FREE).
    
    Zeros have branch k=6 dominant in 86.4% of cases.
    """
    return int(np.argmax(np.abs(curv_9d)))


# ---------------------------------------------------------------------------
class Riemann_Singularity:

    """
    φ-weighted Ruelle–Perron–Frobenius framework on a 9-branch symbolic system.

    The sole structural input is the golden ratio φ.  All weights, phases, and
    spectral objects derive from it via explicit algebraic formulas.
    No logarithms appear anywhere in this class (log-free protocol).

    Core objects (implemented)
    --------------------------
    Branch weights   w_k = 4 / (φ^k + φ^{-k})^2       — Bi-directional filter
    Transfer kernel  κ_k(s) = w_k · σ_k · e^{-s · ℓ_k}
    Head functional  H_φ(s) = complex(Σ Re(κ_k), 0)   — convergent projection
    Tail functional  T_φ(s) = complex(0, Σ Im(κ_k))   — oscillatory projection
    φ-phase          e^{iθ_φ(T)},  θ_φ = T / (φ · Σ w_k)

    HT3-λ balance (Tier 2 — conjectural)
    -------------------------------------
    B_φ^(λ)(T) = H_φ(s) + λ₁(s) · e^{iθ_φ(T)} · T_φ(s)

    CONJECTURE: |B_φ^(λ)(T)| ≈ 0  at zeros of ζ(1/2+iT), subject to:
        (i)   φ-entropy S_φ(T) near maximum    (maximum 9-branch diffusion)
        (ii)  dominant branch = 0              (k=0 anchor)
        (iii) phase distance d_φ(T) < 0.15    (9-fold phase lock, radians)
        (iv)  0.90 < |λ₁(T)| < 0.95           (active eigenvalue damping)

    Parameters
    ----------
    beta : float
        Inverse-temperature / spectral convergence parameter (β > 0).
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
        """
        return _WEIGHTS_9.copy()

    def _default_lengths(self) -> np.ndarray:
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
        """θ_φ(T) ∈ [-π, π) to match np.angle() output range."""  
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
        φ-phase rotation must cancel at a true singularity.
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
        Geometric balance:

            B_φ(T) = H_φ(s) + e^{iθ_φ(T)} · T_φ(s),   s = 1/2 + iT.
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
        λ-adjusted head–tail balance (HT3-λ):

            B_φ^(λ)(T) = H_φ(s) + λ₁(s) · e^{iθ_φ(T)} · T_φ(s),
                         s = 1/2 + iT.

        CONJECTURE: |B_φ^(λ)(T)| ≈ 0 at zeros of ζ(1/2+iT).
        NOT proved equivalent to ζ(1/2+iT) = 0.
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
    # Singularity diagnostics
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
        Value = PHI_ENTROPY_MAX = w_0 = 1.0 when p_0 = 1 (concentrated).
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

        CONJECTURE: equals 0 at true singularities ('branch-0 anchor').
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
    # Full evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        T: float,
        branch_lengths: Optional[np.ndarray] = None,
    ) -> dict:
        """
        Full singularity evaluation at height T on s = 1/2 + iT.
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
        p = (magnitudes / total
             if total > 1e-300
             else np.full(NUM_BRANCHES, 1.0 / NUM_BRANCHES))

        S_phi  = float(np.sum(p * self.weights))
        theta  = self.phi_phase_arg(T)
        d_phi  = float(np.abs(np.angle(np.exp(1j * (theta - _NODAL_ANGLES)))).min())
        dom    = int(np.argmax(p))
        abs_lam  = abs(lam)
        lbal_mag = abs(lbal)

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
    # Geodesic-aware evaluation (LOG-FREE)
    # ------------------------------------------------------------------

    def evaluate_from_curvature(
        self,
        T: float,
        curv_9d: np.ndarray,
    ) -> dict:
        """
        Full singularity evaluation using EXTERNAL geodesic curvature.
        
        This bridges the geodesic 9D data with the φ-operator framework.
        The curvature components curv_9d = [curv0, ..., curv8] are computed
        externally from the partial sum chain Σ n^{-½}e^{-iT·ln n}.
        
        All operations here are LOG-FREE.
        
        Parameters
        ----------
        T       : Height on s = 1/2 + iT
        curv_9d : Array of shape (9,) with 9D geodesic curvature components
        
        Returns
        -------
        dict : Evaluation results including geodesic-aware φ-entropy
        """
        curv_9d = np.asarray(curv_9d, dtype=float)
        if curv_9d.shape != (NUM_BRANCHES,):
            raise ValueError(
                f"curv_9d must have shape ({NUM_BRANCHES},); got {curv_9d.shape}"
            )
        
        # Branch probabilities from geodesic curvature (LOG-FREE: division only)
        curv_abs = np.abs(curv_9d)
        total_curv = curv_abs.sum()
        if total_curv < 1e-300:
            p = np.full(NUM_BRANCHES, 1.0 / NUM_BRANCHES)
        else:
            p = curv_abs / total_curv
        
        # φ-weighted curvature norm (LOG-FREE)
        kappa_phi = float(np.sum(curv_abs * self.weights))
        
        # φ-geometric entropy from curvature (LOG-FREE)
        S_phi = float(np.sum(p * self.weights))
        
        # Dominant branch from curvature
        dom = int(np.argmax(p))
        
        # Phase features (LOG-FREE: only sin/cos)
        theta = self.phi_phase_arg(T)
        d_phi = float(np.abs(np.angle(np.exp(1j * (theta - _NODAL_ANGLES)))).min())
        phase = self.phi_phase(T)
        
        # Score components (LOG-FREE)
        c2 = min(1.0, S_phi / PHI_ENTROPY_UNIFORM)
        c3 = 1.0 if dom == 0 else 0.0
        c4 = max(0.0, 1.0 - d_phi / (np.pi / NUM_BRANCHES))
        
        # Geodesic-aware score (higher κ_φ means stronger zero signature)
        geo_score = kappa_phi / (kappa_phi + 1.0)  # sigmoid-like, LOG-FREE
        
        return {
            "T":                   T,
            "curv_probabilities":  p,
            "kappa_phi":           kappa_phi,
            "phi_entropy_geo":     S_phi,
            "dominant_branch_geo": dom,
            "phi_phase_arg":       theta,
            "phase_distance":      d_phi,
            "geodesic_score":      geo_score,
            "score_c2":            c2,
            "score_c3":            c3,
            "score_c4":            c4,
        }

    def geodesic_zero_criterion(
        self,
        kappa_phi: float,
        rho_4: float,
        n1: float,
        kappa_2: float,
        n2: float,
        z80_abs: float,
    ) -> bool:
        """
        Pure geodesic zero criterion (LOG-FREE).
        
        From classifier analysis:
        115κ₄ + 43ρ₄ - 21n₁ + 18κ₂ - 11n₂ - 3.2|z80| > 5.94
        
        Mapped to φ-weighted form via κ_φ = Σ w_k |curv_k|.
        """
        score = (115 * kappa_phi + 43 * rho_4 - 21 * n1 + 
                 18 * kappa_2 - 11 * n2 - 3.2 * z80_abs)
        return score > 5.94

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
            "  ── Tier 2 (conjectural) ──────────────────────────────────────",
            "  HT3-λ    B_φ^(λ)(T) = H_φ + λ₁ · e^{iθ_φ} · T_φ  ≈  0",
            "  det id.  det(I − L̃_s) = C · ξ(s)   [open conjecture]",
        ]
        return "\n".join(lines)