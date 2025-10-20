from PyQt5.QtWidgets import (QTextEdit)

class StatisticsWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

