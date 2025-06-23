# Tomás de Camino Beck
# Escuela de Sistemas Inteligentes
# Universidad Cenfotec

import board
from ideaboard import IdeaBoard
from time import sleep
from hcsr04 import HCSR04
import random

sonar = HCSR04(board.IO25, board.IO26)
ib = IdeaBoard()

# Sensores infrarrojos
sen1 = ib.AnalogIn(board.IO36)
sen2 = ib.AnalogIn(board.IO39)
sen3 = ib.AnalogIn(board.IO34)
sen4 = ib.AnalogIn(board.IO35)
infrarrojos = [sen1, sen2, sen3, sen4]

def arreglo_a_entero(bits):
    valor = 0
    for bit in bits:
        valor = (valor << 1) | bit
    return valor

def leer_sensores(infrarrojos, valor_critico=10000):
    return [int(sen.value < valor_critico) for sen in infrarrojos]

def line_status(infrarrojos, valor_critico=10000):
    sensores = leer_sensores(infrarrojos, valor_critico)
    return arreglo_a_entero(sensores)

def forward(t, speed):
    ib.pixel = (0, 255, 0)
    ib.motor_1.throttle = speed
    ib.motor_2.throttle = speed
    sleep(t)

def backward(t, speed):
    ib.pixel = (150, 255, 0)
    ib.motor_1.throttle = -speed
    ib.motor_2.throttle = -speed
    sleep(t)

def left(t, speed):
    ib.pixel = (50, 55, 100)
    ib.motor_1.throttle = -speed
    ib.motor_2.throttle = speed
    sleep(t)

def right(t, speed):
    ib.pixel = (50, 55, 100)
    ib.motor_1.throttle = speed
    ib.motor_2.throttle = -speed
    sleep(t)

def stop():
    ib.pixel = (0, 0, 0)
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0

def randomTurn(t, speed):
    dir = random.choice([-1, 1])
    ib.pixel = (255, 0, 0)
    ib.motor_1.throttle = dir * -speed
    ib.motor_2.throttle = dir * speed
    sleep(t)

def lookForward():
    stop()
    dist = sonar.dist_cm()
    sleep(0.2)
    return dist

def forwardCheck(t, speed, th):
    d = int(t / 0.01)
    for i in range(d):
        status = line_status(infrarrojos, th)
        if status == 0:
            forward(0.01, speed)
        elif status >= 1 and status <= 3:
            forward(0.5, 1)
        else:
            stop()
            sleep(0.3)
            backward(1, 0.3)
            randomTurn(1, 0.3)
            break

def espiralBusqueda():
    for i in range(5):
        forward(0.1, 0.3)
        right(0.15 + i * 0.02, 0.3)
        if sonar.dist_cm() < 30:
            break
    # Si no encontró oponente, intenta contraataque lateral
    contraataque_lateral()

def defensaReaccion(status):
    if status in [4, 8, 12]:  # Línea delante
        stop()
        backward(0.5, 0.5)
        randomTurn(0.5, 0.5)
    elif status in [1, 2, 3]:  # Línea atrás
        forward(0.4, 1)
    else:
        stop()
        backward(0.3, 0.3)
        randomTurn(0.5, 0.3)

# NUEVAS FUNCIONES ESTRATÉGICAS
def finta():
    backward(0.3, 0.3)
    sleep(0.2)
    forward(0.4, 1)

def contraataque_lateral():
    randomTurn(0.3, 0.5)
    forward(0.3, 1)

###### LOOP PRINCIPAL MEJORADO CON INTELIGENCIA ######
th = 2950
while True:
    sensores = line_status(infrarrojos, th)

    if sensores != 0:
        defensaReaccion(sensores)
        continue

    distancia = sonar.dist_cm()

    if distancia > -1 and distancia < 30:
        # Atacamos si hay enemigo cerca
        if random.random() < 0.3:  # 30% de probabilidad de hacer finta
            finta()
        else:
            forwardCheck(0.3, 1, th)
    else:
        # No hay enemigo, buscar con táctica
        espiralBusqueda()
