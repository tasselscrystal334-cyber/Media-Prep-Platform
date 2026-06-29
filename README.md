# Loom

## Project Introduction

Loom is a professional media preparation and quality-control platform for live events, XR, broadcast, exhibitions, digital venues, and media-server workflows. The current implementation exposes the `mediaqc` command-line tool and prepares the repository for a future desktop studio, dashboard, plugin SDK, and enterprise deployment model.

## Core Features

- Recursive media scanning for video, image, and audio assets.
- SHA256 hashing with SQLite hash cache and duplicate detection.
- FFprobe metadata extraction and FFmpeg deep decode analysis.
- Modular validation engine with YAML rules and project profiles.
- Live event checks for output specs, LED canvas layouts, codec risk, manifests, and integrity verification.
- FFmpeg/FFplay environment checks, preview playback, transcode presets, subtitles, logo overlays, and batch job reports.
- PySide6 desktop GUI named Loom with splash/welcome cover, light engineering theme, project/rule/history panels, scan queue, preview/log panes, and JSON/CSV/HTML/PDF export.
- Media Pipeline for mounted NAS/SMB/AFP/NFS workflows, SHA256 sync, FFprobe/MediaInfo metadata, transfer reports, compare reports, and project packages.
- Enterprise Media Asset Management foundation for the commercial edition, including users, roles, projects, assets, REST API, GraphQL entry point, webhooks, notification adapters, and Docker Compose services for PostgreSQL, Redis, RabbitMQ, and MinIO.
- JSON, CSV, and HTML reporting.
- FastAPI dashboard with REST API foundations.

## Directory Structure

```text
mediaqc/              Python package for the current CLI implementation
docs/                 GitHub documentation system and product specifications
config/               Example YAML rules, output specs, and canvas specs
profiles/             Built-in workflow profiles
reports/              Local generated reports, ignored by Git
tests/                Automated tests
examples/             Future examples and sample projects
assets/               Documentation and UI assets
scripts/              Utility scripts
tools/                Optional bundled external tools such as FFmpeg, FFprobe, FFplay, and MediaInfo
resources/            Future packaged resources
.github/              GitHub issue, PR, and workflow metadata
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
mediaqc scan ./Media --profile disguise --output ./reports --html
mediaqc version
mediaqc editions
mediaqc tools doctor
mediaqc tools install-check
```

## Editions And Licensing

Loom uses a dual-edition model:

- Community Edition is licensed under Apache License 2.0 and includes FFmpeg integration, FFprobe metadata extraction, SHA256 verification, media validation, and batch transcoding.
- Enterprise Edition is licensed under a commercial license and includes multi-user permissions, LDAP/AD, audit logs, NAS cluster workflows, the web management dashboard, automatic content distribution, and Render Farm management.

Check the current edition matrix from the CLI:

```bash
mediaqc editions
```

## Desktop GUI

Install the optional GUI dependency and launch the desktop app:

```bash
python -m pip install "mediaqc[gui]"
mediaqc gui
# or
loom-gui
```

The V1.0 GUI provides a light PySide6 workspace with:

- Loom splash and welcome cover with version, icon, New/Open/Recent entry points.
- Menu bar sections for Loom, File, Edit, View, Presets, Window, and Help.
- HandBrake-style source/action toolbar, source title controls, preset/range controls, and output path controls.
- Parameter tabs for Summary, Dimensions, Filters, Video, Audio, Subtitles, and Chapters.
- Drag-and-drop scanning, batch queue, progress, and cancel request.
- Source Preview and Output Preview comparison panes for compression and transcode workflows.
- Scan-complete CSV preview dialog showing up to 10 file rows and excluding folders.
- Background scanning in a worker thread.
- Automatic JSON, CSV, HTML, and PDF report export.

## Media Pipeline

Loom treats NAS protocols such as SMB, AFP, and NFS as mounted filesystem paths. Mount the share with the operating system first, then run pipeline commands against the mounted path.

