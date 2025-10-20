from PyQt5.QtWidgets import (QTreeWidget)

class TokenDetailsTable(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setHeaderLabels(['Tipo', 'Quantidade', 'Percentual'])
