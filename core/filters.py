import cv2
import numpy as np
from enum import Enum


class Filter(Enum):
    """Identificadores de los filtros de vídeo disponibles."""
    NONE      = "Original"
    GRAYSCALE = "Escala de grises"
    BLUR      = "Desenfoque"
    CANNY     = "Bordes (Canny)"
    SEPIA     = "Sepia"
    NEGATIVE  = "Negativo"
    CARTOON   = "Caricatura"
    PIXELATE  = "Pixelado"
    EMBOSS    = "Relieve"
    SHARPEN   = "Nitidez"


def _grayscale(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def _blur(frame: np.ndarray) -> np.ndarray:
    # Desenfoque gaussiano con kernel 21x21
    return cv2.GaussianBlur(frame, (21, 21), 0)


def _canny(frame: np.ndarray) -> np.ndarray:
    # Detector de bordes de Canny: convierte a gris, detecta gradientes
    # y aplica supresión de no máximos con umbrales 50 y 150
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def _sepia(frame: np.ndarray) -> np.ndarray:
    # Matriz de transformación de color al tono sepia estándar (entrada BGR)
    kernel = np.array([
        [0.131, 0.534, 0.272],
        [0.168, 0.686, 0.349],
        [0.189, 0.769, 0.393],
    ], dtype=np.float32)
    sepia = cv2.transform(frame.astype(np.float32), kernel)
    return np.clip(sepia, 0, 255).astype(np.uint8)


def _negative(frame: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(frame)


def _cartoon(frame: np.ndarray) -> np.ndarray:
    # Efecto caricatura: combina contornos gruesos con color suavizado.
    # El filtro bilateral preserva los bordes al suavizar, imitando pintura plana.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(
        cv2.medianBlur(gray, 5), 255,
        cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9,
    )
    color = cv2.bilateralFilter(frame, 9, 300, 300)
    return cv2.bitwise_and(color, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))


def _pixelate(frame: np.ndarray, block: int = 12) -> np.ndarray:
    # Reduce la resolución y la amplía con interpolación vecino más cercano
    # para producir el efecto de bloques pixelados
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (w // block, h // block), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def _emboss(frame: np.ndarray) -> np.ndarray:
    # Kernel de relieve: resalta diferencias de intensidad en diagonal
    kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]], dtype=np.float32)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
    result = np.clip(cv2.filter2D(gray, -1, kernel) + 128, 0, 255).astype(np.uint8)
    return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)


def _sharpen(frame: np.ndarray) -> np.ndarray:
    # Kernel de nitidez: resta el laplaciano a la imagen original
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    return cv2.filter2D(frame, -1, kernel)


_MAP = {
    Filter.NONE:      lambda f: f,
    Filter.GRAYSCALE: _grayscale,
    Filter.BLUR:      _blur,
    Filter.CANNY:     _canny,
    Filter.SEPIA:     _sepia,
    Filter.NEGATIVE:  _negative,
    Filter.CARTOON:   _cartoon,
    Filter.PIXELATE:  _pixelate,
    Filter.EMBOSS:    _emboss,
    Filter.SHARPEN:   _sharpen,
}


def apply_filter(frame: np.ndarray, f: Filter) -> np.ndarray:
    """Aplica el filtro indicado al fotograma y devuelve el resultado."""
    return _MAP[f](frame)
