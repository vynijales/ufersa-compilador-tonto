class BaseView:
    def __init__(self, controller, banner):
        self.controller = controller
        self.banner = banner

    def display_help(self):
        help_text = """
COMANDOS DISPONIVEIS:

Use SETAS para navegar e ENTER para selecionar
Ou digite comandos diretamente:

  'arquivo' ou 'a' - Processar um arquivo .tonto
  'digitar' ou 'd' - Digitar codigo diretamente no terminal
  'sair' ou 'q'    - Encerrar o programa
  'ajuda' ou 'h'   - Mostrar esta ajuda
  'limpar' ou 'c'  - Limpar a tela

USO:
  - Para arquivos: digite o caminho completo ou relativo
  - Para codigo: digite seu codigo e use 'EOF' em linha separada para finalizar
        """
        print(help_text)

    def print_tokens(self, tokens, source_name="Codigo digitado", char_count=0):
        print(f'\nProcessando: {source_name}')
        print('-' * 50)
        
        if hasattr(tokens, '__iter__') and not isinstance(tokens, (list, tuple)):
            tokens = list(tokens)
        
        if not tokens:
            print("Nenhum token encontrado.")
            return
            
        valid_tokens = []
        lexical_errors = []
        
        for token in tokens:
            if hasattr(token, 'type'):
                token_type = getattr(token, 'type', 'UNKNOWN')
                if 'ERROR' in str(token_type).upper():
                    lexical_errors.append(token)
                else:
                    valid_tokens.append(token)
            else:
                token_str = str(token)
                if 'ERROR' in token_str.upper():
                    lexical_errors.append(token)
                else:
                    valid_tokens.append(token)
        
        print("\nTOKENS ENCONTRADOS:")
        print("-" * 60)
        
        all_tokens = valid_tokens + lexical_errors
        for i, token in enumerate(all_tokens, 1):
            print(f"{i:3d}. {token}")
        
        print("\n" + "="*70)
        print("RESUMO DA ANALISE LEXICA")
        print("="*70)
        
        print(f"{'Arquivo/Fonte:':<20} {source_name}")
        print(f"{'Caracteres:':<20} {char_count}")
        print(f"{'Tokens Validos:':<20} {len(valid_tokens)}")
        print(f"{'Erros Lexicos:':<20} {len(lexical_errors)}")
        print(f"{'Total de Tokens:':<20} {len(all_tokens)}")
        
        if char_count > 0:
            print(f"{'Tokens por caractere:':<20} {len(all_tokens)/char_count:.2f}")
        
        print("="*70)
        
        if lexical_errors:
            print("\nERROS LEXICOS ENCONTRADOS:")
            for error in lexical_errors:
                print(f"   - {error}")
