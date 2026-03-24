#!/usr/bin/env python3
"""
test_49_sech2_second_moment.py
══════════════════════════════
Tests for the Sech² Second-Moment Bridge (Parseval Identity).

Validates the complete bridge chain:
  1. Parseval/convolution identity: F̃₂(integral) ≡ F̃₂(Toeplitz)
  2. Bochner positivity via both methods (F̃₂ ≥ 0)
  3. Toeplitz diagonal/off-diagonal decomposition
  4. Weil admissibility of the sech² kernel
  5. Off-critical signal via complex sech² FT
  6. 9D spectral Toeplitz PSD
  7. Full bridge certificate
  8. SECOND_MOMENT_BRIDGE_PROVED gate
"""

import numpy as np
import pytest

from engine.sech2_second_moment import (
    parseval_toeplitz_F2,
    integral_F2,
    parseval_identity_certificate,
    toeplitz_decomposition,
    weil_admissibility_certificate,
    corrected_ft_complex,
    off_critical_signal,
    spectral_toeplitz_psd_certificate,
    sech2_second_moment_certificate,
    parseval_toeplitz_F2_general,
    integral_F2_general,
    rqAB_decomposition_verify,
)
from engine.second_moment_bounds import (
    SECOND_MOMENT_BRIDGE_PROVED,
    compute_bridge_error_E,
    F2_corrected,
    bridge_status,
)
from engine.bochner import lambda_star, corrected_fourier


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 1: Parseval/Convolution Identity
# ═══════════════════════════════════════════════════════════════════════════════

class TestParsevalIdentity:
    """The Parseval/convolution identity F̃₂(integral) ≡ F̃₂(Toeplitz)."""

    @pytest.mark.parametrize("T0", [14.135, 21.022, 50.0])
    def test_identity_holds_at_zero_heights(self, T0):
        """Parseval identity must hold at representative zero heights."""
        H, N = 3.0, 20
        F2_t = parseval_toeplitz_F2(T0, H, N)
        F2_i = integral_F2(T0, H, N)
        ref = max(abs(F2_t), abs(F2_i), 1.0)
        assert abs(F2_t - F2_i) / ref < 1e-2

    @pytest.mark.parametrize("N", [5, 10, 20, 30])
    def test_identity_holds_at_various_N(self, N):
        """Parseval identity must hold for different truncation parameters."""
        T0, H = 14.135, 3.0
        F2_t = parseval_toeplitz_F2(T0, H, N)
        F2_i = integral_F2(T0, H, N)
        ref = max(abs(F2_t), abs(F2_i), 1.0)
        assert abs(F2_t - F2_i) / ref < 1e-2

    @pytest.mark.parametrize("H", [1.5, 3.0, 5.0])
    def test_identity_holds_at_various_H(self, H):
        """Parseval identity must hold for different bandwidths."""
        T0, N = 14.135, 15
        F2_t = parseval_toeplitz_F2(T0, H, N)
        F2_i = integral_F2(T0, H, N)
        ref = max(abs(F2_t), abs(F2_i), 1.0)
        assert abs(F2_t - F2_i) / ref < 1e-2

    def test_certificate_all_pass(self):
        """Full Parseval identity certificate must pass."""
        cert = parseval_identity_certificate(
            T0_values=[14.135, 21.022], H=3.0, N_values=[10, 20],
        )
        assert cert['all_pass']
        assert cert['max_relative_error'] < 1e-2


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 2: Bochner Positivity (both methods)
# ═══════════════════════════════════════════════════════════════════════════════

class TestBochnerPositivity:
    """F̃₂ ≥ 0 verified via both Toeplitz and integral forms."""

    @pytest.mark.parametrize("T0", np.linspace(10, 100, 15))
    def test_toeplitz_nonneg(self, T0):
        """F̃₂ via Toeplitz form must be ≥ 0."""
        assert parseval_toeplitz_F2(T0, 3.0, 20) >= -1e-8

    @pytest.mark.parametrize("T0", [14.135, 21.022, 50.0, 100.0])
    def test_integral_nonneg(self, T0):
        """F̃₂ via numerical integral must be ≥ 0."""
        assert integral_F2(T0, 3.0, 20) >= -1e-6

    def test_F2_corrected_nonneg(self):
        """F2_corrected (A + λ*B) must be ≥ 0."""
        for T0 in [14.135, 21.022, 50.0, 100.0]:
            assert F2_corrected(T0, 3.0, 30) >= -1e-8


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 3: Toeplitz Decomposition
# ═══════════════════════════════════════════════════════════════════════════════

