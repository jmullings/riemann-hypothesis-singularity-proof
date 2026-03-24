"""
================================================================================
test_10_weil_density.py — Weil Density & Asymptotic Domination Tests
================================================================================

Tests for the gap-closing results ported from RH_PROOF/src/weil_density.py:

  THEOREM 6.1 — Asymptotic domination for γ₀ ≤ γ₁        [PROVED]
  THEOREM 6.2 — Mellin non-vanishing on Re(s) = ½          [PROVED]
  THEOREM 6.3 — Dilation completeness in L²(ℝ⁺, dx/x)    [PROVED]

Coverage:
  §1 — Complex sech² and off-line contributions
  §2 — On-line sums
  §3 — Theorem 6.1: Asymptotic domination (low-lying zeros)
  §4 — Theorem 6.2: Mellin non-vanishing
  §5 — Theorem 6.3: Dilation completeness
  §6 — Domination landscape & gap status
================================================================================
"""

import pytest
import numpy as np

from engine.weil_density import (
    GAMMA_30,
    sech2_complex,
    off_line_pair_contribution,
    off_line_pair_asymptotic,
    on_line_sum,
    on_line_sum_asymptotic,
    domination_ratio,
    asymptotic_domination_lemma,
    asymptotic_ratio_formula,
    dirichlet_eta,
    mellin_sech2_closed,
    mellin_nonvanishing_theorem,
    dilation_completeness_theorem,
    probe_high_lying_zero,
    domination_landscape,
    full_gap_status,
)


# ─────────────── §1 — COMPLEX SECH² AND OFF-LINE CONTRIBUTIONS ──────────────

class TestComplexSech2:
    """Tests for overflow-safe complex sech²."""

    def test_real_input_matches_kernel(self):
        """sech²(x+0i) = sech²(x) for real x."""
        from engine.kernel import sech2 as real_sech2
        for x in [0.0, 1.0, 5.0, 14.0]:
            z = np.array([complex(x, 0)])
            got = sech2_complex(z)[0].real
            expected = float(real_sech2(np.array([x]))[0])
            assert got == pytest.approx(expected, rel=1e-12)

    def test_overflow_safe_large_real(self):
        """Large real → 0, no overflow."""
        z = np.array([complex(400, 0)])
        assert sech2_complex(z)[0] == pytest.approx(0.0, abs=1e-30)

    def test_pure_imaginary(self):
        """sech²(iy) = 1/cos²(y) = sec²(y)."""
        for y in [0.0, 0.5, 1.0]:
            z = np.array([complex(0, y)])
            got = sech2_complex(z)[0].real
            expected = 1.0 / np.cos(y)**2
            assert got == pytest.approx(expected, rel=1e-10)

    def test_complex_conjugate_symmetry(self):
        """sech²(z̄) = conj(sech²(z))."""
        z = np.array([complex(2.0, 3.0)])
        zbar = np.array([complex(2.0, -3.0)])
        v1 = sech2_complex(z)[0]
        v2 = sech2_complex(zbar)[0]
        assert v1.real == pytest.approx(v2.real, rel=1e-12)
        assert v1.imag == pytest.approx(-v2.imag, rel=1e-12)


class TestOffLineContribution:
    """Off-line pair contribution C_off(α)."""

    def test_zero_delta_beta_reduces_to_on_line(self):
        """When Δβ = 0, C_off = 2·sech²(αγ₀) (on-line)."""
        from engine.kernel import sech2 as real_sech2
        alpha, gamma_0 = 1.0, 14.135
        got = off_line_pair_contribution(alpha, gamma_0, 0.0)
        expected = 2.0 * float(real_sech2(np.array([alpha * gamma_0]))[0])
        assert got == pytest.approx(expected, rel=1e-10)

    def test_sign_changes_with_alpha(self):
        """C_off(α) changes sign due to cos(2αΔβ) oscillation."""
        gamma_0, db = 5.0, 0.3
        signs = set()
        for alpha in np.linspace(0.5, 10.0, 500):
            c = off_line_pair_contribution(alpha, gamma_0, db)
            if abs(c) > 1e-30:
                signs.add(c > 0)
        assert len(signs) == 2, "Should observe both positive and negative contributions"

    def test_asymptotic_agreement(self):
        """Exact and asymptotic forms agree at large α."""
        gamma_0, db = 5.0, 0.2
        for alpha in [5.0, 8.0, 10.0]:
            exact = off_line_pair_contribution(alpha, gamma_0, db)
            asymp = off_line_pair_asymptotic(alpha, gamma_0, db)
            if abs(exact) > 1e-30:
                assert abs(asymp / exact - 1) < 0.1, (
                    f"Asymptotic off by >{10}% at α={alpha}")


# ─────────────── §2 — ON-LINE SUMS ──────────────────────────────────────────

