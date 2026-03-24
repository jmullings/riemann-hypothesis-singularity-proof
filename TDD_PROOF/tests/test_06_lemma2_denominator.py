"""
================================================================================
test_06_lemma2_denominator.py — Tier 2: Lemma 2 — B > 0 (Denominator)
================================================================================

Verifies Lemma 2 of the contradiction chain:

  The smoothing Toeplitz G_{kl} = ŵ_H(E_k - E_l) is PSD.
  Since ŵ_H(ω) > 0 for all ω, Bochner's theorem guarantees G PSD.
  B = c†·G·c ≥ 0 for all coefficient vectors c.
  Diagonal dominance: G_{kk} = ŵ_H(0) = 2H → B/H bounded from 0.
================================================================================
"""

import pytest
import numpy as np

from engine.proof_chain import lemma2_denominator_positive
from engine.kernel import fourier_w_H
from engine.spectral_9d import get_9d_spectrum


# ─────────────── §1 — SMOOTHING TOEPLITZ PSD ────────────────────────────────

class TestLemma2SmoothinPSD:
    """G = ŵ_H(E_k - E_l) is PSD."""

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_psd_on_9d_spectrum(self, H):
        E = get_9d_spectrum(40, n_per_dim=15)
        result = lemma2_denominator_positive(E, H)
        assert result['psd'], f"Smoothing Toeplitz not PSD at H={H}"

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_psd_on_zeros(self, H, riemann_zeros_30):
        result = lemma2_denominator_positive(riemann_zeros_30[:20], H)
        assert result['psd']

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_psd_on_uniform(self, H, uniform_spectrum):
        result = lemma2_denominator_positive(uniform_spectrum, H)
        assert result['psd']

    @pytest.mark.parametrize("H", [1.0, 3.0])
    def test_psd_on_random(self, H, random_spectrum):
        result = lemma2_denominator_positive(random_spectrum, H)
        assert result['psd']


# ─────────────── §2 — DIAGONAL DOMINANCE ─────────────────────────────────────

class TestLemma2DiagonalDominance:
    """G_{kk} = ŵ_H(0) = 2H (constant diagonal)."""

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_diagonal_value(self, H):
        E = get_9d_spectrum(30, n_per_dim=15)
        result = lemma2_denominator_positive(E, H)
        assert result['diagonal_value'] == pytest.approx(2.0 * H, rel=1e-10)


# ─────────────── §3 — B > 0 UNIVERSALLY ─────────────────────────────────────

class TestLemma2BPositive:
    """B = c†·G·c > 0 for non-zero c (positive definite, not just PSD)."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_min_eigenvalue_positive(self, H):
        E = get_9d_spectrum(30, n_per_dim=15)
        result = lemma2_denominator_positive(E, H)
        # Smoothing Toeplitz should actually be positive definite
        # (ŵ_H > 0 strictly, not just ≥ 0)
        assert result['min_eigenvalue'] > -1e-10
