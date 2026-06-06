import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal


class CaptureThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    error = pyqtSignal(str)

    def __init__(self, camera_index: int = 0):
        super().__init__()
        self._camera_index = camera_index
        self._running = False
        self.mirror = True

    def run(self):
        cap = cv2.VideoCapture(self._camera_index)
        if not cap.isOpened():
            self.error.emit("No se puede acceder a la cámara. Comprueba los permisos.")
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self._running = True
        while self._running:
            ret, frame = cap.read()
            if ret:
                if self.mirror:
                    frame = cv2.flip(frame, 1)
                self.frame_ready.emit(frame)
            else:
                self.msleep(10)
        cap.release()

    def stop(self):
        self._running = False
        self.wait()