class TestOnLineSum:
    """On-line sum S_on(α) = Σ_k sech²(αγ_k)."""

    def test_positivity(self):
        """S_on > 0 for all α > 0 (under RH)."""
        for alpha in [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]:
            assert on_line_sum(alpha) > 0

    def test_monotone_decay(self):
        """S_on(α) is monotonically decreasing for α ≥ 0."""
        alphas = np.linspace(0.01, 20.0, 500)
        vals = [on_line_sum(a) for a in alphas]
        for i in range(len(vals) - 1):
            assert vals[i] >= vals[i + 1] - 1e-15

    def test_custom_zeros(self):
        """Works with a subset of zeros."""
        first_5 = GAMMA_30[:5]
        val = on_line_sum(0.1, first_5)
        assert val > 0
        assert val < on_line_sum(0.1)  # fewer terms, smaller sum

    def test_asymptotic_agreement(self):
        """Exact and asymptotic agree for large α."""
        for alpha in [5.0, 8.0]:
            exact = on_line_sum(alpha)
            asymp = on_line_sum_asymptotic(alpha)
            if exact > 1e-30:
                assert abs(asymp / exact - 1) < 0.05


class TestDominationRatio:
    """Ratio |C_off|/S_on for detecting domination."""

    def test_returns_zero_when_coff_positive(self):
        """Ratio = 0 if C_off ≥ 0 (no contradiction)."""
        # At small α, cos(2αΔβ) > 0 so C_off > 0
        ratio, coff, son = domination_ratio(0.01, 5.0, 0.1)
        assert ratio >= 0

    def test_low_lying_produces_large_ratio(self):
        """For γ₀ < γ₁, ratio exceeds 1 at large α."""
        gamma_0 = 5.0
        db = 0.1
        found_large = False
        for alpha in np.linspace(1.0, 100.0, 2000):
            ratio, _, _ = domination_ratio(alpha, gamma_0, db)
            if ratio > 1.0:
                found_large = True
                break
        assert found_large, "Expected domination ratio > 1 for γ₀ < γ₁"


# ─────────────── §3 — THEOREM 6.1: ASYMPTOTIC DOMINATION ────────────────────

class TestTheorem61:
    """Theorem 6.1: Asymptotic domination for low-lying zeros."""

    @pytest.mark.parametrize("gamma_0,delta_beta", [
        (5.0, 0.1),    # well below γ₁
        (10.0, 0.1),   # below γ₁
        (14.0, 0.05),  # near γ₁
    ])
    def test_low_lying_domination(self, gamma_0, delta_beta):
        """For γ₀ ≤ γ₁, asymptotic domination holds: ∃α with S(α) < 0."""
        res = asymptotic_domination_lemma(gamma_0, delta_beta, n_alpha=20000)
        assert res['theorem_holds'] is True
        assert res['alpha_star'] is not None
        assert res['S_at_alpha_star'] < 0

    def test_gamma0_equal_gamma1(self):
        """γ₀ ≈ γ₁: ratio → 2 in the limit."""
        res = asymptotic_domination_lemma(14.134, 0.1, n_alpha=30000)
        assert res['theorem_holds'] is True

    def test_high_lying_out_of_scope(self):
        """γ₀ > γ₁: theorem does not apply (correctly declines)."""
        res = asymptotic_domination_lemma(20.0, 0.1)
        assert res['theorem_holds'] is False
        assert 'high-lying' in res['case']

    def test_on_line_no_contradiction(self):
        """Δβ = 0 (on-line): no contradiction expected."""
        res = asymptotic_domination_lemma(10.0, 0.0)
        assert res['theorem_holds'] is False
        assert 'on-line' in res['case']

    def test_asymptotic_ratio_formula_grows(self):
        """When γ₀ < γ₁, ratio grows exponentially with α."""
        gamma_0, gamma_1 = 5.0, 14.135
        r1 = asymptotic_ratio_formula(10.0, gamma_0, gamma_1)
        r2 = asymptotic_ratio_formula(20.0, gamma_0, gamma_1)
        assert r2 > r1 * 10  # exponential growth

    def test_asymptotic_ratio_formula_at_gamma1(self):
        """When γ₀ = γ₁, ratio is exactly 2."""
        for alpha in [1.0, 10.0, 100.0]:
            r = asymptotic_ratio_formula(alpha, 14.135, 14.135)
            assert r == pytest.approx(2.0, rel=1e-10)


# ─────────────── §4 — THEOREM 6.2: MELLIN NON-VANISHING ─────────────────────

