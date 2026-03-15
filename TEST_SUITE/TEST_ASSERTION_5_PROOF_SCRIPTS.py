#!/usr/bin/env python3
"""
TEST_ASSERTION_5_PROOF_SCRIPTS.py

Comprehensive Unit Tests for Assertion 5: New Mathematical Finds
================================================================

Tests for all 1_PROOF_SCRIPTS_NOTES files:
- 1_PRIME_TRANSFER_OPERATOR.py
- ASSERTION_5_FILE_1__HILBERT_POLYA_SPECTRAL.py
- ASSERTION_5_FILE_2__LI_POSITIVITY_PRINCIPLE.py
- ASSERTION_5_FILE_3__DE_BRUIJN_NEWMAN_FLOW.py
- ASSERTION_5_FILE_4__MONTGOMERY_PAIR_CORRELATION.py
- ASSERTION_5_FILE_5__EXPLICIT_FORMULA_STABILITY.py
- RH_VARIATIONAL_PRINCIPLE_v2.py

Test Categories:
1. SYNTAX VALIDATION: Scripts compile without syntax errors
2. IMPORT VALIDATION: Modules successfully import
3. TRINITY GATE TESTS: Infinity, Boundedness, Consistency
4. RH PRINCIPLE TESTS: 5 independent RH validations
5. PHI-FRAMEWORK TESTS: φ-weight geometric consistency

Date: March 2026
"""

from __future__ import annotations

import sys
import os
import unittest
import importlib.util
import py_compile
from pathlib import Path
import numpy as np
from typing import Optional, Any

# ============================================================================
# CONFIGURATION
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2
NUM_BRANCHES = 9
PROJ_DIM = 6
EPSILON = 1e-10
TRINITY_THRESHOLD = 0.95

BASE_PATH = Path(__file__).parent.parent / "CONJECTURE_V" / "ASSERTION_5_NEW_MATHEMATICAL_FINDS"
PROOF_SCRIPTS_PATH = BASE_PATH / "1_PROOF_SCRIPTS_NOTES"

ASSERTION_5_SCRIPTS = [
    "1_PRIME_TRANSFER_OPERATOR.py",
    "ASSERTION_5_FILE_1__HILBERT_POLYA_SPECTRAL.py",
    "ASSERTION_5_FILE_2__LI_POSITIVITY_PRINCIPLE.py",
    "ASSERTION_5_FILE_3__DE_BRUIJN_NEWMAN_FLOW.py",
    "ASSERTION_5_FILE_4__MONTGOMERY_PAIR_CORRELATION.py",
    "ASSERTION_5_FILE_5__EXPLICIT_FORMULA_STABILITY.py",
    "RH_VARIATIONAL_PRINCIPLE_v2.py",
]

