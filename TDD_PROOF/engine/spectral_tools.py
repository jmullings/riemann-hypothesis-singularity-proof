"""
================================================================================
spectral_tools.py — Spectral Density & Diagnostic Utilities
================================================================================

Provides tools for analysing discrete operator spectra:

  1. Gaussian spectral density  ρ(E) from eigenvalues
  2. Numerical counting function  N(E) = #{E_j ≤ E}
  3. Unfolded nearest-neighbour spacings  s_j
  4. FFT-based spectral resonance frequencies

These are DIAGNOSTIC utilities — they do not prove RH or assert zeta-zero
structure. They provide the controlled objects needed for trace-formula and
prime-sensitivity analysis under TDD.
================================================================================
"""

import numpy as np


def gaussian_spectral_density(evals, E_grid, sigma):
    """
    Smooth spectral density from discrete eigenvalues using
    Gaussian broadening:

      ρ(E) = Σ_j (1 / (√(2π) σ)) exp(-(E - E_j)² / (2 σ²))

    Parameters:
        evals  : 1D array of eigenvalues (real)
        E_grid : 1D grid of energies
        sigma  : smoothing width > 0

    Returns:
        ρ(E_grid) as 1D array, always ≥ 0.
    """
    evals = np.asarray(evals, dtype=float)
    E = np.asarray(E_grid, dtype=float)
    sigma = float(sigma)
    diff = E[:, None] - evals[None, :]
    kernel = np.exp(-0.5 * (diff / sigma) ** 2) / (np.sqrt(2 * np.pi) * sigma)
    return kernel.sum(axis=1)


def numeric_counting_function(evals, E):
    """
    Numerical spectral counting function:

      N_numeric(E) = #{E_j ≤ E}

    for a sorted real eigenvalue array.
    """
    evals = np.sort(np.asarray(evals, dtype=float))
    E = float(E)
    return int(np.searchsorted(evals, E, side="right"))


def unfolded_spacings(evals):
    """
    Compute unfolded nearest-neighbour spacings:

      s_j = (E_{j+1} - E_j) / mean_gap

    for a sorted array of eigenvalues. The mean spacing is normalised
    to 1 by construction.
    """
    evals = np.sort(np.asarray(evals, dtype=float))
    gaps = np.diff(evals)
    if len(gaps) == 0 or (mean_gap := gaps.mean()) <= 0:
        return gaps * 0.0
    return gaps / mean_gap


def spectral_resonance_frequencies(evals, E_min, E_max, n_E, sigma):
    """
    Compute FFT of the smoothed spectral density:

      ρ(E)  →  ρ̂(ω)  via real FFT

    Returns:
        (freqs, amplitudes) — frequency axis and |ρ̂(ω)|.
    """
    E_grid = np.linspace(E_min, E_max, n_E)
    rho = gaussian_spectral_density(evals, E_grid, sigma=sigma)
    hat_rho = np.fft.rfft(rho - rho.mean())
    freqs = np.fft.rfftfreq(n_E, d=(E_grid[1] - E_grid[0]))
    return freqs, np.abs(hat_rho)
