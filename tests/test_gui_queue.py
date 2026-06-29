from pathlib import Path

from mediaqc.gui.queue import GuiTask, GuiTaskQueue
from mediaqc.gui.results import read_csv_preview
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
