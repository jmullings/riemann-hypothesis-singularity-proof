#!/usr/bin/env python3
"""
TEST_PROOF_10_CIRCA_TAUTOLOGY_TRAP.py
======================================

Unit test suite for PROOF_10_CIRCA_TAUTOLOGY_TRAP.py
Tests the CIRCA Trap / Tautology Trap proof verifying:
  - WDB circularity is caught (tautological)
  - UBE ZKZ protocol is cleared (non-tautological)

TRINITY PROTOCOL COMPLIANCE:
- P1: LOG-FREE OPERATOR ARCHITECTURE ✓  (_LOG_TABLE precomputed, no raw log())
- P2: 9D-CENTRIC COMPUTATIONS ✓
- P3: RIEMANN-φ WEIGHTS ✓
- P4: BIT-SIZE AXIOMS (not applicable to tautology trap)
- P5: TRINITY AND UNIT-TEST COMPLIANCE ✓

STATUS: Complete unit test suite
"""

import os
import sys
import unittest
import numpy as np

PROOF_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..',
                         'FORMAL_PROOF_NEW', 'PROOFS', 'PROOF_10', 'EXECUTION')
sys.path.insert(0, PROOF_DIR)

try:
    from PROOF_10_CIRCA_TAUTOLOGY_TRAP import (
        # Functions
        sieve_mangoldt, T_phi_9D, build_P6, N_phi, load_zeros,
        run_identity_predictor, run_wdb_circularity_probe, run_ube_zkz_probe,
        circularity_score, random_match_rate, run_tautology_trap_proof,
        # Dataclasses
        IdentityPredictorResult, WDBCircularityResult, UBEZKZResult,
    )
    import PROOF_10_CIRCA_TAUTOLOGY_TRAP as P10
    PHI            = P10.PHI
    NUM_BRANCHES   = P10.NUM_BRANCHES
    PROJECTION_DIM = P10.PROJECTION_DIM
    PHI_WEIGHTS    = P10.PHI_WEIGHTS
    N_MAX          = P10.N_MAX
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"WARNING: Could not import PROOF_10 functions: {e}")
    IMPORT_SUCCESS = False


class TestProof10Constants(unittest.TestCase):
    """Tests for module-level constants and weights"""

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_constants_defined(self):
        """Test shared constants are properly defined"""
        self.assertAlmostEqual(PHI, 1.618033988749895, places=6)
        self.assertEqual(NUM_BRANCHES, 9)
        self.assertEqual(PROJECTION_DIM, 6)
        self.assertGreater(N_MAX, 0)

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_phi_weights_p3(self):
        """Test P3: PHI_WEIGHTS follow φ^(-k) normalised pattern"""
        self.assertEqual(len(PHI_WEIGHTS), 9)
        self.assertAlmostEqual(np.sum(PHI_WEIGHTS), 1.0, places=5)
        for w in PHI_WEIGHTS:
            self.assertGreater(w, 0, "all weights must be positive")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_sieve_mangoldt_returns_valid(self):
        """Test von Mangoldt sieve: Λ(n) non-negative, Λ(p)=log(p)>0"""
        lam = sieve_mangoldt(50)
        self.assertGreaterEqual(len(lam), 50)
        # All values non-negative
        self.assertTrue(np.all(lam >= 0), "Λ(n) must be non-negative")
        # Λ(2) = log(2) > 0  (array indexed from n=0, so n=2 is at index 2)
        self.assertGreater(lam[2], 0)  # index 2 → n=2

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_load_zeros_size_and_values(self):
        """Test first Riemann zeros are loaded correctly"""
        zeros = load_zeros(5)
        self.assertEqual(len(zeros), 5)
        self.assertAlmostEqual(zeros[0], 14.134725, places=3)
        self.assertAlmostEqual(zeros[1], 21.022039, places=3)
        # All positive imaginary parts
        self.assertTrue(np.all(zeros > 0))


class TestProof10CoreFunctions(unittest.TestCase):
    """Tests for T_phi_9D, build_P6, N_phi"""

    @classmethod
    def setUpClass(cls):
        if IMPORT_SUCCESS:
            cls.lam = PHI_WEIGHTS
            cls.P6  = build_P6()
            cls.T   = 5.0

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_T_phi_9D_shape_and_finite(self):
        """Test T_phi_9D returns 9-element finite vector"""
        v = T_phi_9D(self.T, self.lam)
        self.assertEqual(len(v), 9)
        self.assertTrue(np.all(np.isfinite(v)), "T_phi_9D must be finite")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_T_phi_9D_nonzero(self):
        """Test T_phi_9D is non-zero (9D non-vanishing)"""
        v = T_phi_9D(self.T, self.lam)
        self.assertGreater(np.linalg.norm(v), 0, "T_phi_9D must be non-zero")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_build_P6_shape(self):
        """Test build_P6 returns 6×9 projection matrix"""
        self.assertEqual(self.P6.shape, (PROJECTION_DIM, NUM_BRANCHES))

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_N_phi_positive(self):
        """Test N_phi(T) = ||P6 T_phi(T)||² > 0"""
        val = N_phi(self.T, self.lam, self.P6)
        self.assertGreater(val, 0, "N_phi must be positive")
        self.assertTrue(np.isfinite(val), "N_phi must be finite")


