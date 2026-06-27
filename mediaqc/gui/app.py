"""GUI application entry point."""

from __future__ import annotations

import sys


def launch_gui() -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:  # pragma: no cover - depends on optional GUI dependency.
        raise RuntimeError("PySide6 is not installed. Install GUI dependencies with: python -m pip install 'mediaqc[gui]'") from exc

    from .main_window import MainWindow
    from .theme import DARK_STYLESHEET

    app = QApplication(sys.argv)
    app.setApplicationName("MediaPrep Studio")
    app.setStyleSheet(DARK_STYLESHEET)
    window = MainWindow()
    window.resize(1320, 820)
    window.show()
    return app.exec()


def main() -> None:
    raise SystemExit(launch_gui())


if __name__ == "__main__":
    main()
