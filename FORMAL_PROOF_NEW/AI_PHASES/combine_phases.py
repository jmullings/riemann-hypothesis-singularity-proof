#!/usr/bin/env python3
"""
combine_phases.py
=================
Combines all 10 PHASE_*.py files into a single RH_PROOF_COMPLETE.py
placed in EXECUTION/.

Run:  python3 combine_phases.py
"""

import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # FORMAL_PROOF_NEW/
SRC_DIR  = os.path.join(BASE, 'AI_PHASES')
OUT_FILE = os.path.join(BASE, 'SELECTIVITY', 'PATH_COMPLETE', 'EXECUTION', 'RH_PROOF_COMPLETE.py')

PHASES = [
    ('PHASE_01_FOUNDATIONS.py',        1,  'PHASE 01 — FOUNDATIONS'),
    ('PHASE_02_BRIDGE.py',             2,  'PHASE 02 — RIEMANN-SIEGEL BRIDGE + SPEISER'),
    ('PHASE_03_PRIME_GEOMETRY.py',     3,  'PHASE 03 — PRIME GEOMETRY'),
    ('PHASE_04_EVIDENCE.py',           4,  'PHASE 04 — EVIDENCE'),
    ('PHASE_05_UNIFORM_BOUND.py',      5,  'PHASE 05 — UNIFORM BOUND'),
    ('PHASE_06_ANALYTIC_CONVEXITY.py', 6,  'PHASE 06 — ANALYTIC CONVEXITY'),
    ('PHASE_07_MELLIN_SPECTRAL.py',    7,  'PHASE 07 — MELLIN SPECTRAL'),
    ('PHASE_08_CONTRADICTION_A3.py',   8,  'PHASE 08 — CONTRADICTION & A3 OPERATOR BOUND'),
    ('PHASE_09_PHI_CURVATURE.py',      9,  'PHASE 09 — φ-CURVATURE MEAN-VALUE BOUND'),
    ('PHASE_10_COMPLETION.py',         10, 'PHASE 10 — COMPLETION & FINAL PROOF EQUATION'),
]

# ─────────────────────────────── helpers ──────────────────────────────────

def banner(title, width=78):
    bar = '═' * width
    return f"\n\n# {bar}\n# {title.center(width)}\n# {bar}\n\n"


def remove_top_function(text, funcname):
    """
    Remove a top-level (0-indent) function definition by name.
    Scans line-by-line: skips the 'def funcname' line and all subsequent
    lines that are blank or start with whitespace (the body), stopping at
    the first non-empty, non-indented line.
    """
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r'^def ' + re.escape(funcname) + r'\s*[\(\:]', line):
            # consume function body
            i += 1
            while i < len(lines):
                l = lines[i]
                if l == '' or l[0:1] in (' ', '\t'):
                    i += 1
                else:
                    break
            # eat any trailing blank lines that belong logically to the
            # removed function (the blank lines *after* the body but
            # before the next def)
            continue
        result.append(line)
        i += 1
    return '\n'.join(result)


def strip_module_docstring(text):
    """Remove shebang and the top-level module docstring (triple-quoted)."""
    # shebang
    text = re.sub(r'^#!/usr/bin/env python3\n', '', text)
    # triple-quoted docstring at very top (possibly after shebang removal)
    text = re.sub(r'^"""[\s\S]*?"""\n', '', text)
    return text


