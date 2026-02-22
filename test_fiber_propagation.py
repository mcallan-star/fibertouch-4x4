import numpy as np
from fiber_propagation import (gaussian_pulse, split_step_fourier,
                               dispersion_length, energy, rms_width)


def _grid(n=4096, span=80.0):
    return np.linspace(-span / 2, span / 2, n)


def test_sw_p1_dispersive_broadening():     # SW-P1
    t = _grid(); T0, b2 = 1.0, -1.0
    A0 = gaussian_pulse(t, T0=T0); LD = dispersion_length(T0, b2); z = 2 * LD
    A = split_step_fourier(A0, t, z, 2000, beta2=b2)
    exp = rms_width(A0, t) * np.sqrt(1 + (z / LD) ** 2)
    assert abs(rms_width(A, t) - exp) / exp < 0.02


def test_sw_p3_energy_conservation():       # SW-P3
    t = _grid(); A0 = gaussian_pulse(t, T0=1.0)
    A = split_step_fourier(A0, t, 5.0, 1000, beta2=-1.0, gamma=1.0)
    assert abs(energy(A, t) - energy(A0, t)) / energy(A0, t) < 1e-6


def test_sw_p4_loss_decay():                # SW-P4
    t = _grid(); A0 = gaussian_pulse(t, T0=1.0); al, z = 0.2, 3.0
    A = split_step_fourier(A0, t, z, 1000, beta2=-1.0, alpha=al)
    assert abs(energy(A, t) / energy(A0, t) - np.exp(-al * z)) < 1e-4
