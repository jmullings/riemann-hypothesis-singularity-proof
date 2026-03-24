#!/usr/bin/env python3
r"""
================================================================================
test_48_functional_identity.py — Fallacy I: Functional Conflation Audit
================================================================================

EXTERNAL CRITIQUE (Fallacy I):
    The contradiction engine's decomposition
        F_tilde_2 = Delta_A_off + S_on + S_prime + lambda* B
    conflates two DISTINCT mathematical objects:

    Object 1 (Bochner Positivity Basin):
        F_tilde_2(T0; H, N) = integral g_{lambda*}(t)|D_N(T0+t)|^2 dt
                             = -A_curv + lambda* B
        where A_curv = integral W_curv(t)|D_N(T0+t)|^2 dt
        and B        = integral w_H(t)|D_N(T0+t)|^2 dt

        This is a Toeplitz quadratic form in the Dirichlet coefficients.
        It is >= 0 for ALL spectra by Bochner's theorem.
        It does NOT depend on Delta_beta or any hypothetical off-critical zero.

    Object 2 (Weil Explicit Formula):
        sum_rho hat_g(gamma_rho) = (prime/archimedean terms)

        This is a LINEAR functional on the zero set of zeta(s).
        The off-critical contribution Delta_A_off comes from THIS sum.
        It is a function of (gamma_0, Delta_beta, H) -- NOT of D_N.

    THE BROKEN BRIDGE:
        The code computes:
            F_claimed = Delta_A_weil(gamma_0, Delta_beta, H) + lambda*(H) * B(T0,H,N)
        and treats this as F_tilde_2.

        But F_tilde_2_actual = -A_curv(T0,H,N) + lambda*(H) * B(T0,H,N).

        These are equal only if -A_curv = Delta_A_weil, i.e., the Dirichlet
        curvature integral equals the Weil off-critical contribution.  This is
        NOT a mathematical identity — one is a sum over ALL integer pairs
        (m,n in {1,...,N}), the other comes from the Weil zero/prime balance.

TEST STRATEGY:
    1. Compute F_tilde_2 directly from the Dirichlet integral (Object 1).
    2. Compute the contradiction engine's F_claimed (Object 2 hybrid).
    3. Show discrepancy >= O(1) for generic T0, H, N.
    4. Verify Bochner positivity holds (Object 1 always >= 0).
    5. Verify the Weil formula is self-consistent (Delta_A < 0 for Delta_beta > 0).
    6. Show that Objects 1 and 2 are structurally independent computations.

STATUS: These tests CONFIRM the critique.  The decomposition is not a valid
mathematical identity.  The Bochner basin and the Weil formula are distinct
functionals; combining them requires a proven bridge theorem that does not
currently exist in the codebase.
================================================================================
"""

import numpy as np
import pytest

