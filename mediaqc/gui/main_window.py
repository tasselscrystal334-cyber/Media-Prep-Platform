"""Main PySide6 window for Loom."""

from __future__ import annotations

import subprocess
from pathlib import Path

from mediaqc import __version__
from mediaqc.branding import PRODUCT_NAME, icon_path
from mediaqc.processing.ffmpeg_runner import build_doctor_report, resolve_tool_path
from mediaqc.processing.tool_installer import ensure_ffmpeg_bundle_installed

from PySide6.QtCore import QThread, QTimer, Signal, Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
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

from .live_preview import PreviewSettings, build_output_preview, build_output_preview_text, build_transcode_args
from .queue import GuiTask
from .results import read_csv_preview
from .source_preview import build_source_preview_lines, is_preview_media_file
from .workers import ScanWorker

PRESET_GROUPS = {
    "Codec": ["H.264", "H.265 / HEVC", "ProRes 422 HQ", "ProRes 4444 Alpha", "HAP", "HAP Q", "HAP Alpha", "HAP Q Alpha", "NotchLC"],
    "Frame Rate": ["Source FPS", "24 fps", "25 fps", "29.97 fps", "30 fps", "50 fps", "59.94 fps", "60 fps"],
    "Proxy": ["Proxy H.264 1080p", "Proxy H.265 1080p", "Proxy ProRes 1080p"],
}

VIDEO_FORMATS = ["MOV", "MP4", "MKV", "MXF", "AVI", "WebM"]


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


class OutputPreviewThread(QThread):
    completed = Signal(str)
    failed = Signal(str)

    def __init__(self, settings: PreviewSettings, preview_dir: Path) -> None:
        super().__init__()
        self.settings = settings
        self.preview_dir = preview_dir

    def run(self) -> None:
        try:
            ffmpeg = resolve_tool_path("ffmpeg", auto_install=False)
            if not ffmpeg.path:
                raise RuntimeError("ffmpeg is required to generate live output previews.")
            preview = build_output_preview(self.settings, self.preview_dir)
            command = [ffmpeg.path, *preview.ffmpeg_args]
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
                check=False,
            )
            if completed.returncode != 0 or not preview.output_path.exists():
                detail = completed.stderr.strip() or completed.stdout.strip() or "Unknown FFmpeg error"
                raise RuntimeError(f"Preview render failed: {detail}")
            self.completed.emit(str(preview.output_path))
        except Exception as exc:  # noqa: BLE001 - GUI must show preview errors.
            self.failed.emit(str(exc))


class TranscodeThread(QThread):
    progress = Signal(int, int, str)
    completed = Signal()
    failed = Signal(int, str)

    def __init__(self, jobs: list[tuple[Path, Path, str, str, str, str | None]]) -> None:
        super().__init__()
        self.jobs = jobs
        self.cancel_requested = False

    def run(self) -> None:
        ffmpeg = resolve_tool_path("ffmpeg", auto_install=False)
        if not ffmpeg.path:
            self.failed.emit(-1, "ffmpeg is required for transcoding.")
            return
        for index, (source, output, preset, output_format, fps, crop_filter) in enumerate(self.jobs):
            if self.cancel_requested:
                self.failed.emit(index, "Transcode cancelled.")
                return
            output.parent.mkdir(parents=True, exist_ok=True)
            self.progress.emit(index, 5, "Running")
            command = [ffmpeg.path, *build_transcode_args(source, output, preset, output_format, fps, crop_filter)]
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
                check=False,
            )
            if completed.returncode != 0:
                detail = completed.stderr.strip() or completed.stdout.strip() or "Unknown FFmpeg error"
                self.failed.emit(index, detail)
                return
            self.progress.emit(index, 100, "Done")
        self.completed.emit()

    def cancel(self) -> None:
        self.cancel_requested = True


