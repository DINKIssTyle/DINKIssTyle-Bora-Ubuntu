# Bora for Ubuntu
A simple floating screenshot tool for Ubuntu, inspired by Fuwari (macOS).
This app allows you to capture a region of your screen and float it as a window that stays on top of other applications.

## Features
- **Capture**: Select a region of the screen to capture.
- **Float**: The captured image floats in a frameless window.
- **Always on Top**: Floating images stay above other windows.
- **Interactions**:
    - **Drag**: Move the floating image.
    - **Scroll**: Adjust opacity.
    - **Right Click**: Menu to Save, Copy to Clipboard, or Close.

## Installation
1. Install Python 3 and pip if not installed:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If you are on a managed environment, you might need to use `python3 -m pip install -r requirements.txt --break-system-packages` or use a virtual environment.*
   
   **Virtual Environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage
Run the application:
```bash
python3 main.py
```
A tray icon (camera/menu icon) will appear. Click it or right-click to select **Capture**.

## Wayland Note
On Ubuntu 22.04 and later, Wayland is the default display server. Screen capture applications often face restrictions on Wayland.
This app uses `mss` which attempts to capture the screen. If you see a black screen or capture fails:
- Try logging in with **Ubuntu on Xorg** at the login screen.
- Or ensure `XWayland` is active.

## Project Structure
- `main.py`: Entry point and System Tray handling.
- `snipper.py`: Screen capture overlay logic.
- `floating_widget.py`: The floating image window logic.
