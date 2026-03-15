#!/usr/bin/env python3
"""
test_bridge_09_spiral_geometry.py
==================================
Mirrored unit tests for:
    FORMAL_PROOF_NEW/BRIDGES/BRIDGE_9/EXECUTION/BRIDGE_09_SPIRAL_GEOMETRY.py

Test Categories:
    T1 — Syntax: script compiles without errors
    T2 — Import: module loads (self-contained)
    T3 — Constants: _PRIMES, SIGMA_GRID, _GAMMA_REF
    T4 — spiral_path: output structure and values
    T5 — spiral_metrics: derived metrics from spiral path
    T6 — sigma_selective_spiral_scan: tightness results

Author: auto-generated test mirror
"""

from __future__ import annotations

import sys
import unittest
import py_compile
import importlib.util
from pathlib import Path
import math

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
BRIDGE_EXEC = ROOT / 'FORMAL_PROOF_NEW' / 'BRIDGES' / 'BRIDGE_9' / 'EXECUTION'
SCRIPT = BRIDGE_EXEC / 'BRIDGE_09_SPIRAL_GEOMETRY.py'


def _load_module():
    p = str(BRIDGE_EXEC)
    if p not in sys.path:
        sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location('BRIDGE_09_SPIRAL_GEOMETRY', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1 — Syntax
# ---------------------------------------------------------------------------
class TestBridge09Syntax(unittest.TestCase):

    def test_compiles_without_errors(self):
        """T1: BRIDGE_09_SPIRAL_GEOMETRY.py compiles without syntax errors."""
        self.assertTrue(SCRIPT.exists(), f"Script not found: {SCRIPT}")
        py_compile.compile(str(SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# T2 — Import
# ---------------------------------------------------------------------------
class TestBridge09Import(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_module_loads(self):
        """T2: Module imports successfully."""
        self.assertIsNotNone(self.mod)

    def test_expected_symbols(self):
        """T2: Key symbols exported."""
        for name in ('spiral_path', 'spiral_metrics', 'sigma_selective_spiral_scan',
                     '_PRIMES', 'SIGMA_GRID', '_GAMMA_REF'):
            self.assertTrue(hasattr(self.mod, name), f"Missing: {name}")


# ---------------------------------------------------------------------------
# T3 — Constants
# ---------------------------------------------------------------------------
class TestBridge09Constants(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_primes_nonempty(self):
        """T3: _PRIMES is non-empty."""
        self.assertGreater(len(self.mod._PRIMES), 0)

    def test_primes_are_prime(self):
        """T3: First several entries of _PRIMES are actually prime."""
        expected = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        actual = self.mod._PRIMES[:len(expected)]
        self.assertEqual(actual, expected)

    def test_primes_ascending(self):
        """T3: _PRIMES is in ascending order."""
        p = self.mod._PRIMES
        self.assertTrue(all(p[i] < p[i+1] for i in range(len(p) - 1)))

    def test_sigma_grid(self):
        """T3: SIGMA_GRID = [0.40, 0.45, 0.50, 0.55, 0.60]."""
        self.assertEqual(self.mod.SIGMA_GRID, [0.40, 0.45, 0.50, 0.55, 0.60])

    def test_gamma_ref_contains_first_zero(self):
        """T3: _GAMMA_REF first entry ≈ 14.1347."""
        self.assertAlmostEqual(self.mod._GAMMA_REF[0], 14.134725, places=4)

    def test_gamma_ref_ascending(self):
        """T3: _GAMMA_REF is ascending."""
        g = self.mod._GAMMA_REF
        self.assertTrue(all(g[i] < g[i+1] for i in range(len(g) - 1)))

    def test_gamma_ref_at_least_5_entries(self):
        """T3: At least 5 reference zeros defined."""
        self.assertGreaterEqual(len(self.mod._GAMMA_REF), 5)


# ---------------------------------------------------------------------------
# T4 — spiral_path
# ---------------------------------------------------------------------------
class TestBridge09SpiralPath(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_returns_list(self):
        """T4: spiral_path returns a list."""
        path = self.mod.spiral_path(0.5, 14.134725, P_max=50)
        self.assertIsInstance(path, list)

    def test_nonempty(self):
        """T4: At least one prime contributes to the path."""
        path = self.mod.spiral_path(0.5, 14.134725, P_max=50)
        self.assertGreater(len(path), 0)

    def test_dict_keys(self):
        """T4: Each path entry has required keys."""
        path = self.mod.spiral_path(0.5, 14.134725, P_max=50)
        required_keys = {'prime_index', 'prime', 'z_real', 'z_imag',
                         'radius', 'angle_rad', 'step_size', 'radius_delta'}
        for entry in path:
            for k in required_keys:
                self.assertIn(k, entry, f"Missing key '{k}' in path entry")

    def test_prime_index_ascending(self):
        """T4: prime_index is strictly ascending (1, 2, 3, ...)."""
        path = self.mod.spiral_path(0.5, 14.134725, P_max=50)
        indices = [e['prime_index'] for e in path]
        self.assertEqual(indices, list(range(1, len(path) + 1)))

    def test_prime_values_are_prime(self):
        """T4: 'prime' values in path entries match actual primes."""
        path = self.mod.spiral_path(0.5, 14.134725, P_max=50)
        ref_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for entry, p_ref in zip(path[:len(ref_primes)], ref_primes):
            self.assertEqual(entry['prime'], p_ref)

    def test_radius_nonnegative(self):
        """T4: All radius values ≥ 0."""
        path = self.mod.spiral_path(0.5, 14.134725, P_max=50)
        for entry in path:
            self.assertGreaterEqual(entry['radius'], 0.0)

    def test_step_size_positive(self):
        """T4: All step_size values > 0."""
        path = self.mod.spiral_path(0.5, 14.134725, P_max=50)
        for entry in path:
            self.assertGreater(entry['step_size'], 0.0)

    def test_all_finite(self):
        """T4: All numeric fields are finite."""
        path = self.mod.spiral_path(0.5, 14.134725, P_max=50)
        for entry in path:
            for k, v in entry.items():
                if isinstance(v, float):
                    self.assertTrue(math.isfinite(v), f"Non-finite {k}={v}")

    def test_pmax_limits_primes(self):
        """T4: P_max properly limits the number of primes in path."""
        path_50 = self.mod.spiral_path(0.5, 14.134725, P_max=50)
        path_20 = self.mod.spiral_path(0.5, 14.134725, P_max=20)
        self.assertGreater(len(path_50), len(path_20))
        for entry in path_20:
            self.assertLessEqual(entry['prime'], 20)


# ---------------------------------------------------------------------------
# T5 — spiral_metrics
# ---------------------------------------------------------------------------
class TestBridge09SpiralMetrics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.path = cls.mod.spiral_path(0.5, 14.134725, P_max=100)
        cls.metrics = cls.mod.spiral_metrics(cls.path)

    def test_returns_dict(self):
        """T5: spiral_metrics returns a dict."""
        self.assertIsInstance(self.metrics, dict)

    def test_expected_keys(self):
        """T5: Required keys present in metrics."""
        for k in ('radius_initial', 'radius_final', 'radius_ratio',
                  'tightness', 'winding_number', 'inward_fraction', 'n_primes'):
            self.assertIn(k, self.metrics, f"Missing key: {k}")

    def test_radius_initial_positive(self):
        """T5: radius_initial > 0 (first prime contributes nonzero step)."""
        self.assertGreater(self.metrics['radius_initial'], 0.0)

    def test_radius_ratio_definition(self):
        """T5: radius_ratio = radius_final / radius_initial."""
        r0 = self.metrics['radius_initial']
        rf = self.metrics['radius_final']
        ratio = self.metrics['radius_ratio']
        self.assertAlmostEqual(ratio, rf / r0, places=12)

    def test_tightness_definition(self):
        """T5: tightness = 1 − radius_ratio."""
        ratio = self.metrics['radius_ratio']
        tightness = self.metrics['tightness']
        self.assertAlmostEqual(tightness, 1.0 - ratio, places=12)

    def test_inward_fraction_bounded(self):
        """T5: inward_fraction ∈ [0, 1]."""
        f = self.metrics['inward_fraction']
        self.assertGreaterEqual(f, 0.0)
        self.assertLessEqual(f, 1.0)

    def test_n_primes_matches_path(self):
        """T5: n_primes equals path length."""
        self.assertEqual(self.metrics['n_primes'], len(self.path))

    def test_empty_path_returns_empty_dict(self):
        """T5: spiral_metrics([]) returns empty dict."""
        result = self.mod.spiral_metrics([])
        self.assertEqual(result, {})


# ---------------------------------------------------------------------------
# T6 — sigma_selective_spiral_scan
# ---------------------------------------------------------------------------
class TestBridge09SigmaSelectiveScan(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        # Use small P_max and n_zeros to keep test fast
        cls.results = cls.mod.sigma_selective_spiral_scan(P_max=50, n_zeros=3)

    def test_returns_list(self):
        """T6: sigma_selective_spiral_scan returns a list."""
        self.assertIsInstance(self.results, list)

    def test_nonempty(self):
        """T6: Results list is non-empty."""
        self.assertGreater(len(self.results), 0)

    def test_entry_has_sigma_and_T(self):
        """T6: Each result entry has 'sigma' and 'T' keys."""
        for entry in self.results:
            self.assertIn('sigma', entry)
            self.assertIn('T', entry)

    def test_entry_has_tightness(self):
        """T6: Each result entry has 'tightness'."""
        for entry in self.results:
            self.assertIn('tightness', entry)

    def test_sigma_values_in_grid(self):
        """T6: All sigma values come from SIGMA_GRID."""
        for entry in self.results:
            self.assertIn(entry['sigma'], self.mod.SIGMA_GRID)

    def test_tightness_is_finite(self):
        """T6: All tightness values are finite numbers."""
        for entry in self.results:
            t = entry.get('tightness', float('nan'))
            if not math.isnan(t):
                self.assertTrue(math.isfinite(t))

    def test_n_results_count(self):
        """T6: n_zeros zeros + (n_zeros-1) midpoints, each × len(SIGMA_GRID)."""
        n_zeros = 3
        n_sigma = len(self.mod.SIGMA_GRID)
        n_T_points = n_zeros + (n_zeros - 1)  # zeros + midpoints
        expected = n_T_points * n_sigma
        self.assertEqual(len(self.results), expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
