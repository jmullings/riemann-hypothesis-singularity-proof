"""
================================================================================
test_16_spectral_density.py — Spectral Density & Counting Diagnostics
================================================================================

Tests for the spectral-density and counting-function utilities in
engine/spectral_tools.py:

  §1  Gaussian spectral density: non-negativity, normalisation, total weight
  §2  Numeric counting function: monotonicity, boundary values, BK fluctuation
  §3  Honest limits: diagnostics are diagnostics, not proof

================================================================================
"""

import pytest
import numpy as np

from engine.spectral_tools import gaussian_spectral_density, numeric_counting_function
from engine.hilbert_polya import get_poly_spectrum, berry_keating_counting


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — GAUSSIAN SPECTRAL DENSITY
# ═══════════════════════════════════════════════════════════════════════════════

class TestGaussianSpectralDensity:
    """Gaussian-broadened density of states from discrete eigenvalues."""

    def test_nonnegative(self):
        """ρ(E) ≥ 0 everywhere (sum of Gaussians)."""
        evals = [1.0, 2.0, 3.0]
        E = np.linspace(0.0, 4.0, 200)
        rho = gaussian_spectral_density(evals, E, sigma=0.1)
        assert np.all(rho >= -1e-14)

    def test_single_delta_normalisation(self):
        """Single eigenvalue → ∫ρ dE ≈ 1."""
        evals = [1.5]
        E = np.linspace(0.0, 3.0, 1000)
        rho = gaussian_spectral_density(evals, E, sigma=0.05)
        integral = np.trapz(rho, E)
        assert abs(integral - 1.0) < 1e-2

    def test_total_weight_equals_number_of_levels(self):
        """∫ρ dE ≈ n for n eigenvalues (wide enough grid)."""
        evals = np.linspace(1.0, 10.0, 20)
        E = np.linspace(0.0, 12.0, 2000)
        rho = gaussian_spectral_density(evals, E, sigma=0.1)
        integral = np.trapz(rho, E)
        assert abs(integral - len(evals)) < 1e-1

    def test_peak_near_eigenvalue(self):
        """ρ(E) peaks near the eigenvalue location."""
        evals = [5.0]
        E = np.linspace(3.0, 7.0, 500)
        rho = gaussian_spectral_density(evals, E, sigma=0.1)
        peak_idx = np.argmax(rho)
        assert abs(E[peak_idx] - 5.0) < 0.05

    def test_narrower_sigma_higher_peak(self):
        """Smaller σ → taller, narrower peak."""
        evals = [3.0]
        E = np.linspace(2.0, 4.0, 500)
        rho_wide = gaussian_spectral_density(evals, E, sigma=0.2)
        rho_narrow = gaussian_spectral_density(evals, E, sigma=0.05)
        assert np.max(rho_narrow) > np.max(rho_wide)

    def test_output_shape(self):
        """Output shape matches E_grid."""
        evals = [1.0, 2.0]
        E = np.linspace(0.0, 3.0, 123)
        rho = gaussian_spectral_density(evals, E, sigma=0.1)
        assert rho.shape == (123,)


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — NUMERIC COUNTING FUNCTION & BK FLUCTUATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestNumericCountingFunction:
    """N(E) = #{E_j ≤ E} staircase counting function."""

    def test_below_all_eigenvalues(self):
        """N(E) = 0 below all eigenvalues."""
        evals = [2.0, 3.0, 5.0]
        assert numeric_counting_function(evals, 1.0) == 0

    def test_above_all_eigenvalues(self):
        """N(E) = n above all eigenvalues."""
        evals = [2.0, 3.0, 5.0]
        assert numeric_counting_function(evals, 6.0) == 3

    def test_monotone_nondecreasing(self):
        """N(E) is monotone non-decreasing."""
        evals = np.sort(np.random.default_rng(42).uniform(1.0, 10.0, 50))
        E_vals = np.linspace(0.0, 12.0, 200)
        counts = [numeric_counting_function(evals, e) for e in E_vals]
        for i in range(1, len(counts)):
            assert counts[i] >= counts[i - 1]

    def test_steps_at_eigenvalues(self):
        """N(E) increments by 1 at each simple eigenvalue."""
        evals = [1.0, 2.0, 3.0]
        # Just below → just above each eigenvalue
        assert numeric_counting_function(evals, 0.99) == 0
        assert numeric_counting_function(evals, 1.01) == 1
        assert numeric_counting_function(evals, 2.01) == 2
        assert numeric_counting_function(evals, 3.01) == 3


class TestCountingFluctuations:
    """N_numeric consistency and BK comparison."""

    def test_numeric_counting_consistent(self):
        """N_numeric(E_max) = n for the full spectrum."""
        evals = get_poly_spectrum(n=200, mu0=0.1, p_interval=(0.2, 5.0)).real
        E_max = float(evals[-1]) + 1.0
        N = numeric_counting_function(evals, E_max)
        assert N == len(evals)

    def test_BK_scale_mismatch_documented(self):
        """
        HONEST: The polymeric eigenvalues are Sturm–Liouville energies on
        a discretisation grid — NOT Riemann zeros.  N_BK(E) uses the von
        Mangoldt smooth term which counts imaginary parts of ζ zeros up
        to height E.  Direct comparison requires parameter tuning that
        has NOT been done.  This test documents the mismatch.
        """
        evals = get_poly_spectrum(n=50, mu0=0.1, p_interval=(0.2, 5.0)).real
        E = float(evals[-1])
        N_num = numeric_counting_function(evals, E)
        N_bk = berry_keating_counting(E)
        # N_num is 50, N_bk is ~thousands → large mismatch expected
        assert N_bk > N_num, "BK counting should exceed polymeric level count (scale mismatch)"


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — HONEST LIMITS
# ═══════════════════════════════════════════════════════════════════════════════

class TestHonestLimitsSpectralDensity:
    """Spectral diagnostics are exploratory, not proof."""

    def test_density_does_not_encode_primes(self):
        """ρ(E) is a smoothing tool — no claim about prime structure."""
        assert True  # documentary

    def test_counting_does_not_prove_rh(self):
        """N_numeric vs N_BK is a sanity check, not a proof step."""
        assert True  # documentary
