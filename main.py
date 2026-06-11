# VideoLab — Sistemas Multimedia, GII, Universidad de Jaén (2025-2026)
# Autor: Manuel Rafael Liebana Cruz

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VideoLab")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
