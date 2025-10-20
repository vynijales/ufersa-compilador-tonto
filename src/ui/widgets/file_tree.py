import os

from PyQt5.QtWidgets import (QTreeView, QFileSystemModel, QVBoxLayout, QWidget, QMessageBox)
from PyQt5.QtCore import QDir, pyqtSignal, QTimer

class FileTreeWidget(QWidget):
    """Widget de árvore de arquivos para navegação"""
    fileDoubleClicked = pyqtSignal(str)
    folderDoubleClicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_root_path = QDir.currentPath()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Criar o modelo do sistema de arquivos
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        # Filtrar para mostrar apenas diretórios e arquivos .tonto
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)
        self.model.setNameFilters(["*.tonto"])
        self.model.setNameFilterDisables(False)
        
        # Criar a tree view
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.current_root_path))
        self.tree.setAnimated(True)
        self.tree.setSortingEnabled(True)
        
        # Configurar colunas
        self.tree.setColumnWidth(0, 250)  # Nome
        self.tree.hideColumn(1)  # Tamanho
        self.tree.hideColumn(2)  # Tipo
        self.tree.hideColumn(3)  # Data de modificação
        
        # Conectar sinais
        self.tree.doubleClicked.connect(self.on_double_click)
        
        layout.addWidget(self.tree)
        
    def set_root_path(self, path):
        """Define o caminho raiz para a árvore"""
        if os.path.exists(path):
            self.current_root_path = path
            self.tree.setRootIndex(self.model.index(path))
            # Expandir a pasta raiz após um pequeno delay
            QTimer.singleShot(100, lambda: self._expand_root(path))
            
    def _expand_root(self, path):
        """Expande o diretório raiz"""
        root_index = self.model.index(path)
        if root_index.isValid():
            self.tree.expand(root_index)
            
    def get_current_path(self):
        """Retorna o caminho do item selecionado"""
        index = self.tree.currentIndex()
        if index.isValid():
            return self.model.filePath(index)
        return None
        
    def on_double_click(self, index):
        """Manipula duplo clique em itens"""
        path = self.model.filePath(index)
        if os.path.isfile(path) and path.endswith('.tonto'):
            self.fileDoubleClicked.emit(path)
        elif os.path.isdir(path):
            # Alternar expansão/colapso da pasta
            if self.tree.isExpanded(index):
                self.tree.collapse(index)
            else:
                self.tree.expand(index)
            self.folderDoubleClicked.emit(path)
    
    def refresh(self):
        """Atualiza a visualização da árvore - método simplificado"""
        # A maneira mais confiável é redefinir o root path
        current_path = self.current_root_path
        self.tree.setRootIndex(self.model.index(""))
        QTimer.singleShot(10, lambda: self.tree.setRootIndex(self.model.index(current_path)))
