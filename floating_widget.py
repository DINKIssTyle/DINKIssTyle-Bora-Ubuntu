from PyQt6.QtWidgets import QWidget, QMenu, QApplication, QFileDialog, QPushButton, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint, QRect, QEvent, QTimer
from PyQt6.QtGui import QPixmap, QAction, QPainter, QColor, QGuiApplication, QCursor, QKeySequence, QShortcut

class FloatingWidget(QWidget):
    def __init__(self, pixmap: QPixmap, geometry: QRect = None):
        super().__init__()
        self.original_pixmap = pixmap
        
        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMouseTracking(True) 
        
        # Shortcuts for closing
        self.shortcut_close = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcut_close.activated.connect(self.close)
        
        self.shortcut_quit = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut_quit.activated.connect(self.close)
        
        # Layout setup for shadow
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20) # Margins for shadow
        
        # Image Label
        self.image_label = QLabel(self)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        # Mouse tracking on label too so events pass through or we handle them on parent
        self.image_label.setMouseTracking(True)
        self.image_label.installEventFilter(self)
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 5)
        self.image_label.setGraphicsEffect(shadow)
        
        self.layout.addWidget(self.image_label)
        
        # Prepare geometry
        if geometry:
            # Adjust geometry to account for margins (window needs to be bigger than capture)
            margins = self.layout.contentsMargins()
            new_rect = geometry.adjusted(
                -margins.left(), 
                -margins.top(), 
                margins.right(), 
                margins.bottom()
            )
            self.target_geometry = new_rect
        else:
            self.target_geometry = None
            
        # Close Button
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5f56;
                color: white;
                border-radius: 12px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff3b30;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.hide()
        # Raise button to be above label
        self.close_btn.raise_()
        
        # Interaction state
        self.drag_position = None
        self.resizing = False
        self.resize_edge = None
        self.resize_margin = 10 # detection margin (inside window, outside label maybe?)
        
        # Install event filter to track hover for close button
        self.installEventFilter(self)

        self.show()
        
        # Delayed initialization
        QTimer.singleShot(100, self.apply_geometry_and_raise)

    def apply_geometry_and_raise(self):
        if self.target_geometry:
            print(f"DEBUG: Placing at {self.target_geometry}")
            self.setGeometry(self.target_geometry)
        else:
            print("DEBUG: No geometry, centering")
            margins = self.layout.contentsMargins()
            w = self.original_pixmap.width() + margins.left() + margins.right()
            h = self.original_pixmap.height() + margins.top() + margins.bottom()
            self.resize(w, h)
            self.center_on_screen()

        self.raise_()
        self.activateWindow()

    def center_on_screen(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def eventFilter(self, obj, event):
        if obj == self or obj == self.image_label:
            if event.type() == QEvent.Type.Enter:
                self.close_btn.show()
                self.update_close_btn_pos()
            elif event.type() == QEvent.Type.Leave:
                # Need careful check: if leaving window, hide. If moving between label and window, don't hide.
                # Simplest: check if global mouse is inside window geometry
                local_pos = self.mapFromGlobal(QCursor.pos())
                if not self.rect().contains(local_pos):
                    self.close_btn.hide()
            elif event.type() == QEvent.Type.Resize:
                self.update_close_btn_pos()
            
            # Forward interactions if they happened on label -> to window processing
            # Actually, we handle mouse events in FloatingWidget methods, and events bubble up if ignored.
            # But widgets consume mouse events by default? QLabel usually doesn't consume click unless links.
                
        return super().eventFilter(obj, event)
        
    def update_close_btn_pos(self):
        # Position top-right relative to the IMAGE, not the window (margin)
        margins = self.layout.contentsMargins()
        # x = window width - margin_right - button_width - padding
        self.close_btn.move(self.width() - margins.right() - 30, margins.top() + 6)

    def get_resize_edge(self, pos):
        # Allow resizing from the margin area
        r = self.rect()
        m = self.resize_margin
        # Also include the shadow margin area as resize handle?
        # Actually proper resize handles should be the edges of the content? Or the edges of the window?
        # Let's say edges of the window (the shadow area)
        
        left = pos.x() <= m
        right = pos.x() >= r.width() - m
        top = pos.y() <= m
        bottom = pos.y() >= r.height() - m
        
        if top and left: return Qt.CursorShape.SizeFDiagCursor, 'tl'
        if top and right: return Qt.CursorShape.SizeBDiagCursor, 'tr'
        if bottom and left: return Qt.CursorShape.SizeBDiagCursor, 'bl'
        if bottom and right: return Qt.CursorShape.SizeFDiagCursor, 'br'
        if left: return Qt.CursorShape.SizeHorCursor, 'l'
        if right: return Qt.CursorShape.SizeHorCursor, 'r'
        if top: return Qt.CursorShape.SizeVerCursor, 't'
        if bottom: return Qt.CursorShape.SizeVerCursor, 'b'
        
        return None, None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            cursor, edge = self.get_resize_edge(event.pos())
            if edge:
                self.resizing = True
                self.resize_edge = edge
                self.drag_position = event.globalPosition().toPoint() 
            else:
                # Drag
                # We can use standard logic now that we are on XCB
                self.drag_position = event.globalPosition().toPoint() - self.pos()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        # Update cursor shape
        if not self.resizing and not (event.buttons() & Qt.MouseButton.LeftButton):
            cursor, _ = self.get_resize_edge(event.pos())
            self.setCursor(cursor if cursor else Qt.CursorShape.ArrowCursor)

        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.resizing:
                self.handle_resize(event.globalPosition().toPoint())
            elif self.drag_position:
                new_pos = event.globalPosition().toPoint() - self.drag_position
                self.move(new_pos)
            event.accept()

    def handle_resize(self, global_pos):
        diff = global_pos - self.drag_position 
        # For XCB simple logic approach (might jitter if laggy, but standard)
        # Actually better to use diff from previous drag_pos
        self.drag_position = global_pos # update for next step
        
        # logic needs to be delta based
        #Wait, drag_position was Global Pos.
        # diff is delta vector.
        
        # But previous logic was: diff = global_pos - start_drag_pos
        # Let's use delta.
        # Store prev_global_pos instead of drag_position in dragging?
        
        # Let's fix handle_resize to use delta from last event
        # Logic matches standard Qt simple resize
        
        pass # To fully implement, we need careful delta.
        # Simpler: just use startSystemMove/Resize if on Wayland? But we forced XCB.
        
        # Re-implementing manual resize correctly:
        geo = self.geometry()
        edge = self.resize_edge
        
        # Note: diff calculation above (global_pos - drag_position) is actually 
        # (Current Mouse) - (Mouse at Press). This is total delta. 
        # But I updated self.drag_position = global_pos at end. So it IS step delta.
        # Wait, lines 185: diff = global_pos - self.drag_position.
        # line 186: self.drag_position = global_pos.
        # Yes, this is step delta.
        
        delta_x = diff.x()
        delta_y = diff.y()
        
        if 'r' in edge:
            geo.setWidth(max(100, geo.width() + delta_x))
        if 'b' in edge:
            geo.setHeight(max(100, geo.height() + delta_y))
        if 'l' in edge:
            new_w = max(100, geo.width() - delta_x)
            if new_w != geo.width():
                geo.setLeft(geo.left() + delta_x)
        if 't' in edge:
            new_h = max(100, geo.height() - delta_y)
            if new_h != geo.height():
                geo.setTop(geo.top() + delta_y)
                
        self.setGeometry(geo)

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        self.resizing = False
        self.resize_edge = None

    def wheelEvent(self, event):
        # Adjust opacity
        angle = event.angleDelta().y()
        # Be careful, we apply opacity to *painter* usually.
        # Since we use QLabel + GraphicsEffect, setting window opacity effects everything including shadow.
        # Which is fine.
        val = self.windowOpacity()
        if angle > 0:
            val = min(1.0, val + 0.1)
        else:
            val = max(0.2, val - 0.1)
        self.setWindowOpacity(val)

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
