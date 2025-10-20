import os
import collections
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QTabWidget, QTextEdit, QTreeWidget, QTreeWidgetItem,
                             QPushButton, QLabel, QFileDialog, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCharFormat, QColor, QFont, QSyntaxHighlighter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from lexer import lexer


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.token_colors = {
            'KEYWORD': QColor('blue'),
            'CLASS_IDENTIFIER': QColor('#ff0000'),
            'INSTANCE_IDENTIFIER': QColor('#ff8500'),
            'RELATION_IDENTIFIER': QColor('#ffcb00'),
            'CLASS_STEREOTYPE': QColor('#800080'),
            'RELATION_STEREOTYPE': QColor('#ff1493'),
            'META_ATTRIBUTES': QColor('#008080'),
            "SYMBOL": QColor('#a52a2a'),
            'NUMBER': QColor('#ff4500'),
            'NATIVE_TYPE': QColor('#00f050'),
            'USER_TYPE': QColor('#0050f0'),
            'COMMA': QColor('#000000'),
            'COMMENT': QColor('#444444'),
        }
        self.highlighting_rules = []

    def set_tokens(self, tokens):
        self.highlighting_rules.clear()

        for token in tokens:
            if token.type in self.token_colors:
                format = QTextCharFormat()
                format.setForeground(self.token_colors[token.type])
                self.highlighting_rules.append((token, format))

    def highlightBlock(self, text):
        for token, format in self.highlighting_rules:
            if token.lineno == self.currentBlock().blockNumber() + 1:
                start = text.find(token.value)
                if start >= 0:
                    self.setFormat(start, len(token.value), format)


class CodeEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Courier New", 10))
        self.highlighter = SyntaxHighlighter(self.document())


class TokenTable(QTreeWidget):
    tokenDoubleClicked = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setHeaderLabels(['Linha', 'Tipo', 'Valor'])
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_item_double_clicked(self, item, column):
        line_number = int(item.text(0))
        token_value = item.text(2)
        self.tokenDoubleClicked.emit(line_number, token_value)


class StatisticsWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)


class TokenDetailsTable(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setHeaderLabels(['Tipo', 'Quantidade', 'Percentual'])


class ChartWidget(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(6, 4), dpi=80)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)


class FileTab:
    def __init__(self, filename, content):
        self.filename = filename
        self.display_name = os.path.basename(filename)
        self.editor = CodeEditor()
        self.editor.setText(content)
        self.tokens = []


class AnalysisModel:
    def __init__(self):
        self.files = {}
        self.current_tokens = []

    def add_file(self, filename, file_tab):
        self.files[filename] = file_tab

    def remove_file(self, filename):
        if filename in self.files:
            del self.files[filename]

    def clear_files(self):
        self.files.clear()
        self.current_tokens.clear()

    def analyze_file(self, filename):
        if filename in self.files:
            content = self.files[filename].editor.toPlainText().strip()
            if content:
                tokens = self.parse(content)
                self.files[filename].tokens = tokens
                return tokens
        return []

    def analyze_all_files(self):
        all_tokens = []
        for file_tab in self.files.values():
            content = file_tab.editor.toPlainText().strip()
            if content:
                tokens = self.parse(content)
                file_tab.tokens = tokens
                all_tokens.extend(tokens)
        self.current_tokens = all_tokens
        return all_tokens

    def parse(self, data):
        lexer.lineno = 1
        lexer.input(data)
        return list(iter(lexer.token, None))


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
        self.clear_all_btn = QPushButton("Limpar Tudo")
        self.file_label = QLabel("Nenhum arquivo selecionado")

        controls_layout.addWidget(self.open_file_btn)
        controls_layout.addWidget(self.open_folder_btn)
        controls_layout.addWidget(self.analyze_current_btn)
        controls_layout.addWidget(self.analyze_all_btn)
        controls_layout.addWidget(self.close_tab_btn)
        controls_layout.addWidget(self.clear_all_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.file_label)

        self.tab_widget = QTabWidget()
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

    def update_buttons_state(self):
        has_tabs = self.tab_widget.count() > 0
        self.close_tab_btn.setEnabled(has_tabs)
        self.clear_all_btn.setEnabled(has_tabs)

    def clear_all_tabs(self):
        self.tab_widget.clear()
        self.update_buttons_state()


class MainController:
    def __init__(self):
        self.app = QApplication([])
        self.model = AnalysisModel()
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

            if filename not in self.model.files:
                file_tab = FileTab(filename, content)
                self.model.add_file(filename, file_tab)
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
        # Corrigido: agora recebe o display_name, precisamos encontrar o filename real
        display_name = filename
        for filepath, file_tab in self.model.files.items():
            if file_tab.display_name == display_name:
                self.model.remove_file(filepath)
                break

    def analyze_current_file(self):
        current_index = self.view.tab_widget.currentIndex()
        if current_index >= 0:
            display_name = self.view.tab_widget.tabText(current_index)
            # Encontrar o filename real baseado no display_name
            filename = None
            for filepath, file_tab in self.model.files.items():
                if file_tab.display_name == display_name:
                    filename = filepath
                    break

            if filename:
                tokens = self.model.analyze_file(filename)
                self.update_display(tokens, display_name)

                file_tab = self.model.files[filename]
                file_tab.editor.highlighter.set_tokens(tokens)
                file_tab.editor.highlighter.rehighlight()

    def analyze_all_files(self):
        tokens = self.model.analyze_all_files()
        self.update_display(
            tokens, f"Todos os {len(self.model.files)} arquivos")

        for file_tab in self.model.files.values():
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
        self.model.clear_files()
        self.view.clear_all_tabs()
        self.update_display([], "")

    def run(self):
        return self.app.exec_()


def main():
    controller = MainController()
    controller.run()


if __name__ == '__main__':
    main()
