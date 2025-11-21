from ply import lex
from typing import List, Iterator, Dict
from dataclasses import dataclass

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

KEYWORDS = {
    "genset": "GENSET_KW",
    "disjoint": "DISJOINT_KW",
    "complete": "COMPLETE_KW",
    "general": "GENERAL_KW",
    "specifics": "SPECIFICS_KW",
    "where": "WHERE_KW",
    "package": "PACKAGE_KW",
    "import": "IMPORT_KW",
    "specializes": "SPECIALIZES_KW",
    "datatype": "DATATYPE_KW",
    "enum": "ENUM_KW",
}

CLASS_STEREOTYPES = [
    'event', 'situation', 'process', 'category', 'mixin', 'phaseMixin',
    'roleMixin', 'historicalRoleMixin', 'kind', 'collective', 'quantity',
    'quality', 'mode', 'intrinsicMode', 'extrinsicMode', 'subkind', 'phase',
    'role', 'historicalRole'
]

RELATION_STEREOTYPES = [
    "material", "derivation", "comparative", "mediation", "characterization",
    "externalDependence", "componentOf", "memberOf", "subCollectionOf",
    "subQualityOf", "instantiation", "termination", "participational",
    "participation", "historicalDependence", "creation", "manifestation",
    "bringsAbout", "triggers", "composition", "aggregation", "inherence",
    "value", "formal", "constitution", "relation"
]

META_ATTRIBUTES = ["ordered", "const", "derived", "subsets", "redefines"]
NATIVE_TYPES = ["number", "string", "boolean", "date", "time", "datetime"]

# Termos com hífens exigem tratamento especial regex para não quebrar no '-'
HYPHENATED_TERMS = {
    "functional-complexes": "FUNCTIONAL_COMPLEXES_KW",
    "intrinsic-modes": "CLASS_STEREOTYPE", # Legado
    "extrinsic-modes": "CLASS_STEREOTYPE", # Legado
    "intrinsic-mode": "CLASS_STEREOTYPE",  # Legado
    "extrinsic-mode": "CLASS_STEREOTYPE",  # Legado
}

# Construção do Mapa de Palavras Reservadas
RESERVED: Dict[str, str] = KEYWORDS.copy()

for s in CLASS_STEREOTYPES:
    RESERVED[s] = 'CLASS_STEREOTYPE'
for s in RELATION_STEREOTYPES:
    RESERVED[s] = 'RELATION_STEREOTYPE'
for s in META_ATTRIBUTES:
    RESERVED[s] = 'META_ATTRIBUTES'
for s in NATIVE_TYPES:
    RESERVED[s] = 'NATIVE_TYPE'

# Lista de Tokens
tokens = [
    'CLASS_STEREOTYPE',
    'RELATION_STEREOTYPE',
    'IDENTIFIER',
    'NATIVE_TYPE',
    'USER_TYPE',
    'META_ATTRIBUTES',
    'NUMBER',
    'COMMA',
    'DOT',
    'COLON',
    'OPEN_PAREN',
    'CLOSE_PAREN',
    'OPEN_BRACKET',
    'CLOSE_BRACKET',
    'OPEN_BRACE',
    'CLOSE_BRACE',
    'RANGE',
    'MULTIPLICATION',
    'AT',
    'AGGREGATION',
    'AGGREGATION_INVERSE',
    
    'COMPOSITION',
    'COMPOSITION_INVERSE',
    'DOUBLE_DASH',
    'FUNCTIONAL_COMPLEXES_KW',
    'ERROR'
] + list(set(KEYWORDS.values()))


@dataclass
class LexerError:
    line: int
    column: int
    character: str
    message: str

    def __str__(self):
        return f"Line {self.line}, Column {self.column}: {self.message} ('{self.character}')"


@dataclass
class Token:
    type: str
    value: str
    lineno: int
    lexpos: int
    token_pos: int

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.lineno}, col={self.token_pos})"


class TontoLexer:
    tokens = tokens

    # Regras de String (Prioridade baseada no tamanho do regex pelo PLY)
    # Operadores complexos devem vir antes de simples (ex: <>-- antes de <)
    t_AGGREGATION = r'<>--'
    t_AGGREGATION_INVERSE = r'--<>'
    t_COMPOSITION = r'<o>--'
    t_COMPOSITION_INVERSE = r'--<o>'
    t_DOUBLE_DASH = r'--'
    t_RANGE = r'\.\.'
    
    t_OPEN_PAREN = r'\('
    t_CLOSE_PAREN = r'\)'
    t_OPEN_BRACKET = r'\['
    t_CLOSE_BRACKET = r'\]'
    t_OPEN_BRACE = r'\{'
    t_CLOSE_BRACE = r'\}'
    t_MULTIPLICATION = r'\*'
    t_AT = r'@'
    t_COLON = r':'
    t_COMMA = r','
    t_DOT = r'\.'
    t_NUMBER = r'\d+'

    t_ignore = ' \t'

    def __init__(self):
        self.errors: List[LexerError] = []
        self.lexer = lex.lex(module=self)
        self._input_data = ""

    # Regras de Função (Prioridade Alta)
    def t_COMMENT_MULTILINE(self, t):
        r'/\*.*?\*/'
        t.lexer.lineno += t.value.count('\n')
        pass #

    def t_COMMENT_SINGLE(self, t):
        r'//.*'
        pass 

    # Termos com hífen (exceções que contêm '-')
    # Esta regra deve vir antes de t_IDENTIFIER para não quebrar no hífen
    def t_HYPHENATED_ID(self, t):
        r'[a-zA-Z][a-zA-Z0-9]*(-[a-zA-Z0-9]+)+'
        # Verifica se é um termo conhecido com hífen
        if t.value in HYPHENATED_TERMS:
            t.type = HYPHENATED_TERMS[t.value]
            return t
        
        error_msg = f"Illegal hyphenated identifier '{t.value}'"
        self._add_error(t, error_msg)
        t.type = 'ERROR'
        return t

    # Identificadores e Palavras Reservadas Genéricas
    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        # Verifica se a palavra está no dicionário de reservados
        # Se estiver, muda o tipo (ex: de IDENTIFIER para CLASS_STEREOTYPE)
        t.type = RESERVED.get(t.value, 'IDENTIFIER')
        
        # Regra especial para UserTypes (PascalCase terminando em DataType)
        if t.type == 'IDENTIFIER' and t.value.endswith('DataType') and t.value[0].isupper():
            t.type = 'USER_TYPE'
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        self._add_error(t, "Illegal character")
        t.lexer.skip(1)

    def _add_error(self, t, msg):
        col = self._get_column_position(t.lexpos)
        self.errors.append(LexerError(t.lineno, col, t.value[0], msg))

    def _get_column_position(self, lexpos: int) -> int:
        if not self._input_data: return 0
        last_newline = self._input_data.rfind('\n', 0, lexpos)
        return lexpos - last_newline if last_newline != -1 else lexpos + 1

    def tokenize(self, data: str) -> Iterator[Token]:
        self.errors.clear()
        self._input_data = data
        self.lexer.lineno = 1
        self.lexer.input(data)

        for tok in self.lexer:
            if tok.type == 'ERROR': continue
            
            yield Token(
                type=tok.type,
                value=tok.value,
                lineno=tok.lineno,
                lexpos=tok.lexpos,
                token_pos=self._get_column_position(tok.lexpos)
            )


def tokenize(data: str) -> Iterator[Token]:
    lexer = TontoLexer()
    return lexer.tokenize(data)
