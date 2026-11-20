# Laboratorio No. 02 — Robótica Industrial 2026-II

**Análisis y operación del manipulador Motoman MH6 con RoboDK y trayectoria polar**

Universidad Nacional de Colombia · Robótica 2026-II · LabSIR 408-102
Profesor de laboratorio: Manuel Felipe Carranza Montenegro

| | |
|---|---|
| **Integrantes** | Daniel Torres · Sebastián Zúñiga |
| **Robot** | Yaskawa Motoman MH6 (6 GDL, alcance 1422 mm, carga 6 kg) |
| **Controlador** | Yaskawa DX100 |
| **Software** | RoboDK + API de Python |
| **Entrega** | Según la actividad en Moodle |
| **Vídeo** | *(pendiente: enlace del canal oficial LabSIR)* |

---

## Qué hace el sistema

El Motoman MH6 traza sobre un tablero inclinado un **astroide**, una curva polar
r = f(θ) de cuatro picos, y debajo escribe los nombres de los integrantes. La
trayectoria se programa en Python con la API de RoboDK, se verifica en
simulación sobre la estación del laboratorio y se envía al DX100 desde el PC,
punto a punto.

| Parte | Qué hace |
|---|---|
| Astroide | r = a / (\|cos θ\|^(2/3) + \|sin θ\|^(2/3))^(3/2), a = 70 mm, 81 puntos concentrados en los picos |
| Nombres | «SEBASTIÁN ZÚÑIGA» y «DANIEL TORRES» con una fuente de trazo propia, letras de 9 mm |
| Envío al robot | `MoveL` bloqueante: el siguiente punto sale solo cuando el robot terminó el anterior; si el DX100 se detiene, el script se puede reanudar desde el punto donde quedó |
| Inicio y fin | El robot va a `Target Home` antes y después del trazo |

![Trazo en la simulación de RoboDK](media/img/sim_trazo.png)

---

## Estructura del repositorio

```
├── codigo_robodk/
│   └── AstroidePolar.py           astroide y nombres en RoboDK (anexo de la guía)
├── scripts/
│   ├── gen_preview_polar.py       genera la figura de la trayectoria
│   └── gen_plano.py               genera el plano de planta de la celda
├── docs/
│   ├── 01_comparacion_mh6_irb140.md
│   ├── 02_home1_home2.md
│   ├── 03_movimiento_manual.md
│   ├── 04_velocidades.md
│   ├── 05_robodk.md
│   ├── 06_robodk_vs_robotstudio.md
│   ├── 07_diagrama_flujo.md
│   ├── 08_plano_planta.md
│   ├── 09_trayectoria_polar.md
│   ├── 10_evidencias_y_video.md
│   └── Guia_Laboratorio_02.pdf
├── media/img/                     figuras, fotos del pendant y capturas de la simulación
└── media/video/                   home1 a home2 y trazado en el robot real
```

---

## Cómo trabajar con esto

### 1. Regenerar las figuras

La figura y los nombres están parametrizados en la sección 3 de
`codigo_robodk/AstroidePolar.py` (`a`, `num_points`, `nombres`, `alto_letra`).
Los scripts de figuras leen esa misma sección, así que no hay que duplicar
parámetros:

```bash
python3 scripts/gen_preview_polar.py   # reescribe media/img/trayectoria_polar.png
python3 scripts/gen_plano.py           # reescribe media/img/plano_planta.png
```

### 2. Simular en RoboDK

1. Instalar la API: `pip install robodk`.
2. Abrir RoboDK con la estación del laboratorio (`RobodkBasico-2.rdk`), que ya
   trae el MH6, la herramienta, `Frame_from_Target1` y `Target Home`. El script
   no redefine ninguno de esos datos: los lee de la estación.
3. Dejar `ROBOT_REAL = False` y ejecutar:

   ```bash
   python3 codigo_robodk/AstroidePolar.py
   ```

4. Revisar que el marcador no atraviese el tablero y que no haya avisos de
   alcanzabilidad.

### 3. Antes de pasar al robot real

- [ ] Trayectoria completa verificada en simulación, sin colisiones.
- [ ] PC en la red del DX100 (IP `192.168.1.20`) y llave del pendant en **REMOTE**.
- [ ] Servos encendidos y parada de emergencia al alcance de la mano.
- [ ] `ROBOT_REAL = True` en el script.
- [ ] Velocidad reducida en las primeras pruebas (`robot.setSpeed`).
- [ ] Si el robot se detiene, anotar el movimiento que reporta el script y
      reanudar con `inicio = <n>`.

---

## Cumplimiento de los requisitos de la guía

| Requisito de la guía | Dónde se resuelve |
|---|---|
| Cuadro comparativo MH6 vs. IRB 140 | `docs/01_comparacion_mh6_irb140.md` |
| Home1 y home2, posición de cada articulación y cuál es mejor | `docs/02_home1_home2.md` + fotos del pendant en `media/img/` |
| Movimiento manual por articulaciones y cartesiano, traslaciones y rotaciones | `docs/03_movimiento_manual.md` |
| Niveles de velocidad, cambio entre niveles e indicación en pantalla | `docs/04_velocidades.md` |
| Aplicaciones de RoboDK y comunicación con el Motoman | `docs/05_robodk.md` |
| RoboDK vs. RobotStudio | `docs/06_robodk_vs_robotstudio.md` |
| Diagrama de flujo de acciones del robot | `docs/07_diagrama_flujo.md` |
| Plano de planta | `docs/08_plano_planta.md` + `media/img/plano_planta.png` |
| Trayectoria polar con los nombres de los integrantes | `docs/09_trayectoria_polar.md` |
| Código de RoboDK como anexo | `codigo_robodk/AstroidePolar.py` |
| Vídeo de simulación y del robot real, con intro LabSIR | `docs/10_evidencias_y_video.md` |
