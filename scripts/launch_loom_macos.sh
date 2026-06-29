#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="${ROOT_DIR}/.local_app/Loom.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
EXECUTABLE="${MACOS_DIR}/Loom"
PLIST="${CONTENTS_DIR}/Info.plist"

if [[ "$(uname -s)" != "Darwin" ]]; then
  exec "${ROOT_DIR}/.venv/bin/loom-gui" "$@"
fi

mkdir -p "${MACOS_DIR}" "${CONTENTS_DIR}/Resources"

cat > "${PLIST}" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleDisplayName</key>
  <string>Loom</string>
  <key>CFBundleExecutable</key>
  <string>Loom</string>
  <key>CFBundleIdentifier</key>
  <string>com.loom.localdev</string>
  <key>CFBundleName</key>
  <string>Loom</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0.0</string>
  <key>LSMinimumSystemVersion</key>
  <string>11.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
EOF

cat > "${EXECUTABLE}" <<EOF
#!/usr/bin/env bash
cd "${ROOT_DIR}"
export PYTHONPATH="${ROOT_DIR}:\${PYTHONPATH:-}"
exec "${ROOT_DIR}/.venv/bin/python" -m mediaqc.gui.app "\$@"
EOF
chmod +x "${EXECUTABLE}"

open -n "${APP_DIR}" --args "$@"
