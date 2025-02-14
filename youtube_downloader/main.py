#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from typing import Optional
from PySide6.QtWidgets import QPushButton, QLabel, QFileDialog, \
	QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QObject
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout

from .core.constants import Formats
from .workers.video_data import DownloadWorker
from .workers.preview_worker import PreviewWorker
from .components import PreviewSection, ControlSection, ProgressSection, MessageBox 

from .core.state import AppState
from .core.events import EventBus


def format_time(seconds: int) -> str:
	"""
	Converts a time duration from seconds into a human-readable string format.

	Parameters
	----------
	seconds : int
		The time duration in seconds.

	Returns
	-------
		str
			A string representing the time duration in days, hours, minutes, and seconds.
			The format will include only the non-zero time units, e.g., "1 day 2 hours 3 minutes 4 seconds".
	"""
	days = seconds // (24 * 3600)
	seconds %= (24 * 3600)
	hours = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60
	time_elements = []
	if days > 0:
		time_elements.append(f"{days} day{'s' if days > 1 else ''}")
	if hours > 0:
		time_elements.append(f"{hours} hour{'s' if hours > 1 else ''}")
	if minutes > 0:
		time_elements.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
	if seconds > 0:
		time_elements.append(f"{seconds} second{'s' if seconds > 1 else ''}")
	return " ".join(time_elements)


class YouTubeDownloader(QWidget):
	def __init__(self):
		super().__init__()
		self.state = AppState(os.getcwd())
		self.event_bus = EventBus()
		
		# Initialize components
		self.preview_section = PreviewSection(self)
		self.control_section = ControlSection(self)
		self.progress_section = ProgressSection(self)
		
		self.worker = None
		self.preview_worker = None
		
		self.init_ui()
		self.connect_signals()
		
	def init_ui(self):
		layout = QVBoxLayout()
		layout.setSpacing(10)
		
		layout.addWidget(self.control_section)
		# layout.addWidget(self.progress_section)
		layout.addWidget(self.preview_section)
		
		self.setLayout(layout)
		self.setMinimumSize(800, 400)
		
	def connect_signals(self):
		self.control_section.preview_clicked.connect(self.preview_video)
		self.control_section.download_clicked.connect(self.start_download)
		# self.control_section.directory_changed.connect(self.update_directory)


	def choose_directory(self) -> None:
		self.state.update(path=QFileDialog.getExistingDirectory(self, "Select Directory"))

	def preview_video(self) -> None:
		self.preview_worker = PreviewWorker(self.control_section.url_entry.text())
		self.preview_worker.finished.connect(self.update_preview)
		self.preview_worker.error.connect(self.on_preview_error)
		self.preview_worker.start()

	def on_preview_error(self, error_message: str) -> None:
		self.show_message_box(QMessageBox.Icon.Critical, self, "Error", error_message)

	def start_download(self) -> None:
		self.set_widgets_enabled(False)
		
		self.worker = DownloadWorker(
			self.url_entry.text(),
			self.path,
			Formats[self.format_combo.currentText()].value
		)

		def set_progress_visible(visible: bool) -> None:
			self.progress_bar.setVisible(visible)
			self.status_label.setVisible(visible)
		
		self.worker.finished.connect(self.on_download_complete)
		self.worker.error.connect(self.on_download_error)
		self.worker.finished.connect(lambda: self.set_widgets_enabled(True))
		self.worker.error.connect(lambda: self.set_widgets_enabled(True))
		self.worker.progress_updated.connect(self.progress_bar.setValue)
		self.worker.status_updated.connect(self.status_label.setText)
		self.worker.visibility_changed.connect(set_progress_visible)
		self.worker.start()
		

	def show_message_box(self, 
					message_type: QMessageBox.Icon = QMessageBox.Icon.Information,
					parent: Optional[QWidget] = None,
					title: str= "", 
					message: str =""
					) -> None:
		dialog = MessageBox(
			parent=self if parent is None else parent,
			title=title,
			message=message,
			message_level=message_type
		)
		dialog.exec()

	def set_widgets_enabled(self, enabled: bool) -> None:
		for widget in [self.url_entry, self.download_button, self.directory_button,
					self.preview_button, self.format_combo]:
			widget.setEnabled(enabled)

	def on_download_complete(self) -> None:
		self.show_message_box(QMessageBox.Icon.Information, self, "Download Complete", 
							"The video has been downloaded successfully!")

	def on_download_error(self, error_message: str) -> None:
		self.show_message_box(QMessageBox.Icon.Critical, self, "Error", error_message)

	def make_label_selectable(self, widget: QWidget | QObject) -> None:
		"""
		Makes the text of a QLabel widget selectable by mouse and keyboard.

		Parameters
		----------
		widget : QWidget | QObject
			The widget whose text will be made selectable.
		"""
		if isinstance(widget, QLabel) and not isinstance(widget.parent(), QPushButton):
			widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
			widget.setCursor(Qt.CursorShape.IBeamCursor)
		for child in widget.children():
			self.make_label_selectable(child)


_app: QApplication
_ex: YouTubeDownloader

def main() -> int:
	"""
	The main function that initializes and runs the YouTube Downloader application.

	Returns
	-------
	int
		The exit status code of the application.
	"""
	try:
		import logging
		logging.basicConfig(filename='error.log', level=logging.ERROR)
		app = QApplication(sys.argv)
		app.setApplicationName("YouTube Downloader")
		app.setWindowIcon(QIcon("youtube_downloader/assets/icon.png"))
		ex = YouTubeDownloader()
		global _app, _ex
		_app = app
		_ex = ex
		ex.show()
		return app.exec()
	except Exception as e:
		logging.exception(e)
		MessageBox(title="Error", message="An unexpected error occurred. Please try again.", message_level=QMessageBox.Icon.Critical).exec()
		return 1

if __name__ == '__main__':
	sys.exit(main())
