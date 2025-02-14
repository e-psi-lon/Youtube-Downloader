import os
from io import BytesIO
from PySide6.QtCore import QThread, Signal
from ffmpeg import Progress, FFmpeg  # type: ignore
from pytubefix import YouTube, Stream
from ..models.format import Format
from ..core.constants import Formats


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
			if self.format.extension != "mp4":
				self.convert_video(video.title, buffer.getvalue(), Formats[self.format.name].value, self.path)
			else:
				with open(video_path, "wb") as file:
					file.write(buffer.getvalue())
			self.progress_updated.emit(0)
			self.finished.emit()
		except Exception as e:
			self.error.emit(str(e))
		finally:
			self.status_updated.emit("Download complete!")
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

