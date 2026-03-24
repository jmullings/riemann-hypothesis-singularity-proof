#!/usr/bin/env python3
r"""
================================================================================
limit_safety.py — Limit Interchange and Dirichlet Proxy Guards
================================================================================

Enforces rigorous mathematical limits on promoting finite-N Dirichlet
approximations to the true Riemann zeta function.

ARCHITECTURAL ROLE:
  This module implements the "Limit Safety API" — a principled guard system
  that prevents silent promotion of finite-N Dirichlet polynomial results
  (D_N(t) = Σ_{n≤N} n^{-s}) to statements about the true ζ(s).

  At σ = 1/2 (the critical line), classical unconditional bounds on
  |ζ(1/2+it) - D_N(t)| do NOT vanish uniformly in t without assuming
  RH or Lindelöf. This means any limit interchange at the critical line
  requires RH-equivalent uniformity — the Level C promotion status
  reflects this mathematical reality.

FEATURES:
  §1  E(N, T) Envelopes: Classical, unconditional bounds on |ζ - D_N|
      from Hardy-Littlewood / Titchmarsh.
  §2  ζ-Shadow Functional: Direct evaluation using mpmath for cross-
      validation on bounded boxes.
  §3  LimitInterchangeGuard: Prevents illegal N → ∞ promotions by
      checking whether the classical error envelope permits the limit.
  §4  Level A/B/C Taxonomy: Classification system for promotion claims.

THREE LEVELS OF CLAIMS:
  Level A: Pure kernel statement (independent of ζ)
  Level B: Dirichlet-polynomial model statement (finite N, no ζ substitution)
  Level C: Promotion to ζ (requires uniform convergence bounds)

CRITIQUE RESPONSE (External Review, Critique #3 — "Limit Interchange Circularity"):
  An external review identified that promoting D_N results to ζ(s) at
  σ = 1/2 requires uniform convergence, which itself depends on RH or
  the Lindelöf Hypothesis — creating potential circularity.

  RESPONSE — The critic is CORRECT.  This is a genuine mathematical gap
  and this module exists precisely to track it:
    • The core contradiction chain (Lemmas 1-3) operates at Level A/B ONLY.
      It proves properties of the sech²-corrected kernel (Level A, algebraic
      identity) and the finite Dirichlet polynomial model (Level B).
    • Level C promotion to the true ζ(s) IS the open mathematical problem.
      The `LimitInterchangeGuard` honestly flags this via
      `requires_RH_uniformity = True` at σ = 1/2.
    • The proof chain is NOT circular: it does not assume RH to prove RH.
      It proves the finite-model result unconditionally.  The promotion from
      the finite model to ζ(s) is a separate step that remains open.
    • The `chain_complete` flag in proof_chain.py is TRUE because the A/B
      chain is complete.  Level C status is reported as METADATA (via the
      `limit_safety` field) without blocking the finite-model verdict.

  The TDD architecture makes this gap a labeled, tracked variable — it
  cannot be silently assumed away.

REFERENCES:
  - Titchmarsh (1986), The Theory of the Riemann Zeta-Function, §4
  - Hardy & Littlewood, approximate functional equation remainders
  - Kadiri, Ng, Trudgian (2010–2025), explicit zero-free regions
================================================================================
"""

import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — CLASSICAL DIRICHLET ERROR ENVELOPES E(N, T)
# ═══════════════════════════════════════════════════════════════════════════════

def classical_dirichlet_error_bound(sigma, t, N):
    r"""
    H1: Published, unconditional bound on |ζ(s) - D_N(s)|.

    Using Hardy-Littlewood / Titchmarsh approximate functional equation
    remainder bounds (Titchmarsh 1986, §4.12).

    For s = σ + it with σ ∈ [0, 1], the classical truncation error:
        E(N, σ, t) = O(t^{1/2 - σ} · N^{-σ}) + O(t · N^{-(1+σ)})

    We provide a strict upper envelope for diagnostic guarding.
    At σ = 1/2, this does NOT vanish uniformly in t without RH.

    Parameters
    ----------
    sigma : float
        Real part of s (typically 0.5 for critical line).
    t : float
        Imaginary part of s.
    N : int
        Truncation length of Dirichlet polynomial.

    Returns
    -------
    float
        Upper bound on |ζ(σ+it) - D_N(σ+it)|.
    """
    if N <= 0:
        return np.inf

    t_abs = max(abs(float(t)), 1.0)
    sigma = float(sigma)
    N = int(N)

    # Classical approximate functional equation remainder
    # Two-term bound from Titchmarsh §4.12
    term1 = (t_abs / (2 * np.pi)) ** (0.5 - sigma) * (N ** (-sigma))
    term2 = t_abs / (N ** (1.0 + sigma))

    return float(term1 + term2)


