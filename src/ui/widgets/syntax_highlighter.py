from PyQt5.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter
from lexer.lexer import KEYWORDS, SYMBOLS

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.token_colors = {
            'KEYWORD': QColor('#F92672'),               # Magenta
            'CLASS_IDENTIFIER': QColor('#A6E22E'),      # Verde Claro
            'INSTANCE_IDENTIFIER': QColor('#FD971F'),   # Laranja
            'RELATION_IDENTIFIER': QColor('#E6DB74'),   # Amarelo Claro
            'CLASS_STEREOTYPE': QColor('#AE81FF'),      # Roxo/Lilás
            'RELATION_STEREOTYPE': QColor('#F92672'),   # Magenta
            'META_ATTRIBUTES': QColor('#66D9EF'),       # Ciano
        
            'NUMBER': QColor('#AE81FF'),                # Roxo/Lilás
            'NATIVE_TYPE': QColor('#A6E22E'),           # Verde Claro
            'USER_TYPE': QColor('#66D9EF'),             # Ciano
            
            # Quase Branco (Texto Principal)
            'COMMA': QColor('#F8F8F2'),
            'COMMENT': QColor('#75715E'),               # Cinza Esverdeado
            'ERROR': QColor('#FF8077'),                 # Vermelho Forte
        }

        for s in SYMBOLS.keys():
            self.token_colors[s] = QColor('#00FFFF')

        for kw_type in set(KEYWORDS.values()):
            self.token_colors[kw_type] = QColor('#F92672')
        
        self.highlighting_rules = []

    def set_tokens(self, tokens):
        self.highlighting_rules.clear()

        for token in tokens:
            if token.type in self.token_colors:
                format = QTextCharFormat()
                format.setForeground(self.token_colors[token.type])
                self.highlighting_rules.append((token, format))

            if token.type == 'ERROR':
                format = QTextCharFormat()
                format.setForeground(self.token_colors['ERROR'])
                format.setBackground(QColor('#8E3030'))
                format.setUnderlineColor(QColor(self.token_colors['ERROR']))
                format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                format.setFontWeight(100)
                self.highlighting_rules.append((token, format))

    def highlightBlock(self, text):
        for token, format in self.highlighting_rules:
            if token.lineno == self.currentBlock().blockNumber() + 1:
                start = token.token_pos - 1
                if start >= 0:
                    self.setFormat(start, len(token.value), format)
