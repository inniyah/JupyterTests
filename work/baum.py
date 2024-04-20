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

Soluciones = []

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

hs = np.linspace(0, 40, 400)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Dibujamos rho_simple vs. rho_aerocalc (en escal;a logarítmica)

#~ plt.plot(hs, np.vectorize(rho_simple)(hs), 'r')
#~ plt.yscale("log")
#~ plt.plot(hs, np.vectorize(rho_aerocalc)(hs), 'b')
#~ plt.yscale("log")
#~ plt.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# simulación con rho_simple

rho = rho_simple
sol = solve_ivp(diff_eq, [0, 1000], [y0, v0], t_eval=np.linspace(0, 1000, 10001), events=hit_ground) # Guardo datos cada 0.1 s

Soluciones.append( sol )

#~ f = plt.figure()
#~ plt.plot(sol.t, sol.y[0])
#~ f = plt.figure()
#~ plt.plot(sol.t, abs(sol.y[1]))
#~ plt.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Velocidad del sonido en función de la altura

# Temperatura del aire en función de la altura
# https://www.tiempo.com/noticias/ciencia/el-modelo-atmosfera-teorica-isa-para-estudiar-el-comportamiento-de-la-atmosfera-real.html
def temper(h): # h en Km, results in Kelvin
    t0 = 273.15 + 20 # https://es.weatherspark.com/m/3855/10/Tiempo-promedio-en-octubre-en-Nuevo-M%C3%A9xico-M%C3%A9xico
    if h <= 11:
        return t0 - 6.5 * h
    if h <= 20:
        return t0 - 6.5 * 11
    if h <= 32:
        return t0 - 6.5 * 11 + \
            (h - 20) * 1.0
    return t0 - 6.5 * 11 + \
        (32 - 20) * 1.0 + \
        (h - 32) * 2.8

# Vamos a representarla, pero en Celsius

#~ heights = np.linspace(0, 40, 300)
#~ tempers = np.vectorize(temper)(heights) - 273.15
#~ f = plt.figure()
#~ plt.plot(tempers, heights)

# Representamos también la velocidad del sonido en función de la altura

# Estamos usando esta: http://hyperphysics.phy-astr.gsu.edu/hbasees/Sound/souspe3.html
# Otra opción: https://openstax.org/books/f%C3%ADsica-universitaria-volumen-1/pages/17-2-velocidad-del-sonido

#~ v_sonido = 331.4 + 0.6 * tempers
#~ f = plt.figure()
#~ plt.plot(v_sonido, heights)

#~ plt.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Calcular cuándo viaja a una velocidad superior a la del sonido

# Eventos relevantes

# Cuándo toca el suelo: h = y[0] pasa por cero (definición de evento) de positvo a negativo (direction -1)
def hit_ground(t, y): # t in seconds, y = [ y in m, v in m/s ]
    return y[0] # Nos importan los pasos por cero
hit_ground.terminal = True
hit_ground.direction = -1

# Cuándo la velocidad v = y[1] supera o deja de superar la velocidad del sonico (ambas direcciones)
def speed_of_sound(t, y): # t in seconds, y = [ y in m, v in m/s ]
    temp = temper(y[0] / 1000)
    vsonido = 331 * np.sqrt(temp) / 273.15
    return y[1] - vsonido # Nos importan los pasos por cero

# Con qué puntos queremos quedarnos para representarlo, además de los eventos relevantes
t_eval = np.linspace(0, 1000, 1001)

# Solucionba todos nuestros problemas
sol = solve_ivp(diff_eq, [0, 1000], [y0, v0], t_eval=t_eval, events=( hit_ground, speed_of_sound ) )

#~ # Represento la velocidad del señor
#~ f = plt.figure()
#~ plt.plot(sol.t, abs(sol.y[1]), 'b')

#~ # Represento la velocidad del sonido a la altura en la que está el señor en cada momento
#~ tempers = np.vectorize(temper)(sol.y[0] / 1000)
#~ v_sonido = 331 * np.sqrt(tempers / 273.15)
#~ plt.plot(sol.t, v_sonido, 'r')

#~ # Dibujo las rayas
#~ tsupera = sol.t[ np.where(abs(sol.y[1]) >= v_sonido) ]
#~ tiempo0 = min(tsupera)
#~ tiempo1 = max(tsupera)
#~ print(tiempo0, tiempo1)
#~ plt.plot([tiempo0, tiempo0], [0, 350], 'k')
#~ plt.plot([tiempo1, tiempo1], [0, 350], 'k')
#~ plt.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# rho = rho_aerocalc
def rho(h): # h en Km, results in kg/l = kg/dm**3
    return std_atm.alt2density(h * 1000, alt_units='m', density_units='kg/m**3')

def temper(h): # h en Km, results in Kelvin
    return std_atm.alt2temp(h * 1000, alt_units='m', temp_units='K')

def hit_ground(t, y): # t in seconds, y = [ y in m, v in m/s ]
    return y[0]
