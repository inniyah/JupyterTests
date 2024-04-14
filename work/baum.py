#!/home/inniyah/venv/bin/python3

import numpy as np
import scipy as sp
import vpython as vp

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

from scipy.integrate import solve_ivp
from aerocalc import std_atm

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# https://www.20minutos.es/deportes/noticia/felix-baumgartner-traje-ansiedad-creer-salto-1781818/0/
m = 115 # kg

# https://enjoy.es/magazine/2022/10/01/historia-del-deporte-extremo-10-anos-del-salto-de-felix-baumgartner/
Vmax = 1357.6 # km/h

# https://es.wikipedia.org/wiki/Red_Bull_Stratos
Ttotal = 260 # s

y0 = 39068 # m
v0 = 0 # m/s

CD = 0.4

A = 1.0 # m**2

g = -9.81 # m/s**2

def rho_simple(h): # h en Km, results in g/l = g/dm**3 = kg/m**3
    rho_0 = 1.225 # g/dm**3 = kg/m**3
    h0 = 0 # km
    H = 8.5 # km
    return rho_0 * np.exp( - (h - h0) / H ) # g/dm**3

def rho_aerocalc(h): # h en Km, results in kg/l = kg/dm**3
    return std_atm.alt2density(h * 1000, alt_units='m', density_units='kg/m**3')

def diff_eq(t, X):
    D = 1 / 2 * rho(X[0] / 1000) * X[1]**2 * CD * A
    return [ X[1], D / m + g ]

def hit_ground(t, y):
    return y[0]

hit_ground.terminal = True

hit_ground.direction = -1

t_eval = np.linspace(0, 1000, 1001)

f = plt.figure()
hs = np.linspace(0, 40, 400)

#~ plt.plot(hs, np.vectorize(rho_simple)(hs), 'r')
#~ plt.yscale("log")
#~ plt.plot(hs, np.vectorize(rho_aerocalc)(hs), 'b')
#~ plt.yscale("log")
#~ plt.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

rho = rho_simple
sol = solve_ivp(diff_eq, [0, 1000], [y0, v0], t_eval=np.linspace(0, 1000, 1001), events=hit_ground) # Guardo datos cada 1 s

#~ f = plt.figure()
#~ plt.plot(sol.t, sol.y[0])
#~ f = plt.figure()
#~ plt.plot(sol.t, abs(sol.y[1]))
#~ plt.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

rho = rho_aerocalc
sol = solve_ivp(diff_eq, [0, 1000], [y0, v0], t_eval=np.linspace(0, 1000, 10001), events=hit_ground) # Guardo datos cada 0.1 s

#~ f = plt.figure()
#~ plt.plot(sol.t, sol.y[0])
#~ f = plt.figure()
#~ plt.plot(sol.t, abs(sol.y[1]))
#~ plt.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

side = 10000.0
thk = 300.0
wallB = vp.box (pos=vp.vector(0, 0, 0), size=vp.vector(2*side + thk, thk, 2*side + thk), color=vp.color.red)

ball = vp.sphere (color=vp.color.green, radius=2.0, make_trail=True, retain=200)
ball.pos = vp.vector (0.0, 10.0, 0.0)

t = min(sol.t)
tmax = max(sol.t)
dt = 1 # Se genera una imagen cada segundo del tiempo simulado

while t < tmax:
    vp.rate(60)
    i_ante = np.where(sol.t <= t)[0][-1]
    i_post = np.where(sol.t >= t)[0][0]
    h, v = sol.y[:, i_ante]
    ball.pos = vp.vector (0.0, h, 0.0)
    t += dt