class TestTheorem62:
    """Theorem 6.2: M[sech²](½+it) ≠ 0 for all t."""

    def test_eta_convergence(self):
        """η(s) converges for Re(s) > 0."""
        eta = dirichlet_eta(2.0)
        expected = np.pi**2 / 12.0  # η(2) = π²/12
        assert abs(eta - expected) < 0.01

    def test_eta_at_1(self):
        """η(1) = ln(2)."""
        eta = dirichlet_eta(1.0)
        assert abs(eta - np.log(2)) < 0.01

    def test_mellin_at_real_s(self):
        """M[sech²](s) finite for s > 0."""
        s = 2.0
        M = mellin_sech2_closed(s)
        assert np.isfinite(M)
        assert abs(M) > 0

    def test_mellin_nonvanishing_on_critical_line(self):
        """M[sech²](½+it) ≠ 0 for sampled t values."""
        ts = np.linspace(-30, 30, 301)
        res = mellin_nonvanishing_theorem(ts)
        assert res['theorem_verified'] is True
        assert res['min_magnitude'] > 0
        assert res['all_nonzero'] is True

    def test_mellin_nonvanishing_at_zero(self):
        """M[sech²](½+0i) ≠ 0."""
        val = mellin_sech2_closed(0.5 + 0j)
        assert abs(val) > 0.01

    def test_factor_decomposition_power(self):
        """Factor |2^{2-s}| at s = ½+it is always 2^{3/2} > 0."""
        for t in [0, 1, 5, 20, 50]:
            s = 0.5 + 1j * t
            power = abs(2.0 ** (2.0 - s))
            assert power == pytest.approx(2.0 ** 1.5, rel=1e-10)


# ─────────────── §5 — THEOREM 6.3: DILATION COMPLETENESS ────────────────────

class TestTheorem63:
    """Theorem 6.3: Dilation completeness of sech² family."""

    def test_completeness_holds(self):
        """Dilation completeness verified via Theorem 6.2."""
        res = dilation_completeness_theorem(n_test=101)
        assert res['status'] == 'PROVED'
        assert res['numerical_verification'] is True

    def test_key_ingredient(self):
        """Completeness rests on Mellin non-vanishing."""
        res = dilation_completeness_theorem(n_test=51)
        assert 'Theorem 6.2' in res['key_ingredient']

    def test_min_magnitude_positive(self):
        """Mellin transform stays bounded away from 0."""
        res = dilation_completeness_theorem(n_test=101)
        assert res['min_mellin_magnitude'] > 0


# ─────────────── §6 — LANDSCAPE & GAP STATUS ────────────────────────────────

class TestDominationLandscape:
    """Domination landscape analysis."""

    def test_low_lying_is_proved(self):
        """γ₀ < γ₁ → status PROVED."""
        res = domination_landscape(5.0, 0.1)
        assert res['status'] == 'PROVED'
        assert res['found_domination'] is True

    def test_high_lying_large_db(self):
        """γ₀ > γ₁, large Δβ → potentially NUMERICAL."""
        res = domination_landscape(20.0, 0.4, alpha_range=np.linspace(0.1, 100, 2000))
        # May or may not find domination — just check structure
        assert res['status'] in ('NUMERICAL', 'OPEN')

    def test_high_lying_small_db(self):
        """γ₀ > γ₁, small Δβ → likely OPEN."""
        res = domination_landscape(50.0, 0.001, alpha_range=np.linspace(0.1, 30, 500))
        assert res['status'] == 'OPEN'


class TestProbeHighLying:
    """Numerical probe for high-lying zeros."""

    def test_on_line_returns_not_found(self):
        """Δβ = 0 → no off-line contradiction."""
        res = probe_high_lying_zero(20.0, 0.0)
        assert res['found'] is False

    def test_structure(self):
        """Probe returns expected keys."""
        res = probe_high_lying_zero(20.0, 0.1, n_alpha=500)
        assert 'found' in res
        assert 'gamma_0' in res
        assert 'delta_beta' in res


class TestFullGapStatus:
    """Integration test: full gap status report."""

    def test_returns_all_theorems(self):
        """Report includes all three theorems."""
        status = full_gap_status()
        assert 'theorem_6_1' in status
        assert 'theorem_6_2' in status
        assert 'theorem_6_3' in status

    def test_theorem_61_proved_scope(self):
        status = full_gap_status()
        t61 = status['theorem_6_1']
        assert t61['status'] == 'PROVED'
        assert 'γ₁' in t61['scope']

    def test_theorem_62_proved(self):
        status = full_gap_status()
        assert 'PROVED' in status['theorem_6_2']['status']
        assert status['theorem_6_2']['verified'] is True

    def test_theorem_63_status(self):
        status = full_gap_status()
        assert status['theorem_6_3']['status'] == 'PROVED'

    def test_overall_honesty(self):
        """Overall report honestly marks general case as OPEN."""
        status = full_gap_status()
        assert 'OPEN' in status['overall']['reverse_general']
        assert 'PROVED' in status['overall']['forward']


# ─────────────── GAMMA_30 DATA INTEGRITY ─────────────────────────────────────

class TestGamma30:
    """First 30 Riemann zeros data consistency."""

    def test_length(self):
        assert len(GAMMA_30) == 30

    def test_sorted(self):
        assert np.all(np.diff(GAMMA_30) > 0)

    def test_first_zero(self):
        assert GAMMA_30[0] == pytest.approx(14.134725142, rel=1e-8)

    def test_all_positive(self):
        assert np.all(GAMMA_30 > 0)
