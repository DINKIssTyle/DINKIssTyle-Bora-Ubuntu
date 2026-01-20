#!/bin/bash
set -e

APP_NAME="bora"
VERSION="1.0.0"
ARCH="amd64"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR/deb_dist"
DIST_DIR="$SCRIPT_DIR/dist"
ICON_DIR="$SCRIPT_DIR/assets"

echo "==================================="
echo "  Bora .deb Build Script"
echo "==================================="

# 0. Check PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller is not installed."
    echo "Please run: pip3 install --user pyinstaller"
    exit 1
fi

# 1. Build Binary
echo "[1/5] Building binary..."
cd "$SCRIPT_DIR"
# Clean previous build
rm -rf "$DIST_DIR" "$SCRIPT_DIR/build"

pyinstaller \
    --onefile \
    --name="$APP_NAME" \
    --windowed \
    --add-data="assets:assets" \
    --hidden-import=PyQt6 \
    --hidden-import=mss \
    --hidden-import=PIL \
    --hidden-import=keyboard \
    --hidden-import=numpy \
    main.py

# 2. Prepare Directory Structure
echo "[2/5] Creating directory structure..."
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR/DEBIAN"
mkdir -p "$WORK_DIR/usr/bin"
mkdir -p "$WORK_DIR/usr/share/applications"
mkdir -p "$WORK_DIR/usr/share/icons/hicolor/128x128/apps"

# 3. Copy Files
echo "[3/5] Copying files..."
if [ -f "$DIST_DIR/$APP_NAME" ]; then
    cp "$DIST_DIR/$APP_NAME" "$WORK_DIR/usr/bin/"
    chmod 755 "$WORK_DIR/usr/bin/$APP_NAME"
else
    echo "Error: Binary not found at $DIST_DIR/$APP_NAME"
    exit 1
fi

# Copy Icon
if [ -f "$ICON_DIR/icon.png" ]; then
    cp "$ICON_DIR/icon.png" "$WORK_DIR/usr/share/icons/hicolor/128x128/apps/$APP_NAME.png"
else
    echo "Warning: Icon not found at $ICON_DIR/icon.png"
fi

# Create Desktop File for Package
cat > "$WORK_DIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Name=Bora
Name[ko]=보라
Comment=Screen Capture Utility
Comment[ko]=화면 캡처 유틸리티
Exec=/usr/bin/$APP_NAME
Icon=$APP_NAME
Terminal=false
Type=Application
Categories=Utility;Graphics;
Keywords=screenshot;capture;image;
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

# 4. Create Control File
echo "[4/5] Creating control file..."

cat > "$WORK_DIR/DEBIAN/control" << EOF
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: python3, libxcb-cursor0, gnome-screenshot
Maintainer: DINKIssTyle <dinki@me.com>
Description: Screen Capture Utility
 Bora is a screen capture tool that allows you to capture selected areas
 and pin them as floating windows on your desktop.
EOF

# 5. Build Package
echo "[5/5] Building .deb package..."
dpkg-deb --build "$WORK_DIR" "${APP_NAME}_${VERSION}_${ARCH}.deb"

echo
echo "==================================="
echo "  Package created: ${APP_NAME}_${VERSION}_${ARCH}.deb"
echo "==================================="
