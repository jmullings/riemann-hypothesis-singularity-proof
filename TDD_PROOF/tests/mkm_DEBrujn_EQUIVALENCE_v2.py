import math
import os
from typing import Tuple

import numpy as np
from scipy.fft import fft


# ----------------------------------------------------------------------
# 0. Zeros loader
# ----------------------------------------------------------------------


def load_riemann_zeros(
    filename: str = "RiemannZeros.txt",
    max_zeros: int = 99999,
) -> np.ndarray:
    if not os.path.exists(filename):
        return np.array([], dtype=float)

    gammas = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.replace(",", " ").split()
            if not parts:
                continue
            try:
                g = float(parts[0])
            except ValueError:
                continue
            gammas.append(abs(g))
            if len(gammas) >= max_zeros:
                break

    if not gammas:
        return np.array([], dtype=float)

    arr = np.array(gammas, dtype=float)
    arr = np.sort(arr)
    return arr


# ----------------------------------------------------------------------
# 1. Hardy Z(t): Riemann–Siegel / eta-based approximation
# ----------------------------------------------------------------------


def hardy_z(t: float) -> float:
    t = abs(t)
    if t < 7.0:
        re, im = 0.0, 0.0
        for n in range(1, 201):
            sign = -1.0 if (n % 2 == 0) else 1.0
            term = sign / math.sqrt(n)
            angle = -t * math.log(n)
            re += term * math.cos(angle)
            im += term * math.sin(angle)
        ln2 = math.log(2.0)
        a = 1.0 - math.sqrt(2.0) * math.cos(-t * ln2)
        b = -math.sqrt(2.0) * math.sin(-t * ln2)
        den = a * a + b * b
        if den == 0.0:
            return 0.0
        z_re = (re * a + im * b) / den
        z_im = (im * a - re * b) / den
        return -math.hypot(z_re, z_im)

    n_max = int(math.sqrt(t / (2.0 * math.pi)))
    theta = (
        0.5 * t * math.log(t / (2.0 * math.pi))
        - 0.5 * t
        - math.pi / 8.0
        + 1.0 / (48.0 * t)
    )
    s = 0.0
    for n in range(1, n_max + 1):
        s += math.cos(theta - t * math.log(n)) / math.sqrt(n)
    z = 2.0 * s

    p = math.sqrt(t / (2.0 * math.pi)) - n_max
    cp = math.cos(2.0 * math.pi * p)
    if abs(cp) > 1e-6:
        sign = 1.0 if (n_max % 2 == 0) else -1.0
        z += (
            sign
            * (t / (2.0 * math.pi)) ** (-0.25)
            * math.cos(2.0 * math.pi * (p * p - p - 1.0 / 16.0))
            / cp
        )
    return z


# ----------------------------------------------------------------------
# 2. Sech^2 kernel
# ----------------------------------------------------------------------


def sech2(u: float, H: float) -> float:
    x = u / H
    if abs(x) > 30.0:
        return 0.0
    c = math.cosh(x)
    return 1.0 / (c * c)


def sech2_kernel_grid(H: float, dt: float, window: float) -> Tuple[np.ndarray, np.ndarray]:
    n = int(2.0 * window / dt) + 1
    if n % 2 == 0:
        n += 1
    u = np.linspace(-window, window, n)
    k = np.array([sech2(ui, H) for ui in u], dtype=float)
    return u, k


# ----------------------------------------------------------------------
# 3. Time-domain Λ(T,H)
# ----------------------------------------------------------------------


def lambda_sech2(T: float, H: float, dt: float = 0.01, window: float = None) -> float:
    if window is None:
        window = 12.0 * H
    u, k = sech2_kernel_grid(H, dt, window)
    du = u[1] - u[0]
    z_vals = np.array([hardy_z(T + ui) for ui in u], dtype=float)
    z2 = z_vals * z_vals
    num = float(np.sum(z2 * k) * du)
    den = float(np.sum(k) * du)
    return num / den if den > 0.0 else 0.0


# ----------------------------------------------------------------------
# 4. Spectral Λ(T,H) via weighted FFT (corrected Parseval scaling)
# ----------------------------------------------------------------------


def lambda_sech2_spectral(
    T: float,
    H: float,
    dt: float = 0.01,
    window: float = None,
) -> float:
    """
    Λ(T,H) = ∫ |Z(T+u)|² sech²(u/H) du / (2H)

    Implemented via:
        g(u) = sech²(u/H)
        f(u) = Z(T+u) * sqrt(g(u)) = Z(T+u) * sech(u/H)

        ∫ |f(u)|² du  ≈ du * Σ |f_i|²
                     = (du / N) * Σ |FFT(f)_k|²   (unscaled FFT)
    """
    if window is None:
        window = 12.0 * H

    u, k = sech2_kernel_grid(H, dt, window)  # k = sech²(u/H)
    du = u[1] - u[0]

    z_vals = np.array([hardy_z(T + ui) for ui in u], dtype=float)

    # Weight by sqrt(g) = sech(u/H)
    weight = np.sqrt(k)
    z_weighted = z_vals * weight

    N = len(u)
    Z_hat = fft(z_weighted)

    # Discrete Parseval: ∫ |f|² du ≈ (du / N) * sum |FFT(f)|²
    energy = np.sum(np.abs(Z_hat) ** 2) * (du / N)

    # Normalise by ∫ g(u) du = 2H
    return energy / (2.0 * H) if H > 0.0 else 0.0


