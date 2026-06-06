# Storyboard — VideoLab

**Autor:** Manuel Rafael Liebana Cruz  
Sistemas Multimedia — GII, Universidad de Jaén (2025-2026)

## Pantalla principal

```
┌─────────────────────────────────────────────────────────────────────┐
│  VideoLab                                               [−] [□] [×] │
├──────────────────┬──────────────────────────────┬───────────────────┤
│  FILTROS         │                              │  DETECCIÓN IA     │
│                  │                              │                   │
│  ┌────────────┐  │                              │  ┌─────────────┐  │
│  │ Original ◀ │  │                              │  │   Caras     │  │
│  └────────────┘  │                              │  └─────────────┘  │
│  ┌────────────┐  │     ┌──────────────────┐     │  ┌─────────────┐  │
│  │Escala gris │  │     │                  │     │  │   Manos     │  │
│  └────────────┘  │     │   FEED WEBCAM    │     │  └─────────────┘  │
│  ┌────────────┐  │     │   1280 × 720     │     │                   │
│  │Desenfoque  │  │     │                  │     │  ESTADÍSTICAS     │
│  └────────────┘  │     └──────────────────┘     │                   │
│  ┌────────────┐  │                              │  Caras det.: 0    │
│  │Bordes Canny│  │                              │  Manos det.: 0    │
│  └────────────┘  │                              │                   │
│  ┌────────────┐  │                              │                   │
│  │   Sepia    │  │                              │                   │
│  └────────────┘  │                              │                   │
│       ...        │                              │                   │
├──────────────────┴──────────────────────────────┴───────────────────┤
│  ┌──────────┐     ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │⏺ Grabar  │     │📷 Captura│   │⏹ Detener │   │⇄ Espejo  │        │
│  └──────────┘     └──────────┘   └──────────┘   └──────────┘        │
├─────────────────────────────────────────────────────────────────────┤
│  FPS: 29  |  1280×720                                               │
└─────────────────────────────────────────────────────────────────────┘
```

**Descripción:** Estado inicial al abrir la aplicación. El filtro "Original" está seleccionado (resaltado). La detección IA está desactivada. El botón "Detener" aparece deshabilitado hasta que se inicie una grabación.

---

## Escenario 1 — Aplicar filtro

```
┌──────────────────┬──────────────────────────────┬───────────────────┐
│  FILTROS         │                              │  DETECCIÓN IA     │
│                  │                              │                   │
│  ┌────────────┐  │                              │                   │
│  │ Original   │  │                              │                   │
│  └────────────┘  │     ┌──────────────────┐     │                   │
│  ┌────────────┐  │     │                  │     │                   │
│  │Escala gris │  │     │  IMAGEN EN       │     │                   │
│  └────────────┘  │     │  ESCALA DE       │     │                   │
│  ┌────────────┐  │     │  GRISES          │     │                   │
│  │Desenfoque  │  │     │                  │     │                   │
│  └────────────┘  │     └──────────────────┘     │                   │
│  ┌────────────┐  │                              │                   │
│  │Bordes Canny│  │                              │                   │
│  └────────────┘  │                              │                   │
│  ...             │                              │                   │
```

**Interacción:** El usuario hace clic en "Escala de grises". El botón queda resaltado, el resto vuelve al estado normal. El vídeo cambia instantáneamente al filtro seleccionado.

---

## Escenario 2 — Detección IA activa

```
┌──────────────────┬──────────────────────────────┬───────────────────┐
│  FILTROS         │                              │  DETECCIÓN IA     │
│                  │                              │                   │
│  ┌────────────┐  │   ┌──────────────────────┐   │  ┌─────────────┐  │
│  │ Original ◀ │  │   │   ┌──────────┐       │   │  │  Caras  ◀   │  │
│  └────────────┘  │   │   │          │       │   │  └─────────────┘  │
│                  │   │   │  [CARA]  │  ✋   │   │  ┌─────────────┐  │
│                  │   │   │          │       │   │  │  Manos  ◀   │  │
│                  │   │   └──────────┘       │   │  └─────────────┘  │
│                  │   └──────────────────────┘   │                   │
│                  │                              │  ESTADÍSTICAS     │
│                  │                              │  Caras det.: 1    │
│                  │                              │  Manos det.: 1    │
```

**Interacción:** El usuario activa "Caras" y "Manos" en el panel derecho. Ambos botones quedan resaltados. El sistema superpone los landmarks de la mano y el recuadro de la cara sobre el vídeo. Los contadores se actualizan en tiempo real.

---

## Escenario 3 — Grabación en curso

```
├──────────────────────────────────────────────────────────────────────┤
│  ┌────────────┐     ┌──────────┐   ┌──────────┐   ┌──────────┐       │
│  │⏺ Grabar 🚫 │     │📷 Captura │  │⏹ Detener  │   │⇄ Espejo  │      │
│  └────────────┘     └──────────┘   └──────────┘   └──────────┘       │
├──────────────────────────────────────────────────────────────────────┤
│  FPS: 29  |  1280×720                             ● REC              │
└──────────────────────────────────────────────────────────────────────┘
```

**Interacción:** Al pulsar "Grabar", el botón se deshabilita y aparece el indicador "● REC" en rojo en la esquina derecha de la barra de estado. El botón "Detener" se habilita. Al pulsar "Detener", el archivo MP4 se guarda en `grabaciones/` y el indicador desaparece.

---

## Paleta de colores y tipografía

| Elemento | Color |
|---|---|
| Fondo principal | `#1a1a2e` |
| Paneles laterales | `#16213e` |
| Botón activo / seleccionado | `#7c8cf8` |
| Botón normal | `#0f3460` |
| Botón grabar | `#1a3a1a` / texto `#80e080` |
| Botón detener | `#3a1a1a` / texto `#e08080` |
| Indicador REC | `#e94560` |
| Texto principal | `#e0e0f0` |
| Fuente | Helvetica Neue / Segoe UI / Arial |
