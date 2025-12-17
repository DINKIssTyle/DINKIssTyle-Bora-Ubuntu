# DINKIssTyle Bora (Ubuntu Edition)

A premium floating screenshot tool for Ubuntu, inspired by Fuwari (macOS).
Capture any region of your screen and float it as an "Always on Top" window for reference.

## Features
-   **Smart Capture**: Works seamlessly on both **Wayland** (via `gnome-screenshot`) and **X11**.
-   **Floating widget**: Drag, move, and keep your screenshots visible while you work.
-   **Global Hotkeys**: 
    -   Default: `Meta+Shift+S` (Configurable via Settings).
    -   Powered by a custom `evdev` driver for maximum stability on Linux.
-   **Polished UI**: Drop shadows, smooth interactions, and native desktop integration.
-   **Shortcuts**:
    -   `Ctrl+W` / `Ctrl+Q`: Close floating widget.
    -   `Right-Click`: Context menu (Save, Copy, Close).

## Installation

### Method 1: Easy Install (Recommended)
This installs the standalone binary, sets up permissions, and creates a desktop shortcut.

1.  Download the source.
2.  Run the installer:
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
3.  **Logout and Login** (Required for hotkey permissions).

### Method 2: Development / Source
If you want to run from source or modify the code:

1.  Install `uv` (modern Python package manager):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
2.  Install dependencies and run:
    ```bash
    uv sync
    uv run main.py
    ```

## Requirements
-   **System**: Ubuntu 22.04 / 24.04 (Wayland or X11)
-   **Dependencies**: `libxcb-cursor0`, `gnome-screenshot` (Installed automatically by `install.sh`)
-   **Permissions**: User must be in the `input` group for global hotkeys (Configured automatically by `install.sh`).

## Troubleshooting
-   **Hotkeys not working?** 
    Ensure you are in the input group: `groups | grep input`. If empty, run `./install.sh` again and **logout**.
-   **Black screen capture?**
    Ensure `gnome-screenshot` is installed: `sudo apt install gnome-screenshot`.
