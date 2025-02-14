# components/progress_section.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel

class ProgressSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress_bar = QProgressBar()
        self.status_label = QLabel()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        self.setVisible(False)
        
    def update_progress(self, value: int):
        self.progress_bar.setValue(value)
        
    def update_status(self, status: str):
        self.status_label.setText(status)