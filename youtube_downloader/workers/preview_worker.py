from PySide6.QtCore import QThread, Signal
from pytubefix import YouTube
import requests
from ..models.video_data import VideoPreviewData

class PreviewWorker(QThread):
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