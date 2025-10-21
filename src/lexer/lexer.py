from ply import lex
import re
from typing import List, Iterator
from dataclasses import dataclass

tokens = (
    'CLASS_STEREOTYPE',
    'RELATION_STEREOTYPE',
    'KEYWORD',

    'PACKAGE_IDENTIFIER',
    'CLASS_IDENTIFIER',
    'RELATION_IDENTIFIER',
    'INSTANCE_IDENTIFIER',

    'NATIVE_TYPE',
    'USER_TYPE',
    'META_ATTRIBUTES',

    'NUMBER',
    'COMMA',
    'DOT',

    'OPEN_PAREN',
    'CLOSE_PAREN',
    'OPEN_BRACKET',
    'CLOSE_BRACKET',
    'OPEN_BRACE',
    'CLOSE_BRACE',
    'RANGE',
    'MULTIPLICATION',
    'AT',
    'COLON',

    'AGGREGATION',
    'AGGREGATION_INVERSE',
    'COMPOSITION',
    'COMPOSITION_INVERSE',
    'DOUBLE_DASH',
    'ERROR',
)

CLASS_STEREOTYPES = [
    'event',
    'situation',
    'process',
    'category',
    'mixin',
    'phaseMixin',
    'roleMixin',
    'historicalRoleMixin',
    'kind',
    'collective',
    'quantity',
    'quality',
    'mode',
    'intrinsicMode',
    'extrinsicMode',
    'subkind',
    'phase',
    'role',
    'historicalRole',

    # Para compatibilidade com versões antigas
    'intrinsic-modes',
    'extrinsic-modes',  
    'intrinsic-mode',
    'extrinsic-mode',
]

RELATION_STEREOTYPES = [
    "material",
    "derivation",
    "comparative",
    "mediation",
    "characterization",
    "externalDependence",
    "componentOf",
    "memberOf",
    "subCollectionOf",
    "subQualityOf",
    "instantiation",
    "termination",
    "participational",
    "participation",
    "historicalDependence",
    "creation",
    "manifestation",
    "bringsAbout",
    "triggers",
    "composition",
    "aggregation",
    "inherence",
    "value",
    "formal",
    "constitution",
]

KEYWORDS = [
    "genset",
    "disjoint",
    "complete",
    "general",
    "specifics",
    "where",
    "package",
    "import",
    "functional-complexes",
]

SYMBOLS = {
    'OPEN_PAREN':'(',
    'CLOSE_PAREN':')',
    'OPEN_BRACKET':'[',
    'CLOSE_BRACKET':']',
    'OPEN_BRACE':'{',
    'CLOSE_BRACE':'}',
    'RANGE':'..',
    
    'AGGREGATION':'<>--',
    'AGGREGATION_INVERSE':'--<>',
    'COMPOSITION': '<o>--',
    'COMPOSITION_INVERSE':'--<o>',
    'DOUBLE_DASH':'--',

    'MULTIPLICATION':'*',
    'AT':'@',
    'COLON':':',
}

META_ATTRIBUTES = [
    "ordered",
    "const",
    "derived",
    "subsets",
    "redefines"
]

NATIVE_TYPES = [
    "number",
    "string",
    "boolean",
    "date",
    "time",
    "datetime",
]


@dataclass
class LexerError:
    """Representa um erro encontrado durante a análise léxica"""
    line: int
    column: int
    character: str
    message: str

    def __str__(self):
        return f"Line {self.line}, Column {self.column}: {self.message} ('{self.character}')"


class Token:
    """Representa um token com informações de posição"""

    def __init__(self, type_: str, value: str, lineno: int, lexpos: int, token_pos: int):
        self.type = type_
        self.value = value
        self.lineno = lineno
        self.lexpos = lexpos
        self.token_pos = token_pos
    
    def __str__(self):
        return f"Token(type={self.type}, value={self.value}, line={self.lineno}, pos={self.token_pos})"

    def __repr__(self):
        return self.__str__()


