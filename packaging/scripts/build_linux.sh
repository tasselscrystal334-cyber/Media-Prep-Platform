#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

python3 -m pip install -U pip
python3 -m pip install -e ".[gui,enterprise]" pyinstaller

rm -rf build dist dist_release
pyinstaller packaging/pyinstaller/mediaqc_cli.spec --noconfirm --clean
pyinstaller packaging/pyinstaller/mediaqc_gui.spec --noconfirm --clean
python3 packaging/scripts/make_release.py --platform linux --dist dist --output dist_release
