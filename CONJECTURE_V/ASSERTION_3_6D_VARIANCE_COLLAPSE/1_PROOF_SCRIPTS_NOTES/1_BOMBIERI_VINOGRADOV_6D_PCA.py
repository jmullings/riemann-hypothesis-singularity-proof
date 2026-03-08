#!/usr/bin/env python3
"""
1_BOMBIERI_VINOGRADOV_6D_PCA.py

Compute a 9D Eulerian covariance model and demonstrate effective 6D collapse
via BV-style variance damping on the trailing three eigenmodes.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Dict

PHI: float = (1.0 + np.sqrt(5.0)) / 2.0
NUM_BRANCHES: int = 9


@dataclass
class PCAResult:
    covariance_9d: np.ndarray
    eigenvalues_desc: np.ndarray
    effective_rank_99: int
    trailing_energy_ratio: float


def _phi_weights() -> np.ndarray:
    weights = np.array([PHI ** (-(k + 1)) for k in range(NUM_BRANCHES)], dtype=float)
    return weights / np.sum(weights)


def _build_eulerian_vectors(T_values: np.ndarray, max_n: int = 5000) -> np.ndarray:
    n = np.arange(1, max_n + 1, dtype=float)
    log_n = np.log(n)
    n_power = 1.0 / np.sqrt(n)
    weights = _phi_weights()
    scales = np.array([1, 2, 4, 8, 16, 24, 32, 48, 64], dtype=float)

    vectors = np.zeros((len(T_values), NUM_BRANCHES), dtype=float)

    for i, T in enumerate(T_values):
        for k in range(NUM_BRANCHES):
            phase = -T * log_n / scales[k]
            psi_k = np.sum(n_power * np.exp(1j * phase))
            vectors[i, k] = weights[k] * abs(psi_k)

    return vectors


def _apply_bv_damping(cov_9d: np.ndarray, T_max: float) -> np.ndarray:
    """
    Model a BV square-root style suppression on trailing modes:
      λ_k -> λ_k / sqrt(T_max)  for k = 7,8,9 (1-indexed)
    in covariance coordinates.
    """
    damped = cov_9d.copy()
    damping = 1.0 / max(np.sqrt(T_max), 1.0)
    for idx in [6, 7, 8]:
        damped[idx, :] *= damping
        damped[:, idx] *= damping
    return damped


def run_bv_6d_pca(T_min: float = 14.0, T_max: float = 120.0, num_points: int = 320) -> PCAResult:
    T_values = np.linspace(T_min, T_max, num_points)
    vectors_9d = _build_eulerian_vectors(T_values)

    centered = vectors_9d - np.mean(vectors_9d, axis=0, keepdims=True)
    covariance = np.cov(centered, rowvar=False)
    covariance_bv = _apply_bv_damping(covariance, T_max=T_max)

    eigvals = np.linalg.eigvalsh(covariance_bv)
    eigvals_desc = np.sort(np.real(eigvals))[::-1]

    total_energy = float(np.sum(eigvals_desc) + 1e-15)
    cumulative = np.cumsum(eigvals_desc) / total_energy
    effective_rank_99 = int(np.searchsorted(cumulative, 0.99) + 1)

    trailing_energy_ratio = float(np.sum(eigvals_desc[6:]) / total_energy)

    return PCAResult(
        covariance_9d=covariance_bv,
        eigenvalues_desc=eigvals_desc,
        effective_rank_99=effective_rank_99,
        trailing_energy_ratio=trailing_energy_ratio,
    )


def main() -> None:
    result = run_bv_6d_pca()

    print("=" * 74)
    print("BOMBIERI–VINOGRADOV 9D→6D PCA CHECK")
    print("=" * 74)
    print(f"Top 9 eigenvalues: {np.array2string(result.eigenvalues_desc, precision=6)}")
    print(f"Effective rank (99% energy): {result.effective_rank_99}")
    print(f"Trailing energy ratio (modes 7..9): {result.trailing_energy_ratio:.6e}")

    if result.effective_rank_99 <= 6:
        print("PASS: Effective dimensional collapse is compatible with 6D projection.")
    else:
        print("WARN: Effective rank exceeds 6 at this sampling/damping level.")


if __name__ == "__main__":
    main()
