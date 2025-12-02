# Tonto Language - Analisador Sintático (Parser)

## Índice

- [Tonto Language - Analisador Sintático (Parser)](#tonto-language---analisador-sintático-parser)
  - [Índice](#índice)
  - [Visão Geral](#visão-geral)
  - [Arquitetura de Implementação](#arquitetura-de-implementação)
  - [Decisões de Implementação do Parser](#decisões-de-implementação-do-parser)
    - [Estrutura da Gramática](#estrutura-da-gramática)
    - [Estratégia de Recuperação de Erros](#estratégia-de-recuperação-de-erros)
  - [Sistema de Sugestões Inteligentes (Fuzzy Matching)](#sistema-de-sugestões-inteligentes-fuzzy-matching)
    - [Motivação](#motivação)
    - [Implementação](#implementação)
    - [Algoritmo de Sugestão](#algoritmo-de-sugestão)
    - [Exemplos de Sugestões](#exemplos-de-sugestões)
  - [Visualização da AST em Árvore](#visualização-da-ast-em-árvore)
    - [Arquitetura do GraphViewer](#arquitetura-do-graphviewer)
    - [Conversão AST para Lista de Adjacências](#conversão-ast-para-lista-de-adjacências)
    - [Algoritmo de Layout Hierárquico](#algoritmo-de-layout-hierárquico)
      - [1. Atribuição de Níveis (BFS)](#1-atribuição-de-níveis-bfs)
      - [2. Cálculo de Larguras de Subárvores (Bottom-Up)](#2-cálculo-de-larguras-de-subárvores-bottom-up)
      - [3. Posicionamento Recursivo (Top-Down)](#3-posicionamento-recursivo-top-down)
    - [Renderização com PyQt5](#renderização-com-pyqt5)
  - [Sistema de Relatórios](#sistema-de-relatórios)
    - [ErrorReport](#errorreport)
    - [OntologySummary](#ontologysummary)
  - [Integração com a Interface](#integração-com-a-interface)
  - [Uso Programático](#uso-programático)
  - [Estruturas de Dados](#estruturas-de-dados)
  - [Dependências](#dependências)
  - [Contribuidores](#contribuidores)
  - [Licença](#licença)

---

## Visão Geral

O analisador sintático (parser) implementa análise sintática para ontologias fundamentadas usando **PLY (Python Lex-Yacc)**. As principais responsabilidades incluem:

1. **Análise Sintática**: Validação da estrutura gramatical
2. **Construção da AST**: Geração de árvore sintática abstrata
3. **Detecção de Erros**: Identificação de erros léxicos e sintáticos com sugestões inteligentes
4. **Visualização**: Renderização interativa da AST em formato de árvore hierárquica
5. **Síntese**: Geração de tabelas de resumo da ontologia

---

## Arquitetura de Implementação

```
┌──────────────────────────────────────────────────────────────────┐
│                        Código Tonto (.tonto)                      │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                     TontoLexer (lexer.py)                         │
│  • Tokenização                                                    │
│  • Detecção de erros léxicos                                      │
└────────────────────────────┬─────────────────────────────────────┘
                             │ Tokens
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                     TontoParser (parser.py)                       │
│  • Análise sintática (PLY yacc)                                   │
│  • Construção da AST                                              │
│  • Fuzzy matching para sugestões de erro                          │
│  • Coleta de estatísticas (OntologySummary)                       │
└────────────────────────────┬─────────────────────────────────────┘
                             │ AST + Relatórios
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                           Saídas                                  │
│  ┌────────────────┬────────────────┬──────────────────────────┐  │
│  │  AST (dict)    │  ErrorReport   │  OntologySummary         │  │
│  └────────────────┴────────────────┴──────────────────────────┘  │
└────────────┬──────────────────────┬────────────────────────────┬─┘
             │                      │                            │
             ▼                      ▼                            ▼
  ┌──────────────────┐   ┌──────────────────┐       ┌──────────────────┐
  │  GraphViewer     │   │  Error Table     │       │  Summary Table   │
  │  (Visualização)  │   │  (GUI/CLI)       │       │  (GUI/CLI)       │
  └──────────────────┘   └──────────────────┘       └──────────────────┘
```

---

## Decisões de Implementação do Parser

### Estrutura da Gramática

A gramática é implementada através de funções Python decoradas com docstrings BNF:

```python
def p_class_declaration(p):
    '''class_declaration : CLASS_STEREOTYPE IDENTIFIER class_body
                         | CLASS_STEREOTYPE IDENTIFIER 
                         | CLASS_STEREOTYPE IDENTIFIER OF_KW ONTOLOGICAL_CATEGORY class_body
                         | CLASS_STEREOTYPE IDENTIFIER OF_KW ONTOLOGICAL_CATEGORY
    '''
    # Construção da AST para classes
```

**Decisão de Design:**
- Cada regra gramatical retorna um dicionário estruturado representando o nó da AST
- Uso de listas para coletar elementos repetidos (imports, declarations, attributes)
- Regras opcionais implementadas através de múltiplas produções alternativas

### Estratégia de Recuperação de Erros

Implementamos modo de recuperação de erros usando o token especial `error` do PLY:

```python
def p_error(p):
    if p:
        suggestion = generate_smart_suggestion(str(p.value), p.type)
        error_report.add_syntactic_error(
            line=p.lineno,
            column=0,
            message=f"Token inesperado '{p.value}' do tipo {p.type}",
            suggestion=suggestion
        )
        parser.errok()  # Tenta continuar o parsing
    else:
        # EOF inesperado
        error_report.add_syntactic_error(...)
```

**Vantagens:**
- O parsing continua após erros para detectar múltiplos problemas
- Relatório completo de erros em uma única execução
- Melhor experiência do usuário (feedback mais rico)

---

## Sistema de Sugestões Inteligentes (Fuzzy Matching)

### Motivação

Erros de digitação são comuns durante a modelagem de ontologias. Um sistema de sugestões inteligentes:
- Reduz o tempo de depuração
- Melhora a experiência do usuário
- Auxilia na aprendizagem da sintaxe

### Implementação

Utilizamos a biblioteca padrão `difflib.get_close_matches()` para implementar fuzzy matching:

```python
from difflib import get_close_matches

def find_similar_token(token: str, token_type: str = None) -> Optional[str]:
    """
    Encontra tokens similares usando fuzzy matching.
    Algoritmo de Ratcliff/Obershelp para similaridade de strings.
    """
    token_lower = token.lower()
    suggestions = []
    
    # Buscar em palavras-chave
    keywords = list(KEYWORDS.keys())
    close_keywords = get_close_matches(token_lower, keywords, n=3, cutoff=0.6)
    if close_keywords:
        suggestions.extend(close_keywords)
    
    # Buscar em estereótipos de classe
    close_class_stereotypes = get_close_matches(token_lower, CLASS_STEREOTYPES, n=3, cutoff=0.6)
    if close_class_stereotypes:
        suggestions.extend(close_class_stereotypes)
    
    # ... outros vocabulários
    
    if suggestions:
        unique_suggestions = list(dict.fromkeys(suggestions))
        if len(unique_suggestions) == 1:
            return f"Você quis dizer '{unique_suggestions[0]}'?"
        else:
            return f"Você quis dizer: {', '.join(f"'{s}'" for s in unique_suggestions[:3])}?"
    
    return None
```

### Algoritmo de Sugestão

**Parâmetros:**
- **cutoff=0.6**: Limiar de similaridade de 60%
- **n=3**: Máximo de 3 sugestões por categoria

**Vocabulários Pesquisados:**
1. `KEYWORDS`: Palavras-chave da linguagem (package, import, genset, etc.)
2. `CLASS_STEREOTYPES`: Estereótipos de classes (kind, subkind, role, etc.)
3. `RELATION_STEREOTYPES`: Estereótipos de relações (mediation, material, etc.)
4. `NATIVE_TYPES`: Tipos nativos (string, number, boolean, etc.)
5. `META_ATTRIBUTES`: Meta-atributos (ordered, const, derived, etc.)

**Complexidade:**
- Tempo: O(n × m) onde n = tamanho do token, m = tamanho do vocabulário
- Espaço: O(k) onde k = número de sugestões (limitado a 3)

### Exemplos de Sugestões

```python
# Erro: "kindd" (typo)
[ERRO SINTÁTICO - Linha 5, Coluna 1]
  Mensagem: Token inesperado 'kindd' do tipo IDENTIFIER
  Sugestão: Você quis dizer 'kind'?

# Erro: "medation" (falta 'i')
[ERRO SINTÁTICO - Linha 10, Coluna 5]
  Mensagem: Token inesperado 'medation' do tipo IDENTIFIER
  Sugestão: Você quis dizer 'mediation'?

# Erro: "relatr" (múltiplas possibilidades)
[ERRO SINTÁTICO - Linha 15, Coluna 1]
  Mensagem: Token inesperado 'relatr' do tipo IDENTIFIER
  Sugestão: Você quis dizer: 'relator', 'relation'?
```

---

## Visualização da AST em Árvore

### Arquitetura do GraphViewer

O `GraphViewer` é um widget PyQt5 customizado que renderiza a AST como um grafo hierárquico interativo:

```
┌─────────────────────────────────────────────────────────┐
│              GraphViewer (QGraphicsView)                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │         QGraphicsScene                            │  │
│  │  ┌──────────┐                                     │  │
│  │  │  package │    ← NodeItem (classe customizada)  │  │
│  │  └────┬─────┘                                     │  │
│  │       │                                           │  │
│  │  ┌────┴────┬─────────┐                           │  │
│  │  │imports  │ decls   │    ← EdgeItem (arestas)   │  │
│  │  └─────────┴─────────┘                           │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Componentes:**
- `GraphViewer`: Herda de `GraphViewerCore` (QGraphicsView)
- `NodeItem`: QGraphicsItem customizado para nós
- `EdgeItem`: QGraphicsItem customizado para arestas
- `ASTConverter`: Converte AST em lista de adjacências

### Conversão AST para Lista de Adjacências

**Problema:** A AST é uma estrutura aninhada (dicts e lists). O GraphViewer precisa de uma lista de adjacências.

**Solução:** Implementação recursiva que percorre a AST e constrói o grafo:

```python
class ASTConverter:
    def _traverse_and_build(self, node_data, key_context="Root"):
        """
        Percorre recursivamente a AST convertendo em lista de adjacências.
        
        Estratégia:
        1. Cria um nó para cada dict/list
        2. Conecta pais aos filhos através de índices
        3. Retorna o índice do nó criado
        """
        if not isinstance(node_data, (dict, list)):
            return None  # Folhas (strings, números) não são nós
        
        # Gerar nome descritivo do nó
        if isinstance(node_data, dict):
            node_type = node_data.get("type", key_context)
            node_name = f"{node_type}: {node_data.get('name')}"
        else:
            node_name = key_context
        
        # Inserir nó na lista de adjacências
        current_node_index = len(self.adjacency_list)
        self.adjacency_list.append({"name": node_name, "connections": []})
        
        # Processar filhos recursivamente
        children_indices = []
        
        if isinstance(node_data, dict):
            for key, value in node_data.items():
                child_index = self._traverse_and_build(value, key)
                if child_index is not None:
                    children_indices.append(child_index)
        
        elif isinstance(node_data, list):
            for i, item in enumerate(node_data):
                child_index = self._traverse_and_build(item, f"{key_context}_Item_{i}")
                if child_index is not None:
                    children_indices.append(child_index)
        
        # Atualizar conexões do nó atual
        self.adjacency_list[current_node_index]["connections"] = children_indices
        
        return current_node_index
```

**Complexidade:**
- Tempo: O(n) onde n = número de nós na AST
- Espaço: O(n) para a lista de adjacências

### Algoritmo de Layout Hierárquico

**Problema:** Posicionar nós de forma hierárquica e visualmente agradável.

**Solução:** Algoritmo de layout em três etapas:

#### 1. Atribuição de Níveis (BFS)

```python
def _assign_levels(self, graph_data, root_id, levels):
    """
    Usa BFS para atribuir profundidade (nível) a cada nó.
    Nível 0 = raiz, Nível 1 = filhos diretos, etc.
    """
    visited = set()
    queue = [(root_id, 0)]
    
    while queue:
        node_id, level = queue.pop(0)
        if node_id in visited:
            continue
        
        visited.add(node_id)
        if level not in levels:
            levels[level] = []
        levels[level].append(node_id)
        
        # Adicionar filhos à fila
        for child_id in graph_data[node_id].get("connections", []):
            if child_id not in visited:
                queue.append((child_id, level + 1))
```

#### 2. Cálculo de Larguras de Subárvores (Bottom-Up)

```python
def _calculate_subtree_widths(self, graph_data, levels, subtree_widths, min_spacing):
    """
    Calcula a largura necessária para cada subárvore (processamento bottom-up).
    
    Fórmula:
    - Nó folha: largura = min_spacing
    - Nó interno: largura = soma(largura dos filhos)
    """
    max_level = max(levels.keys()) if levels else 0
    
    # Processar de baixo para cima
    for level in range(max_level, -1, -1):
        for node_id in levels[level]:
            children = graph_data[node_id].get("connections", [])
            
            if not children:
                subtree_widths[node_id] = min_spacing
            else:
                total_width = sum(
                    subtree_widths.get(child_id, min_spacing)
                    for child_id in children
                )
                subtree_widths[node_id] = max(min_spacing, total_width)
```

#### 3. Posicionamento Recursivo (Top-Down)

```python
def _position_subtree(self, graph_data, node_id, center_x, y, positions, 
                      subtree_widths, level_height):
    """
    Posiciona recursivamente uma subárvore centrada em center_x.
    
    Estratégia:
    - Posiciona o nó atual em (center_x, y)
    - Distribui filhos horizontalmente proporcionalmente às suas larguras
    - Centraliza filhos sob o pai
    """
    positions[node_id] = QPointF(center_x, y)
    
    children = graph_data[node_id].get("connections", [])
    if not children:
        return
    
    child_y = y + level_height
    
    if len(children) == 1:
        # Um único filho: centralizar sob o pai
        self._position_subtree(graph_data, children[0], center_x, child_y, ...)
    else:
        # Múltiplos filhos: distribuir horizontalmente
        total_width = sum(subtree_widths.get(c, 80) for c in children)
        start_x = center_x - total_width / 2
        
        current_x = start_x
        for child_id in children:
            child_width = subtree_widths.get(child_id, 80)
            child_center_x = current_x + child_width / 2
            
            self._position_subtree(graph_data, child_id, child_center_x, child_y, ...)
            current_x += child_width
```

**Parâmetros de Layout:**
- `level_height = 120`: Distância vertical entre níveis
- `min_node_spacing = 100`: Espaçamento horizontal mínimo
- `margin = 120`: Margem ao redor da cena

**Vantagens do Algoritmo:**
- Subárvores balanceadas e centralizadas
- Sem sobreposição de nós
- Layout escalável para árvores grandes

### Renderização com PyQt5

**NodeItem (Nós):**
```python
class NodeItem(QGraphicsEllipseItem):
    def __init__(self, name, node_id, position):
        super().__init__(-40, -40, 80, 80)  # Elipse 80x80
        self.setBrush(QBrush(QColor("#4A90E2")))
        self.setPen(QPen(QColor("#2E5F8A"), 2))
        self.setFlag(QGraphicsItem.ItemIsMovable)  # Arrastar nós
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPos(position)
        
        # Label do nó
        text_item = QGraphicsTextItem(name, self)
        text_item.setPos(-35, -10)
```

**EdgeItem (Arestas):**
```python
class EdgeItem(QGraphicsLineItem):
    def __init__(self, source_node, dest_node):
        super().__init__()
        self.source = source_node
        self.dest = dest_node
        self.setPen(QPen(QColor("#7F8C8D"), 1.5))
        self.update_position()
    
    def update_position(self):
        """Atualiza a linha entre os nós"""
        line = QLineF(self.source.pos(), self.dest.pos())
        self.setLine(line)
```

**Interatividade:**
- Zoom in/out com scroll do mouse
- Pan com drag (modo grab ativado)
- Nós arrastáveis individualmente
- Seleção de nós (highlight)

---

## Sistema de Relatórios

### ErrorReport

Gerencia erros léxicos e sintáticos separadamente:

```python
class ErrorReport:
    def __init__(self):
        self.lexical_errors: List[ParseError] = []
        self.syntactic_errors: List[ParseError] = []
    
    def add_syntactic_error(self, line, column, message, suggestion=""):
        self.syntactic_errors.append(
            ParseError(line, column, message, "SYNTACTIC", suggestion)
        )
    
    def get_error_report(self) -> str:
        """Gera relatório formatado em texto"""
        # Formata erros léxicos e sintáticos separadamente
```

**Decisão de Design:**
- Separação explícita entre erros léxicos e sintáticos
- Erros léxicos capturados pelo lexer (caracteres ilegais)
- Erros sintáticos capturados pelo parser (estrutura inválida)

### OntologySummary

Coleta estatísticas durante o parsing:

```python
class OntologySummary:
    def __init__(self):
        self.package_name: str = None
        self.imports: List[str] = []
        self.classes: Dict[str, Dict] = {}
        self.datatypes: List[str] = []
        self.enums: Dict[str, List[str]] = {}
        self.gensets: List[Dict] = []
        self.external_relations: List[Dict] = []
    
    def add_class(self, name, stereotype, specializes, category):
        """Adiciona uma classe ao sumário"""
        self.classes[name] = {
            'stereotype': stereotype,
            'category': category,
            'attributes': [],
            'relations': [],
            'specializes': specializes
        }
```

**Estratégia:**
- Coleta incremental durante o parsing (ação semântica nas regras gramaticais)
- Formatação textual para exibição em CLI/GUI

---

## Integração com a Interface

**Interface Gráfica (GUI):**
```python
# src/ui/controller/main_controller.py
from parser.parser import parse_ontology

def analyze_current_file(self):
    code = self.current_tab.editor.toPlainText()
    result = parse_ontology(code)
    
    # Exibir síntese
    self.view.summary_text.setText(result['summary'])
    
    # Exibir erros
    self.view.error_table.populate(result['error_report'])
    
    # Exibir AST visual
    self.view.graph_tab.editor.load_graph(result)
```

**CLI:**
```python
# src/cli_app.py
result = parse_ontology(code)
print(result['summary'])
print(result['error_report'])
```

---

## Uso Programático

```python
from parser.parser import parse_ontology, print_parse_results

# Ler código
with open('exemplo.tonto', 'r') as f:
    code = f.read()

# Parsing
result = parse_ontology(code)

# Verificar erros
if result['has_errors']:
    print(result['error_report'])
else:
    print("✓ Parsing bem-sucedido!")

# Imprimir síntese e erros
print_parse_results(result)

# Acessar AST
package = result['package']
classes = [d for d in result['declarations'] if d['type'] in ['kind', 'subkind']]
```

---

## Estruturas de Dados

**AST (Árvore Sintática Abstrata):**
```python
{
    'package': 'CarOwnership',
    'imports': ['CoreDatatypes'],
    'declarations': [
        {
            'type': 'kind',
            'name': 'Car',
            'content': {
                'attributes': [...],
                'relations': [...]
            }
        }
    ],
    'summary': "...",  # Tabela de síntese formatada
    'error_report': "...",  # Relatório de erros formatado
    'has_errors': False
}
```

**ParseError:**
```python
@dataclass
class ParseError:
    line: int
    column: int
    message: str
    error_type: str  # 'LEXICAL' ou 'SYNTACTIC'
    suggestion: str
```

---

## Dependências

```txt
ply==3.11              # Parser generator (Lex/Yacc)
PyQt5==5.15.9          # GUI framework (GraphViewer)
```

Instalação:
```bash
pip install -r requirements.txt
```

---

## Contribuidores

- [Matheus Vynicius](https://github.com/vynijales)
- [Thiago Coelho](https://github.com/thiagocoelhoo)

---

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
