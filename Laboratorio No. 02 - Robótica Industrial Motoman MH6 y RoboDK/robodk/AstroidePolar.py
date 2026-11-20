from robodk.robolink import *    # API para comunicarte con RoboDK
from robodk.robomath import *    # Funciones matemáticas
from robodk.robodialogs import mbox
import math

#------------------------------------------------
# 1) Conexión a RoboDK e inicialización
#------------------------------------------------
RDK = Robolink()

ROBOT_REAL = False          # True: mueve el MH6; False: solo simulación
IP_ROBOT = "192.168.1.20"

# Elegir un robot (si hay varios, aparece un popup)
robot = RDK.ItemUserPick("Selecciona un robot", ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("No se ha seleccionado un robot válido.")

if ROBOT_REAL:
    robot.Connect(IP_ROBOT)
    estado, msg = robot.ConnectedState()
    if estado != ROBOTCOM_READY:
        raise Exception(f"El robot no está conectado correctamente: {msg}")
    RDK.setRunMode(RUNMODE_RUN_ROBOT)
    print("Robot conectado correctamente.")

#------------------------------------------------
# 2) Cargar el Frame (ya existente) donde se dibuja
#------------------------------------------------
frame_name = "Frame_from_Target1"
frame = RDK.Item(frame_name, ITEM_TYPE_FRAME)
if not frame.Valid():
    raise Exception(f'No se encontró el Frame "{frame_name}" en la estación.')

robot.setPoseFrame(frame)
robot.setPoseTool(robot.PoseTool())

robot.setSpeed(50)     # mm/s
robot.setRounding(1)   # mm

#------------------------------------------------
# 3) Parámetros de la figura (astroide)
#    r = a / (|cos θ|^(2/3) + |sin θ|^(2/3))^(3/2)
#------------------------------------------------
a = 70                 # radio de los picos [mm]
num_points = 81        # con n - 1 múltiplo de 4 los 4 picos caen en puntos de la lista
z_surface = 0          # Z=0 en el plano del frame
z_safe = 50            # el z del frame apunta hacia el tablero: alejarse es -z
inicio = 0             # punto desde el que se reanuda si el script se cortó


def radio(theta):
    return a / (abs(math.cos(theta)) ** (2 / 3) + abs(math.sin(theta)) ** (2 / 3)) ** 1.5


# θ uniforme deja los picos mal muestreados; se toma θ = atan2(sin³u, cos³u) con u uniforme,
# que concentra los puntos en los picos, donde la curva gira (error de cuerda 0,08 mm con 81)
puntos = []
for i in range(num_points):
    u = 2 * math.pi * i / (num_points - 1)
    theta = math.atan2(math.sin(u) ** 3, math.cos(u) ** 3)
    r = radio(theta)
    puntos.append((r * math.cos(theta), r * math.sin(theta)))

# Lista plana de poses: bajar, recorrer y subir, para poder reanudar por índice
x0, y0 = puntos[0]
movimientos = [transl(x0, y0, z_surface - z_safe)]
movimientos += [transl(x, y, z_surface) for x, y in puntos]
movimientos.append(transl(x0, y0, z_surface - z_safe))

#------------------------------------------------
# 3b) Nombres debajo del astroide
#    Fuente de trazo simple en una rejilla de 4 x 6 (u a la derecha, v hacia arriba).
#    En el frame, +x sube por el tablero y +y va a la derecha mirando desde el robot.
#------------------------------------------------
TILDE = [(1.5, 6.8), (2.5, 7.8)]
FUENTE = {
    "A": [[(0, 0), (2, 6), (4, 0)], [(1, 3), (3, 3)]],
    "B": [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)],
          [(3, 3), (4, 2), (4, 1), (3, 0), (0, 0)]],
    "D": [[(0, 0), (0, 6), (2, 6), (4, 4), (4, 2), (2, 0), (0, 0)]],
    "E": [[(4, 6), (0, 6), (0, 0), (4, 0)], [(0, 3), (3, 3)]],
    "G": [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1), (4, 3), (2, 3)]],
    "I": [[(2, 0), (2, 6)]],
    "L": [[(0, 6), (0, 0), (4, 0)]],
    "N": [[(0, 0), (0, 6), (4, 0), (4, 6)]],
    "O": [[(1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)]],
    "R": [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)], [(2, 3), (4, 0)]],
    "S": [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 4), (1, 3), (3, 3), (4, 2), (4, 1), (3, 0),
           (1, 0), (0, 1)]],
    "T": [[(0, 6), (4, 6)], [(2, 6), (2, 0)]],
    "U": [[(0, 6), (0, 1), (1, 0), (3, 0), (4, 1), (4, 6)]],
    "Z": [[(0, 6), (4, 6), (0, 0), (4, 0)]],
}
FUENTE["Á"] = FUENTE["A"] + [TILDE]
FUENTE["Ú"] = FUENTE["U"] + [TILDE]
FUENTE["Ñ"] = FUENTE["N"] + [[(0.5, 6.8), (1.5, 7.6), (2.5, 6.8), (3.5, 7.6)]]

nombres = ["SEBASTIÁN ZÚÑIGA", "DANIEL TORRES"]
x_base = [-94, -109]   # línea base de cada renglón [mm]
alto_letra = 9         # [mm]
z_lift = 10            # alejamiento entre trazos [mm]

escala = alto_letra / 6
avance = 6 * escala
for texto, xb in zip(nombres, x_base):
    y_ini = -(len(texto) * avance - 2 * escala) / 2
    for k, letra in enumerate(texto):
        for trazo in FUENTE.get(letra, []):
            pts = [(xb + v * escala, y_ini + k * avance + u * escala) for u, v in trazo]
            movimientos.append(transl(pts[0][0], pts[0][1], z_surface - z_lift))
            movimientos += [transl(x, y, z_surface) for x, y in pts]
            movimientos.append(transl(pts[-1][0], pts[-1][1], z_surface - z_lift))

#------------------------------------------------
# 4) Movimiento en altura segura sobre el primer punto
#------------------------------------------------
T_H = RDK.Item("Target Home", ITEM_TYPE_TARGET)
if not T_H.Valid():
    raise Exception('No se encontró el target "Target Home" en la estación.')

robot.MoveJ(T_H)
x, y, _ = movimientos[inicio].Pos()
robot.MoveJ(transl(x, y, z_surface - z_safe))

#------------------------------------------------
# 5) Dibujar el astroide punto a punto
#    MoveL bloqueante: el siguiente punto se envía solo cuando el robot terminó el
#    anterior, así un HOLD en el pendant deja de enviar y el buffer del DX100 no se llena
#------------------------------------------------
i = inicio
while i < len(movimientos):
    try:
        robot.MoveL(movimientos[i])
    except TargetReachError:
        raise
    except Exception as e:
        print(f"Robot detenido en el movimiento {i}: {e}")
        if not mbox(f"Robot detenido en el movimiento {i} de {len(movimientos) - 1}.\n"
                    "Rearme el DX100 (servos ON, REMOTE) y presione OK para seguir desde ahí."):
            raise Exception(f"Detenido. Para reanudar ponga inicio = {i}")
        if ROBOT_REAL:
            robot.Connect(IP_ROBOT)
        continue
    i += 1

print(f"¡Astroide y nombres completados en el frame '{frame_name}'!")

robot.MoveJ(T_H)