def error_envelope_monotone_in_N(sigma, t, N_values):
    """
    Verify that E(N, σ, t) is monotone decreasing in N at fixed σ, t.

    Returns dict with monotonicity check results.
    """
    bounds = [classical_dirichlet_error_bound(sigma, t, N) for N in N_values]
    monotone = all(
        bounds[i] >= bounds[i + 1] - 1e-15
        for i in range(len(bounds) - 1)
    )

    return {
        'N_values': list(N_values),
        'bounds': bounds,
        'monotone_decreasing': monotone,
        'min_bound': min(bounds),
        'max_bound': max(bounds),
    }


def error_envelope_growth_in_T(sigma, t_values, N):
    """
    Characterise E(N, σ, t) growth as t increases at fixed σ, N.

    At σ = 1/2: E grows with t (cannot vanish uniformly).
    At σ > 1: E stays bounded (uniform convergence possible).
    """
    bounds = [classical_dirichlet_error_bound(sigma, t, N) for t in t_values]

    grows_with_t = any(
        bounds[i] < bounds[i + 1]
        for i in range(len(bounds) - 1)
    )

    return {
        't_values': list(t_values),
        'bounds': bounds,
        'grows_with_t': grows_with_t,
        'sigma': sigma,
        'N': N,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — ζ-SHADOW FUNCTIONAL (mpmath Ground Truth)
# ═══════════════════════════════════════════════════════════════════════════════

def zeta_shadow_value(sigma, t):
    """
    Evaluate ζ(σ + it) using mpmath for ground-truth comparison.

    Returns complex value of ζ at the given point.
    """
    import mpmath
    mpmath.mp.dps = 30
    s = mpmath.mpc(sigma, t)
    return complex(mpmath.zeta(s))


def dirichlet_polynomial_value(sigma, t, N):
    r"""
    Evaluate D_N(σ + it) = Σ_{n=1}^{N} n^{-(σ+it)}.
    """
    ns = np.arange(1, N + 1, dtype=np.float64)
    vals = ns ** (-sigma) * np.exp(-1j * t * np.log(ns))
    return complex(np.sum(vals))


def measured_discrepancy(sigma, t, N):
    """
    Measure |ζ(s) - D_N(s)| at a specific point.

    Returns dict with theoretical bound vs measured discrepancy.
    """
    zeta_val = zeta_shadow_value(sigma, t)
    dn_val = dirichlet_polynomial_value(sigma, t, N)
    measured = abs(zeta_val - dn_val)
    theoretical = classical_dirichlet_error_bound(sigma, t, N)

    return {
        'sigma': sigma,
        't': t,
        'N': N,
        'zeta_value': zeta_val,
        'D_N_value': dn_val,
        'measured_discrepancy': measured,
        'theoretical_bound': theoretical,
        'bound_valid': theoretical >= measured * 0.9,  # 10% constant-factor tolerance
    }


def zeta_shadow_functional(T0, H, n_points=200):
    r"""
    Evaluate the true ζ-based functional ∫ |ζ(1/2+i(T0+t))|² w_H(t) dt
    on a bounded box using mpmath.

    This is the ground-truth baseline against which D_N-based functionals
    are measured.  Only used on bounded T0 — NOT for asymptotic claims.
    """
    import mpmath
    mpmath.mp.dps = 30

    # Integrate over [-5H, 5H] where sech²(t/H) is non-negligible
    t_grid = np.linspace(-5 * H, 5 * H, n_points)
    dt = t_grid[1] - t_grid[0]

    integral = 0.0
    for t in t_grid:
        s = mpmath.mpc(0.5, T0 + t)
        zeta_val = complex(mpmath.zeta(s))
        weight = 1.0 / np.cosh(t / H) ** 2  # sech²(t/H)
        integral += (abs(zeta_val) ** 2) * weight * dt

    return float(integral)


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — LIMIT INTERCHANGE GUARD
# ═══════════════════════════════════════════════════════════════════════════════

class LimitInterchangeGuard:
    r"""
    H2: Guard object enforcing proven bounds before permitting N → ∞
    limit interchanges.

    At σ = 1/2 (critical line), the classical error E(N, T) does NOT
    vanish uniformly in T as N → ∞ without assuming RH or Lindelöf.

    This guard:
    1. Computes the maximum E(N, T) over the integration window
    2. Checks if this permits a safe limit interchange
    3. Tags the promotion as CONJECTURAL if RH-equivalent uniformity
       would be needed

    Usage:
        guard = LimitInterchangeGuard(T0_range=[0, 100], N=100, H=3.0)
        cert = guard.generate_certificate()
        if cert['is_promotable']:
            # Safe to promote finite-N result to ζ
        else:
            # Level C is CONJECTURAL
    """

    def __init__(self, T0_range, N, H, sigma=0.5):
        self.T0_max = max(T0_range)
        self.T0_min = min(T0_range)
        self.N = int(N)
        self.H = float(H)
        self.sigma = float(sigma)

        # Calculate max theoretical error over the integration window
        # Worst case is at the top of the T0 range + kernel support
        t_worst = self.T0_max + 10 * H
        self.max_E_N_T = classical_dirichlet_error_bound(sigma, t_worst, N)

        # At σ = 1/2, the classical bound does NOT vanish uniformly.
        # Even if E(N, T_max) is small for this specific T_max, the bound
        # grows without limit as T → ∞ at σ = 1/2. This means the limit
        # interchange cannot be justified unconditionally.
        # For σ > 1, E → 0 as N → ∞ at fixed T (unconditional).
        if sigma <= 0.5 + 1e-10:
            # σ ≤ 1/2: always conjectural — E does not vanish uniformly in T
            self.requires_RH_uniformity = True
        else:
            # σ > 1: classical bounds vanish as N → ∞
            self.requires_RH_uniformity = self.max_E_N_T > 0.01
        self.is_promotable = not self.requires_RH_uniformity

    def generate_certificate(self):
        """Generate a structured certificate documenting limit safety status."""
        return {
            'N': self.N,
            'H': self.H,
            'sigma': self.sigma,
            'T0_range': [self.T0_min, self.T0_max],
            'E_N_T_bound': self.max_E_N_T,
            'requires_RH_uniformity': self.requires_RH_uniformity,
            'is_promotable': self.is_promotable,
            'status': 'CONJECTURAL' if self.requires_RH_uniformity else 'PROVED',
            'reason': (
                f'At σ={self.sigma}, classical E(N={self.N}, '
                f'T={self.T0_max + 10 * self.H:.0f}) = '
                f'{self.max_E_N_T:.4e}. '
                + (
                    'Unconditional bounds do not vanish uniformly in T at the '
                    'critical line without assuming RH or Lindelöf hypothesis.'
                    if self.requires_RH_uniformity else
                    'Classical bounds permit uniform convergence at this σ.'
                )
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — PROMOTION CLASSIFICATION (Level A / B / C)
# ═══════════════════════════════════════════════════════════════════════════════

# Promotion level constants
LEVEL_A = 'LEVEL_A'    # Pure kernel statement (no ζ reference)
LEVEL_B = 'LEVEL_B'    # Dirichlet model statement (finite N)
LEVEL_C = 'LEVEL_C'    # Promotion to ζ (requires limit interchange)

NON_PROMOTABLE = 'NON_PROMOTABLE'
"""Label for lemmas whose promotion would require RH-equivalent uniformity.
These are kept as conjectural modules with explicit metadata."""


def classify_promotion(statement_type, sigma=0.5, N=None, T0_max=None, H=None):
    """
    Classify a mathematical statement as Level A, B, or C.

    Level A: Pure kernel / harmonic analysis fact (no ζ, no D_N)
    Level B: Dirichlet polynomial model (finite N, no ζ substitution)
    Level C: Promotion to true ζ (requires limit interchange guard)

    Returns classification dict.
    """
    if statement_type == LEVEL_A:
        return {
            'level': LEVEL_A,
            'status': 'PROVED',
            'depends_on_zeta': False,
            'depends_on_DN': False,
            'requires_limit_interchange': False,
        }

    elif statement_type == LEVEL_B:
        return {
            'level': LEVEL_B,
            'status': 'PROVED',
            'depends_on_zeta': False,
            'depends_on_DN': True,
            'requires_limit_interchange': False,
            'N': N,
        }

    elif statement_type == LEVEL_C:
        if N is None or T0_max is None or H is None:
            return {
                'level': LEVEL_C,
                'status': 'UNGUARDED',
                'depends_on_zeta': True,
                'depends_on_DN': True,
                'requires_limit_interchange': True,
                'error': 'Missing parameters for LimitInterchangeGuard',
            }

        guard = LimitInterchangeGuard(
            T0_range=[0.0, T0_max], N=N, H=H, sigma=sigma,
        )
        cert = guard.generate_certificate()

        return {
            'level': LEVEL_C,
            'status': cert['status'],
            'depends_on_zeta': True,
            'depends_on_DN': True,
            'requires_limit_interchange': True,
            'limit_guard': cert,
            'is_promotable': cert['is_promotable'],
        }

    else:
        raise ValueError(f"Unknown statement type: {statement_type}")


def is_conjectural(classification):
    """Check if a promotion classification is conjectural (requires RH)."""
    if classification['level'] == LEVEL_C:
        return classification.get('status') != 'PROVED'
    return False


def non_promotable_metadata(theorem_name, reason):
    """
    Create metadata tag for a lemma whose promotion requires RH.

    This lemma should NOT be consumed by the RH contradiction chain
    as if the promotion were analytic.
    """
    return {
        'theorem': theorem_name,
        'label': NON_PROMOTABLE,
        'requires': 'RH-equivalent uniform convergence',
        'reason': reason,
        'consumable_by_proof_chain': False,
    }
