from PyQt5.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

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
