from .base_view import BaseView

class TextView(BaseView):
    def __init__(self, controller, banner):
        super().__init__(controller, banner)

    def process_command(self, command):
        command = command.strip().lower()
        
        if command in ('sair', 'q', 'exit', 'quit'):
            return False
        
        elif command in ('ajuda', 'h', 'help', '?'):
            self.display_help()
        
        elif command in ('limpar', 'c', 'clear'):
            self.controller.clear_screen()
        
        elif command in ('arquivo', 'a', 'file'):
            file_path = input("Digite o caminho do arquivo .tonto: ").strip()
            result, error = self.controller.tokenize_file(file_path)
            if error:
                print(error)
            else:
                self.print_tokens(**result)
        
        elif command in ('digitar', 'd', 'type', 'input'):
            code = self._get_code_from_input()
            if code is not None:
                result, error = self.controller.tokenize_input(code)
                if error:
                    print(error)
                else:
                    self.print_tokens(**result)
        
        elif command and command.endswith('.tonto'):
            result, error = self.controller.tokenize_file(command)
            if error:
                print(error)
            else:
                self.print_tokens(**result)
        
        elif not command:
            print("Digite 'ajuda' para ver os comandos disponiveis")
        
        else:
            print(f"Comando nao reconhecido: {command}")
            print("Digite 'ajuda' para ver os comandos disponiveis")
        
        return True

    def _get_code_from_input(self):
        print("\nModo de entrada de codigo:")
        print("Digite seu codigo .tonto (use 'EOF' em linha separada para finalizar):")
        print("-" * 60)
        
        lines = []
        try:
            while True:
                try:
                    line = input()
                    if line.strip().upper() == 'EOF':
                        break
                    lines.append(line)
                except EOFError:
                    break
        except KeyboardInterrupt:
            print("\nEntrada cancelada pelo usuario")
            return None

        return '\n'.join(lines) if lines else None

    def run(self):
        self.controller.clear_screen()
        print(self.banner)
        self.display_help()
        
        print("Pronto para processar codigo .tonto!")
        print("Dica: Pressione Enter vazio para menu interativo")
        print("-" * 50)
        
        while True:
            try:
                user_input = input('TontoCLI > ').strip()
                
                if not self.process_command(user_input):
                    print("\nAte logo!")
                    break
                    
            except KeyboardInterrupt:
                print("\nUse 'sair' para encerrar o programa corretamente")
            except Exception as e:
                print(f"\nErro inesperado: {e}")