def strip_imports_and_paths(text, phase_num):
    """Remove sys/os imports, sys.path.insert, cross-phase imports."""
    text = re.sub(r'^import\s+sys\b[^\n]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^import\s+os\b[^\n]*\n',  '', text, flags=re.MULTILINE)
    text = re.sub(r'^sys\.path\.insert[^\n]*\n', '', text, flags=re.MULTILINE)
    # Multi-line parenthesized cross-phase imports: from PHASE_NN_NAME import (\n...\n)
    text = re.sub(
        r'^from\s+PHASE_\d+\S*\s+import\s*\([\s\S]*?\)\n',
        '', text, flags=re.MULTILINE)
    # Single-line cross-phase imports
    text = re.sub(r'^from\s+PHASE_\d+[^\n]+\n', '', text, flags=re.MULTILINE)
    # Remove typing imports (unused in combined file — added once in header)
    text = re.sub(r'^from\s+typing[^\n]+\n', '', text, flags=re.MULTILINE)
    # Remove stdlib imports already present in the file header (all phases)
    text = re.sub(r'^import\s+math\b[^\n]*\n',  '', text, flags=re.MULTILINE)
    text = re.sub(r'^import\s+cmath\b[^\n]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^import\s+numpy[^\n]*\n',   '', text, flags=re.MULTILINE)
    text = re.sub(r'^import\s+time\b[^\n]*\n',  '', text, flags=re.MULTILINE)
    text = re.sub(r'^from\s+scipy[^\n]+\n',     '', text, flags=re.MULTILINE)
    return text


def strip_dup_constants(text, phase_num):
    """Remove constant definitions already present in the shared section."""
    # Phase 01 may have NDIM; DTYPE; CDTYPE on one compound line
    if phase_num == 1:
        text = re.sub(r'^NDIM\s*=\s*\d+\s*;.*\n', '', text, flags=re.MULTILINE)
    # All phases — strip any top-level re-definition of shared constants
    text = re.sub(r'^PI\s*=\s*math\.pi[^\n]*\n',      '', text, flags=re.MULTILINE)
    text = re.sub(r'^TWO_PI\s*=[^\n]*\n',              '', text, flags=re.MULTILINE)
    text = re.sub(r'^DTYPE\s*=[^\n]*\n',               '', text, flags=re.MULTILINE)
    text = re.sub(r'^CDTYPE\s*=[^\n]*\n',              '', text, flags=re.MULTILINE)
    text = re.sub(r'^NDIM\s*=[^\n]*\n',                '', text, flags=re.MULTILINE)
    if phase_num > 1:
        # _N_MAX_RS = 10000 (Phase 02) — alias to shared _N_MAX
        text = re.sub(r'^_N_MAX_RS\s*=[^\n]*\n',           '', text, flags=re.MULTILINE)
        # _N_MAX = 10000 or 5000
        text = re.sub(r'^_N_MAX\s*=\s*(10000|5000)\n',     '', text, flags=re.MULTILINE)
        # _LOG_TABLE = np.array(...) multi-line; dtype=DTYPE or dtype=np.float64
        text = re.sub(
            r'^_LOG_TABLE\s*=\s*np\.array\(\s*\n\s*\[0\.0\][^\n]*\)\n',
            '', text, flags=re.MULTILINE)
        # Single-line fallback
        text = re.sub(r'^_LOG_TABLE\s*=\s*np\.array[^\n]*\n', '', text, flags=re.MULTILINE)

    if phase_num >= 9:
        text = re.sub(r'^H_STAR\s*=[^\n]*\n',      '', text, flags=re.MULTILINE)
    if phase_num == 10:
        text = re.sub(r'^CONT_NORM\s*=[^\n]*\n',   '', text, flags=re.MULTILINE)
    return text


def strip_dup_functions(text, phase_num):
    """Remove function definitions that have already appeared in earlier phases."""
    if phase_num == 7:
        # sech2_fourier already defined in PH06
        text = remove_top_function(text, 'sech2_fourier')

    if phase_num == 8:
        # sech2_kernel and sech2_fourier already defined
        text = remove_top_function(text, 'sech2_kernel')
        text = remove_top_function(text, 'sech2_fourier')

    if phase_num == 9:
        # These are placed in the SHARED HELPERS section before PH09
        for fn in ['_vectors', 'Lambda_H', 'Lambda_H_pp', 'D0_squared']:
            text = remove_top_function(text, fn)

    if phase_num == 10:
        # These are placed in the SHARED HELPERS section before PH09
        for fn in ['_build_vectors', '_quad_real', '_Lambda_H', '_Lambda_H_pp', '_D0_squared']:
            text = remove_top_function(text, fn)

    return text


