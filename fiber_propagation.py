"""split-step fourier NLSE solver. wip - just gvd + loss for now."""
import numpy as np


def gaussian_pulse(t, t0=0.0, T0=1.0, P0=1.0):
    return np.sqrt(P0) * np.exp(-((t - t0) ** 2) / (2.0 * T0 ** 2))


def dispersion_length(T0, beta2):
    return np.inf if beta2 == 0 else T0 ** 2 / abs(beta2)


def energy(A, t):
    return float(np.sum(np.abs(A) ** 2) * (t[1] - t[0]))


def rms_width(A, t):
    power = np.abs(A) ** 2
    norm = np.sum(power)
    mean = np.sum(t * power) / norm
    return float(np.sqrt(np.sum((t - mean) ** 2 * power) / norm))


def split_step_fourier(A0, t, distance, n_steps, beta2=0.0, gamma=0.0, alpha=0.0):
    A = np.asarray(A0, dtype=complex).copy()
    N = len(t); dt = t[1] - t[0]
    w = 2.0 * np.pi * np.fft.fftfreq(N, d=dt)
    dz = float(distance) / int(n_steps)
    lin_half = np.exp((1j * beta2 / 2.0 * w ** 2 - alpha / 2.0) * (dz / 2.0))
    for _ in range(int(n_steps)):
        A = np.fft.ifft(lin_half * np.fft.fft(A))
        A = A * np.exp(1j * gamma * np.abs(A) ** 2 * dz)
        A = np.fft.ifft(lin_half * np.fft.fft(A))
    return A
