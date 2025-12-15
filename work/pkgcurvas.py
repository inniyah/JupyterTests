# -*- coding: utf-8 -*-
"""
Created on Tue May 20 11:21:24 2025

@author: cesarm

Definicion paramétrica de curvas habituales en 2D (XZ) y 3D (XYZ)
"""
import numbers
import numpy as np
import sympy as sp
import scipy as sc
import scipy.integrate as scin
# Para salvar la animación en formato mpeg, es necesario instalar el paquete
# conda install -c conda-forge ffmpeg

import numbers
import types
#
# Generación de curvas típicas en 2D y 3D
"""
    sigmoide: A/(1+np.exp(m*p)). Argumentos A (amplitud) m (pendiente)
        recorrido~A[1-ε,ε], intervalo~[ln(A/ε-1)/m] , ε=0.005
        https://es.wikipedia.org/wiki/Funci%C3%B3n_sigmoide
    clotoide: A*int(cos(p^2)), A*int(sin(p^2)). Argumentos A, t0 (inicio)
        intervalo~2A, recorrido~[0,A], maximo en x~0.663*A
        https://es.wikipedia.org/wiki/Clotoide
    helicoide: A*cos(p), A*sin(p). Argumentos A
        DD [0,2 pi]  recorrido [-1,1]
        elipse(p,a,b):
            elipse(p,a,b):
                parabola(p,a):
        https://es.wikipedia.org/wiki/H%C3%A9lice_(geometr%C3%ADa)
    gausiana: A exp(-(p/s)^2)
        intervalo~±2.6s, recorrido~[0,0.995 A]
        https://es.wikipedia.org/wiki/Funci%C3%B3n_gaussiana
"""
#
###############################################################################
#    GEOMETRIA
###############################################################################
def curva3ds(tipo,p,A=1,C=[0,0,0],paso=0, plano="xz",args=[]):
    pass

def curva3d(tipo,p,A=1,C=[0,0,0],paso=0, plano="xz",args=[]):
    """
    Evalua la curva indicada que depende del parámetro p  

    Parameters
    ----------
    p : float
        parámetro
    A : float
        Escalado (amplitud) de la curva
    C : terna de float
        origen de coordenadas
    paso : float o list of floats
        paso en la tercera dimensión
    plano : cadena de caracteres
        plano normal al desplazamiento {xy, xz, yz, 2D}. Por defecto "xz"
    args: list of floats
        argumentos para cada tipo de curva

    Returns
    -------
    data : 2/3D array of floats
        coordenadas bi/tridimensionales de los puntos

    """
    plano = plano.lower()
    if isinstance(C,(tuple,list,np.ndarray)):
        if plano=="2d" and len(C)==2:
            if isinstance(C, np.array):
                C = C.tolist()
            elif isinstance(C,tuple):
                C = list(C)
            else:
                pass
            C.append(0)
    else:
        raise ValueError("Origen de coordenadas mal definido")
    if len(C) != 3:
        raise ValueError("Nº de elementos del origen de coordenadas incorrecto")
    C = np.atleast_2d(C).T
    
    if len(args)>0:
        s = args[0]
    else:
        s = None

    tipo = tipo.lower()[0]
    if tipo == "h":
        x,y = elipse(p,A,A)
    elif tipo == "c":
        x,y = clotoide(p,A,s)
    elif tipo == "l": # bucle, looping
        x,y = clotoide(p,A,s)
        xk  = 2*x[-1] - x[::-1] # calculo de la parte simétrica
        yk  = y[::-1]
        x   = np.concatenate((x,xk[1:]))
        y   = np.concatenate((y,yk[1:]))
        # sustituimos el parametro para la dimension z
        p   = np.cumsum(np.abs(np.diff(x)))
        p   = np.array([0,*p])/p[-1]
    elif tipo == "s":
        x,y = sigmoide(p,A,s)
    elif tipo == "g":
        x,y = gausiana(p,A,s)
    else:
        raise ValueError("tipo de curva no contemplada")

    if isinstance(paso,(int,float)):
        z = paso*p
    elif isinstance(paso,(list,tuple,np.ndarray)) and \
         isinstance(p,(list,tuple,np.ndarray)) and \
         len(paso)==len(p):
            z = paso*p
    else:
        raise ValueError("Valor del paso incoherente")

    if plano=="xy":
        data = np.array([x,y,z])
    elif plano=="xz":
        data = np.array([x,z,y])
    elif plano=="yz":
        data = np.array([z,x,y])
    else:
        raise ValueError("Plano de representación no válido")
    data +=  C
    return data

def sigmoide(p,A=1,s=1):
    """
    Genera la función sigmoide. Util para la bajada inicial
    ===> Parametros
    p : parámetro [float]
    A : amplitud (altura) [float]
    s : controla de pendiente [float]
    ===> Resultados
    x,y : coordenadas de los puntos [1D array of floats]
    """
    x = np.array(p)
    y = A/(1+np.exp(s*x))
    return [x,y]

def elipse(p,a,b):
    """
    Genera una elipse de semiejes a y b 
    ===> Parametros
    p : parámetro [float]
    a,b : semiejes [float]
    ===> Resultados
    x,y : coordenadas de los puntos [1D array of floats]
    """
    x = a*np.cos(p)
    y = b*np.sin(p)
    return [x,y]

def hiperbola(p,a,b):
    """
    Genera una hipérbola de semiejes a y b 
    ===> Parametros
    p : parámetro [float]
    a,b : semiejes [float]
    ===> Resultados
    x,y : coordenadas de los puntos [1D array of floats]
    """
    x = a*np.cosh(p)
    y = b*np.sinh(p)
    return [x,y]

def parabola(p,a):
    """
    Genera una parábola de semiejes a
    ===> Parametros
    p : parámetro [float]
    a : semiejes [float]
    ===> Resultados
    x,y : coordenadas de los puntos [1D array of floats]
    """
    x = p
    y = a*p*p
    return [x,y]

def gausiana(p,A,s):
    """
    Genera una campana de Gauss
    ===> Parametros
    p : parámetro [float]
    A : amplitud (altura) [float]
    s : desviación típica [float]
    ===> Resultados
    x,y : coordenadas de los puntos [1D array of floats]
    """
    x = np.array(p)
    y = A*np.exp(-(p/s)**2)
    return [x,y]

def clotoide(p,A=1,p0=0):
    """
    Genera la curva clotoide 
    ===> Parametros
    p : parámetro [float]
    A : amplitud (altura y anchura) [float]
    s : escala en x [float]
    ===> Resultados
    x,y : coordenadas de los puntos [1D array of floats]
    """
    fx= lambda x: np.cos(x**2)
    fy= lambda x: np.sin(x**2)
    if isinstance(p,(int,float)):
        y, ey = scin.quad(fx, p0, p)
        x, ex = scin.quad(fy, p0, p)
    else:
        p = p.tolist()
        kkx = scin.quad(fx, p0, p[0])
        kky = scin.quad(fy, p0, p[0])
        x = [kkx[0]]
        y = [kkx[0]]
        for i in range(len(p)-1):
            kkx = scin.quad(fx, p[i], p[i+1])
            kky = scin.quad(fy, p[i], p[i+1])
            x.append(kkx[0])
            y.append(kky[0])
        x = np.cumsum(x)
        y = np.cumsum(y)
    return [A*x,A*y]