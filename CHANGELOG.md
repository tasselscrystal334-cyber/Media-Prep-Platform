# Changelog

All notable Loom changes are documented here.

## [Unreleased]

### Added

- Default FFmpeg tool modules for `ffmpeg`, `ffprobe`, and `ffplay`.
- First-run GUI detection with an install confirmation prompt when `ffmpeg`, `ffprobe`, or `ffplay` is missing.
- Automatic FFmpeg-family tool installation into the software-local `tools/plugins/ffmpeg` directory when required binaries are missing.
- `mediaqc tools install-ffmpeg` for explicit preinstallation or repair of the FFmpeg tool bundle.
- Preferences > Basic action for installing or repairing FFmpeg-family tools from the desktop GUI.
- Help > Tools Doctor opens an interactive diagnostics table in the desktop GUI.
- Help > Documentation opens the local repository documentation entry point.
- Scan-complete CSV preview dialog that shows up to 10 file rows and excludes folders.
- `scripts/local_live_update.sh` for local editable install, test, tools doctor, and optional GUI launch without downloading GitHub release assets.
- `scripts/launch_loom_macos.sh` for a local macOS Loom.app launcher during development.
- GUI source previews now ignore `.DS_Store`, folders, and unsupported non-media files.
- GUI source previews now show the detected media file count directly in the file list header.
- GUI title selection now uses a dropdown of supported files in the selected source folder with duration labels.
- GUI output presets now use parent/child grouped menus.
- GUI format selection now uses common output container choices such as MP4, MOV, MKV, WebM, MXF, AVI, and image sequences.
- GUI output preview now includes a Start Live Preview action that summarizes the selected title, preset, format, duration, and output name, and attempts to render a preview frame with FFmpeg.

### Changed

- Desktop GUI palette now uses a softer light, low-contrast theme.
- Desktop GUI layout now uses a professional transcoding-tool structure with a top action toolbar, source controls, parameter tabs, queue, and source/output preview comparison panes.
- Desktop GUI source controls replace the irrelevant HandBrake-style Angle field with Scan Range and remove duplicated toolbar Presets, Preview, and Queue actions.
- Desktop GUI preset labels use Proxy for H.264/H.265 lightweight review/transcode outputs to avoid confusing them with the Preview panel.
- Desktop GUI uses an in-window Loom menu bar during local Python launches so menus remain correctly branded and responsive.
- Documentation and generated build/report artifacts have been cleaned so current Loom documentation stays focused on active product behavior.

## [1.0.0] - 2026-06-27

### Added

- Loom CLI and desktop GUI release line.
- Media scanning, SHA256, FFprobe metadata, FFmpeg analysis, validation rules, reports, live-event checks, manifests, watch mode, dashboard, packaging, and release automation.

## Revision History

- Documentation version: 1.1
- Last updated: 2026-06-29