```bash
mediaqc pipeline sync ./Media --destination /Volumes/ShowNAS/Media --profile disguise --output ./reports
mediaqc pipeline compare ./Media --destination /Volumes/ShowNAS/Media --output ./reports
mediaqc pipeline package ./Media --profile millumin --output ./packages
```

Pipeline commands automatically calculate SHA256, run FFprobe, optionally collect MediaInfo when the `mediainfo` command is installed, generate `manifest.json`, synchronize media to the server path, write `transfer_report.json/csv`, write `sha256_compare.json/csv`, and create a project package for Millumin, Disguise, Pixera, TouchDesigner, or Notch handoff.

## Enterprise MAM

Enterprise MAM capabilities are part of Loom Enterprise Edition under a commercial license. Start the V2.0 enterprise API locally for licensed enterprise development and evaluation:

```bash
mediaqc enterprise-api --host 127.0.0.1 --port 8080
```

Default development login:

- Email: `admin@example.com`
- Password: `admin`

OpenAPI is available at `http://127.0.0.1:8080/docs`. The enterprise dashboard is available at `http://127.0.0.1:8080/dashboard`. The API currently includes login, users, projects, assets, overview counts, webhook preview, notification dry-runs, and a minimal GraphQL endpoint at `/graphql`.

Run the container stack:

```bash
cp .env.example .env
docker compose up --build
```

The compose stack defines services for the API, Celery worker, PostgreSQL, Redis, RabbitMQ, and MinIO. V2.0 stores API data in an in-memory reference repository while the deployment contract and configuration are prepared for PostgreSQL-backed persistence in the next enterprise iteration.

Supported storage contracts:

- NAS/local mounted paths, including SMB, AFP, and NFS shares mounted by the operating system.
- S3, Azure, Google Drive, and WebDAV URI adapters for future provider implementations.

Supported notification adapters:

- Feishu
- Slack
- Microsoft Teams
- Email

## Packaging And Release

Loom can be built as cross-platform CLI and desktop GUI release bundles with PyInstaller:

```bash
python -m pip install -e ".[release]"
bash packaging/scripts/build_macos.sh
bash packaging/scripts/build_linux.sh
powershell -ExecutionPolicy Bypass -File packaging/scripts/build_windows.ps1
```

Release artifacts are written to `dist_release/` and include zipped CLI bundles, a desktop GUI bundle named like `Loom-1.0.0-macos.zip`, Docker packaging assets, `SHA256SUMS.txt`, and `release_notes.md`. GitHub Actions builds release assets from `.github/workflows/release.yml` when a `v*` tag is pushed.

Loom uses `ffmpeg`, `ffprobe`, and `ffplay` as default media tool modules. They can be provided externally on `PATH`, pointed to with `MEDIAQC_FFMPEG_PATH` / `MEDIAQC_FFMPEG_DIR`, bundled beside the executable, or installed into the software-local `tools/plugins/ffmpeg` directory. On first GUI launch, Loom checks for all three tools and prompts before installing missing tools. Use `mediaqc tools install-ffmpeg` or Preferences > Basic to preinstall or repair the full FFmpeg tool bundle, and `LOOM_DISABLE_TOOL_DOWNLOAD=1` to disable automatic downloads.

## Documentation Entry Points

- Project overview: `docs/00_Project/README.md`
- Architecture: `docs/01_Architecture/README.md`
- Development workflow: `docs/02_Development/README.md`
- User guide: `docs/13_UserGuide/README.md`
- AI collaboration: `docs/14_AI/README.md`
- Specifications: `docs/17_Specifications/README.md`

## Example Project

A copyable live-event example is available in `examples/LED_Show_6400x2000/`. Add media files to its `Media/` folder, then run the command in that example README to generate JSON, CSV, HTML, and manifest reports.

## Diagnostics And Updates

```bash
mediaqc doctor
mediaqc tools install-ffmpeg
mediaqc tools install-check
mediaqc tools logs
mediaqc update check
```

Logs are written to the platform log directory by default, or to `--log-dir` / `MEDIAQC_LOG_DIR` when configured.

## Development Entry Points

```bash
python -m pytest
ruff check .
mediaqc --help
```

## Roadmap

See `ROADMAP.md` and `docs/00_Project/Roadmap.md`.

