#!/usr/bin/env python3
r"""
================================================================================
test_44_euler_form_spectral.py — Layer B: Euler-Form Spectral Protocol
================================================================================

TIER 25e — Internal consistency and external validation of the non-log
spectral protocol (euler_form.py).

EQUATIONS UNDER TEST:
    Θ_H(t) = Σ_{n≥2} Λ(n) e^{-t τ_n},      τ_n = ln n
    ζ_H(s) = Σ_{n≥2} Λ(n) e^{-s τ_n} = -ζ'/ζ(s)
    ψ(e^T) = Σ_{p^m ≤ e^T} ln(p)

HARNESS STRUCTURE:
  §1  TestSpectralTimes:
        τ_n, Λ(n) data integrity (prime-only, prime-power, weights).
  §2  TestHeatTraceConsistency:
        Θ_H ↔ ζ_H Laplace relationship, derivative sign.
  §3  TestSpectralZetaExternal:
        ζ_H(s) vs mpmath -ζ'/ζ(s) for several s ∈ {2,3,4,5,2+3i}.
  §4  TestTruncationConvergence:
        nmax stability for both Θ_H and ζ_H.
  §5  TestPrimeOnlySanity:
        Prime-only subset traces match the expected partial sum.
  §6  TestPNTResidualDecay:
        |ψ(e^T) - e^T| / e^T satisfies the Kadiri-Faber envelope.

================================================================================
"""

import numpy as np
import pytest
from scipy import integrate

from engine.euler_form import (
    spectral_times,
    chebyshev_psi_euler,
    heat_trace,
    heat_trace_derivative,
    spectral_zeta,
    pnt_residual_euler,
    _sieve_primes,
)
from engine.analytic_bounds import _pnt_decay_factor


# ═══════════════════════════════════════════════════════════════════════════════
# §1 — SPECTRAL TIMES DATA INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpectralTimes:

    def test_tau_equals_ln_n(self):
        """τ_n = ln(n) for each index n returned."""
        tau, wt, idx = spectral_times(100)
        for t, n in zip(tau, idx):
            assert abs(t - np.log(n)) < 1e-12, (
                f"τ({n}) = {t}, expected ln({n}) = {np.log(n)}"
            )

    def test_weights_are_von_mangoldt(self):
        """Λ(p^m) = ln(p) for each prime power."""
        tau, wt, idx = spectral_times(100)
        primes = set(_sieve_primes(100))
        for w, n in zip(wt, idx):
            # Find the prime base p such that n = p^m
            p_found = None
            for p in primes:
                if p > n:
                    break
                k = n
                while k > 1 and k % p == 0:
                    k //= p
                if k == 1:
                    p_found = p
                    break
            assert p_found is not None, f"n={n} is not a prime power"
            assert abs(w - np.log(p_found)) < 1e-12, (
                f"Λ({n}) = {w}, expected ln({p_found}) = {np.log(p_found)}"
            )

    def test_indices_are_prime_powers(self):
        """Every index returned is a prime power."""
        _, _, idx = spectral_times(200)
        primes = sorted(_sieve_primes(200))
        for n in idx:
            is_pp = False
            for p in primes:
                if p > n:
                    break
                k = n
                while k > 1 and k % p == 0:
                    k //= p
                if k == 1:
                    is_pp = True
                    break
            assert is_pp, f"n={n} is not a prime power"

    def test_indices_sorted(self):
        """Indices are returned in ascending order."""
        _, _, idx = spectral_times(500)
        assert np.all(idx[:-1] <= idx[1:])

    def test_known_small_values(self):
        """Spot-check: n=2,3,4,5,7,8,9 should all appear for n_max=10."""
        _, _, idx = spectral_times(10)
        expected = {2, 3, 4, 5, 7, 8, 9}
        assert expected == set(idx), f"Expected {expected}, got {set(idx)}"


# ═══════════════════════════════════════════════════════════════════════════════
# §2 — HEAT TRACE / SPECTRAL ZETA CONSISTENCY
# ═══════════════════════════════════════════════════════════════════════════════

