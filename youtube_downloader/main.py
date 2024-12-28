#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import Optional
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, \
	QMessageBox, QProgressBar, QComboBox, QHBoxLayout, QScrollArea, QDialog, QStyle
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QByteArray, QBuffer, QThread, QObject, Signal
from pytubefix import YouTube, Stream  # type: ignore
import requests
from ffmpeg import Progress, FFmpeg  # type: ignore

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
THUMBNAIL_WIDTH = 300
THUMBNAIL_HEIGHT = 210
DESCRIPTION_MAX_LENGTH = 100

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


@dataclass
class Format:
	"""
	Represents a video format with its extension and FFmpeg arguments.

	Attributes
	----------
	name : str
		The name of the format.
	extension : str
		The file extension of the format.
	ffmpeg_args : str
		The FFmpeg arguments used to convert the video to this format.
	"""
	name: str
	extension: str
	ffmpeg_args: str

	def __str__(self) -> str:
		return self.extension

@dataclass
class VideoPreviewData:
	"""
	Represents the data of a YouTube video preview.

	Attributes
	----------
	title : str
		The title of the video.
	duration : int
		The duration of the video in seconds.
	description : str
		The description of the video.
	thumbnail_data : bytes
		The binary data of the video thumbnail image.
	"""
	title: str
	duration: int
	description: str
	thumbnail_data: bytes

class PreviewWorker(QThread):
	"""
	A worker thread that retrieves the preview data of a YouTube video.

	Attributes
	----------
	url : str
		The URL of the YouTube video.
	"""
	finished = Signal(VideoPreviewData)
	error = Signal(str)
	
	def __init__(self, url: str) -> None:
		super().__init__()
		self.url = url
		
	def run(self) -> None:
		try:
			video = YouTube(self.url)
			response = requests.get(video.thumbnail_url)
			preview_data = VideoPreviewData(
				title=video.title,
				duration=video.length,
				description=video.description or "No description available",
				thumbnail_data=response.content
			)
			self.finished.emit(preview_data)
		except Exception as e:
			self.error.emit(str(e))

class DownloadWorker(QThread):
	"""
	A worker thread that downloads a YouTube video and optionally converts it to a different format.

	Attributes
	----------
	url : str
		The URL of the YouTube video.
	path : str
		The path where the video will be saved.
	format : Format
		The format in which the video will be downloaded.
	"""
	progress_updated = Signal(int)
	status_updated = Signal(str)
	visibility_changed = Signal(bool)
	finished = Signal()
	error = Signal(str)
	
	def __init__(self, url: str, path: str, file_format: Format) -> None:
		super().__init__()
		self.url = url
		self.path = path
		self.format = file_format
		def on_progress(stream: Stream, _: bytes, bytes_remaining: int) -> None:
			self.progress_updated.emit(int((stream.filesize - bytes_remaining) / stream.filesize * 100))
		self._on_progress_download = on_progress

	def run(self) -> None:
		self.status_updated.emit("Downloading video...")
		self.visibility_changed.emit(True)
		self.progress_updated.emit(0)
		try:
			video = YouTube(self.url, on_progress_callback=self._on_progress_download)
			stream = video.streams.filter(progressive=True, file_extension='mp4').first()
			video_path = os.path.join(self.path, f"{video.title}.mp4")
			buffer = BytesIO()
			stream.stream_to_buffer(buffer)
			buffer.seek(0)
			if self.format != "MP4":
				self.convert_video(video.title, buffer.getvalue(), Formats[self.format.name].value, self.path)
			else:
				with open(video_path, "wb") as file:
					file.write(buffer.getvalue())
			self.finished.emit()
		except Exception as e:
			self.error.emit(str(e))
		finally:
			self.progress_updated.emit(0)
			self.status_updated.emit("Download complete !")
			self.visibility_changed.emit(False)

	def convert_video(self, name: str, input_data: bytes, output_format: Format, path: str) -> None:
		"""
		Converts the video to the specified format using FFmpeg.

		Parameters
		----------
		name : str
			The name of the video file.
		input_data : bytes
			The binary data of the video file.
		output_format : Format
			The format to which the video will be converted.
		"""
		output_file = os.path.join(path, f"{name}.{output_format.extension}")
		self.status_updated.emit(f"Converting to {output_format}...")
		self.progress_updated.emit(0)
		try:
			process = FFmpeg().input("pipe:0").output(output_file)
			@process.on('progress')
			def on_progress(progress: Progress) -> None:
				self.progress_updated.emit(int(progress.size/len(input_data)*100))
			process.execute(input_data)
		except Exception as e:
			self.error.emit(f"Conversion failed: {str(e)}")