class DropMediaList(QListWidget):
    dropped = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def dragEnterEvent(self, event) -> None:  # noqa: ANN001
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # noqa: ANN001
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile()]
        if paths:
            self.dropped.emit(paths)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(PRODUCT_NAME)
        self.setWindowIcon(QIcon(str(icon_path())))
        self.setMinimumSize(1120, 720)
        self.menuBar().setNativeMenuBar(False)
        self.current_thread: QtScanThread | None = None
        self.current_task: GuiTask | None = None
        self.tool_install_thread: ToolInstallThread | None = None
        self.preview_thread: OutputPreviewThread | None = None
        self.preview_process: subprocess.Popen | None = None
        self.transcode_thread: TranscodeThread | None = None
        self.pending_tasks: list[GuiTask] = []
        self.last_outputs: dict[str, Path | None] = {}
        self.media_files: list[Path] = []
        self.selected_preset = "ProRes 422 HQ"
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
        new_project = QAction("New Batch", self)
        open_project = QAction("Import Folder...", self)
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
        clear_queue = QAction("Clear Files", self)
        clear_queue.triggered.connect(self._clear_files)
        edit_menu.addAction(clear_queue)

        view_menu = self.menuBar().addMenu("View")
        welcome_action = QAction("Welcome", self)
        workspace_action = QAction("Workspace", self)
        welcome_action.triggered.connect(lambda: self.stack.setCurrentIndex(0))
        workspace_action.triggered.connect(lambda: self.stack.setCurrentIndex(1))
        view_menu.addActions([welcome_action, workspace_action])

        preset_menu = self.menuBar().addMenu("Presets")
        for group_name, presets in PRESET_GROUPS.items():
            submenu = preset_menu.addMenu(group_name)
            for name in presets:
                preset_action = QAction(name, self)
                preset_action.triggered.connect(lambda checked=False, value=name: self._set_output_preset(value))
                submenu.addAction(preset_action)

        window_menu = self.menuBar().addMenu("Window")
        minimize_action = QAction("Minimize", self)
        zoom_action = QAction("Zoom", self)
        minimize_action.triggered.connect(self.showMinimized)
        zoom_action.triggered.connect(self.showMaximized)
        window_menu.addActions([minimize_action, zoom_action])

        help_menu = self.menuBar().addMenu("Help")
        doctor_action = QAction("Tools Doctor", self)
        docs_action = QAction("Documentation", self)
        doctor_action.triggered.connect(self._open_tools_doctor)
        docs_action.triggered.connect(self._open_documentation)
        help_menu.addActions([doctor_action, docs_action])

    def _open_tools_doctor(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Tools Doctor")
        dialog.resize(860, 520)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Check", "Value"])
        layout.addWidget(QLabel("FFmpeg, FFprobe, FFplay, codec, and Adobe Media Encoder diagnostics."))
        layout.addWidget(table)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        try:
            report = build_doctor_report()
            values = report.to_dict()
            rows = [(key, "; ".join(value) if isinstance(value, list) else str(value)) for key, value in values.items()]
        except Exception as exc:  # noqa: BLE001 - diagnostics should surface errors in UI.
            rows = [("error", str(exc))]

        table.setRowCount(len(rows))
        for row_index, (key, value) in enumerate(rows):
            table.setItem(row_index, 0, QTableWidgetItem(key))
            table.setItem(row_index, 1, QTableWidgetItem(value))
        table.resizeColumnsToContents()
        self._log("Tools Doctor opened.")
        dialog.exec()

    def _open_documentation(self) -> None:
        candidates = [
            Path.cwd() / "docs" / "README.md",
            Path(__file__).resolve().parents[2] / "docs" / "README.md",
            Path(__file__).resolve().parents[2] / "README.md",
        ]
        for path in candidates:
            if path.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
                self._log(f"Documentation opened: {path}")
                return
        QMessageBox.information(self, "Documentation", "Documentation files were not found in this local install.")

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
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self._batch_panel())
        splitter.addWidget(self._right_panel())
        splitter.setSizes([460, 300])
        layout.addWidget(splitter, 1)
        return panel

    def _toolbar_panel(self) -> QWidget:
        toolbar = QFrame()
        toolbar.setObjectName("TopToolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)
        buttons = [
            ("Import Files", self._browse_files, "ToolbarButton"),
            ("Import Folder", self._browse_project, "ToolbarButton"),
            ("Analyze", self._start_scan, "ToolbarPrimaryButton"),
            ("SHA256", self._start_scan, "ToolbarButton"),
            ("Play", self._play_selected_media, "ToolbarButton"),
            ("Transcode", self._start_transcode, "ToolbarPrimaryButton"),
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

    def _batch_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("SourcePanel")
        layout = QGridLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setHorizontalSpacing(18)
        layout.setVerticalSpacing(10)

        files_title = QLabel("Files to process")
        files_title.setStyleSheet("font-weight: 700; font-size: 15px;")
        import_files = QPushButton("Import Files")
        import_folder = QPushButton("Import Folder")
        clear_files = QPushButton("Clear")
        import_files.clicked.connect(self._browse_files)
        import_folder.clicked.connect(self._browse_project)
        clear_files.clicked.connect(self._clear_files)
        file_buttons = QHBoxLayout()
        file_buttons.addWidget(import_files)
        file_buttons.addWidget(import_folder)
        file_buttons.addWidget(clear_files)
        self.files_list = DropMediaList()
        self.files_list.dropped.connect(self._add_media_paths)
        self.files_list.currentRowChanged.connect(lambda _row: self._on_file_selection_changed())

        format_title = QLabel("Output settings")
        format_title.setStyleSheet("font-weight: 700; font-size: 15px;")
        self.format_combo = QComboBox()
        self.format_combo.addItems(VIDEO_FORMATS)
        self.format_combo.setCurrentText("MOV")
        self.format_combo.currentIndexChanged.connect(lambda _index: self._refresh_output_files())
        self.codec_combo = QComboBox()
        self.codec_combo.addItems(PRESET_GROUPS["Codec"])
        self.codec_combo.setCurrentText("ProRes 422 HQ")
        self.codec_combo.currentIndexChanged.connect(lambda _index: self._sync_preset_from_controls())
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(PRESET_GROUPS["Frame Rate"])
        self.fps_combo.currentIndexChanged.connect(lambda _index: self._sync_preset_from_controls())
        self.proxy_combo = QComboBox()
        self.proxy_combo.addItems(["None", *PRESET_GROUPS["Proxy"]])
        self.proxy_combo.currentIndexChanged.connect(lambda _index: self._sync_preset_from_controls())
        self.audio_mode = QLineEdit("Copy original audio")
        self.audio_mode.setReadOnly(True)

        rename_title = QLabel("File renaming")
        rename_title.setStyleSheet("font-weight: 700; font-size: 15px;")
        self.remove_text = QLineEdit("")
        self.append_text = QLineEdit("")
        self.prefix_text = QLineEdit("")
        for field in (self.remove_text, self.append_text, self.prefix_text):
            field.textChanged.connect(self._refresh_output_files)
        self.same_as_source_checkbox = QCheckBox("Same as source")
        self.same_as_source_checkbox.setChecked(True)
        self.same_as_source_checkbox.stateChanged.connect(lambda _state: self._on_destination_mode_changed())
        self.output_input = QLineEdit("")
        self.output_input.setEnabled(False)
        choose_output = QPushButton("Choose...")
        choose_output.clicked.connect(self._browse_output)
        self.choose_output_button = choose_output
        self.choose_output_button.setEnabled(False)

        output_title = QLabel("Output files")
        output_title.setStyleSheet("font-weight: 700; font-size: 15px;")
        export_button = QPushButton("Export")
        export_button.setObjectName("PrimaryButton")
        export_button.clicked.connect(self._start_transcode)
        self.output_table = QTableWidget(0, 2)
        self.output_table.setHorizontalHeaderLabels(["File", "Status"])
        self.output_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)

        layout.addWidget(files_title, 0, 0)
        layout.addLayout(file_buttons, 1, 0)
        layout.addWidget(self.files_list, 2, 0, 8, 1)

        layout.addWidget(format_title, 0, 1)
        layout.addWidget(QLabel("Format:"), 1, 1)
        layout.addWidget(self.format_combo, 2, 1)
        layout.addWidget(QLabel("Codec:"), 3, 1)
        layout.addWidget(self.codec_combo, 4, 1)
        layout.addWidget(QLabel("Frame rate:"), 5, 1)
        layout.addWidget(self.fps_combo, 6, 1)
        layout.addWidget(QLabel("Proxy:"), 7, 1)
        layout.addWidget(self.proxy_combo, 8, 1)
        layout.addWidget(self.audio_mode, 9, 1)

        layout.addWidget(rename_title, 0, 2)
        layout.addWidget(QLabel("Remove:"), 1, 2)
        layout.addWidget(self.remove_text, 2, 2)
        layout.addWidget(QLabel("Append:"), 3, 2)
        layout.addWidget(self.append_text, 4, 2)
        layout.addWidget(QLabel("Prefix:"), 5, 2)
        layout.addWidget(self.prefix_text, 6, 2)
        layout.addWidget(QLabel("Destination:"), 7, 2)
        layout.addWidget(self.same_as_source_checkbox, 8, 2)
        destination_row = QHBoxLayout()
        destination_row.addWidget(self.output_input)
        destination_row.addWidget(choose_output)
        layout.addLayout(destination_row, 9, 2)

        layout.addWidget(output_title, 0, 3)
        layout.addWidget(export_button, 1, 3)
        layout.addWidget(self.output_table, 2, 3, 8, 1)
        layout.addWidget(self.progress, 10, 0, 1, 4)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 2)
        return panel

    def _right_panel(self) -> QWidget:
        tabs = QTabWidget()
        self.right_tabs = tabs

        source_panel = QWidget()
        source_layout = QVBoxLayout(source_panel)
        self.source_preview = QTextEdit()
        self.source_preview.setReadOnly(True)
        self.source_preview.setText("Open a source folder or file.")
        self.source_preview.setMinimumHeight(420)
        source_layout.addWidget(self.source_preview)

        output_panel = QWidget()
        output_layout = QVBoxLayout(output_panel)
        output_layout.setContentsMargins(18, 16, 18, 16)
        output_layout.setSpacing(12)
        self.output_preview = QTextEdit()
        self.output_preview.setReadOnly(True)
        self.output_preview.setText("Select a title, preset, and format, then start live preview.")
        self.output_preview.setMinimumHeight(150)
        self.output_preview.setMaximumHeight(190)
        self.output_preview_image = QLabel("Live output preview opens in an FFplay window.")
        self.output_preview_image.setObjectName("PreviewCanvas")
        self.output_preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_preview_image.setMinimumHeight(260)
        self.output_preview_image.setMaximumHeight(260)
        self.output_preview_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        crop_layout = QHBoxLayout()
        self.crop_left = QLineEdit("0")
        self.crop_top = QLineEdit("0")
        self.crop_width = QLineEdit("Auto")
        self.crop_height = QLineEdit("Auto")
        for field in (self.crop_left, self.crop_top, self.crop_width, self.crop_height):
            field.setMaximumWidth(84)
        crop_layout.addWidget(QLabel("Crop:"))
        crop_layout.addWidget(QLabel("X"))
        crop_layout.addWidget(self.crop_left)
        crop_layout.addWidget(QLabel("Y"))
        crop_layout.addWidget(self.crop_top)
        crop_layout.addWidget(QLabel("W"))
        crop_layout.addWidget(self.crop_width)
        crop_layout.addWidget(QLabel("H"))
        crop_layout.addWidget(self.crop_height)
        crop_layout.addStretch(1)
        preview_controls = QHBoxLayout()
        self.preview_duration_combo = QComboBox()
        self.preview_duration_combo.addItems(["10 sec", "30 sec", "60 sec"])
        self.preview_duration_combo.setFixedWidth(130)
        live_preview_button = QPushButton("Start Live Preview")
        live_preview_button.setObjectName("PrimaryButton")
        live_preview_button.setFixedWidth(180)
        live_preview_button.clicked.connect(self._start_live_preview)
        preview_controls.addWidget(QLabel("Live Preview:"))
        preview_controls.addWidget(self.preview_duration_combo)
        preview_controls.addWidget(live_preview_button)
        preview_controls.addStretch(1)
        output_layout.addWidget(self.output_preview_image)
        output_layout.addWidget(self.output_preview)
        output_layout.addLayout(crop_layout)
        output_layout.addLayout(preview_controls)
        self.preview = self.output_preview
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        tabs.addTab(source_panel, "Source Preview")
        tabs.addTab(output_panel, "Output Preview")
        tabs.addTab(self.log, "Logs")
        return tabs

    def _browse_project(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self._add_media_paths([folder])

    def _browse_files(self) -> None:
        files, _selected_filter = QFileDialog.getOpenFileNames(
            self,
            "Select Media Files",
            str(Path.home()),
            "Media Files (*.mov *.mp4 *.mxf *.avi *.mkv *.png *.jpg *.jpeg *.tif *.tiff *.exr *.wav *.aiff *.mp3);;All Files (*)",
        )
        if files:
            self._add_media_paths(files)

    def _browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_input.setText(folder)
            self.same_as_source_checkbox.setChecked(False)
            self._refresh_output_files()

    def _add_project(self, path: str) -> None:
        self._add_media_paths([path])

    def _add_media_paths(self, paths: list[str] | list[Path]) -> None:
        discovered: list[Path] = []
        for raw_path in paths:
            path = Path(raw_path).expanduser()
            if path.is_dir():
                discovered.extend(item for item in sorted(path.rglob("*"), key=lambda item: str(item).casefold()) if is_preview_media_file(item))
            elif is_preview_media_file(path):
                discovered.append(path)
        existing = {path.resolve() for path in self.media_files if path.exists()}
        for path in discovered:
            resolved = path.resolve()
            if resolved in existing:
                continue
            self.media_files.append(path)
            existing.add(resolved)
            item = QListWidgetItem(path.name)
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            self.files_list.addItem(item)
        if self.files_list.count() and self.files_list.currentRow() < 0:
            self.files_list.setCurrentRow(0)
        if self.media_files and not self.output_input.text():
            self.output_input.setText(str(self.media_files[0].parent))
        first_path = str(Path(paths[0]).expanduser()) if paths else ""
        if first_path and not self._list_contains(self.recent_projects, first_path):
            self.recent_projects.addItem(first_path)
        self._on_file_selection_changed()
        self._refresh_output_files()
        self._log(f"Imported {len(discovered)} supported media file(s).")

    def _clear_files(self) -> None:
        self.media_files = []
        self.files_list.clear()
        self.output_table.setRowCount(0)
        self.source_preview.setText("Import media files or drag files/folders into the list.")
        self.output_preview.setText("Select a file, codec, frame rate, proxy, and format, then start live preview.")
        self.progress.setValue(0)
        self._log("Media file list cleared.")

    def _on_destination_mode_changed(self) -> None:
        enabled = not self.same_as_source_checkbox.isChecked()
        self.output_input.setEnabled(enabled)
        self.choose_output_button.setEnabled(enabled)
        self._refresh_output_files()

    def _sync_preset_from_controls(self) -> None:
        proxy = self.proxy_combo.currentText()
        self.selected_preset = proxy if proxy != "None" else self.codec_combo.currentText()
        self._refresh_output_files()
        self._update_output_preview_placeholder()

    def _on_file_selection_changed(self) -> None:
        source = self._selected_title_path()
        if not source:
            return
        self._update_source_preview(source)
        self._update_output_preview_placeholder()

    def _refresh_output_files(self) -> None:
        if not hasattr(self, "output_table"):
            return
        self.output_table.setRowCount(len(self.media_files))
        for row, source in enumerate(self.media_files):
            output_path = self._output_path_for(source)
            self.output_table.setItem(row, 0, QTableWidgetItem(str(output_path)))
            self.output_table.setItem(row, 1, QTableWidgetItem("Ready"))

    def _output_path_for(self, source: Path) -> Path:
        destination = source.parent if self.same_as_source_checkbox.isChecked() else Path(self.output_input.text()).expanduser()
        extension = f".{self.format_combo.currentText().lower()}"
        stem = source.stem
        remove = self.remove_text.text()
        if remove:
            stem = stem.replace(remove, "")
        stem = f"{self.prefix_text.text()}{stem}{self.append_text.text()}"
        return destination / f"{stem}{extension}"

    def _new_project(self) -> None:
        self.stack.setCurrentIndex(1)
        self._clear_files()
        self._log("New project ready.")

    def _open_project_path(self, path: str) -> None:
        self.stack.setCurrentIndex(1)
        self._add_media_paths([path])

    def _open_recent(self) -> None:
        if self.recent_projects.count() == 0:
            self._log("No recent projects yet.")
            return
        self._open_project_path(self.recent_projects.item(0).text())

    def _select_preset(self, name: str) -> None:
        self.stack.setCurrentIndex(1)
        self._set_output_preset(name)

    def _set_output_preset(self, name: str) -> None:
        self.selected_preset = name
        if hasattr(self, "codec_combo") and name in PRESET_GROUPS["Codec"]:
            self.codec_combo.setCurrentText(name)
        elif hasattr(self, "fps_combo") and name in PRESET_GROUPS["Frame Rate"]:
            self.fps_combo.setCurrentText(name)
        elif hasattr(self, "proxy_combo") and name in PRESET_GROUPS["Proxy"]:
            self.proxy_combo.setCurrentText(name)
        self._log(f"Output preset selected: {name}")
        self._update_output_preview_placeholder()

    def _focus_logs(self) -> None:
        self.stack.setCurrentIndex(1)
        self.right_tabs.setCurrentIndex(2)
        self.log.setFocus()

    def _update_source_preview(self, path: Path) -> None:
        if not hasattr(self, "source_preview"):
            return
        path = Path(path)
        if path.is_dir():
            preview_lines, total_files = build_source_preview_lines(path)
            self.source_preview.setText("\n".join(preview_lines))
            self._log(f"{total_files} supported media file(s) detected.")
        else:
            self.source_preview.setText(f"Source file:\n{path}")

    def _selected_title_path(self) -> Path | None:
        if hasattr(self, "files_list") and self.files_list.currentItem():
            value = self.files_list.currentItem().data(Qt.ItemDataRole.UserRole)
            return Path(value) if value else None
        return self.media_files[0] if self.media_files else None

    def _update_output_preview_placeholder(self) -> None:
        source = self._selected_title_path()
        name = source.name if source else "No title selected"
        self.output_preview.setText(
            "\n".join(
                [
                    "Output Preview",
                    "",
                    f"Title: {name}",
                    f"Preset: {self.selected_preset}",
                    f"Format: {self.format_combo.currentText()}",
                    "",
                    "Click Start Live Preview to generate a short output video and play it in realtime.",
                ]
            )
        )

    def _start_live_preview(self) -> None:
        seconds = int(self.preview_duration_combo.currentText().split()[0])
        settings = PreviewSettings(
            source_path=self._selected_title_path(),
            preset=self.selected_preset,
            output_format=self.format_combo.currentText(),
            duration_seconds=seconds,
        )
        self.output_preview.setText(build_output_preview_text(settings))
        self._start_output_video_preview(settings)
        self.right_tabs.setCurrentIndex(1)
        self._log("Live output preview requested.")

    def _play_selected_media(self) -> None:
        source = self._selected_title_path()
        if not source or not source.exists():
            self._log("No media file selected for playback.")
            return
        ffplay = resolve_tool_path("ffplay", auto_install=False)
        if not ffplay.path:
            self._log("Playback skipped: ffplay was not found.")
            QMessageBox.warning(self, "Playback", "ffplay is required for playback. Install FFmpeg tools first.")
            return
        command = [
            ffplay.path,
            "-fs",
            "-window_title",
            f"Loom Player - {source.name}",
        ]
        crop_filter = self._crop_filter()
        if crop_filter:
            command.extend(["-vf", crop_filter])
        command.append(str(source))
        self._stop_preview_process()
        try:
            self.preview_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # noqa: S603
        except OSError as exc:
            self._log(f"Unable to launch player: {exc}")
            return
        self.right_tabs.setCurrentIndex(1)
        self.output_preview_image.setText(f"Playing selected media in fullscreen FFplay:\n{source}")
        self._log(f"Playback started: {source}")

    def _crop_filter(self) -> str | None:
        width = self.crop_width.text().strip()
        height = self.crop_height.text().strip()
        if width.lower() == "auto" or height.lower() == "auto":
            return None
        try:
            int(width)
            int(height)
            int(self.crop_left.text())
            int(self.crop_top.text())
        except ValueError:
            self._log("Crop ignored: X/Y/W/H must be integers, or W/H can be Auto.")
            return None
        return f"crop={width}:{height}:{self.crop_left.text()}:{self.crop_top.text()}"

    def _start_output_video_preview(self, settings: PreviewSettings) -> None:
        if not settings.source_path or not settings.source_path.exists():
            self.output_preview_image.setText("Select a media title to preview.")
            return
        if self.preview_thread and self.preview_thread.isRunning():
            self.output_preview_image.setText("Preview render is already running.")
            return
        self._stop_preview_process()
        ffmpeg = resolve_tool_path("ffmpeg", auto_install=False)
        if not ffmpeg.path:
            self.output_preview_image.setText("ffmpeg is required for live output preview.")
            self._log("Live output preview skipped: ffmpeg was not found.")
            return
        self.output_preview_image.setText("Generating output preview video...")
        self.preview_thread = OutputPreviewThread(settings, Path.cwd() / ".preview")
        self.preview_thread.completed.connect(self._on_output_preview_ready)
        self.preview_thread.failed.connect(self._on_output_preview_failed)
        self.preview_thread.start()

    def _on_output_preview_ready(self, output_path: str) -> None:
        ffplay = resolve_tool_path("ffplay", auto_install=False)
        if not ffplay.path:
            self.output_preview_image.setText(f"Preview video generated:\n{output_path}\n\nffplay is required to play it.")
            self._log("Output preview generated, but ffplay was not found.")
            return
        command = [
            ffplay.path,
            "-autoexit",
            "-window_title",
            "Loom Output Preview",
            output_path,
        ]
        try:
            self.preview_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # noqa: S603
        except OSError as exc:
            self.output_preview_image.setText(f"Preview video generated:\n{output_path}\n\nUnable to launch ffplay.")
            self._log(f"Unable to launch ffplay: {exc}")
            return
        self.output_preview_image.setText(f"Playing output preview in FFplay:\n{output_path}")
        self.output_preview.setText(
            "\n".join(
                [
                    self.output_preview.toPlainText(),
                    "",
                    "Preview status: playing realtime output video",
                    f"Preview file: {output_path}",
                ]
            )
        )
        self._log(f"Output preview playing: {output_path}")

    def _on_output_preview_failed(self, error: str) -> None:
        self.output_preview_image.setText("Unable to generate output preview video.")
        self.output_preview.setText(f"{self.output_preview.toPlainText()}\n\nPreview error: {error}")
        self._log(f"Output preview failed: {error}")

    def _stop_preview_process(self) -> None:
        if self.preview_process and self.preview_process.poll() is None:
            self.preview_process.terminate()
        self.preview_process = None

    def _start_transcode(self) -> None:
        if not self.media_files:
            self._log("No media files selected for transcode.")
            return
        if self.transcode_thread and self.transcode_thread.isRunning():
            self._log("Transcode is already running.")
            return
        jobs = [
            (
                source,
                self._output_path_for(source),
                self.selected_preset,
                self.format_combo.currentText(),
                self.fps_combo.currentText(),
                self._crop_filter(),
            )
            for source in self.media_files
        ]
        for row in range(self.output_table.rowCount()):
            self.output_table.setItem(row, 1, QTableWidgetItem("Waiting"))
        self.transcode_thread = TranscodeThread(jobs)
        self.transcode_thread.progress.connect(self._on_transcode_progress)
        self.transcode_thread.completed.connect(self._on_transcode_completed)
        self.transcode_thread.failed.connect(self._on_transcode_failed)
        self.transcode_thread.start()
        self._log(f"Transcode started for {len(jobs)} file(s). Audio mode: copy original audio.")

    def _on_transcode_progress(self, row: int, value: int, message: str) -> None:
        if row >= 0 and row < self.output_table.rowCount():
            self.output_table.setItem(row, 1, QTableWidgetItem(message))
        total = max(1, len(self.media_files))
        self.progress.setValue(int(((row + 1) / total) * value))

    def _on_transcode_completed(self) -> None:
        self.progress.setValue(100)
        self._log("Transcode completed.")

    def _on_transcode_failed(self, row: int, error: str) -> None:
        if row >= 0 and row < self.output_table.rowCount():
            self.output_table.setItem(row, 1, QTableWidgetItem("Failed"))
        self._log(f"Transcode failed: {error}")

    def _start_scan(self) -> None:
        projects = self._project_paths()
        if not projects:
            self._log("No valid media files selected.")
            return
        self.pending_tasks = [
            GuiTask(project_path=project, output_path=project / "loom_reports", status="PENDING", progress=0, message="Pending")
            for project in projects
        ]
        self._start_next_task()

    def _start_next_task(self) -> None:
        if not self.pending_tasks:
            self.current_task = None
            return
        task = self.pending_tasks.pop(0)
        self.current_task = task
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

    def _on_progress(self, value: int, message: str) -> None:
        self.progress.setValue(value)
        running = self.current_task
        if running:
            task = running
            task.progress = value
            task.message = message
        self._log(message)

    def _on_completed(self, result: dict) -> None:
        running = self.current_task
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
        if hasattr(self, "open_html_button"):
            self.open_html_button.setEnabled(bool(result.get("html_path")))
        self._log("Scan completed")
        self._show_scan_result_dialog(result)
        self._start_next_task()

    def _on_failed(self, error: str) -> None:
        running = self.current_task
        if running:
            task = running
            task.status = "FAILED"
            task.errors.append(error)
            task.message = error
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
        return

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
        return sorted({path.parent for path in self.media_files if path.exists()})

    def _running_task(self) -> GuiTask | None:
        return self.current_task if self.current_task and self.current_task.status == "RUNNING" else None

    def closeEvent(self, event) -> None:  # noqa: ANN001
        self._stop_preview_process()
        if self.preview_thread and self.preview_thread.isRunning():
            self.preview_thread.quit()
            self.preview_thread.wait(1500)
        if self.transcode_thread and self.transcode_thread.isRunning():
            self.transcode_thread.cancel()
            self.transcode_thread.wait(1500)
        super().closeEvent(event)
