import os
import collections

from PyQt5.QtWidgets import (QApplication, QTreeWidgetItem, QMessageBox)

import matplotlib.pyplot as plt

from ui.controller import FilesHandler
from ui.widgets import FileTab
from ui.view import MainView

class MainController:
    def __init__(self):
        self.app = QApplication([])
        self.files_handler = FilesHandler()
        self.view = MainView()

        self.setup_connections()
        self.view.show()

    def setup_connections(self):
        self.view.analyzeCurrentRequested.connect(self.analyze_current_file)
        self.view.analyzeAllRequested.connect(self.analyze_all_files)
        self.view.fileOpened.connect(self.open_file)
        self.view.folderOpened.connect(self.open_folder)
        self.view.tabClosed.connect(self.close_file)
        self.view.allCleared.connect(self.clear_all)
        self.view.token_table.tokenDoubleClicked.connect(self.navigate_to_token)

    def open_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            if filename not in self.files_handler.files:
                file_tab = FileTab(filename, content)
                self.files_handler.add_file(filename, file_tab)
                self.view.add_file_tab(file_tab)
            else:
                self.select_existing_tab(filename)

        except Exception as e:
            QMessageBox.critical(
                self.view, "Erro", f"Erro ao ler arquivo: {str(e)}")

    def open_folder(self, folder_path):
        tonto_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.tonto'):
                    tonto_files.append(os.path.join(root, file))

        if not tonto_files:
            QMessageBox.information(
                self.view, "Informação", "Nenhum arquivo .tonto encontrado.")
            return

        for file_path in tonto_files:
            self.open_file(file_path)

        QMessageBox.information(self.view, "Sucesso",
                                f"Carregados {len(tonto_files)} arquivos.")

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
                tokens = self.files_handler.analyze_file(filename)
                self.update_display(tokens, display_name)

                file_tab = self.files_handler.files[filename]
                file_tab.editor.highlighter.set_tokens(tokens)
                file_tab.editor.highlighter.rehighlight()

    def analyze_all_files(self):
        tokens = self.files_handler.analyze_all_files()
        self.update_display(
            tokens, f"Todos os {len(self.files_handler.files)} arquivos")

        for file_tab in self.files_handler.files.values():
            file_tab.editor.highlighter.set_tokens(file_tab.tokens)
            file_tab.editor.highlighter.rehighlight()

    def update_display(self, tokens, source_name):
        self.update_token_table(tokens)
        self.update_statistics(tokens, source_name)
        self.update_chart(tokens)
        self.update_details_table(tokens)

    def update_token_table(self, tokens):
        self.view.token_table.clear()
        for token in tokens:
            item = QTreeWidgetItem(
                [str(token.lineno), token.type, token.value])
            self.view.token_table.addTopLevelItem(item)

    def update_statistics(self, tokens, source_name):
        stats_text = f"📊 ANÁLISE LÉXICA - {source_name.upper()}\n"
        stats_text += "=" * 50 + "\n"

        if tokens:
            stats_text += f"• Total de tokens: {len(tokens)}\n"
            stats_text += f"• Linhas processadas: {tokens[-1].lineno if tokens else 0}\n"
            stats_text += f"• Tipos únicos de tokens: {len(set(token.type for token in tokens))}\n"

            token_counts = collections.Counter(token.type for token in tokens)
            most_common = token_counts.most_common(1)[0]
            stats_text += f"• Token mais frequente: {most_common[0]} ({most_common[1]} ocorrências)\n"
        else:
            stats_text += "Nenhum token encontrado."

        self.view.stats_widget.setText(stats_text)

    def update_chart(self, tokens):
        self.view.chart_widget.ax.clear()

        if not tokens:
            self.view.chart_widget.ax.text(0.5, 0.5, 'Nenhum dado\npara exibir',
                                           horizontalalignment='center', verticalalignment='center',
                                           transform=self.view.chart_widget.ax.transAxes,
                                           fontsize=12, color='gray')
            self.view.chart_widget.ax.set_facecolor('#f0f0f0')
        else:
            token_counts = collections.Counter(token.type for token in tokens)
            labels = [
                f"{token_type}\n({count})" for token_type, count in token_counts.most_common()]
            sizes = list(token_counts.values())

            colors = plt.cm.Pastel1(range(len(labels)))
            self.view.chart_widget.ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                          startangle=90, colors=colors, textprops={'fontsize': 8})

        self.view.chart_widget.ax.set_title(
            'Distribuição de Tokens', pad=20, fontweight='bold')
        self.view.chart_widget.draw()

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

    def navigate_to_token(self, line_number, token_value):
        current_editor = self.view.tab_widget.currentWidget()
        if not current_editor:
            return

        cursor = current_editor.textCursor()
        cursor.movePosition(cursor.Start)

        for _ in range(line_number - 1):
            cursor.movePosition(cursor.Down)

        line_text = cursor.block().text()
        start_pos = line_text.find(token_value)

        if start_pos != -1:
            cursor.setPosition(cursor.block().position() + start_pos)
            cursor.setPosition(cursor.block().position() +
                               start_pos + len(token_value), cursor.KeepAnchor)
            current_editor.setTextCursor(cursor)
            current_editor.setFocus()

    def clear_all(self):
        self.files_handler.clear_files()
        self.view.clear_all_tabs()
        self.update_display([], "")

    def run(self):
        return self.app.exec_()