def strip_lazy_imports(text):
    """Remove inline 'from PHASE_XX import ...' inside function bodies."""
    # Multi-line parenthesized lazy imports (indented)
    text = re.sub(
        r'^\s+from\s+PHASE_\d+\S*\s+import\s*\([\s\S]*?\)\n',
        '', text, flags=re.MULTILINE)
    # Single-line lazy imports (indented)
    text = re.sub(r'^\s+from\s+PHASE_\d+[^\n]+\n', '', text, flags=re.MULTILINE)
    return text


def strip_main_block(text):
    """Remove 'if __name__ == ...' run-block at end of each phase file."""
    text = re.sub(
        r'\nif __name__\s*==\s*["\']__main__["\']\s*:\n[\s\S]*',
        '', text)
    return text


def compress_blank_lines(text, max_consecutive=2):
    """Collapse runs of >max_consecutive blank lines to max_consecutive."""
    pattern = r'(\n{' + str(max_consecutive + 1) + r',})'
    replacement = '\n' * max_consecutive
    return re.sub(pattern, replacement, text)


def process_phase(filename, phase_num, title):
    filepath = os.path.join(SRC_DIR, filename)
    with open(filepath, encoding='utf-8') as f:
        text = f.read()

    text = strip_module_docstring(text)
    text = strip_imports_and_paths(text, phase_num)
    text = strip_dup_constants(text, phase_num)
    text = strip_dup_functions(text, phase_num)
    text = strip_lazy_imports(text)
    text = strip_main_block(text)
    text = compress_blank_lines(text)

    return banner(title) + text.strip() + '\n'


# ─────────────────────────────── Content blocks ───────────────────────────

FILE_HEADER = '''\
#!/usr/bin/env python3
"""
RH_PROOF_COMPLETE.py
====================
σ-Selectivity Proof of the Riemann Hypothesis
All 10 phases combined into a single executable file.

Phase structure
---------------
Phase 01 — Foundations           (9-prime basis, φ-metric, F₂ curvature)
Phase 02 — RS Bridge + Speiser   (Riemann-Siegel, chi-factor, Speiser thm)
Phase 03 — Prime Geometry        (PSS spiral, x* constructions, sech²)
Phase 04 — Evidence              (interference, null model, zeros vs random)
Phase 05 — Uniform Bound         (averaged F₂, sech² smoothing)
Phase 06 — Analytic Convexity    (Fourier decomposition, F̄₂ = 4M₂ + R)
Phase 07 — Mellin Spectral       (operator T_H, Parseval identity)
Phase 08 — Contradiction & A3    (smoothed contradiction, diagonal dominance)
Phase 09 — φ-Curvature Theorem   (Re⟨TD²b,b⟩ ≥ 0 verification)
Phase 10 — Completion            (final proof equation, consolidation)

Usage
-----
    python3 RH_PROOF_COMPLETE.py
"""

import math
import cmath
import time
from typing import Tuple, List, Dict, Optional

import numpy as np
from scipy import integrate

# ════════════════════════════════════════════════════════════════════════════
#                  SHARED CONSTANTS & PRECOMPUTED TABLES
# ════════════════════════════════════════════════════════════════════════════

PI        = math.pi
TWO_PI    = 2.0 * PI
DTYPE     = np.float64
CDTYPE    = np.complex128
NDIM      = 9
H_STAR    = 1.5
CONT_NORM = TWO_PI - 2.0 * H_STAR   # ≈ 3.2832

_N_MAX    = 10000
_LOG_TABLE = np.array(
    [0.0] + [math.log(n) for n in range(1, _N_MAX + 1)], dtype=DTYPE)

'''

