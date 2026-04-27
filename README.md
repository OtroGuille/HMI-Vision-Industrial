# Proyecto Brazo Robótico - Programación

## Descripción General del Proyecto

Este proyecto implementa un **sistema de control de brazo robótico** que integra:
- **Visión por computadora** para detección y localización de objetos
- **Interfaz gráfica (GUI)** para control y monitoreo
- **Comunicación Modbus TCP** para la comunicación con el PLC (Controlador Lógico Programable)

El sistema es capaz de procesar imágenes de video en tiempo real, detectar objetos por color, calcular sus posiciones en coordenadas del robot y comunicarse con el PLC para realizar movimientos.

---

## Estructura del Proyecto

### 1. **App_vision** (Aplicación Principal)
- **Tipo:** Aplicación de escritorio
- **Tecnología:** Python + PyQt6
- **Función:** Interfaz gráfica principal del sistema

**Características:**
- Interfaz visual para visualizar el feed de cámara en tiempo real
- Panel de controles con botones, sliders y campos de entrada
- Parámetros ajustables para el procesamiento de visión
- Visualización de coordenadas detectadas
- Integración con el módulo de visión (`vision`)

**Componentes de la UI:**
- Visualización de video en vivo
- SpinBox y DoubleSpinBox para parámetros numéricos
- Sliders para ajustes en tiempo real
- Botones de control
- Etiquetas (QLabel) para mostrar información

---

### 2. **vision** (Módulo de Procesamiento de Visión)
- **Tipo:** Módulo Python (librería)
- **Tecnología:** OpenCV + NumPy
- **Función:** Procesamiento de imágenes y detección de objetos

**Clase Principal: `VisionRobotLocal`**

**Funcionalidades:**
- **Captura de video:** Obtiene frames de la cámara conectada
- **Conversión de coordenadas:** Factor de conversión pixel-a-milímetros (0.75 px/mm)
- **Región de Interés (ROI):** Define área de análisis
  - Posición inicial: (150, 100)
  - Dimensiones: 300x300 píxeles
- **Detección de colores:** Identifica objetos por rango de color HSV
- **Cálculo de posiciones:** Determina coordenadas (X, Y) de objetos detectados
- **Cálculo de ángulos:** Determina orientación de los objetos

**Parámetros Ajustables:**
- Rango de colores HSV para detección
- Dimensiones de la ROI
- Factor de conversión pixel-a-mm
- Valores de umbral para procesamiento

**Output:**
- Coordenadas X, Y del objeto en milímetros
- Ángulo de orientación del objeto
- Información del color identificado

---

### 3. **simulador_modbus.py** (Simulador de PLC)
- **Tipo:** Servidor Modbus TCP
- **Tecnología:** Python + pymodbus
- **Función:** Simula el comportamiento del PLC para pruebas y desarrollo

**Características:**
- **Servidor TCP:** Escucha conexiones en puerto Modbus estándar (502)
- **Contexto Modbus:** Gestiona registros de entrada/salida
- **Monitoreo en tiempo real:** Imprime valores de registros cada segundo
- **Registros simulados (0-3):**
  - Registro 0: Coordenada X
  - Registro 1: Coordenada Y
  - Registro 2: Ángulo
  - Registro 3: Color detectado

**Funciones:**
- `monitor_plc()`: Hilo que monitorea los registros Modbus
- Actualiza valores basados en comandos del brazo robótico
- Permite pruebas sin hardware real

**Requisitos:**
```
pymodbus >= 2.0
threading (stdlib)
```

---

## Flujo de Trabajo del Sistema

```
Cámara (entrada)
    ↓
[vision] - Procesa frame
    ↓
Detecta objeto (X, Y, Ángulo, Color)
    ↓
[App_vision] - Muestra en GUI
    ↓
Envía coordenadas al PLC
    ↓
[simulador_modbus] - Recibe vía Modbus TCP
    ↓
Brazo robótico se mueve
```

---

## Instalación y Configuración

### Dependencias Requeridas:
```
opencv-python      # Procesamiento de imágenes
PyQt6               # Interfaz gráfica
numpy               # Operaciones numéricas
pymodbus            # Comunicación Modbus TCP
```

### Para instalar:
```bash
pip install opencv-python PyQt6 numpy pymodbus
```

---

## Uso del Sistema

### Iniciar la aplicación principal:
```bash
python App_vision
```

### Iniciar el simulador Modbus (en otra terminal):
```bash
python simulador_modbus.py
```

---

## Parámetros Configurables

Los siguientes parámetros se pueden ajustar en la interfaz o en el código:

| Parámetro | Predeterminado | Descripción |
|-----------|----------------|-------------|
| `px_to_mm` | 0.75 | Factor de conversión pixel a milímetro |
| `roi_x` | 150 | Posición X de la región de interés |
| `roi_y` | 100 | Posición Y de la región de interés |
| `roi_w` | 300 | Ancho de la región de interés |
| `roi_h` | 300 | Alto de la región de interés |

---

## Comunicación Modbus

El sistema utiliza **Modbus TCP** para comunicarse con el PLC:

**Configuración:**
- **Protocolo:** TCP/IP
- **Puerto:** 502 (estándar Modbus)
- **Dirección:** Localhost (127.0.0.1) para pruebas locales
- **Función:** Lectura/escritura de registros

**Registros Disponibles:**
- Registro 0-3: Valores de X, Y, Ángulo, Color del brazo
- Registro 4-9: Reservados para expansión futura

---

## Archivos del Proyecto

| Archivo | Descripción |
|---------|------------|
| `App_vision` | Aplicación PyQt6 con interfaz gráfica |
| `vision` | Módulo de procesamiento de imágenes con OpenCV |
| `simulador_modbus.py` | Servidor Modbus TCP para simular el PLC |

---

## Notas de Desarrollo

- La conversión de coordenadas es crítica para la precisión del brazo
- El factor `px_to_mm` debe calibrarse según la cámara y distancia de captura
- La ROI define el espacio de trabajo útil para el sistema
- El simulador Modbus es útil para desarrollo sin hardware real

---

## Futuros Mejoras

- [ ] Agregar soporte para múltiples cámaras
- [ ] Implementar filtrado de Kalman para movimiento suave
- [ ] Agregar detección de múltiples objetos simultáneamente
- [ ] Interfaz de calibración automática
- [ ] Grabación de movimientos para reproducción

---

**Última actualización:** Abril 2026  
**Versión:** 1.0
**Proyecto:** Brazo Robótico - Sistema de Control Integrado
