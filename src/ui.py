import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from lexer import lexer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import collections

class LexicalAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador Léxico - Tonto Language")
        self.root.geometry("1600x900")
        
        # Variáveis
        self.current_file = None
        self.open_files = {}
        self.tabs = {}
        self.current_tokens = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configurar grid weights principal
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Frame principal com paned window para redimensionamento
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left frame - Código fonte
        left_frame = ttk.Frame(main_paned)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # Right frame - Tokens e estatísticas
        right_frame = ttk.Frame(main_paned)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        main_paned.add(left_frame, weight=1)
        main_paned.add(right_frame, weight=1)
        
        # ===== LEFT FRAME - CÓDIGO FONTE =====
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(left_frame, text="Controles", padding="10")
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botões superiores
        btn_frame_top = ttk.Frame(controls_frame)
        btn_frame_top.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(btn_frame_top, text="Abrir Arquivo", command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame_top, text="Abrir Pasta", command=self.open_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame_top, text="Analisar Arquivo Atual", command=self.analyze_current_tab).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame_top, text="Analisar Todos", command=self.analyze_all_tabs).pack(side=tk.LEFT, padx=(0, 5))
        
        # Botões inferiores
        btn_frame_bottom = ttk.Frame(controls_frame)
        btn_frame_bottom.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.close_tab_btn = ttk.Button(btn_frame_bottom, text="Fechar Aba Atual", command=self.close_current_tab)
        self.close_tab_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_all_btn = ttk.Button(btn_frame_bottom, text="Limpar Tudo", command=self.clear_all)
        self.clear_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Label do arquivo atual
        self.file_label = ttk.Label(btn_frame_bottom, text="Nenhum arquivo selecionado")
        self.file_label.pack(side=tk.RIGHT)
        
        # Frame para código fonte
        source_frame = ttk.LabelFrame(left_frame, text="Código Fonte", padding="5")
        source_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        source_frame.columnconfigure(0, weight=1)
        source_frame.rowconfigure(0, weight=1)
        
        # Notebook (abas) para código fonte
        self.notebook = ttk.Notebook(source_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # ===== RIGHT FRAME - TOKENS E ESTATÍSTICAS =====
        
        # Frame dos tokens (parte superior direita)
        tokens_frame = ttk.LabelFrame(right_frame, text="Tokens Encontrados", padding="5")
        tokens_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tokens_frame.columnconfigure(0, weight=1)
        tokens_frame.rowconfigure(0, weight=1)
        
        # Treeview para mostrar tokens
        columns = ('Line', 'Type', 'Value')
        self.tokens_tree = ttk.Treeview(tokens_frame, columns=columns, show='headings', height=15)
        
        # Definir cabeçalhos
        self.tokens_tree.heading('Line', text='Linha')
        self.tokens_tree.heading('Type', text='Tipo')
        self.tokens_tree.heading('Value', text='Valor')
        
        # Configurar colunas
        self.tokens_tree.column('Line', width=80, anchor=tk.CENTER)
        self.tokens_tree.column('Type', width=150)
        self.tokens_tree.column('Value', width=300)
        
        # Scrollbar para a treeview
        tree_scroll = ttk.Scrollbar(tokens_frame, orient=tk.VERTICAL, command=self.tokens_tree.yview)
        self.tokens_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tokens_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame de estatísticas (parte inferior direita)
        stats_frame = ttk.LabelFrame(right_frame, text="Estatísticas e Análise", padding="5")
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.rowconfigure(1, weight=1)
        
        # Frame para estatísticas textuais
        text_stats_frame = ttk.Frame(stats_frame)
        text_stats_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        text_stats_frame.columnconfigure(0, weight=1)
        
        # Área de texto para estatísticas
        self.stats_text = scrolledtext.ScrolledText(text_stats_frame, height=6, wrap=tk.WORD, font=("Arial", 9))
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.stats_text.config(state=tk.DISABLED)
        
        # Frame para o gráfico
        chart_frame = ttk.LabelFrame(stats_frame, text="Distribuição de Tokens - Gráfico")
        chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        # Frame para detalhes dos tokens
        details_frame = ttk.LabelFrame(stats_frame, text="Detalhes por Tipo")
        details_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        # Treeview para detalhes dos tokens
        detail_columns = ('Type', 'Count', 'Percentage')
        self.detail_tree = ttk.Treeview(details_frame, columns=detail_columns, show='headings', height=10)
        
        self.detail_tree.heading('Type', text='Tipo')
        self.detail_tree.heading('Count', text='Quantidade')
        self.detail_tree.heading('Percentage', text='Percentual')
        
        self.detail_tree.column('Type', width=120)
        self.detail_tree.column('Count', width=80, anchor=tk.CENTER)
        self.detail_tree.column('Percentage', width=80, anchor=tk.CENTER)
        
        detail_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=detail_scroll.set)
        
        self.detail_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Canvas para o gráfico
        self.chart_canvas = None
        self.chart_frame = chart_frame
        
        # Bind para duplo clique na treeview
        self.tokens_tree.bind('<Double-1>', self.on_token_double_click)
        
        # Inicializar estado dos botões
        self.update_buttons_state()
        
    def update_buttons_state(self):
        """Atualiza o estado dos botões baseado no número de abas"""
        has_tabs = len(self.notebook.tabs()) > 0
        
        if has_tabs:
            self.close_tab_btn.config(state=tk.NORMAL)
            self.clear_all_btn.config(state=tk.NORMAL)
        else:
            self.close_tab_btn.config(state=tk.DISABLED)
            self.clear_all_btn.config(state=tk.DISABLED)
    
    def create_text_tab(self, filename, content):
        """Cria uma nova aba com área de texto editável"""
        tab_frame = ttk.Frame(self.notebook)
        tab_frame.grid_rowconfigure(0, weight=1)
        tab_frame.grid_columnconfigure(0, weight=1)
        
        text_area = scrolledtext.ScrolledText(tab_frame, wrap=tk.WORD, font=("Courier New", 10))
        text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_area.insert(1.0, content)
        
        display_name = os.path.basename(filename)
        self.notebook.add(tab_frame, text=display_name)
        
        self.open_files[filename] = content
        self.tabs[filename] = {
            'frame': tab_frame,
            'text_area': text_area,
            'display_name': display_name
        }
        
        self.notebook.select(tab_frame)
        self.update_buttons_state()
        
    def get_current_tab_info(self):
        """Retorna informações da aba atual"""
        current_tab = self.notebook.select()
        if not current_tab:
            return None, None, None
            
        for filename, tab_info in self.tabs.items():
            if str(tab_info['frame']) == current_tab:
                return filename, tab_info['display_name'], tab_info['text_area']
        
        return None, None, None
    
    def on_tab_changed(self, event):
        """Callback quando a aba é alterada"""
        filename, display_name, text_area = self.get_current_tab_info()
        if filename:
            self.file_label.config(text=f"Arquivo atual: {display_name}")
            self.current_file = filename
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
            
            for file_path in files:
                self.load_file_into_tab(file_path)
            
            messagebox.showinfo("Sucesso", f"Carregados {len(files)} arquivos em abas separadas.")
    
    def load_file_into_tab(self, file_path):
        """Carrega um arquivo em uma nova aba"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path in self.open_files:
                for filename, tab_info in self.tabs.items():
                    if filename == file_path:
                        self.notebook.select(tab_info['frame'])
                        break
            else:
                self.create_text_tab(file_path, content)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler arquivo {file_path}: {str(e)}")
    
    def analyze_current_tab(self):
        """Analisa o conteúdo da aba atual"""
        filename, display_name, text_area = self.get_current_tab_info()
        
        if not text_area:
            return
        
        content = text_area.get(1.0, tk.END).strip()
        if not content:
            self.clear_analysis()
            return
        
        try:
            tokens = self.parse(content)
            self.current_tokens = tokens
            self.display_tokens(tokens)
            self.update_stats(tokens, display_name)
            self.update_chart(tokens)
            self.update_detail_tree(tokens)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante análise: {str(e)}")
    
    def analyze_all_tabs(self):
        """Analisa todos os arquivos abertos nas abas"""
        if not self.open_files:
            messagebox.showwarning("Aviso", "Não há arquivos abertos para analisar.")
            return
        
        all_tokens = []
        total_tokens = 0
        
        for filename, tab_info in self.tabs.items():
            try:
                content = tab_info['text_area'].get(1.0, tk.END).strip()
                if content:
                    tokens = self.parse(content)
                    all_tokens.extend(tokens)
                    total_tokens += len(tokens)
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro no arquivo {tab_info['display_name']}: {str(e)}")
        
        self.current_tokens = all_tokens
        self.display_tokens(all_tokens)
        self.update_stats(all_tokens, f"Todos os {len(self.tabs)} arquivos")
        self.update_chart(all_tokens)
        self.update_detail_tree(all_tokens)
        
        messagebox.showinfo("Análise Concluída", 
                          f"Processados {len(self.tabs)} arquivos\nTotal de tokens: {total_tokens}")
    
    def close_current_tab(self):
        """Fecha a aba atual"""
        filename, display_name, text_area = self.get_current_tab_info()
        
        if not filename:
            return
        
        current_tab = self.notebook.select()
        self.notebook.forget(current_tab)
        
        if filename in self.open_files:
            del self.open_files[filename]
        if filename in self.tabs:
            del self.tabs[filename]
        
        if len(self.notebook.tabs()) == 0:
            self.file_label.config(text="Nenhum arquivo selecionado")
            self.clear_analysis()
        
        self.update_buttons_state()
    
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
    
    def clear_detail_tree(self):
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
    
    def update_stats(self, tokens, filename):
        """Atualiza as estatísticas textuais"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        if not tokens:
            self.stats_text.insert(1.0, "Nenhum token encontrado.")
        else:
            stats_text = f"📊 ANÁLISE LÉXICA - {filename.upper()}\n"
            stats_text += "=" * 50 + "\n"
            stats_text += f"• Total de tokens: {len(tokens)}\n"
            stats_text += f"• Linhas processadas: {tokens[-1].lineno if tokens else 0}\n"
            stats_text += f"• Tipos únicos de tokens: {len(set(token.type for token in tokens))}\n"
            
            # Encontrar token mais frequente
            if tokens:
                token_counts = collections.Counter(token.type for token in tokens)
                most_common = token_counts.most_common(1)[0]
                stats_text += f"• Token mais frequente: {most_common[0]} ({most_common[1]} ocorrências)\n"
            
            self.stats_text.insert(1.0, stats_text)
        
        self.stats_text.config(state=tk.DISABLED)
    
    def update_detail_tree(self, tokens):
        """Atualiza a treeview de detalhes"""
        self.clear_detail_tree()
        
        if not tokens:
            return
        
        token_counts = collections.Counter(token.type for token in tokens)
        total_tokens = len(tokens)
        
        for token_type, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_tokens) * 100
            self.detail_tree.insert('', tk.END, values=(
                token_type, 
                count, 
                f"{percentage:.1f}%"
            ))
    
    def update_chart(self, tokens):
        """Atualiza o gráfico de pizza com a distribuição dos tokens"""
        self.clear_chart()
        
        if not tokens:
            # Mostrar gráfico vazio
            fig = Figure(figsize=(6, 4), dpi=80)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'Nenhum dado\npara exibir', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            ax.set_facecolor('#f0f0f0')
            ax.set_title('Distribuição de Tokens', pad=20, fontweight='bold')
        else:
            # Contar tokens por tipo
            token_counts = collections.Counter(token.type for token in tokens)
            
            # Preparar dados para o gráfico
            labels = []
            sizes = []
            
            for token_type, count in token_counts.most_common():
                labels.append(f"{token_type}\n({count})")
                sizes.append(count)
            
            # Criar figura do matplotlib
            fig = Figure(figsize=(6, 4), dpi=80)
            ax = fig.add_subplot(111)
            
            # Criar gráfico de pizza
            colors = plt.cm.Pastel1(range(len(labels)))
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                             startangle=90, colors=colors, 
                                             textprops={'fontsize': 8})
            
            # Melhorar a aparência
            ax.set_title('Distribuição de Tokens', pad=20, fontweight='bold')
            
            # Ajustar layout
            fig.tight_layout()
        
        # Embeddar no tkinter
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def clear_chart(self):
        """Limpa o gráfico atual"""
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None
    
    def clear_analysis(self):
        """Limpa toda a análise"""
        self.clear_tokens()
        self.clear_detail_tree()
        self.update_stats([], "")
        self.clear_chart()
    
    def on_token_double_click(self, event):
        """Quando um token é clicado duas vezes, navega para o lexema no editor atual"""
        filename, display_name, text_area = self.get_current_tab_info()
        if not text_area:
            return
            
        selection = self.tokens_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        line_number = int(self.tokens_tree.item(item, 'values')[0])
        token_value = self.tokens_tree.item(item, 'values')[2]
        
        line_start = f"{line_number}.0"
        line_end = f"{line_number}.end"
        line_content = text_area.get(line_start, line_end)
        
        start_pos = line_content.find(token_value)
        
        if start_pos != -1:
            lexema_start = f"{line_number}.{start_pos}"
            lexema_end = f"{line_number}.{start_pos + len(token_value)}"
            
            text_area.focus_set()
            text_area.tag_remove("sel", "1.0", tk.END)
            text_area.tag_add("sel", lexema_start, lexema_end)
            text_area.see(lexema_start)
            text_area.focus_force()
        else:
            text_area.focus_set()
            text_area.tag_remove("sel", "1.0", tk.END)
            text_area.tag_add("sel", line_start, line_end)
            text_area.see(line_start)
    
    def clear_all(self):
        """Fecha todas as abas e limpa a interface"""
        while self.notebook.tabs():
            self.notebook.forget(0)
        
        self.open_files.clear()
        self.tabs.clear()
        self.clear_analysis()
        self.file_label.config(text="Nenhum arquivo selecionado")
        self.current_file = None
        self.update_buttons_state()

def main():
    root = tk.Tk()
    app = LexicalAnalyzerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
