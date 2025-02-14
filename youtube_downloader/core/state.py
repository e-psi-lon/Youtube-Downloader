from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal

@dataclass
class AppState(QObject):
    path: str = ""
    url: str = ""
    format: str = "MP4"
    is_downloading: bool = False
    
    state_changed = Signal()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.state_changed.emit()