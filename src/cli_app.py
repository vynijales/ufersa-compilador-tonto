from cli.controller.main_controller import TontoController
from cli.view.interactive_view import InteractiveView
from cli.view.text_view import TextView

class TontoCLI:
    def __init__(self):
        self.controller = TontoController()
        self.version = "1.0.0"
        self.banner = """
==========================================
          TONTO LEXER CLI             
          Versao {0}                    
==========================================
        """.format(self.version)

    def run(self):
        if self.controller.has_questionary:
            mode_choice = InteractiveView.select_interface_mode()
            
            if mode_choice == "interactive":
                self._run_interactive_mode()
            else:
                self._run_text_mode()
        else:
            self._run_text_mode()

    def _run_interactive_mode(self):
        view = InteractiveView(self.controller, self.banner)
        view.run()

    def _run_text_mode(self):
        view = TextView(self.controller, self.banner)
        view.run()

def main():
    cli = TontoCLI()
    cli.run()

if __name__ == '__main__':
    main()
