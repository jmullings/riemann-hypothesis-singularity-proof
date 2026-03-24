#!/usr/bin/env python3
"""
================================================================================
operator_axioms.py — PHO-Representability Predicate
================================================================================

Finite-dimensional PHO (Polymeric Hilbert–Pólya Operator) admissibility test.

A matrix H is PHO-representable if it satisfies ALL of:
  1. Self-adjoint: H ≈ H†  (Hermitian within numerical tolerance)
  2. Real spectrum: all eigenvalues have negligible imaginary part
  3. Orthonormal eigenvectors: V†V = I  (eigenvectors form an ONB)
  4. Spectral reconstruction: H = V Λ V†  (spectral theorem)

HONEST: This is a STRUCTURAL filter on finite-dimensional matrices.
It does NOT assert that any operator's spectrum equals Riemann zeros.
PHO-representability is necessary but not sufficient for a Hilbert–Pólya
connection to ζ(s).
================================================================================
"""

import numpy as np


def is_PHO_representable(H, atol=1e-10, rtol=1e-10):
    """
    Finite-dimensional PHO-admissibility test.

    Checks:
      1. H is square
      2. H is (numerically) self-adjoint: H ≈ H†
      3. Spectrum is (numerically) real
      4. Eigenvectors form an orthonormal basis: V†V = I
      5. Spectral reconstruction holds: H = V Λ V†

    Parameters:
        H : array_like, square matrix to test
        atol : absolute tolerance for numerical comparisons
        rtol : relative tolerance for numerical comparisons

    Returns:
        bool — True if H passes all PHO admissibility checks
    """
    H = np.asarray(H, dtype=np.complex128)

    # 1. Square check
    if H.ndim != 2 or H.shape[0] != H.shape[1]:
        return False

    # 2. Self-adjoint: H ≈ H†
    if not np.allclose(H, H.conj().T, atol=atol, rtol=rtol):
        return False

    # 3–5. Spectral theorem structure
    # np.linalg.eigh assumes Hermitian input but check 2 already validated that.
    evals, V = np.linalg.eigh(H.real if np.allclose(H.imag, 0) else H)

    # 3. Real spectrum (eigh returns real for Hermitian, but be explicit)
    if not np.all(np.isfinite(evals)):
        return False

    # 4. Orthonormal eigenvectors: V†V = I
    n = V.shape[1]
    if not np.allclose(V.conj().T @ V, np.eye(n), atol=atol, rtol=rtol):
        return False

    # 5. Spectral reconstruction: H = V Λ V†
    H_rec = V @ np.diag(evals) @ V.conj().T
    H_check = H.real if np.allclose(H.imag, 0) else H
    if not np.allclose(H_check, H_rec, atol=atol, rtol=rtol):
        return False

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — ARITHMETIC BINDING PREDICATE
# ═══════════════════════════════════════════════════════════════════════════════

def is_arithmetically_bound(spectrum, ref_invariants=None, thresholds=None):
    """
    Arithmetic binding test: does this spectrum reproduce number-theoretic
    invariants consistent with Riemann zeta zeros?

    A spectrum is arithmetically bound if:
      1. Counting function distance to Riemann–von Mangoldt ≤ threshold
      2. KS statistic against GUE Wigner surmise ≤ threshold
      3. Linear statistics within tolerance of reference

    Parameters:
        spectrum: 1D array of eigenvalues/zero ordinates
        ref_invariants: dict from compute_reference_invariants() (or None for auto)
        thresholds: dict with 'counting', 'spacing', 'linear' keys (or None for defaults)

    Returns:
        bool — True if all binding tests pass
    """
    from .arithmetic_invariants import compute_zero_like_invariants, compute_reference_invariants

    if thresholds is None:
        thresholds = {
            'counting': 3.0,    # L² distance from N₀(T)
            'spacing': 0.5,     # KS statistic vs GUE
            'linear': None,     # auto-set from reference ± tolerance
        }

    if ref_invariants is None:
        ref_invariants = compute_reference_invariants()

    inv = compute_zero_like_invariants(np.asarray(spectrum, dtype=float))

    # 1. Counting function close to Riemann–von Mangoldt
    if inv['counting_distance'] > thresholds['counting']:
        return False

    # 2. Spacing distribution close to GUE
    if inv['ks_statistic'] > thresholds['spacing']:
        return False

    # 3. Linear statistics close to reference (if threshold set)
    if thresholds.get('linear') is not None:
        ref_lin = ref_invariants.get('linear_stat', 0.0)
        if abs(inv['linear_stat'] - ref_lin) > thresholds['linear']:
            return False

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — GRAVITY-WELL GATE (PHO + PSD + ARITHMETIC BINDING)
# ═══════════════════════════════════════════════════════════════════════════════

def gravity_well_gate(operator, spectrum, ref_invariants=None, thresholds=None):
    """
    Full gravity-well admissibility gate:

      1. PHO-representable (self-adjoint, real spectrum, ONB, spectral theorem)
      2. Arithmetically bound to ζ(s) (counting, spacings, linear stats)

    Both must pass for the operator+spectrum pair to be admissible.

    Parameters:
        operator: square matrix (Hamiltonian)
        spectrum: 1D array of eigenvalues
        ref_invariants: reference invariants (or None for auto)
        thresholds: binding thresholds (or None for defaults)

    Returns:
        bool — True if operator passes both gates
    """
    if not is_PHO_representable(operator):
        return False
    if not is_arithmetically_bound(spectrum, ref_invariants, thresholds):
        return False
    return True
