"""
================================================================================
test_17_gue_spacing.py — GUE-Style Spacing Diagnostics
================================================================================

Tests for unfolded nearest-neighbour spacing statistics from
engine/spectral_tools.py:

  §1  Spacing sanity: positivity, mean = 1, variance finite
  §2  Operator-specific: polymeric spectrum spacings
  §3  Honest limits: no GUE enforcement

These are DIAGNOSTIC tests — they verify the spacing machinery works
and produce sensible output, but do not assert GUE statistics as a theorem.
================================================================================
"""

import pytest
import numpy as np

from engine.spectral_tools import unfolded_spacings
from engine.hilbert_polya import get_poly_spectrum


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — SPACING SANITY CHECKS
# ═══════════════════════════════════════════════════════════════════════════════

class TestUnfoldedSpacingSanity:
    """Basic structural properties of unfolded spacings."""

    def test_spacings_positive_uniform(self):
        """Spacings from a strictly increasing sequence are > 0."""
        evals = np.linspace(1.0, 10.0, 50)
        s = unfolded_spacings(evals)
        assert np.all(s > 0)

    def test_mean_spacing_is_one(self):
        """Mean unfolded spacing = 1 by construction."""
        evals = np.linspace(1.0, 10.0, 50)
        s = unfolded_spacings(evals)
        np.testing.assert_allclose(s.mean(), 1.0, atol=1e-12)

    def test_output_length(self):
        """len(spacings) = len(evals) - 1."""
        evals = np.array([1.0, 3.0, 4.0, 8.0, 9.5])
        s = unfolded_spacings(evals)
        assert len(s) == len(evals) - 1

    def test_uniform_spectrum_constant_spacings(self):
        """Uniformly spaced eigenvalues → all spacings = 1."""
        evals = np.arange(0.0, 20.0)
        s = unfolded_spacings(evals)
        np.testing.assert_allclose(s, 1.0, atol=1e-12)

    def test_variance_finite(self):
        """Spacing variance is finite for any reasonable spectrum."""
        rng = np.random.default_rng(99)
        evals = np.sort(rng.uniform(0.0, 100.0, 200))
        s = unfolded_spacings(evals)
        assert np.isfinite(np.var(s))

    def test_unsorted_input_handled(self):
        """Unsorted input is internally sorted."""
        evals = [5.0, 1.0, 3.0, 9.0, 2.0]
        s = unfolded_spacings(evals)
        assert np.all(s > 0)
        np.testing.assert_allclose(s.mean(), 1.0, atol=1e-12)

    def test_degenerate_mean_gap(self):
        """All-equal eigenvalues → zero spacings (no divide-by-zero)."""
        evals = np.ones(10)
        s = unfolded_spacings(evals)
        np.testing.assert_allclose(s, 0.0, atol=1e-14)


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — POLYMERIC SPECTRUM SPACINGS
# ═══════════════════════════════════════════════════════════════════════════════

class TestPolySpacings:
    """Apply spacing analysis to the polymeric operator spectrum."""

    def test_spacings_positive(self):
        """Polymeric eigenvalue spacings are positive."""
        evals = get_poly_spectrum(n=200, mu0=0.1, p_interval=(0.2, 5.0)).real
        s = unfolded_spacings(evals)
        assert np.all(s > 0)

    def test_mean_spacing_is_one(self):
        """Mean unfolded spacing = 1 for polymeric spectrum."""
        evals = get_poly_spectrum(n=200, mu0=0.1, p_interval=(0.2, 5.0)).real
        s = unfolded_spacings(evals)
        assert abs(s.mean() - 1.0) < 0.1

    def test_no_exact_degeneracies(self):
        """Polymeric operator has no degenerate eigenvalues."""
        evals = get_poly_spectrum(n=100, mu0=0.1, p_interval=(0.2, 5.0)).real
        gaps = np.diff(np.sort(evals))
        assert np.all(gaps > 1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — HONEST LIMITS
# ═══════════════════════════════════════════════════════════════════════════════

class TestHonestLimitsGUE:
    """GUE diagnostics are exploratory, not assertions."""

    def test_no_gue_assertion(self):
        """We do NOT assert that the spectrum follows GUE statistics."""
        assert True  # documentary
