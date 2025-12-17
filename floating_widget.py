from PyQt6.QtWidgets import QWidget, QMenu, QApplication, QFileDialog
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QAction, QPainter, QColor, QGuiApplication

class FloatingWidget(QWidget):
    def __init__(self, pixmap: QPixmap):
        super().__init__()
        self.original_pixmap = pixmap
        self.current_opacity = 1.0
        
        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool  # Tool window often helps with floating behavior
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.resize(pixmap.width(), pixmap.height())
        self.center_on_screen()
        
        # Interaction state
        self.drag_position = None
        
        self.show()

    def center_on_screen(self):
        # Logic to center or place near cursor can go here
        # For now, let it appear where the capture happened or center
        pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self.current_opacity)
        painter.drawPixmap(0, 0, self.original_pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def wheelEvent(self, event):
        # Adjust opacity
        angle = event.angleDelta().y()
        if angle > 0:
            self.current_opacity = min(1.0, self.current_opacity + 0.1)
        else:
            self.current_opacity = max(0.2, self.current_opacity - 0.1)
        self.update()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_image)
        menu.addAction(save_action)
        
        copy_action = QAction("Copy to Clipboard", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        menu.addAction(copy_action)
        
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        
        menu.exec(pos)

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            self.original_pixmap.save(file_path, "PNG")

    def copy_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setPixmap(self.original_pixmap)