# ----------------------------------------------------------------------
# 5. Equivalence scan on a T-grid
# ----------------------------------------------------------------------


def scan_lambda_sech2_equivalence(
    T_values: np.ndarray,
    H: float = 0.5,
    dt: float = 0.01,
    window: float = None,
    report_every: int = 10,
):
    Lambda_time = np.zeros_like(T_values, dtype=float)
    Lambda_spec = np.zeros_like(T_values, dtype=float)
    diffs = np.zeros_like(T_values, dtype=float)

    for idx, T in enumerate(T_values):
        L_t = lambda_sech2(T=T, H=H, dt=dt, window=window)
        L_s = lambda_sech2_spectral(T=T, H=H, dt=dt, window=window)
        Lambda_time[idx] = L_t
        Lambda_spec[idx] = L_s
        diffs[idx] = L_t - L_s

        if report_every and (idx + 1) % report_every == 0:
            max_abs_diff = float(np.max(np.abs(diffs[: idx + 1])))
            ratio = L_s / L_t if L_t != 0.0 else float("nan")
            print(
                f"[{idx + 1}/{len(T_values)}] "
                f"T ≈ {T:.6f}, Λ_time = {L_t:.6e}, Λ_spec = {L_s:.6e}, "
                f"Λ_spec/Λ_time = {ratio:.6e}, max |Δ| so far = {max_abs_diff:.3e}"
            )

    return T_values, Lambda_time, Lambda_spec, diffs


# ----------------------------------------------------------------------
# 6. Equivalence scan on all zeros
# ----------------------------------------------------------------------


def scan_all_zeros_equivalence(
    H: float = 0.5,
    dt: float = 0.01,
    window: float = None,
    zeros_file: str = "RiemannZeros.txt",
    max_zeros: int = 99999,
    report_every: int = 500,
):
    gammas = load_riemann_zeros(zeros_file, max_zeros=max_zeros)
    if gammas.size == 0:
        raise RuntimeError("No zeros loaded from file.")

    Lambda_time = np.zeros_like(gammas, dtype=float)
    Lambda_spec = np.zeros_like(gammas, dtype=float)
    diffs = np.zeros_like(gammas, dtype=float)

    for idx, g in enumerate(gammas):
        L_t = lambda_sech2(T=g, H=H, dt=dt, window=window)
        L_s = lambda_sech2_spectral(T=g, H=H, dt=dt, window=window)
        Lambda_time[idx] = L_t
        Lambda_spec[idx] = L_s
        diffs[idx] = L_t - L_s

        if report_every and (idx + 1) % report_every == 0:
            max_abs_diff = float(np.max(np.abs(diffs[: idx + 1])))
            ratio = L_s / L_t if L_t != 0.0 else float("nan")
            print(
                f"[{idx + 1}/{gammas.size}] "
                f"γ ≈ {g:.6f}, Λ_time = {L_t:.6e}, Λ_spec = {L_s:.6e}, "
                f"Λ_spec/Λ_time = {ratio:.6e}, max |Δ| so far = {max_abs_diff:.3e}"
            )

    return gammas, Lambda_time, Lambda_spec, diffs


# ----------------------------------------------------------------------
# 7. Main
# ----------------------------------------------------------------------


if __name__ == "__main__":
    # 1) T-grid equivalence test near first zeros
    T_grid = np.linspace(10.0, 60.0, 51)
    T_vals, L_time_grid, L_spec_grid, diffs_grid = scan_lambda_sech2_equivalence(
        T_values=T_grid,
        H=0.5,
        dt=0.01,
        window=None,
        report_every=5,
    )
    np.savez(
        "lambda_sech2_equivalence_Tgrid.npz",
        T_vals=T_vals,
        Lambda_time=L_time_grid,
        Lambda_spec=L_spec_grid,
        diffs=diffs_grid,
    )
    print("T-grid equivalence scan complete.")
    print(f"T-grid max |Λ_time - Λ_spec| = {np.max(np.abs(diffs_grid)):.3e}")

    # 2) Full zero-scan equivalence test (up to 99,999 zeros)
    gammas, L_time_zeros, L_spec_zeros, diffs_zeros = scan_all_zeros_equivalence(
        H=0.5,
        dt=0.01,
        window=None,
        zeros_file="RiemannZeros.txt",
        max_zeros=99999,
        report_every=500,
    )
    np.savez(
        "lambda_sech2_equivalence_zeros.npz",
        gammas=gammas,
        Lambda_time=L_time_zeros,
        Lambda_spec=L_spec_zeros,
        diffs=diffs_zeros,
    )
    print("Zero-scan equivalence complete.")
    print(f"Zero-scan max |Λ_time - Λ_spec| = {np.max(np.abs(diffs_zeros)):.3e}")