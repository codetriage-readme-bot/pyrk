import numpy as np

import neutronics 
import thermal_hydraulics
from scipy.integrate import ode

t0 = 0.0
dt = 0.01
tf = 1.0
timesteps = tf/dt + 1

n_precursor_groups = 6
n_decay_groups = 3
component_names = {"fuel":0, "cool":1, "mod":2, "refl":3}
n_components = len(component_names)
n_entries = 1 + n_precursor_groups + n_decay_groups + n_components

coeffs = {"fuel":-3.7, "cool":-1.8, "mod":-0.7, "refl":1.8}

y = np.zeros(shape = (n_entries, timesteps), dtype=float)
dydt = np.zeros(shape = (n_entries, timesteps), dtype=float)

p = np.zeros(shape= (1, timesteps), dtype=float)
dpdt = np.zeros(shape= (1, timesteps), dtype=float)

ksi = np.zeros(shape= (n_precursor_groups, timesteps), dtype=float)
dksidt = np.zeros(shape= (n_precursor_groups, timesteps), dtype=float)

w = np.zeros(shape= (n_decay_groups, timesteps), dtype=float)
dwdt = np.zeros(shape= (n_decay_groups, timesteps), dtype=float)

temp = np.zeros(shape= (n_components, timesteps), dtype=float)
dtempdt = np.zeros(shape= (n_components, timesteps), dtype=float)

ne = neutronics.Neutronics()
th = thermal_hydraulics.ThermalHydraulics()

def f(t, y, coeffs):
    lams = ne._data._lambdas
    temp_i = 2 + n_precursor_groups + n_decay_groups
    temp_f = 3 + n_precursor_groups + n_decay_groups + n_components
    f = {"p":ne.dpdt(t, dt, temp, coeffs, y[0],
        y[1:n_precursor_groups+1])}
    for j in range(0, n_precursor_groups):
        name = "ksi"+str(j)
        f[name] = ne.dksidt(t, y[0], y[j+1], j)
    for k in range(0, n_decay_groups):
        name = "w"+str(k)
        f[name] = ne.dwdt(k)
    for c in component_names:
        f[c] = th.dtempdt(c)
    return f.values()

def f_n(t, y, coeffs):
    lams = ne._data._lambdas
    temp_i = 2 + n_precursor_groups + n_decay_groups
    temp_f = 3 + n_precursor_groups + n_decay_groups + n_components
    f = {"p":ne.dpdt(t, dt, temp, coeffs, y[0],
        y[1:n_precursor_groups+1])}
    for j in range(0, n_precursor_groups):
        name = "ksi"+str(j)
        f[name] = ne.dksidt(t, y[0], y[j+1], j)
    for k in range(0, n_decay_groups):
        name = "w"+str(k)
        f[name] = ne.dwdt(k)
    return f.values()

def f_th(t, y, power):
    f = {}
    for c in component_names:
        f[c] = th.dtempdt(c, y, power)
    return f.values()

def y0(): 
    y0 = [236] # 236 MWth?
    for j in range(0, n_precursor_groups):
        y0.append(0)
    for k in range(0, n_decay_groups):
        y0.append(ne._data._omegas[j])
    for name, num in component_names.iteritems():
        y0.append(th.temp(name, 0))
    assert len(y0) == n_entries
    return y0

def y0_th():
def y0_n():



def solve():
    n = ode(f_n).set_integrator('dopri15')
    n.set_initial_value(y0(), t0).set_f_params(coeffs)
    th = ode(f_th).set_integrator('dopri15')
    n.set_initial_value(y0(), t0).set_f_params(coeffs)
    while n.successful() and n.t < tf:
        n.integrate(n.t+dt)
        print("%g %g" % (n.t, n.y))
        th.integrate(th.t+dt)
        print("%g %g" % (th.t, th.y))
        update(n.y, th.y)

#def f(t, y, arg1):
#    return [1j*arg1*y[0] + y[1], -arg1*y[1]**2]
#def jac(t, y, arg1):    
#    return [[1j*arg1, 1], [0, -arg1*2*y[1]]]

#r = ode(f, jac).set_integrator('zvode', method='bdf', with_jacobian=True)
#r.set_initial_value(y0(), t0).set_f_params(coeffs, Lambda, lams, ksis).set_jac_params(2.0)