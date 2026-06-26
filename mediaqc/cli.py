"""Command line interface for mediaqc."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import typer
from rich.live import Live
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .database import MediaDatabase, utc_now
from .deep_analysis import FFmpegNotFoundError, analyze_media
from .hash_check import calculate_sha256
from .live_event.canvas import check_media_canvas, load_canvas_spec, summarize_canvas, validate_canvas_spec
from .live_event.codec_profiles import analyze_codec_profile, summarize_codec_profiles
from .live_event.edid import check_output_spec, load_output_spec, summarize_output_spec
from .live_event.integrity import verify_manifest
from .live_event.manifest import build_manifest, write_manifest
from .probe import FFprobeNotFoundError, probe_media
from .processing.adobe_ame import (
    OFFICIAL_NOTCHLC_POLICY,
    detect_adobe_media_encoder,
    detect_notchlc_adobe_plugin_hint,
    prepare_ame_notchlc_jobs,
)
from .processing.ffmpeg_runner import (
    EncoderNotAvailableError,
    FFplayNotFoundError,
    build_doctor_report,
)
from .processing.ffplay import play_media
from .processing.jobs import ProcessingJob, run_jobs, write_job_report
from .processing.overlay import build_logo_command
from .processing.progress import make_processing_progress
from .processing.subtitles import build_subtitle_command, ensure_subtitle_filter_available
from .processing.transcode import build_transcode_jobs, collect_inputs
from .profiles import load_profile
from .report import build_report, build_summary, write_csv_report, write_html_report, write_json_report
from .rules import ProjectRules, evaluate_rules, load_rules
from .scanner import SUPPORTED_EXTENSIONS, scan_media_files

app = typer.Typer(help="Media QC Tool for show, LED, Millumin, Disguise, and TD workflows.")
tools_app = typer.Typer(help="Environment and diagnostic tools.")
notchlc_app = typer.Typer(help="Official NotchLC workflow helpers.")
app.add_typer(tools_app, name="tools")
app.add_typer(notchlc_app, name="notchlc")
console = Console()


@app.callback()
def main() -> None:
    """Media QC Tool."""


@tools_app.command("doctor")
def tools_doctor() -> None:
    """Check FFmpeg, FFprobe, FFplay, encoder, and filter availability."""

    report = build_doctor_report()
    table = Table(title="MediaQC Tools Doctor")
    table.add_column("Check")
    table.add_column("Value")
    values = report.to_dict()
    for key, value in values.items():
        if key == "errors":
            continue
        table.add_row(key, str(value))
    if report.errors:
        table.add_row("errors", "; ".join(report.errors), style="red")
    console.print(table)


@notchlc_app.command("prepare")
def notchlc_prepare(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        resolve_path=True,
        help="Input media file or folder for AME watch-folder preparation.",
    ),
    watch_folder: Path = typer.Option(
        ...,
        "--watch-folder",
        file_okay=False,
        dir_okay=True,
        help="Adobe Media Encoder watch folder to populate.",
    ),
    output: Path = typer.Option(
        ...,
        "--output",
        "-o",
        file_okay=False,
        dir_okay=True,
        help="Expected AME output folder for encoded NotchLC files.",
    ),
    recursive: bool = typer.Option(False, "--recursive", help="Prepare folder inputs recursively."),
    link: bool = typer.Option(False, "--link", help="Use symlinks instead of copying source files."),
    wait: bool = typer.Option(False, "--wait", help="Wait for output files, then build manifest and QC report."),
    timeout: int = typer.Option(0, "--timeout", min=0, help="Seconds to wait for output files. 0 waits until Ctrl+C."),
) -> None:
    """Prepare an official Adobe Media Encoder NotchLC watch-folder workflow."""

    ame_path = detect_adobe_media_encoder()
    plugin_hint = detect_notchlc_adobe_plugin_hint()
    if ame_path is None:
        console.print(
            "[yellow]Adobe Media Encoder was not detected.[/yellow] "
            "Install Adobe Media Encoder and the official NotchLC Adobe plugin, "
            "or use an official NotchLC SDK/tool backend."
        )
    console.print(f"[bold]Policy:[/bold] {OFFICIAL_NOTCHLC_POLICY}")
    payload = prepare_ame_notchlc_jobs(
        input_path=input_path,
        watch_folder=watch_folder,
        output_dir=output,
        recursive=recursive,
        link=link,
    )
    console.print(f"[green]AME jobs JSON:[/green] {Path(watch_folder) / 'ame_jobs.json'}")
    console.print(f"[green]AME jobs CSV:[/green] {Path(watch_folder) / 'ame_jobs.csv'}")
    console.print(f"[green]Instructions:[/green] {Path(watch_folder) / 'README_AME_NOTCHLC.txt'}")
    console.print(f"[green]Jobs prepared:[/green] {payload['total_jobs']}")
    console.print(f"[green]Adobe Media Encoder:[/green] {ame_path or 'NOT DETECTED'}")
    console.print(f"[green]NotchLC plugin hint:[/green] {plugin_hint}")
    if wait:
        _wait_for_notchlc_output(output, timeout)


@app.command()
def play(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Media file to preview.",
    ),
    loop: bool = typer.Option(False, "--loop", help="Loop playback."),
    mute: bool = typer.Option(False, "--mute", help="Disable audio playback."),
    start: str | None = typer.Option(None, "--start", help="Start time, e.g. 00:01:20."),
    scale: float | None = typer.Option(None, "--scale", min=0.05, help="Preview scale factor."),
    timecode: bool = typer.Option(False, "--timecode", help="Overlay timecode during preview."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print command without launching ffplay."),
) -> None:
    """Preview a media file with FFplay."""

    try:
        result = play_media(input_path, loop=loop, mute=mute, start=start, scale=scale, timecode=timecode, dry_run=dry_run)
    except FFplayNotFoundError as exc:
        console.print(f"[bold red]FFplay failed:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(" ".join(result.command))
    if result.returncode != 0:
        console.print(f"[bold red]FFplay exited with {result.returncode}[/bold red]")
        raise typer.Exit(code=result.returncode)


@app.command()
def gui() -> None:
    """Launch the PySide6 desktop GUI."""

    try:
        from .gui.app import launch_gui
        exit_code = launch_gui()
    except RuntimeError as exc:
        console.print(f"GUI failed: {exc}", markup=False)
        raise typer.Exit(code=1) from exc
    raise typer.Exit(code=exit_code)


@app.command()
def transcode(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        resolve_path=True,
        help="Input media file or folder.",
    ),
    preset: str = typer.Option(..., "--preset", "-p", help="Transcode preset name or YAML path."),
    output: Path = typer.Option(Path("./encoded"), "--output", "-o", file_okay=False, dir_okay=True, help="Output folder."),
    recursive: bool = typer.Option(False, "--recursive", help="Scan folders recursively."),
    preserve_structure: bool = typer.Option(True, "--preserve-structure/--flat", help="Preserve input folder structure."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing outputs."),
    skip_existing: bool = typer.Option(False, "--skip-existing", help="Skip outputs that already exist."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Build jobs and commands without executing."),
    workers: int = typer.Option(1, "--workers", min=1, help="Concurrent workers. Default 1 for show machines."),
) -> None:
    """Transcode one file or a batch using a YAML preset."""

    try:
        jobs = build_transcode_jobs(
            input_path=input_path,
            output_dir=output,
            preset_name=preset,
            recursive=recursive,
            preserve_structure=preserve_structure,
            overwrite=overwrite,
            skip_existing=skip_existing,
        )
    except (OSError, ValueError, EncoderNotAvailableError) as exc:
        console.print(f"[bold red]Transcode failed:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
    _run_processing_jobs(jobs, output, dry_run=dry_run, workers=workers)


@app.command()
def subtitle(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Input media file.",
    ),
    subtitle_path: Path = typer.Option(
        ...,
        "--subtitle",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Subtitle file (.srt, .ass, .vtt).",
    ),
    mode: str = typer.Option("soft", "--mode", help="Subtitle mode: soft or burn."),
    output: Path = typer.Option(..., "--output", "-o", file_okay=True, dir_okay=False, help="Output media file."),
    fonts_dir: Path | None = typer.Option(None, "--fonts-dir", file_okay=False, dir_okay=True, help="Fonts directory for burn mode."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing output."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Build command without executing."),
) -> None:
    """Embed or burn subtitles into a media file."""

    try:
        if mode == "burn":
            ensure_subtitle_filter_available()
        command = build_subtitle_command(input_path, subtitle_path, output, mode, fonts_dir=fonts_dir, overwrite=overwrite)
    except (ValueError, EncoderNotAvailableError) as exc:
        console.print(f"[bold red]Subtitle failed:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
    job = ProcessingJob(input_path=input_path, output_path=output, preset=f"subtitle_{mode}", command=command, log_path=output.with_suffix(output.suffix + ".log"))
    _run_processing_jobs([job], output.parent, dry_run=dry_run, workers=1)


@app.command()
def logo(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        resolve_path=True,
        help="Input media file or folder.",
    ),
    logo_path: Path = typer.Option(
        ...,
        "--logo",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Logo image, usually PNG with alpha.",
    ),
    output: Path = typer.Option(..., "--output", "-o", help="Output file for single input or output folder for batch."),
    position: str = typer.Option("top-right", "--position", help="top-left, top-right, bottom-left, bottom-right, center."),
    x: int | None = typer.Option(None, "--x", help="Custom overlay x coordinate."),
    y: int | None = typer.Option(None, "--y", help="Custom overlay y coordinate."),
    opacity: float = typer.Option(1.0, "--opacity", min=0.0, max=1.0, help="Logo opacity."),
    start: float | None = typer.Option(None, "--start", help="Overlay start time in seconds."),
    end: float | None = typer.Option(None, "--end", help="Overlay end time in seconds."),
    logo_scale: float | None = typer.Option(None, "--logo-scale", min=0.01, help="Scale logo by factor."),
    preset: str = typer.Option("h264_preview", "--preset", help="Output transcode preset."),
    recursive: bool = typer.Option(False, "--recursive", help="Batch process folder recursively."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing outputs."),
    skip_existing: bool = typer.Option(False, "--skip-existing", help="Skip existing outputs."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Build jobs and commands without executing."),
    workers: int = typer.Option(1, "--workers", min=1, help="Concurrent workers."),
) -> None:
    """Overlay a logo on one file or a batch."""

    try:
        inputs = collect_inputs(input_path, recursive=recursive)
        jobs = []
        for source in inputs:
            if Path(input_path).is_dir():
                output_path = output / f"{source.stem}_logo.mp4"
            else:
                output_path = output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            command = build_logo_command(
                source,
                logo_path,
                output_path,
                position=position,
                x=x,
                y=y,
                opacity=opacity,
                start=start,
                end=end,
                logo_scale=logo_scale,
                preset_name=preset,
                overwrite=overwrite,
            )
            jobs.append(
                ProcessingJob(
                    input_path=source,
                    output_path=output_path,
                    preset=f"logo_{preset}",
                    command=command,
                    log_path=output_path.with_suffix(output_path.suffix + ".log"),
                    skip_existing=skip_existing,
                )
            )
    except (OSError, ValueError, EncoderNotAvailableError) as exc:
        console.print(f"[bold red]Logo failed:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
    _run_processing_jobs(jobs, output if Path(input_path).is_dir() else output.parent, dry_run=dry_run, workers=workers)


@app.command()
def scan(
    project_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Folder containing media assets.",
    ),
    output: Path = typer.Option(
        Path("./reports"),
        "--output",
        "-o",
        file_okay=False,
        dir_okay=True,
        help="Output folder for JSON and CSV reports.",
    ),
    database: Path | None = typer.Option(
        None,
        "--database",
        help="SQLite database path. Defaults to <output>/media.db.",
    ),
    rules: Path | None = typer.Option(
        None,
        "--rules",
        "-r",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="YAML project rules file.",
    ),
    profile: str | None = typer.Option(
        None,
        "--profile",
        help="Built-in project profile, e.g. disguise, millumin, pixera, touchdesigner.",
    ),
    html: bool = typer.Option(
        False,
        "--html",
        help="Generate media_qc_report.html.",
    ),
    deep: bool = typer.Option(
        False,
        "--deep",
        help="Run FFmpeg deep decode analysis for video files.",
    ),
    output_spec: Path | None = typer.Option(
        None,
        "--output-spec",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="YAML live event output specification.",
    ),
    canvas_spec: Path | None = typer.Option(
        None,
        "--canvas-spec",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="YAML multi-screen canvas specification.",
    ),
    manifest: bool = typer.Option(
        False,
        "--manifest",
        help="Generate manifest.json and manifest.csv with the scan.",
    ),
) -> None:
    """Scan media files and generate JSON/CSV QC reports."""

    project_rules, active_rules_path = _load_rule_source(rules, profile)
    files, json_path, csv_path, html_path, db_path = _run_scan(
        project_path=project_path,
        output=output,
        database=database,
        project_rules=project_rules,
        active_rules_path=active_rules_path,
        html=html,
        deep=deep,
        output_spec_path=output_spec,
        canvas_spec_path=canvas_spec,
        write_manifest_files=manifest,
        show_progress=True,
    )

    _print_summary(files, json_path, csv_path, html_path, db_path)


@app.command()
def watch(
    project_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Folder containing media assets.",
    ),
    output: Path = typer.Option(
        Path("./reports"),
        "--output",
        "-o",
        file_okay=False,
        dir_okay=True,
        help="Output folder for JSON/CSV/HTML reports.",
    ),
    database: Path | None = typer.Option(
        None,
        "--database",
        help="SQLite database path. Defaults to <output>/media.db.",
    ),
    rules: Path | None = typer.Option(
        None,
        "--rules",
        "-r",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="YAML project rules file.",
    ),
    profile: str | None = typer.Option(
        None,
        "--profile",
        help="Built-in project profile, e.g. disguise, millumin, pixera, touchdesigner.",
    ),
    deep: bool = typer.Option(
        False,
        "--deep",
        help="Run FFmpeg deep decode analysis for video files.",
    ),
    debounce: float = typer.Option(
        1.5,
        "--debounce",
        min=0.2,
        help="Seconds to wait after file events before refreshing reports.",
    ),
) -> None:
    """Watch a folder and refresh database/HTML reports on media changes."""

    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError as exc:
        console.print("[bold red]Watch failed:[/bold red] watchdog is not installed.")
        console.print("Run: python -m pip install -r requirements.txt")
        raise typer.Exit(code=1) from exc

    project_rules, active_rules_path = _load_rule_source(rules, profile)
    stop_event = threading.Event()
    refresh_event = threading.Event()
    lock = threading.Lock()
    state = {
        "last_event": "Initial scan",
        "last_scan": "-",
        "total": 0,
        "db": str(database or (output / "media.db")),
    }

    class MediaEventHandler(FileSystemEventHandler):
        def on_any_event(self, event):  # noqa: ANN001
            if event.is_directory:
                return
            paths = [Path(event.src_path)]
            if getattr(event, "dest_path", ""):
                paths.append(Path(event.dest_path))
            if not any(_is_supported_path(path) for path in paths):
                return
            with lock:
                state["last_event"] = f"{event.event_type}: {paths[-1]}"
            console.print(f"[cyan]watch[/cyan] {event.event_type}: {paths[-1]}")
            refresh_event.set()

    def refresh(reason: str) -> None:
        console.print(f"[cyan]watch[/cyan] refreshing reports ({reason})")
        files, _, _, html_path, db_path = _run_scan(
            project_path=project_path,
            output=output,
            database=database,
            project_rules=project_rules,
            active_rules_path=active_rules_path,
            html=True,
            deep=deep,
            output_spec_path=None,
            canvas_spec_path=None,
            write_manifest_files=False,
            show_progress=False,
        )
        with lock:
            state["last_scan"] = utc_now()
            state["total"] = len(files)
            state["db"] = str(db_path)
        console.print(f"[green]watch[/green] updated HTML: {html_path}")

    refresh("startup")
    observer = Observer()
    observer.schedule(MediaEventHandler(), str(project_path), recursive=True)
    observer.start()

    console.print("[green]watch[/green] running. Press Ctrl+C to stop.")
    try:
        with Live(_watch_table(state, lock), console=console, refresh_per_second=2) as live:
            while not stop_event.is_set():
                if refresh_event.wait(0.25):
                    refresh_event.clear()
                    time.sleep(debounce)
                    while refresh_event.is_set():
                        refresh_event.clear()
                        time.sleep(debounce)
                    refresh("file change")
                live.update(_watch_table(state, lock))
    except KeyboardInterrupt:
        console.print("\n[yellow]watch[/yellow] stopping...")
    finally:
        stop_event.set()
        observer.stop()
        observer.join(timeout=5)
        console.print("[green]watch[/green] stopped safely.")


@app.command("db")
def db_info(
    database: Path = typer.Option(
        Path("./reports/media.db"),
        "--database",
        "-d",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="SQLite database path.",
    ),
) -> None:
    """Show SQLite database table counts."""

    with MediaDatabase(database) as db:
        counts = db.database_counts()

    table = Table(title=f"Media QC Database: {database}")
    table.add_column("Table")
    table.add_column("Rows", justify="right")
    for name, count in counts.items():
        table.add_row(name, str(count))
    console.print(table)


@app.command()
def history(
    database: Path = typer.Option(
        Path("./reports/media.db"),
        "--database",
        "-d",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="SQLite database path.",
    ),
    limit: int = typer.Option(20, "--limit", "-n", min=1, help="Maximum rows to show."),
) -> None:
    """Show scan history."""

    with MediaDatabase(database) as db:
        rows = db.history(limit)

    table = Table(title="Scan History")
    table.add_column("Started")
    table.add_column("Project")
    table.add_column("Files", justify="right")
    table.add_column("PASS", justify="right", style="green")
    table.add_column("WARN", justify="right", style="yellow")
    table.add_column("FAIL", justify="right", style="red")
    table.add_column("Deep")
    for row in rows:
        table.add_row(
            row["scan_started"],
            row["project_name"] or row["project_path"],
            str(row["total_files"]),
            str(row["pass_count"]),
            str(row["warn_count"]),
            str(row["fail_count"]),
            "yes" if row["deep"] else "no",
        )
    console.print(table)


@app.command()
def duplicates(
    database: Path = typer.Option(
        Path("./reports/media.db"),
        "--database",
        "-d",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="SQLite database path.",
    ),
) -> None:
    """Search duplicate media by SHA256."""

    with MediaDatabase(database) as db:
        rows = db.duplicates()

    table = Table(title="Duplicate Media")
    table.add_column("SHA256")
    table.add_column("Files", justify="right")
    table.add_column("Total Size", justify="right")
    table.add_column("Paths")
    for row in rows:
        table.add_row(
            row["sha256"],
            str(row["file_count"]),
            str(row["total_size"]),
            row["paths"],
        )
    console.print(table)


@app.command()
def manifest(
    project_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Folder containing media assets.",
    ),
    output: Path = typer.Option(
        Path("./reports"),
        "--output",
        "-o",
        file_okay=False,
        dir_okay=True,
        help="Output folder for manifest.json and manifest.csv.",
    ),
    project_name: str | None = typer.Option(None, "--project-name", help="Manifest project name."),
) -> None:
    """Generate manifest.json and manifest.csv."""

    data = build_manifest(project_path, project_name=project_name)
    json_path, csv_path = write_manifest(data, output)
    console.print(f"[green]Manifest JSON:[/green] {json_path}")
    console.print(f"[green]Manifest CSV:[/green] {csv_path}")


@app.command()
def verify(
    project_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Folder containing media assets.",
    ),
    manifest_path: Path = typer.Option(
        ...,
        "--manifest",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Manifest JSON path.",
    ),
) -> None:
    """Verify a media folder against a manifest.json."""

    report = verify_manifest(project_path, manifest_path)
    table = Table(title=f"Integrity Check: {report.status}")
    table.add_column("Category")
    table.add_column("Count", justify="right")
    table.add_row("Missing", str(len(report.missing_files)))
    table.add_row("Modified", str(len(report.modified_files)))
    table.add_row("New", str(len(report.new_files)))
    table.add_row("Duplicates", str(len(report.duplicate_files)))
    table.add_row("Empty", str(len(report.empty_files)))
    table.add_row("Naming WARN", str(len(report.naming_warnings)))
    table.add_row("Offline refs", str(len(report.offline_references)))
    console.print(table)
    raise typer.Exit(code=1 if report.status == "FAIL" else 0)


@app.command()
def dashboard(
    database: Path = typer.Option(
        Path("./reports/media.db"),
        "--database",
        "-d",
        file_okay=True,
        dir_okay=False,
        help="SQLite database path.",
    ),
    host: str = typer.Option("127.0.0.1", "--host", help="Dashboard host."),
    port: int = typer.Option(8000, "--port", help="Dashboard port."),
    reload: bool = typer.Option(False, "--reload", help="Enable uvicorn auto reload."),
) -> None:
    """Run the FastAPI dashboard."""

    try:
        import uvicorn
        from .dashboard import create_app
    except ImportError as exc:
        console.print("[bold red]Dashboard failed:[/bold red] FastAPI/uvicorn is not installed.")
        console.print("Run: python -m pip install -r requirements.txt")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Dashboard:[/green] http://{host}:{port}")
    console.print(f"[green]Database:[/green] {database}")
    uvicorn.run(
        create_app(database),
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


def _print_summary(
    files: list[object],
    json_path: Path,
    csv_path: Path,
    html_path: Path | None = None,
    db_path: Path | None = None,
) -> None:
    summary = build_summary(files)

    table = Table(title="Media QC Summary")
    table.add_column("Total", justify="right")
    table.add_column("PASS", justify="right", style="green")
    table.add_column("FAIL", justify="right", style="red")
    table.add_column("Rule PASS", justify="right", style="green")
    table.add_column("Rule WARN", justify="right", style="yellow")
    table.add_column("Rule FAIL", justify="right", style="red")
    table.add_row(
        str(summary["total"]),
        str(summary["status_pass"]),
        str(summary["status_fail"]),
        str(summary["rule_pass"]),
        str(summary["rule_warn"]),
        str(summary["rule_fail"]),
    )
    console.print(table)
    console.print(f"[green]JSON:[/green] {json_path}")
    console.print(f"[green]CSV:[/green] {csv_path}")
    if html_path is not None:
        console.print(f"[green]HTML:[/green] {html_path}")
    if db_path is not None:
        console.print(f"[green]DB:[/green] {db_path}")


def _load_rule_source(
    rules: Path | None,
    profile: str | None,
) -> tuple[ProjectRules | None, Path | None]:
    project_rules: ProjectRules | None = None
    active_rules_path: Path | None = None
    if rules is not None and profile is not None:
        console.print("[bold red]Rules failed:[/bold red] Use either --rules or --profile, not both.")
        raise typer.Exit(code=1)
    if profile is not None:
        try:
            project_rules, active_rules_path = load_profile(profile)
        except (OSError, ValueError) as exc:
            console.print(f"[bold red]Profile failed:[/bold red] {exc}")
            raise typer.Exit(code=1) from exc
    if rules is not None:
        try:
            project_rules = load_rules(rules)
            active_rules_path = rules
        except (OSError, ValueError) as exc:
            console.print(f"[bold red]Rules failed:[/bold red] {exc}")
            raise typer.Exit(code=1) from exc
    return project_rules, active_rules_path


def _run_scan(
    project_path: Path,
    output: Path,
    database: Path | None,
    project_rules: ProjectRules | None,
    active_rules_path: Path | None,
    html: bool,
    deep: bool,
    output_spec_path: Path | None,
    canvas_spec_path: Path | None,
    write_manifest_files: bool,
    show_progress: bool,
) -> tuple[list[object], Path, Path, Path | None, Path]:
    scan_started = utc_now()
    output_spec = load_output_spec(output_spec_path) if output_spec_path else None
    canvas_spec = load_canvas_spec(canvas_spec_path) if canvas_spec_path else None
    canvas_layout_report = validate_canvas_spec(canvas_spec) if canvas_spec else None

    try:
        files = scan_media_files(project_path)
    except (FileNotFoundError, NotADirectoryError, PermissionError) as exc:
        console.print(f"[bold red]Scan failed:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    if show_progress:
        console.print(f"[bold]Project:[/bold] {project_path}")
        if project_rules and project_rules.project_name:
            console.print(f"[bold]Rules project:[/bold] {project_rules.project_name}")
        if project_rules and project_rules.profile_name:
            console.print(f"[bold]Profile:[/bold] {project_rules.profile_name}")
        console.print(f"[bold]Supported media files:[/bold] {len(files)}")

    db_path = database or (output / "media.db")
    db = MediaDatabase(db_path)
    project_id = db.get_or_create_project(
        project_path,
        project_rules.project_name if project_rules else None,
    )

    try:
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("Checking media...", total=None)
                for item in files:
                    progress.update(task, description=f"Checking {item.filename}")
                    _check_file(item, db, project_id, project_rules, deep, output_spec, canvas_spec)
        else:
            for item in files:
                _check_file(item, db, project_id, project_rules, deep, output_spec, canvas_spec)

        removed = db.prune_missing_media(project_id, {item.path for item in files})
        if removed and show_progress:
            console.print(f"[yellow]DB:[/yellow] removed {removed} missing file(s)")

        summary = build_summary(files)
        history_pass = summary["rule_pass"] if project_rules is not None else summary["status_pass"]
        history_warn = summary["rule_warn"] if project_rules is not None else 0
        history_fail = summary["rule_fail"] if project_rules is not None else summary["status_fail"]
        db.record_history(
            project_id=project_id,
            project_path=project_path,
            project_name=project_rules.project_name if project_rules else None,
            total_files=summary["total"],
            pass_count=history_pass,
            warn_count=history_warn,
            fail_count=history_fail,
            rules_path=active_rules_path,
            deep=deep,
            html=html,
            scan_started=scan_started,
        )
    finally:
        db.close()

    manifest_data = build_manifest(
        project_path,
        project_name=project_rules.project_name if project_rules else None,
        files=files,
    ) if write_manifest_files else None
    if manifest_data:
        write_manifest(manifest_data, output)

    live_event = _live_event_summary(output_spec, canvas_spec, canvas_layout_report, files, manifest_data)
    report = build_report(
        project_path,
        files,
        rules_path=active_rules_path,
        project_name=project_rules.project_name if project_rules else None,
        profile_name=project_rules.profile_name if project_rules else None,
        live_event=live_event,
    )
    json_path = write_json_report(report, output)
    csv_path = write_csv_report(files, output)
    html_path = write_html_report(report, output) if html else None
    return files, json_path, csv_path, html_path, db_path


def _check_file(
    item: object,
    db: MediaDatabase,
    project_id: int,
    project_rules: ProjectRules | None,
    deep: bool,
    output_spec: dict | None,
    canvas_spec: dict | None,
) -> None:
    try:
        item.sha256, item.hash_cached = db.get_or_calculate_sha256(
            item.path,
            calculate_sha256,
        )
    except OSError as exc:
        item.fail(f"SHA256 failed: {exc}")

    try:
        item.ffprobe = probe_media(item.path)
    except FFprobeNotFoundError as exc:
        item.fail(str(exc))
    except Exception as exc:  # noqa: BLE001 - each file must record errors and continue.
        item.fail(str(exc))

    if deep:
        try:
            item.decode_report = analyze_media(item.path, item.ffprobe)
        except FFmpegNotFoundError as exc:
            item.fail(str(exc))
        except Exception as exc:  # noqa: BLE001 - deep analysis should not stop the scan.
            item.fail(f"Deep analysis failed: {exc}")

    if project_rules is not None:
        evaluate_rules(item, project_rules)

    try:
        item.codec_profile = analyze_codec_profile(item)
        if output_spec is not None:
            item.output_match = check_output_spec(item, output_spec)
        if canvas_spec is not None:
            item.canvas_match = check_media_canvas(item, canvas_spec)
        item.manifest_status = "READY"
    except Exception as exc:  # noqa: BLE001
        item.warnings.append(f"Live event checks failed: {exc}")

    db.record_media(project_id, item)


def _live_event_summary(
    output_spec: dict | None,
    canvas_spec: dict | None,
    canvas_layout_report: object | None,
    files: list[object],
    manifest_data: dict | None,
) -> dict[str, object]:
    output_checks = [item.output_match for item in files if item.output_match is not None]
    canvas_checks = [item.canvas_match for item in files if item.canvas_match is not None]
    codec_profiles = [item.codec_profile for item in files if item.codec_profile is not None]
    summary: dict[str, object] = {
        "codec_profiles": summarize_codec_profiles(codec_profiles),
    }
    output_summary = summarize_output_spec(output_spec, output_checks)
    if output_summary:
        summary["output_spec"] = output_summary
    canvas_summary = summarize_canvas(canvas_spec, canvas_layout_report, canvas_checks)
    if canvas_summary:
        summary["canvas"] = canvas_summary
    if manifest_data:
        summary["manifest"] = {
            "media_count": manifest_data["media_count"],
            "generated_at": manifest_data["generated_at"],
        }
    return summary


def _watch_table(state: dict[str, object], lock: threading.Lock) -> Table:
    with lock:
        last_event = str(state["last_event"])
        last_scan = str(state["last_scan"])
        total = str(state["total"])
        db_path = str(state["db"])
    table = Table(title="MediaQC Watch")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Last Event", last_event)
    table.add_row("Last Scan", last_scan)
    table.add_row("Files", total)
    table.add_row("Database", db_path)
    return table


def _run_processing_jobs(
    jobs: list[ProcessingJob],
    output_dir: Path,
    dry_run: bool,
    workers: int,
) -> None:
    if not jobs:
        console.print("[yellow]Processing:[/yellow] no supported input files found.")
        return
    completed: list[ProcessingJob] = []
    with make_processing_progress(console) as progress:
        task = progress.add_task("Processing jobs...", total=len(jobs))

        def on_update(job: ProcessingJob) -> None:
            completed.append(job)
            progress.update(task, advance=1, description=f"{job.status}: {job.output_path.name}")

        run_jobs(jobs, dry_run=dry_run, workers=workers, on_update=on_update)
    json_path, csv_path = write_job_report(jobs, output_dir)
    table = Table(title="Processing Summary")
    table.add_column("Total", justify="right")
    table.add_column("SUCCESS", justify="right", style="green")
    table.add_column("FAILED", justify="right", style="red")
    table.add_column("SKIPPED", justify="right", style="yellow")
    table.add_row(
        str(len(jobs)),
        str(sum(1 for job in jobs if job.status == "SUCCESS")),
        str(sum(1 for job in jobs if job.status == "FAILED")),
        str(sum(1 for job in jobs if job.status == "SKIPPED")),
    )
    console.print(table)
    console.print(f"[green]Job JSON:[/green] {json_path}")
    console.print(f"[green]Job CSV:[/green] {csv_path}")
    failed = [job for job in jobs if job.status == "FAILED"]
    if failed:
        for job in failed[:5]:
            console.print(f"[red]FAILED[/red] {job.input_path}: {job.error}")
        raise typer.Exit(code=1)


def _wait_for_notchlc_output(output: Path, timeout: int) -> None:
    output_path = Path(output)
    console.print(f"[cyan]notchlc[/cyan] waiting for encoded files in {output_path}")
    started = time.monotonic()
    try:
        while True:
            files = scan_media_files(output_path) if output_path.exists() else []
            if files:
                console.print(f"[green]notchlc[/green] detected {len(files)} output file(s). Running QC and manifest.")
                reports = output_path / "mediaqc_reports"
                scan_files, json_path, csv_path, html_path, _ = _run_scan(
                    project_path=output_path,
                    output=reports,
                    database=reports / "media.db",
                    project_rules=None,
                    active_rules_path=None,
                    html=True,
                    deep=False,
                    output_spec_path=None,
                    canvas_spec_path=None,
                    write_manifest_files=True,
                    show_progress=True,
                )
                console.print(f"[green]Output files checked:[/green] {len(scan_files)}")
                console.print(f"[green]JSON:[/green] {json_path}")
                console.print(f"[green]CSV:[/green] {csv_path}")
                console.print(f"[green]HTML:[/green] {html_path}")
                return
            if timeout and time.monotonic() - started >= timeout:
                console.print("[yellow]notchlc[/yellow] wait timed out before encoded files appeared.")
                return
            time.sleep(2)
    except KeyboardInterrupt:
        console.print("\n[yellow]notchlc[/yellow] wait cancelled.")


def _is_supported_path(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


if __name__ == "__main__":
    app()
