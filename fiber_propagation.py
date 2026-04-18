"""Split-step Fourier solver for IR pulse propagation in the fibers (NLSE).

dA/dz = -i (beta2/2) d^2A/dt^2 + i gamma |A|^2 A - (alpha/2) A

alpha is the *power* attenuation coefficient (1/m). Used to sanity-check the
optical model and to reason about pulse integrity over the short fiber runs.
"""
import numpy as np


def gaussian_pulse(t, t0=0.0, T0=1.0, P0=1.0):
    return np.sqrt(P0) * np.exp(-((t - t0) ** 2) / (2.0 * T0 ** 2))


def sech_pulse(t, t0=0.0, T0=1.0, P0=1.0):
    return np.sqrt(P0) / np.cosh((t - t0) / T0)


def dispersion_length(T0, beta2):
    if beta2 == 0:
        return np.inf
    return T0 ** 2 / abs(beta2)


def fundamental_soliton_power(T0, beta2, gamma):
    if gamma == 0:
        raise ValueError("gamma must be > 0 for a soliton")
    return abs(beta2) / (gamma * T0 ** 2)


def soliton_order(P0, T0, beta2, gamma):
    return np.sqrt(gamma * P0 * T0 ** 2 / abs(beta2))


def energy(A, t):
    dt = t[1] - t[0]
    return float(np.sum(np.abs(A) ** 2) * dt)


def rms_width(A, t):
    power = np.abs(A) ** 2
    norm = np.sum(power)
    mean = np.sum(t * power) / norm
    return float(np.sqrt(np.sum((t - mean) ** 2 * power) / norm))


def split_step_fourier(A0, t, distance, n_steps, beta2=0.0, gamma=0.0, alpha=0.0):
    """Symmetric split-step Fourier integration of the NLSE."""
    A = np.asarray(A0, dtype=complex).copy()
    N = len(t)
    dt = t[1] - t[0]
    w = 2.0 * np.pi * np.fft.fftfreq(N, d=dt)
    dz = float(distance) / int(n_steps)
    # half-step linear operator (dispersion + loss)
    lin_half = np.exp((1j * beta2 / 2.0 * w ** 2 - alpha / 2.0) * (dz / 2.0))
    for _ in range(int(n_steps)):
        A = np.fft.ifft(lin_half * np.fft.fft(A))
        A = A * np.exp(1j * gamma * np.abs(A) ** 2 * dz)  # full nonlinear step
        A = np.fft.ifft(lin_half * np.fft.fft(A))
    return A
\n# note: could add third-order dispersion (beta3) later if pulses get short\n