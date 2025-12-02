import os
import collections

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QApplication, QMessageBox, QTreeWidgetItem

from ui.controller import FilesHandler
from ui.view import MainView
from ui.widgets.code_editor import CodeEditor
from ui.widgets.file_tab import GraphTab, FileTab


class MainController:
    def __init__(self):
        self.app = QApplication([])
        self.files_handler = FilesHandler()
        self.view = MainView()

        self.setup_connections()
        self.setup_file_tree()
        self.view.show()

    def setup_connections(self):
        self.view.analyzeCurrentRequested.connect(self.analyze_current_file)
        self.view.analyzeAllRequested.connect(self.analyze_all_files)
        self.view.fileOpened.connect(self.open_file)
        self.view.folderOpened.connect(self.open_folder)
        self.view.tabClosed.connect(self.close_file)
        self.view.allCleared.connect(self.clear_all)
        self.view.token_table.tokenDoubleClicked.connect(self.navigate_to_token)
        self.view.error_table.errorDoubleClicked.connect(self.navigate_to_error)  # Adicionar conexão para erros

    def setup_file_tree(self):
        """Configura o file tree widget na interface"""
        # Adicionar file tree ao painel esquerdo
        self.view.file_tree.fileDoubleClicked.connect(self.open_file)
        self.view.file_tree.folderDoubleClicked.connect(self.on_folder_double_clicked)
        
        # Inserir o file tree no layout do painel esquerdo
        self.view.left_layout.insertWidget(0, self.view.file_tree)

    def on_folder_double_clicked(self, folder_path):
        """Manipula duplo clique em pastas - expande/contrai na árvore"""
        # A expansão/contração já é tratada no próprio FileTreeWidget
        pass

    def open_file(self, filename):
        filename = os.path.normpath(filename) # Padronizar o caminho usando /

        try:
            # Verificar se é um arquivo .tonto
            if not filename.endswith('.tonto'):
                if os.path.isfile(filename):
                    QMessageBox.information(
                        self.view, "Informação", 
                        "Apenas arquivos .tonto são suportados."
                    )
                return

            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            if filename not in self.files_handler.files:
                file_tab = FileTab(filename, content)
                self.files_handler.add_file(filename, file_tab)
                self.view.add_file_tab(file_tab)

                graph_name = f'Graph: {filename}'
                graph_tab = GraphTab(graph_name, content)
                self.files_handler.add_file(graph_name, graph_tab)
                self.view.add_file_tab(graph_tab)

                # Não alterar o root path do file tree, apenas garantir que está atualizado
                self.view.file_tree.refresh()
            else:
                self.select_existing_tab(filename)
        except Exception as e:
            QMessageBox.critical(self.view, "Erro", f"Erro ao ler arquivo: {str(e)}")

    def open_folder(self, folder_path):
        try:
            # Atualizar o file tree para mostrar a pasta selecionada como raiz
            self.view.file_tree.set_root_path(folder_path)
            
            # Buscar todos os arquivos .tonto recursivamente
            tonto_files = []
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith('.tonto'):
                        full_path = os.path.join(root, file)
                        full_path = os.path.normpath(full_path) # Padronizar o caminho usando /
                        tonto_files.append(full_path)
                        
                        # Abrir cada arquivo .tonto encontrado
                        self.open_single_file(full_path)

            if not tonto_files:
                QMessageBox.information(
                    self.view, "Informação", 
                    f"Nenhum arquivo .tonto encontrado em: {folder_path}"
                )
                return

            QMessageBox.information(
                self.view, "Sucesso",
                f"Carregados {len(tonto_files)} arquivos .tonto da pasta."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self.view, "Erro", 
                f"Erro ao abrir pasta: {str(e)}"
            )

    def open_single_file(self, file_path):
        """Abre um único arquivo sem mostrar múltiplas mensagens"""
        try:
            if file_path not in self.files_handler.files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                file_tab = GraphTab(file_path, content)
                self.files_handler.add_file(file_path, file_tab)
                self.view.add_file_tab(file_tab)
                
        except Exception as e:
            print(f"Erro ao abrir arquivo {file_path}: {str(e)}")

    def select_existing_tab(self, filename):
        display_name = os.path.basename(filename)
        for i in range(self.view.tab_widget.count()):
            if self.view.tab_widget.tabText(i) == display_name:
                self.view.tab_widget.setCurrentIndex(i)
                break

    def close_file(self, filename):
        display_name = filename
        for filepath, file_tab in self.files_handler.files.items():
            if file_tab.display_name == display_name:
                self.files_handler.remove_file(filepath)
                break
        # Atualizar o file tree para refletir as mudanças
        self.view.file_tree.refresh()

    def analyze_current_file(self):
        current_index = self.view.tab_widget.currentIndex()
        if current_index >= 0:
            display_name = self.view.tab_widget.tabText(current_index)
            # Encontrar o filename real baseado no display_name
            filename = None
            for filepath, file_tab in self.files_handler.files.items():
                if file_tab.display_name == display_name:
                    filename = filepath
                    break

            if filename:
                tokens, errors, syntactic_errors = self.files_handler.analyze_file(filename)  # Receber tokens, erros léxicos e sintáticos
                self.update_display(tokens, errors, syntactic_errors, display_name)  # Passar todos os erros

                file_tab = self.files_handler.files[filename]
                if isinstance(file_tab.editor, CodeEditor):
                    file_tab.editor.highlighter.set_tokens(tokens)
                    file_tab.editor.highlighter.rehighlight()

    def analyze_all_files(self):
        tokens, errors, syntactic_errors = self.files_handler.analyze_all_files()  # Receber tokens, erros léxicos e sintáticos
        self.update_display(tokens, errors, syntactic_errors, f"Todos os {len(self.files_handler.files)} arquivos")  # Passar todos os erros

        for file_tab in self.files_handler.files.values():
            file_tab.editor.highlighter.set_tokens(file_tab.tokens)
            file_tab.editor.highlighter.rehighlight()

    def update_display(self, tokens, errors, syntactic_errors, source_name):  # Adicionar parâmetros de erros
        self.update_token_table(tokens)
        self.update_error_table(errors, syntactic_errors) 
        self.update_statistics(tokens, errors, syntactic_errors, source_name)
        self.update_details_table(tokens)
    
    def update_token_table(self, tokens):
        self.view.token_table.clear()
        for token in tokens:
            item = QTreeWidgetItem([str(token.lineno), str(token.token_pos), token.type, token.value])
            self.view.token_table.addTopLevelItem(item)

    def update_error_table(self, lexical_errors, syntactic_errors):
        """Atualiza a tabela de erros com erros léxicos e sintáticos"""
        self.view.error_table.update_all_errors(lexical_errors, syntactic_errors)


    def update_statistics(self, tokens, errors, syntactic_errors, source_name):
        token_count = len(tokens)
        error_count = len(errors) + len(syntactic_errors)  # Soma de erros léxicos e sintáticos
        line_count = len(set(token.lineno for token in tokens))

        self.view.stats_widget.update_statistics(token_count, line_count, error_count)

    def update_details_table(self, tokens):
        self.view.details_table.clear()

        if tokens:
            token_counts = collections.Counter(token.type for token in tokens)
            total_tokens = len(tokens)

            for token_type, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_tokens) * 100
                item = QTreeWidgetItem(
                    [token_type, str(count), f"{percentage:.1f}%"])
                self.view.details_table.addTopLevelItem(item)

    def navigate_to_token(self, line_number, token_pos, token_value):
        current_editor = self.view.tab_widget.currentWidget()
        if not current_editor:
            return

        cursor = current_editor.textCursor()
        cursor.movePosition(cursor.Start)

        for _ in range(line_number - 1):
            cursor.movePosition(cursor.Down)
    
        cursor.setPosition(cursor.block().position() + token_pos - 1)
        cursor.setPosition(cursor.block().position() + token_pos - 1 + len(token_value), cursor.KeepAnchor)
        current_editor.setTextCursor(cursor)
        current_editor.setFocus()

    def navigate_to_error(self, line_number, column_pos, character):
        """Navega para a posição do erro no editor"""
        current_editor = self.view.tab_widget.currentWidget()
        if not current_editor:
            return

        cursor = current_editor.textCursor()
        cursor.movePosition(cursor.Start)

        # Mover para a linha do erro
        for _ in range(line_number - 1):
            cursor.movePosition(cursor.Down)
        
        # Mover para a coluna do erro
        cursor.setPosition(cursor.block().position() + column_pos - 1)
        
        # Selecionar o caractere problemático se existir
        if character:
            cursor.setPosition(cursor.block().position() + column_pos - 1 + len(character), cursor.KeepAnchor)
        
        current_editor.setTextCursor(cursor)
        current_editor.setFocus()
    
    def clear_all(self):
        self.files_handler.clear_files()
        self.view.clear_all_tabs()
        self.update_display([], [], [], "")  # Passar listas vazias de tokens e erros
        # Restaurar file tree para diretório atual
        self.view.file_tree.set_root_path(QDir.currentPath())
    
    def run(self):
        return self.app.exec_()
