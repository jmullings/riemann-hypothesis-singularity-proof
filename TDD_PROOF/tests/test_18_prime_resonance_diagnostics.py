"""
================================================================================
test_18_prime_resonance_diagnostics.py — FFT Prime Resonance Diagnostics
================================================================================

Tests for the FFT-based spectral resonance detector in
engine/spectral_tools.py:

  §1  FFT structural: finite output, correct shapes, non-negative amplitudes
  §2  Prime window: log(p) windows are defined within frequency range
  §3  Honest limits: no prime extraction assertion

These are EXPLORATORY diagnostics — they set up the infrastructure for
checking whether the polymeric spectral density has structure near log(p)
frequencies, but do not assert it as a theorem.
================================================================================
"""

import pytest
import numpy as np

from engine.spectral_tools import spectral_resonance_frequencies
from engine.hilbert_polya import get_poly_spectrum


# ─────────────────────────────────────────────────────────────────────────────
# Helper: standard polymeric spectrum for diagnostics
# ─────────────────────────────────────────────────────────────────────────────

def _diagnostic_spectrum():
    """300-level polymeric spectrum for resonance testing."""
    return get_poly_spectrum(n=300, mu0=0.1, p_interval=(0.2, 6.0)).real


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — FFT STRUCTURAL CHECKS
# ═══════════════════════════════════════════════════════════════════════════════

class TestFFTStructure:
    """The FFT resonance detector produces well-formed output."""

    def test_fft_runs_and_is_finite(self):
        """FFT of spectral density produces finite values."""
        evals = _diagnostic_spectrum()
        freqs, amp = spectral_resonance_frequencies(
            evals, E_min=0.5, E_max=6.0, n_E=4096, sigma=0.05
        )
        assert np.all(np.isfinite(freqs))
        assert np.all(np.isfinite(amp))

    def test_amplitudes_nonnegative(self):
        """|ρ̂(ω)| ≥ 0 (amplitudes are absolute values)."""
        evals = _diagnostic_spectrum()
        _, amp = spectral_resonance_frequencies(
            evals, E_min=0.5, E_max=6.0, n_E=4096, sigma=0.05
        )
        assert np.all(amp >= 0)

    def test_frequency_axis_nonnegative(self):
        """rfftfreq returns non-negative frequencies."""
        evals = _diagnostic_spectrum()
        freqs, _ = spectral_resonance_frequencies(
            evals, E_min=0.5, E_max=6.0, n_E=4096, sigma=0.05
        )
        assert np.all(freqs >= 0)

    def test_output_shapes_consistent(self):
        """freqs and amplitudes have matching shapes."""
        evals = _diagnostic_spectrum()
        freqs, amp = spectral_resonance_frequencies(
            evals, E_min=0.5, E_max=6.0, n_E=4096, sigma=0.05
        )
        assert freqs.shape == amp.shape
        # rfft of length n_E → n_E//2 + 1
        assert len(freqs) == 4096 // 2 + 1

    def test_dc_component_near_zero(self):
        """Mean-subtracted FFT → DC (ω=0) component ≈ 0."""
        evals = _diagnostic_spectrum()
        _, amp = spectral_resonance_frequencies(
            evals, E_min=0.5, E_max=6.0, n_E=4096, sigma=0.05
        )
        # The DC component should be near zero since we subtract the mean
        assert amp[0] < 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — PRIME WINDOW DEFINITION
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrimeWindowDefinition:
    """Define log-prime windows in frequency space (structural, not asserting peaks)."""

    def test_prime_window_is_defined_not_enforced(self):
        """
        log(p) for small primes lies within the FFT frequency range.
        This defines the diagnostic region but does NOT assert actual peaks.
        """
        primes = [2, 3, 5, 7]
        logs = np.log(primes)
        evals = _diagnostic_spectrum()
        freqs, _ = spectral_resonance_frequencies(
            evals, E_min=0.5, E_max=6.0, n_E=4096, sigma=0.05
        )
        assert logs[0] > freqs[0]   # ln(2) ≈ 0.69 > 0
        assert logs[-1] < freqs[-1]  # ln(7) ≈ 1.95 < max freq

    def test_frequency_resolution_adequate(self):
        """Frequency resolution is fine enough to resolve log-prime spacing.
        log(3) - log(2) ≈ 0.405, so Δf < 0.405 is sufficient."""
        evals = _diagnostic_spectrum()
        freqs, _ = spectral_resonance_frequencies(
            evals, E_min=0.5, E_max=6.0, n_E=4096, sigma=0.05
        )
        df = freqs[1] - freqs[0]
        log_prime_gap = np.log(3) - np.log(2)  # ≈ 0.405
        assert df < log_prime_gap, f"Δf={df:.3f} must resolve log-prime gap {log_prime_gap:.3f}"


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — HONEST LIMITS
# ═══════════════════════════════════════════════════════════════════════════════

class TestHonestLimitsPrimeResonance:
    """Prime resonance diagnostics are exploratory, not proof."""

    def test_we_do_not_assert_prime_extraction(self):
        """
        Spectral FFT diagnostics do NOT assert that primes are encoded
        in the polymeric spectrum or that Spec(H) = {γ_n}.
        """
        assert True  # documentary

    def test_peaks_not_required(self):
        """No test requires FFT peaks at log(p) — that is a research question."""
        assert True  # documentary
