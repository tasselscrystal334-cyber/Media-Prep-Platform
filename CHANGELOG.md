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

### Changed

- Root documentation now uses MediaPrep Studio as the product name while preserving the current `mediaqc` CLI implementation.
- Manifest `fps` values are normalized to numeric values for delivery manifests.
- HAP Alpha checks now warn when alpha is requested by codec name but not confirmed by pixel format metadata.
- HTML report template can display a Processing Summary when processing job data is provided.

## [0.95.0] - 2026-06-26

### Added

- Live Event Media QC extension with output spec checks, canvas validation, codec risk profiles, manifest generation, and integrity verification.
- FastAPI dashboard and REST API foundation.
- SQLite hash cache, history, and duplicate search.
- Watch mode, project profiles, validation engine, FFmpeg deep analysis, and HTML reporting.

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27
