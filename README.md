# MediaPrep Studio

## Project Introduction

MediaPrep Studio is a professional media preparation and quality-control platform for live events, XR, broadcast, exhibitions, digital venues, and media-server workflows. The current implementation exposes the `mediaqc` command-line tool and prepares the repository for a future desktop studio, dashboard, plugin SDK, and enterprise deployment model.

## Core Features

- Recursive media scanning for video, image, and audio assets.
- SHA256 hashing with SQLite hash cache and duplicate detection.
- FFprobe metadata extraction and FFmpeg deep decode analysis.
- Modular validation engine with YAML rules and project profiles.
- Live event checks for output specs, LED canvas layouts, codec risk, manifests, and integrity verification.
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
tools/                Development and documentation tools
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
```

## Documentation Entry Points

- Project overview: `docs/00_Project/README.md`
- Architecture: `docs/01_Architecture/README.md`
- Development workflow: `docs/02_Development/README.md`
- User guide: `docs/13_UserGuide/README.md`
- AI collaboration: `docs/14_AI/README.md`
- Specifications: `docs/17_Specifications/README.md`

## Development Entry Points

```bash
python -m pytest
ruff check .
mediaqc --help
```

## Roadmap

See `ROADMAP.md` and `docs/00_Project/Roadmap.md`.

## License

This repository currently uses the Apache License 2.0. Commercial licensing and enterprise activation plans are documented separately under `docs/15_Commercial/`.

## Legacy Level 1 Overview

Earlier documentation may refer to the implementation as MediaPrepTool or Media QC Tool. Those files are preserved as Level 1 overview documents while the repository evolves toward the MediaPrep Studio product structure.
