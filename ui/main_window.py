import os
import time
from datetime import datetime

import cv2
import numpy as np
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from core.capture import CaptureThread
from core.filters import Filter, apply_filter
from core.ai_detector import AIDetector

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class VideoDisplay(QLabel):
    """Video frame display that scales while keeping aspect ratio."""

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #000000; border-radius: 8px;")
        self.setText("Iniciando cámara...")

    def update_frame(self, frame: np.ndarray):
        h, w, ch = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image).scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(pixmap)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoLab")
        self.setMinimumSize(1100, 680)

        self._current_filter = Filter.NONE
        self._ai = AIDetector()
        self._last_frame: np.ndarray | None = None
        self._recorder: cv2.VideoWriter | None = None
        self._recording = False
        self._frame_size = (1280, 720)
        self._fps_times: list[float] = []

        self._build_ui()
        self._load_styles()
        self._start_capture()

        # AI stats refresh timer (avoids updating labels every frame)
        self._stats_timer = QTimer(self)
        self._stats_timer.timeout.connect(self._refresh_ai_stats)
        self._stats_timer.start(500)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        root.addWidget(self._make_filter_panel())

        center = QVBoxLayout()
        self._video = VideoDisplay()
        center.addWidget(self._video, 1)
        center.addWidget(self._make_controls_bar())
        root.addLayout(center, 1)

        root.addWidget(self._make_ai_panel())

        self._build_status_bar()

    def _make_filter_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(155)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 10, 8, 10)
        layout.setSpacing(5)

        title = QLabel("FILTROS")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        self._filter_group = QButtonGroup(self)
        self._filter_group.setExclusive(True)
        for f in Filter:
            btn = QPushButton(f.value)
            btn.setCheckable(True)
            btn.setChecked(f == Filter.NONE)
            btn.setProperty("filter", f)
            self._filter_group.addButton(btn)
            layout.addWidget(btn)

        self._filter_group.buttonClicked.connect(
            lambda btn: setattr(self, "_current_filter", btn.property("filter"))
        )
        layout.addStretch()
        return panel

    def _make_ai_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(155)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 10, 8, 10)
        layout.setSpacing(5)

        title = QLabel("DETECCIÓN IA")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        self._btn_faces = QPushButton("Caras")
        self._btn_faces.setCheckable(True)
        self._btn_faces.toggled.connect(lambda on: setattr(self._ai, "faces_enabled", on))
        layout.addWidget(self._btn_faces)

        self._btn_hands = QPushButton("Manos")
        self._btn_hands.setCheckable(True)
        self._btn_hands.toggled.connect(lambda on: setattr(self._ai, "hands_enabled", on))
        layout.addWidget(self._btn_hands)

        layout.addSpacing(12)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #0f3460;")
        layout.addWidget(sep)
        layout.addSpacing(4)

        stats_title = QLabel("ESTADÍSTICAS")
        stats_title.setObjectName("panelTitle")
        layout.addWidget(stats_title)

        self._lbl_ai_faces = QLabel("Caras detectadas: 0")
        self._lbl_ai_faces.setWordWrap(True)
        self._lbl_ai_faces.setStyleSheet("color: #8090b0; font-size: 12px;")
        layout.addWidget(self._lbl_ai_faces)

        self._lbl_ai_hands = QLabel("Manos detectadas: 0")
        self._lbl_ai_hands.setWordWrap(True)
        self._lbl_ai_hands.setStyleSheet("color: #8090b0; font-size: 12px;")
        layout.addWidget(self._lbl_ai_hands)

        layout.addStretch()
        return panel

    def _make_controls_bar(self) -> QWidget:
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(8)

        self._btn_record = QPushButton("⏺  Grabar")
        self._btn_record.setObjectName("btnRecord")
        self._btn_record.setFixedHeight(42)
        self._btn_record.clicked.connect(self._start_recording)

        self._btn_snap = QPushButton("📷  Captura")
        self._btn_snap.setFixedHeight(42)
        self._btn_snap.clicked.connect(self._take_snapshot)

        self._btn_stop = QPushButton("⏹  Detener")
        self._btn_stop.setObjectName("btnStop")
        self._btn_stop.setFixedHeight(42)
        self._btn_stop.setEnabled(False)
        self._btn_stop.clicked.connect(self._stop_recording)

        for btn in (self._btn_record, self._btn_snap, self._btn_stop):
            layout.addWidget(btn)

        return bar

    def _build_status_bar(self):
        bar = QStatusBar()
        self.setStatusBar(bar)
        self._lbl_fps = QLabel("FPS: --")
        self._lbl_res = QLabel("--")
        self._lbl_rec = QLabel("")
        self._lbl_rec.setStyleSheet("color: #e94560; font-weight: bold;")
        bar.addWidget(self._lbl_fps)
        bar.addWidget(QLabel("  |  "))
        bar.addWidget(self._lbl_res)
        bar.addPermanentWidget(self._lbl_rec)

    # ── Styles ────────────────────────────────────────────────────────────────

    def _load_styles(self):
        qss = os.path.join(BASE_DIR, "ui", "styles.qss")
        try:
            with open(qss) as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass

    # ── Capture ───────────────────────────────────────────────────────────────

    def _start_capture(self):
        self._capture = CaptureThread(0)
        self._capture.frame_ready.connect(self._on_frame)
        self._capture.error.connect(
            lambda msg: QMessageBox.critical(self, "Error de cámara", msg)
        )
        self._capture.start()

    # ── Frame pipeline ────────────────────────────────────────────────────────

    @pyqtSlot(np.ndarray)
    def _on_frame(self, frame: np.ndarray):
        self._frame_size = (frame.shape[1], frame.shape[0])
        processed = apply_filter(frame, self._current_filter)
        processed = self._ai.process(processed)
        self._last_frame = processed
        self._video.update_frame(processed)
        if self._recording and self._recorder:
            self._recorder.write(processed)
        self._tick_fps()

    def _tick_fps(self):
        now = time.monotonic()
        self._fps_times.append(now)
        self._fps_times = [t for t in self._fps_times if now - t <= 1.0]
        self._lbl_fps.setText(f"FPS: {len(self._fps_times)}")
        w, h = self._frame_size
        self._lbl_res.setText(f"{w}×{h}")

    def _refresh_ai_stats(self):
        self._lbl_ai_faces.setText(f"Caras detectadas: {self._ai.face_count}")
        self._lbl_ai_hands.setText(f"Manos detectadas: {self._ai.hand_count}")

    # ── Recording ─────────────────────────────────────────────────────────────

    def _start_recording(self):
        out_dir = os.path.join(BASE_DIR, "grabaciones")
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(out_dir, f"grabacion_{ts}.mp4")
        w, h = self._frame_size
        self._recorder = cv2.VideoWriter(
            path, cv2.VideoWriter_fourcc(*"mp4v"), 20, (w, h)
        )
        self._recording = True
        self._btn_record.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._lbl_rec.setText("● REC")
        self.statusBar().showMessage(f"Grabando: {os.path.basename(path)}", 0)

    def _stop_recording(self):
        if self._recorder:
            self._recorder.release()
            self._recorder = None
        self._recording = False
        self._btn_record.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._lbl_rec.setText("")
        self.statusBar().showMessage("Grabación guardada en /grabaciones", 4000)

    # ── Snapshot ──────────────────────────────────────────────────────────────

    def _take_snapshot(self):
        if self._last_frame is None:
            return
        out_dir = os.path.join(BASE_DIR, "capturas")
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(out_dir, f"captura_{ts}.png")
        cv2.imwrite(path, self._last_frame)
        self.statusBar().showMessage(f"Captura guardada: {os.path.basename(path)}", 3000)

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        self._stats_timer.stop()
        self._capture.stop()
        self._stop_recording()
        self._ai.close()
        super().closeEvent(event)
