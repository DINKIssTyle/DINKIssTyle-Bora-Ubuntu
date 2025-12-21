import sys
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QScreen

class Snipper(QWidget):
    capture_signal = pyqtSignal(QPixmap, QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # State
        self.is_snipping = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        
        # Capture full screen immediately
        screen = QApplication.primaryScreen()
        # Handle multi-screen geometry union if needed, but for simplicity starts with virtual geometry
        # Combining all screens:
        self.full_screen_pixmap = self.grab_all_screens()
        
        # Geometry setup
        self.setGeometry(self.get_virtual_geometry())
        self.show()

    def get_virtual_geometry(self):
        geometry = QRect()
        for screen in QApplication.screens():
            geometry = geometry.united(screen.geometry())
        return geometry

    def grab_all_screens(self):
        import mss
        import numpy as np
        from PyQt6.QtGui import QImage
        import os
        import subprocess
        import tempfile

        # Check for Wayland
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        is_wayland = 'wayland' in session_type

        # Wayland specific capture using gnome-screenshot (common on Ubuntu)
        if is_wayland:
            print("Wayland session detected. Attempting to use gnome-screenshot...")
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tf:
                    temp_filename = tf.name
                
                # Check if gnome-screenshot exists, otherwise fall back or warn
                # Ubuntu 22.04+ might need: sudo apt install gnome-screenshot
                subprocess.run(['gnome-screenshot', '-f', temp_filename], check=True)
                
                # Load into QPixmap
                pixmap = QPixmap(temp_filename)
                
                # Cleanup
                os.remove(temp_filename)
                
                if not pixmap.isNull():
                    # Update geometry to match the pixmap
                    self.resize(pixmap.width(), pixmap.height())
                    self.move(0, 0)
                    return pixmap
            except subprocess.CalledProcessError:
                print("gnome-screenshot failed.")
            except FileNotFoundError:
                print("gnome-screenshot not found.")
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Capture Failed", 
                                    "Wayland session detected but 'gnome-screenshot' is missing.\n"
                                    "Please install it: sudo apt install gnome-screenshot")
                # Fall through to try MSS or return black
            except Exception as e:
                print(f"Wayland capture failed: {e}")

        # Default / Fallback to MSS (X11 / macOS / Windows)
        try:
            with mss.mss() as sct:
                # Capture all monitors (virtual monitor 0)
                monitor = sct.monitors[0] 
                sct_img = sct.grab(monitor)
                
                img_data = sct_img.bgra
                
                qimage = QImage(img_data, sct_img.width, sct_img.height, QImage.Format.Format_ARGB32)
                pixmap = QPixmap.fromImage(qimage)
                
                self.move(monitor['left'], monitor['top'])
                self.resize(monitor['width'], monitor['height'])
                
                return pixmap
        except Exception as e:
            print(f"Error capturing screen: {e}")
            # On macOS, this often happens if Screen Recording permission is denied.
            # Return a blank pixmap to prevent crash
            blank = QPixmap(self.size())
            blank.fill(QColor("black"))
            return blank

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.full_screen_pixmap:
             # Draw the full dimmed screenshot
            painter.drawPixmap(0, 0, self.full_screen_pixmap)
        else:
            painter.fillRect(self.rect(), Qt.GlobalColor.black)
        
        # Dimming overlay
        dim_color = QColor(0, 0, 0, 100) # Semi-transparent black
        painter.fillRect(self.rect(), dim_color)
        
        if self.is_snipping:
            # Calculate rect
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            
            # Draw the clear (undimmed) area by redrawing that part of the pixmap
            if self.full_screen_pixmap:
                painter.drawPixmap(selection_rect, self.full_screen_pixmap, selection_rect)
            
            # Draw border
            painter.setPen(QPen(QColor(0, 120, 215), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_snipping = True
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_snipping:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_snipping:
            self.is_snipping = False
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            
            # Minimum size check
            if selection_rect.width() > 10 and selection_rect.height() > 10:
                if self.full_screen_pixmap:
                    cropped = self.full_screen_pixmap.copy(selection_rect)
                    # selection_rect is in local coords, which match global coords if full screen
                    # But let's map to global just in case we change window logic later
                    global_pos = self.mapToGlobal(selection_rect.topLeft())
                    global_rect = QRect(global_pos, selection_rect.size())
                    self.capture_signal.emit(cropped, global_rect)
                self.close()
            else:
                self.start_point = QPoint()
                self.end_point = QPoint()
                self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.is_snipping = False
            self.close()