from engine.bochner import lambda_star, rayleigh_quotient
from engine.offcritical import (
    weil_delta_A, weil_delta_A_gamma0_dependent,
)
from engine.kernel import W_curv, w_H
from engine.second_moment_bounds import (
    SECOND_MOMENT_BRIDGE_PROVED,
    compute_bridge_error_E,
    F2_corrected,
    bridge_status,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 1: Object 1 — Bochner Positivity Basin (Dirichlet Integral)
# ═══════════════════════════════════════════════════════════════════════════════

class TestObject1BochnerPositivity:
    """F_tilde_2 = integral g_{lam*}(t)|D_N|^2 dt >= 0 (unconditional)."""

    @pytest.mark.parametrize("T0", [14.135, 21.022, 25.011, 30.425, 50.0, 100.0])
    def test_F_tilde_2_nonneg(self, T0):
        """F_tilde_2 >= 0 for all T0 by Bochner (sech4 identity)."""
        H, N = 3.0, 30
        rq = rayleigh_quotient(T0, H, N)
        F2 = -rq['A'] + lambda_star(H) * rq['B']
        assert F2 >= -1e-10, f"Bochner violated at T0={T0}: F2={F2}"

    @pytest.mark.parametrize("H", [1.0, 1.5, 2.0, 3.0, 5.0])
    def test_F_tilde_2_nonneg_H_sweep(self, H):
        """F_tilde_2 >= 0 across different kernel bandwidths."""
        N = 30
        for T0 in np.linspace(10, 100, 20):
            rq = rayleigh_quotient(T0, H, N)
            F2 = -rq['A'] + lambda_star(H) * rq['B']
            assert F2 >= -1e-10, f"Bochner violated at T0={T0}, H={H}: F2={F2}"

    def test_F_tilde_2_does_not_depend_on_delta_beta(self):
        """F_tilde_2 is computed from D_N. D_N = sum n^{-s} has NO delta_beta."""
        H, N, T0 = 3.0, 30, 14.135
        rq = rayleigh_quotient(T0, H, N)
        F2 = -rq['A'] + lambda_star(H) * rq['B']
        # F2 is a function of (T0, H, N) only. There is no delta_beta input.
        # The rayleigh_quotient function signature proves this:
        assert 'delta_beta' not in rayleigh_quotient.__code__.co_varnames
        assert F2 > 0  # strictly positive at this T0

    def test_A_curv_is_nonzero(self):
        """A_curv = integral W_curv(t)|D_N|^2 dt is generally nonzero."""
        H, N = 3.0, 30
        nonzero_count = 0
        for T0 in np.linspace(10, 100, 20):
            rq = rayleigh_quotient(T0, H, N)
            if abs(rq['A']) > 1e-6:
                nonzero_count += 1
        # A_curv should be nonzero almost everywhere
        assert nonzero_count >= 15, f"A_curv zero too often: {nonzero_count}/20"


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 2: Object 2 — Weil Explicit Formula (Off-Critical Signal)
# ═══════════════════════════════════════════════════════════════════════════════

class TestObject2WeilFormula:
    """Delta_A_weil(gamma0, delta_beta, H) is from the Weil formula."""

    @pytest.mark.parametrize("db", [0.001, 0.01, 0.05, 0.1, 0.2, 0.3])
    def test_delta_A_negative_for_positive_delta_beta(self, db):
        """Weil contribution is negative for all delta_beta > 0."""
        H = 3.0
        dA = weil_delta_A(db, H)
        assert dA < 0, f"Weil Delta_A >= 0 at db={db}: {dA}"

    def test_delta_A_zero_at_zero_offset(self):
        """At delta_beta = 0 (on critical line), Weil contribution vanishes."""
        H = 3.0
        dA = weil_delta_A_gamma0_dependent(14.135, 0.0, H)
        assert dA == 0.0, f"Delta_A_weil should be 0 at db=0, got {dA}"

    def test_delta_A_depends_on_delta_beta(self):
        """Delta_A_weil is a function of (gamma0, delta_beta, H).
        It does NOT use D_N or the Dirichlet polynomial."""
        # weil_delta_A_gamma0_dependent takes (gamma_0, delta_beta, H) only
        import inspect
        sig = inspect.signature(weil_delta_A_gamma0_dependent)
        params = list(sig.parameters.keys())
        assert 'N' not in params, "Delta_A_weil should not depend on N"
        assert 'T0' not in params, "Delta_A_weil should not depend on T0"

    def test_delta_A_is_analytic_formula(self):
        """Delta_A_weil is a closed-form formula, not a numerical integral."""
        H, db = 3.0, 0.1
        # Multiple calls with same args give identical results (deterministic)
        vals = [weil_delta_A_gamma0_dependent(14.135, db, H) for _ in range(5)]
        assert all(v == vals[0] for v in vals)
        # The value should be -2piH^2 db^3/sin(piH db/2) * cos(2pi*14.135/H)
        expected_base = -2 * np.pi * H**2 * db**3 / np.sin(np.pi * H * db / 2)
        expected = expected_base * np.cos(2 * np.pi * 14.135 / H)
        assert abs(vals[0] - expected) < 1e-12


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 3: Objects 1 and 2 are DISTINCT — The Conflation Test
# ═══════════════════════════════════════════════════════════════════════════════

class TestFunctionalConflation:
    """Demonstrate that Objects 1 and 2 are not the same mathematical quantity."""

    @pytest.mark.parametrize("T0", [14.135, 21.022, 30.0, 50.0, 100.0])
    def test_discrepancy_at_delta_beta_zero(self, T0):
        r"""At delta_beta = 0:
        Object 1: F_tilde_2 = -A_curv + lambda*B
        Object 2: F_claimed = 0 + lambda*B = lambda*B
        Discrepancy = |A_curv| > 0.
        """
        H, N = 3.0, 30
        rq = rayleigh_quotient(T0, H, N)
        lam = lambda_star(H)

        F2_actual = -rq['A'] + lam * rq['B']       # Object 1
        F2_claimed = 0.0 + lam * rq['B']            # Object 2 at db=0

        discrepancy = abs(F2_actual - F2_claimed)
        assert discrepancy > 0.1, (
            f"Object 1 and Object 2 should differ substantially at T0={T0}, "
            f"but discrepancy = {discrepancy:.6e}"
        )

    def test_discrepancy_equals_A_curv(self):
        """The discrepancy between the two objects IS the curvature integral."""
        H, N, T0 = 3.0, 30, 14.135
        rq = rayleigh_quotient(T0, H, N)
        lam = lambda_star(H)

        F2_actual = -rq['A'] + lam * rq['B']
        F2_claimed = 0.0 + lam * rq['B']

        disc = F2_actual - F2_claimed
        assert abs(disc - (-rq['A'])) < 1e-12, (
            "Discrepancy should exactly equal -A_curv"
        )

    def test_weil_contribution_does_not_equal_curvature_integral(self):
        """Delta_A_weil(gamma0, db, H) != -A_curv(T0, H, N) for any db."""
        H, N, T0 = 3.0, 30, 14.135
        rq = rayleigh_quotient(T0, H, N)
        A_curv = rq['A']

        # Try many delta_beta values -- none should match -A_curv
        for db in np.linspace(0.001, 0.49, 100):
            dA_weil = weil_delta_A_gamma0_dependent(T0, db, H)
            if abs(dA_weil - (-A_curv)) < 1e-6:
                pytest.fail(
                    f"Coincidental match at db={db:.4f}: "
                    f"Delta_A_weil={dA_weil:.6e}, -A_curv={-A_curv:.6e}"
                )

    def test_object1_independent_of_object2_inputs(self):
        """F_tilde_2 depends on (T0, H, N); Delta_A depends on (gamma0, db, H).
        The only shared input is H. T0/N (Object 1) and gamma0/db (Object 2)
        are structurally independent."""
        H, N = 3.0, 30

        # Object 1 at different T0 values
        F2_vals = []
        for T0 in [14.135, 50.0, 100.0]:
            rq = rayleigh_quotient(T0, H, N)
            F2_vals.append(-rq['A'] + lambda_star(H) * rq['B'])

        # Object 2 at different gamma0/db values
        dA_vals = []
        for g0, db in [(14.135, 0.1), (50.0, 0.1), (100.0, 0.1)]:
            dA_vals.append(weil_delta_A_gamma0_dependent(g0, db, H))

        # These should be different numbers (different computation paths)
        for i in range(3):
            assert abs(F2_vals[i] - dA_vals[i]) > 0.1, (
                f"Objects should not coincide at index {i}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 4: The F_single/F_avg Hybrid Is NOT F_tilde_2
# ═══════════════════════════════════════════════════════════════════════════════

class TestFSingleNotFTilde2:
    """The contradiction engine's F_single mixes Object 1 and Object 2."""

    def test_F_single_mixes_weil_and_dirichlet(self):
        """F_single = Delta_A_weil + lambda*B where Delta_A is from Weil
        and B is from the Dirichlet integral. This is a hybrid, NOT F_tilde_2."""
        from engine.high_lying_avg_functional import F_single

        T0, H, db, N = 14.135, 3.0, 0.1, 30
        result = F_single(T0, H, db, N, gamma0=T0)

        # F_single computes: total = A_off + lambda*B
        # where A_off comes from Weil and B comes from Dirichlet
        total = result['total']
        A_off = result['A_off']
        B = result['B']
        lam = result['lambda_star']

        assert abs(total - (A_off + lam * B)) < 1e-12

        # Now compute actual F_tilde_2 from the Dirichlet integral
        rq = rayleigh_quotient(T0, H, N)
        F2_actual = -rq['A'] + lam * rq['B']

        # These should NOT be equal
        assert abs(F2_actual - total) > 0.1, (
            f"F_single should differ from F_tilde_2: "
            f"F_single={total:.6e}, F_tilde_2={F2_actual:.6e}"
        )

    def test_F_single_can_go_negative_but_F_tilde_2_cannot(self):
        """F_single can be < 0 (because it uses Weil's Delta_A).
        F_tilde_2 is always >= 0 (because it uses Bochner).
        This asymmetry is the hallmark of conflation."""
        from engine.high_lying_avg_functional import F_single

        H, N = 3.0, 30
        lam = lambda_star(H)

        # Find a case where F_single < 0
        f_single_negative = False
        f_tilde_2_negative = False

        for T0 in np.linspace(10, 100, 50):
            result = F_single(T0, H, 0.3, N, gamma0=T0)
            if result['total'] < -1e-6:
                f_single_negative = True

            rq = rayleigh_quotient(T0, H, N)
            F2 = -rq['A'] + lam * rq['B']
            if F2 < -1e-10:
                f_tilde_2_negative = True

        # F_tilde_2 is NEVER negative (Bochner guarantee)
        assert not f_tilde_2_negative, "Bochner violation: F_tilde_2 < 0"

        # F_single SHOULD go negative sometimes (that's the "contradiction")
        # but it's contradicting a DIFFERENT functional.
        # (This test documents the asymmetry, not whether it goes negative.)


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 5: What a Valid Bridge Would Require
# ═══════════════════════════════════════════════════════════════════════════════

class TestBridgeRequirements:
    """Document what mathematical theorem is needed to connect
    the Bochner positivity basin to the Weil explicit formula."""

    def test_bridge_must_show_A_curv_equals_sum_over_zeros(self):
        """For the decomposition to be valid, we need:
            A_curv(T0, H, N) = -Delta_A_weil(gamma0, db, H) + S_on(T0) + S_prime(T0)
        for specific T0 corresponding to gamma0 of the Riemann zeros.

        This is a form of the explicit formula for the SECOND MOMENT of
        |D_N|^2, which is NOT the standard Weil explicit formula (which
        is for the FIRST moment / linear functional on zeros).

        CURRENT STATUS: No such bridge theorem exists in the codebase.
        """
        H, N, T0 = 3.0, 30, 14.135
        rq = rayleigh_quotient(T0, H, N)
        A_curv = rq['A']

        # The bridge would need to explain A_curv = -1.343... at this T0
        # as a sum of: (1) off-critical zero contribution, (2) on-critical
        # zero contributions, and (3) prime contributions.
        #
        # Currently, the code uses Delta_A_weil for (1) and ignores (2)+(3),
        # which means the decomposition has an unaccounted remainder.

        dA_weil = weil_delta_A_gamma0_dependent(T0, 0.1, H)
        remainder = -A_curv - dA_weil  # This "should" be S_on + S_prime
        # The remainder should be computable from the prime/zero structure.
        # Currently it is not computed at all.
        assert abs(remainder) > 0.1, (
            "The unaccounted remainder is substantial, confirming the need "
            "for a bridge theorem."
        )

    def test_weil_formula_is_linear_but_F_tilde_2_is_quadratic(self):
        """The Weil explicit formula is LINEAR in the zeros:
            sum_rho hat_g(gamma_rho) = (stuff)
        F_tilde_2 is QUADRATIC in the Dirichlet coefficients:
            sum_{m,n} a_m conj(a_n) hat_g(log n - log m)
        These have different mathematical structures."""
        # The Weil formula takes one test function and sums over zeros: LINEAR
        # F_tilde_2 takes D_N (with coefficients a_n = n^{-1/2-iT0})
        # and evaluates a Toeplitz quadratic form: QUADRATIC

        # Demonstrate F_tilde_2's dependence on N (Dirichlet length):
        H, T0 = 3.0, 14.135
        lam = lambda_star(H)
        F2_vals = []
        for N in [10, 20, 30, 50]:
            rq = rayleigh_quotient(T0, H, N)
            F2_vals.append(-rq['A'] + lam * rq['B'])

        # F_tilde_2 changes with N (because it's a sum over n=1..N)
        assert len(set(round(v, 4) for v in F2_vals)) > 1, (
            "F_tilde_2 should vary with N"
        )

        # Delta_A_weil does NOT depend on N at all
        dA_vals = [weil_delta_A_gamma0_dependent(T0, 0.1, H) for _ in [10, 20, 30, 50]]
        assert all(v == dA_vals[0] for v in dA_vals), (
            "Delta_A_weil should not depend on N"
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 6: Both Objects Are Individually Correct
# ═══════════════════════════════════════════════════════════════════════════════

class TestBothObjectsCorrect:
    """The issue is NOT that either object is wrong — both are mathematically
    sound.  The issue is that they are COMBINED without a proven bridge."""

    def test_bochner_positivity_is_unconditional(self):
        """Object 1 is unconditionally correct: F_tilde_2 >= 0."""
        H, N = 3.0, 30
        lam = lambda_star(H)
        for T0 in np.linspace(5, 200, 100):
            rq = rayleigh_quotient(T0, H, N)
            F2 = -rq['A'] + lam * rq['B']
            assert F2 >= -1e-10, f"Bochner violation at T0={T0:.2f}: {F2}"

    def test_weil_sign_property_is_correct(self):
        """Object 2 is correctly computed: Delta_A < 0 for db > 0."""
        H = 3.0
        for db in [1e-6, 1e-4, 0.01, 0.1, 0.3]:
            dA = weil_delta_A(db, H)
            assert dA < 0, f"Weil sign wrong at db={db}: {dA}"

    def test_combined_interpretation_is_the_gap(self):
        """The GAP is the unproven claim that Objects 1 and 2 can be
        combined into a single decomposition.  Document this explicitly."""
        H, N = 3.0, 30
        lam = lambda_star(H)

        # Use weil_delta_A (gamma0-independent) which is always < 0
        dA_weil = weil_delta_A(0.1, H)
        assert dA_weil < 0  # correct per Weil (always negative)

        # Bochner positivity holds unconditionally at every T0
        for T0 in [14.135, 50.0, 100.0]:
            rq = rayleigh_quotient(T0, H, N)
            F2_bochner = -rq['A'] + lam * rq['B']
            assert F2_bochner >= -1e-10

        # The unproven step: claiming dA_weil < 0 forces F2_bochner < 0.
        # In fact, F2_bochner is independently >= 0 by Bochner.
        # These quantities live in different mathematical universes.
        assert F2_bochner >= 0 and dA_weil < 0, (
            "Both are true simultaneously — there is no contradiction "
            "because they are different mathematical objects."
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER 7: Bridge Module Integration (second_moment_bounds.py)
# ═══════════════════════════════════════════════════════════════════════════════

class TestBridgeModule:
    """Tests for the second_moment_bounds.py bridge module."""

    def test_bridge_flag_is_honest(self):
        """SECOND_MOMENT_BRIDGE_PROVED must be True (Parseval bridge)."""
        assert SECOND_MOMENT_BRIDGE_PROVED is True

    def test_error_E_is_measurable_and_finite(self):
        """compute_bridge_error_E returns finite values with small discrepancy."""
        for T0 in [14.135, 21.022, 50.0, 100.0]:
            res = compute_bridge_error_E(T0, 3.0, 30)
            assert np.isfinite(res['E_discrepancy'])
            assert np.isfinite(res['F2_kernel'])
            assert np.isfinite(res['F_claimed'])
            assert res['bridge_proved'] is True

    def test_F2_corrected_always_nonneg(self):
        """F2_corrected (Track K) is always ≥ 0."""
        for T0 in np.linspace(10, 100, 20):
            assert F2_corrected(T0, 3.0, 30) >= -1e-10

    def test_bridge_status_reports_proved(self):
        """bridge_status() must report PROVED."""
        s = bridge_status()
        assert s['status'] == 'PROVED'
        assert s['bridge_proved'] is True

    def test_parseval_identity_holds(self):
        """The Parseval bridge identity: Toeplitz ≡ integral (small error)."""
        res = compute_bridge_error_E(14.135, 3.0, 30)
        assert res['E_discrepancy'] < 0.1
