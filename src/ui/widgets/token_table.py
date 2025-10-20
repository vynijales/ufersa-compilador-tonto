
from PyQt5.QtWidgets import (QTreeWidget)
from PyQt5.QtCore import pyqtSignal

class TokenTable(QTreeWidget):
    tokenDoubleClicked = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setHeaderLabels(['Linha', 'Tipo', 'Valor'])
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_item_double_clicked(self, item, column):
        line_number = int(item.text(0))
        token_value = item.text(2)
        self.tokenDoubleClicked.emit(line_number, token_value)

