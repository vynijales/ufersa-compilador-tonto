from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QPushButton, QLabel, QFileDialog, 
                             QMenuBar, QMenu, QAction)

from ui.widgets import TokenTable, StatisticsWidget, ChartWidget, CloseableTabWidget, TokenDetailsTable, FileTreeWidget

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
        self.main_splitter = QSplitter(Qt.Horizontal)

        left_widget = self.create_left_panel()
        middle_widget = self.create_middle_panel()
        right_widget = self.create_right_panel()

        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(middle_widget)
        self.main_splitter.addWidget(right_widget)

        main_layout.addWidget(self.main_splitter)
        
        # Configurar a barra de menu
        self.setup_menu_bar()

    def setup_menu_bar(self):
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu('Arquivo')
        
        self.open_file_action = QAction('Abrir Arquivo', self)
        self.open_file_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(self.open_file_action)
        
        self.open_folder_action = QAction('Abrir Pasta', self)
        self.open_folder_action.triggered.connect(self.open_folder_dialog)
        file_menu.addAction(self.open_folder_action)
        
        file_menu.addSeparator()
        
        self.close_tab_action = QAction('Fechar Aba Atual', self)
        self.close_tab_action.triggered.connect(self.close_current_tab)
        self.close_tab_action.setEnabled(False)
        file_menu.addAction(self.close_tab_action)
        
        self.clear_all_action = QAction('Limpar Tudo', self)
        self.clear_all_action.triggered.connect(self.allCleared.emit)
        self.clear_all_action.setEnabled(False)
        file_menu.addAction(self.clear_all_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Sair', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Análise
        analysis_menu = menubar.addMenu('Análise')
        
        self.analyze_current_action = QAction('Analisar Arquivo Atual', self)
        self.analyze_current_action.triggered.connect(self.analyzeCurrentRequested.emit)
        self.analyze_current_action.setEnabled(False)
        analysis_menu.addAction(self.analyze_current_action)
        
        self.analyze_all_action = QAction('Analisar Todos os Arquivos', self)
        self.analyze_all_action.triggered.connect(self.analyzeAllRequested.emit)
        self.analyze_all_action.setEnabled(False)
        analysis_menu.addAction(self.analyze_all_action)

    def create_left_panel(self):
        widget = QWidget()
        self.left_layout = QVBoxLayout(widget)
        self.left_layout.addWidget(QLabel("Árvore de Arquivos"))
        widget.setMaximumWidth(300)

        # Área do file tree
        self.file_tree = FileTreeWidget()
        self.left_layout.addWidget(self.file_tree)
        return widget

    def create_middle_panel(self):
        widget = QWidget()
        self.middle_layout = QVBoxLayout(widget)

        # Área de abas
        self.tab_widget = CloseableTabWidget(close_callback=self.on_tab_closed)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.middle_layout.addWidget(self.tab_widget)

        return widget

    def create_right_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        widget.setMaximumWidth(500)
        widget.setMinimumWidth(300)

        self.token_table = TokenTable()
        layout.addWidget(QLabel("Tokens Encontrados"))
        layout.addWidget(self.token_table)

        self.stats_widget = StatisticsWidget()
        layout.addWidget(QLabel("Estatísticas"))
        layout.addWidget(self.stats_widget)

        self.details_table = TokenDetailsTable()
        layout.addWidget(self.details_table)

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
            # self.file_label.setText(f"Arquivo atual: {display_name}")
            self.analyzeCurrentRequested.emit()
        else:
            pass
            # self.file_label.setText("Nenhum arquivo selecionado")

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
        self.close_tab_action.setEnabled(has_tabs)
        self.clear_all_action.setEnabled(has_tabs)
        self.analyze_current_action.setEnabled(has_tabs)
        self.analyze_all_action.setEnabled(has_tabs)

    def clear_all_tabs(self):
        self.tab_widget.clear()
        self.update_buttons_state()
