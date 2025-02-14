from enum import Enum
from ..models.format import Format

THUMBNAIL_WIDTH = 300
THUMBNAIL_HEIGHT = 210
DESCRIPTION_MAX_LENGTH = 100
DEFAULT_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

class Formats(Enum):
    MP4 = Format("MP4", "mp4", "-c:v libx264 -c:a aac")
    AVI = Format("AVI", "avi", "-c:v libxvid -c:a mp3")
    MOV = Format("MOV", "mov", "-c:v libx264 -c:a aac")
    MP3 = Format("MP3", "mp3", "-c:a libmp3lame")
    OGG = Format("OGG", "ogg", "-c:a libvorbis")
    OPUS = Format("OPUS", "opus", "-c:a libopus")

STYLES = {
    "scroll_area": """
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
    """
}