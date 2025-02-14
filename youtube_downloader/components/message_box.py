from typing import Optional
from PySide6.QtWidgets import QPushButton, QLabel, QMessageBox, QWidget, \
    QDialog, QVBoxLayout, QHBoxLayout, QStyle
from PySide6.QtGui import QIcon

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
				return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)

