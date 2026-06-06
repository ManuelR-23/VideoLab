import cv2
import mediapipe as mp
import numpy as np


class AIDetector:
    """Wraps MediaPipe face detection and hand tracking."""

    def __init__(self):
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

        # Stats exposed to UI
        self.face_count = 0
        self.hand_count = 0

    def process(self, frame: np.ndarray) -> np.ndarray:
        if not self.faces_enabled and not self.hands_enabled:
            self.face_count = 0
            self.hand_count = 0
            return frame

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
                self._draw.draw_landmarks(output, lm, self._hand_conn)

        return output

    def close(self):
        self._face.close()
        self._hands.close()
