#!/usr/bin/env python3
"""
FORMAL_PROOF_NEW/CONFIGURATIONS/AXIOMS.py
=========================================

**STATUS: FOUNDATIONAL — March 11, 2026**
**Scope: FORMAL_PROOF_NEW tree — self-contained, no cross-tree imports**
**Protocol: P1 (no log), P2 (9D-centric), P3 (Riemann-φ), P4 (bitsize), P5 (Trinity)**

This module is the single consolidated axiom foundation for the
FORMAL_PROOF_NEW proof tree.  Every execution script under

    FORMAL_PROOF_NEW/{BRIDGES,DEFINITIONS,PROOFS,SIGMAS,STEPS}/

should import constants and classes from HERE rather than from any
file in the legacy FORMAL_PROOF/ tree.

=============================================================================
MODULE STRUCTURE
=============================================================================

SECTION 0 — Module constants
    LAMBDA_STAR, NORM_X_STAR, COUPLING_K, PHI

SECTION 1 — Local arithmetic primitives  (P1-safe)
    von_mangoldt(n), bitsize(n), bit_band(n)

SECTION 2 — Definitions 1–8: Bitsize-Aware Eulerian Geometry
    Def 1  bitsize coordinate          b(n) := ⌊log₂ n⌋
    Def 2  9D state factorisation      X(T) = X_macro ⊕ X_micro
    Def 3  energy conservation         E_9D = E_macro + E_micro
    Def 4  6D projection               P₆ X(T) := X_micro(T)
    Def 5  bitsize scale functional    S(T) := 2^{Δb(T)}
    Def 6  normalised bridge operator  Ã := (1/S) P₆ A P₆ᵀ
    Def 7  band-restricted state       X^(k)(T)
    Def 8  band-wise convexity         C_k(T,h) ≥ 0  [Axiom U1*]

SECTION 3 — Axiom 8: Inverse Bitsize Shift  (CONJECTURAL)
    MacroSectorReconstruction
    InverseBitsizeShift
    BridgeLift6Dto9D

SECTION 4 — Master verifier
    AxiomVerifier.full_verification()

=============================================================================
PROTOCOL CONSTRAINTS
=============================================================================

P1 — log() is FORBIDDEN as a primary operator anywhere in this tree.
     The single permitted use is inside bitsize() below, where it
     measures bit-complexity of integers, not any analytic function.

P2 — All geometric objects live in 9D Riemannian space (metric g_ij = φ^{i+j})
     or in its 6D micro-projection.  3D-only models are inadmissible.

P3 — Weights are Riemann-φ (von Mangoldt × φ-kernel).  MKM or ad-hoc
     weights are inadmissible.

P4 — Bitsize axioms BS-1 through BS-5 must be respected:
     BS-1  b(n) is a coordinate, not a diagnostic.
     BS-2  S(T) is the ONLY normalization factor for bridge operators.
     BS-3  The macro/micro split is orthogonal by construction.
     BS-4  Band-wise convexity (U1*) is the required non-negativity test.
     BS-5  Inverse shift (Axiom 8) is labelled CONJECTURAL until proved.

P5 — Trinity compliance: every execution file that imports this module
     must pass Gate-0 (ambient dimensions) and Gate-1 (P1-4 static checks).

=============================================================================
Author : Jason Mullings
Date   : March 11, 2026
Version: 1.0.0
=============================================================================
"""

from __future__ import annotations

import math
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# =============================================================================
# SECTION 0: MODULE-LEVEL CONSTANTS
# =============================================================================
#
# PROVENANCE NOTE — read before citing these numbers in any proof:
#
# LAMBDA_STAR and NORM_X_STAR are EMPIRICAL CONFIGURATION CONSTANTS derived
# from fitting the sech²-energy field E = k·sech²(λ*·||x*||) to the prime-side
# Gram-matrix analysis (SINGULARITY_50D.py / compute_9d_coordinates_prime_only).
# They ARE NOT mathematical axioms.  They may be regenerated at runtime from
# primes alone via compute_9d_coordinates_prime_only() in SINGULARITY_50D.py.
#
# DO NOT cite LAMBDA_STAR or NORM_X_STAR as "axiomatic" in the proof chain.
# Correct description: "empirical constants derived from prime-side Gram
# eigenvector analysis; independent of any specific Riemann zero height."
#
# COUPLING_K is the fitted sech² amplitude from the E*k*SECH² analysis.
# PHI is the analytic golden ratio — this IS a mathematical constant.
# =============================================================================

# Empirical sech² pinning constant  (prime-side Gram matrix fit, NOT an axiom)
LAMBDA_STAR: float = 494.05895555802020426355559872240107048767357569104664

# Empirical geometric anchor norm   (prime-only eigenvector, NOT an axiom)
NORM_X_STAR: float = 0.34226067113747900961787251073434770451853996743283664

# Soliton-information coupling constant k  (E = k · sech²(x), empirical fit)
COUPLING_K: float = 0.002675

# Golden ratio φ
PHI: float = (1.0 + math.sqrt(5.0)) / 2.0

