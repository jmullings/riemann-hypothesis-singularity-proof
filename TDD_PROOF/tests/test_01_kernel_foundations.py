"""
================================================================================
test_01_kernel_foundations.py — Tier 1: Sech² Kernel Identities
================================================================================

Verifies the fundamental mathematical properties of the sech² kernel
that underpin the entire proof framework:

  1. sech²(x) = 1/cosh²(x) with correct values and symmetry
  2. w_H(t) smoothing kernel and its curvature weight W_curv(t)
  3. Fourier transforms: ŵ_H(ω) > 0 for all ω (Bochner precondition)
  4. Schwartz-class membership: all seminorms finite
  5. Integration by parts consistency
================================================================================
"""

import pytest
import numpy as np

from engine.kernel import (
    sech2, w_H, fourier_w_H, W_curv, fourier_W_curv,
    w_H_deriv2, schwartz_seminorm,
)


# ─────────────── §1 — SECH² IDENTITY ────────────────────────────────────────

class TestSech2Identity:
    """Core sech²(x) = 1/cosh²(x) mathematical properties."""

    def test_sech2_at_zero(self):
        assert sech2(0.0) == pytest.approx(1.0, abs=1e-15)

    def test_sech2_symmetry(self):
        for x in [0.5, 1.0, 2.0, 5.0, 10.0]:
            assert sech2(x) == pytest.approx(sech2(-x), rel=1e-14)

    def test_sech2_known_values(self):
        """sech²(x) = 1/cosh²(x) at specific points."""
        for x in [0.5, 1.0, 2.0, 3.0]:
            expected = 1.0 / np.cosh(x)**2
            assert sech2(x) == pytest.approx(expected, rel=1e-14)

    def test_sech2_positivity(self):
        """sech²(x) > 0 for all finite x."""
        x = np.linspace(-50, 50, 10000)
        vals = sech2(x)
        assert np.all(vals > 0)

    def test_sech2_bounded_by_one(self):
        """0 < sech²(x) ≤ 1 always."""
        x = np.linspace(-50, 50, 10000)
        vals = sech2(x)
        assert np.all(vals <= 1.0 + 1e-15)
        assert np.all(vals > 0)

    def test_sech2_decay(self):
        """sech²(x) → 0 exponentially as |x| → ∞."""
        assert sech2(10.0) < 1e-8
        assert sech2(20.0) < 1e-16

    def test_sech2_large_argument_stability(self):
        """No overflow for very large arguments."""
        assert sech2(350.0) >= 0
        assert sech2(500.0) >= 0
        assert np.isfinite(sech2(500.0))

    def test_sech2_array_input(self):
        x = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        vals = sech2(x)
        assert len(vals) == 5
        assert vals[2] == pytest.approx(1.0, abs=1e-15)


# ─────────────── §2 — SMOOTHING KERNEL w_H ──────────────────────────────────

class TestSmoothingKernel:
    """w_H(t, H) = sech²(t/H) smoothing kernel."""

    @pytest.mark.parametrize("H", [0.5, 1.0, 2.0, 3.0, 5.0, 10.0])
    def test_w_H_at_zero(self, H):
        assert w_H(0.0, H) == pytest.approx(1.0, abs=1e-15)

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_w_H_symmetry(self, H):
        t = np.linspace(-10*H, 10*H, 1000)
        vals = w_H(t, H)
        vals_neg = w_H(-t, H)
        np.testing.assert_allclose(vals, vals_neg, atol=1e-14)

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_w_H_positivity(self, H):
        t = np.linspace(-20*H, 20*H, 5000)
        vals = w_H(t, H)
        assert np.all(vals > 0)

    def test_w_H_scaling(self):
        """w_H(t) for larger H is wider (slower decay)."""
        assert w_H(5.0, 1.0) < w_H(5.0, 3.0)


# ─────────────── §3 — CURVATURE WEIGHT W_curv ───────────────────────────────

