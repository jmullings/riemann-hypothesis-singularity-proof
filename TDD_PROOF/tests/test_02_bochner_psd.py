"""
================================================================================
test_02_bochner_psd.py — Tier 1: Bochner PSD Verification
================================================================================

Verifies the corrected Toeplitz matrix M̃ is PSD at λ* = 4/H²:

  1. λ* = 4/H² is correctly computed
  2. Corrected FT: f(ω) = (ω²+4/H²)·ŵ_H(ω) ≥ 0 for all ω (KERNEL IDENTITY)
  3. Corrected Toeplitz M̃ is PSD for various spectra
  4. Uncorrected curvature Toeplitz is INDEFINITE (obstruction exists)
  5. Kernel universality: PSD holds for ANY spectrum
================================================================================
"""

import pytest
import numpy as np

from engine.bochner import (
    lambda_star, corrected_fourier, build_corrected_toeplitz,
    build_curvature_toeplitz, min_eigenvalue, is_psd, eigenspectrum,
    F2_corrected, rayleigh_quotient,
)
from engine.kernel import fourier_w_H


# ─────────────── §1 — λ* = 4/H² ────────────────────────────────────────────

class TestLambdaStar:
    """Critical correction parameter λ* = 4/H²."""

    @pytest.mark.parametrize("H,expected", [
        (1.0, 4.0), (2.0, 1.0), (3.0, 4.0/9), (5.0, 0.16),
    ])
    def test_lambda_star_values(self, H, expected):
        assert lambda_star(H) == pytest.approx(expected, rel=1e-12)

    @pytest.mark.parametrize("H", [0.5, 1.0, 2.0, 3.0, 5.0, 10.0])
    def test_lambda_star_positive(self, H):
        assert lambda_star(H) > 0

    def test_lambda_star_decreasing_in_H(self):
        """λ* = 4/H² is monotone decreasing."""
        Hs = [0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
        vals = [lambda_star(h) for h in Hs]
        for i in range(1, len(vals)):
            assert vals[i] < vals[i-1]


# ─────────────── §2 — CORRECTED FOURIER NON-NEGATIVITY ──────────────────────

class TestCorrectedFourier:
    """f(ω) = (ω²+4/H²)·ŵ_H(ω) ≥ 0 — the kernel identity."""

    @pytest.mark.parametrize("H", [0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0])
    def test_corrected_fourier_nonneg(self, H):
        """THE KERNEL IDENTITY: f(ω) ≥ 0 for all ω ∈ ℝ."""
        omega = np.linspace(-50, 50, 5000)
        f = corrected_fourier(omega, H)
        assert np.all(f >= -1e-15), (
            f"Corrected FT must be ≥ 0; min = {np.min(f)} at H={H}"
        )

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_corrected_fourier_at_zero(self, H):
        """f(0) = (0 + 4/H²)·ŵ_H(0) = (4/H²)·2H = 8/H."""
        val = corrected_fourier(np.array([0.0]), H)
        expected = (4.0 / H**2) * 2.0 * H
        assert float(val[0]) == pytest.approx(expected, rel=1e-10)

    @pytest.mark.parametrize("H", [1.0, 3.0])
    def test_corrected_fourier_symmetry(self, H):
        omega = np.linspace(0.01, 40, 500)
        fwd = corrected_fourier(omega, H)
        bwd = corrected_fourier(-omega, H)
        np.testing.assert_allclose(fwd, bwd, rtol=1e-12)


# ─────────────── §3 — BOCHNER OBSTRUCTION EXISTS ────────────────────────────

class TestObstructionExists:
    """Uncorrected curvature Toeplitz is INDEFINITE."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_curvature_toeplitz_indefinite(self, H, riemann_zeros_30):
        """The motivation for λ-correction: uncorrected M has negative eigenvalue."""
        M = build_curvature_toeplitz(riemann_zeros_30[:15], H)
        me = min_eigenvalue(M)
        assert me < -1e-10, "Obstruction must exist for the correction to matter"


# ─────────────── §4 — CORRECTED TOEPLITZ PSD ────────────────────────────────

class TestCorrectedToeplitzPSD:
    """Corrected M̃ = f(E_k-E_l) is PSD for all tested spectra."""

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_psd_on_riemann_zeros(self, H, riemann_zeros_30):
        M = build_corrected_toeplitz(riemann_zeros_30[:20], H)
        assert is_psd(M), f"Corrected Toeplitz not PSD on zeros at H={H}"

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_psd_on_uniform_grid(self, H, uniform_spectrum):
        M = build_corrected_toeplitz(uniform_spectrum, H)
        assert is_psd(M), f"Corrected Toeplitz not PSD on uniform at H={H}"

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_psd_on_random_points(self, H, random_spectrum):
        M = build_corrected_toeplitz(random_spectrum, H)
        assert is_psd(M), f"Corrected Toeplitz not PSD on random at H={H}"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_psd_on_clustered_points(self, H):
        """Adversarial: tightly clustered points (worst case for conditioning)."""
        E = np.sort(np.concatenate([
            np.linspace(14.0, 14.5, 10),
            np.linspace(50.0, 50.5, 10),
        ]))
        M = build_corrected_toeplitz(E, H)
        assert is_psd(M)

    @pytest.mark.parametrize("H", [1.0, 3.0])
    def test_psd_on_irrational_spacing(self, H):
        """Arithmetic progression with irrational ratio."""
        E = np.array([10.0 + k * np.pi for k in range(25)])
        M = build_corrected_toeplitz(E, H)
        assert is_psd(M)


# ─────────────── §5 — KERNEL UNIVERSALITY ────────────────────────────────────

class TestKernelUniversality:
    """Corrected Toeplitz is PSD for ANY spectrum (Bochner + non-neg FT)."""

    @pytest.mark.parametrize("seed", range(5))
    def test_psd_random_seeds(self, seed):
        """PSD holds across 5 independent random spectra."""
        rng = np.random.RandomState(seed + 100)
        E = np.sort(rng.uniform(1, 200, 30))
        M = build_corrected_toeplitz(E, H=3.0)
        assert is_psd(M), f"PSD failed for seed={seed}"

    def test_psd_single_point(self):
        """Degenerate case: 1×1 matrix is always PSD."""
        M = build_corrected_toeplitz(np.array([14.135]), H=3.0)
        assert is_psd(M)

    def test_psd_two_points(self):
        """2×2 case."""
        M = build_corrected_toeplitz(np.array([14.135, 21.022]), H=3.0)
        assert is_psd(M)


# ─────────────── §6 — FUNCTIONAL EVALUATION ─────────────────────────────────

class TestFunctionalEvaluation:
    """F̃₂ corrected functional and Rayleigh quotient."""

    def test_F2_corrected_nonneg(self):
        """F̃₂ ≥ 0 at λ = λ* for several T₀ values."""
        for T0 in [14.0, 21.0, 50.0, 100.0]:
            val = F2_corrected(T0, H=3.0, N=15)
            assert val >= -1e-8, f"F̃₂ < 0 at T₀={T0}: {val}"

    def test_rayleigh_denominator_positive(self):
        """B(T₀) > 0 always (smoothing integral of |D_N|² > 0)."""
        for T0 in [14.0, 21.0, 50.0]:
            r = rayleigh_quotient(T0, H=3.0, N=15)
            assert r['B'] > 0, f"B ≤ 0 at T₀={T0}"