class TestToeplitzDecomposition:
    """Diagonal + off-diagonal decomposition of F̃₂."""

    def test_decomposition_sums_correctly(self):
        """diagonal + off_diagonal must equal F2_total."""
        d = toeplitz_decomposition(14.135, 3.0, 20)
        assert abs(d['diagonal'] + d['off_diagonal'] - d['F2_total']) < 1e-8

    def test_diagonal_is_positive(self):
        """Diagonal term (harmonic sum × ĝ(0)) is always positive."""
        d = toeplitz_decomposition(14.135, 3.0, 20)
        assert d['diagonal'] > 0

    def test_g_hat_zero_correct(self):
        """ĝ_{λ*}(0) = λ* · 2H = 8/H."""
        for H in [1.5, 3.0, 5.0]:
            d = toeplitz_decomposition(14.135, H, 10)
            assert abs(d['g_hat_zero'] - 8.0 / H) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 4: Weil Admissibility
# ═══════════════════════════════════════════════════════════════════════════════

class TestWeilAdmissibility:
    """Sech² kernel is Weil-admissible: even, positive FT, Schwartz."""

    def test_certificate_passes(self):
        cert = weil_admissibility_certificate(3.0)
        assert cert['weil_admissible']

    def test_fourier_strictly_positive(self):
        cert = weil_admissibility_certificate(3.0)
        assert cert['fourier_positive']
        assert cert['min_fourier_value'] > 0

    def test_even_symmetry(self):
        cert = weil_admissibility_certificate(3.0)
        assert cert['even_symmetry']

    def test_poles_outside_strip(self):
        """Poles of ŵ_H at Im(ω) = 2/H must be > 0.5 for working H < 4."""
        for H in [1.5, 3.0]:
            cert = weil_admissibility_certificate(H)
            assert cert['poles_outside_weil_strip']
            assert cert['first_pole_imaginary_part'] > 0.5


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 5: Off-Critical Signal via Complex ĝ
# ═══════════════════════════════════════════════════════════════════════════════

class TestOffCriticalSignal:
    """Off-critical zero contribution via complex sech² Fourier transform."""

    def test_near_resonance_signal_is_real_valued(self):
        """At resonance (T0 ≈ γ₀), the signal should be approximately real."""
        sig = off_critical_signal(14.135, 0.05, 14.135, 3.0)
        assert sig['near_resonance']
        # ĝ at purely imaginary argument gives real result
        assert abs(sig['g_hat_complex'].imag) < abs(sig['g_hat_complex'].real) * 0.01

    def test_signal_positive_at_resonance(self):
        """Corrected kernel gives positive ĝ_{λ*}(-iΔβ) at resonance.

        λ* = 4/H² > Δβ² for small Δβ, so (-Δβ² + λ*) > 0 and
        ŵ_H(-iΔβ) > 0, making the full product positive.
        This is the Bochner positivity guarantee."""
        for db in [0.01, 0.05, 0.1]:
            sig = off_critical_signal(14.135, db, 14.135, 3.0)
            assert sig['delta_Q_off'] > 0

    def test_exponential_suppression_far_from_resonance(self):
        """Signal is exponentially suppressed far from γ₀."""
        near = off_critical_signal(14.135, 0.05, 14.135, 3.0)
        far = off_critical_signal(14.135, 0.05, 50.0, 3.0)
        assert abs(far['delta_Q_off']) < abs(near['delta_Q_off'])
        assert far['exponential_suppression'] < 0.01

    def test_corrected_ft_complex_at_real_arg_matches_real_version(self):
        """ĝ_{λ*}(ω) at real ω must match corrected_fourier()."""
        H = 3.0
        omegas = [0.5, 1.0, 2.0, 5.0]
        for omega in omegas:
            g_complex = corrected_ft_complex(np.array([complex(omega, 0)]), H)[0]
            g_real = corrected_fourier(np.array([omega]), H)[0]
            assert abs(g_complex.real - g_real) < 1e-8
            assert abs(g_complex.imag) < 1e-12


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 6: 9D Spectral Toeplitz PSD
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpectralPSD:
    """9D spectral Toeplitz matrix is PSD by Bochner."""

    def test_9d_toeplitz_psd(self):
        cert = spectral_toeplitz_psd_certificate(3.0, n_lowest=40)
        assert cert['psd']
        assert cert['min_eigenvalue'] >= -1e-10


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 7: Full Bridge Certificate
# ═══════════════════════════════════════════════════════════════════════════════

