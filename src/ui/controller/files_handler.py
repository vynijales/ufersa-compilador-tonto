
from lexer.lexer import TontoLexer
from parser.parser import parse_ontology

class FilesHandler:
    def __init__(self):
        self.files = {}
        self.current_tokens = []
        self.current_errors = []
        self.current_syntactic_errors = []

    def add_file(self, filename, file_tab):
        self.files[filename] = file_tab

    def remove_file(self, filename):
        if filename in self.files:
            del self.files[filename]

    def clear_files(self):
        self.files.clear()
        self.current_tokens.clear()
        self.current_errors.clear()
        self.current_syntactic_errors.clear()

    def analyze_file(self, filename):
        if filename in self.files:
            content = self.files[filename].editor.toPlainText().strip()
            if content:
                tokens, errors = self.tokenize(content)
                syntactic_errors = self.parse(content)
                
                self.files[filename].tokens = tokens
                self.files[filename].errors = errors
                self.files[filename].syntactic_errors = syntactic_errors
                
                return tokens, errors, syntactic_errors
        return [], [], []

    def analyze_all_files(self):
        all_tokens = []
        all_errors = []
        all_syntactic_errors = []
        
        for file_tab in self.files.values():
            content = file_tab.editor.toPlainText().strip()
            if content:
                tokens, errors = self.tokenize(content)
                syntactic_errors = self.parse(content)
                
                file_tab.tokens = tokens
                file_tab.errors = errors
                file_tab.syntactic_errors = syntactic_errors
                
                all_tokens.extend(tokens)
                all_errors.extend(errors)
                all_syntactic_errors.extend(syntactic_errors)
        
        self.current_tokens = all_tokens
        self.current_errors = all_errors
        self.current_syntactic_errors = all_syntactic_errors
        
        return all_tokens, all_errors, all_syntactic_errors

    def tokenize(self, data):
        lexer = TontoLexer()
        tokens = list(lexer.tokenize(data))
        errors = tuple(lexer.errors)
        return tokens, errors
    
    def parse(self, data):
        """
        Realiza análise sintática e retorna lista de erros sintáticos
        """
        try:
            result = parse_ontology(data)
            
            # Extrair erros sintáticos do error_report
            if result and 'error_report' in result:
                # O error_report é uma string formatada, mas também temos acesso direto aos erros
                # através do módulo parser
                from parser.parser import error_report
                return list(error_report.syntactic_errors)
            
            return []
        except Exception as e:
            # Em caso de erro no parser, retornar lista vazia
            print(f"Erro ao fazer parsing: {e}")
            return []
