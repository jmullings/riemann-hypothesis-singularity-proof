"""
core/ — Conjecture IV Infrastructure Modules

This package provides the trace-class operator, Fredholm determinant,
and geometric growth verification infrastructure for Conjecture IV.
"""

from .PHIWEIGHTEDTRANSFEROPERATOR import (
    PhiWeightedTransferOperator,
    HilbertSpace,
    SymbolicDynamics,
    PHI,
)
from .FINITERANKAPPROXIMATIONS import FiniteRankApproximation
from .FREDHOLMDETERMINANTCALCULATOR import FredholmDeterminant
from .PHIGEOMETRICGROWTHVERIFIER import PhiGeometricGrowthVerifier
from .CONJECTUREVBRIDGE import psipartialsum, TYPEGAP

__all__ = [
    'PhiWeightedTransferOperator',
    'HilbertSpace', 
    'SymbolicDynamics',
    'PHI',
    'FiniteRankApproximation',
    'FredholmDeterminant',
    'PhiGeometricGrowthVerifier',
    'psipartialsum',
    'TYPEGAP',
]
