from pathlib import Path

from mediaqc.gui.queue import GuiTask, GuiTaskQueue
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