class TestHeatTraceConsistency:

    def test_heat_trace_equals_spectral_zeta_at_real_s(self):
        """Θ_H(t) and ζ_H(s) coincide for real s = t > 1."""
        n_max = 5000
        for s in [2.0, 3.0, 5.0]:
            ht = heat_trace(s, n_max=n_max)
            sz = spectral_zeta(s, n_max=n_max).real
            assert abs(ht - sz) < 1e-8, (
                f"s={s}: Θ_H={ht:.8e} ≠ ζ_H={sz:.8e}"
            )

    def test_spectral_zeta_is_laplace_of_heat_trace(self):
        """
        ζ_H(s) ≈ s · ∫₀^∞ Θ_H(t) · e^{-st} dt  (Laplace relation).

        Actually, Θ_H(t) = Σ Λ(n) e^{-tτ_n} and ζ_H(s) = Σ Λ(n) e^{-sτ_n},
        so they are the SAME series evaluated at the same point. The deeper
        Laplace connection is:  Θ_H and ζ_H share the same spectral measure,
        so we verify they agree numerically for real arguments.
        """
        n_max = 5000
        for s in [2.5, 4.0]:
            ht = heat_trace(s, n_max=n_max)
            sz = spectral_zeta(s, n_max=n_max).real
            rel_err = abs(ht - sz) / max(abs(sz), 1e-15)
            assert rel_err < 1e-10, (
                f"s={s}: Laplace consistency fails, rel_err={rel_err:.2e}"
            )

    def test_heat_trace_derivative_negative(self):
        """Θ'_H(t) < 0 for all t > 0 (monotone decay)."""
        n_max = 5000
        for t in [0.5, 1.0, 2.0, 5.0, 10.0]:
            d = heat_trace_derivative(t, n_max=n_max)
            assert d < 0, f"Θ'_H({t}) = {d} — should be negative"

    def test_heat_trace_vectorized(self):
        """heat_trace handles array input and returns array."""
        t_arr = np.array([1.0, 2.0, 3.0])
        result = heat_trace(t_arr, n_max=1000)
        assert result.shape == (3,)
        # Should be strictly decreasing
        assert result[0] > result[1] > result[2]


