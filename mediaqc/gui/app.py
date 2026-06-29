"""GUI application entry point."""

from __future__ import annotations

import sys

from mediaqc import __version__
from mediaqc.branding import PRODUCT_NAME, icon_path


def launch_gui() -> int:
    if sys.platform == "darwin":
        sys.argv[0] = PRODUCT_NAME
    try:
        from PySide6.QtCore import QCoreApplication, Qt
        from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:  # pragma: no cover - depends on optional GUI dependency.
        raise RuntimeError("PySide6 is not installed. Install GUI dependencies with: python -m pip install 'mediaqc[gui]'") from exc

    from .main_window import MainWindow
    from .theme import LIGHT_STYLESHEET

    QCoreApplication.setApplicationName(PRODUCT_NAME)
    QCoreApplication.setApplicationVersion(__version__)
    QCoreApplication.setOrganizationName(PRODUCT_NAME)
    app = QApplication(sys.argv)
    app.setApplicationName(PRODUCT_NAME)
    app.setApplicationDisplayName(PRODUCT_NAME)
    app.setWindowIcon(QIcon(str(icon_path())))
    app.setStyleSheet(LIGHT_STYLESHEET)

    splash = QPixmap(520, 300)
    splash.fill(QColor("#f2f4f7"))
    painter = QPainter(splash)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(255, 255, 255, 224))
    painter.setPen(QColor("#d7dee7"))
    painter.drawRoundedRect(26, 24, 468, 252, 16, 16)
    painter.drawPixmap(58, 54, 72, 72, QIcon(str(icon_path())).pixmap(96, 96))
    painter.setPen(QColor("#26323f"))
    title_font = QFont("SF Pro Display", 30, QFont.Weight.Bold)
    painter.setFont(title_font)
    painter.drawText(148, 86, PRODUCT_NAME)
    painter.setFont(QFont("SF Pro Text", 11))
    painter.setPen(QColor("#667789"))
    painter.drawText(150, 116, f"Version {__version__}")
    painter.drawText(58, 178, "Preparing media QC workspace...")
    painter.drawText(58, 204, "FFmpeg, FFprobe, validation, batch transcode")
    painter.end()

    from PySide6.QtWidgets import QSplashScreen

    splash_screen = QSplashScreen(splash, Qt.WindowType.WindowStaysOnTopHint)
    splash_screen.show()
    app.processEvents()

    window = MainWindow()
    window.resize(1320, 820)
    window.show()
    splash_screen.finish(window)
    return app.exec()


def main() -> None:
    raise SystemExit(launch_gui())


if __name__ == "__main__":
    main()
