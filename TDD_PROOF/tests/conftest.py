"""
TDD_PROOF test configuration.

Adds the TDD_PROOF root to sys.path so `engine` imports work from any cwd.
Provides shared fixtures for the entire test suite.
"""

import sys
import os
import pytest
import numpy as np

# Ensure TDD_PROOF/ is on the path
_TDD_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TDD_ROOT not in sys.path:
    sys.path.insert(0, _TDD_ROOT)


# ─────────────── SHARED FIXTURES ─────────────────────────────────────────────

@pytest.fixture
def H():
    """Default smoothing bandwidth."""
    return 3.0


@pytest.fixture
def riemann_zeros_30():
    """First 30 non-trivial Riemann zeros (imaginary parts)."""
    return np.array([
        14.135, 21.022, 25.011, 30.425, 32.935,
        37.586, 40.919, 43.327, 48.005, 49.774,
        52.970, 56.446, 59.347, 60.832, 65.113,
        67.080, 69.546, 72.067, 75.705, 77.145,
        79.337, 82.910, 84.735, 87.425, 88.809,
        92.492, 94.651, 95.871, 98.831, 101.318,
    ])


@pytest.fixture
def spectrum_9d():
    """60 lowest 9D eigenvalues from the sech² operator."""
    from engine.spectral_9d import get_9d_spectrum
    return get_9d_spectrum(n_lowest=60)


@pytest.fixture
def uniform_spectrum():
    """Uniform grid spectrum for universality tests."""
    return np.linspace(10, 100, 30)


@pytest.fixture
def random_spectrum():
    """Random points for adversarial PSD tests."""
    return np.sort(np.random.RandomState(42).uniform(5, 120, 30))


@pytest.fixture(params=[1.0, 2.0, 3.0, 5.0], ids=['H=1', 'H=2', 'H=3', 'H=5'])
def H_sweep(request):
    """Parametrized H values spanning the operating range."""
    return request.param