## FFmpeg / FFplay

Install a full FFmpeg package that includes `ffmpeg`, `ffprobe`, and `ffplay`.

```bash
brew install ffmpeg
mediaqc tools doctor
```

The doctor command reports binary paths, FFmpeg version, available encoder/filter counts, and support hints for HAP, ProRes, libx264, libx265, and NotchLC decode/encode.

## Preview Playback

```bash
mediaqc play ./Media/Opening.mov
mediaqc play ./Media/Opening.mov --loop --mute --scale 0.5 --timecode
mediaqc play ./Media/Opening.mov --start 00:01:20
```

If `ffplay` is missing, install a full FFmpeg package rather than an ffmpeg-only runtime.

## Transcode Presets

Preset YAML files live in `config/transcode_presets/`.

```bash
mediaqc transcode input.mov --preset hap_q_4k --output ./encoded
mediaqc transcode ./Media --preset h264_preview --output ./preview --recursive
mediaqc transcode input.mov --preset prores_4444 --output ./masters --dry-run
```

Transcode jobs write `job_report.json` and `job_report.csv`, and each job can write its own log file.

## NotchLC Encoding

NotchLC decode/probe support is separate from NotchLC encoding support. Encoding requires an optional backend configured in `config/encoder_backends.yaml`:

- `ffmpeg` backend for codecs available in the local FFmpeg build.
- `notchlc_external` backend for an external NotchLC encoder executable.
- `adobe_media_encoder` workflow for preparing Adobe Media Encoder Watch Folders.
- `custom_command` backend for user-defined command templates.

Loom does not reverse engineer, decompile, patch, recompile, or directly load any NotchLC Adobe plugin binary. NotchLC encoding depends on official Adobe Media Encoder, Premiere, After Effects, or official NotchLC SDK/tool availability.

Prepare an official AME Watch Folder workflow:

```bash
mediaqc notchlc prepare ./Media --watch-folder ./AME_Watch --output ./Encoded_NotchLC
```

The command writes `ame_jobs.json`, `ame_jobs.csv`, and `README_AME_NOTCHLC.txt`, then asks the operator to select an official NotchLC preset inside Adobe Media Encoder.

If the NotchLC encoder backend is unavailable, Loom reports a clear error and does not crash.

## Subtitles

```bash
mediaqc subtitle input.mov --subtitle captions.srt --mode soft --output output.mp4
mediaqc subtitle input.mov --subtitle captions.ass --mode burn --fonts-dir ./fonts --output output_subbed.mp4
```

Soft subtitles add a subtitle track. Burned subtitles use the FFmpeg `subtitles` filter and write stderr to a log on failure.

## Logo Overlay

```bash
mediaqc logo input.mov --logo logo.png --position top-right --output output_logo.mp4
mediaqc logo input.mov --logo logo.png --x 100 --y 80 --opacity 0.8 --output output_logo.mp4
mediaqc logo ./Media --logo logo.png --position bottom-right --output ./review --recursive --preset h264_preview
```

Logo overlay uses FFmpeg filter graphs and supports PNG alpha, opacity, position presets, custom x/y, start/end timing, dry-run, and batch jobs.

## Common Processing Errors

- `ffmpeg was not found`: install FFmpeg and confirm the binary is on `PATH`.
- `ffplay was not found`: install a full FFmpeg package with FFplay included.
- `Encoder is not available`: choose another preset or install/configure the required encoder.
- `NotchLC encoder backend is not available`: configure `config/encoder_backends.yaml` or use HAP/ProRes/H264 presets.

## License

Loom Community Edition is licensed under Apache License 2.0.

Loom Enterprise Edition is distributed under a commercial license for capabilities such as multi-user permissions, LDAP/AD, audit logs, NAS cluster workflows, web management, automatic content distribution, and Render Farm management. See `docs/00_Project/Editions.md` and `docs/15_Commercial/Licensing.md`.

## Legacy Notes

The stable Python package and CLI command remain `mediaqc` for script compatibility. User-facing product documentation, GUI surfaces, and release downloads use the Loom name.
