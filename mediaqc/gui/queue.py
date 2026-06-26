"""GUI task queue models independent of PySide6."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class GuiTask:
    project_path: Path
    output_path: Path
    status: str = "PENDING"
    progress: int = 0
    message: str = ""
    json_path: Path | None = None
    csv_path: Path | None = None
    html_path: Path | None = None
    pdf_path: Path | None = None
    errors: list[str] = field(default_factory=list)

    def to_row(self) -> list[str]:
        return [
            str(self.project_path),
            self.status,
            f"{self.progress}%",
            self.message,
        ]


class GuiTaskQueue:
    def __init__(self) -> None:
        self._tasks: list[GuiTask] = []

    def add(self, task: GuiTask) -> None:
        self._tasks.append(task)

    def clear(self) -> None:
        self._tasks.clear()

    def pending(self) -> list[GuiTask]:
        return [task for task in self._tasks if task.status == "PENDING"]

    def all(self) -> list[GuiTask]:
        return list(self._tasks)
