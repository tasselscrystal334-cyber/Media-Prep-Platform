from pathlib import Path

from mediaqc.gui.queue import GuiTask, GuiTaskQueue
from mediaqc.gui.results import read_csv_preview
from mediaqc.gui.source_preview import build_source_preview_lines, is_preview_media_file, list_preview_media_files
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
