# VideoLab

Aplicación de captura y edición de vídeo en tiempo real desarrollada en Python.  
Permite aplicar filtros visuales sobre la webcam y detectar caras y manos mediante inteligencia artificial.

Desarrollado para la asignatura **Sistemas Multimedia** — Grado en Ingeniería Informática, Universidad de Jaén (curso 2025-2026).

**Autor:** Manuel Rafael Liebana Cruz

---

## Funcionalidades

- Captura de vídeo en tiempo real desde la webcam (1280×720)
- 10 filtros de vídeo aplicables en tiempo real:
  - Original, Escala de grises, Desenfoque, Bordes (Canny), Sepia, Negativo, Caricatura, Pixelado, Relieve, Nitidez
- Detección por inteligencia artificial (activable/desactivable):
  - **Detección de caras** — localiza y enmarca rostros (MediaPipe FaceDetection)
  - **Detección de manos** — traza los 21 landmarks de cada mano (MediaPipe Hands)
- Contador de elementos detectados en tiempo real
- Grabación de vídeo en formato MP4
- Captura de pantalla en formato PNG
- Modo espejo (volteo horizontal)
- Indicador de FPS y resolución en la barra de estado

---

## Requisitos

- Python 3.12
- Dependencias (ver `requirements.txt`):
  - opencv-python
  - PyQt6
  - numpy
  - mediapipe

---

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/ManuelR-23/VideoLab.git
cd VideoLab

# Crear y activar el entorno virtual (requiere Python 3.12)
python3.12 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt
```

> **macOS:** la primera vez que se ejecute la app, el sistema pedirá permiso de acceso a la cámara. Aceptar en el diálogo que aparece.

---

## Uso

```bash
source venv/bin/activate
python3 main.py
```

### Interfaz

```
┌─────────────────┬──────────────────────────┬─────────────────┐
│   FILTROS       │                          │  DETECCIÓN IA   │
│                 │     Vídeo en tiempo      │                 │
│  [Original    ] │         real             │  [Caras       ] │
│  [Escala gris ] │                          │  [Manos       ] │
│  [Desenfoque  ] │                          │                 │
│  [Bordes      ] │                          │  ESTADÍSTICAS   │
│  [Sepia       ] │                          │  Caras: 0       │
│  [Negativo    ] │                          │  Manos: 0       │
│  [Caricatura  ] │                          │                 │
│  [Pixelado    ] │                          │                 │
│  [Relieve     ] │                          │                 │
│  [Nitidez     ] │                          │                 │
├─────────────────┴──────────────────────────┴─────────────────┤
│  [⏺ Grabar]        [📷 Captura]   [⏹ Detener]  [⇄ Espejo]  │
└──────────────────────────────────────────────────────────────┘
  FPS: 29  |  1280×720
```

| Control | Acción |
|---|---|
| Panel izquierdo | Seleccionar filtro activo (uno a la vez) |
| Panel derecho — Caras / Manos | Activar/desactivar detección IA |
| ⏺ Grabar | Inicia la grabación de vídeo (MP4) |
| ⏹ Detener | Finaliza la grabación y guarda el archivo |
| 📷 Captura | Guarda el fotograma actual como PNG |
| ⇄ Espejo | Activa/desactiva el volteo horizontal |

Los vídeos grabados se guardan en `grabaciones/` y las capturas en `capturas/`.

---

## Estructura del proyecto

```
VideoLab/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── core/
│   ├── capture.py          # Hilo de captura de webcam (QThread)
│   ├── filters.py          # Implementación de los 10 filtros
│   └── ai_detector.py      # Detección IA con MediaPipe
├── ui/
│   ├── main_window.py      # Ventana principal (PyQt6)
│   └── styles.qss          # Tema visual oscuro
├── capturas/               # Capturas de pantalla guardadas
└── grabaciones/            # Vídeos grabados
```

---

## Notas de implementación

### Pipeline de procesamiento

Cada fotograma sigue este flujo:

```
Webcam → CaptureThread → apply_filter() → AIDetector.process() → VideoDisplay
                                                               └→ VideoWriter (si grabando)
```

`CaptureThread` corre en un hilo separado (`QThread`) para no bloquear la interfaz gráfica. Los fotogramas se emiten como señales Qt y se procesan en el hilo principal.

### Filtros de vídeo

Los filtros se implementan como funciones puras sobre arrays NumPy/OpenCV y se registran en un diccionario `_MAP` indexado por el enum `Filter`. Esto permite añadir nuevos filtros sin modificar la lógica de selección.

Los más técnicamente interesantes:
- **Canny**: aplica gradiente de Sobel + supresión de no máximos + histéresis (umbrales 50/150).
- **Caricatura**: combina `bilateralFilter` (suavizado preservando bordes) con `adaptiveThreshold` para obtener contornos gruesos.
- **Sepia**: transformación lineal de color mediante multiplicación matricial con la matriz de sepia estándar.
- **Relieve** y **Nitidez**: convolución con kernels 3×3 personalizados.

### Detección por IA

Se utilizan dos modelos de MediaPipe:
- `FaceDetection` (model_selection=0): optimizado para corto alcance (< 2 m), ideal para webcam de escritorio.
- `Hands`: detecta hasta 2 manos simultáneamente con 21 landmarks por mano.

MediaPipe requiere entrada en RGB; la conversión desde BGR (formato de OpenCV) se hace solo cuando alguna detección está activa, para no penalizar el rendimiento cuando está desactivada.

### Grabación

Se usa `cv2.VideoWriter` con el codec `mp4v`. La grabación corre en el hilo principal: cada fotograma procesado (con filtro y detecciones) se escribe directamente, por lo que el vídeo guardado refleja exactamente lo que se ve en pantalla.

### Problema con MediaPipe y Python 3.13

MediaPipe (versión 0.10.x) no es compatible con Python 3.13. El proyecto requiere **Python 3.12**. Se recomienda usar un entorno virtual para aislar las dependencias del entorno global del sistema.
