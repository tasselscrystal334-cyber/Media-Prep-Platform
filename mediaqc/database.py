"""SQLite persistence and hash cache."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class MediaDatabase:
    """Small SQLite database for scans, history, and hash caching."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.init_schema()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "MediaDatabase":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def init_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS Project (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                path TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                last_scan TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Hash (
                sha256 TEXT PRIMARY KEY,
                size_bytes INTEGER NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                media_count INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS Media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                path TEXT NOT NULL UNIQUE,
                filename TEXT NOT NULL,
                extension TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                sha256 TEXT,
                status TEXT NOT NULL,
                rule_status TEXT NOT NULL,
                video_codec TEXT,
                width INTEGER,
                height INTEGER,
                fps TEXT,
                error_count INTEGER NOT NULL DEFAULT 0,
                first_seen TEXT NOT NULL,
                last_scan TEXT NOT NULL,
                last_modified TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES Project(id),
                FOREIGN KEY(sha256) REFERENCES Hash(sha256)
            );

            CREATE TABLE IF NOT EXISTS History (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                project_path TEXT NOT NULL,
                project_name TEXT,
                scan_started TEXT NOT NULL,
                scan_finished TEXT NOT NULL,
                total_files INTEGER NOT NULL,
                pass_count INTEGER NOT NULL,
                warn_count INTEGER NOT NULL,
                fail_count INTEGER NOT NULL,
                rules_path TEXT,
                deep INTEGER NOT NULL,
                html INTEGER NOT NULL,
                FOREIGN KEY(project_id) REFERENCES Project(id)
            );

            CREATE TABLE IF NOT EXISTS HashCache (
                path TEXT PRIMARY KEY,
                size_bytes INTEGER NOT NULL,
                mtime_ns INTEGER NOT NULL,
                sha256 TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_scan TEXT NOT NULL,
                last_modified TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_media_sha256 ON Media(sha256);
            CREATE INDEX IF NOT EXISTS idx_hashcache_sha256 ON HashCache(sha256);
            CREATE INDEX IF NOT EXISTS idx_history_scan_started ON History(scan_started);
            """
        )
        self._ensure_media_columns()
        self.connection.commit()

    def _ensure_media_columns(self) -> None:
        existing = {
            row["name"]
            for row in self.connection.execute("PRAGMA table_info(Media)").fetchall()
        }
        columns = {
            "video_codec": "TEXT",
            "width": "INTEGER",
            "height": "INTEGER",
            "fps": "TEXT",
            "error_count": "INTEGER NOT NULL DEFAULT 0",
        }
        for name, definition in columns.items():
            if name not in existing:
                self.connection.execute(f"ALTER TABLE Media ADD COLUMN {name} {definition}")

    def get_or_create_project(self, project_path: Path, name: str | None = None) -> int:
        now = utc_now()
        path_text = str(Path(project_path).resolve())
        row = self.connection.execute(
            "SELECT id FROM Project WHERE path = ?",
            (path_text,),
        ).fetchone()
        if row:
            self.connection.execute(
                "UPDATE Project SET name = COALESCE(?, name), last_scan = ? WHERE id = ?",
                (name, now, row["id"]),
            )
            self.connection.commit()
            return int(row["id"])

        cursor = self.connection.execute(
            "INSERT INTO Project (name, path, created_at, last_scan) VALUES (?, ?, ?, ?)",
            (name, path_text, now, now),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get_cached_sha256(self, path: Path) -> str | None:
        stat = Path(path).stat()
        row = self.connection.execute(
            """
            SELECT sha256
            FROM HashCache
            WHERE path = ? AND size_bytes = ? AND mtime_ns = ?
            """,
            (str(Path(path).resolve()), stat.st_size, stat.st_mtime_ns),
        ).fetchone()
        return str(row["sha256"]) if row else None

    def get_or_calculate_sha256(
        self,
        path: Path,
        calculate: Callable[[Path], str],
    ) -> tuple[str, bool]:
        cached = self.get_cached_sha256(path)
        if cached is not None:
            self.touch_hash_cache(path, cached)
            return cached, True

        sha256 = calculate(path)
        self.upsert_hash_cache(path, sha256)
        return sha256, False

    def touch_hash_cache(self, path: Path, sha256: str) -> None:
        now = utc_now()
        stat = Path(path).stat()
        self.connection.execute(
            """
            UPDATE HashCache
            SET last_scan = ?, last_modified = ?, size_bytes = ?, mtime_ns = ?, sha256 = ?
            WHERE path = ?
            """,
            (
                now,
                _mtime_iso(stat),
                stat.st_size,
                stat.st_mtime_ns,
                sha256,
                str(Path(path).resolve()),
            ),
        )
        self.connection.commit()

    def upsert_hash_cache(self, path: Path, sha256: str) -> None:
        now = utc_now()
        stat = Path(path).stat()
        path_text = str(Path(path).resolve())
        existing = self.connection.execute(
            "SELECT first_seen FROM HashCache WHERE path = ?",
            (path_text,),
        ).fetchone()
        first_seen = existing["first_seen"] if existing else now
        self.connection.execute(
            """
            INSERT OR REPLACE INTO HashCache (
                path, size_bytes, mtime_ns, sha256, first_seen, last_scan, last_modified
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (path_text, stat.st_size, stat.st_mtime_ns, sha256, first_seen, now, _mtime_iso(stat)),
        )
        self.connection.commit()

    def record_media(self, project_id: int, media: Any) -> None:
        now = utc_now()
        path_text = str(Path(media.path).resolve())
        existing = self.connection.execute(
            "SELECT first_seen FROM Media WHERE path = ?",
            (path_text,),
        ).fetchone()
        first_seen = existing["first_seen"] if existing else now
        stat = Path(media.path).stat()

        self.connection.execute(
            """
            INSERT OR REPLACE INTO Media (
                project_id, path, filename, extension, size_bytes, sha256,
                status, rule_status, video_codec, width, height, fps, error_count,
                first_seen, last_scan, last_modified
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                path_text,
                media.filename,
                media.extension,
                media.size_bytes,
                media.sha256,
                media.status,
                media.rule_status,
                _video_value(media, "codec_name"),
                _video_value(media, "width"),
                _video_value(media, "height"),
                _video_value(media, "avg_frame_rate"),
                len(getattr(media, "errors", [])) + len(getattr(media, "failures", [])),
                first_seen,
                now,
                _mtime_iso(stat),
            ),
        )
        if media.sha256:
            self._upsert_hash(media.sha256, media.size_bytes)
        self.connection.commit()

    def prune_missing_media(self, project_id: int, existing_paths: set[Path]) -> int:
        """Remove database rows for watched files that no longer exist."""

        existing_text = {str(path.resolve()) for path in existing_paths}
        rows = self.connection.execute(
            "SELECT path, sha256 FROM Media WHERE project_id = ?",
            (project_id,),
        ).fetchall()
        removed = 0
        affected_hashes: set[str] = set()
        for row in rows:
            path_text = row["path"]
            if path_text in existing_text:
                continue
            removed += 1
            if row["sha256"]:
                affected_hashes.add(row["sha256"])
            self.connection.execute("DELETE FROM Media WHERE path = ?", (path_text,))
            self.connection.execute("DELETE FROM HashCache WHERE path = ?", (path_text,))

        for sha256 in affected_hashes:
            self._refresh_hash_count(sha256)
        self.connection.commit()
        return removed

    def record_history(
        self,
        project_id: int,
        project_path: Path,
        project_name: str | None,
        total_files: int,
        pass_count: int,
        warn_count: int,
        fail_count: int,
        rules_path: Path | None,
        deep: bool,
        html: bool,
        scan_started: str,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO History (
                project_id, project_path, project_name, scan_started, scan_finished,
                total_files, pass_count, warn_count, fail_count, rules_path, deep, html
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                str(Path(project_path).resolve()),
                project_name,
                scan_started,
                utc_now(),
                total_files,
                pass_count,
                warn_count,
                fail_count,
                str(Path(rules_path).resolve()) if rules_path else None,
                int(deep),
                int(html),
            ),
        )
        self.connection.commit()

    def database_counts(self) -> dict[str, int]:
        return {
            table: int(
                self.connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"]
            )
            for table in ("Project", "Media", "Hash", "History", "HashCache")
        }

    def history(self, limit: int = 20) -> list[sqlite3.Row]:
        return list(
            self.connection.execute(
                """
                SELECT *
                FROM History
                ORDER BY scan_started DESC
                LIMIT ?
                """,
                (limit,),
            )
        )

    def duplicates(self) -> list[sqlite3.Row]:
        return list(
            self.connection.execute(
                """
                SELECT
                    sha256,
                    COUNT(*) AS file_count,
                    SUM(size_bytes) AS total_size,
                    GROUP_CONCAT(path, char(10)) AS paths
                FROM Media
                WHERE sha256 IS NOT NULL AND sha256 != ''
                GROUP BY sha256
                HAVING COUNT(*) > 1
                ORDER BY file_count DESC, total_size DESC
                """
            )
        )

    def projects(self) -> list[sqlite3.Row]:
        return list(
            self.connection.execute(
                """
                SELECT
                    Project.*,
                    COUNT(Media.id) AS media_count
                FROM Project
                LEFT JOIN Media ON Media.project_id = Project.id
                GROUP BY Project.id
                ORDER BY Project.last_scan DESC
                """
            )
        )

    def media_files(self, search: str | None = None, limit: int = 200) -> list[sqlite3.Row]:
        if search:
            pattern = f"%{search}%"
            return list(
                self.connection.execute(
                    """
                    SELECT Media.*, Project.name AS project_name
                    FROM Media
                    LEFT JOIN Project ON Project.id = Media.project_id
                    WHERE Media.filename LIKE ? OR Media.path LIKE ? OR Media.sha256 LIKE ?
                    ORDER BY Media.last_scan DESC
                    LIMIT ?
                    """,
                    (pattern, pattern, pattern, limit),
                )
            )
        return list(
            self.connection.execute(
                """
                SELECT Media.*, Project.name AS project_name
                FROM Media
                LEFT JOIN Project ON Project.id = Media.project_id
                ORDER BY Media.last_scan DESC
                LIMIT ?
                """,
                (limit,),
            )
        )

    def overview(self) -> dict[str, Any]:
        counts = self.database_counts()
        status_counts = self._counts_by("Media", "rule_status")
        return {
            "counts": counts,
            "status": status_counts,
            "duplicates": len(self.duplicates()),
            "recent_history": [dict(row) for row in self.history(5)],
        }

    def statistics(self) -> dict[str, Any]:
        return {
            "codec": self._counts_by("Media", "video_codec"),
            "resolution": self._resolution_counts(),
            "fps": self._counts_by("Media", "fps"),
            "errors": self._error_counts(),
            "recent_scan": [dict(row) for row in self.history(10)],
            "duplicates": [dict(row) for row in self.duplicates()],
        }

    def _counts_by(self, table: str, column: str) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            f"""
            SELECT COALESCE(NULLIF({column}, ''), 'Unknown') AS label, COUNT(*) AS count
            FROM {table}
            GROUP BY label
            ORDER BY count DESC, label ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def _resolution_counts(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT
                CASE
                    WHEN width IS NULL OR height IS NULL THEN 'Unknown'
                    ELSE width || 'x' || height
                END AS label,
                COUNT(*) AS count
            FROM Media
            GROUP BY label
            ORDER BY count DESC, label ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def _error_counts(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT
                CASE
                    WHEN error_count = 0 THEN 'No Errors'
                    ELSE 'Has Errors'
                END AS label,
                COUNT(*) AS count
            FROM Media
            GROUP BY label
            ORDER BY count DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def _upsert_hash(self, sha256: str, size_bytes: int) -> None:
        now = utc_now()
        row = self.connection.execute(
            "SELECT first_seen FROM Hash WHERE sha256 = ?",
            (sha256,),
        ).fetchone()
        first_seen = row["first_seen"] if row else now
        media_count = self.connection.execute(
            "SELECT COUNT(*) AS count FROM Media WHERE sha256 = ?",
            (sha256,),
        ).fetchone()["count"]
        self.connection.execute(
            """
            INSERT OR REPLACE INTO Hash (sha256, size_bytes, first_seen, last_seen, media_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (sha256, size_bytes, first_seen, now, media_count),
        )

    def _refresh_hash_count(self, sha256: str) -> None:
        row = self.connection.execute(
            "SELECT COUNT(*) AS count FROM Media WHERE sha256 = ?",
            (sha256,),
        ).fetchone()
        media_count = int(row["count"])
        if media_count == 0:
            self.connection.execute("DELETE FROM Hash WHERE sha256 = ?", (sha256,))
            return
        self.connection.execute(
            "UPDATE Hash SET media_count = ?, last_seen = ? WHERE sha256 = ?",
            (media_count, utc_now(), sha256),
        )


def _mtime_iso(stat_result: Any) -> str:
    return datetime.fromtimestamp(stat_result.st_mtime).replace(microsecond=0).isoformat()


def _video_value(media: Any, key: str) -> Any:
    ffprobe = getattr(media, "ffprobe", None) or {}
    for stream in ffprobe.get("streams", []):
        if stream.get("codec_type") == "video":
            return stream.get(key)
    return None
