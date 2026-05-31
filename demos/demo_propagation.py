"""Sanity demo: push a Gaussian through the solver, show energy is kept."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
from fiber_propagation import gaussian_pulse, split_step_fourier, energy
t = np.linspace(-40, 40, 4096)
A0 = gaussian_pulse(t, T0=1.0)
A = split_step_fourier(A0, t, 5.0, 1000, beta2=-1.0, gamma=1.0)
print("energy in/out: %.6f / %.6f" % (energy(A0, t), energy(A, t)))
