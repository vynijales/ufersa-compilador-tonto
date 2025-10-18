import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from lexer import lexer

class LexicalAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador Léxico - Tonto Language")
        self.root.geometry("1400x800")
        
        # Variáveis
        self.current_file = None
        self.open_files = {}  # Dicionário para armazenar arquivos abertos: {filename: content}
        self.tabs = {}  # Dicionário para armazenar referências das abas: {filename: tab_widget}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Frame de controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botões
        ttk.Button(controls_frame, text="Abrir Arquivo", command=self.open_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Abrir Pasta", command=self.open_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Analisar Arquivo Atual", command=self.analyze_current_tab).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Analisar Todos", command=self.analyze_all_tabs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Fechar Aba Atual", command=self.close_current_tab).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Limpar Tudo", command=self.clear_all).pack(side=tk.LEFT)
        
        # Label do arquivo atual
        self.file_label = ttk.Label(controls_frame, text="Nenhum arquivo selecionado")
        self.file_label.pack(side=tk.RIGHT)
        
        # Frame para código fonte com abas
        source_frame = ttk.LabelFrame(main_frame, text="Código Fonte", padding="5")
        source_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        source_frame.columnconfigure(0, weight=1)
        source_frame.rowconfigure(0, weight=1)
        
        # Notebook (abas) para código fonte
        self.notebook = ttk.Notebook(source_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind para mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Frame dos tokens
        tokens_frame = ttk.LabelFrame(main_frame, text="Tokens Encontrados", padding="5")
        tokens_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        tokens_frame.columnconfigure(0, weight=1)
        tokens_frame.rowconfigure(0, weight=1)
        
        # Treeview para mostrar tokens
        columns = ('Line', 'Type', 'Value')
        self.tokens_tree = ttk.Treeview(tokens_frame, columns=columns, show='headings')
        
        # Definir cabeçalhos
        self.tokens_tree.heading('Line', text='Linha')
        self.tokens_tree.heading('Type', text='Tipo')
        self.tokens_tree.heading('Value', text='Valor')
        
        # Configurar colunas
        self.tokens_tree.column('Line', width=80)
        self.tokens_tree.column('Type', width=150)
        self.tokens_tree.column('Value', width=400)
        
        # Scrollbar para a treeview
        tree_scroll = ttk.Scrollbar(tokens_frame, orient=tk.VERTICAL, command=self.tokens_tree.yview)
        self.tokens_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tokens_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame de estatísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estatísticas", padding="5")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Área de texto para estatísticas
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=4, wrap=tk.WORD)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.stats_text.config(state=tk.DISABLED)
        
        # Bind para duplo clique na treeview
        self.tokens_tree.bind('<Double-1>', self.on_token_double_click)
        
    def create_text_tab(self, filename, content):
        """Cria uma nova aba com área de texto editável"""
        # Frame para a aba
        tab_frame = ttk.Frame(self.notebook)
        tab_frame.grid_rowconfigure(0, weight=1)
        tab_frame.grid_columnconfigure(0, weight=1)
        
        # Área de texto com scroll
        text_area = scrolledtext.ScrolledText(tab_frame, wrap=tk.WORD, font=("Courier New", 10))
        text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_area.insert(1.0, content)
        
        # Adicionar aba ao notebook
        display_name = os.path.basename(filename)
        self.notebook.add(tab_frame, text=display_name)
        
        # Armazenar referências
        self.open_files[filename] = content
        self.tabs[filename] = {
            'frame': tab_frame,
            'text_area': text_area,
            'display_name': display_name
        }
        
        # Selecionar a nova aba
        self.notebook.select(tab_frame)
        
    def get_current_tab_info(self):
        """Retorna informações da aba atual"""
        current_tab = self.notebook.select()
        if not current_tab:
            return None, None, None
            
        # Encontrar o filename correspondente à aba atual
        for filename, tab_info in self.tabs.items():
            if str(tab_info['frame']) == current_tab:
                return filename, tab_info['display_name'], tab_info['text_area']
        
        return None, None, None
    
    def on_tab_changed(self, event):
        """Callback quando a aba é alterada"""
        filename, display_name, text_area = self.get_current_tab_info()
        if filename:
            self.file_label.config(text=display_name)
            self.current_file = filename
            # Atualizar a análise para a aba atual
            self.analyze_current_tab()
    
    def open_file(self):
        """Abre um arquivo individual"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo .tonto",
            filetypes=[("Tonto files", "*.tonto"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_file_into_tab(file_path)
    
    def open_folder(self):
        """Abre todos os arquivos .tonto de uma pasta"""
        folder_path = filedialog.askdirectory(title="Selecionar pasta com arquivos .tonto")
        
        if folder_path:
            files = []
            for root, _, filenames in os.walk(folder_path):
                for filename in filenames:
                    if filename.endswith('.tonto'):
                        files.append(os.path.join(root, filename))
            
            if not files:
                messagebox.showinfo("Informação", "Nenhum arquivo .tonto encontrado na pasta selecionada.")
                return
            
            # Carregar todos os arquivos em abas
            for file_path in files:
                self.load_file_into_tab(file_path)
            
            messagebox.showinfo("Sucesso", f"Carregados {len(files)} arquivos em abas separadas.")
    
    def load_file_into_tab(self, file_path):
        """Carrega um arquivo em uma nova aba"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se o arquivo já está aberto
            if file_path in self.open_files:
                # Selecionar a aba existente
                for filename, tab_info in self.tabs.items():
                    if filename == file_path:
                        self.notebook.select(tab_info['frame'])
                        break
            else:
                # Criar nova aba
                self.create_text_tab(file_path, content)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler arquivo {file_path}: {str(e)}")
    
    def analyze_current_tab(self):
        """Analisa o conteúdo da aba atual"""
        filename, display_name, text_area = self.get_current_tab_info()
        
        if not text_area:
            messagebox.showwarning("Aviso", "Não há arquivo aberto para analisar.")
            return
        
        content = text_area.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Aviso", "O arquivo atual está vazio.")
            return
        
        try:
            tokens = self.parse(content)
            self.display_tokens(tokens)
            self.update_stats(f"Arquivo: {display_name}\n"
                            f"Total de tokens: {len(tokens)}\n"
                            f"Linhas processadas: {tokens[-1].lineno if tokens else 0}\n"
                            f"Análise concluída com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante análise: {str(e)}")
    
    def analyze_all_tabs(self):
        """Analisa todos os arquivos abertos nas abas"""
        if not self.open_files:
            messagebox.showwarning("Aviso", "Não há arquivos abertos para analisar.")
            return
        
        total_tokens = 0
        results = []
        
        for filename, tab_info in self.tabs.items():
            try:
                content = tab_info['text_area'].get(1.0, tk.END).strip()
                if content:
                    tokens = self.parse(content)
                    total_tokens += len(tokens)
                    
                    results.append(f"Arquivo: {tab_info['display_name']}")
                    results.append(f"  Tokens encontrados: {len(tokens)}")
                    results.append(f"  Linhas processadas: {tokens[-1].lineno if tokens else 0}")
                    results.append("")
                    
            except Exception as e:
                results.append(f"Erro no arquivo {tab_info['display_name']}: {str(e)}")
                results.append("")
        
        # Mostrar estatísticas gerais
        self.update_stats("\n".join(results))
        
        # Atualizar a análise da aba atual também
        self.analyze_current_tab()
        
        messagebox.showinfo("Análise Concluída", 
                          f"Processados {len(self.tabs)} arquivos\nTotal de tokens: {total_tokens}")
    
    def close_current_tab(self):
        """Fecha a aba atual"""
        filename, display_name, text_area = self.get_current_tab_info()
        
        if not filename:
            return
        
        # Remover do notebook
        current_tab = self.notebook.select()
        self.notebook.forget(current_tab)
        
        # Remover das estruturas de dados
        if filename in self.open_files:
            del self.open_files[filename]
        if filename in self.tabs:
            del self.tabs[filename]
        
        # Atualizar label se não houver mais abas
        if len(self.notebook.tabs()) == 0:
            self.file_label.config(text="Nenhum arquivo selecionado")
            self.clear_tokens()
            self.update_stats("")
    
    def parse(self, data):
        lexer.lineno = 1
        lexer.input(data)
        tokens = []
        while True:
            tok = lexer.token()
            if not tok:
                break
            tokens.append(tok)
        return tokens
    
    def display_tokens(self, tokens):
        self.clear_tokens()
        
        for token in tokens:
            self.tokens_tree.insert('', tk.END, values=(token.lineno, token.type, token.value))
    
    def clear_tokens(self):
        for item in self.tokens_tree.get_children():
            self.tokens_tree.delete(item)
    
    def update_stats(self, text):
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, text)
        self.stats_text.config(state=tk.DISABLED)
    
    def on_token_double_click(self, event):
        """Quando um token é clicado duas vezes, navega para a linha no editor atual"""
        filename, display_name, text_area = self.get_current_tab_info()
        if not text_area:
            return
            
        item = self.tokens_tree.selection()[0]
        line_number = self.tokens_tree.item(item, 'values')[0]
        
        # Navegar para a linha no editor de texto atual
        text_area.focus_set()
        text_area.tag_remove("sel", "1.0", tk.END)
        text_area.tag_add("sel", f"{line_number}.0", f"{line_number}.end")
        text_area.see(f"{line_number}.0")
    
    def clear_all(self):
        """Fecha todas as abas e limpa a interface"""
        # Fechar todas as abas
        while self.notebook.tabs():
            self.notebook.forget(0)
        
        # Limpar estruturas de dados
        self.open_files.clear()
        self.tabs.clear()
        
        # Limpar resto da interface
        self.clear_tokens()
        self.update_stats("")
        self.file_label.config(text="Nenhum arquivo selecionado")
        self.current_file = None

def main():
    root = tk.Tk()
    app = LexicalAnalyzerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
