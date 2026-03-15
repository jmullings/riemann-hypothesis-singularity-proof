# DIRICHLET_INFINITY_SERIES.py
#
# Step 7: Dirichlet polynomial wave evaluation
# -------------------------------------------
# Implements:
#   D0(T) = sum_{n<=N} n^{-1/2} e^{-i T log n}
#   D1(T) = d/dT D0(T)
#   Λ_H(t) = 2 * sech^2(H t)
#   Λ_H''(t) = second derivative of Λ_H
#
# And evaluates:
#   PSD term:   <TDb,Db>  = (1/(2π)) ∫ Λ_H(τ) |D1(T0+τ)|^2 dτ
#   Cross term: (1/(4π)) ∫ Λ_H''(τ) |D0(T0+τ)|^2 dτ
#   Central:    Re<T D^2 b,b> = <TDb,Db> - cross term
#
# using finite windows and trapezoidal integration.

import numpy as np
import mpmath as mp

# High precision for stability
mp.mp.dps = 50

# -----------------------------
# Dirichlet polynomials D0, D1
# -----------------------------

def D0(T, N):
    """
    D0(T) = sum_{n<=N} n^{-1/2} e^{-i T log n}
    """
    return mp.nsum(
        lambda k: k**(-0.5) * mp.e**(-1j * T * mp.log(k)),
        [1, N]
    )

def D1(T, N):
    """
    D1(T) = d/dT D0(T)
          = -i sum_{n<=N} (log n) n^{-1/2} e^{-i T log n}
    """
    return mp.nsum(
        lambda k: (-1j * mp.log(k)) * k**(-0.5) * mp.e**(-1j * T * mp.log(k)),
        [1, N]
    )

# -----------------------------
# Kernel Λ_H and Λ_H''
# Λ_H(t) = 2 * sech^2(H t)
# -----------------------------

def Lambda_H(t, H):
    """
    Λ_H(t) = 2 * sech^2(H t)
    """
    return 2.0 * (1.0 / mp.cosh(H * t))**2

def Lambda_H_dd(t, H):
    """
    Λ_H''(t) for Λ_H(t) = 2 * sech^2(H t)

    If f(t) = sech^2(H t), then:
      f'(t)  = -2H sech^2(H t) tanh(H t)
      f''(t) = 4H^2 sech^2(H t) tanh^2(H t) - 2H^2 sech^4(H t)

    Λ_H = 2 f, so Λ_H'' = 2 f''.
    """
    sech = 1.0 / mp.cosh(H * t)
    tanh = mp.tanh(H * t)
    fpp = 4 * H**2 * sech**2 * tanh**2 - 2 * H**2 * sech**4
    return 2.0 * fpp

# ------------------------------------------
# Numerical integrals for Step 7 components
# ------------------------------------------

def dirichlet_wave_energy(T0, N, H, tau_max=10.0, num_tau=2001):
    """
    Approximate integral:
        I(T0) = ∫ Λ_H''(τ) |D0(T0+τ)|^2 dτ
    using a symmetric window [-tau_max, tau_max]
    and trapezoidal rule.
    """
    taus = np.linspace(-tau_max, tau_max, num_tau)
    vals = []
    for tau in taus:
        T = T0 + tau
        d0 = D0(T, N)
        lampp = Lambda_H_dd(tau, H)
        vals.append(lampp * abs(d0)**2)
    vals = np.array(list(map(complex, vals)))
    integral = np.trapz(vals, taus)
    return integral

def cross_term(T0, N, H, tau_max=10.0, num_tau=2001):
    """
    Cross term:
        C(T0) = (1/(4π)) ∫ Λ_H''(τ) |D0(T0+τ)|^2 dτ
    """
    I = dirichlet_wave_energy(T0, N, H, tau_max, num_tau)
    return (1.0 / (4 * mp.pi)) * I

def psd_term(T0, N, H, tau_max=10.0, num_tau=2001):
    """
    PSD term:
        P(T0) = <TDb,Db>
              = (1/(2π)) ∫ Λ_H(τ) |D1(T0+τ)|^2 dτ
    finite-window approximation.
    """
    taus = np.linspace(-tau_max, tau_max, num_tau)
    vals = []
    for tau in taus:
        T = T0 + tau
        d1 = D1(T, N)
        lam = Lambda_H(tau, H)
        vals.append(lam * abs(d1)**2)
    vals = np.array(list(map(complex, vals)))
    integral = np.trapz(vals, taus)
    return (1.0 / (2 * mp.pi)) * integral

# ------------------------------------------
# Central Step 7 quantity
# ------------------------------------------

def central_step7(T0, N, H, tau_max=10.0, num_tau=2001):
    """
    Evaluate central Step 7 equation at (H, N, T0):

        Re⟨T D^2 b,b⟩
        = <TDb,Db> - (1/(4π)) ∫ Λ_H''(τ) |D0(T0+τ)|^2 dτ

    Returns:
        (PSD_term, correction_term, central_value)
    """
    psd = psd_term(T0, N, H, tau_max, num_tau)
    corr = cross_term(T0, N, H, tau_max, num_tau)
    value = psd - corr
    return psd, corr, value

# ------------------------------------------
# Example usage / single sample evaluation
# ------------------------------------------

if __name__ == "__main__":
    H = 1.5
    N = 50
    T0 = 30.0

    psd, corr, val = central_step7(T0, N, H, tau_max=10.0, num_tau=2001)

    print("DIRICHLET_INFINITY_SERIES.py")
    print("H =", H, "N =", N, "T0 =", T0)
    print("PSD term <TDb,Db> ≈", psd)
    print("Correction term (1/(4π))∫Λ_H''|D0|^2 ≈", corr)
    print("Re⟨T D^2 b, b⟩ ≈", val, "  (real part ≈", mp.re(val), ")")
