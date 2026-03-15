"""
conftest.py — SIGMAS test suite
================================
Adds the old PROOFSCRIPTS directories to sys.path so that
SIGMA_4 through SIGMA_10 source scripts can resolve their
EQ3_SIGMA_SELECTIVITY_LIFT (and its transitive dependencies
EQ1_GLOBAL_CONVEXITY_XI, EQ2_STRICT_CONVEXITY_AWAY,
EQ3_UBE_CONVEXITY_SIGMA) via normal Python import machinery.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent

_PROOFSCRIPT_DIRS = [
    _REPO / "FORMAL_PROOF/RH_Eulerian_PHI_PROOF/SIGMA_SELECTIVITY/EQ1_GLOBAL_CONVEXITY_XI/PROOFSCRIPTS",
    _REPO / "FORMAL_PROOF/RH_Eulerian_PHI_PROOF/SIGMA_SELECTIVITY/EQ2_STRICT_CONVEXITY_AWAY/PROOFSCRIPTS",
    _REPO / "FORMAL_PROOF/RH_Eulerian_PHI_PROOF/SIGMA_SELECTIVITY/EQ3_UBE_CONVEXITY_SIGMA/PROOFSCRIPTS",
]

for _d in _PROOFSCRIPT_DIRS:
    _s = str(_d)
    if _s not in sys.path:
        sys.path.insert(0, _s)
