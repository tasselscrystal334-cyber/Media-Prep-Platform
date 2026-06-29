# Changelog

All notable Loom changes are documented here.

## [Unreleased]

### Added

- Default FFmpeg tool modules for `ffmpeg`, `ffprobe`, and `ffplay`.
- First-run GUI detection with an install confirmation prompt when `ffmpeg`, `ffprobe`, or `ffplay` is missing.
- Automatic FFmpeg-family tool installation into the software-local `tools/plugins/ffmpeg` directory when required binaries are missing.
- `mediaqc tools install-ffmpeg` for explicit preinstallation or repair of the FFmpeg tool bundle.
- Preferences > Basic action for installing or repairing FFmpeg-family tools from the desktop GUI.
- Scan-complete CSV preview dialog that shows up to 10 file rows and excludes folders.
- `scripts/local_live_update.sh` for local editable install, test, tools doctor, and optional GUI launch without downloading GitHub release assets.

### Changed

- Desktop GUI palette now uses a softer light, low-contrast theme.
- Desktop GUI layout now uses a professional transcoding-tool structure with a top action toolbar, source controls, parameter tabs, queue, and source/output preview comparison panes.
- Documentation and generated build/report artifacts have been cleaned so current Loom documentation stays focused on active product behavior.

## [1.0.0] - 2026-06-27

### Added

- Loom CLI and desktop GUI release line.
- Media scanning, SHA256, FFprobe metadata, FFmpeg analysis, validation rules, reports, live-event checks, manifests, watch mode, dashboard, packaging, and release automation.

## Revision History

- Documentation version: 1.1
- Last updated: 2026-06-29
