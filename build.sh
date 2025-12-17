#!/bin/bash
set -e

echo "Building DINKIssTyle-Bora..."

# Clean previous builds
rm -rf build dist

# Build using PyInstaller via uv
# --hidden-import=evdev is important because it's imported dynamically often, though here it is static.
# --add-data "assets:assets" if we had assets, but we might not have the folder yet. 
# We should check if assets exists or just add config.json logic.
# Actually config.json is generated at runtime, no need to bundle.
# But we need icon. Let's assume we might have one later. For now, basic build.

uv run pyinstaller --noconsole --onefile --name DINKIssTyle-Bora \
    --hidden-import=evdev \
    --hidden-import=PyQt6 \
    --collect-all=evdev \
    main.py

echo "Build complete! Binary is in dist/DINKIssTyle-Bora"
