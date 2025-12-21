#!/bin/bash
set -e

APP_NAME="DINKIssTyle-Bora"
PACKAGE_NAME="dinkisstyle-bora"
VERSION="1.0.0"
ARCH="amd64"
OUTPUT_DIR="deb_dist"
STAGING_DIR="$OUTPUT_DIR/${PACKAGE_NAME}_${VERSION}_${ARCH}"

echo "🔨 Starting .deb build process for $APP_NAME..."

# 1. Build the binary
echo "📦 Building binary..."

# Clean previous builds
rm -rf build dist

# Build using PyInstaller via uv
echo "Running PyInstaller..."
uv run pyinstaller --noconsole --onefile --name DINKIssTyle-Bora \
    --hidden-import=evdev \
    --hidden-import=PyQt6 \
    --hidden-import=mss \
    --hidden-import=numpy \
    --hidden-import=PIL \
    --add-data "assets:assets" \
    --collect-all=mss \
    --collect-all=evdev \
    main.py

echo "Build complete! Binary is in dist/DINKIssTyle-Bora"

# 2. Prepare directories
echo "📂 Preparing directory structure..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$STAGING_DIR/usr/bin"
mkdir -p "$STAGING_DIR/usr/share/applications"
mkdir -p "$STAGING_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$STAGING_DIR/DEBIAN"

# 3. Copy files
echo "COPY Creating package files..."

# Binary
cp "dist/$APP_NAME" "$STAGING_DIR/usr/bin/$APP_NAME"
chmod 755 "$STAGING_DIR/usr/bin/$APP_NAME"

# Icon
cp "assets/icon.png" "$STAGING_DIR/usr/share/icons/hicolor/256x256/apps/${PACKAGE_NAME}.png"

# Desktop Entry
# We manually create/modify the desktop file for the system-wide installation
cat > "$STAGING_DIR/usr/share/applications/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Name=Bora
Comment=Screen Capture and Floating Window Utility
Exec=/usr/bin/$APP_NAME
Icon=$PACKAGE_NAME
Type=Application
Categories=Utility;
Terminal=false
EOF

# 4. Create Control File
echo "📝 Generating control file..."
INSTALLED_SIZE=$(du -s "$STAGING_DIR" | cut -f1)

cat > "$STAGING_DIR/DEBIAN/control" <<EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: libxcb-cursor0, gnome-screenshot, libxcb-xinerama0
Maintainer: DINKI <dinki@example.com>
Description: Screen capture and input utility for Ubuntu
 Floating window capture tool with clipboard features.
EOF

# 5. Create Post-Install Script (Optional, for permissions)
# We need to warn user about 'input' group or udev rules. 
# Simplest is just a message.
cat > "$STAGING_DIR/DEBIAN/postinst" <<EOF
#!/bin/sh
echo "DINKIssTyle-Bora installed!"
echo "NOTE: To use global hotkeys, your user usually needs to be in the 'input' group."
echo "Run: sudo usermod -aG input \$USER"
echo "Then logout and login again."
exit 0
EOF
chmod 755 "$STAGING_DIR/DEBIAN/postinst"

# 6. Build .deb
echo "📦 Packaging..."
dpkg-deb --build "$STAGING_DIR"

echo "✅ Build Complete!"
echo "Generated: $(ls $OUTPUT_DIR/*.deb)"