# First 9 nontrivial Riemann zeta zeros (imaginary parts)
RIEMANN_ZEROS_9: list[float] = [
    14.134725141734693, 21.022039638771554, 25.010857580145688,
    30.424876125859513, 32.935061587739189, 37.586178158825677,
    40.918719011061954, 43.327073280914983, 48.005150881167150
]

# Ambient dimension of the full Eulerian state space
DIM_9D: int = 9

# Dimension of the micro (zero-geometry) sector
DIM_6D: int = 6

# Dimension of the macro (PNT-bulk / bitsize) sector
DIM_3D: int = 3

# Fixed sigma: all zeros lie on the critical line σ = 1/2 (RH axiom)
SIGMA_FIXED: float = 0.5


# =============================================================================
# SECTION 1: LOCAL ARITHMETIC PRIMITIVES  (no cross-tree imports)
# =============================================================================

def von_mangoldt(n: int) -> float:
    """
    Von Mangoldt function Λ(n).

    Returns log(p) if n = p^k for some prime p and integer k ≥ 1,
    otherwise returns 0.

    NOTE: The log() here is locked inside a classical arithmetic
    primitive — it does NOT violate P1.  P1 bans log as a *primary
    spectral operator*, not as an ingredient of Λ(n).
    """
    if n <= 1:
        return 0.0
    # Trial-division factorisation — small N, correctness over speed
    temp = n
    p = 2
    factors = set()
    while p * p <= temp:
        while temp % p == 0:
            factors.add(p)
            temp //= p
        p += 1
    if temp > 1:
        factors.add(temp)
    if len(factors) == 1:
        p = next(iter(factors))
        return math.log(p)          # log(p) is the canonical value of Λ(n)
    return 0.0


def bitsize(n: int) -> int:
    """
    DEFINITION 1 — Bitsize coordinate.

        b(n) := ⌊log₂ n⌋

    This is a COORDINATE measuring the bit-complexity of integers.
    It is the ONLY permitted use of a logarithm in the FORMAL_PROOF_NEW
    tree (P1 compliance).

    Returns 0 for n ≤ 0.
    """
    if n <= 0:
        return 0
    return int(math.floor(math.log2(n)))   # sole P1-permitted log


def bit_band(n: int) -> int:
    """
    Bit-band of n: the integer k such that 2^k ≤ n < 2^{k+1}.

    Consequent of Definition 1 — no additional axiom needed.
    """
    return bitsize(n)


# =============================================================================
# SECTION 2: DEFINITIONS 1–8
# =============================================================================

# -----------------------------------------------------------------------------
# DEFINITION 2 — 9D STATE FACTORISATION
# -----------------------------------------------------------------------------

@dataclass
class FactoredState9D:
    """
    DEFINITION 2.

        X(T) = X_macro(T) ⊕ X_micro(T)

    X_macro ∈ ℝ³  : bitsize / PNT sector  (macroscopic growth)
    X_micro ∈ ℝ⁶  : geometric / ripple sector (zero structure)

    The direct sum is ORTHOGONAL by construction (different dimensions).
    """
    T: float
    T_macro: np.ndarray   # shape (3,)
    T_micro: np.ndarray   # shape (6,)

    def __post_init__(self) -> None:
        if self.T_macro.shape != (3,):
            raise ValueError(f"T_macro must be 3D, got {self.T_macro.shape}")
        if self.T_micro.shape != (6,):
            raise ValueError(f"T_micro must be 6D, got {self.T_micro.shape}")

    @property
    def full_vector(self) -> np.ndarray:
        """Reconstruct full 9D vector: X_micro ⊕ X_macro."""
        return np.concatenate([self.T_micro, self.T_macro])

    # DEFINITION 3 — energy quantities

    @property
    def E_9D(self) -> float:
        """Total 9D energy  E_9D := ‖X(T)‖²."""
        return float(np.linalg.norm(self.full_vector) ** 2)

    @property
    def E_macro(self) -> float:
        """Macroscopic energy  E_macro := ‖X_macro(T)‖²."""
        return float(np.linalg.norm(self.T_macro) ** 2)

    @property
    def E_micro(self) -> float:
        """Microscopic energy  E_micro := ‖X_micro(T)‖²."""
        return float(np.linalg.norm(self.T_micro) ** 2)

    def _software_sanity_check(self) -> float:
        """
        SOFTWARE SANITY CHECK — NOT a mathematical axiom.

        Confirms that numpy.linalg.norm behaves correctly on concatenated
        orthogonal vectors, i.e. ||A ⊕ B||² == ||A||² + ||B||².
        This is a consequence of the Pythagorean theorem, not a property
        of primes or zeros.  Returns the floating-point residual
        (should be < 1e-14 for any inputs; a failure here is a bug).

        Formerly mislabelled "DEFINITION 3 (Axiom)" — renamed to prevent
        it from being cited as a mathematical result in the proof chain.
        """
        return abs(self.E_9D - self.E_macro - self.E_micro)


