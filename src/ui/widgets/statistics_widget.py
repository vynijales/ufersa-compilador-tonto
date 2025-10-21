from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class StatisticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Labels para estatísticas
        self.total_tokens_label = QLabel("Total de tokens: 0")
        self.total_lines_label = QLabel("Total de linhas: 0")
        self.error_count_label = QLabel("Erros encontrados: 0")
        
        # Configurar fonte e cor para erros
        font = QFont()
        font.setBold(True)
        self.error_count_label.setFont(font)
        
        layout.addWidget(self.total_tokens_label)
        layout.addWidget(self.total_lines_label)
        layout.addWidget(self.error_count_label)
        
        # Adicionar espaçamento
        layout.addStretch()
        
        self.setLayout(layout)

    def update_statistics(self, token_count=0, line_count=0, error_count=0):
        """Atualiza as estatísticas exibidas"""
        self.total_tokens_label.setText(f"Total de tokens: {token_count}")
        self.total_lines_label.setText(f"Total de linhas: {line_count}")
        self.error_count_label.setText(f"Erros encontrados: {error_count}")
        
        # Mudar cor baseado na quantidade de erros
        if error_count > 0:
            self.error_count_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
        else:
            self.error_count_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

    def clear_statistics(self):
        """Limpa todas as estatísticas"""
        self.update_statistics(0, 0, 0)