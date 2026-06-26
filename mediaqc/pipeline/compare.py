"""SHA256 comparison between project and server paths."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from mediaqc.hash_check import calculate_sha256
from mediaqc.scanner import scan_media_files

COMPARE_FIELDS = ["relative_path", "source_sha256", "destination_sha256", "status", "error"]


def compare_sha256(source: Path, destination: Path) -> dict[str, Any]:
    src = Path(source).resolve()
    dst = Path(destination).resolve()
    records: list[dict[str, Any]] = []
    for media in scan_media_files(src):
        relative = str(Path(media.path).resolve().relative_to(src))
        destination_path = dst / relative
        record = {
            "relative_path": relative,
            "source_sha256": "",
            "destination_sha256": "",
            "status": "PENDING",
            "error": "",
        }
        try:
            record["source_sha256"] = calculate_sha256(media.path)
            if not destination_path.exists():
                record["status"] = "MISSING"
                record["error"] = "Destination file is missing."
            else:
                record["destination_sha256"] = calculate_sha256(destination_path)
                record["status"] = "MATCH" if record["source_sha256"] == record["destination_sha256"] else "MISMATCH"
        except Exception as exc:  # noqa: BLE001
            record["status"] = "ERROR"
            record["error"] = str(exc)
        records.append(record)
    return {
        "generated_at": datetime.now().replace(microsecond=0).isoformat(),
        "source": str(src),
        "destination": str(dst),
        "total_files": len(records),
        "match": sum(1 for item in records if item["status"] == "MATCH"),
        "mismatch": sum(1 for item in records if item["status"] == "MISMATCH"),
        "missing": sum(1 for item in records if item["status"] == "MISSING"),
        "error": sum(1 for item in records if item["status"] == "ERROR"),
        "records": records,
    }


def write_compare_report(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "sha256_compare.json"
    csv_path = output / "sha256_compare.csv"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=COMPARE_FIELDS)
        writer.writeheader()
        for record in report["records"]:
            writer.writerow({field: record.get(field, "") for field in COMPARE_FIELDS})
    return json_path, csv_path
