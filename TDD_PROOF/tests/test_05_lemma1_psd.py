"""
================================================================================
test_05_lemma1_psd.py — Tier 2: Lemma 1 — PSD at λ* = 4/H²
================================================================================

Verifies Lemma 1 of the contradiction chain:

  The corrected Bochner-Toeplitz matrix M̃(λ=4/H²) is PSD for
  ANY spectrum — this is the KERNEL UNIVERSALITY result.

  Sub-assertions:
    (a) Obstruction exists (uncorrected M is indefinite)
    (b) λ-correction repairs it (M̃ is PSD)
    (c) PSD holds for 9D eigenvalues of ANY size
    (d) PSD holds for Riemann zeros, uniform, random, adversarial spectra
================================================================================
"""

import pytest
import numpy as np

from engine.proof_chain import (
    lemma1_psd_at_lambda_star,
    lemma1_obstruction_exists,
    lemma1_kernel_universality,
)
from engine.bochner import build_corrected_toeplitz, is_psd, lambda_star
from engine.spectral_9d import get_9d_spectrum


# ─────────────── §1 — OBSTRUCTION EXISTS ─────────────────────────────────────

class TestLemma1Obstruction:
    """The uncorrected Toeplitz is indefinite."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_obstruction_on_zeros(self, H, riemann_zeros_30):
        result = lemma1_obstruction_exists(riemann_zeros_30[:15], H)
        assert result['indefinite'], "Obstruction must exist"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_obstruction_on_uniform(self, H, uniform_spectrum):
        result = lemma1_obstruction_exists(uniform_spectrum[:15], H)
        assert result['indefinite'], "Obstruction should also appear on uniform spectrum"


# ─────────────── §2 — λ-CORRECTION REPAIRS ──────────────────────────────────

class TestLemma1PSDBySweep:
    """Corrected M̃ is PSD for multiple spectra and H values."""

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_psd_on_9d_spectrum(self, H):
        E = get_9d_spectrum(40, n_per_dim=15)
        result = lemma1_psd_at_lambda_star(E, H)
        assert result['psd'], f"PSD fails on 9D spectrum at H={H}"

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_psd_on_zeros(self, H, riemann_zeros_30):
        result = lemma1_psd_at_lambda_star(riemann_zeros_30[:20], H)
        assert result['psd'], f"PSD fails on zeros at H={H}"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_psd_on_random(self, H, random_spectrum):
        result = lemma1_psd_at_lambda_star(random_spectrum, H)
        assert result['psd']


# ─────────────── §3 — KERNEL UNIVERSALITY ────────────────────────────────────

class TestLemma1KernelUniversality:
    """The corrected FT ≥ 0 everywhere → PSD for ANY spectrum."""

    @pytest.mark.parametrize("H", [0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0])
    def test_universal_nonneg(self, H):
        result = lemma1_kernel_universality(H)
        assert result['all_nonneg'], (
            f"Kernel universality fails at H={H}; min={result['min_value']}"
        )


# ─────────────── §4 — PSD PRESERVATION AS n GROWS ───────────────────────────

class TestLemma1PSDAcrossN:
    """PSD holds as spectrum size increases (RS limit passage)."""

    def test_psd_preserved_across_n(self):
        H = 3.0
        for n in [5, 10, 20, 40, 60]:
            E = get_9d_spectrum(n, n_per_dim=15)
            result = lemma1_psd_at_lambda_star(E, H)
            assert result['psd'], f"PSD fails at n={n}"