class MessageBox(QDialog):
	"""
	A simple message box dialog with an icon, title, and message.

	Attributes
	----------
	parent : Optional[QWidget]
		The parent widget of the dialog.
	title : str
		The title of the dialog.
	message : str
		The message text of the dialog.
	message_level : QMessageBox.Icon
		The icon level of the message dialog.
	"""
	def __init__(self, 
			  parent: Optional[QWidget] = None, 
			  title: str = "", 
			  message: str = "", 
			  message_level: QMessageBox.Icon = QMessageBox.Icon.Information
			) -> None:
		super().__init__(parent)
		self.setWindowTitle(title)
		self.setFixedSize(300, 100)
		
		layout = QVBoxLayout()
		
		icon_label = QLabel()
		icon = self._get_icon(message_level)
		if icon:
			icon_label.setPixmap(icon.pixmap(16, 16))
			layout.addWidget(icon_label)
		
		message_label = QLabel(message)
		layout.addWidget(message_label)
		
		button_layout = QHBoxLayout()
		button_layout.addStretch()

		ok_button = QPushButton("OK")
		ok_button.setMaximumWidth(100)
		ok_button.clicked.connect(self.accept)
		button_layout.addWidget(ok_button)
		
		button_layout.addStretch()
		layout.addLayout(button_layout)
		
		self.setLayout(layout)
	
	def _get_icon(self, message_level: QMessageBox.Icon) -> QIcon:
		style = self.style()
		match message_level:
			case QMessageBox.Icon.Information:
				return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
			case QMessageBox.Icon.Warning:
				return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
			case QMessageBox.Icon.Critical:
				return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
			case QMessageBox.Icon.Question:
				return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
			case _:
				raise ValueError("Invalid message level")

class Formats(Enum):
	"""
	An enumeration of video formats with their extension and FFmpeg arguments.
	"""
	MP4 = Format("MP4", "mp4", "-c:v libx264 -c:a aac")
	AVI = Format("AVI", "avi", "-c:v libxvid -c:a mp3")
	MOV = Format("MOV", "mov", "-c:v libx264 -c:a aac")
	MP3 = Format("MP3", "mp3", "-c:a libmp3lame")
	OGG = Format("OGG", "ogg", "-c:a libvorbis")
	OPUS = Format("OPUS", "opus", "-c:a libopus")

