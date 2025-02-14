from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from ..core.constants import THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, STYLES
from ..models.video_data import VideoPreviewData

class PreviewSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_label = QLabel("Title: ")
        self.title_text = QLabel()
        self.duration_label = QLabel("Duration: ")
        self.duration_text = QLabel()
        self.description_label = QLabel("Description: ")
        self.description_text = QLabel()
        self.thumbnail_label = QLabel("Thumbnail:")
        self.thumbnail_image = QLabel()
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Text section
        text_section = QVBoxLayout()
        text_section.setSpacing(0)
        
        # Title
        title_layout = QVBoxLayout()
        title_layout.addWidget(self.title_label)
        self.title_text.setWordWrap(True)
        title_layout.addWidget(self.title_text)
        text_section.addLayout(title_layout)
        
        # Duration
        duration_layout = QVBoxLayout()
        duration_layout.addWidget(self.duration_label)
        duration_layout.addWidget(self.duration_text)
        text_section.addLayout(duration_layout)
        
        # Description
        description_layout = self._create_description_section()
        text_section.addLayout(description_layout)
        
        layout.addLayout(text_section, stretch=2)
        
        # Thumbnail section
        thumbnail_section = self._create_thumbnail_section()
        layout.addLayout(thumbnail_section, stretch=1)
        
        self.setLayout(layout)
        
    def _create_description_section(self):
        layout = QVBoxLayout()
        layout.addWidget(self.description_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(STYLES["scroll_area"])
        # ... rest of description section setup ...
        
        return layout
        
    def _create_thumbnail_section(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        layout.addWidget(self.thumbnail_label)
        
        self.thumbnail_image.setFixedSize(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)
        self.thumbnail_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.thumbnail_image)
        
        return layout
        
    def update_preview(self, data: VideoPreviewData):
        self.title_text.setText(data.title)
        self.duration_text.setText(data.duration)
        self.description_text.setText(data.description)
        
        pixmap = QPixmap()
        pixmap.loadFromData(data.thumbnail_data)
        self.thumbnail_image.setPixmap(
            pixmap.scaled(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, 
                        Qt.AspectRatioMode.KeepAspectRatio)
        )