#!/usr/bin/env python3
"""
================================================================================
hp_alignment.py — Dirichlet–HP Alignment and Hybrid Crack Functional
================================================================================

Implements the hybrid RS–HP spectral sieve:
  • Dirichlet state φ(T₀, Δβ) in the n-basis
  • HP spectral energy B_HP(T₀, Δβ) = ⟨φ, H_HP φ⟩
  • RS Rayleigh quotient with Δβ drift
  • Hybrid functional F_tot^RS = F̃₂ + ε·B_HP
  • Hybrid Rayleigh quotient λ_new^*(T₀, Δβ)

THE IDEA:
    The old RS Rayleigh quotient λ_old dips below λ*(H) = 4/H² for small Δβ
    (this is the "crack"). Adding the HP spectral energy as a penalty term
    may lift the quotient above the Bochner floor — but this is EXPERIMENTAL.

WHAT THIS DOES NOT PROVE:
    Global inequality λ_new ≥ λ*(H) for all T₀, Δβ (OPEN).
    The tests measure whether the HP penalty improves the small-Δβ behaviour
    compared to the pure RS functional.

LOG-FREE: No runtime log() operations.
================================================================================
"""

import numpy as np

from .bochner import F2_corrected, rayleigh_quotient as bochner_rayleigh, lambda_star
from .hilbert_polya import hp_operator_matrix
from .kernel import W_curv, w_H


# ─────────────────────────────────────────────────────────────────────────────
# §1 — Dirichlet state with Δβ drift
# ─────────────────────────────────────────────────────────────────────────────

def dirichlet_state(T0, N, delta_beta=0.0):
    """
    Dirichlet state φ_{T₀,Δβ} in the n-basis:

        φ_n(T₀,Δβ) = n^{-1/2-Δβ} · e^{-i T₀ log n},  1 ≤ n ≤ N.

    This is the finite-dimensional "arithmetic state" fed into H_HP.
    """
    n = np.arange(1, N + 1, dtype=np.float64)
    logn = np.log(n)
    amp = n ** (-0.5 - float(delta_beta))
    phase = np.exp(-1j * T0 * logn)
    return amp * phase  # shape (N,), complex


# ─────────────────────────────────────────────────────────────────────────────
# §2 — HP spectral energy on Dirichlet states
# ─────────────────────────────────────────────────────────────────────────────

def hp_energy(T0, H_hp, N, delta_beta=0.0):
    """
    Spectral energy of the Dirichlet state under H_HP:

        B_HP(T₀,Δβ) = ⟨φ_{T₀,Δβ}, H_HP φ_{T₀,Δβ}⟩.

    Returns float (real part of inner product).
    """
    phi = dirichlet_state(T0, N, delta_beta=delta_beta)
    v = H_hp @ phi
    val = np.vdot(phi, v)  # ⟨φ, H φ⟩
    return float(val.real)


# ─────────────────────────────────────────────────────────────────────────────
# §3 — RS Rayleigh quotient with Δβ drift
# ─────────────────────────────────────────────────────────────────────────────

def rs_rayleigh_with_drift(T0, H, N, delta_beta=0.0, n_points=500):
    """
    RS-side Rayleigh quotient data under amplitude drift Δβ.

    Computes:
        A = ∫ W_curv(t) |D_N^{(Δβ)}(T₀+t)|² dt
        B = ∫ w_H(t)    |D_N^{(Δβ)}(T₀+t)|² dt
        λ*(T₀) = -A/B

    where D_N^{(Δβ)}(t) = Σ n^{-1/2-Δβ} e^{-i t log n}.
    """
    t_grid = np.linspace(-10 * H, 10 * H, n_points)
    dt = t_grid[1] - t_grid[0]

    ks = np.arange(1, N + 1, dtype=np.float64)
    log_ks = np.log(ks)
    amp = ks ** (-0.5 - float(delta_beta))
    # shape (N, n_points)
    phases = np.exp(-1j * log_ks[:, None] * (T0 + t_grid[None, :]))
    D = np.sum(amp[:, None] * phases, axis=0)
    D_sq = np.abs(D) ** 2

    A = float(np.sum(W_curv(t_grid, H) * D_sq) * dt)
    B = float(np.sum(w_H(t_grid, H) * D_sq) * dt)

    lam_T0 = -A / B if B > 0 else np.inf

    return {'A': A, 'B': B, 'lambda_star_T0': lam_T0}


# ─────────────────────────────────────────────────────────────────────────────
# §4 — Hybrid functional and Rayleigh quotient
# ─────────────────────────────────────────────────────────────────────────────

def hybrid_lambda_star(T0, H, N, H_hp, eps, delta_beta=0.0, n_points=500):
    """
    Hybrid Rayleigh quotient:

        λ_new^*(T₀,Δβ;H) =
            [ -A_RS(T₀,Δβ,H) + ε · B_HP(T₀,Δβ) ] / B_RS(T₀,Δβ,H).

    Returns dict with:
        'A_RS', 'B_RS', 'B_HP', 'lambda_old', 'lambda_new'
    """
    rs = rs_rayleigh_with_drift(T0, H, N, delta_beta=delta_beta,
                                n_points=n_points)
    A_RS = rs['A']
    B_RS = rs['B']
    lam_old = rs['lambda_star_T0']

    B_HP = hp_energy(T0, H_hp, N, delta_beta=delta_beta)

    if B_RS <= 0:
        lam_new = np.inf
    else:
        lam_new = (-A_RS + eps * B_HP) / B_RS

    return {
        'A_RS': A_RS,
        'B_RS': B_RS,
        'B_HP': B_HP,
        'lambda_old': lam_old,
        'lambda_new': lam_new,
    }


def hybrid_F2_RS(T0, H, N, H_hp, eps, delta_beta=0.0, n_points=500):
    """
    Hybrid RS functional at Dirichlet level:

        F_tot^(N)(T₀,H) = F̃₂^(N)(T₀,H) + ε · B_HP(T₀,Δβ).

    Here F̃₂^(N) uses the corrected Bochner kernel (Theorem B 2.0).
    """
    F_corr = F2_corrected(T0, H, N, lam=None, n_points=n_points)
    B_HP = hp_energy(T0, H_hp, N, delta_beta=delta_beta)
    return float(F_corr + eps * B_HP)
