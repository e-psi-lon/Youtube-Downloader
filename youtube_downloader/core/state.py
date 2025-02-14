from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass

@dataclass
class AppState(QObject):
    path: str
    url: str = ""
    format: str = "MP4"
    is_downloading: bool = False
    
    state_changed = Signal()

    def __init__(self, path: str):
        super().__init__()  # Call QObject's __init__
        self.path = path
        self.url = ""
        self.format = "MP4"
        self.is_downloading = False

    def update(self, **kwargs):
        changed = False
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                setattr(self, key, value)
                changed = True
        if changed:
            self.state_changed.emit()