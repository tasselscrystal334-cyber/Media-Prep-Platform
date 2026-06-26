"""Dark theme stylesheet for the PySide6 GUI."""

from __future__ import annotations

DARK_STYLESHEET = """
QWidget {
    background: #111318;
    color: #e6e8ee;
    font-family: "Inter", "SF Pro Display", "Segoe UI", sans-serif;
    font-size: 13px;
}
QMainWindow, QTabWidget::pane {
    background: #111318;
}
QFrame, QGroupBox, QTableWidget, QTextEdit, QListWidget, QTreeWidget {
    background: #171a21;
    border: 1px solid #2a2f3a;
    border-radius: 6px;
}
QHeaderView::section {
    background: #202532;
    color: #cfd5e3;
    padding: 6px;
    border: 0;
}
QPushButton {
    background: #2c68d8;
    border: 0;
    border-radius: 5px;
    padding: 7px 11px;
    color: white;
}
QPushButton:hover {
    background: #3777ee;
}
QPushButton:disabled {
    background: #343946;
    color: #858b99;
}
QLineEdit, QComboBox {
    background: #0f1117;
    border: 1px solid #303644;
    border-radius: 5px;
    padding: 6px;
}
QProgressBar {
    background: #0f1117;
    border: 1px solid #303644;
    border-radius: 5px;
    text-align: center;
}
QProgressBar::chunk {
    background: #2c68d8;
    border-radius: 5px;
}
"""