hit_ground.terminal = True
hit_ground.direction = -1

def speed_of_sound(t, y): # t in seconds, y = [ y in m, v in m/s ]
    temp = temper(y[0] / 1000) # en Kelvin
    vsonido = 331 * np.sqrt(temp / 273.15)
    return y[1] - vsonido

sol = solve_ivp(diff_eq, [0, 1000], [y0, v0], t_eval=np.linspace(0, 1000, 10001), events=( hit_ground, speed_of_sound )) # Guardo datos cada 0.1 s

Soluciones.append( sol )

#~ f = plt.figure()
#~ plt.plot(sol.t, sol.y[0])
#~ f = plt.figure()
#~ plt.plot(sol.t, abs(sol.y[1]))
#~ f = plt.figure()
#~ plt.plot(abs(sol.y[1]), sol.y[0])

# Velocidad vs. velocidad del sonido

#~ f = plt.figure()
#~ plt.plot(sol.t, abs(sol.y[1]), 'b')

#~ tempers = np.vectorize(temper)(sol.y[0] / 1000)
#~ v_sonido = 331 * np.sqrt(tempers / 273.15)
#~ plt.plot(sol.t, v_sonido, 'r')

#~ tsupera = sol.t[ np.where(abs(sol.y[1]) >= v_sonido) ]
#~ tiempo0 = min(tsupera)
#~ tiempo1 = max(tsupera)
#~ print(tiempo0, tiempo1)
#~ plt.plot([tiempo0, tiempo0], [0, 350], 'k')
#~ plt.plot([tiempo1, tiempo1], [0, 350], 'k')

#~ plt.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Caso sin rozamiento

def diff_eq(t, X):
    return [ X[1], g ]

# rho = rho_aerocalc
def rho(h): # h en Km, results in kg/l = kg/dm**3
    return std_atm.alt2density(h * 1000, alt_units='m', density_units='kg/m**3')

def temper(h): # h en Km, results in Kelvin
    return std_atm.alt2temp(h * 1000, alt_units='m', temp_units='K')

def hit_ground(t, y): # t in seconds, y = [ y in m, v in m/s ]
    return y[0]
hit_ground.terminal = True
hit_ground.direction = -1

def speed_of_sound(t, y): # t in seconds, y = [ y in m, v in m/s ]
    temp = temper(y[0] / 1000) # en Kelvin
    vsonido = 331 * np.sqrt(temp / 273.15)
    return y[1] - vsonido

sol = solve_ivp(diff_eq, [0, 1000], [y0, v0], t_eval=np.linspace(0, 1000, 10001), events=( hit_ground, speed_of_sound )) # Guardo datos cada 0.1 s

Soluciones.append( sol )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

side = 15000.0
thk = 300.0
wallB = vp.box (pos=vp.vector(0, 0, 0), size=vp.vector(2*side + thk, thk, 2*side + thk), color=vp.color.red)

balls = [
    vp.sphere (color=vp.color.green, radius=2.0, make_trail=True, retain=10),
    vp.sphere (color=vp.color.yellow, radius=2.0, make_trail=True, retain=10),
    vp.sphere (color=vp.color.magenta, radius=2.0, make_trail=True, retain=10),
]

balls[0].pos = vp.vector (0.0, y0, 0.0)
balls[1].pos = vp.vector (0.0, y0, 0.0)
balls[2].pos = vp.vector (0.0, y0, 0.0)

arrow_dir = vp.vec(1500, -2500, 2500)

arrows = []
texts = []
for n, ball in enumerate(balls):
    arrow = vp.arrow(
        pos = ball.pos + arrow_dir * 5/4,
        axis = -arrow_dir,
        shaftwidth = 400,
        color = vp.color.white
    )
    txt = vp.text(
        text = ['A', 'B', 'C'][n],
        pos = ball.pos + arrow_dir * 6/4 + vp.vec(0, -1000, 0),
        align = 'center',
        height = 1500,
        color = [vp.color.green, vp.color.yellow, vp.color.magenta][n],
        billboard = True,
        emissive = True
    )
    arrows.append(arrow)
    texts.append(txt)

t = min([ min(sol.t) for sol in Soluciones ])
tmax = max([ max(sol.t) for sol in Soluciones ])

dt = 1 # Se genera una imagen cada segundo del tiempo simulado

while t <= tmax:
    vp.rate(10)
    for sol_num in range(0, len(Soluciones)):
        sol = Soluciones[sol_num]
        ball = balls[sol_num]
        arrow = arrows[sol_num]
        txt = texts[sol_num]
        i_ante = np.where(sol.t <= t)[0][-1]
        #~ i_post = np.where(sol.t >= t)[0][0]
        h, v = sol.y[:, i_ante]
        ball.pos = vp.vector ((sol_num - 1) * 10000.0, h, 0.0)
        arrow.pos = ball.pos + arrow_dir * 5/4
        txt.pos = ball.pos + arrow_dir * 6/4 + vp.vec(0, -1000, 0)
    t += dt
