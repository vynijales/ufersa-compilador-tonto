import os
from pathlib import Path
from lexer.lexer import tokenize

try:
    import questionary
    HAS_QUESTIONARY = True
except ImportError:
    HAS_QUESTIONARY = False
    print("Aviso: Biblioteca 'questionary' nao encontrada. Instale com: pip install questionary")
    print("Usando interface basica...")

class TontoController:
    def __init__(self):
        self.has_questionary = HAS_QUESTIONARY

    def tokenize_file(self, file_path=None):
        if not file_path:
            return None, "Caminho vazio"

        try:
            path = Path(file_path)
            if not path.exists():
                return None, f"Arquivo nao encontrado: {file_path}"
            
            if path.suffix != '.tonto':
                return None, "O arquivo deve ter extensao .tonto"

            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()

            char_count = len(content)
            tokens = tokenize(content)
            return {
                'tokens': tokens,
                'source_name': f"Arquivo: {path.name}",
                'char_count': char_count
            }, None

        except UnicodeDecodeError:
            return None, "Erro de codificacao: nao foi possivel ler o arquivo como UTF-8"
        except Exception as e:
            return None, f"Erro ao processar arquivo: {e}"

    def tokenize_input(self, code):
        if not code:
            return None, "Nenhum codigo foi digitado"

        char_count = len(code)
        tokens = tokenize(code)
        return {
            'tokens': tokens,
            'source_name': "Entrada do Terminal",
            'char_count': char_count
        }, None

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
