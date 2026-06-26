# Project Constitution

## Purpose

Define the highest-level rules for MediaPrep Studio engineering, documentation, testing, AI collaboration, and commercial readiness.

## Overview

MediaPrep Studio is a professional media preparation platform for live events, XR, broadcast, exhibitions, digital venues, and media-server workflows. The constitution is the final authority when feature speed conflicts with maintainability.

## Architecture

Architecture is designed before implementation. New subsystems must document ownership boundaries, dependencies, APIs, persistence, error handling, and test strategy before code is considered complete.

## Workflow

Design, document, implement, test, update documentation, then commit. Chat history is not permanent project memory; the GitHub repository is the source of truth.

## Dependencies

Engineering decisions must prefer stable Python, FFmpeg, SQLite, documented APIs, and platform-neutral filesystem behavior unless an architecture document approves a specialized dependency.

## Configuration

Configuration must be explicit, versionable, and documented. YAML is used for project rules, profiles, output specs, canvas specs, and future workflow presets.

## Example

A validator plugin must include design notes, API contract, tests, documentation updates, and changelog entry before merge.

## Known Limitations

This constitution governs the repository; legal, financial, and commercial policy may require separate review before public release.

## Future Improvements

Add signed release governance, enterprise support policy, and formal plugin marketplace rules before v1.0.

## Related Modules

- `CONTRIBUTING.md`
- `docs/02_Development/DocumentationPolicy.md`
- `docs/14_AI/AIDocumentationPolicy.md`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27