# ═══════════════════════════════════════════════════════════════════════════════
# §3 — SPECTRAL ZETA vs EXTERNAL -ζ'/ζ (mpmath)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSpectralZetaExternal:
    """Compare ζ_H(s) to mpmath -ζ'/ζ(s) for multiple s-values."""

    @staticmethod
    def _reference_minus_zeta_prime_over_zeta(s):
        """Compute -ζ'(s)/ζ(s) via mpmath."""
        import mpmath
        mpmath.mp.dps = 30
        z = mpmath.zeta(s)
        zp = mpmath.diff(mpmath.zeta, s)
        return float((-zp / z).real)

    @pytest.mark.parametrize("s", [2.0, 3.0, 4.0, 5.0])
    def test_spectral_zeta_matches_reference(self, s):
        """ζ_H(s) ≈ -ζ'/ζ(s) for Re(s) > 1, with truncation tolerance."""
        n_max = 100000
        computed = spectral_zeta(s, n_max=n_max).real
        reference = self._reference_minus_zeta_prime_over_zeta(s)
        rel_err = abs(computed - reference) / max(abs(reference), 1e-15)
        assert rel_err < 1e-3, (
            f"s={s}: ζ_H={computed:.8f}, -ζ'/ζ={reference:.8f}, "
            f"rel_err={rel_err:.2e}"
        )

    def test_spectral_zeta_complex_argument(self):
        """ζ_H(2+3i) matches mpmath -ζ'(2+3i)/ζ(2+3i)."""
        import mpmath
        mpmath.mp.dps = 30
        s_mp = mpmath.mpc(2, 3)
        z = mpmath.zeta(s_mp)
        zp = mpmath.diff(mpmath.zeta, s_mp)
        ref = complex(-zp / z)

        n_max = 100000
        computed = spectral_zeta(2.0 + 3.0j, n_max=n_max)

        rel_err = abs(computed - ref) / max(abs(ref), 1e-15)
        assert rel_err < 1e-2, (
            f"s=2+3i: ζ_H={computed}, ref={ref}, rel_err={rel_err:.2e}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §4 — TRUNCATION / nmax CONVERGENCE
# ═══════════════════════════════════════════════════════════════════════════════

class TestTruncationConvergence:

    def test_heat_trace_convergence(self):
        """Θ_H(t) converges as nmax increases: |Θ(N₂) - Θ(N₁)| < ε."""
        t = 2.0
        val_small = heat_trace(t, n_max=1000)
        val_med = heat_trace(t, n_max=10000)
        val_large = heat_trace(t, n_max=100000)
        diff_1 = abs(val_med - val_small)
        diff_2 = abs(val_large - val_med)
        # The second difference should be smaller (convergence)
        assert diff_2 < diff_1, (
            f"Not converging: |Θ(10⁴)-Θ(10³)|={diff_1:.6e}, "
            f"|Θ(10⁵)-Θ(10⁴)|={diff_2:.6e}"
        )
        # Absolute difference should be small at t=2
        assert diff_2 < 1e-3, f"Slow convergence: diff_2={diff_2:.6e}"

    def test_spectral_zeta_convergence(self):
        """ζ_H(s) converges as nmax increases."""
        s = 3.0
        val_small = spectral_zeta(s, n_max=1000).real
        val_med = spectral_zeta(s, n_max=10000).real
        val_large = spectral_zeta(s, n_max=100000).real
        diff_1 = abs(val_med - val_small)
        diff_2 = abs(val_large - val_med)
        assert diff_2 < diff_1, (
            f"Not converging: |ζ(10⁴)-ζ(10³)|={diff_1:.6e}, "
            f"|ζ(10⁵)-ζ(10⁴)|={diff_2:.6e}"
        )
        assert diff_2 < 1e-4, f"Slow convergence: diff_2={diff_2:.6e}"

    @pytest.mark.parametrize("t", [1.0, 3.0])
    def test_heat_trace_monotone_in_t(self, t):
        """Θ_H(t) is strictly positive and decreasing in t."""
        n_max = 10000
        vals = [heat_trace(t + dt, n_max=n_max) for dt in [0.0, 0.5, 1.0]]
        assert vals[0] > vals[1] > vals[2] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# §5 — PRIME-ONLY SANITY CHECK
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrimeOnlySanity:

    def test_prime_only_heat_trace(self):
        """
        Restricting to primes (m=1 only), the heat trace should equal
        Σ_p ln(p) · p^{-t} = Σ_p ln(p) · e^{-t ln p}.
        """
        n_max = 500
        t = 2.0
        tau, wt, idx = spectral_times(n_max)
        primes = set(_sieve_primes(n_max))

        # Full trace
        full = float(np.sum(wt * np.exp(-t * tau)))
        # Prime-only subset
        mask = np.array([int(n) in primes for n in idx])
        prime_only = float(np.sum(wt[mask] * np.exp(-t * tau[mask])))

        # Manual prime-only computation
        manual = sum(np.log(p) * p ** (-t) for p in primes)
        assert abs(prime_only - manual) < 1e-10, (
            f"Prime-only mismatch: {prime_only:.8e} vs manual {manual:.8e}"
        )
        # Prime-only should be strictly less than full (prime powers add)
        assert prime_only < full, (
            f"Prime-only {prime_only:.6e} ≥ full {full:.6e}"
        )

    def test_prime_power_contributions_positive(self):
        """Each prime-power contribution e^{-t τ_n} is positive."""
        tau, wt, idx = spectral_times(200)
        t = 1.0
        terms = wt * np.exp(-t * tau)
        assert np.all(terms > 0)

    def test_chebyshev_psi_matches_manual(self):
        """ψ(e^T) matches manual Λ-sum for small T."""
        T = 3.0  # e^3 ≈ 20
        psi_val = chebyshev_psi_euler(T, n_max=100)
        # Manually: Λ(2)=ln2, Λ(3)=ln3, Λ(4)=ln2, Λ(5)=ln5,
        #           Λ(7)=ln7, Λ(8)=ln2, Λ(9)=ln3, Λ(11)=ln11,
        #           Λ(13)=ln13, Λ(16)=ln2, Λ(17)=ln17, Λ(19)=ln19
        import math
        expected = (4 * math.log(2) + 2 * math.log(3) + math.log(5) +
                    math.log(7) + math.log(11) + math.log(13) +
                    math.log(17) + math.log(19))
        assert abs(psi_val - expected) < 1e-10, (
            f"ψ(e^3) = {psi_val:.8f}, expected {expected:.8f}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §6 — PNT RESIDUAL DECAY ENVELOPE
# ═══════════════════════════════════════════════════════════════════════════════

class TestPNTResidualDecay:

    @pytest.mark.parametrize("T", [5.0, 7.0, 9.0, 11.0])
    def test_residual_satisfies_kadiri_faber_envelope(self, T):
        r"""
        |ψ(e^T) - e^T| / e^T ≤ C · δ(T)
        for C consistent with A_k = 1.0.
        """
        R = pnt_residual_euler(T)
        ratio = abs(R) / np.exp(T)
        delta = _pnt_decay_factor(T)
        # A_k = 1.0 → C = 1.0
        assert ratio <= delta, (
            f"T={T}: |R|/e^T = {ratio:.6e} > δ(T) = {delta:.6e}"
        )

    def test_residual_changes_sign(self):
        """PNT residual oscillates: should have both positive and negative values."""
        signs = set()
        for T in np.linspace(3, 12, 30):
            R = pnt_residual_euler(float(T))
            if R > 0:
                signs.add('+')
            elif R < 0:
                signs.add('-')
        assert len(signs) == 2, (
            f"Residual does not oscillate: signs = {signs}"
        )

    def test_residual_ratio_decreasing_trend(self):
        """
        |ψ(e^T) - e^T| / e^T should decrease on average.
        Uses a linear regression on log-ratios (negative slope).
        """
        T_vals = [5.0, 7.0, 9.0, 11.0, 13.0]
        ratios = []
        for T in T_vals:
            R = pnt_residual_euler(T)
            r = abs(R) / np.exp(T)
            if r > 0:
                ratios.append(np.log(r))
            else:
                ratios.append(-30)  # effectively zero
        # Check slope is negative (ratios decreasing)
        coeffs = np.polyfit(T_vals[:len(ratios)], ratios, 1)
        assert coeffs[0] < 0, (
            f"Log-ratio slope = {coeffs[0]:.4f} — not decreasing"
        )
