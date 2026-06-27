# Changelog

All notable changes to MediaPrep Studio are documented in this file.

The format follows Keep a Changelog and the project aims to follow Semantic Versioning after the public v1.0 release.

## [Unreleased]

### Added

- Repository documentation system for MediaPrep Studio.
- Project constitution, security policy, code of conduct, and AI collaboration documents.
- Product specifications under `docs/17_Specifications/`.
- Direct tests for Live Event output spec and codec profile risk behavior.
- FFmpeg/FFplay processing extension with tools doctor, preview playback, YAML transcode presets, optional encoder backends, subtitle embedding/burn-in, logo overlay, batch jobs, logs, and job reports.
- Adobe Media Encoder NotchLC Watch Folder preparation workflow with official-only plugin policy, `ame_jobs.json`, `ame_jobs.csv`, and operator instructions.
- V1.0 PySide6 desktop GUI with dark theme, Projects/Rules/History navigation, drag-and-drop scan queue, threaded scanning, progress, cancellation request, logs, preview pane, and JSON/CSV/HTML/PDF export.
- V1.5 Media Pipeline for NAS/SMB/AFP/NFS mounted sync, SHA256 transfer reports, FFprobe/optional MediaInfo metadata, compare reports, and project packages for Millumin, Disguise, Pixera, TouchDesigner, and Notch workflows.
- V2.0 enterprise MAM foundation with users, permissions, project management, REST/OpenAPI, GraphQL entry point, webhooks, notifications, storage adapters, Docker Compose, PostgreSQL, Redis, Celery, RabbitMQ, and MinIO configuration.
- V2.0 packaging and release system with PyInstaller CLI/GUI specs, platform build scripts, Docker packaging files, GitHub Actions release workflow, bundled FFmpeg path detection, `mediaqc-gui` entry point, SHA256SUMS generation, and release notes generation.
- V2.0 stability pass with root command aliases, install health checks, file log discovery, update checks, support diagnostics, and a copyable LED example project.
- Community/Enterprise edition matrix with Apache License 2.0 Community capabilities and commercial Enterprise capabilities exposed through `mediaqc editions`.

### Changed

- Root documentation now uses MediaPrep Studio as the product name while preserving the current `mediaqc` CLI implementation.
- Manifest `fps` values are normalized to numeric values for delivery manifests.
- HAP Alpha checks now warn when alpha is requested by codec name but not confirmed by pixel format metadata.
- HTML report template can display a Processing Summary when processing job data is provided.
- Package version updated to `1.0.0` for the first public release line.

## [0.95.0] - 2026-06-26

### Added

- Live Event Media QC extension with output spec checks, canvas validation, codec risk profiles, manifest generation, and integrity verification.
- FastAPI dashboard and REST API foundation.
- SQLite hash cache, history, and duplicate search.
- Watch mode, project profiles, validation engine, FFmpeg deep analysis, and HTML reporting.

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27
