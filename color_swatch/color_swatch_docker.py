from krita import DockWidget, Krita
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableView
from PyQt5.QtGui import QColor, QPainter, QPixmap, QBrush, QImage
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QModelIndex, QTimer

class BrushPreviewDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brush Preview")
        self.setObjectName("brush_preview_docker")

        # Main widget setup
        self.main_widget = QWidget()
        self.main_widget.setLayout(QVBoxLayout())
        self.main_widget.layout().setContentsMargins(2, 2, 2, 2)

        # Preview label with fixed size
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(15, 15)
        self.setMinimumSize(20, 20)
        self.main_widget.layout().addWidget(self.preview_label)
        self.setWidget(self.main_widget)

        # Initialize states
        self.current_color = QColor(0, 0, 0)
        self.last_erase_mode = False
        self.checker_image = self.create_checker_image()

        # Setup monitoring
        self.setup_event_hooks()
        self.update_display()

        # Fallback timer for color updates
        self.fallback_timer = QTimer()
        self.fallback_timer.timeout.connect(self.update_color_from_view)
        self.fallback_timer.start(500)  # Check every ###ms as fallback

    def create_checker_image(self):
        """Create a transparent checkerboard pattern"""
        img = QImage(16, 16, QImage.Format_ARGB32)
        img.fill(Qt.transparent)
        painter = QPainter(img)
        painter.fillRect(0, 0, 8, 8, QColor(200, 200, 200))
        painter.fillRect(8, 8, 8, 8, QColor(200, 200, 200))
        painter.end()
        return img

    def setup_event_hooks(self):
        """Set up event listeners for color and erase mode changes"""
        app = Krita.instance()

        # Connect to erase action if available
        self.erase_action = app.action("erase_action")
        if self.erase_action:
            self.erase_action.toggled.connect(self.on_erase_toggled)

        # Try to connect to palette box for color changes
        try:
            window = app.activeWindow()
            if window:
                qwin = window.qwindow()
                palette_box = qwin.findChild(QTableView, 'paletteBox')
                if palette_box:
                    palette_box.selectionModel().currentChanged.connect(self.on_color_changed)
        except:
            pass

        # Monitor window changes to re-establish connections
        app.notifier().windowCreated.connect(self.on_window_changed)

    def on_window_changed(self):
        """Re-establish connections when window changes"""
        self.setup_event_hooks()
        self.update_color_from_view()

    @pyqtSlot(QModelIndex, QModelIndex)
    def on_color_changed(self, current, previous):
        """Handle color changes from palette"""
        self.update_color_from_view()

    def update_color_from_view(self):
        """Update color from active view"""
        try:
            window = Krita.instance().activeWindow()
            if window and window.activeView():
                view = window.activeView()
                fg_color = view.foregroundColor()
                if fg_color:
                    self.current_color = fg_color.colorForCanvas(None)
                    self.update_display()
        except:
            pass

    @pyqtSlot(bool)
    def on_erase_toggled(self, state):
        """Handle erase mode toggles"""
        self.last_erase_mode = state
        self.update_display()

    def update_display(self):
        """Update the preview display"""
        try:
            size = self.preview_label.size()
            pixmap = QPixmap(size)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            if self.last_erase_mode:
                brush = QBrush(self.checker_image)
                painter.fillRect(0, 0, size.width(), size.height(), brush)
            else:
                painter.fillRect(0, 0, size.width(), size.height(), self.current_color)
            painter.end()

            self.preview_label.setPixmap(pixmap)
        except:
            pass

    def canvasChanged(self, canvas):
        """Required override"""
        pass
