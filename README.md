# Guía de Optimización de Cámara Industrial y Control de Robot

## Arquitectura del Sistema
Esta aplicación implementa una arquitectura de **Productor-Consumidor** para garantizar un procesamiento de visión de alto rendimiento y un control del robot en tiempo real, sin congelamientos del sistema ni "acumulación de coordenadas" (movimientos de recuperación o *catch-up*).

### Optimizaciones Clave
- **Pre-asignación de Memoria**: Los buffers de la cámara se asignan una sola vez durante la inicialización en `objeto_camara.py` para evitar la fragmentación de la memoria RAM y picos de CPU.
- **Colas No Bloqueantes**: Se utilizan `queue.Queue(maxsize=1)` tanto para el hilo de IA como para el de Modbus. Si el procesamiento es más lento que la cámara, el frame o la coordenada más antigua se descarta, asegurando que el robot siempre reaccione al dato más *reciente*.
- **Reducción de Presión del GC**: Se eliminaron las llamadas manuales a `gc.collect()` para evitar las pausas "stop-the-world" que causaban micro-congelamientos.
- **Manejo Eficiente de Imágenes**: Las imágenes se pasan como arreglos de NumPy y se convierten a `QImage` utilizando buffers de memoria compartida para evitar copias costosas.

## Parámetros de Configuración

Puede ajustar las siguientes variables en `App_vision.py` para adaptar el sistema a las capacidades del hardware:

### Ajuste de Rendimiento
| Variable | Valor Def. | Descripción |
| :--- | :--- | :--- |
| `FRAME_SKIP` | `2` | Número de frames a saltar. `2` significa procesar cada 2do frame (50% de carga). Aumente este valor si la PC se congela o el uso de CPU es muy alto. |
| `PROMEDIO_MEDIDAS` | `15` | Número de frames a promediar para obtener coordenadas de visión estables. Mayor = más suave pero respuesta más lenta. |
| `PROMEDIO_MEDIDAS_MODBUS` | `30` | Ventana de promedio para las escrituras Modbus. |

### Ajuste de Visión
| Variable | Valor Def. | Descripción |
| :--- | :--- | :--- |
| `R_GAIN`, `G_GAIN`, `B_GAIN` | `0.85`, `0.88`, `1.3` | Ganancias de color para compensar la iluminación industrial. Ajuste estos valores para eliminar dominantes de color. |
| `DISTANCIA_CENTROS` | `60` | Distancia máxima (px) para emparejar una detección de IA con un centroide basado en contornos. |
| `ROI_ANCHO_INICIAL` | `300` | Ancho inicial de la zona de análisis (ROI). |
| `ROI_ALTO_INICIAL` | `300` | Alto inicial de la zona de análisis (ROI). |

### Conectividad Modbus y Robot
- **Dirección IP**: Por defecto `192.168.2.17`
- **Puerto**: Por defecto `502`
- **Mapeo de Memoria**: Utiliza la fórmula `Registro = 2 * GV`.
    - Telemetría (Lectura): Inicia en el Registro `412` (GV206).
    - Control (Escritura): GV1 (Reg 2), GV2 y GV3 (Reg 4, 6).

## Solución de Problemas
- **El robot "recupera" movimientos**: Esto ahora está prevenido por la cola `maxsize=1`. Si persiste, verifique si el PLC del robot está encolando comandos internamente.
- **Congelamientos/Lags**: Aumente el valor de `FRAME_SKIP` en `App_vision.py`.
- **Cámara no encontrada**: Asegúrese de que los runtimes de `iCentral` estén instalados en `C:\Program Files\iCentral\iCentral\Runtime\x64`.
