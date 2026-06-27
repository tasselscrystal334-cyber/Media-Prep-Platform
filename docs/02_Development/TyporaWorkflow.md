# Typora Workflow

## Purpose

Explain how maintainers can edit GitHub-compatible Markdown with Typora.

## Overview

Typora is optional. It can improve local Markdown authoring, but documents must stay compatible with GitHub rendering.

## Architecture

This document aligns with the Loom layered architecture: presentation, application, services, core, infrastructure, codec engine, media engine, and hardware integration.

## Workflow

Open the repository folder in Typora or open `docs/README.md` directly. Preview Markdown before committing, keep Mermaid diagrams fenced as `mermaid`, store images under `assets/` or `docs/assets/`, and avoid Typora-only syntax that breaks GitHub display.

## Dependencies

Typora is optional. If Typora is not installed, continue using any Markdown editor and do not block development.

## Configuration

Use GitHub-compatible Markdown. Tables should use normal pipe-table syntax. Mermaid diagrams should be committed as fenced code blocks. File names should be descriptive PascalCase or clear README names.

## Example

macOS:

```bash
open -a Typora docs/README.md
```

Windows PowerShell:

```powershell
Start-Process "typora" "docs/README.md"
```

## Known Limitations

Typora-specific visual settings are not repository standards.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `docs/README.md`
- `docs/02_Development/DocumentationPolicy.md`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27