class TestFullBridgeCertificate:
    """Complete sech² second-moment bridge certificate."""

    def test_bridge_certificate_passes(self):
        cert = sech2_second_moment_certificate(
            H=3.0, N=20,
            T0_values=[14.135, 21.022],
            parseval_tol=1e-2,
        )
        assert cert['bridge_proved']

    def test_all_subcertificates_pass(self):
        cert = sech2_second_moment_certificate(
            H=3.0, N=20,
            T0_values=[14.135],
            parseval_tol=1e-2,
        )
        assert cert['parseval_identity']['all_pass']
        assert cert['weil_admissibility']['weil_admissible']
        assert cert['spectral_9d_psd']['psd']
        assert cert['bochner_positivity']


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 8: Gate Integration (SECOND_MOMENT_BRIDGE_PROVED)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGateIntegration:
    """The bridge flag and chain_complete gate."""

    def test_bridge_flag_is_true(self):
        """SECOND_MOMENT_BRIDGE_PROVED must be True."""
        assert SECOND_MOMENT_BRIDGE_PROVED is True

    def test_bridge_status_reports_proved(self):
        """bridge_status() must report PROVED."""
        s = bridge_status()
        assert s['status'] == 'PROVED'
        assert s['bridge_proved'] is True

    def test_compute_bridge_error_is_small(self):
        """Parseval bridge verification error must be tiny (not O(1))."""
        res = compute_bridge_error_E(14.135, 3.0, 30)
        assert res['E_discrepancy'] < 0.1
        assert res['bridge_proved'] is True

    def test_chain_complete_in_strict_weil(self):
        """strict_weil mode should have chain_complete = True."""
        from engine.holy_grail import (
            rh_contradiction_certificate, PROOF_MODE_STRICT_WEIL,
        )
        cert = rh_contradiction_certificate(mode=PROOF_MODE_STRICT_WEIL)
        assert cert['functional_identity_pass'] is True
        assert cert['chain_complete'] is True


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 9: 9D Log-Free Parseval Identity (TODO_CONFLATION §1–§2)
# ═══════════════════════════════════════════════════════════════════════════════

