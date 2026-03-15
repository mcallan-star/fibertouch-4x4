import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from fiber_propagation import sech_pulse, fundamental_soliton_power, split_step_fourier, dispersion_length
t=np.linspace(-40,40,4096); T0,b2=1.0,-1.0
P0=fundamental_soliton_power(T0,b2,1.0); A0=sech_pulse(t,T0=T0,P0=P0)
A=split_step_fourier(A0,t,(np.pi/2)*dispersion_length(T0,b2),3000,beta2=b2,gamma=1.0)
print("peak drift", abs(np.max(np.abs(A))-np.max(np.abs(A0))))  # tiny. holds shape
