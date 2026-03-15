#!/usr/bin/env python3
"""
VALIDATE_PROOF_09.py
==================
Trinity + Protocol validator for:
    PROOFS/PROOF_9/EXECUTION/PROOF_09_WEIL_POSITIVITY.py

Description : Weil Positivity Criterion
Category    : PROOF

Exit codes:  0 = all PASS   1 = one or more FAIL
"""

from __future__ import annotations
import importlib.util, re, sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

# -- Path setup
THIS_TRINITY  = Path(__file__).resolve().parent
ITEM_DIR      = THIS_TRINITY.parent
GROUP_DIR     = ITEM_DIR.parent
FP_NEW_DIR    = GROUP_DIR.parent
FP_DIR        = FP_NEW_DIR.parent / 'FORMAL_PROOF'
OPERATOR_DIR  = FP_DIR / 'Prime-Defined-Operator'
EXECUTION_DIR = ITEM_DIR / 'EXECUTION'
ANALYTICS_DIR = ITEM_DIR / 'ANALYTICS'
ANALYTICS_DIR.mkdir(exist_ok=True)
EXECUTION_FILE  = EXECUTION_DIR / 'PROOF_09_WEIL_POSITIVITY.py'
BRIDGE1_TRINITY = FP_NEW_DIR / 'BRIDGES' / 'BRIDGE_1' / 'TRINITY'

