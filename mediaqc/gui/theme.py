"""Light engineering stylesheet for the Loom PySide6 GUI."""

from __future__ import annotations

LIGHT_STYLESHEET = """
QWidget {
    background: #f7f8fa;
    color: #26323f;
    font-family: "SF Pro Text", "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}
QMainWindow {
    background: #f2f4f7;
}
QMenuBar {
    background: #fbfcfd;
    border-bottom: 1px solid #e1e5eb;
    padding: 2px 6px;
}
QMenuBar::item {
    background: transparent;
    padding: 5px 10px;
}
QMenuBar::item:selected {
    background: #eef2f6;
    border-radius: 4px;
}
QMenu {
    background: #ffffff;
    border: 1px solid #dce2e9;
    padding: 6px;
}
QMenu::item {
    padding: 6px 26px 6px 18px;
}
QMenu::item:selected {
    background: #edf4f8;
    color: #315f78;
}
QFrame#WelcomeBackground {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fcfdfe, stop:1 #edf1f5);
}
QFrame#GlassPanel {
    background: rgba(255, 255, 255, 218);
    border: 1px solid rgba(198, 207, 218, 128);
    border-radius: 8px;
}
QFrame#TopToolbar {
    background: #f6f7f9;
    border-bottom: 1px solid #dfe4eb;
}
QFrame#SourcePanel {
    background: #f3f4f6;
    border-bottom: 1px solid #dfe4eb;
}
QFrame#Panel, QTabWidget::pane, QTableWidget, QTextEdit, QListWidget {
    background: #ffffff;
    border: 1px solid #dfe4eb;
    border-radius: 6px;
}
QTabBar::tab {
    background: #f0f3f6;
    border: 1px solid #dfe4eb;
    padding: 7px 12px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #ffffff;
    border-bottom-color: #ffffff;
}
QHeaderView::section {
    background: #f4f6f8;
    color: #465465;
    padding: 7px;
    border: 0;
    border-right: 1px solid #e1e6ed;
    border-bottom: 1px solid #e1e6ed;
}
QPushButton {
    background: #fbfcfd;
    border: 1px solid #cfd7e1;
    border-radius: 5px;
    padding: 7px 12px;
    color: #2d3846;
}
QPushButton:hover {
    background: #f0f5f8;
    border-color: #aebdcc;
}
QPushButton:pressed {
    background: #e8f0f4;
}
QPushButton#PrimaryButton {
    background: #5f7f95;
    border-color: #557287;
    color: white;
    font-weight: 600;
}
QPushButton#PrimaryButton:hover {
    background: #526f82;
}
QPushButton#ToolbarButton {
    background: transparent;
    border: 0;
    padding: 8px 10px;
    color: #56616f;
    font-size: 14px;
}
QPushButton#ToolbarButton:hover {
    background: #e9eef3;
}
QPushButton#ToolbarPrimaryButton {
    background: transparent;
    border: 0;
    padding: 8px 12px;
    color: #5c9d65;
    font-size: 14px;
    font-weight: 700;
}
QPushButton#ToolbarPrimaryButton:hover {
    background: #e9f3ea;
}
QPushButton:disabled {
    background: #edf0f3;
    border-color: #dfe4eb;
    color: #99a3ae;
}
QLineEdit, QComboBox {
    background: #ffffff;
    border: 1px solid #d4dbe4;
    border-radius: 5px;
    padding: 7px;
    selection-background-color: #d8e8f0;
}
QProgressBar {
    background: #ffffff;
    border: 1px solid #d4dbe4;
    border-radius: 5px;
    text-align: center;
}
QProgressBar::chunk {
    background: #8ab6b8;
    border-radius: 5px;
}
"""

DARK_STYLESHEET = LIGHT_STYLESHEET