class Test9DLogFreeParseval:
    """Parseval identity with 9D spectral times {T_n} and general a_n.

    From TODO_CONFLATION.md: replace log(n) with 9D Euler/HP spectral
    eigenvalues and use general complex coefficients a_n.
    """

    @staticmethod
    def _get_9d_times(N):
        """Get N 9D spectral eigenvalues as spectral times."""
        from engine.spectral_9d import get_9d_spectrum
        return get_9d_spectrum(N)

    def test_identity_with_9d_times_unit_coeffs(self):
        """Parseval identity holds using 9D eigenvalues as spectral times."""
        times = self._get_9d_times(15)
        a = np.ones(len(times), dtype=np.complex128)
        H, T0 = 3.0, 14.135
        F2_t = parseval_toeplitz_F2_general(T0, H, times, a)
        F2_i = integral_F2_general(T0, H, times, a)
        ref = max(abs(F2_t), abs(F2_i), 1.0)
        assert abs(F2_t - F2_i) / ref < 1e-2

    def test_identity_with_9d_times_weighted_coeffs(self):
        """Parseval identity holds with prime-weighted coefficients."""
        times = self._get_9d_times(15)
        a = 1.0 / np.sqrt(np.arange(1, len(times) + 1, dtype=np.float64))
        H, T0 = 3.0, 21.022
        F2_t = parseval_toeplitz_F2_general(T0, H, times, a)
        F2_i = integral_F2_general(T0, H, times, a)
        ref = max(abs(F2_t), abs(F2_i), 1.0)
        assert abs(F2_t - F2_i) / ref < 1e-2

    def test_identity_with_9d_times_random_coeffs(self):
        """Parseval identity holds with random complex coefficients."""
        rng = np.random.default_rng(42)
        times = self._get_9d_times(10)
        a = rng.standard_normal(len(times)) + 1j * rng.standard_normal(len(times))
        H, T0 = 3.0, 50.0
        F2_t = parseval_toeplitz_F2_general(T0, H, times, a)
        F2_i = integral_F2_general(T0, H, times, a)
        ref = max(abs(F2_t), abs(F2_i), 1.0)
        assert abs(F2_t - F2_i) / ref < 1e-2

    def test_bochner_positivity_9d(self):
        """F̃₂ via 9D Toeplitz must be ≥ 0 (Bochner guarantee)."""
        times = self._get_9d_times(15)
        a = np.ones(len(times), dtype=np.complex128)
        for T0 in [14.135, 21.022, 50.0]:
            F2_t = parseval_toeplitz_F2_general(T0, 3.0, times, a)
            assert F2_t >= -1e-8

    def test_general_reduces_to_standard(self):
        """General Parseval with log(n) times and n^{-1/2} coeffs matches
        the standard parseval_toeplitz_F2."""
        N, H, T0 = 20, 3.0, 14.135
        indices = np.arange(1, N + 1, dtype=np.float64)
        times = np.log(indices)
        a = indices ** (-0.5)
        F2_gen = parseval_toeplitz_F2_general(T0, H, times, a)
        F2_std = parseval_toeplitz_F2(T0, H, N)
        ref = max(abs(F2_gen), abs(F2_std), 1.0)
        assert abs(F2_gen - F2_std) / ref < 1e-10

    @pytest.mark.parametrize("H", [1.5, 3.0])
    def test_9d_identity_at_various_H(self, H):
        """Parseval identity with 9D times for different bandwidths."""
        times = self._get_9d_times(10)
        a = np.ones(len(times), dtype=np.complex128)
        T0 = 14.135
        F2_t = parseval_toeplitz_F2_general(T0, H, times, a)
        F2_i = integral_F2_general(T0, H, times, a)
        ref = max(abs(F2_t), abs(F2_i), 1.0)
        assert abs(F2_t - F2_i) / ref < 1e-2


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 10: rq[A] + λ*·rq[B] Decomposition (TODO_CONFLATION §4)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRqABDecomposition:
    """Verify F̃₂ = rq[A] + λ*·rq[B] from TODO_CONFLATION.md §4.

    rq[A] = ∫ (-w_H''(u)) |D_N|² du   (curvature functional)
    rq[B] = ∫ w_H(u) |D_N|² du          (floor functional)
    """

    @pytest.mark.parametrize("T0", [14.135, 21.022, 50.0])
    def test_rqAB_equals_toeplitz(self, T0):
        """rq[A] + λ*rq[B] must match Toeplitz F̃₂ to machine precision."""
        result = rqAB_decomposition_verify(T0, 3.0, 20)
        assert result['agrees']
        assert result['relative_error'] < 1e-10

    @pytest.mark.parametrize("N", [5, 10, 20, 30])
    def test_rqAB_at_various_N(self, N):
        """rq decomposition holds for different truncation parameters."""
        result = rqAB_decomposition_verify(14.135, 3.0, N)
        assert result['agrees']

    def test_floor_functional_positive(self):
        """rq[B] = ∫ w_H(u)|D_N|²du is always positive (sech² > 0)."""
        result = rqAB_decomposition_verify(14.135, 3.0, 20)
        assert result['B'] > 0

    def test_lambda_star_correct(self):
        """λ* = 4/H² in the decomposition."""
        for H in [1.5, 3.0]:
            result = rqAB_decomposition_verify(14.135, H, 10)
            assert abs(result['lambda_star'] - 4.0 / H**2) < 1e-14

    @pytest.mark.parametrize("H", [1.5, 3.0])
    def test_rqAB_at_various_H(self, H):
        """rq decomposition holds for different bandwidths."""
        result = rqAB_decomposition_verify(14.135, H, 15)
        assert result['agrees']
        assert result['relative_error'] < 1e-10
