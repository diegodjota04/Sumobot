import board
from ideaboard import IdeaBoard
from time import sleep, monotonic
from hcsr04 import HCSR04
import random

ib = IdeaBoard()
sonar = HCSR04(board.IO25, board.IO26)

sen1 = ib.AnalogIn(board.IO36)
sen2 = ib.AnalogIn(board.IO39)
sen3 = ib.AnalogIn(board.IO34)
sen4 = ib.AnalogIn(board.IO35)
sensores = [sen1, sen2, sen3, sen4]

# --- Funciones auxiliares ---
def arreglo_a_entero(bits):
    valor = 0
    for bit in bits:
        valor = (valor << 1) | bit
    return valor

def leer_sensores(sensores, umbral=10000):
    return [int(s.value < umbral) for s in sensores]

def line_status(sensores, umbral=10000):
    return arreglo_a_entero(leer_sensores(sensores, umbral))


def forward(t, speed):
    print(f"Avanzando: {t:.2f}s a velocidad {speed}")
    ib.motor_1.throttle = speed
    ib.motor_2.throttle = speed
    sleep(t)

def backward(t, speed):
    print(f"Retrocediendo: {t:.2f}s a velocidad {speed}")
    ib.motor_1.throttle = -speed
    ib.motor_2.throttle = -speed
    sleep(t)

def right(t, speed):
    print(f"Girando a la derecha: {t:.2f}s a velocidad {speed}")
    ib.motor_1.throttle = speed
    ib.motor_2.throttle = -speed
    sleep(t)

def left(t, speed):
    print(f"Girando a la izquierda: {t:.2f}s a velocidad {speed}")
    ib.motor_1.throttle = -speed
    ib.motor_2.throttle = speed
    sleep(t)

def stop():
    print("Detenido")
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0

# Mejora a randomTurn para evitar bucles
def randomTurn(t, speed):
    dir = random.choice([-1, 1])
    print(f"Giro aleatorio {'izquierda' if dir == -1 else 'derecha'}: {t:.2f}s a velocidad {speed}")
    ib.motor_1.throttle = -dir * speed
    ib.motor_2.throttle = dir * speed
    sleep(t)
    stop()


def leer_distancia_filtrada(intentos=5):
    lecturas = []
    for _ in range(intentos):
        d = sonar.dist_cm()
        if 5 < d < 150:  # Rango válido (evita 0, -1, lecturas erráticas)
            lecturas.append(d)
        sleep(0.01)
    if lecturas:
        return sum(lecturas) / len(lecturas)
    else:
        return -1  # Indicador de error

def finta():
    backward(0.3, 0.3)
    sleep(0.2)
    forward(0.4, 1)

def forwardCheck(t, speed, th):
    for _ in range(int(t / 0.01)):
        status = line_status(sensores, th)
        if status == 0:
            forward(0.01, speed)
        elif status <= 3:
            forward(0.5, 1)
        else:
            stop()
            backward(0.5, 0.3)
            randomTurn(0.4, 0.3)
            break

# --- Variables de control ---
th = 25108
fase = 1
inicio_ataque = None

# --- Bucle principal ---
while True:
    status = line_status(sensores, th)

    # Reacción universal a línea
    if status != 0:
        stop()
        backward(0.5, 0.3)
        randomTurn(0.3, 0.3)
        continue

    distancia = sonar.dist_cm()

    # --- FASE 1: avance inicial forzado (~30 cm) ---
    if fase == 1:
        print("Fase 1: avance al centro")
        distancia_inicial = leer_distancia_filtrada()
        tiempo_inicio = monotonic()

        while True:
            forward(0.05, 0.6)
            distancia_actual = leer_distancia_filtrada()

            if 0 < distancia_actual < distancia_inicial - 30:
                print("Avance completado (30 cm).")
                break

            if monotonic() - tiempo_inicio > 3:
                print("Tiempo máximo de avance alcanzado.")
                break

        stop()
        fase = 2
        inicio_ataque = monotonic()
        continue

    # --- FASE 2-A: ataque inmediato si detecta enemigo (por 2 seg) ---
    if fase == 2:
        print("Fase 2-A: ataque inicial")
        tiempo_actual = monotonic()

        if 0 < distancia < 60:
            print("Enemigo detectado, atacando.")
            if random.random() < 0.2:
                finta()
            else:
                forwardCheck(0.3, 1, th)
            inicio_ataque = monotonic()  # reinicia tiempo si lo sigue viendo

        elif tiempo_actual - inicio_ataque > 2:
            print("No se detectó enemigo. Entrando a patrullaje.")
            fase = 3
            continue
        else:
            right(0.2, 0.3)  # sigue buscando
        continue

    # --- FASE 3: patrullaje continuo ---
    if fase == 3:
        if 0 < distancia < 60:
            print("Enemigo detectado en patrulla, atacando.")
            if random.random() < 0.2:
                finta()
            else:
                forwardCheck(0.3, 1, th)
        else:
            print("Patrullando...")
            forward(0.3, 0.4)
            if random.random() < 0.5:
                right(0.2, 0.4)
            else:
                left(0.2, 0.4)
