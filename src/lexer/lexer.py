from ply import lex
import re

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

"""
Formato para nomes de pacotes: iniciando com letra Maiúscula, podendo conter letras minúsculas,
e tendo sublinhado como subcadeia própria, sem números. Pode conter múltiplos níveis separados por ponto.
Devendo ser terminado com a subcadeia "Package".
Exemplos:
    LivingThings.HumanPackage
    Geography.PlanetPackage
    Company.Department.SubDepartmentPackage
"""
t_PACKAGE_IDENTIFIER = r'([A-Z][a-zA-Z]*(_[A-Za-z]+)*\.)*([A-Z][a-zA-Z]*(_[A-Za-z]+)*)Package'

"""
Convenção para nomes de classes: iniciando com letra maiúscula, seguida por qualquer
combinação de letras, ou tendo sublinhado como subcadeia própria, sem números.
Exemplos:
    Person, Child, Church, University, Second_Baptist_Church.
"""
t_CLASS_IDENTIFIER = r'[A-Z][_A-Za-z]*'

"""
Convenção para nomes de relações: começando com letra minúscula, seguida por qualquer
combinação de letras, ou tendo sublinhado como subcadeia própria, sem números.
Exemplos:
    has, hasParent, has_parent, isPartOf, is_part_of.
"""
t_RELATION_IDENTIFIER = r'[a-z]+[_a-zA-Z]*'

"""
Convenção para nomes de instâncias: iniciando com qualquer letra, podendo ter o sublinhado
como subcadeia própria e terminando com algum número inteiro.
Exemplos:
    Planeta1, Planeta2, pizza03, pizza123
"""
t_INSTANCE_IDENTIFIER = r'[a-zA-Z][a-zA-Z_]*\d+'

"""
Novos tipos: iniciando com letra, sem números, sem sublinhado e terminando com a subcadeia
“DataType”. 
Exemplo: 
    CPFDataType, PhoneNumberDataType.
"""
t_USER_TYPE = r'[A-Za-z]+DataType'

t_KEYWORD = r'\b({})\b'.format('|'.join(KEYWORDS))
t_CLASS_STEREOTYPE = r'\b({})\b'.format('|'.join(CLASS_STEREOTYPES))
t_RELATION_STEREOTYPE = r'\b({})\b'.format('|'.join(RELATION_STEREOTYPES))
t_META_ATTRIBUTES = r'\b({})\b'.format('|'.join(META_ATTRIBUTES))
t_NATIVE_TYPE = r'\b({})\b'.format('|'.join(NATIVE_TYPES))

t_NUMBER = r'\d+'

t_OPEN_PAREN = r'\('
t_CLOSE_PAREN = r'\)'
t_OPEN_BRACKET = r'\['
t_CLOSE_BRACKET = r'\]'
t_OPEN_BRACE = r'\{'
t_CLOSE_BRACE = r'\}'
t_RANGE = r'\.\.'

t_DOUBLE_DASH = r'--'
t_AGGREGATION = r'<>--'
t_AGGREGATION_INVERSE = r'--<>'
t_COMPOSITION = r'<o>--'
t_COMPOSITION_INVERSE = r'--<o>'

t_MULTIPLICATION = r'\*'
t_AT = r'@'
t_COLON = r':'
t_COMMA = r','

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'


# Error handling rule
def t_error(t):
    print(f"Illegal character '{t.value[0]}', Line: {t.lexer.lineno}")
    t.type = 'ERROR'
    t.value = t.value[0]
    t.lexer.skip(1)
    return t


# Build the lexer
lexer = lex.lex()


def preprocess_input(data):
    # Remove comentários substituindo-os por espaços em branco para manter a contagem correta de linhas
    data = re.sub(r'//[^\n]*', '', data)          # Comentários de uma linha

    # Comentários multilinha
    multiline_comment_pattern = r'/\*.*?\*/'  
    multiline_comments = re.findall(multiline_comment_pattern, data, re.DOTALL)
    for comment in multiline_comments:
        num_newlines = comment.count('\n')
        data = data.replace(comment, '\n' * num_newlines)
    
    return data 

def tokenize(data):
    data = preprocess_input(data)

    lexer.lineno = 1
    lexer.input(data)
    
    for tok in lexer:
        # criar atributo "token_pos" para armazenar a posição do token na linha
        tok.token_pos = tok.lexpos - data.rfind('\n', 0, tok.lexpos)

        # retornar o token
        yield tok
