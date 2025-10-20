from PyQt5.QtWidgets import (QTextEdit)
from PyQt5.QtGui import QFont

from ui.widgets.syntax_highlighter import SyntaxHighlighter

class CodeEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Courier New", 10))
        self.highlighter = SyntaxHighlighter(self.document())
