
from lexer.lexer import TontoLexer

class FilesHandler:
    def __init__(self):
        self.files = {}
        self.current_tokens = []
        self.current_errors = []

    def add_file(self, filename, file_tab):
        self.files[filename] = file_tab

    def remove_file(self, filename):
        if filename in self.files:
            del self.files[filename]

    def clear_files(self):
        self.files.clear()
        self.current_tokens.clear()
        self.current_errors.clear()

    def analyze_file(self, filename):
        if filename in self.files:
            content = self.files[filename].editor.toPlainText().strip()
            if content:
                tokens, errors = self.tokenize(content)
                self.files[filename].tokens = tokens
                self.files[filename].errors = errors
                return tokens, errors
        return [], []

    def analyze_all_files(self):
        all_tokens = []
        all_errors = []
        for file_tab in self.files.values():
            content = file_tab.editor.toPlainText().strip()
            if content:
                tokens, errors = self.tokenize(content)
                file_tab.tokens = tokens
                file_tab.errors = errors  # Armazenar erros no file_tab
                all_tokens.extend(tokens)
                all_errors.extend(errors)
        self.current_tokens = all_tokens
        self.current_errors = all_errors
        return all_tokens, all_errors

    def tokenize(self, data):
        lexer = TontoLexer()
        tokens = list(lexer.tokenize(data))
        errors = lexer.get_errors()
        return tokens, errors