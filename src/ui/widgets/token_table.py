
from PyQt5.QtWidgets import (QTreeWidget)
from PyQt5.QtCore import pyqtSignal

class TokenTable(QTreeWidget):
    tokenDoubleClicked = pyqtSignal(int, int, str)

    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHeaderLabels(['Linha', 'Posição', 'Tipo', 'Valor'])
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_item_double_clicked(self, item, column):
        line_number = int(item.text(0))
        token_pos = int(item.text(1))
        token_value = item.text(3)
        self.tokenDoubleClicked.emit(line_number, token_pos, token_value)
