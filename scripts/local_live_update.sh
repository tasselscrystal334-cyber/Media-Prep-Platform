#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python3}"
VENV_DIR="${ROOT_DIR}/.venv"
RUN_TESTS=1
LAUNCH_GUI=0
INSTALL_TOOLS=0

usage() {
  cat <<'EOF'
Usage: scripts/local_live_update.sh [--no-tests] [--launch] [--install-tools]

Refresh the local Loom development install from this working tree.

Options:
  --no-tests       Skip pytest after editable install.
  --launch         Launch the local GUI after install/tests.
  --install-tools  Install or repair ffmpeg, ffprobe, and ffplay locally.
  -h, --help       Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-tests)
      RUN_TESTS=0
      ;;
    --launch)
      LAUNCH_GUI=1
      ;;
    --install-tools)
      INSTALL_TOOLS=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

cd "${ROOT_DIR}"

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

"${VENV_DIR}/bin/python" -m pip install -U pip
"${VENV_DIR}/bin/python" -m pip install -e ".[gui,dev]"

if [[ "${INSTALL_TOOLS}" -eq 1 ]]; then
  "${VENV_DIR}/bin/mediaqc" tools install-ffmpeg
fi

if [[ "${RUN_TESTS}" -eq 1 ]]; then
  LOOM_DISABLE_TOOL_DOWNLOAD=1 "${VENV_DIR}/bin/python" -m pytest
fi

"${VENV_DIR}/bin/mediaqc" tools doctor || true

if [[ "${LAUNCH_GUI}" -eq 1 ]]; then
  "${VENV_DIR}/bin/loom-gui"
fi