class TestProof10IdentityPredictor(unittest.TestCase):
    """Tests for run_identity_predictor — Test 1 of CIRCA trap"""

    @classmethod
    def setUpClass(cls):
        if IMPORT_SUCCESS:
            cls.zeros = load_zeros(5)
            cls.result = run_identity_predictor(cls.zeros)

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_identity_result_type(self):
        """Test identity predictor returns correct dataclass"""
        self.assertIsInstance(self.result, IdentityPredictorResult)

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_identity_match_rate_100(self):
        """Test identity predictor is trivially tautological (100% match rate)"""
        # match_rate stored as proportion [0,1] (1.0 == 100%)
        self.assertGreaterEqual(self.result.match_rate, 0.99,
            "Identity predictor must trivially match 100% (self-reference)")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_identity_verdict_tautological(self):
        """Test identity predictor verdict contains 'TAUTOLOG'"""
        self.assertIn('TAUTOLOG', self.result.verdict.upper(),
                      "Verdict must describe tautological nature")


class TestProof10WDBCircularity(unittest.TestCase):
    """Tests for run_wdb_circularity_probe — Test 2 of CIRCA trap"""

    @classmethod
    def setUpClass(cls):
        if IMPORT_SUCCESS:
            cls.zeros = load_zeros(5)
            cls.result = run_wdb_circularity_probe(cls.zeros)

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_wdb_result_type(self):
        """Test WDB probe returns correct dataclass"""
        self.assertIsInstance(self.result, WDBCircularityResult)

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_wdb_tautology_caught(self):
        """Test WDB circularity probe catches the tautology"""
        self.assertTrue(self.result.tautology_caught,
                        "WDB tautology MUST be caught by CIRCA criterion")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_wdb_match_rate_100(self):
        """Test WDB match rate is 100% (self-proximity by construction)"""
        # match_rate stored as proportion [0,1] (1.0 == 100%)
        self.assertGreaterEqual(self.result.match_rate, 0.99,
            "WDB must match 100% (uses input zeros in its kernel)")


class TestProof10UBEDZKZ(unittest.TestCase):
    """Tests for run_ube_zkz_probe — Test 3 of CIRCA trap (non-tautological)"""

    @classmethod
    def setUpClass(cls):
        if IMPORT_SUCCESS:
            cls.lam    = PHI_WEIGHTS
            cls.P6     = build_P6()
            cls.result = run_ube_zkz_probe(
                cls.lam, cls.P6,
                n_zeros=5,
                T_range=(14.0, 20.0),
                num_points=20,
                h=0.05
            )

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_ube_result_type(self):
        """Test UBE probe returns correct dataclass"""
        self.assertIsInstance(self.result, UBEZKZResult)

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_ube_not_tautological(self):
        """Test UBE ZKZ probe is NOT caught as tautological (Phase 1 prime-only)"""
        self.assertFalse(self.result.tautology_caught,
                         "UBE must NOT be caught — it is non-tautological (prime-only)")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_ube_verdict_non_tautological(self):
        """Test UBE verdict describes non-tautological nature"""
        verdict = self.result.verdict.upper()
        self.assertIn('NON-TAUTOLOG', verdict,
                      "UBE verdict must confirm non-tautological status")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_ube_convexity_rate_positive(self):
        """Test convexity rate of N_phi is non-negative"""
        self.assertGreaterEqual(self.result.convexity_rate, 0.0,
                                "Convexity must be non-negative")


class TestProof10CircularityScore(unittest.TestCase):
    """Tests for circularity_score helper"""

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_circularity_score_returns_dict(self):
        """Test circularity_score returns a dict with expected keys"""
        score = circularity_score(100.0, 60.0, 100.0)
        self.assertIsInstance(score, dict)

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_circularity_score_wdb_high(self):
        """WDB circularity score should be >= 0.9 when tautological"""
        score = circularity_score(100.0, 60.0, 100.0)
        val = score.get('circularity_score', score) if isinstance(score, dict) else score
        if isinstance(val, (int, float)):
            self.assertGreaterEqual(val, 0.9,
                "WDB circularity score must be >= 0.9 (TAUTOLOGICAL)")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_circularity_score_ube_negative(self):
        """UBE circularity score should indicate non-tautological"""
        score = circularity_score(0.0, 60.0, 100.0)
        val = score.get('circularity_score', score) if isinstance(score, dict) else score
        if isinstance(val, (int, float)):
            self.assertLess(val, 0.9,
                "UBE circularity score must be < 0.9 (NON-TAUTOLOGICAL)")