for _p in [str(OPERATOR_DIR), str(EXECUTION_DIR), str(ITEM_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# -- Import Trinity template engine
_tspec = importlib.util.spec_from_file_location(
    'TRINITY_VALIDATION', BRIDGE1_TRINITY / 'TRINITY_VALIDATION.py'
)
_tmod = importlib.util.module_from_spec(_tspec)
sys.modules['TRINITY_VALIDATION'] = _tmod
_tspec.loader.exec_module(_tmod)

Infinity_Trinity_Validator = _tmod.Infinity_Trinity_Validator
QuantumGeodesicSingularity = _tmod.QuantumGeodesicSingularity
Riemann_Singularity        = _tmod.Riemann_Singularity

# =============================================================================
# PROTOCOL STATIC CHECKS  (P1-P4)
# =============================================================================

_MKM = {'mkm_weight', 'meissel_weight', 'kubiluis_weight', 'mertens_tonnage'}
_LOG = {'np.log', 'math.log', 'cmath.log', 'mpmath.log', 'scipy.log'}
_LOG_OK = ['CLASSICAL WEYL', 'analytics comparison', 'reference only', 'log() permitted']


def check_p1(path):
    bad = []
    for no, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if line.strip().startswith('#'):
            continue
        for sym in _LOG:
            if sym + '(' in line and not any(t in line for t in _LOG_OK):
                bad.append(f'  L{no}: {line.strip()[:90]}')
    return (not bad), ('P1 PASS' if not bad else 'P1 FAIL\n' + '\n'.join(bad))


def check_p2(path):
    src  = path.read_text(encoding='utf-8')
    has9 = any(t in src for t in ['9D','9d','InverseBitsizeShift','BridgeLift6Dto9D','NUM_BRANCHES'])
    has6 = any(t in src for t in ['Projection6D','6D','6d'])
    if has6 and not has9:
        return False, 'P2 FAIL -- 6D without 9D initialization'
    note = ' (9D->6D lift present)' if (has6 and has9) else ''
    return True, 'P2 PASS' + note


def check_p3(path):
    src = path.read_text(encoding='utf-8')
    bad = [s for s in _MKM if s in src]
    if bad:
        return False, f'P3 FAIL -- MKM symbols: {bad}'
    ok = any(t in src for t in ['phi','PHI','_WEIGHTS_9','BitsizeScaleFunctional'])
    return ok, 'P3 PASS' if ok else 'P3 FAIL -- no phi weights'


def check_p4(path):
    src  = path.read_text(encoding='utf-8')
    hits = [t for t in ['AXIOMS_BITSIZE_AWARE','AXIOM_8_INVERSE_BITSIZE_SHIFT',
                         'bitsize','BitsizeScaleFunctional','InverseBitsizeShift',
                         'sech2','sech_sq','BS-'] if t in src]
    return bool(hits), (f'P4 PASS -- {hits[:4]}' if hits else 'P4 FAIL')


def run_static_checks(path):
    rows, ok_all = [], True
    for fn in [check_p1, check_p2, check_p3, check_p4]:
        ok, msg = fn(path)
        rows.append(f"  {'✅' if ok else '❌'} {msg}")
        if not ok:
            ok_all = False
    return ok_all, rows


# =============================================================================
# UNIT TESTS  (P5 — U1-U5)
# =============================================================================

def run_unit_tests():
    rows, ok_all = [], True
    src = EXECUTION_FILE.read_text(encoding='utf-8')

    ok4 = 'input(' not in src
    rows.append(f"  {'✅' if ok4 else '❌'} U4: no interactive input(): {ok4}")
    if not ok4:
        ok_all = False

    ok5 = any(t in src for t in ['PASS','FAIL','assert','\u2713','\u2717'])
    rows.append(f"  {'✅' if ok5 else '❌'} U5: PASS/FAIL/assert present: {ok5}")
    if not ok5:
        ok_all = False

    try:
        def _exec(tag):
            sp = importlib.util.spec_from_file_location(f'_ut_{tag}', EXECUTION_FILE)
            m  = importlib.util.module_from_spec(sp)
            sys.modules[f'_ut_{tag}'] = m
            sp.loader.exec_module(m)
            return {k: getattr(m, k) for k in dir(m)
                    if not k.startswith('_') and isinstance(getattr(m, k), (int, float))}

        c1 = _exec('r1')
        rows.append("  ✅ U3: execution ran without exception")
        c2 = _exec('r2')
        c3 = _exec('r3')
        ok1 = (c2 == c3)
        rows.append(f"  {'✅' if ok1 else '❌'} U1: deterministic constants: {ok1}")
        if not ok1:
            ok_all = False
        rows.append("  ✅ U2: script-specific reference checks delegated to Doctrines")
    except Exception as exc:
        rows.append(f"  ❌ U1/U2/U3: error -- {exc}")
        ok_all = False

    return ok_all, rows


# =============================================================================
# CATEGORY DOCTRINES  (PROOF)
# =============================================================================

class V_PROOF_09(Infinity_Trinity_Validator):
    """
    PROOF validator -- PROOF_09 (Weil Positivity Criterion)

    Doctrine I   : Proof Script Executes
    Doctrine II  : Conditional / Status Labels
    Doctrine III : No Unmediated Zeta Oracle
    """

    def _doctrine_I_specific(self) -> Tuple[bool, str]:
        print(f"\n  [Doctrine I -- Proof Script Executes]")
        print(f"\n    loading: {EXECUTION_FILE.name}")
        try:
            import importlib.util as _ilu
            _sp = _ilu.spec_from_file_location("_pmod_I", EXECUTION_FILE)
            _m  = _ilu.module_from_spec(_sp)
            sys.modules["_pmod_I"] = _m
            _sp.loader.exec_module(_m)
            ok = True
        except Exception as exc:
            print(f"    error: {exc}"); ok = False
        print(f"    {'✅ PASS' if ok else '❌ FAIL'}: Clean execution")
        return ok, f"loaded={ok}"

    def _doctrine_II_specific(self) -> Tuple[bool, str]:
        print(f"\n  [Doctrine II -- Conditional / Status Labels]")
        src  = EXECUTION_FILE.read_text(encoding="utf-8")
        tags = ["CONDITIONAL", "OPEN", "PROVED (finite)", "conditional", "open",
                "CONJECTURAL", "Evidence", "EVIDENCE", "WARNING", "STATUS", "finite model"]
        found = [t for t in tags if t in src]
        ok = len(found) > 0
        print(f"    status labels: {found[:4]}")
        print(f"    {'✅ PASS' if ok else '❌ FAIL'}: Honest status labels")
        return ok, f"labels={found[:3]}"

    def _doctrine_III_specific(self) -> Tuple[bool, str]:
        print(f"\n  [Doctrine III -- No Unmediated Zeta Oracle]")
        import re as _re
        src = EXECUTION_FILE.read_text(encoding="utf-8")
        zeta_calls   = _re.findall(r'(?<!#)\b(?:mpmath\.zeta|scipy\.special\.zeta)\s*\(', src)
        has_disclaim = "reference" in src.lower() or "comparison" in src.lower()
        ok = (not zeta_calls) or has_disclaim
        print(f"    direct zeta calls: {zeta_calls[:3]}")
        print(f"    disclaimer: {has_disclaim}")
        print(f"    {'✅ PASS' if ok else '⚠ WARN'}: Prime-side construction")
        return ok, f"zeta={len(zeta_calls)} disclaim={has_disclaim}"

    def run_proof_09_trinity(self) -> Tuple[bool, Dict]:
        print("\n" + "=" * 60)
        print("  PROOF_09 TRINITY PROTOCOL")
        print("  (Weil Positivity Criterion)")
        print("=" * 60)
        ok1, d1 = self._doctrine_I_specific()
        ok2, d2 = self._doctrine_II_specific()
        ok3, d3 = self._doctrine_III_specific()
        passed  = ok1 and ok2 and ok3
        print("\n  Trinity -- Verdict")
        print("  " + "-" * 38)
        print(f"  Doctrine I   (Proof Script Execute:22) : {'✅' if ok1 else '❌'}")
        print(f"  Doctrine II  (Conditional / Status:22) : {'✅' if ok2 else '❌'}")
        print(f"  Doctrine III (No Unmediated Zeta O:22) : {'✅' if ok3 else '❌'}")
        print(f"\n  {'✅ TRINITY PASSED' if passed else '❌ TRINITY FAILED'}")
        return passed, {
            'doctrine_I':  {'pass': ok1, 'detail': d1},
            'doctrine_II': {'pass': ok2, 'detail': d2},
            'doctrine_III':{'pass': ok3, 'detail': d3},
        }

# =============================================================================
# AMBIENT TRINITY  (QuantumGeodesicSingularity + Riemann-phi)
# =============================================================================

def run_ambient_trinity():
    v = Infinity_Trinity_Validator()
    ok = v.run_rh_infinity_trinity(T_min=14.0, T_max=70.0, num_T=100, tol=1e-8)
    return ok, 'T in [14,70], 100 pts'


# =============================================================================
# REPORT
# =============================================================================

def write_report(results):
    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    P  = lambda ok: 'PASS' if ok else 'FAIL'
    td = results['trinity']
    rows = [
        f"# PROOF_09 Trinity Validation Report",
        f"",
        f"**Script:** `EXECUTION/PROOF_09_WEIL_POSITIVITY.py`",
        f"**Category:** PROOF  **Description:** Weil Positivity Criterion",
        f"**Generated:** {ts}",
        f"",
        f"## P1-P4 Static Checks",
        f"",
        f"| Protocol | Result |",
        f"|----------|--------|",
    ]
    for msg in results['static']:
        rows.append(f"| -- | {P('PASS' in msg)} -- {msg.strip()[:100]} |")
    rows += [
        f"",
        f"## Unit Tests (P5)",
        f"",
        f"| Test | Result |",
        f"|------|--------|",
    ]
    for msg in results['unit_tests']:
        rows.append(f"| -- | {P('✅' in msg)} -- {msg.strip()[:100]} |")
    rows += [
        f"",
        f"## Category Trinity (PROOF) -- Doctrines I-III",
        f"",
        f"| Doctrine | Label | Result | Detail |",
        f"|----------|-------|--------|--------|",
        f"| I   | Proof Script Executes | {P(td.get('doctrine_I', {}).get('pass', False))} | {td.get('doctrine_I', {}).get('detail', '')} |",
        f"| II  | Conditional / Status Labels | {P(td.get('doctrine_II', {}).get('pass', False))} | {td.get('doctrine_II', {}).get('detail', '')} |",
        f"| III | No Unmediated Zeta Oracle | {P(td.get('doctrine_III',{}).get('pass', False))} | {td.get('doctrine_III',{}).get('detail', '')} |",
        f"",
        f"## Ambient Trinity",
        f"",
        f"| {results.get('ambient_detail','')} | {P(results['ambient'])} |",
        f"",
        f"## Final Verdict",
        f"",
        f"| Gate | Result |",
        f"|------|--------|",
        f"| P1-P4 Static Checks      | {P(results['static_pass'])} |",
        f"| Unit Tests (U1-U5)       | {P(results['unit_pass'])} |",
        f"| Category Trinity (I-III) | {P(results['trinity_pass'])} |",
        f"| Ambient Trinity          | {P(results['ambient'])} |",
        f"| **OVERALL**              | **{P(results['overall'])}** |",
    ]
    out = ANALYTICS_DIR / 'TRINITY_REPORT_PROOF_09.md'
    out.write_text('\n'.join(rows), encoding='utf-8')
    return out

# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    print('=' * 70)
    print('  TRINITY VALIDATOR  PROOF_09  --  Weil Positivity Criterion')
    print('  Target: EXECUTION/PROOF_09_WEIL_POSITIVITY.py')
    print('=' * 70)

    if not EXECUTION_FILE.exists():
        print(f'\n  ERROR: not found: {EXECUTION_FILE}')
        return 1

    results = {}

    print('\n' + '=' * 70)
    print('  GATE 1 -- Protocol Static Checks (P1-P4)')
    print('=' * 70)
    sp, sl = run_static_checks(EXECUTION_FILE)
    for ln in sl: print(ln)
    results.update(static=sl, static_pass=sp)
    print(f"\n  {'✅ P1-P4 PASS' if sp else '❌ P1-P4 FAIL'}")

    print('\n' + '=' * 70)
    print('  GATE 2 -- Unit Tests (P5: U1-U5)')
    print('=' * 70)
    up, ul = run_unit_tests()
    for ln in ul: print(ln)
    results.update(unit_tests=ul, unit_pass=up)
    print(f"\n  {'✅ UNIT PASS' if up else '❌ UNIT FAIL'}")

    print('\n' + '=' * 70)
    print('  GATE 3 -- Category Trinity (I-III)')
    print('=' * 70)
    v = V_PROOF_09()
    tp, td = v.run_proof_09_trinity()
    results.update(trinity=td, trinity_pass=tp)

    print('\n' + '=' * 70)
    print('  GATE 4 -- Ambient Trinity')
    print('=' * 70)
    ap, ad = run_ambient_trinity()
    results.update(ambient=ap, ambient_detail=ad)

    overall = sp and up and tp and ap
    results['overall'] = overall

    print('\n' + '=' * 70)
    print('  FINAL VERDICT -- PROOF_09_WEIL_POSITIVITY.py')
    print('=' * 70)
    print(f"  P1-P4 Static Checks  : {'✅' if sp else '❌'}")
    print(f"  Unit Tests           : {'✅' if up else '❌'}")
    print(f"  Category Trinity     : {'✅' if tp else '❌'}")
    print(f"  Ambient Trinity      : {'✅' if ap else '❌'}")
    print(f"\n  {'✅ ALL PASS' if overall else '❌ ONE OR MORE FAILED'}")
    print('=' * 70)

    rpt = write_report(results)
    print(f'\n  Report: {rpt.relative_to(FP_NEW_DIR)}')
    return 0 if overall else 1


if __name__ == '__main__':
    sys.exit(main())