class TontoLexer:
    """Analisador léxico para a linguagem Tonto"""

    tokens = tokens

    
    def __init__(self):
        self.errors: List[LexerError] = []
        self.lexer = None
        self._build_lexer()

    def _build_lexer(self):
        """Constrói o lexer PLY"""
        # Regras de tokens
        self.t_PACKAGE_IDENTIFIER = r"(\".+\")|(\b(?:[a-zA-Z][a-zA-Z_]*\.)*[a-zA-Z][a-zA-Z_]*Package\b)"
        self.t_CLASS_IDENTIFIER = r'\b[A-Z][_A-Za-z]*\b'
        self.t_RELATION_IDENTIFIER = r'\b[a-z]+[_a-zA-Z]*\b'
        self.t_INSTANCE_IDENTIFIER = r'\b[a-zA-Z][a-zA-Z_]*\d+\b'
        self.t_USER_TYPE = r'\b[A-Za-z]+DataType\b'

        self.t_KEYWORD = r'\b({})\b'.format('|'.join(KEYWORDS))
        self.t_CLASS_STEREOTYPE = r'\b({})\b'.format('|'.join(CLASS_STEREOTYPES))
        self.t_RELATION_STEREOTYPE = r'\b({})\b'.format('|'.join(RELATION_STEREOTYPES))
        self.t_META_ATTRIBUTES = r'\b({})\b'.format('|'.join(META_ATTRIBUTES))
        self.t_NATIVE_TYPE = r'\b({})\b'.format('|'.join(NATIVE_TYPES))

        self.t_NUMBER = r'\b\d+\b'

        # Símbolos (ordem importa para evitar conflitos)
        self.t_AGGREGATION = r'<>--'
        self.t_AGGREGATION_INVERSE = r'--<>'
        self.t_COMPOSITION = r'<o>--'
        self.t_COMPOSITION_INVERSE = r'--<o>'
        self.t_DOUBLE_DASH = r'--'
        self.t_RANGE = r'\.\.'

        self.t_OPEN_PAREN = r'\('
        self.t_CLOSE_PAREN = r'\)'
        self.t_OPEN_BRACKET = r'\['
        self.t_CLOSE_BRACKET = r'\]'
        self.t_OPEN_BRACE = r'\{'
        self.t_CLOSE_BRACE = r'\}'
        self.t_MULTIPLICATION = r'\*'
        self.t_AT = r'@'
        self.t_COLON = r':'
        self.t_COMMA = r','
        self.t_DOT = r'\.'

        # Caracteres ignorados
        self.t_ignore = ' \t'

        # Constrói o lexer
        self.lexer = lex.lex(module=self)

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        """Trata erros léxicos e os adiciona à lista de erros"""
        line = t.lexer.lineno
        column = self._get_column_position(t.lexpos)
        
        # Captura o token completo até encontrar um delimitador
        error_token = ""
        pos = 0
        
        # Define delimitadores que separam tokens
        delimiters = {' ', '\t', '\n', '\r'}
        
        # Consome caracteres até encontrar um delimitador ou fim da string
        while pos < len(t.value) and t.value[pos] not in delimiters:
            error_token += t.value[pos]
            pos += 1
        
        # Se não encontrou nenhum caractere válido, pega pelo menos um
        if not error_token:
            error_token = t.value[0]
            pos = 1
        
        message = f"Illegal token"
        
        error = LexerError(line, column, error_token, message)
        self.errors.append(error)
        
        # Cria token de erro com o token completo
        t.type = 'ERROR'
        t.value = error_token
        t.lexer.skip(pos)  # Pula todos os caracteres do token inválido
        return t

    def _get_column_position(self, lexpos: int) -> int:
        """Calcula a posição da coluna baseada na posição léxica"""
        if not hasattr(self, '_input_data'):
            return 1

        last_newline = self._input_data.rfind('\n', 0, lexpos)
        return lexpos - last_newline if last_newline != -1 else lexpos + 1

    def preprocess_input(self, data: str) -> str:
        """Remove comentários mantendo a contagem de linhas"""
        # Remove comentários de linha única
        data = re.sub(r'(\".*?\"|\'.*?\')|//.*',
                      lambda m: m.group(1) if m.group(
                          1) else '\n' * m.group(0).count('\n'),
                      data)

        # Remove comentários multilinha
        multiline_comment_pattern = r'/\*.*?\*/'
        multiline_comments = re.findall(
            multiline_comment_pattern, data, re.DOTALL)
        for comment in multiline_comments:
            num_newlines = comment.count('\n')
            data = data.replace(comment, '\n' * num_newlines)

        return data

    def tokenize(self, data: str) -> Iterator[Token]:
        """Tokeniza o input e retorna um gerador de tokens"""
        # Limpa erros anteriores
        self.errors.clear()

        # Pré-processa os dados
        processed_data = self.preprocess_input(data)
        self._input_data = processed_data 

        # Configura o lexer
        self.lexer.lineno = 1
        self.lexer.input(processed_data)

        # Gera tokens
        for tok in self.lexer:
            token_pos = self._get_column_position(tok.lexpos)

            token = Token(
                type_=tok.type,
                value=tok.value,
                lineno=tok.lineno,
                lexpos=tok.lexpos,
                token_pos=token_pos
            )

            yield token

    def get_errors(self) -> List[LexerError]:
        return self.errors.copy()

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def print_errors(self):
        if not self.errors:
            print("No lexical errors found.")
            return

        print(f"Found {len(self.errors)} lexical error(s):")
        for error in self.errors:
            print(f"  {error}")


def tokenize(data: str) -> Iterator[Token]:
    lexer = TontoLexer()
    return lexer.tokenize(data)

