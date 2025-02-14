from dataclasses import dataclass

@dataclass
class Format:
    name: str
    extension: str
    ffmpeg_args: str

    def __str__(self) -> str:
        return self.extension
    