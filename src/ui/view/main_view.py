from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton, QLabel, QFileDialog

from ui.widgets import TokenTable, StatisticsWidget, ChartWidget, CloseableTabWidget, TokenDetailsTable

class MainView(QMainWindow):
    analyzeCurrentRequested = pyqtSignal()
    analyzeAllRequested = pyqtSignal()
    fileOpened = pyqtSignal(str)
    folderOpened = pyqtSignal(str)
    tabClosed = pyqtSignal(str)
    allCleared = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analisador Léxico - Tonto Language")
        self.setGeometry(100, 100, 1600, 900)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)

        left_widget = self.create_left_panel()
        right_widget = self.create_right_panel()

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([800, 800])

        main_layout.addWidget(splitter)

    def create_left_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls_layout = QHBoxLayout()
        self.open_file_btn = QPushButton("Abrir Arquivo")
        self.open_folder_btn = QPushButton("Abrir Pasta")
        self.analyze_current_btn = QPushButton("Analisar Arquivo Atual")
        self.analyze_all_btn = QPushButton("Analisar Todos")
        self.close_tab_btn = QPushButton("Fechar Aba Atual")
        self.close_tab_btn.setEnabled(False)
        self.clear_all_btn = QPushButton("Limpar Tudo")
        self.clear_all_btn.setEnabled(False)
        self.file_label = QLabel("Nenhum arquivo selecionado")

        controls_layout.addWidget(self.open_file_btn)
        controls_layout.addWidget(self.open_folder_btn)
        controls_layout.addWidget(self.analyze_current_btn)
        controls_layout.addWidget(self.analyze_all_btn)
        controls_layout.addWidget(self.close_tab_btn)
        controls_layout.addWidget(self.clear_all_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.file_label)

        self.tab_widget = CloseableTabWidget(close_callback=self.on_tab_closed)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        layout.addLayout(controls_layout)
        layout.addWidget(self.tab_widget)

        self.open_file_btn.clicked.connect(self.open_file_dialog)
        self.open_folder_btn.clicked.connect(self.open_folder_dialog)
        self.analyze_current_btn.clicked.connect(
            self.analyzeCurrentRequested.emit)
        self.analyze_all_btn.clicked.connect(self.analyzeAllRequested.emit)
        self.close_tab_btn.clicked.connect(self.close_current_tab)
        self.clear_all_btn.clicked.connect(self.allCleared.emit)

        return widget

    def create_right_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.token_table = TokenTable()
        layout.addWidget(QLabel("Tokens Encontrados"))
        layout.addWidget(self.token_table)

        self.stats_widget = StatisticsWidget()
        layout.addWidget(QLabel("Estatísticas"))
        layout.addWidget(self.stats_widget)

        charts_layout = QHBoxLayout()
        self.chart_widget = ChartWidget()
        self.details_table = TokenDetailsTable()

        charts_layout.addWidget(self.chart_widget)
        charts_layout.addWidget(self.details_table)
        layout.addLayout(charts_layout)

        return widget

    def open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Selecionar arquivo .tonto", "", "Tonto files (*.tonto);;All files (*.*)"
        )
        if filename:
            self.fileOpened.emit(filename)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Selecionar pasta com arquivos .tonto")
        if folder:
            self.folderOpened.emit(folder)

    def add_file_tab(self, file_tab):
        self.tab_widget.addTab(file_tab.editor, file_tab.display_name)
        self.update_buttons_state()

    def close_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            filename = self.get_current_filename()
            self.tab_widget.removeTab(current_index)
            if filename:
                self.tabClosed.emit(filename)
            self.update_buttons_state()

    def get_current_filename(self):
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            return self.tab_widget.tabText(current_index)
        return None

    def on_tab_changed(self, index):
        if index >= 0:
            display_name = self.tab_widget.tabText(index)
            self.file_label.setText(f"Arquivo atual: {display_name}")
            self.analyzeCurrentRequested.emit()
        else:
            self.file_label.setText("Nenhum arquivo selecionado")

    def on_tab_closed(self, index):
        """Callback chamado quando uma aba é fechada via botão de fechar"""
        if index >= 0:
            filename = self.tab_widget.tabText(index)
            self.tab_widget.removeTab(index)
            if filename:
                self.tabClosed.emit(filename)
            self.update_buttons_state()

    def update_buttons_state(self):
        has_tabs = self.tab_widget.count() > 0
        self.close_tab_btn.setEnabled(has_tabs)
        self.clear_all_btn.setEnabled(has_tabs)

    def clear_all_tabs(self):
        self.tab_widget.clear()
        self.update_buttons_state()
