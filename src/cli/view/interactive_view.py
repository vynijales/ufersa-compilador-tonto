from .base_view import BaseView
import questionary

class InteractiveView(BaseView):
    def __init__(self, controller, banner):
        super().__init__(controller, banner)
        self.main_menu_options = [
            {"name": "Processar arquivo .tonto", "value": "file"},
            {"name": "Digitar codigo no terminal", "value": "input"},
            {"name": "Mostrar ajuda", "value": "help"},
            {"name": "Sair do programa", "value": "exit"},
            {"name": "Limpar tela", "value": "clear"}
        ]

    @staticmethod
    def select_interface_mode():
        mode_options = [
            {"name": "Modo Interativo (com setas)", "value": "interactive"},
            {"name": "Modo Texto (digitacao)", "value": "text"}
        ]
        
        mode_choice = questionary.select(
            "Escolha o modo de interface:",
            choices=mode_options,
            use_arrow_keys=True,
            default=mode_options[0]
        ).ask()
        
        return mode_choice

    def show_menu(self):
        choice = questionary.select(
            "Escolha uma opcao:",
            choices=self.main_menu_options,
            use_arrow_keys=True,
            use_indicator=True
        ).ask()
        
        return choice

    def get_file_path(self):
        return questionary.text(
            "Digite o caminho do arquivo .tonto:",
            validate=lambda text: True
        ).ask()

    def get_code_input(self):
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
        
        while True:
            choice = self.show_menu()
            
            if not choice:
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
                file_path = self.get_file_path()
                if file_path:
                    result, error = self.controller.tokenize_file(file_path)
                    if error:
                        print(error)
                    else:
                        self.print_tokens(**result)
            elif choice == "input":
                code = self.get_code_input()
                if code is not None:
                    result, error = self.controller.tokenize_input(code)
                    if error:
                        print(error)
                    else:
                        self.print_tokens(**result)
            elif choice == "help":
                self.display_help()
            elif choice == "clear":
                self.controller.clear_screen()
                
            if choice not in ["clear", "help"]:
                input("\nPressione Enter para continuar...")