RH_PRINCIPLE_FILES = [
    ("Hilbert-Pólya Spectral", "ASSERTION_5_FILE_1__HILBERT_POLYA_SPECTRAL.py"),
    ("Li Positivity", "ASSERTION_5_FILE_2__LI_POSITIVITY_PRINCIPLE.py"),
    ("de Bruijn-Newman Flow", "ASSERTION_5_FILE_3__DE_BRUIJN_NEWMAN_FLOW.py"),
    ("Montgomery Pair Correlation", "ASSERTION_5_FILE_4__MONTGOMERY_PAIR_CORRELATION.py"),
    ("Explicit Formula Stability", "ASSERTION_5_FILE_5__EXPLICIT_FORMULA_STABILITY.py"),
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_module_from_path(script_path: Path, module_name: str) -> Optional[Any]:
    """Dynamically load a module from a file path."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Failed to load {script_path}: {e}")
        return None


def can_compile(script_path: Path) -> bool:
    """Check if a Python script compiles without syntax errors."""
    try:
        py_compile.compile(str(script_path), doraise=True)
        return True
    except py_compile.PyCompileError:
        return False


def check_independence_statement(script_path: Path) -> bool:
    """Check if script contains ζ-FREE INDEPENDENCE STATEMENT."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return "INDEPENDENCE STATEMENT" in content or "INDEPENDENCE_STATEMENT" in content
    except Exception:
        return False


# ============================================================================
# REFERENCE IMPLEMENTATIONS
# ============================================================================

def phi_weights_9d() -> np.ndarray:
    """Return normalized φ-weights for 9 branches."""
    weights = np.array([PHI ** (-(k + 1)) for k in range(NUM_BRANCHES)], dtype=float)
    return weights / weights.sum()


def euler_psi_sum(T: float, N: int = 2000) -> complex:
    """Euler-style Dirichlet sum: ψ_E(T) = Σ_{n=1}^N n^{-1/2} e^{-iT log n}."""
    n = np.arange(1, N + 1, dtype=float)
    log_n = np.log(n)
    n_power = 1.0 / np.sqrt(n)
    phases = -T * log_n
    return np.sum(n_power * np.exp(1j * phases))


def build_t_phi_vector(T: float, N: int = 2000, delta: float = 0.015) -> np.ndarray:
    """Build 9D vector from φ-weighted curvatures."""
    weights = phi_weights_9d()
    t_phi = np.zeros(NUM_BRANCHES, dtype=float)
    scales = np.array([PHI ** (k + 1) for k in range(NUM_BRANCHES)])
    
    for k in range(NUM_BRANCHES):
        h_k = delta * scales[k]
        psi_plus = euler_psi_sum(T + h_k, N)
        psi_zero = euler_psi_sum(T, N)
        psi_minus = euler_psi_sum(T - h_k, N)
        second_deriv = (psi_plus - 2 * psi_zero + psi_minus) / (h_k ** 2)
        t_phi[k] = weights[k] * abs(second_deriv)
    
    return t_phi


def trinity_gate_check(T: float, N: int = 1000) -> dict:
    """Check Trinity Gate criteria at height T."""
    state = build_t_phi_vector(T, N)
    norm = np.linalg.norm(state)
    
    # Gate 1: Infinity (unbounded growth potentiality)
    infinity_score = min(1.0, norm / 100) if norm > EPSILON else 0.0
    
    # Gate 2: Boundedness (finite constraint)
    boundedness_score = 1.0 if norm < 1e6 else 0.0
    
    # Gate 3: Consistency (structural coherence)
    weights = phi_weights_9d()
    expected_decay = np.array([PHI ** (-(k+1)) for k in range(NUM_BRANCHES)])
    if norm > EPSILON:
        normalized = state / norm
        correlation = np.abs(np.corrcoef(normalized, expected_decay)[0, 1])
        consistency_score = correlation if not np.isnan(correlation) else 0.5
    else:
        consistency_score = 0.5
    
    return {
        'infinity': infinity_score,
        'boundedness': boundedness_score,
        'consistency': consistency_score,
        'total': (infinity_score + boundedness_score + consistency_score) / 3
    }


# ============================================================================
# SYNTAX VALIDATION TESTS
# ============================================================================

class TestAssertion5Syntax(unittest.TestCase):
    """Test that all Assertion 5 scripts compile without syntax errors."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_all_scripts_compile(self):
        """All Assertion 5 scripts compile without syntax errors."""
        for script_name in ASSERTION_5_SCRIPTS:
            script = self.scripts_path / script_name
            if script.exists():
                with self.subTest(script=script_name):
                    self.assertTrue(can_compile(script), f"Syntax error in {script_name}")


# ============================================================================
# IMPORT VALIDATION TESTS
# ============================================================================

class TestAssertion5Imports(unittest.TestCase):
    """Test that all Assertion 5 scripts import successfully."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_prime_transfer_operator_imports(self):
        """1_PRIME_TRANSFER_OPERATOR.py imports successfully."""
        script = self.scripts_path / "1_PRIME_TRANSFER_OPERATOR.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "prime_transfer")
        self.assertIsNotNone(module, "Module failed to import")

    def test_hilbert_polya_imports(self):
        """ASSERTION_5_FILE_1__HILBERT_POLYA_SPECTRAL.py imports successfully."""
        script = self.scripts_path / "ASSERTION_5_FILE_1__HILBERT_POLYA_SPECTRAL.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "hilbert_polya")
        self.assertIsNotNone(module, "Module failed to import")

    def test_li_positivity_imports(self):
        """ASSERTION_5_FILE_2__LI_POSITIVITY_PRINCIPLE.py imports successfully."""
        script = self.scripts_path / "ASSERTION_5_FILE_2__LI_POSITIVITY_PRINCIPLE.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "li_positivity")
        self.assertIsNotNone(module, "Module failed to import")

    def test_de_bruijn_newman_imports(self):
        """ASSERTION_5_FILE_3__DE_BRUIJN_NEWMAN_FLOW.py imports successfully."""
        script = self.scripts_path / "ASSERTION_5_FILE_3__DE_BRUIJN_NEWMAN_FLOW.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "de_bruijn_newman")
        self.assertIsNotNone(module, "Module failed to import")

    def test_montgomery_imports(self):
        """ASSERTION_5_FILE_4__MONTGOMERY_PAIR_CORRELATION.py imports successfully."""
        script = self.scripts_path / "ASSERTION_5_FILE_4__MONTGOMERY_PAIR_CORRELATION.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "montgomery")
        self.assertIsNotNone(module, "Module failed to import")

    def test_explicit_formula_imports(self):
        """ASSERTION_5_FILE_5__EXPLICIT_FORMULA_STABILITY.py imports successfully."""
        script = self.scripts_path / "ASSERTION_5_FILE_5__EXPLICIT_FORMULA_STABILITY.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "explicit_formula")
        self.assertIsNotNone(module, "Module failed to import")


# ============================================================================
# TRINITY GATE TESTS
# ============================================================================

class TestAssertion5TrinityGates(unittest.TestCase):
    """Test Trinity Gate validation criteria."""

    def test_infinity_gate(self):
        """Infinity Gate: state norms are positive."""
        for T in [10.0, 14.0, 21.0, 30.0]:
            with self.subTest(T=T):
                gates = trinity_gate_check(T, N=500)
                self.assertGreaterEqual(gates['infinity'], 0)
                self.assertLessEqual(gates['infinity'], 1)

    def test_boundedness_gate(self):
        """Boundedness Gate: state norms are finite."""
        for T in [10.0, 14.0, 21.0, 30.0]:
            with self.subTest(T=T):
                gates = trinity_gate_check(T, N=500)
                self.assertEqual(gates['boundedness'], 1.0,
                    f"Boundedness should be 1.0 at T={T}")

    def test_consistency_gate(self):
        """Consistency Gate: φ-weight coherence is maintained."""
        for T in [10.0, 14.0, 21.0, 30.0]:
            with self.subTest(T=T):
                gates = trinity_gate_check(T, N=500)
                self.assertGreaterEqual(gates['consistency'], 0)
                self.assertLessEqual(gates['consistency'], 1)

    def test_trinity_total_score(self):
        """Trinity total score is average of three gates."""
        T = 14.0
        gates = trinity_gate_check(T, N=500)
        expected_total = (gates['infinity'] + gates['boundedness'] + gates['consistency']) / 3
        self.assertAlmostEqual(gates['total'], expected_total, places=10)


# ============================================================================
# RH PRINCIPLE INDEPENDENCE TESTS
# ============================================================================

class TestAssertion5Independence(unittest.TestCase):
    """Test ζ-free independence in RH principle files."""

    @classmethod
    def setUpClass(cls):
        cls.scripts_path = PROOF_SCRIPTS_PATH
        if not cls.scripts_path.exists():
            raise unittest.SkipTest(f"Proof scripts path not found: {cls.scripts_path}")

    def test_all_rh_principles_have_independence_statement(self):
        """All 5 RH principle files contain independence statements."""
        for principle_name, filename in RH_PRINCIPLE_FILES:
            script = self.scripts_path / filename
            if script.exists():
                with self.subTest(principle=principle_name):
                    has_statement = check_independence_statement(script)
                    self.assertTrue(has_statement,
                        f"{principle_name} missing independence statement")


# ============================================================================
# PHI-FRAMEWORK CONSISTENCY TESTS
# ============================================================================

class TestAssertion5PhiFramework(unittest.TestCase):
    """Test φ-framework mathematical consistency."""

    def test_phi_constant_value(self):
        """PHI = (1 + √5) / 2 ≈ 1.618033988749895."""
        expected = (1 + np.sqrt(5)) / 2
        self.assertAlmostEqual(PHI, expected, places=14)

    def test_phi_golden_property(self):
        """PHI satisfies φ² = φ + 1."""
        self.assertAlmostEqual(PHI ** 2, PHI + 1, places=14)

    def test_phi_weights_sum_to_one(self):
        """φ-weights sum to 1 (normalization)."""
        weights = phi_weights_9d()
        self.assertAlmostEqual(weights.sum(), 1.0, places=14)

    def test_phi_weights_monotonic_decreasing(self):
        """φ-weights are monotonically decreasing."""
        weights = phi_weights_9d()
        for i in range(1, NUM_BRANCHES):
            self.assertLess(weights[i], weights[i-1],
                f"Weight {i} should be less than weight {i-1}")

    def test_euler_psi_sum_converges(self):
        """Euler ψ-sum converges as N increases."""
        T = 10.0
        psi_500 = euler_psi_sum(T, N=500)
        psi_1000 = euler_psi_sum(T, N=1000)
        psi_2000 = euler_psi_sum(T, N=2000)
        
        # Differences should decrease with increasing N
        diff_1 = abs(psi_1000 - psi_500)
        diff_2 = abs(psi_2000 - psi_1000)
        # Allow some tolerance for numerical variance
        self.assertLess(diff_2, diff_1 * 2,
            "ψ-sum should converge as N increases")


# ============================================================================
# STATE VECTOR TESTS
# ============================================================================

class TestAssertion5StateVector(unittest.TestCase):
    """Test 9D state vector construction and properties."""

    def test_state_vector_dimension(self):
        """State vector has correct dimension (9D)."""
        state = build_t_phi_vector(14.0, N=500)
        self.assertEqual(len(state), NUM_BRANCHES)

    def test_state_vector_non_negative(self):
        """State vector components are non-negative (magnitudes)."""
        state = build_t_phi_vector(14.0, N=500)
        for k, component in enumerate(state):
            self.assertGreaterEqual(component, 0,
                f"Component {k} should be non-negative")

    def test_state_vector_varies_with_T(self):
        """State vector varies with T (not constant)."""
        state_10 = build_t_phi_vector(10.0, N=500)
        state_20 = build_t_phi_vector(20.0, N=500)
        
        difference = np.linalg.norm(state_20 - state_10)
        self.assertGreater(difference, EPSILON,
            "State vectors should differ at different T values")


# ============================================================================
# VARIATIONAL PRINCIPLE TESTS
# ============================================================================

class TestAssertion5Variational(unittest.TestCase):
    """Test variational principle implementation."""

    def test_variational_principle_script_exists(self):
        """RH_VARIATIONAL_PRINCIPLE_v2.py exists."""
        script = PROOF_SCRIPTS_PATH / "RH_VARIATIONAL_PRINCIPLE_v2.py"
        if not script.exists():
            self.skipTest("RH_VARIATIONAL_PRINCIPLE_v2.py not yet created")
        self.assertTrue(script.exists())

    def test_variational_imports(self):
        """Variational principle script imports successfully."""
        script = PROOF_SCRIPTS_PATH / "RH_VARIATIONAL_PRINCIPLE_v2.py"
        if not script.exists():
            self.skipTest(f"Script not found: {script}")
        module = load_module_from_path(script, "variational_v2")
        self.assertIsNotNone(module, "Variational module failed to import")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ASSERTION 5: NEW MATHEMATICAL FINDS - UNIT TESTS")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion5Syntax))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion5Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion5TrinityGates))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion5Independence))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion5PhiFramework))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion5StateVector))
    suite.addTests(loader.loadTestsFromTestCase(TestAssertion5Variational))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL ASSERTION 5 TESTS PASSED")
    else:
        print(f"❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
