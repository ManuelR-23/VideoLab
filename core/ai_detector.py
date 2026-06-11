# VideoLab — Sistemas Multimedia, GII, Universidad de Jaén (2025-2026)
# Autor: Manuel Rafael Liebana Cruz

import cv2
import mediapipe as mp
import numpy as np


class AIDetector:
    """
    Detector de elementos visuales mediante inteligencia artificial.

    Utiliza los modelos preentrenados de MediaPipe para:
    - Detección de caras (FaceDetection): localiza y enmarca rostros en tiempo real.
    - Seguimiento de manos (Hands): detecta landmarks de los 21 puntos de cada mano.

    Ambas detecciones son opcionales e independientes; se activan desde la UI.
    """

    def __init__(self):
        # model_selection=0: modelo corto alcance (< 2 m), más rápido para webcam
        self._face = mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.6
        )
        self._hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        self._draw = mp.solutions.drawing_utils
        self._hand_conn = mp.solutions.hands.HAND_CONNECTIONS

        self.faces_enabled = False
        self.hands_enabled = False

        # Contadores expuestos a la UI para las estadísticas en tiempo real
        self.face_count = 0
        self.hand_count = 0

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Procesa un fotograma BGR y dibuja las detecciones activas.
        Devuelve el fotograma anotado (copia del original si hay detecciones).
        """
        if not self.faces_enabled and not self.hands_enabled:
            self.face_count = 0
            self.hand_count = 0
            return frame

        # MediaPipe trabaja en RGB; convertimos solo cuando es necesario
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = frame.copy()

        if self.faces_enabled:
            results = self._face.process(rgb)
            detections = results.detections or []
            self.face_count = len(detections)
            for det in detections:
                self._draw.draw_detection(output, det)

        if self.hands_enabled:
            results = self._hands.process(rgb)
            landmarks = results.multi_hand_landmarks or []
            self.hand_count = len(landmarks)
            for lm in landmarks:
                # Dibuja los 21 landmarks y las conexiones entre ellos
                self._draw.draw_landmarks(output, lm, self._hand_conn)

        return output

    def close(self):
        """Libera los recursos de los modelos de MediaPipe."""
        self._face.close()
        self._hands.close()
