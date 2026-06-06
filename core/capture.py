import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal


class CaptureThread(QThread):
    """
    Hilo de captura de vídeo de la webcam.

    Corre en segundo plano para no bloquear la interfaz gráfica.
    Emite cada fotograma capturado como señal frame_ready.
    """

    frame_ready = pyqtSignal(np.ndarray)  # Emitida con cada fotograma BGR
    error = pyqtSignal(str)               # Emitida si la cámara no está disponible

    def __init__(self, camera_index: int = 0):
        super().__init__()
        self._camera_index = camera_index
        self._running = False
        self.mirror = True  # Volteo horizontal (modo espejo, como FaceTime)

    def run(self):
        cap = cv2.VideoCapture(self._camera_index)
        if not cap.isOpened():
            self.error.emit("No se puede acceder a la cámara. Comprueba los permisos.")
            return

        # Solicitar resolución 1280x720; la cámara usará la más cercana disponible
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self._running = True
        while self._running:
            ret, frame = cap.read()
            if ret:
                if self.mirror:
                    frame = cv2.flip(frame, 1)  # Volteo horizontal (eje Y)
                self.frame_ready.emit(frame)
            else:
                self.msleep(10)  # Pequeña pausa si el fotograma falla
        cap.release()

    def stop(self):
        """Detiene el bucle de captura y espera a que el hilo termine."""
        self._running = False
        self.wait()
