import os
from pathlib import Path
from lexer.lexer import tokenize

try:
    import questionary
    HAS_QUESTIONARY = True
except ImportError:
    HAS_QUESTIONARY = False
    print("⚠️  Biblioteca 'questionary' não encontrada. Instale com: pip install questionary")
    print("   Usando interface básica...")

class TontoCLI:
    def __init__(self):
        self.version = "1.0.0"
        self.banner = """
╔══════════════════════════════════════╗
║          TONTO LEXER CLI             ║
║        Versão {0}                    ║
╚══════════════════════════════════════╝
        """.format(self.version)
        
        self.main_menu_options = [
            {"name": "📁 Processar arquivo .tonto", "value": "file"},
            {"name": "⌨️  Digitar código no terminal", "value": "input"},
            {"name": "ℹ️  Mostrar ajuda", "value": "help"},
            {"name": "❌ Sair do programa", "value": "exit"},
            {"name": "🧹 Limpar tela", "value": "clear"}
        ]

    def display_help(self):
        help_text = """
📖 COMANDOS DISPONÍVEIS:

• Use SETAS ↑↓ para navegar e ENTER para selecionar
• Ou digite comandos diretamente:

  'arquivo' ou 'a' - Processar um arquivo .tonto
  'digitar' ou 'd' - Digitar código diretamente no terminal
  'sair' ou 'q'    - Encerrar o programa
  'ajuda' ou 'h'   - Mostrar esta ajuda
  'limpar' ou 'c'  - Limpar a tela

📝 USO:
  - Para arquivos: digite o caminho completo ou relativo
  - Para código: digite seu código e use 'EOF' em linha separada para finalizar
        """
        print(help_text)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_tokens(self, tokens, source_name="Código digitado"):
        print(f'\n🎯 Processando: {source_name}')
        print('─' * 50)
        
        # Converter generator para lista se necessário
        if hasattr(tokens, '__iter__') and not isinstance(tokens, (list, tuple)):
            tokens = list(tokens)
        
        if not tokens:
            print("❌ Nenhum token encontrado.")
            return
            
        token_count = 0
        for i, token in enumerate(tokens, 1):
            print(f"{i:3d}. {token}")
            token_count += 1
        
        print(f'\n✅ Total de tokens encontrados: {token_count}')
        print('─' * 50)

    def tokenize_file(self, file_path=None):
        if not file_path:
            if HAS_QUESTIONARY:
                file_path = questionary.text(
                    "📁 Digite o caminho do arquivo .tonto:",
                    validate=lambda text: True
                ).ask()
            else:
                file_path = input("📁 Digite o caminho do arquivo .tonto: ").strip()
        
        if not file_path:
            print("❌ Caminho vazio")
            return

        try:
            path = Path(file_path)
            if not path.exists():
                print(f"❌ Arquivo não encontrado: {file_path}")
                return
            
            if path.suffix != '.tonto':
                print("❌ O arquivo deve ter extensão .tonto")
                return

            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Tokenize e converte para lista se for generator
            tokens = tokenize(content)
            self.print_tokens(tokens, f"Arquivo: {path.name}")

        except UnicodeDecodeError:
            print("❌ Erro de codificação: não foi possível ler o arquivo como UTF-8")
        except Exception as e:
            print(f"❌ Erro ao processar arquivo: {e}")

    def tokenize_input(self):
        print("\n📝 Modo de entrada de código:")
        print("Digite seu código .tonto (use 'EOF' em linha separada para finalizar):")
        print("─" * 60)
        
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
            print("\n⏹️  Entrada cancelada pelo usuário")
            return

        if not lines:
            print("❌ Nenhum código foi digitado")
            return

        code = '\n'.join(lines)
        
        # Tokenize e converte para lista se for generator
        tokens = tokenize(code)
        self.print_tokens(tokens)

    def get_token_count(self, tokens):
        """Conta tokens de forma segura, lidando com generators"""
        if hasattr(tokens, '__len__'):
            return len(tokens)
        else:
            # Para generators, conta iterando
            count = 0
            for _ in tokens:
                count += 1
            return count

    def show_interactive_menu(self):
        """Mostra menu interativo com setas"""
        if not HAS_QUESTIONARY:
            print("❌ Menu interativo não disponível. Digite comandos manualmente.")
            return None
            
        choice = questionary.select(
            "Escolha uma opção:",
            choices=self.main_menu_options,
            use_arrow_keys=True,
            use_indicator=True
        ).ask()
        
        return choice

    def process_command(self, command):
        command = command.strip().lower()
        
        if command in ('sair', 'q', 'exit', 'quit'):
            return False
        
        elif command in ('ajuda', 'h', 'help', '?'):
            self.display_help()
        
        elif command in ('limpar', 'c', 'clear'):
            self.clear_screen()
        
        elif command in ('arquivo', 'a', 'file'):
            self.tokenize_file()
        
        elif command in ('digitar', 'd', 'type', 'input'):
            self.tokenize_input()
        
        elif command and command.endswith('.tonto'):
            self.tokenize_file(command)
        
        elif not command:
            # Enter vazio - mostra menu interativo
            choice = self.show_interactive_menu()
            if not choice:  # Usuário cancelou
                return True
            if choice == "exit":
                return False
            elif choice == "file":
                self.tokenize_file()
            elif choice == "input":
                self.tokenize_input()
            elif choice == "help":
                self.display_help()
            elif choice == "clear":
                self.clear_screen()
        
        else:
            print(f"❌ Comando não reconhecido: {command}")
            print("💡 Digite 'ajuda' para ver os comandos disponíveis")
        
        return True

    def run_interactive_mode(self):
        """Modo totalmente interativo com menus"""
        if not HAS_QUESTIONARY:
            print("❌ Modo interativo requer 'questionary'. Instale com: pip install questionary")
            self.run_text_mode()
            return
            
        self.clear_screen()
        print(self.banner)
        
        while True:
            choice = self.show_interactive_menu()
            
            if not choice:  # Usuário pressionou Ctrl+C
                confirm = questionary.confirm("Tem certeza que deseja sair?").ask()
                if confirm:
                    break
                else:
                    continue
                    
            if choice == "exit":
                confirm = questionary.confirm("Tem certeza que deseja sair?").ask()
                if confirm:
                    break
                else:
                    continue
            elif choice == "file":
                self.tokenize_file()
            elif choice == "input":
                self.tokenize_input()
            elif choice == "help":
                self.display_help()
            elif choice == "clear":
                self.clear_screen()
                
            # Pausa antes de mostrar o menu novamente
            if choice not in ["clear", "help"]:
                input("\n⏎ Pressione Enter para continuar...")

    def run_text_mode(self):
        """Modo texto tradicional"""
        self.clear_screen()
        print(self.banner)
        self.display_help()
        
        print("🚀 Pronto para processar código .tonto!")
        print("💡 Dica: Pressione Enter vazio para menu interativo")
        print("─" * 50)
        
        while True:
            try:
                user_input = input('\n🎯 TontoCLI > ').strip()
                
                if not self.process_command(user_input):
                    print("\n👋 Até logo!")
                    break
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Use 'sair' para encerrar o programa corretamente")
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}")

    def run(self):
        """Executa o CLI no modo apropriado"""
        if HAS_QUESTIONARY:
            # Corrigido: usar o objeto de choice como default
            mode_options = [
                {"name": "🎯 Modo Interativo (com setas)", "value": "interactive"},
                {"name": "⌨️  Modo Texto (digitação)", "value": "text"}
            ]
            
            mode_choice = questionary.select(
                "Escolha o modo de interface:",
                choices=mode_options,
                use_arrow_keys=True,
                default=mode_options[0]  # Usar o objeto em vez do valor
            ).ask()
            
            if mode_choice == "interactive":
                self.run_interactive_mode()
            else:
                self.run_text_mode()
        else:
            self.run_text_mode()

def main():
    cli = TontoCLI()
    cli.run()

if __name__ == '__main__':
    main()