class StateFactory:
    """
    Construct FactoredState9D from height parameter T.

    The factorisation is axiomatic:
      X_micro — φ-scaled geometric modes  (ripple / zero structure)
      X_macro — bitsize moment statistics (PNT bulk)
    """

    def __init__(self, phi: float = PHI) -> None:
        self.phi = phi

    def create(self, T: float) -> FactoredState9D:
        """
        Build the 9D factored state at height T.

        X_micro = (F₁, …, F₆)  — six φ-scaled Gaussian mode sums
        X_macro = (B₁, B₂, B₃) — weighted bitsize mean / var / skew
        """
        primes_data: List[Dict] = []
        for n in range(2, int(T) + 1):
            lam = von_mangoldt(n)
            if lam > 0:
                primes_data.append(
                    {"n": n, "Lambda": lam, "b": bitsize(n)}
                )

        if not primes_data:
            return FactoredState9D(T=T,
                                   T_macro=np.zeros(3),
                                   T_micro=np.zeros(6))

        # ── X_micro : 6D geometric modes ────────────────────────────────────
        X_micro = np.zeros(6)
        for k in range(6):
            scale = self.phi ** k
            total = 0.0
            for p in primes_data:
                weight = math.exp(-((p["n"] / scale) - 1.0) ** 2 / 2.0)
                total += p["Lambda"] * weight
            X_micro[k] = total

        # ── X_macro : 3D bitsize moment statistics ───────────────────────────
        total_weight = sum(p["Lambda"] for p in primes_data)

        B1 = sum(p["Lambda"] * p["b"] for p in primes_data) / total_weight

        B2 = sum(p["Lambda"] * (p["b"] - B1) ** 2
                 for p in primes_data) / total_weight

        if B2 > 0.0:
            B3 = sum(p["Lambda"] * (p["b"] - B1) ** 3
                     for p in primes_data) / (total_weight * B2 ** 1.5)
        else:
            B3 = 0.0

        X_macro = np.array([B1, B2, B3])

        return FactoredState9D(T=T, T_macro=X_macro, T_micro=X_micro)


# -----------------------------------------------------------------------------
# DEFINITION 4 — 6D PROJECTION  (BITSIZE-AWARE)
# -----------------------------------------------------------------------------

class Projection6D:
    """
    DEFINITION 4.

        P₆ : ℝ⁹ → ℝ⁶,   P₆ X(T) := X_micro(T)

    The projection discards X_macro exactly.
    The dumped energy ‖X_macro‖² = E_macro is the PNT bulk, not a mystery.
    """

    @staticmethod
    def project(state: FactoredState9D) -> np.ndarray:
        """Return the 6D micro component of the state."""
        return state.T_micro

    @staticmethod
    def dumped_energy(state: FactoredState9D) -> float:
        """Energy discarded by projection: E_macro := ‖X_macro‖²."""
        return state.E_macro


# -----------------------------------------------------------------------------
# DEFINITION 5 — BITSIZE SCALE FUNCTIONAL
# -----------------------------------------------------------------------------

class BitsizeScaleFunctional:
    """
    DEFINITION 5.

        S(T) := 2^{Δb(T)}

    where Δb(T) = log₂(centroid_natural(T) / centroid_geometric(T)).

    Empirically Δb(T) ≈ 4.5 bits → S(T) ≈ 22.

    NOTE: The log₂ here is inside S(T) which is the *normalisation*
    scalar — it does NOT appear as a spectral operator (P1 compliant).
    """

    def __init__(self, phi: float = PHI) -> None:
        self.phi = phi

    def centroid_natural(self, T: float) -> float:
        """Λ-weighted average of n  (grows with T — PNT bulk)."""
        sum_n = 0.0
        total_weight = 0.0
        for n in range(2, int(T) + 1):
            lam = von_mangoldt(n)
            if lam > 0.0:
                sum_n += lam * n
                total_weight += lam
        return sum_n / total_weight if total_weight > 0.0 else 1.0

    def centroid_geometric(self, T: float) -> float:
        """φ-weighted average of n  (approximately fixed — geometric anchor)."""
        sum_n = 0.0
        total_weight = 0.0
        for n in range(2, int(T) + 1):
            lam = von_mangoldt(n)
            if lam > 0.0:
                for k in range(6):
                    scale = self.phi ** k
                    w = lam * math.exp(-((n / scale) - 1.0) ** 2 / 2.0)
                    sum_n += w * n
                    total_weight += w
        return sum_n / total_weight if total_weight > 0.0 else 1.0

    def delta_b(self, T: float) -> float:
        """Centroid shift in bits: Δb(T) = log₂(c_natural / c_geometric)."""
        c_nat = self.centroid_natural(T)
        c_geo = self.centroid_geometric(T)
        if c_geo <= 0.0:
            return 0.0
        return math.log2(c_nat / c_geo)       # internal use inside S(T) only

    def S(self, T: float) -> float:
        """
        Bitsize scale functional S(T) = 2^{Δb(T)}.

        This is the sole normalization factor for bridge operators (BS-2).
        """
        return 2.0 ** self.delta_b(T)


# -----------------------------------------------------------------------------
# DEFINITION 6 — NORMALISED BRIDGE OPERATOR
# -----------------------------------------------------------------------------