class TestCurvatureWeight:
    """W_curv(t) = -w_H''(t) curvature weight."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_W_curv_at_zero_positive(self, H):
        """W_curv(0) = 2/H² > 0 (from -d²/dt² sech²(t/H) at t=0)."""
        assert W_curv(0.0, H) > 0

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_W_curv_has_negative_region(self, H):
        """The Bochner obstruction: W_curv goes negative for |t| > t*."""
        t = np.linspace(-6*H, 6*H, 5000)
        vals = W_curv(t, H)
        assert np.min(vals) < 0, "W_curv should have a negative region"

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_W_curv_symmetry(self, H):
        t = np.linspace(0.01, 6*H, 500)
        np.testing.assert_allclose(W_curv(t, H), W_curv(-t, H), atol=1e-13)


# ─────────────── §4 — FOURIER TRANSFORMS ────────────────────────────────────

class TestFourierTransforms:
    """ŵ_H(ω) = πH²ω/sinh(πHω/2) — positive for all ω."""

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_fourier_w_H_at_zero(self, H):
        """ŵ_H(0) = 2H (L'Hôpital limit)."""
        val = fourier_w_H(np.array([0.0]), H)[0]
        assert val == pytest.approx(2.0 * H, rel=1e-10)

    @pytest.mark.parametrize("H", [1.0, 2.0, 3.0, 5.0])
    def test_fourier_w_H_strictly_positive(self, H):
        """ŵ_H(ω) > 0 for all ω — the BOCHNER PRECONDITION."""
        omega = np.linspace(-50, 50, 5000)
        vals = fourier_w_H(omega, H)
        assert np.all(vals > 0), (
            f"ŵ_H must be strictly positive; min={np.min(vals)}"
        )

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_fourier_w_H_symmetry(self, H):
        omega = np.linspace(0.01, 30, 500)
        fwd = fourier_w_H(omega, H)
        bwd = fourier_w_H(-omega, H)
        np.testing.assert_allclose(fwd, bwd, rtol=1e-12)

    @pytest.mark.parametrize("H", [1.0, 3.0])
    def test_fourier_W_curv_nonneg(self, H):
        """Ŵ_curv(ω) = ω²·ŵ_H(ω) ≥ 0 for all ω."""
        omega = np.linspace(-50, 50, 5000)
        vals = fourier_W_curv(omega, H)
        assert np.all(vals >= -1e-15)


# ─────────────── §5 — SCHWARTZ CLASS ────────────────────────────────────────

class TestSchwartzClass:
    """w_H(t) ∈ S(ℝ) — all Schwartz seminorms finite."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_schwartz_seminorms_finite(self, H):
        """sup_t |t^m · d^k w_H| < ∞ for m, k ≤ 3."""
        for m in range(4):
            for k in range(4):
                val = schwartz_seminorm(H, m, k)
                assert np.isfinite(val), f"Seminorm ({m},{k}) not finite"
                assert val >= 0

    @pytest.mark.parametrize("H", [0.5, 1.0, 3.0, 10.0])
    def test_schwartz_zeroth_order(self, H):
        """s_{0,0} = sup|w_H(t)| = w_H(0) = 1."""
        val = schwartz_seminorm(H, 0, 0)
        assert val == pytest.approx(1.0, rel=0.01)


# ─────────────── §6 — INTEGRATION BY PARTS CONSISTENCY ──────────────────────

class TestIntegrationByParts:
    """W_curv = -w_H'' consistency check via numerical differentiation."""

    @pytest.mark.parametrize("H", [1.0, 3.0, 5.0])
    def test_W_curv_matches_negative_second_derivative(self, H):
        """W_curv(t) should equal -w_H''(t) = w_H_deriv2 cast properly."""
        t = np.linspace(-4*H, 4*H, 500)
        analytic = W_curv(t, H)
        deriv2 = w_H_deriv2(t, H)
        # W_curv = -w_H'' means W_curv = -deriv2
        np.testing.assert_allclose(analytic, -deriv2, rtol=1e-10)
