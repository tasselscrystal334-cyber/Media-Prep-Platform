#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="/Applications/Loom Local.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
EXECUTABLE="${MACOS_DIR}/Loom Local"
PLIST="${CONTENTS_DIR}/Info.plist"

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
  <string>Loom Local</string>
  <key>CFBundleExecutable</key>
  <string>Loom Local</string>
  <key>CFBundleIdentifier</key>
  <string>com.loom.localdev.applications</string>
  <key>CFBundleName</key>
  <string>Loom Local</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0.0-local</string>
  <key>LSMinimumSystemVersion</key>
  <string>11.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
EOF

cat > "${EXECUTABLE}" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${ROOT_DIR}"
export PYTHONPATH="${ROOT_DIR}:\${PYTHONPATH:-}"
exec -a "Loom Local" "${ROOT_DIR}/.venv/bin/python" -m mediaqc.gui.app "\$@"
EOF

chmod +x "${EXECUTABLE}"
echo "Installed ${APP_DIR}"