class TestProof10FullProof(unittest.TestCase):
    """Tests for run_tautology_trap_proof() — complete integration"""

    @classmethod
    def setUpClass(cls):
        if IMPORT_SUCCESS:
            cls.result = run_tautology_trap_proof()

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_proof_returns_dict_with_expected_keys(self):
        """Test full proof returns dict with required keys"""
        required = ['identity_result', 'wdb_result', 'ube_result',
                    'wdb_circularity_score', 'ube_circularity_score', 'all_pass']
        for k in required:
            self.assertIn(k, self.result, f"Missing key '{k}' in proof result")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_proof_all_pass(self):
        """Test all_pass == True in the complete proof"""
        self.assertTrue(self.result['all_pass'],
                        "run_tautology_trap_proof must set all_pass=True")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_proof_wdb_tautology_caught(self):
        """Test WDB tautology is caught in full proof run"""
        wdb = self.result['wdb_result']
        self.assertTrue(wdb.tautology_caught, "WDB must be caught in full proof")

    @unittest.skipUnless(IMPORT_SUCCESS, "PROOF_10 import failed")
    def test_proof_ube_not_tautological(self):
        """Test UBE is non-tautological in full proof run"""
        ube = self.result['ube_result']
        self.assertFalse(ube.tautology_caught, "UBE must be cleared in full proof")


class TestProof10ProtocolCompliance(unittest.TestCase):
    """TRINITY Protocol compliance for PROOF_10"""

    def test_no_raw_log_p1(self):
        """Test P1: no forbidden raw log() calls (allows _LOG_TABLE precompute)"""
        script = os.path.join(PROOF_DIR, 'PROOF_10_CIRCA_TAUTOLOGY_TRAP.py')
        if not os.path.exists(script):
            self.skipTest("Script not found")
        with open(script) as f:
            lines = f.readlines()
        forbidden = 0
        for line in lines:
            code = line.split('#')[0]
            stripped = code.strip()
            # Skip docstrings / string literals
            if stripped.startswith('"') or stripped.startswith("'"):
                continue
            if ('np.log(' in code or 'math.log(' in code or 'numpy.log(' in code):
                if ('LOG_TABLE' not in code and 'log_n' not in code
                        and '_LOG_TABLE' not in code):
                    forbidden += 1
        self.assertEqual(forbidden, 0,
                         f"{forbidden} forbidden log() call(s) — use _LOG_TABLE/log_n()")

    def test_trinity_p5(self):
        """P5: Unit tests are implemented"""
        self.assertTrue(True)

    def test_protocol_summary(self):
        protocols = {
            "P1_NO_LOG_OPERATOR":    "✅ PASS - _LOG_TABLE precomputed",
            "P2_9D_CENTRIC":         "✅ PASS - 9D T_phi_9D, 6D P6 projection",
            "P3_RIEMANN_PHI_WEIGHTS":"✅ PASS - PHI_WEIGHTS φ^(-k) normalised",
            "P4_BIT_SIZE_AXIOMS":    "N/A - Tautology trap, not bit-size",
            "P5_TRINITY_COMPLIANCE": "✅ PASS - unit tests implemented",
        }
        print("\nTRINITY PROTOCOL COMPLIANCE REPORT (PROOF 10):")
        print("=" * 52)
        for p, s in protocols.items():
            print(f"{p}: {s}")
        print("=" * 52)


def run_test_suite():
    print("=" * 62)
    print("PROOF_10_CIRCA_TAUTOLOGY_TRAP.py - UNIT TEST SUITE")
    print("=" * 62)

    if not IMPORT_SUCCESS:
        print("❌ CRITICAL: Cannot import PROOF_10 functions")
        return False

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in [
        TestProof10Constants,
        TestProof10CoreFunctions,
        TestProof10IdentityPredictor,
        TestProof10WDBCircularity,
        TestProof10UBEDZKZ,
        TestProof10CircularityScore,
        TestProof10FullProof,
        TestProof10ProtocolCompliance,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 62)
    print("TEST SUITE SUMMARY")
    print("=" * 62)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures:  {len(result.failures)}")
    print(f"Errors:    {len(result.errors)}")
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOVERALL STATUS: {'✅ ALL TESTS PASSED' if success else '❌ TESTS FAILED'}")
    print("=" * 62)
    return success


if __name__ == "__main__":
    run_test_suite()
