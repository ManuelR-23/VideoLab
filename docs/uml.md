# Diagrama UML de clases — VideoLab

**Autor:** Manuel Rafael Liebana Cruz  
Sistemas Multimedia — GII, Universidad de Jaén (2025-2026)

```mermaid
classDiagram

    %% ── Capa de captura ──────────────────────────────────────────
    class CaptureThread {
        +mirror : bool
        -_camera_index : int
        -_running : bool
        +run()
        +stop()
        --signals--
        +frame_ready(ndarray)
        +error(str)
    }

    %% ── Capa de procesamiento ────────────────────────────────────
    class Filter {
        <<enumeration>>
        NONE
        GRAYSCALE
        BLUR
        CANNY
        SEPIA
        NEGATIVE
        CARTOON
        PIXELATE
        EMBOSS
        SHARPEN
    }

    class FilterFunctions {
        <<module>>
        +apply_filter(frame, Filter) ndarray
        -_grayscale(frame) ndarray
        -_blur(frame) ndarray
        -_canny(frame) ndarray
        -_sepia(frame) ndarray
        -_negative(frame) ndarray
        -_cartoon(frame) ndarray
        -_pixelate(frame) ndarray
        -_emboss(frame) ndarray
        -_sharpen(frame) ndarray
    }

    class AIDetector {
        +faces_enabled : bool
        +hands_enabled : bool
        +face_count : int
        +hand_count : int
        -_face : FaceDetection
        -_hands : Hands
        +process(frame) ndarray
        +close()
    }

    %% ── Capa de interfaz ─────────────────────────────────────────
    class VideoDisplay {
        +update_frame(frame)
    }

    class MainWindow {
        -_current_filter : Filter
        -_ai : AIDetector
        -_capture : CaptureThread
        -_recorder : VideoWriter
        -_recording : bool
        -_last_frame : ndarray
        -_fps_times : list
        +closeEvent(event)
        -_on_frame(frame)
        -_start_recording()
        -_stop_recording()
        -_take_snapshot()
        -_refresh_ai_stats()
    }

    %% ── Relaciones ───────────────────────────────────────────────
    MainWindow *-- VideoDisplay       : contiene
    MainWindow *-- AIDetector         : contiene
    MainWindow *-- CaptureThread      : contiene
    MainWindow ..> FilterFunctions    : usa
    MainWindow ..> Filter             : usa
    FilterFunctions ..> Filter        : indexado por
    CaptureThread ..> MainWindow      : frame_ready →

    %% ── Herencia Qt ──────────────────────────────────────────────
    class QMainWindow { <<Qt>> }
    class QThread { <<Qt>> }
    class QLabel { <<Qt>> }

    QMainWindow <|-- MainWindow
    QThread <|-- CaptureThread
    QLabel <|-- VideoDisplay
```

## Descripción de las capas

| Capa | Clases | Responsabilidad |
|---|---|---|
| **Captura** | `CaptureThread` | Acceso a la webcam en hilo separado; emite fotogramas vía señal Qt |
| **Procesamiento** | `Filter`, `FilterFunctions`, `AIDetector` | Transformaciones de imagen (filtros + IA); sin dependencias de UI |
| **Interfaz** | `MainWindow`, `VideoDisplay` | Presentación, interacción con el usuario y coordinación del pipeline |

## Flujo de datos

```
Webcam
  └─► CaptureThread.run()
        └─► [señal] frame_ready
              └─► MainWindow._on_frame()
                    ├─► apply_filter(frame, filtro_activo)
                    ├─► AIDetector.process(frame)
                    ├─► VideoDisplay.update_frame(frame)   → pantalla
                    └─► VideoWriter.write(frame)           → archivo MP4 (si graba)
```
