from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QBrush, QColor
from typing import List, Any

class ErrorTable(QTreeWidget):
    errorDoubleClicked = pyqtSignal(int, int, str)

    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHeaderLabels(['Linha', 'Coluna', 'Tipo', 'Mensagem'])
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Configurar cores para diferentes tipos de erros
        self.lexical_error_brush = QBrush(QColor('#FF9800'))    # Laranja para erros léxicos
        self.syntactic_error_brush = QBrush(QColor('#FF5252'))  # Vermelho forte para erros sintáticos
        self.warning_brush = QBrush(QColor('#FFC107'))          # Amarelo para avisos
        
        self.setAlternatingRowColors(True)
        
        # Ajustar largura das colunas
        self.setColumnWidth(0, 60)   # Linha
        self.setColumnWidth(1, 60)   # Coluna
        self.setColumnWidth(2, 100)  # Tipo

    def update_errors(self, errors):
        """Atualiza a tabela com a lista de erros léxicos (compatibilidade com código antigo)"""
        self.clear()
        
        for error in errors:
            # Para erros léxicos do formato antigo
            character = getattr(error, 'character', '-')
            message = getattr(error, 'message', str(error))
            
            item = QTreeWidgetItem([
                str(error.line),
                str(error.column),
                character,
                message
            ])
            
            # Aplicar cor laranja para erros léxicos
            for column in range(4):
                item.setForeground(column, self.lexical_error_brush)
            
            self.addTopLevelItem(item)
        
        # Ajustar largura das colunas
        for column in range(4):
            self.resizeColumnToContents(column)

    def update_all_errors(self, lexical_errors: List[Any] = None, syntactic_errors: List[Any] = None):
        """
        Atualiza a tabela com erros léxicos e sintáticos
        
        Args:
            lexical_errors: Lista de erros léxicos
            syntactic_errors: Lista de erros sintáticos
        """
        self.clear()
        
        # Adicionar erros léxicos
        if lexical_errors:
            for error in lexical_errors:
                line = str(getattr(error, 'line', 0))
                column = str(getattr(error, 'column', 0))
                
                # Para erros léxicos, mostrar o caractere problemático
                character = getattr(error, 'character', '-')
                message = getattr(error, 'message', str(error))
                
                # Se houver sugestão, adicionar à mensagem
                if hasattr(error, 'suggestion') and error.suggestion:
                    message += f" | {error.suggestion}"
                
                # Criar item com tipo "LÉXICO"
                item = QTreeWidgetItem([line, column, 'LÉXICO', f"{character}: {message}"])
                
                for col in range(4):
                    item.setForeground(col, self.lexical_error_brush)
                
                self.addTopLevelItem(item)
        
        # Adicionar erros sintáticos
        if syntactic_errors:
            for error in syntactic_errors:
                line = str(getattr(error, 'line', 0))
                column = str(getattr(error, 'column', 0))
                message = getattr(error, 'message', str(error))
                
                # Se houver sugestão, adicionar à mensagem
                if hasattr(error, 'suggestion') and error.suggestion:
                    message += f" | {error.suggestion}"
                
                # Criar item com tipo "SINTÁTICO"
                item = QTreeWidgetItem([line, column, 'SINTÁTICO', message])
                
                for col in range(4):
                    item.setForeground(col, self.syntactic_error_brush)
                
                self.addTopLevelItem(item)
        
        # Ajustar largura das colunas
        for column in range(4):
            self.resizeColumnToContents(column)

    def on_item_double_clicked(self, item, column):
        """Emite sinal quando um erro é clicado duas vezes"""
        try:
            line_number = int(item.text(0))
            column_pos = int(item.text(1))
            message = item.text(3)
            self.errorDoubleClicked.emit(line_number, column_pos, message)
        except ValueError:
            # Ignorar se não conseguir converter para int
            pass

    def clear_errors(self):
        """Limpa todos os erros da tabela"""
        self.clear()
    
    def get_error_count(self) -> int:
        """Retorna o número total de erros"""
        return self.topLevelItemCount()
    
    def has_errors(self) -> bool:
        """Verifica se há erros na tabela"""
        return self.topLevelItemCount() > 0
