from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLineEdit, 
							QComboBox)
from PySide6.QtCore import Signal, Qt
from ..core.constants import DEFAULT_URL, Formats

class ControlSection(QWidget):
	preview_clicked = Signal(str)  # Emits URL
	download_clicked = Signal(str, str)  # Emits URL and format
	directory_changed = Signal(str)  # Emits new directory path
	
	def __init__(self, parent=None):
		super().__init__(parent)
		self.url_entry = QLineEdit()
		self.preview_button = QPushButton("Preview")
		self.download_button = QPushButton("Download")
		self.directory_button = QPushButton("Choose Directory")
		self.format_combo = QComboBox()
		self.init_ui()
		self.connect_signals()
		
	def init_ui(self):
		button_bar = QHBoxLayout()
		self.url_entry.setPlaceholderText("Enter YouTube video URL")
		self.url_entry.setToolTip("Enter the URL of the YouTube video you want to download")
		self.url_entry.setText(DEFAULT_URL)
		url_layout = QHBoxLayout()
		url_layout.addWidget(self.url_entry)

		button_bar.setAlignment(Qt.AlignmentFlag.AlignHCenter)
		button_bar.setSpacing(50)
		button_bar.setContentsMargins(0, 0, 0, 0)

		self.preview_button.setToolTip("Preview the video information before downloading")
		button_bar.addWidget(self.preview_button)

		self.download_button.setToolTip("Download the video")
		button_bar.addWidget(self.download_button)

		self.directory_button.setToolTip("Choose the directory where you want to save the video")
		self.directory_button.setFixedWidth(110)
		button_bar.addWidget(self.directory_button)

		self.format_combo.addItems([formats.name for formats in Formats])
		self.format_combo.setToolTip("Select the format you want to download the video in")
		self.format_combo.setFixedWidth(75)
		button_bar.addWidget(self.format_combo)

	
	def connect_signals(self):
		self.preview_button.clicked.connect(self.preview_video)
		self.directory_button.clicked.connect(self.choose_directory)
		self.download_button.clicked.connect(self.start_download)