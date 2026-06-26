"""Main PySide6 window for MediaPrep Studio."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal, Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QProgressBar,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .queue import GuiTask, GuiTaskQueue
from .workers import ScanWorker


class QtScanThread(QThread):
    progress = Signal(int, str)
    completed = Signal(dict)
    failed = Signal(str)

    def __init__(self, worker: ScanWorker) -> None:
        super().__init__()
        self.worker = worker

    def run(self) -> None:
        try:
            self.progress.emit(10, "Starting scan")
            result = self.worker.run()
            self.progress.emit(100, "Scan finished")
            self.completed.emit(result)
        except Exception as exc:  # noqa: BLE001 - GUI must surface errors.
            self.failed.emit(str(exc))

    def cancel(self) -> None:
        self.worker.cancel()


class DropLineEdit(QLineEdit):
    dropped = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setPlaceholderText("Drop a media folder here")

    def dragEnterEvent(self, event) -> None:  # noqa: ANN001
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # noqa: ANN001
        urls = event.mimeData().urls()
        for index, url in enumerate(urls):
            path = Path(url.toLocalFile())
            if path.is_file():
                path = path.parent
            if index == 0:
                self.setText(str(path))
            self.dropped.emit(str(path))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MediaPrep Studio")
        self.queue = GuiTaskQueue()
        self.current_thread: QtScanThread | None = None
        self.pending_tasks: list[GuiTask] = []
        self.last_outputs: dict[str, Path | None] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        self._build_actions()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._left_panel())
        splitter.addWidget(self._center_panel())
        splitter.addWidget(self._right_panel())
        splitter.setSizes([240, 720, 360])
        self.setCentralWidget(splitter)

    def _build_actions(self) -> None:
        export_pdf = QAction("Export PDF", self)
        export_pdf.triggered.connect(self._open_pdf)
        self.menuBar().addMenu("File").addAction(export_pdf)

    def _left_panel(self) -> QWidget:
        tabs = QTabWidget()
        self.projects = QListWidget()
        self.rules = QListWidget()
        self.history = QListWidget()
        self.rules.addItems(["project_rules.yaml", "LED_4K", "Disguise", "TouchDesigner"])
        tabs.addTab(self.projects, "Projects")
        tabs.addTab(self.rules, "Rules")
        tabs.addTab(self.history, "History")
        return tabs

    def _center_panel(self) -> QWidget:
        panel = QFrame()
        layout = QVBoxLayout(panel)
        title = QLabel("Scan")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        self.project_input = DropLineEdit()
        self.project_input.dropped.connect(self._add_project)
        self.output_input = QLineEdit(str(Path("./reports").resolve()))
        browse_project = QPushButton("Browse Project")
        browse_output = QPushButton("Browse Output")
        browse_project.clicked.connect(self._browse_project)
        browse_output.clicked.connect(self._browse_output)
        button_row = QHBoxLayout()
        self.scan_button = QPushButton("Start Scan")
        self.cancel_button = QPushButton("Cancel")
        self.open_html_button = QPushButton("Open HTML")
        self.open_html_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.scan_button.clicked.connect(self._start_scan)
        self.cancel_button.clicked.connect(self._cancel_scan)
        self.open_html_button.clicked.connect(self._open_html)
        button_row.addWidget(self.scan_button)
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.open_html_button)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.tasks = QTableWidget(0, 4)
        self.tasks.setHorizontalHeaderLabels(["Project", "Status", "Progress", "Message"])
        layout.addWidget(title)
        layout.addWidget(QLabel("Project Folder"))
        layout.addWidget(self.project_input)
        layout.addWidget(browse_project)
        layout.addWidget(QLabel("Output Folder"))
        layout.addWidget(self.output_input)
        layout.addWidget(browse_output)
        layout.addLayout(button_row)
        layout.addWidget(self.progress)
        layout.addWidget(QLabel("Task Queue"))
        layout.addWidget(self.tasks)
        return panel

    def _right_panel(self) -> QWidget:
        tabs = QTabWidget()
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setText("Preview\n\nDrop a folder or run a scan to inspect report outputs.")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        tabs.addTab(self.preview, "Preview")
        tabs.addTab(self.log, "Logs")
        return tabs

    def _browse_project(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.project_input.setText(folder)
            self._add_project(folder)

    def _browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_input.setText(folder)

    def _add_project(self, path: str) -> None:
        if path and not self._list_contains(self.projects, path):
            self.projects.addItem(path)

    def _start_scan(self) -> None:
        output = Path(self.output_input.text()).expanduser()
        projects = self._project_paths()
        if not projects:
            project = Path(self.project_input.text()).expanduser()
            if project.is_file():
                project = project.parent
            if project.exists() and project.is_dir():
                projects = [project]
        if not projects:
            self._log("No valid project folders selected.")
            return
        self.pending_tasks = [
            GuiTask(project_path=project, output_path=output / project.name, status="PENDING", progress=0, message="Queued")
            for project in projects
        ]
        for task in self.pending_tasks:
            self.queue.add(task)
        self._refresh_tasks()
        self.scan_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self._start_next_task()

    def _start_next_task(self) -> None:
        if not self.pending_tasks:
            self.scan_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            return
        task = self.pending_tasks.pop(0)
        task.status = "RUNNING"
        task.message = "Starting"
        worker = ScanWorker(task.project_path, task.output_path, html=True, pdf=True)
        self.current_thread = QtScanThread(worker)
        self.current_thread.progress.connect(self._on_progress)
        self.current_thread.completed.connect(self._on_completed)
        self.current_thread.failed.connect(self._on_failed)
        self.current_thread.start()

    def _cancel_scan(self) -> None:
        if self.current_thread:
            self.current_thread.cancel()
            self._log("Cancel requested. Current file operation may finish before the scan stops.")
            self.cancel_button.setEnabled(False)

    def _on_progress(self, value: int, message: str) -> None:
        self.progress.setValue(value)
        running = self._running_task()
        if running:
            task = running
            task.progress = value
            task.message = message
            self._refresh_tasks()
        self._log(message)

    def _on_completed(self, result: dict) -> None:
        running = self._running_task()
        if running:
            task = running
            task.status = str(result.get("status", "SUCCESS"))
            task.progress = 100
            task.message = f"{result.get('files', 0)} files"
            task.json_path = result.get("json_path")
            task.csv_path = result.get("csv_path")
            task.html_path = result.get("html_path")
            task.pdf_path = result.get("pdf_path")
        self.last_outputs = {
            "json": result.get("json_path"),
            "csv": result.get("csv_path"),
            "html": result.get("html_path"),
            "pdf": result.get("pdf_path"),
        }
        self.preview.setText("\n".join(f"{key.upper()}: {value}" for key, value in self.last_outputs.items() if value))
        self.open_html_button.setEnabled(bool(result.get("html_path")))
        self._refresh_tasks()
        self._log("Scan completed")
        self._start_next_task()

    def _on_failed(self, error: str) -> None:
        running = self._running_task()
        if running:
            task = running
            task.status = "FAILED"
            task.errors.append(error)
            task.message = error
        self._refresh_tasks()
        self._log(f"Scan failed: {error}")
        self._start_next_task()

    def _open_html(self) -> None:
        html = self.last_outputs.get("html")
        if html:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(html)))

    def _open_pdf(self) -> None:
        pdf = self.last_outputs.get("pdf")
        if pdf:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf)))

    def _refresh_tasks(self) -> None:
        tasks = self.queue.all()
        self.tasks.setRowCount(len(tasks))
        for row, task in enumerate(tasks):
            for column, value in enumerate(task.to_row()):
                self.tasks.setItem(row, column, QTableWidgetItem(value))

    def _log(self, message: str) -> None:
        self.log.append(message)

    @staticmethod
    def _list_contains(widget: QListWidget, value: str) -> bool:
        return any(widget.item(index).text() == value for index in range(widget.count()))

    def _project_paths(self) -> list[Path]:
        projects: list[Path] = []
        for index in range(self.projects.count()):
            path = Path(self.projects.item(index).text()).expanduser()
            if path.is_file():
                path = path.parent
            if path.exists() and path.is_dir():
                projects.append(path)
        return projects

    def _running_task(self) -> GuiTask | None:
        for task in self.queue.all():
            if task.status == "RUNNING":
                return task
        return None
