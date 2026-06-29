"""Main PySide6 window for Loom."""

from __future__ import annotations

from pathlib import Path

from mediaqc import __version__
from mediaqc.branding import PRODUCT_NAME, icon_path
from mediaqc.processing.ffmpeg_runner import resolve_tool_path
from mediaqc.processing.tool_installer import ensure_ffmpeg_bundle_installed

from PySide6.QtCore import QThread, QTimer, Signal, Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QProgressBar,
    QSizePolicy,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .queue import GuiTask, GuiTaskQueue
from .results import read_csv_preview
from .source_preview import is_preview_media_file, list_preview_media_files
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


class ToolInstallThread(QThread):
    completed = Signal(str, bool, str)
    failed = Signal(str)

    def run(self) -> None:
        try:
            result = ensure_ffmpeg_bundle_installed()
            self.completed.emit(str(result.install_dir), result.downloaded, result.source_url)
        except Exception as exc:  # noqa: BLE001 - GUI must surface installer failures.
            self.failed.emit(str(exc))


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
        self.setWindowTitle(PRODUCT_NAME)
        self.setWindowIcon(QIcon(str(icon_path())))
        self.setMinimumSize(1120, 720)
        self.menuBar().setNativeMenuBar(False)
        self.queue = GuiTaskQueue()
        self.current_thread: QtScanThread | None = None
        self.tool_install_thread: ToolInstallThread | None = None
        self.pending_tasks: list[GuiTask] = []
        self.last_outputs: dict[str, Path | None] = {}
        self._build_ui()
        QTimer.singleShot(250, self._check_tools_on_first_run)

    def _build_ui(self) -> None:
        self._build_actions()
        self.workspace = self._workspace_panel()
        self.stack = QStackedWidget()
        self.stack.addWidget(self._welcome_panel())
        self.stack.addWidget(self.workspace)
        self.setCentralWidget(self.stack)

    def _build_actions(self) -> None:
        app_menu = self.menuBar().addMenu(PRODUCT_NAME)
        about = QAction(f"About {PRODUCT_NAME}", self)
        preferences = QAction("Preferences...", self)
        about.triggered.connect(lambda: self._log(f"{PRODUCT_NAME} {__version__}"))
        preferences.triggered.connect(self._open_preferences)
        app_menu.addAction(preferences)
        app_menu.addAction(about)

        file_menu = self.menuBar().addMenu("File")
        new_project = QAction("New Project", self)
        open_project = QAction("Open Project...", self)
        export_html = QAction("Open HTML Report", self)
        export_pdf = QAction("Export PDF", self)
        quit_action = QAction("Quit", self)
        new_project.triggered.connect(self._new_project)
        open_project.triggered.connect(self._browse_project)
        export_html.triggered.connect(self._open_html)
        export_pdf.triggered.connect(self._open_pdf)
        quit_action.triggered.connect(self.close)
        file_menu.addActions([new_project, open_project])
        file_menu.addSeparator()
        file_menu.addActions([export_html, export_pdf])
        file_menu.addSeparator()
        file_menu.addAction(quit_action)

        edit_menu = self.menuBar().addMenu("Edit")
        clear_queue = QAction("Clear Task Queue", self)
        clear_queue.triggered.connect(self._clear_queue)
        edit_menu.addAction(clear_queue)

        view_menu = self.menuBar().addMenu("View")
        welcome_action = QAction("Welcome", self)
        workspace_action = QAction("Workspace", self)
        welcome_action.triggered.connect(lambda: self.stack.setCurrentIndex(0))
        workspace_action.triggered.connect(lambda: self.stack.setCurrentIndex(1))
        view_menu.addActions([welcome_action, workspace_action])

        preset_menu = self.menuBar().addMenu("Presets")
        for name in ["LED 4K", "LED 8K", "Disguise", "Millumin", "TouchDesigner", "Notch"]:
            preset_action = QAction(name, self)
            preset_action.triggered.connect(lambda checked=False, value=name: self._select_preset(value))
            preset_menu.addAction(preset_action)

        window_menu = self.menuBar().addMenu("Window")
        minimize_action = QAction("Minimize", self)
        zoom_action = QAction("Zoom", self)
        minimize_action.triggered.connect(self.showMinimized)
        zoom_action.triggered.connect(self.showMaximized)
        window_menu.addActions([minimize_action, zoom_action])

        help_menu = self.menuBar().addMenu("Help")
        doctor_action = QAction("Tools Doctor", self)
        docs_action = QAction("Documentation", self)
        doctor_action.triggered.connect(lambda: self._log("Run `mediaqc tools doctor` for FFmpeg paths."))
        docs_action.triggered.connect(lambda: self._log("Documentation is available in the repository docs folder."))
        help_menu.addActions([doctor_action, docs_action])

    def _open_preferences(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Preferences")
        dialog.resize(560, 300)
        layout = QVBoxLayout(dialog)
        tabs = QTabWidget()
        basic = QWidget()
        basic_layout = QVBoxLayout(basic)
        title = QLabel("FFmpeg Tools")
        title.setStyleSheet("font-weight: 700; background: transparent;")
        description = QLabel("Install or repair ffmpeg, ffprobe, and ffplay in Loom tools/plugins.")
        description.setWordWrap(True)
        install_button = QPushButton("Install / Repair FFmpeg Tools")
        install_button.setObjectName("PrimaryButton")
        install_button.clicked.connect(self._install_tools_from_preferences)
        basic_layout.addWidget(title)
        basic_layout.addWidget(description)
        basic_layout.addWidget(install_button)
        basic_layout.addStretch(1)
        tabs.addTab(basic, "Basic")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(tabs)
        layout.addWidget(buttons)
        dialog.exec()

    def _check_tools_on_first_run(self) -> None:
        missing = self._missing_tools()
        if not missing:
            self._log("FFmpeg tools detected: ffmpeg, ffprobe, ffplay.")
            return
        names = ", ".join(missing)
        response = QMessageBox.question(
            self,
            "Install FFmpeg Tools",
            f"Loom could not find: {names}.\n\nInstall ffmpeg, ffprobe, and ffplay into tools/plugins now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if response == QMessageBox.StandardButton.Yes:
            self._start_tool_install("Installing FFmpeg tools...")
        else:
            self._log(f"FFmpeg tool install skipped. Missing: {names}")

    def _install_tools_from_preferences(self) -> None:
        self._start_tool_install("Installing FFmpeg tools from Preferences...")

    def _start_tool_install(self, message: str) -> None:
        if self.tool_install_thread and self.tool_install_thread.isRunning():
            self._log("FFmpeg tool installation is already running.")
            return
        self._log(message)
        self.tool_install_thread = ToolInstallThread()
        self.tool_install_thread.completed.connect(self._on_tool_install_completed)
        self.tool_install_thread.failed.connect(self._on_tool_install_failed)
        self.tool_install_thread.start()

    def _on_tool_install_completed(self, install_dir: str, downloaded: bool, source_url: str) -> None:
        status = "Downloaded" if downloaded else "Already installed"
        self._log(f"{status} FFmpeg tools: {install_dir}")
        if source_url:
            self._log(f"FFmpeg source: {source_url}")
        QMessageBox.information(self, "FFmpeg Tools", f"{status} FFmpeg tools in:\n{install_dir}")

    def _on_tool_install_failed(self, error: str) -> None:
        self._log(f"FFmpeg tool install failed: {error}")
        QMessageBox.warning(self, "FFmpeg Tools", f"Install failed:\n{error}")

    @staticmethod
    def _missing_tools() -> list[str]:
        return [name for name in ("ffmpeg", "ffprobe", "ffplay") if resolve_tool_path(name, auto_install=False).path is None]

    def _welcome_panel(self) -> QWidget:
        background = QFrame()
        background.setObjectName("WelcomeBackground")
        outer = QVBoxLayout(background)
        outer.setContentsMargins(72, 58, 72, 58)
        outer.addStretch(1)

        glass = QFrame()
        glass.setObjectName("GlassPanel")
        glass.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(glass)
        layout.setContentsMargins(42, 34, 42, 34)
        layout.setSpacing(16)

        icon_label = QLabel()
        icon_label.setPixmap(QIcon(str(icon_path())).pixmap(72, 72))
        title = QLabel(PRODUCT_NAME)
        title.setStyleSheet("font-size: 36px; font-weight: 700; background: transparent;")
        version = QLabel(f"Version {__version__}")
        version.setStyleSheet("color: #526071; background: transparent;")
        subtitle = QLabel("Media preparation, QC, FFmpeg tooling, and delivery reports for live event workflows.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #344054; font-size: 14px; background: transparent;")

        header = QHBoxLayout()
        header.addWidget(icon_label)
        text_col = QVBoxLayout()
        text_col.addWidget(title)
        text_col.addWidget(version)
        header.addLayout(text_col)
        header.addStretch(1)

        actions = QHBoxLayout()
        new_button = QPushButton("New")
        new_button.setObjectName("PrimaryButton")
        open_button = QPushButton("Open")
        recent_button = QPushButton("Recent")
        new_button.clicked.connect(self._new_project)
        open_button.clicked.connect(self._browse_project)
        recent_button.clicked.connect(self._open_recent)
        actions.addWidget(new_button)
        actions.addWidget(open_button)
        actions.addWidget(recent_button)
        actions.addStretch(1)

        recent_label = QLabel("Recent Projects")
        recent_label.setStyleSheet("font-weight: 600; background: transparent;")
        self.recent_projects = QListWidget()
        self.recent_projects.setMaximumHeight(110)
        self.recent_projects.itemDoubleClicked.connect(lambda item: self._open_project_path(item.text()))

        layout.addLayout(header)
        layout.addWidget(subtitle)
        layout.addLayout(actions)
        layout.addWidget(recent_label)
        layout.addWidget(self.recent_projects)
        outer.addWidget(glass)
        outer.addStretch(2)
        return background

    def _workspace_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._toolbar_panel())
        layout.addWidget(self._source_panel())
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._settings_panel())
        splitter.addWidget(self._right_panel())
        splitter.setSizes([900, 480])
        layout.addWidget(splitter, 1)
        return panel

    def _toolbar_panel(self) -> QWidget:
        toolbar = QFrame()
        toolbar.setObjectName("TopToolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)
        buttons = [
            ("Open Source", self._browse_project, "ToolbarButton"),
            ("Add Queue", self._add_current_to_queue, "ToolbarButton"),
            ("Start", self._start_scan, "ToolbarPrimaryButton"),
            ("Pause", self._cancel_scan, "ToolbarButton"),
        ]
        for text, callback, object_name in buttons:
            button = QPushButton(text)
            button.setObjectName(object_name)
            button.clicked.connect(callback)
            layout.addWidget(button)
        layout.addStretch(1)
        for text, callback in [
            ("Activity", self._focus_logs),
        ]:
            button = QPushButton(text)
            button.setObjectName("ToolbarButton")
            button.clicked.connect(callback)
            layout.addWidget(button)
        return toolbar

    def _source_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("SourcePanel")
        layout = QGridLayout(panel)
        layout.setContentsMargins(18, 14, 18, 12)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(10)
        self.project_input = DropLineEdit()
        self.project_input.dropped.connect(self._add_project)
        self.output_input = QLineEdit(str(Path("./reports").resolve()))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Source title")
        self.range_combo = QComboBox()
        self.range_combo.addItems(["Full Scan", "First 10 Files", "Selected Queue"])
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Unnamed", "H264 Preview", "H265 Preview", "HAP Q 4K", "ProRes 4444", "NotchLC"])
        browse_project = QPushButton("Browse...")
        browse_output = QPushButton("Browse...")
        browse_project.clicked.connect(self._browse_project)
        browse_output.clicked.connect(self._browse_output)
        layout.addWidget(QLabel("Source:"), 0, 0)
        layout.addWidget(self.project_input, 0, 1, 1, 5)
        layout.addWidget(browse_project, 0, 6)
        layout.addWidget(QLabel("Title:"), 1, 0)
        layout.addWidget(self.title_input, 1, 1, 1, 3)
        layout.addWidget(QLabel("Scan Range:"), 1, 4)
        layout.addWidget(self.range_combo, 1, 5, 1, 2)
        layout.addWidget(QLabel("Preset:"), 2, 0)
        layout.addWidget(self.preset_combo, 2, 1, 1, 2)
        layout.addWidget(QLabel("Save As:"), 2, 3)
        layout.addWidget(self.output_input, 2, 4, 1, 3)
        layout.addWidget(browse_output, 2, 7)
        return panel

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

    def _settings_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        self.settings_tabs = QTabWidget()
        self.settings_tabs.addTab(self._summary_tab(), "Summary")
        self.settings_tabs.addTab(self._simple_tab("Dimensions", ["Resolution", "Canvas", "Scaling"]), "Dimensions")
        self.settings_tabs.addTab(self._simple_tab("Filters", ["Deinterlace", "Color", "Sharpen"]), "Filters")
        self.settings_tabs.addTab(self._simple_tab("Video", ["Codec", "Frame Rate", "Bitrate"]), "Video")
        self.settings_tabs.addTab(self._simple_tab("Audio", ["Tracks", "Codec", "Mixdown"]), "Audio")
        self.settings_tabs.addTab(self._simple_tab("Subtitles", ["Tracks", "Burn-in", "Passthrough"]), "Subtitles")
        self.settings_tabs.addTab(self._simple_tab("Chapters", ["Markers", "Export"]), "Chapters")
        layout.addWidget(self.settings_tabs)
        button_row = QHBoxLayout()
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.setObjectName("PrimaryButton")
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
        layout.addLayout(button_row)
        layout.addWidget(self.progress)
        layout.addWidget(QLabel("Task Queue"))
        layout.addWidget(self.tasks)
        return panel

    def _summary_tab(self) -> QWidget:
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setContentsMargins(28, 22, 28, 22)
        self.projects = QListWidget()
        self.rules = QListWidget()
        self.history = QListWidget()
        self.rules.addItems(["project_rules.yaml", "LED_4K", "Disguise", "TouchDesigner"])
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV + JSON + HTML + PDF", "CSV only", "JSON only"])
        self.passthrough_box = QLineEdit("Enabled")
        self.passthrough_box.setReadOnly(True)
        self.source_count_label = QLabel("No source selected")
        layout.addWidget(QLabel("Projects"), 0, 0)
        layout.addWidget(self.projects, 1, 0, 5, 1)
        layout.addWidget(QLabel("Rules"), 0, 1)
        layout.addWidget(self.rules, 1, 1, 5, 1)
        layout.addWidget(QLabel("Format:"), 1, 2)
        layout.addWidget(self.format_combo, 1, 3)
        layout.addWidget(QLabel("Metadata:"), 2, 2)
        layout.addWidget(self.passthrough_box, 2, 3)
        layout.addWidget(QLabel("Source files:"), 3, 2)
        layout.addWidget(self.source_count_label, 3, 3)
        layout.setColumnStretch(3, 1)
        return panel

    def _simple_tab(self, title: str, rows: list[str]) -> QWidget:
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setVerticalSpacing(18)
        for index, label in enumerate(rows):
            layout.addWidget(QLabel(f"{label}:"), index, 0)
            field = QLineEdit("Auto")
            field.setReadOnly(True)
            layout.addWidget(field, index, 1)
        layout.setColumnStretch(1, 1)
        return panel

    def _right_panel(self) -> QWidget:
        tabs = QTabWidget()
        self.right_tabs = tabs
        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        compare_row = QHBoxLayout()
        source_box = QGroupBox("Source Preview")
        source_layout = QVBoxLayout(source_box)
        self.source_preview = QTextEdit()
        self.source_preview.setReadOnly(True)
        self.source_preview.setText("Open a source folder or file.")
        source_layout.addWidget(self.source_preview)
        output_box = QGroupBox("Output Preview")
        output_layout = QVBoxLayout(output_box)
        self.output_preview = QTextEdit()
        self.output_preview.setReadOnly(True)
        self.output_preview.setText("Scan, compress, or transcode to compare output here.")
        output_layout.addWidget(self.output_preview)
        compare_row.addWidget(source_box)
        compare_row.addWidget(output_box)
        preview_layout.addLayout(compare_row)
        self.preview = self.output_preview
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        tabs.addTab(preview_panel, "Preview Compare")
        tabs.addTab(self.log, "Logs")
        return tabs

    def _browse_project(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self._open_project_path(folder)

    def _browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_input.setText(folder)

    def _add_project(self, path: str) -> None:
        if path and not self._list_contains(self.projects, path):
            self.projects.addItem(path)
        if path and not self._list_contains(self.recent_projects, path):
            self.recent_projects.addItem(path)
        self._update_source_preview(Path(path))

    def _new_project(self) -> None:
        self.stack.setCurrentIndex(1)
        self.project_input.clear()
        self.project_input.setFocus()
        self._log("New project ready.")

    def _open_project_path(self, path: str) -> None:
        self.stack.setCurrentIndex(1)
        self.project_input.setText(path)
        self._add_project(path)

    def _open_recent(self) -> None:
        if self.recent_projects.count() == 0:
            self._log("No recent projects yet.")
            return
        self._open_project_path(self.recent_projects.item(0).text())

    def _clear_queue(self) -> None:
        self.queue.clear()
        self.pending_tasks = []
        self._refresh_tasks()
        self.progress.setValue(0)
        self._log("Task queue cleared.")

    def _select_preset(self, name: str) -> None:
        self.stack.setCurrentIndex(1)
        matches = self.rules.findItems(name, Qt.MatchFlag.MatchContains)
        if matches:
            self.rules.setCurrentItem(matches[0])
        self._log(f"Preset selected: {name}")

    def _add_current_to_queue(self) -> None:
        path = self.project_input.text().strip()
        if not path:
            self._log("No source selected for queue.")
            return
        self._add_project(path)
        self._log(f"Added to queue: {path}")

    def _focus_logs(self) -> None:
        self.stack.setCurrentIndex(1)
        self.right_tabs.setCurrentIndex(1)
        self.log.setFocus()

    def _update_source_preview(self, path: Path) -> None:
        if not hasattr(self, "source_preview"):
            return
        path = Path(path)
        if path.is_dir():
            files, total_files = list_preview_media_files(path)
            self.source_count_label.setText(f"{total_files} top-level media files")
            preview_lines = [f"Source folder: {path}", "", "Files:"]
            if files:
                preview_lines.extend(f"- {item.name}" for item in files)
            else:
                preview_lines.append("No supported media files found.")
            if total_files > len(files):
                preview_lines.append(f"... {total_files - len(files)} more")
            self.source_preview.setText("\n".join(preview_lines))
        else:
            self.source_count_label.setText("1 media file" if is_preview_media_file(path) else "No supported media selected")
            self.source_preview.setText(f"Source file:\n{path}")

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
        self._show_scan_result_dialog(result)
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

    def _show_scan_result_dialog(self, result: dict) -> None:
        csv_path = result.get("csv_path")
        if not csv_path:
            return
        preview = read_csv_preview(Path(csv_path), limit=10)
        if not preview.headers:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Scan Results")
        dialog.resize(980, 420)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"CSV preview: {csv_path}"))
        table = QTableWidget(len(preview.rows), len(preview.headers))
        table.setHorizontalHeaderLabels(preview.headers)
        for row_index, row in enumerate(preview.rows):
            for column_index, value in enumerate(row):
                table.setItem(row_index, column_index, QTableWidgetItem(value))
        layout.addWidget(table)
        layout.addWidget(QLabel(f"Showing {len(preview.rows)} of {preview.total_rows} file rows. Folders are excluded."))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Open | QDialogButtonBox.StandardButton.Close)
        buttons.accepted.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(csv_path))))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

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