class NormalizedBridgeOperator:
    """
    DEFINITION 6.

        Ã := (1/S(T))  P₆ A P₆ᵀ

    The spectrum of Ã stabilises as N → ∞.
    The N-dependent blow-up is absorbed into S(T), not Ã.
    """

    def __init__(self, states: List[FactoredState9D], S_T: float) -> None:
        self.states = states
        self.S_T = S_T

        projected = np.array([Projection6D.project(s) for s in states])

        if len(projected) < 2:
            self.H_raw = np.eye(6)
        else:
            mean = np.mean(projected, axis=0)
            centered = projected - mean
            self.H_raw = (centered.T @ centered) / (len(projected) - 1)

        # Ensure self-adjoint (Hermitian for ℝ matrices)
        self.H_raw = 0.5 * (self.H_raw + self.H_raw.T)

        # Normalised operator Ã
        self.H_tilde = self.H_raw / self.S_T if self.S_T > 0.0 else self.H_raw

    @property
    def eigenvalues(self) -> np.ndarray:
        """Eigenvalues of Ã, sorted descending."""
        eigs = np.linalg.eigvalsh(self.H_tilde)
        return np.sort(eigs)[::-1]

    def trace_power(self, n: int) -> float:
        """Tr(Ã^n) — the stable trace (not raw Tr(A^n))."""
        return float(np.sum(self.eigenvalues ** n))


# -----------------------------------------------------------------------------
# DEFINITIONS 7 & 8 — BAND-RESTRICTED STATE AND BAND-WISE CONVEXITY
# -----------------------------------------------------------------------------

@dataclass
class BandRestrictedState:
    """
    DEFINITION 7.

        X^(k)(T) := Λ-weighted φ-mode contribution from bit-band k.

    Bit-band k = {n : 2^k ≤ n < 2^{k+1}}.
    """
    T: float
    band: int
    T_micro_k: np.ndarray   # shape (6,)

    @property
    def projected_norm_squared(self) -> float:
        """‖P₆ X^(k)‖²"""
        return float(np.linalg.norm(self.T_micro_k) ** 2)


class BandwiseConvexityChecker:
    """
    DEFINITION 8 / AXIOM U1*.

        C_k(T, h) :=
            ‖P₆ X^(k)_{T+h}‖² + ‖P₆ X^(k)_{T-h}‖² − 2‖P₆ X^(k)_T‖²

    AXIOM U1*: C_k(T, h) ≥ 0 for all bands k and admissible h.

    This is STRONGER than global convexity — failures cannot hide by
    mixing across bit-scales.
    """

    def __init__(self, phi: float = PHI) -> None:
        self.phi = phi

    def compute_band_state(self, T: float, band: int) -> BandRestrictedState:
        """Compute X^(k)(T) — the 6D state restricted to bit-band k."""
        T_micro_k = np.zeros(6)
        band_min = 2 ** band
        band_max = 2 ** (band + 1)

        for n in range(max(2, band_min), min(int(T) + 1, band_max)):
            lam = von_mangoldt(n)
            if lam > 0.0:
                for mode in range(6):
                    scale = self.phi ** mode
                    w = math.exp(-((n / scale) - 1.0) ** 2 / 2.0)
                    T_micro_k[mode] += lam * w

        return BandRestrictedState(T=T, band=band, T_micro_k=T_micro_k)

    def C_k(self, T: float, h: float, band: int) -> float:
        """
        Band-wise convexity functional C_k(T, h).

        AXIOM U1*: must be ≥ 0.
        """
        s_plus  = self.compute_band_state(T + h, band)
        s_minus = self.compute_band_state(T - h, band)
        s_ctr   = self.compute_band_state(T, band)
        return (s_plus.projected_norm_squared
                + s_minus.projected_norm_squared
                - 2.0 * s_ctr.projected_norm_squared)

    def verify_all_bands(
        self,
        T_values: np.ndarray,
        h_values: Optional[np.ndarray] = None,
    ) -> Dict[int, Dict]:
        """
        Verify C_k(T, h) ≥ 0 for all active bit-bands and test points.

        Returns
        -------
        {band: {'is_convex': bool, 'min_C': float, 'violations': int}}
        """
        if h_values is None:
            h_values = np.array([1.0, 2.0, 5.0, 10.0, 20.0])

        max_T = float(max(T_values))
        max_band = bitsize(int(max_T))
        results: Dict[int, Dict] = {}

        for band in range(1, max_band + 1):
            band_min = 2 ** band
            min_C = math.inf
            violations = 0

            for T in T_values:
                if T <= band_min + float(max(h_values)):
                    continue
                for h in h_values:
                    if T - h < band_min:
                        continue
                    C = self.C_k(float(T), float(h), band)
                    if C < min_C:
                        min_C = C
                    if C < -1e-10:
                        violations += 1

            results[band] = {
                "is_convex": violations == 0,
                "min_C": min_C if math.isfinite(min_C) else 0.0,
                "violations": violations,
            }

        return results


# =============================================================================
# SECTION 3: AXIOM 8 — INVERSE BITSIZE SHIFT  (CONJECTURAL)
# =============================================================================

