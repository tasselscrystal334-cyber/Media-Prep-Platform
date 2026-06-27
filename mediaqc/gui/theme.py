"""Light engineering stylesheet for the Loom PySide6 GUI."""

from __future__ import annotations

LIGHT_STYLESHEET = """
QWidget {
    background: #f3f4f6;
    color: #1f2933;
    font-family: "SF Pro Text", "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}
QMainWindow {
    background: #eef1f5;
}
QMenuBar {
    background: #f8f9fb;
    border-bottom: 1px solid #d6dbe3;
    padding: 2px 6px;
}
QMenuBar::item {
    background: transparent;
    padding: 5px 10px;
}
QMenuBar::item:selected {
    background: #e7ecf3;
    border-radius: 4px;
}
QMenu {
    background: #ffffff;
    border: 1px solid #cfd6df;
    padding: 6px;
}
QMenu::item {
    padding: 6px 26px 6px 18px;
}
QMenu::item:selected {
    background: #e8f0fe;
    color: #1f4fb2;
}
QFrame#WelcomeBackground {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fbfcfe, stop:1 #dfe5ee);
}
QFrame#GlassPanel {
    background: rgba(255, 255, 255, 210);
    border: 1px solid rgba(180, 190, 205, 150);
    border-radius: 8px;
}
QFrame#Panel, QTabWidget::pane, QTableWidget, QTextEdit, QListWidget {
    background: #ffffff;
    border: 1px solid #d4d9e2;
    border-radius: 6px;
}
QTabBar::tab {
    background: #e9edf3;
    border: 1px solid #d4d9e2;
    padding: 7px 12px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #ffffff;
    border-bottom-color: #ffffff;
}
QHeaderView::section {
    background: #eef1f5;
    color: #344054;
    padding: 7px;
    border: 0;
    border-right: 1px solid #d4d9e2;
    border-bottom: 1px solid #d4d9e2;
}
QPushButton {
    background: #f9fafb;
    border: 1px solid #b9c3d0;
    border-radius: 5px;
    padding: 7px 12px;
    color: #1f2933;
}
QPushButton:hover {
    background: #eef5ff;
    border-color: #8dafdf;
}
QPushButton:pressed {
    background: #dfeeff;
}
QPushButton#PrimaryButton {
    background: #2563eb;
    border-color: #1d4ed8;
    color: white;
    font-weight: 600;
}
QPushButton#PrimaryButton:hover {
    background: #1d4ed8;
}
QPushButton:disabled {
    background: #e5e7eb;
    border-color: #d1d5db;
    color: #8a94a3;
}
QLineEdit, QComboBox {
    background: #ffffff;
    border: 1px solid #c7ced9;
    border-radius: 5px;
    padding: 7px;
    selection-background-color: #bfdbfe;
}
QProgressBar {
    background: #ffffff;
    border: 1px solid #c7ced9;
    border-radius: 5px;
    text-align: center;
}
QProgressBar::chunk {
    background: #22a3a6;
    border-radius: 5px;
}
"""

DARK_STYLESHEET = LIGHT_STYLESHEET
