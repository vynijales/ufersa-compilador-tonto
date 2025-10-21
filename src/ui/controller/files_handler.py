
from lexer.lexer import TontoLexer

class FilesHandler:
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

    def tokenize(self, data):
        lexer = TontoLexer()
        tokens = list(lexer.tokenize(data))
        return tokens
