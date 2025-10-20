# Tonto Language - Ambiente de Análise Léxica

## Índice

- [Tonto Language - Ambiente de Análise Léxica](#tonto-language---ambiente-de-análise-léxica)
  - [Índice](#índice)
  - [Sobre o Projeto](#sobre-o-projeto)
  - [Pré-requisitos](#pré-requisitos)
  - [Instalação do PIP](#instalação-do-pip)
  - [Configuração do Projeto (Python)](#configuração-do-projeto-python)
  - [Estrutura do Projeto](#estrutura-do-projeto)
  - [Como Usar](#como-usar)
    - [Interface Gráfica (GUI)](#interface-gráfica-gui)
    - [Linha de Comando (CLI)](#linha-de-comando-cli)
  - [Exemplos](#exemplos)
  - [Contribuidores](#contribuidores)
  - [Licença](#licença)

---

## Sobre o Projeto

Este projeto implementa um analisador léxico para a linguagem Tonto, uma linguagem textual para modelagem de ontologias fundamentadas (baseada na UFO). Inclui uma interface gráfica (GUI) para análise, visualização e navegação de arquivos `.tonto`, além de ferramentas de linha de comando (CLI) para automação e integração.

---

## Pré-requisitos

- Python 3.12 ou superior
- [pip](https://pip.pypa.io/en/stable/installation/) (Python Package Manager)

---

## Instalação do PIP

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install python3-pip
```
**Fedora:**
```bash
sudo dnf install python3-pip
```
**Arch Linux:**
```bash
sudo pacman -S python-pip
```
Se necessário, consulte a [documentação oficial do pip](https://pip.pypa.io/en/stable/installation/).

---

## Configuração do Projeto (Python)

1. **Crie um ambiente virtual:**
   ```bash
   python3 -m venv venv
   ```

2. **Ative o ambiente virtual:**
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **Instale as dependências Python:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Estrutura do Projeto

```
.
├── src/
│   ├── lexer/           # Analisador léxico da linguagem Tonto
│   └── ui/
│       ├── controller/  # Lógica de controle da interface gráfica
│       ├── view/        # Componentes visuais (layouts, janelas)
│       └── widgets/     # Widgets reutilizáveis (editor, árvore de arquivos, tabelas)
├── exemplos/            # Exemplos de projetos e arquivos .tonto
├── requirements.txt     # Dependências Python
├── readme.md            # Este arquivo
└── ...
```

- **lexer/**: Implementação do analisador léxico usando [PLY](https://www.dabeaz.com/ply/).
- **ui/controller/**: Controladores da interface gráfica (PyQt5).
- **ui/view/**: Layouts e janelas principais.
- **ui/widgets/**: Componentes reutilizáveis (editor de código, árvore de arquivos, tabelas de tokens, etc).
- **exemplos/**: Projetos e arquivos de exemplo para testes e aprendizado.

---

## Como Usar

### Interface Gráfica (GUI)

1. Execute o aplicativo principal:
   ```bash
   python src/main.py
   ```
2. Abra arquivos `.tonto` ou pastas pelo menu "Arquivo".
3. Analise arquivos individualmente ou todos de uma vez pelo menu "Análise".
4. Visualize tokens, estatísticas, gráficos e navegue pelo código.

### Linha de Comando (CLI)

Para analisar um arquivo `.tonto` via terminal:
```bash
python src/cli.py
```
Siga as instruções interativas para informar o caminho do arquivo.

## Exemplos

Veja a pasta [exemplos/](exemplos/) para exemplos práticos de projetos Tonto, incluindo sintaxe de pacotes, classes, datatypes e relações.

---

## Contribuidores

- [Matheus Vynicius](https://github.com/vynijales)
- [Thiago Coelho](https://github.com/thiagocoelhoo)

---

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---