SHARED_HELPERS = '''\

# ════════════════════════════════════════════════════════════════════════════
#             SHARED HELPERS  (used by Phase 09 and Phase 10)
# ════════════════════════════════════════════════════════════════════════════


def _build_vectors(T0, sigma, N):
    """Build  b, Db, D²b  where  b_n = n^{-σ} e^{iT₀ ln n}."""
    ns    = np.arange(1, N + 1, dtype=np.float64)
    ln_ns = _LOG_TABLE[1:N + 1]
    amp   = ns ** (-sigma)
    phase = T0 * ln_ns
    b     = amp * (np.cos(phase) + 1j * np.sin(phase))
    return b, ln_ns * b, ln_ns ** 2 * b


_vectors = _build_vectors          # alias used in Phase 09


def _quad_real(T, u, v):
    """Re⟨Tu, v⟩  for real-symmetric T and complex u, v."""
    return float(np.real(np.conj(v) @ (T @ u)))


def _Lambda_H(tau, H):
    """Λ_H(τ) = 2π sech²(τ/H)."""
    u = tau / H
    if abs(u) > 300:
        return 0.0
    return 2.0 * PI / (math.cosh(u) ** 2)


Lambda_H = _Lambda_H               # alias used in Phase 09


def _Lambda_H_pp(tau, H):
    """Λ″_H(τ) = (2π/H²) sech²(τ/H) [4 − 6 sech²(τ/H)]."""
    u = tau / H
    if abs(u) > 300:
        return 0.0
    s  = 1.0 / math.cosh(u)
    s2 = s * s
    return (2.0 * PI / (H * H)) * s2 * (4.0 - 6.0 * s2)


Lambda_H_pp = _Lambda_H_pp         # alias used in Phase 09


def _D0_squared(T0, tau, sigma, N):
    """Compute |D₀(T₀+τ)|²."""
    ln_ns = _LOG_TABLE[1:N + 1]
    amp   = np.arange(1, N + 1, dtype=np.float64) ** (-sigma)
    t     = T0 + tau
    re    = float(np.dot(amp, np.cos(t * ln_ns)))
    im    = float(np.dot(amp, np.sin(t * ln_ns)))
    return re * re + im * im


D0_squared = _D0_squared           # alias used in Phase 09

'''

FILE_FOOTER = '''\

# ════════════════════════════════════════════════════════════════════════════
#                           MASTER RUNNER
# ════════════════════════════════════════════════════════════════════════════


def run_complete_proof():
    """Run all 10 phases sequentially."""
    print("\\n" + "═" * 78)
    print("  RH PROOF COMPLETE  —  σ-Selectivity Proof  (10 phases)")
    print("═" * 78 + "\\n")
    t_total = time.time()

    run_rs_bridge()
    run_speiser()
    run_phase_05()
    run_phase_06()
    run_phase_07()
    run_phase_08()
    run_phase_09()
    run_phase_10()

    elapsed = time.time() - t_total
    print("\\n" + "═" * 78)
    print(f"  ALL PHASES COMPLETE  —  total time: {elapsed:.1f}s")
    print("═" * 78)


if __name__ == "__main__":
    run_complete_proof()
'''

# ─────────────────────────────── main ─────────────────────────────────────

def main():
    parts = [FILE_HEADER]

    for i, (filename, phase_num, title) in enumerate(PHASES):
        print(f"  Processing {filename} ...", end='', flush=True)
        chunk = process_phase(filename, phase_num, title)
        parts.append(chunk)
        print(f" {len(chunk.splitlines())} lines")

        # Insert shared helpers section after Phase 08
        if phase_num == 8:
            parts.append(SHARED_HELPERS)

    parts.append(FILE_FOOTER)

    combined = ''.join(parts)

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(combined)

    total_lines = combined.count('\n')
    print(f"\n  Written to: {OUT_FILE}")
    print(f"  Total lines: {total_lines}")


if __name__ == "__main__":
    main()
