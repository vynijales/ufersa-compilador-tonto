from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QBrush, QColor

class ErrorTable(QTreeWidget):
    errorDoubleClicked = pyqtSignal(int, int, str)

    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHeaderLabels(['Linha', 'Coluna', 'Caractere', 'Mensagem'])
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Configurar cores
        self.error_brush = QBrush(QColor('#FF6B6B'))  # Vermelho claro
        self.setAlternatingRowColors(True)

    def update_errors(self, errors):
        """Atualiza a tabela com a lista de erros"""
        print('ERROROROROROR:', errors)
        self.clear()
        
        for error in errors:
            item = QTreeWidgetItem([
                str(error.line),
                str(error.column),
                error.character,
                error.message
            ])
            
            # Aplicar cor vermelha ao item
            for column in range(4):
                item.setForeground(column, self.error_brush)
            
            self.addTopLevelItem(item)
        
        # Ajustar largura das colunas
        for column in range(4):
            self.resizeColumnToContents(column)

    def on_item_double_clicked(self, item, column):
        """Emite sinal quando um erro é clicado duas vezes"""
        line_number = int(item.text(0))
        column_pos = int(item.text(1))
        character = item.text(2)
        self.errorDoubleClicked.emit(line_number, column_pos, character)

    def clear_errors(self):
        """Limpa todos os erros da tabela"""
        self.clear()