class YouTubeDownloader(QWidget):
	"""
	Main class of the application that provides a GUI for downloading YouTube videos
	in multiple formats and displaying video information.
	"""
	def __init__(self) -> None:
		super().__init__()
		self.path: str = os.getcwd()
		self.thumbnail_label: QLabel = QLabel("Thumbnail: ", self)
		self.thumbnail_image: QLabel = QLabel(self)
		self.description_text: QLabel = QLabel(self)
		self.duration_text: QLabel = QLabel(self)
		self.title_text: QLabel = QLabel(self)
		self.progress_bar: QProgressBar = QProgressBar(self)
		self.status_label: QLabel = QLabel("Ready", self)
		self.duration_label: QLabel = QLabel("Duration: ", self)
		self.title_label: QLabel = QLabel("Title: ", self)
		self.format_combo: QComboBox = QComboBox(self)
		self.directory_button: QPushButton = QPushButton("Choose Directory", self)
		self.download_button: QPushButton = QPushButton("Download", self)
		self.preview_button: QPushButton = QPushButton("Preview", self)
		self.url_entry: QLineEdit = QLineEdit(self)
		self.description_label: QLabel = QLabel("Description: ", self)
		self.worker: Optional[DownloadWorker] = None
		self.preview_worker: Optional[PreviewWorker] = None
		self.init_ui()

	def init_ui(self) -> None:
		self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

		layout = QVBoxLayout()

		button_bar = QHBoxLayout()
		self.url_entry.setPlaceholderText("Enter YouTube video URL")
		self.url_entry.setToolTip("Enter the URL of the YouTube video you want to download")
		self.url_entry.setText("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
		self.url_entry.setFixedWidth(700)
		layout.addWidget(self.url_entry)

		layout.addLayout(button_bar)
		button_bar.setAlignment(Qt.AlignmentFlag.AlignHCenter)
		button_bar.setSpacing(50)
		button_bar.setContentsMargins(0, 0, 0, 0)

		self.preview_button.setToolTip("Preview the video information before downloading")
		self.preview_button.clicked.connect(self.preview_video)
		button_bar.addWidget(self.preview_button)

		self.download_button.setToolTip("Download the video")
		self.download_button.clicked.connect(self.start_download)
		button_bar.addWidget(self.download_button)

		self.directory_button.setToolTip("Choose the directory where you want to save the video")
		self.directory_button.clicked.connect(self.choose_directory)
		self.directory_button.setFixedWidth(110)
		button_bar.addWidget(self.directory_button)

		self.format_combo.addItems([formats.name for formats in Formats])
		self.format_combo.setToolTip("Select the format you want to download the video in")
		self.format_combo.setFixedWidth(75)
		button_bar.addWidget(self.format_combo)

		progress_layout = QVBoxLayout()
	
		progress_layout.addWidget(self.status_label)
		self.status_label.setVisible(False)
		
		self.progress_bar.setMinimum(0)
		self.progress_bar.setMaximum(100)
		self.progress_bar.setValue(0)
		self.progress_bar.setTextVisible(True)
		self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.progress_bar.setVisible(False)
		self.progress_bar.setFixedWidth(400)
		progress_layout.addWidget(self.progress_bar)
		
		layout.addLayout(progress_layout)

		preview_layout = QHBoxLayout()
		preview_layout.setSpacing(0)
		layout.addLayout(preview_layout)
		text_preview_layout = QVBoxLayout()
		preview_layout.addLayout(text_preview_layout)

		title = QVBoxLayout()
		text_preview_layout.addLayout(title)
		title.addWidget(self.title_label)
		self.title_text = QLabel(self)
		self.title_text.setWordWrap(True)
		title.setContentsMargins(0, 10, 0, 10)
		title.addWidget(self.title_text)

		duration = QVBoxLayout()
		text_preview_layout.addLayout(duration)
		duration.addWidget(self.duration_label)
		self.duration_text = QLabel(self)
		duration.setContentsMargins(0, 10, 0, 10)
		duration.addWidget(self.duration_text)

		# Description with scroll area
		description_container = QVBoxLayout()
		description_container.setContentsMargins(0, 10, 0, 10)
		description_container.addWidget(self.description_label)
		
		# Create scroll area for description
		scroll_area = QScrollArea(self)
		scroll_area.setWidgetResizable(True)
		scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
		scroll_area.setStyleSheet("""
			QScrollArea {
				background-color: #3d3d3d;
				border: 1px solid #4d4d4d;
				border-radius: 5px;
			}
			
			QScrollArea > QWidget > QWidget {
				background-color: #3d3d3d;
			}
							
			QLabel {
				color: #ffffff;
			}
							
			QScrollBar:vertical {
				background: #6d6d6d;
				width: 10px;
				margin: 0px 0px 0px 0px;
			}
		""")

		
		description_widget = QWidget()
		description_layout = QVBoxLayout(description_widget)
		self.description_text = QLabel(self)
		self.description_text.setWordWrap(True)
		self.description_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
		description_layout.addWidget(self.description_text)
		
		scroll_area.setWidget(description_widget)
		scroll_area.setFixedHeight(100) 
		scroll_area.setFixedWidth(400)
		description_container.addWidget(scroll_area)
	

		text_preview_layout.addLayout(description_container)

		image_preview_layout = QVBoxLayout()
		preview_layout.addLayout(image_preview_layout)

		self.thumbnail_label = QLabel("Thumbnail: ", self)
		image_preview_layout.addWidget(self.thumbnail_label)

		self.thumbnail_image = QLabel(self)
		self.thumbnail_image.setPixmap(QPixmap("assets/youtube.png").scaled(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
		self.thumbnail_image.setFixedWidth(THUMBNAIL_WIDTH)
		self.thumbnail_image.setFixedHeight(THUMBNAIL_HEIGHT)
		image_preview_layout.addWidget(self.thumbnail_image)

		self.setLayout(layout)
		self.make_label_selectable(self)

	def choose_directory(self) -> None:
		self.path = QFileDialog.getExistingDirectory(self, "Select Directory")

	def preview_video(self) -> None:
		self.preview_worker = PreviewWorker(self.url_entry.text())
		self.preview_worker.finished.connect(self.update_preview)
		self.preview_worker.error.connect(self.on_preview_error)
		self.preview_worker.start()

	def update_preview(self, data: VideoPreviewData) -> None:
		self.title_text.setText(data.title)
		self.duration_text.setText(format_time(data.duration))
		
		self.description_text.setText(data.description)
			
		byte_array = QByteArray(data.thumbnail_data)
		buffer = QBuffer(byte_array)
		buffer.open(QBuffer.OpenModeFlag.ReadOnly)
		pixmap = QPixmap()
		pixmap.loadFromData(buffer.data())
		self.thumbnail_image.setPixmap(pixmap.scaled(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
		
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
		

def main() -> int:
	app = QApplication(sys.argv)
	app.setApplicationName("YouTube Downloader")
	app.setWindowIcon(QIcon("assets/icon.png"))
	ex = YouTubeDownloader()
	ex.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
	return app.exec()


if __name__ == '__main__':
	sys.exit(main())
