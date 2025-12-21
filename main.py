import sys
import os

# Force XCB (X11) backend to bypass strict Wayland window placement restrictions
# This allows 'Always on Top' and programmatic positioning to work correctly.
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QDialog, QVBoxLayout, QLabel, QPushButton, QKeySequenceEdit
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QPixmap
from PyQt6.QtCore import QObject, Qt

from snipper import Snipper
from floating_widget import FloatingWidget
from config_manager import ConfigManager

class AboutDialog(QDialog):
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Bora")
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon
        icon_label = QLabel(self)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            # Scale it nicely
            pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title = QLabel("Bora", self)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Copyright
        copyright = QLabel("(C) 2025 DINKI'ssTyle", self)
        copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Capture Hotkey:"))
        
        self.key_edit = QKeySequenceEdit(self)
        current_hotkey = ConfigManager.get_hotkey()
        self.key_edit.setKeySequence(QKeySequence(current_hotkey))
        layout.addWidget(self.key_edit)
        
        save_btn = QPushButton("Save", self)
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
    def save_settings(self):
        # Determine the key sequence string
        seq = self.key_edit.keySequence().toString()
        # Convert to a format friendly for 'keyboard' module if possible, 
        # or just save as Qt string and let the main app handle conversion/warning.
        # 'keyboard' module likes 'ctrl+shift+s', Qt gives 'Ctrl+Shift+S'.
        # Usually case insensitive.
        if seq:
            ConfigManager.set_hotkey(seq)
        self.accept()

class BoraUbuntu(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Keep track of windows to prevent GC
        self.floating_windows = []
        self.snipper = None

        # Setup Tray Icon
        self.tray_icon = QSystemTrayIcon(self.app)
        self.load_icon()
        
        # Tray Menu
        self.menu = QMenu()
        
        self.capture_action = QAction("Capture", self)
        self.capture_action.triggered.connect(self.start_capture)
        self.menu.addAction(self.capture_action)
        
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(self.settings_action)
        
        self.menu.addSeparator()
        
        self.about_action = QAction("About Bora", self)
        self.about_action.triggered.connect(self.open_about)
        self.menu.addAction(self.about_action)

        self.menu.addSeparator()
        
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
        
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, relative_path)

    def load_icon(self):
        # Try to load local icon, fallback to system icon
        # Use resource_path to correctly locate assets in both dev and built versions
        icon_path = self.resource_path(os.path.join('assets', 'icon.png'))
        
        print(f"DEBUG: Loading icon from {icon_path}") # Debug print
        
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            print(f"DEBUG: Icon not found at {icon_path}, using fallback.")
            # Fallback
            self.tray_icon.setIcon(QIcon.fromTheme("camera-photo"))

    def start_capture(self):
        # Create snipper
        # We need to make sure previous snipper is gone or reused
        if self.snipper:
            self.snipper.close()
        
        self.snipper = Snipper()
        self.snipper.capture_signal.connect(self.create_floating_window)
        # Snipper shows itself in its __init__ (which is a bit aggressive but fine for now)

    def create_floating_window(self, pixmap, rect):
        print("DEBUG: create_floating_window called")
        try:
            fw = FloatingWidget(pixmap, rect)
            # When window closes, remove from list ??
            # For now just keep them appended. In a long running app, we'd want to cleanup.
            # Let's add a cleanup hook
            fw.destroyed.connect(lambda: self.cleanup_window(fw))
            self.floating_windows.append(fw)
            fw.show()
            print("DEBUG: FloatingWidget created and shown")
        except Exception as e:
            print(f"ERROR: Failed to create floating window: {e}")
            import traceback
            traceback.print_exc()

    def cleanup_window(self, window):
        if window in self.floating_windows:
            self.floating_windows.remove(window)

    def open_settings(self):
        dlg = SettingsDialog()
        if dlg.exec():
            # Reload hotkeys
            self.setup_hotkeys()

    def open_about(self):
        icon_path = self.resource_path(os.path.join('assets', 'icon.png'))
        dlg = AboutDialog(icon_path, None)
        dlg.exec()

    def setup_hotkeys(self):
        try:
            from hotkey_listener import HotkeyListener
            
            # Stop existing listener if any
            if hasattr(self, 'hotkey_listener') and self.hotkey_listener:
                self.hotkey_listener.stop()
            
            hotkey = ConfigManager.get_hotkey()
            self.hotkey_listener = HotkeyListener(hotkey, self.start_capture_safe)
            self.hotkey_listener.start()
            
            print(f"Hotkey listener started for: {hotkey}")
        except Exception as e:
            print(f"Failed to setup hotkeys: {e}")

    def start_capture_safe(self):
        # Keyboard library callback runs in a separate thread.
        # We must invoke GUI methods on the main thread.
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self.start_capture)

    def run(self):
        self.setup_hotkeys()
        sys.exit(self.app.exec())

def exception_hook(exctype, value, traceback):
    print(f"Uncaught exception: {value}")
    import traceback as tb
    tb.print_tb(traceback)
    sys.__excepthook__(exctype, value, traceback)

if __name__ == "__main__":
    sys.excepthook = exception_hook
    app = BoraUbuntu()
    app.run()