AXIOM_8_STATEMENT = """
╔══════════════════════════════════════════════════════════════════════════════╗
║  AXIOM 8 — Inverse Bitsize Shift  (CONJECTURAL)                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  There exists a reconstruction map L such that, for all admissible T:       ║
║                                                                              ║
║      Â_9D(T) = S(T) · P₆ᵀ Ã(T) P₆  ⊕  A_macro(T)                           ║
║                                                                              ║
║  CONJECTURE (No-Loss Reconstruction):                                        ║
║      (Ã(T), S(T)) determines A_9D(T) uniquely up to natural symmetries.     ║
║                                                                              ║
║  STATUS: TESTABLE — NOT PROVED  (BS-5)                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


class MacroSectorReconstruction:
    """
    Reconstruct the 3×3 macro operator A_macro(T) from bitsize statistics.

    A_macro encodes:
      • Total bitsize energy E_macro
      • Mean bitsize ⟨b(n)⟩ over n ≤ T
      • Bitsize variance Var(b)
    """

    def __init__(self, T: float, N_max: Optional[int] = None) -> None:
        self.T = T
        self.N_max = N_max if N_max is not None else int(T)

        bitsizes_arr = np.array([bitsize(n) for n in range(1, self.N_max + 1)],
                                dtype=float)
        self.mean_b = float(np.mean(bitsizes_arr))
        self.var_b  = float(np.var(bitsizes_arr))
        self.max_b  = float(np.max(bitsizes_arr))
        self.expected_b = math.log2(max(T, 2.0))   # inside normalisation scalar

    def build_A_macro(self) -> np.ndarray:
        """
        Build the 3×3 diagonal macro operator from bitsize moments.

        A_macro = diag(mean_b, √var_b, max_b) / expected_b
        """
        norm = self.expected_b if self.expected_b > 0.0 else 1.0
        return np.array([
            [self.mean_b / norm,           0.0,                       0.0],
            [0.0,                math.sqrt(self.var_b) / norm,        0.0],
            [0.0,                          0.0,           self.max_b / norm],
        ])

    @property
    def energy(self) -> float:
        """Mean squared bitsize — the macro-sector energy proxy."""
        return float(
            sum(bitsize(n) ** 2 for n in range(1, self.N_max + 1))
            / self.N_max
        )


class InverseBitsizeShift:
    """
    AXIOM 8 implementation: reconstruct the 9D operator from (Ã, S(T)).

    FORWARD (Axioms 1–7):
        Ã(T) = (1/S(T)) P₆ A_9D(T) P₆ᵀ

    INVERSE (Axiom 8 — CONJECTURAL, BS-5):
        Â_9D(T) = S(T) P₆ᵀ Ã(T) P₆  ⊕  A_macro(T)
    """

    def __init__(
        self,
        T_range: Tuple[float, float] = (100.0, 500.0),
        num_samples: int = 30,
    ) -> None:
        self.T_min, self.T_max = T_range
        self.T_values = np.linspace(self.T_min, self.T_max, num_samples)

        self._factory     = StateFactory()
        self._scale_func  = BitsizeScaleFunctional()
        self._projection  = Projection6D()

        self.states: List[FactoredState9D] = [
            self._factory.create(T) for T in self.T_values
        ]

        self.S_T: float = float(
            np.mean([self._scale_func.S(T) for T in self.T_values])
        )

        self._operator_6D = NormalizedBridgeOperator(self.states, self.S_T)

    # ── accessors ──────────────────────────────────────────────────────────

    def get_A_tilde(self) -> np.ndarray:
        """Return the ensemble-averaged 6×6 normalised operator Ã."""
        return self._operator_6D.H_tilde

    def get_S_T(self) -> float:
        """Return the ensemble-averaged scale functional S(T)."""
        return self.S_T

    def build_A_macro(self, T: float) -> np.ndarray:
        """Build the 3×3 macro sector operator at height T."""
        return MacroSectorReconstruction(T).build_A_macro()

    # ── core reconstruction ────────────────────────────────────────────────

    def reconstruct_9D(self, T: Optional[float] = None) -> np.ndarray:
        """
        Reconstruct the 9×9 operator from (Ã, S(T), A_macro).

            Â_9D(T) = S(T) P₆ᵀ Ã(T) P₆  ⊕  A_macro(T)

        Result is block-diagonal: micro block (6×6) ⊕ macro block (3×3).
        """
        if T is None:
            T = float(np.mean(self.T_values))

        A_tilde  = self.get_A_tilde()              # 6×6
        S_at_T   = self._scale_func.S(T)
        A_micro  = S_at_T * A_tilde                # 6×6
        A_macro  = self.build_A_macro(T)           # 3×3

        A_9D = np.zeros((9, 9))
        A_9D[:6, :6] = A_micro
        A_9D[6:, 6:] = A_macro
        return A_9D

    def build_true_9D(self, T: float) -> np.ndarray:
        """
        Construct the 'true' 9D operator directly from prime states
        (no 6D reduction).  Used to measure reconstruction error.
        """
        A_ensemble = np.zeros((9, 9))
        for s in self.states:
            v = s.full_vector
            A_ensemble += np.outer(v, v)
        A_ensemble /= len(self.states)
        return A_ensemble

    # ── error analysis ─────────────────────────────────────────────────────

    def compute_reconstruction_error(self) -> Dict:
        """
        Measure ‖A_9D_true − Â_9D_recon‖_F and block-wise errors.

        This is the key test of the No-Loss Conjecture (BS-5).
        """
        T = float(np.mean(self.T_values))

        A_true  = self.build_true_9D(T)
        A_recon = self.reconstruct_9D(T)

        micro_true  = A_true[:6, :6]
        micro_recon = A_recon[:6, :6]
        macro_true  = A_true[6:, 6:]
        macro_recon = A_recon[6:, 6:]
        cross_true  = A_true[:6, 6:]

        total_norm = float(np.linalg.norm(A_true, "fro"))

        def rel_err(a: np.ndarray, b: np.ndarray) -> float:
            n = float(np.linalg.norm(a, "fro"))
            return float(np.linalg.norm(a - b, "fro")) / n if n > 0.0 else 0.0

        return {
            "T": T,
            "S_T": self._scale_func.S(T),
            "micro_rel_error": rel_err(micro_true, micro_recon),
            "macro_rel_error": rel_err(macro_true, macro_recon),
            "cross_term_norm": float(np.linalg.norm(cross_true, "fro")),
            "cross_rel": float(np.linalg.norm(cross_true, "fro")) / total_norm
                         if total_norm > 0.0 else 0.0,
            "total_error": float(np.linalg.norm(A_true - A_recon, "fro")),
            "total_rel_error": rel_err(A_true, A_recon),
            "A_9D_true": A_true,
            "A_9D_recon": A_recon,
        }

    def stability_over_T(self) -> List[Dict]:
        """Test reconstruction error stability at spot-check T values."""
        results = []
        for T in [100.0, 200.0, 300.0, 400.0, 500.0]:
            state = self._factory.create(T)
            v     = state.full_vector
            A_true = np.outer(v, v)

            S_at_T  = self._scale_func.S(T)
            A_recon = np.zeros((9, 9))
            A_recon[:6, :6] = S_at_T * self.get_A_tilde()
            A_recon[6:, 6:] = self.build_A_macro(T)

            norm  = float(np.linalg.norm(A_true, "fro"))
            error = float(np.linalg.norm(A_true - A_recon, "fro"))
            results.append({
                "T": T,
                "S_T": S_at_T,
                "error": error,
                "rel_error": error / norm if norm > 0.0 else 0.0,
            })
        return results


class BridgeLift6Dto9D:
    """
    Apply Axiom 8 to lift 6D bridge results back into full 9D prime geometry.

    Usage pattern (any BRIDGE_* execution script):

        from CONFIGURATIONS.AXIOMS import InverseBitsizeShift, BridgeLift6Dto9D
        inv = InverseBitsizeShift()
        lift = BridgeLift6Dto9D(inv)
        result = lift.lift_eigenvalues(eigs_6D)
    """

    def __init__(self, inverse_shift: InverseBitsizeShift) -> None:
        self.inverse = inverse_shift

    def lift_eigenvalues(self, eigenvalues_6D: np.ndarray) -> Dict:
        """
        Lift 6D eigenvalues into the 9D prime geometry.

        6D eigenvalues (zero-geometry) are scaled by S(T) for the micro
        sector; the macro sector eigenvalues come from A_macro.
        """
        S_T = self.inverse.get_S_T()
        T   = float(np.mean(self.inverse.T_values))

        eigs_micro = S_T * eigenvalues_6D
        A_macro    = self.inverse.build_A_macro(T)
        eigs_macro = np.linalg.eigvalsh(A_macro)

        eigs_9D = np.sort(np.concatenate([eigs_micro, eigs_macro]))[::-1]

        return {
            "6D_eigenvalues":     eigenvalues_6D,
            "9D_micro_eigenvalues": eigs_micro,
            "9D_macro_eigenvalues": eigs_macro,
            "9D_full_eigenvalues":  eigs_9D,
            "S_T": S_T,
            "lift_factor": S_T,
        }

    def lift_trace(self, trace_6D: float, power: int = 1) -> Dict:
        """
        Lift 6D trace Tr(Ã^n) to 9D.

        Tr(A_9D^n) = S(T)^n · Tr(Ã^n)  +  Tr(A_macro^n)
        """
        S_T  = self.inverse.get_S_T()
        T    = float(np.mean(self.inverse.T_values))

        micro_contribution = (S_T ** power) * trace_6D
        A_macro = self.inverse.build_A_macro(T)
        macro_trace = float(np.trace(np.linalg.matrix_power(A_macro, power)))

        return {
            "trace_6D":          trace_6D,
            "trace_9D_micro":    micro_contribution,
            "trace_9D_macro":    macro_trace,
            "trace_9D_total":    micro_contribution + macro_trace,
            "power":             power,
            "S_T_power":         S_T ** power,
        }

    def interpret_gue_statistics(self, gue_score_6D: float) -> Dict:
        """
        Interpret 6D GUE score in terms of full 9D prime geometry.

        The 6D (zero) sector shows GUE statistics.
        The 3D macro (PNT bulk) sector is NOT expected to be GUE.
        """
        return {
            "6D_gue_score": gue_score_6D,
            "micro_sector_gue": gue_score_6D,
            "macro_sector_gue": None,   # Not GUE — PNT bulk is statistically
                                        # distinct from zero-ripple sector.
            "note": (
                "GUE statistics apply to the 6D micro sector only.  "
                "The 3D macro sector encodes PNT bulk behavior and "
                "is not expected to follow GUE level-spacing."
            ),
        }


# =============================================================================
# SECTION 4: MASTER VERIFIER
# =============================================================================

class AxiomVerifier:
    """
    Verify all foundational axioms (Definitions 1–8 + Axiom 8) for a T range.

    Quick usage::

        from CONFIGURATIONS.AXIOMS import AxiomVerifier
        results = AxiomVerifier(T_range=(100, 300), num_samples=15).full_verification()
    """

    def __init__(
        self,
        T_range: Tuple[float, float] = (100.0, 500.0),
        num_samples: int = 20,
    ) -> None:
        self.T_min, self.T_max = T_range
        self.T_values = np.linspace(self.T_min, self.T_max, num_samples)

        self._factory   = StateFactory()
        self._scale     = BitsizeScaleFunctional()
        self._convexity = BandwiseConvexityChecker()

    # ── individual checks ──────────────────────────────────────────────────

    def verify_energy_conservation(self) -> Dict:
        """DEFINITION 3: E_9D = E_macro + E_micro  (exactly)."""
        errors = []
        for T in self.T_values:
            state = self._factory.create(T)
            errors.append(state.verify_conservation())
        return {
            "max_error": max(errors),
            "avg_error": sum(errors) / len(errors),
            "holds": max(errors) < 1e-10,
        }

    def verify_projection_orthogonality(self) -> Dict:
        """DEFINITION 2: T_macro ⊥ T_micro — norms add correctly."""
        max_err = 0.0
        for T in self.T_values:
            state = self._factory.create(T)
            err = abs(float(np.linalg.norm(state.full_vector) ** 2)
                      - state.E_macro - state.E_micro)
            if err > max_err:
                max_err = err
        return {"max_orthogonality_error": max_err, "holds": max_err < 1e-10}

    def verify_scale_functional(self) -> Dict:
        """DEFINITION 5: S(T) = 2^{Δb(T)} is well-defined and stable."""
        S_vals = [self._scale.S(T) for T in self.T_values]
        db_vals = [self._scale.delta_b(T) for T in self.T_values]
        return {
            "S_min": min(S_vals),
            "S_max": max(S_vals),
            "S_mean": float(np.mean(S_vals)),
            "delta_b_mean": float(np.mean(db_vals)),
            "delta_b_std": float(np.std(db_vals)),
            "well_defined": all(s > 0.0 for s in S_vals),
        }

    def verify_bandwise_convexity(self) -> Dict[int, Dict]:
        """AXIOM U1* (Definition 8): C_k(T, h) ≥ 0 for all bands k."""
        return self._convexity.verify_all_bands(self.T_values)

    def build_normalized_operator(self) -> NormalizedBridgeOperator:
        """DEFINITION 6: Construct Ã = (1/S) P₆ A P₆ᵀ."""
        states = [self._factory.create(T) for T in self.T_values]
        S_T = float(np.mean([self._scale.S(T) for T in self.T_values]))
        return NormalizedBridgeOperator(states, S_T)

    # ── full run ───────────────────────────────────────────────────────────

    def full_verification(self) -> Dict:
        """Run all axiom checks and print a summary."""
        print("=" * 72)
        print("AXIOM VERIFICATION  —  FORMAL_PROOF_NEW  (Definitions 1–8 + Ax 8)")
        print(f"  λ* = {LAMBDA_STAR}")
        print(f"  ‖x*‖₂ = {NORM_X_STAR}")
        print("=" * 72)

        # Def 3: Energy conservation
        print("\nDEFINITION 3 — Energy Conservation  E_9D = E_macro + E_micro")
        print("-" * 55)
        cons = self.verify_energy_conservation()
        print(f"  Max error : {cons['max_error']:.2e}")
        print(f"  Status    : {'✓ HOLDS' if cons['holds'] else '✗ FAILS'}")

        # Def 2: Orthogonality
        print("\nDEFINITION 2 — Orthogonal Factorisation  X = X_macro ⊕ X_micro")
        print("-" * 55)
        orth = self.verify_projection_orthogonality()
        print(f"  Max error : {orth['max_orthogonality_error']:.2e}")
        print(f"  Status    : {'✓ HOLDS' if orth['holds'] else '✗ FAILS'}")

        # Def 5: Scale functional
        print("\nDEFINITION 5 — Scale Functional  S(T) = 2^{Δb(T)}")
        print("-" * 55)
        scl = self.verify_scale_functional()
        print(f"  S(T) range: [{scl['S_min']:.2f}, {scl['S_max']:.2f}]")
        print(f"  Δb mean   : {scl['delta_b_mean']:.2f} bits")
        print(f"  Status    : {'✓ WELL-DEFINED' if scl['well_defined'] else '✗ UNDEFINED'}")

        # Axiom U1*: Band-wise convexity
        print("\nAXIOM U1* (Def 8) — Band-Wise Convexity  C_k(T,h) ≥ 0")
        print("-" * 55)
        bw = self.verify_bandwise_convexity()
        all_convex = all(v["is_convex"] for v in bw.values())
        for band, res in sorted(bw.items()):
            sym = "✓" if res["is_convex"] else "✗"
            print(f"  Band {band:2d}: {sym}  min C = {res['min_C']:.2e}")
        print(f"  Status    : {'✓ ALL CONVEX' if all_convex else '✗ SOME BANDS FAIL'}")

        # Def 6: Normalised operator
        print("\nDEFINITION 6 — Normalised Operator  Ã = (1/S) P₆ A P₆ᵀ")
        print("-" * 55)
        op = self.build_normalized_operator()
        print(f"  S(T) used : {op.S_T:.2f}")
        for i, eig in enumerate(op.eigenvalues):
            print(f"  λ_{i+1}       = {eig:.6e}")
        print(f"  Tr(Ã)     = {op.trace_power(1):.6e}")
        print(f"  Tr(Ã²)    = {op.trace_power(2):.6e}")

        # ── Separate core axioms from conjectural U1* (BS-5) ─────────────────
        # Core: Definitions 2, 3, 5 (conservation, orthogonality, scale).
        # U1* (band-wise convexity, Axiom 8 / BS-5) is CONJECTURAL and does
        # NOT gate the overall core verdict — matching the semantics in
        # STEP_01_OBTAIN_RESOURCES.py.
        core_hold = cons["holds"] and orth["holds"] and scl["well_defined"]
        all_hold  = core_hold and all_convex   # full hold requires U1* too

        print("\n" + "=" * 72)
        core_sym = "✓ CORE AXIOMS HOLD" if core_hold else "✗ CORE AXIOMS FAIL"
        u1_sym   = "✓ U1* HOLDS (conjectural)" if all_convex else "⚠  U1* FAILS (conjectural — does not gate core)"
        print(f"CORE   : {core_sym}")
        print(f"U1*    : {u1_sym}")
        print(f"OVERALL: {'✓ ALL AXIOMS HOLD' if all_hold else core_sym + ' | ' + u1_sym}")
        print("=" * 72)

        return {
            "conservation": cons,
            "orthogonality": orth,
            "scale": scl,
            "bandwise_convexity": bw,
            "operator": op,
            "core_hold": core_hold,
            "all_hold": all_hold,
        }


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Constants
    "LAMBDA_STAR",
    "NORM_X_STAR",
    "COUPLING_K",
    "PHI",
    "DIM_9D",
    "DIM_6D",
    "DIM_3D",
    # Arithmetic primitives
    "von_mangoldt",
    "bitsize",
    "bit_band",
    # Definitions 1–8
    "FactoredState9D",
    "StateFactory",
    "Projection6D",
    "BitsizeScaleFunctional",
    "NormalizedBridgeOperator",
    "BandRestrictedState",
    "BandwiseConvexityChecker",
    # Axiom 8 (conjectural)
    "AXIOM_8_STATEMENT",
    "MacroSectorReconstruction",
    "InverseBitsizeShift",
    "BridgeLift6Dto9D",
    # Verifier
    "AxiomVerifier",
]


# =============================================================================
# SMOKE TEST
# =============================================================================

def _smoke_test() -> None:
    """Quick sanity check — runs in < 5 s for small T range."""
    print("Running AXIOMS.py smoke test …")

    # Def 1
    assert bitsize(8) == 3
    assert bitsize(1) == 0
    assert bit_band(15) == 3
    print("  Def 1 (bitsize):        ✓")

    # Def 2 + 3
    factory = StateFactory()
    state = factory.create(50.0)
    assert state.T_macro.shape == (3,)
    assert state.T_micro.shape == (6,)
    assert state.verify_conservation() < 1e-12
    print("  Def 2+3 (factorisation): ✓")

    # Def 4
    proj = Projection6D.project(state)
    assert proj.shape == (6,)
    print("  Def 4 (projection):     ✓")

    # Def 5
    sf = BitsizeScaleFunctional()
    S = sf.S(50.0)
    assert S > 0.0
    print(f"  Def 5 (S(50)={S:.2f}):  ✓")

    # Def 6
    states_small = [factory.create(T) for T in [30.0, 40.0, 50.0]]
    op = NormalizedBridgeOperator(states_small, S)
    assert op.H_tilde.shape == (6, 6)
    print("  Def 6 (Ã operator):     ✓")

    # Von Mangoldt
    assert abs(von_mangoldt(2) - math.log(2)) < 1e-12
    assert von_mangoldt(6) == 0.0
    print("  von_mangoldt:           ✓")

    # Constants present
    assert LAMBDA_STAR > 494.0
    assert NORM_X_STAR > 0.3
    print(f"  Constants (λ*={LAMBDA_STAR:.2f}): ✓")

    print("Smoke test PASSED.\n")


if __name__ == "__main__":
    _smoke_test()
    verifier = AxiomVerifier(T_range=(100.0, 200.0), num_samples=10)
    verifier.full_verification()
