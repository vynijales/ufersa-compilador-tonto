# 🔍 Tonto Language - Analisador Semântico

## Índice

- [Tonto Language - Analisador Semântico](#tonto-language---analisador-semântico)
  - [Índice](#índice)
  - [Sobre o Analisador Semântico](#sobre-o-analisador-semântico)
  - [Arquitetura do Analisador](#arquitetura-do-analisador)
  - [Principais Decisões de Design](#principais-decisões-de-design)
    - [1. Análise em Três Fases](#1-análise-em-três-fases)
    - [2. Tabela de Símbolos Centralizada](#2-tabela-de-símbolos-centralizada)
    - [3. Validação de Estereótipos](#3-validação-de-estereótipos)
    - [4. Validação de Hierarquia de Rigidez](#4-validação-de-hierarquia-de-rigidez)
    - [5. Separação de Responsabilidades](#5-separação-de-responsabilidades)
  - [Estrutura de Módulos](#estrutura-de-módulos)
  - [Validações Implementadas](#validações-implementadas)
    - [Validações Básicas](#validações-básicas)
    - [Validações Ontológicas](#validações-ontológicas)
    - [Validações de Padrões](#validações-de-padrões)
  - [Como Usar](#como-usar)
  - [Exemplos de Erros Detectados](#exemplos-de-erros-detectados)
  - [Contribuidores](#contribuidores)
  - [Licença](#licença)

---

## 📖 Sobre o Analisador Semântico

O analisador semântico é responsável por validar a corretude semântica de programas escritos em Tonto.

Este módulo recebe como entrada a Árvore Sintática Abstrata (AST) gerada pelo parser e produz:
- **Tabela de Símbolos**: estrutura contendo todas as classes, relações, datatypes, enums e gensets declarados.
- **Lista de Erros Semânticos**: erros que violam as regras ontológicas e de consistência da linguagem.

---

## 🏗️ Arquitetura do Analisador

O analisador semântico é composto por três componentes principais:

```
src/semantic/
├── analyzer.py          # Analisador principal (SemanticAnalyzer)
├── symbol_table.py      # Tabela de símbolos
├── pattern_validator.py # Validador de padrões ontológicos
└── dataclasses.py       # Estruturas de dados (TontoClass, Genset, etc.)
```

O fluxo de análise segue um pipeline de três fases sequenciais, garantindo que cada etapa tenha as informações necessárias para suas validações.

---

## 💡 Principais Decisões de Design

### 1. Análise em Três Fases

A análise semântica foi dividida em **três fases distintas** para garantir que todas as informações necessárias estejam disponíveis em cada etapa:

**Fase 1: Construção da Tabela de Símbolos**
- Percorre toda a AST e registra todas as declarações (classes, datatypes, enums, gensets, relações).
- Detecta redeclarações de símbolos.
- Valida restrições básicas de cada construção (ex.: `kind` não pode especializar outra classe).

**Fase 2: Validação de Referências**
- Valida que todas as referências a classes, datatypes e enums existem.
- Verifica especializações, relações e gensets.
- Valida a **hierarquia de rigidez** (rigid não pode especializar anti-rigid).

**Fase 3: Validação de Padrões Ontológicos**
- Delega ao `PatternValidator` a verificação de padrões complexos.
- Valida restrições de gensets (disjoint, complete, overlapping).
- Valida que non-ultimate sortals especializam exatamente um ultimate sortal.

**Justificativa**: A divisão em fases permite que validações mais complexas (como padrões ontológicos) tenham acesso a uma tabela de símbolos completa, evitando problemas de dependência circular e referências não resolvidas.

---

### 2. Tabela de Símbolos Centralizada

A tabela de símbolos (`SymbolTable`) é a estrutura central do analisador, armazenando:
- **Classes** (`TontoClass`): com estereótipo, especializações, atributos e relações.
- **Gensets** (`Genset`): generalizações e especializações com restrições.
- **Relações Externas** (`TontoRelation`): relações materiais entre classes.
- **Datatypes e Enums**: tipos de dados e enumerações.

**Justificativa**: Centralizar todos os símbolos em uma única estrutura facilita a navegação e consulta durante as validações. A tabela de símbolos também pode ser reutilizada por fases posteriores do compilador (geração de código, otimizações, etc.).

---

### 3. Validação de Estereótipos

O analisador distingue entre **Ultimate Sortals** e **Non-Ultimate Sortals**:

- **Ultimate Sortals** (kinds, collectives, quantities, etc.): fornecem princípio de identidade e não podem especializar outras classes.
- **Non-Ultimate Sortals** (subkinds, phases, roles, etc.): **devem** especializar exatamente um ultimate sortal.

```python
ULTIMATE_SORTALS = {
    'kind', 'collective', 'quantity', 'relator',
    'quality', 'mode', 'intrinsicMode', 'extrinsicMode',
    'type', 'powertype'
}

NON_ULTIMATE_SORTALS = {
    'subkind', 'phase', 'role', 'historicalRole'
}
```

---

### 4. Validação de Hierarquia de Rigidez

O analisador implementa a validação de **rigidez**, uma propriedade meta-ontológica que classifica universais em:

- **Rigid** (kind, subkind, collective, quantity, category): propriedades essenciais que se aplicam necessariamente a todas as instâncias.
- **Anti-Rigid** (role, phase, historicalRole, roleMixin): propriedades acidentais.
- **Semi-Rigid** (mixin, phaseMixin): podem ser essenciais para algumas instâncias e acidentais para outras.

**Restrição Fundamental**: Um universal **rigid não pode especializar um universal anti-rigid**.

**Justificativa**: Esta validação previne inconsistências ontológicas. Por exemplo, um `subkind` (rigid) não pode especializar um `role` (anti-rigid), pois isso violaria a propriedade de rigidez: um subkind é uma especialização essencial, enquanto um role é uma classificação acidental e contingente.

---

### 5. Separação de Responsabilidades

O analisador foi modularizado em componentes com responsabilidades bem definidas:

- **`SemanticAnalyzer`**: orquestra o processo de análise e validações básicas.
- **`SymbolTable`**: armazena e fornece acesso aos símbolos.
- **`PatternValidator`**: valida padrões ontológicos complexos (gensets, especializações múltiplas, etc.).
- **`dataclasses`**: define estruturas de dados imutáveis para representar os símbolos.

**Justificativa**: Esta arquitetura facilita a manutenção, testes e extensão do analisador. Novos padrões de validação podem ser adicionados ao `PatternValidator` sem modificar o fluxo principal do `SemanticAnalyzer`.

---

## 📁 Estrutura de Módulos

```
src/semantic/
├── analyzer.py          # Analisador principal e orquestrador
├── symbol_table.py      # Estrutura de dados para símbolos
├── pattern_validator.py # Validações de padrões ontológicos
└── dataclasses.py       # Classes de dados (TontoClass, Genset, etc.)
```

- **analyzer.py**: Implementa o `SemanticAnalyzer` com as três fases de análise.
- **symbol_table.py**: Implementa a `SymbolTable` com métodos para adicionar e consultar símbolos.
- **pattern_validator.py**: Implementa o `PatternValidator` para validações complexas de padrões.
- **dataclasses.py**: Define estruturas de dados como `TontoClass`, `Genset`, `TontoRelation`, `SemanticError`.

---

## ✅ Validações Implementadas

### 🔹 Validações Básicas
- Redeclaração de classes, datatypes, enums e gensets.
- Existência de referências (especializações, relações, gensets).
- Restrições de estereótipos (ex.: `kind` não pode especializar outra classe).

### 🔹 Validações Ontológicas
- **Ultimate Sortals**: non-ultimate sortals devem especializar um ultimate sortal.
- **Hierarquia de Rigidez**: rigid não pode especializar anti-rigid.
- **Gensets**: validação de restrições `disjoint`, `complete` e `overlapping`.

### 🔹 Validações de Padrões
- **Especializações múltiplas**: detecta conflitos de rigidez em hierarquias complexas.
- **Relações**: valida cardinalidades e conectores (ex.: relators em relações materiais).
- **Categorias**: validação de mixins e categorias como especializações de múltiplos sortals.

---

## 🚀 Como Usar

O analisador semântico é invocado automaticamente pela interface gráfica e CLI após a análise sintática. Para uso programático:

```python
from semantic.analyzer import analyze

# ast = resultado do parser
symbol_table, errors = analyze(ast)

if errors:
    for error in errors:
        print(f"Semantic Error: {error}")
else:
    print("No semantic errors found!")
```

---

## Exemplos de Erros Detectados

**Erro 1: Kind especializando outra classe**
```tonto
kind Person specializes Entity { }
```
Erro: `Kind 'Person' cannot specialize another class. Kinds are the top-level sortals.`

**Erro 2: Subkind sem especialização**
```tonto
subkind Student { }
```
Erro: `This class does not specialize a Ultimate Sortal. Every sortal class must specialize a unique Ultimate Sortal (kind, collective, quantity, ...)`

**Erro 3: Rigid especializando Anti-Rigid**
```tonto
kind Person { }
role Student specializes Person { }
subkind GraduateStudent specializes Student { }
```
Erro: `Rigid universal 'GraduateStudent' (subkind) cannot specialize anti-rigid universal 'Student' (role).`

**Erro 4: Referência indefinida**
```tonto
subkind Student specializes UndefinedClass { }
```
Erro: `Class 'Student' specializes undefined class 'UndefinedClass'.`

---
