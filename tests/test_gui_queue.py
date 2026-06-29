from pathlib import Path

import mediaqc.gui.source_preview as source_preview
from mediaqc.gui.live_preview import PreviewSettings, build_output_preview_text
from mediaqc.gui.queue import GuiTask, GuiTaskQueue
from mediaqc.gui.results import read_csv_preview
from mediaqc.gui.source_preview import (
    build_source_preview_lines,
    format_duration,
    is_preview_media_file,
    list_preview_media_files,
    list_source_titles,
)
from mediaqc.gui.workers import ScanWorker


def test_gui_task_queue_pending_and_rows(tmp_path: Path) -> None:
    queue = GuiTaskQueue()
    task = GuiTask(project_path=tmp_path / "Project", output_path=tmp_path / "Reports")

    queue.add(task)

    assert queue.pending() == [task]
    assert task.to_row()[1] == "PENDING"


def test_scan_worker_cancel_before_start(tmp_path: Path) -> None:
    worker = ScanWorker(tmp_path / "Project", tmp_path / "Reports")
    worker.cancel()

    result = worker.run()

    assert result["status"] == "CANCELLED"


def test_read_csv_preview_limits_files_and_excludes_folders(tmp_path: Path) -> None:
    folder = tmp_path / "Folder"
    folder.mkdir()
    csv_path = tmp_path / "report.csv"
    rows = ["filename,path,status"]
    rows.append(f"Folder,{folder},PASS")
    for index in range(12):
        media = tmp_path / f"clip_{index}.mov"
        media.write_text("x", encoding="utf-8")
        rows.append(f"{media.name},{media},PASS")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    preview = read_csv_preview(csv_path)

    assert preview.headers == ["filename", "path", "status"]
    assert preview.total_rows == 12
    assert len(preview.rows) == 10
    assert preview.rows[0][0] == "clip_0.mov"


def test_source_preview_lists_only_supported_media_files(tmp_path: Path) -> None:
    (tmp_path / ".DS_Store").write_text("metadata", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("notes", encoding="utf-8")
    (tmp_path / "Folder").mkdir()
    mov = tmp_path / "Opening.mov"
    mp4 = tmp_path / "Preview.mp4"
    mov.write_text("x", encoding="utf-8")
    mp4.write_text("x", encoding="utf-8")

    files, total = list_preview_media_files(tmp_path)

    assert total == 2
    assert [file.name for file in files] == ["Opening.mov", "Preview.mp4"]
    assert is_preview_media_file(mov)
    assert not is_preview_media_file(tmp_path / ".DS_Store")


def test_source_preview_lines_show_detected_file_count(tmp_path: Path) -> None:
    (tmp_path / ".DS_Store").write_text("metadata", encoding="utf-8")
    for index in range(3):
        (tmp_path / f"clip_{index}.mov").write_text("x", encoding="utf-8")

    lines, total = build_source_preview_lines(tmp_path)

    assert total == 3
    assert "Files (3 detected):" in lines
    assert ".DS_Store" not in "\n".join(lines)


def test_source_titles_include_index_duration_and_filename(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    movie = tmp_path / "Opening.mov"
    movie.write_text("x", encoding="utf-8")
    monkeypatch.setattr(source_preview, "probe_duration_label", lambda path: "00:01:05")

    titles = list_source_titles(tmp_path)

    assert len(titles) == 1
    assert titles[0].label == "1 - 00:01:05 - Opening"
    assert titles[0].path == movie


def test_format_duration_handles_fractional_seconds() -> None:
    assert format_duration("65.4") == "00:01:05"
    assert format_duration(None) == "--:--:--"


def test_live_preview_text_uses_selected_source_preset_and_format(tmp_path: Path) -> None:
    source = tmp_path / "clip.mov"
    source.write_text("x", encoding="utf-8")

    text = build_output_preview_text(
        PreviewSettings(source_path=source, preset="Fast 1080p30", output_format="MP4", duration_seconds=30)
    )

    assert "Live Preview" in text
    assert "Source: clip.mov" in text
    assert "Preset: Fast 1080p30" in text
    assert "Format: MP4" in text
    assert "Output: clip.mp4" in text
