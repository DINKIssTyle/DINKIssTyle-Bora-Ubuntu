import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject

from snipper import Snipper
from floating_widget import FloatingWidget

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
        
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
        
    def load_icon(self):
        # Try to load local icon, fallback to system icon
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
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

    def create_floating_window(self, pixmap):
        fw = FloatingWidget(pixmap)
        # When window closes, remove from list ??
        # For now just keep them appended. In a long running app, we'd want to cleanup.
        # Let's add a cleanup hook
        fw.destroyed.connect(lambda: self.cleanup_window(fw))
        self.floating_windows.append(fw)
        fw.show()

    def cleanup_window(self, window):
        if window in self.floating_windows:
            self.floating_windows.remove(window)

    def setup_hotkeys(self):
        try:
            import keyboard
            # Hotkey: Ctrl+Shift+S (You can change this)
            # Note: On Linux, this might need sudo if not using specific permissions.
            # But the user mentioned it's a resident app.
            keyboard.add_hotkey('ctrl+shift+s', self.start_capture_safe)
            print("Hotkey registered: Ctrl+Shift+S")
        except ImportError:
            print("Keyboard module not found. Hotkeys disabled.")
        except Exception as e:
            print(f"Failed to setup hotkeys: {e}")

    def start_capture_safe(self):
        # Hotkeys run in a separate thread usually, so we should use signals/slots or current app context
        # to trigger the UI safely on the main thread.
        # But for simple triggering, it might be okay. To be safe, let's defer it.
        # However, Qt objects must be touched from the main thread.
        # Let's use QMetaObject.invokeMethod or similar if we were strict. 
        # But 'keyboard' callbacks might crash PyQt if we touch GUI directly.
        # A simple way that often works in PyQt6 is just calling it, but better is using a signal.
        # Let's emit a signal from a QObject if we can, but we are inside the class.
        # We'll use QTimer.singleShot(0, ...) to push it to the main event loop.
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self.start_capture)

    def run(self):
        self.setup_hotkeys()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = BoraUbuntu()
    app.run()
