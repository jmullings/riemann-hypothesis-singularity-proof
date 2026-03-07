#!/usr/bin/env python3
"""
RHSINGULARITY.py
================

Tier-2 Singularity / Phase-Wheel Layer (Heuristic Visualization)

This module provides heuristic diagnostics for the 9D singularity framework.
These are NOT zero-certifying tests — they are observational tools that
correlate with zeta zero behavior but do not constitute a proof.

Functions:
---------
- compute_balance_vector: Head-tail balance on the 9 branches
- singularity_score: Heuristic score measuring singularity proximity
- phase_entropy: φ-weighted entropy of the branch distribution
"""

import numpy as np
from typing import Tuple

# Golden ratio
PHI = (1.0 + np.sqrt(5.0)) / 2.0
NUM_BRANCHES = 9

# Calibrated branch weights (normalized)
BRANCH_WEIGHTS = np.array([
    0.0175504462, 0.1471033037, 0.0041498042, 0.3353044327,
    0.0981287513, 0.0127626154, 0.1906439411, 0.1869808699, 0.0073758354
])
BRANCH_WEIGHTS /= BRANCH_WEIGHTS.sum()

# Branch signatures
BRANCH_SIGNATURES = np.array([(-1.0)**k for k in range(NUM_BRANCHES)])


def compute_balance_vector(T: float, branch_lengths: np.ndarray = None) -> np.ndarray:
    """
    Compute the 9D head-tail balance vector at s = 1/2 + iT.
    
    The balance measures the residual between head (real projection)
    and tail (imaginary projection) components on each branch.
    
    Parameters
    ----------
    T : float
        Height on the critical line
    branch_lengths : np.ndarray, optional
        Branch geodesic lengths (default: 1, 2, ..., 9)
    
    Returns
    -------
    np.ndarray
        9D balance vector
    """
    if branch_lengths is None:
        branch_lengths = np.arange(1, NUM_BRANCHES + 1, dtype=float)
    
    s = complex(0.5, T)
    
    # Branch kernels: κ_k(s) = w_k · σ_k · e^{-s·ℓ_k}
    kernels = BRANCH_WEIGHTS * BRANCH_SIGNATURES * np.exp(-s * branch_lengths)
    
    # Head (real) and tail (imaginary) components
    head = kernels.real
    tail = kernels.imag
    
    # φ-phase rotation
    theta = T / (PHI * BRANCH_WEIGHTS.sum())
    phase = np.exp(1j * theta)
    
    # Balance = head + phase-rotated tail
    balance = head + (phase * (tail * 1j)).real
    
    return balance


def singularity_score(balance: np.ndarray) -> float:
    """
    Compute a heuristic singularity score from the balance vector.
    
    Higher scores indicate proximity to a potential singularity.
    
    THIS IS A HEURISTIC — not a rigorous zero test.
    
    Parameters
    ----------
    balance : np.ndarray
        9D balance vector from compute_balance_vector
    
    Returns
    -------
    float
        Singularity score (unbounded, higher = more singular)
    """
    # Norm-based score
    norm = np.linalg.norm(balance)
    
    # Phase alignment (how synchronized are the branches?)
    if norm < 1e-12:
        return 0.0
    
    normalized = balance / norm
    
    # Measure of concentration
    concentration = np.sum(normalized**2) * NUM_BRANCHES  # Max = 9 (all on one branch)
    
    # Entropy penalty (lower entropy = more singular)
    probs = np.abs(balance) / (np.sum(np.abs(balance)) + 1e-12)
    entropy = -np.sum(probs * np.log(probs + 1e-12))
    
    # Combined score
    score = concentration * (1.0 / (1.0 + norm)) - entropy
    
    return float(score)


def phase_entropy(balance: np.ndarray) -> float:
    """
    Compute the φ-weighted entropy of the balance distribution.
    
    S_φ = Σ_k w_k · p_k
    
    where p_k = |balance_k| / Σ|balance|
    
    Lower entropy indicates more concentrated (singular) states.
    
    Parameters
    ----------
    balance : np.ndarray
        9D balance vector
    
    Returns
    -------
    float
        φ-entropy value
    """
    magnitudes = np.abs(balance)
    total = np.sum(magnitudes)
    
    if total < 1e-12:
        return 1.0 / NUM_BRANCHES  # Uniform baseline
    
    probs = magnitudes / total
    
    # φ-weighted entropy (not Shannon, to avoid log)
    S_phi = np.sum(BRANCH_WEIGHTS * probs)
    
    return float(S_phi)


def compute_full_diagnostics(T: float) -> dict:
    """
    Compute all singularity diagnostics at T.
    
    Returns a dictionary with all heuristic quantities.
    """
    balance = compute_balance_vector(T)
    
    return {
        'T': T,
        's': complex(0.5, T),
        'balance_vector': balance,
        'balance_norm': float(np.linalg.norm(balance)),
        'singularity_score': singularity_score(balance),
        'phase_entropy': phase_entropy(balance),
        'dominant_branch': int(np.argmax(np.abs(balance))),
        'max_balance': float(np.max(np.abs(balance))),
    }
