from dataclasses import dataclass

@dataclass
class VideoPreviewData:
    title: str
    duration: int
    description: str
    thumbnail_data: bytes