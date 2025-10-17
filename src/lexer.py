from ply import lex

tokens = (
    'CLASS_STEREOTYPE',
    'RELATION_STEREOTYPE',
    'KEYWORD',
    'SYMBOL',

    'CLASS_IDENTIFIER',
    'RELATION_IDENTIFIER',
    'INSTANCE_IDENTIFIER',

    'NATIVE_TYPE',
    'USER_TYPE',
    'META_ATTRIBUTES',

    'NUMBER',
    'COMMA',
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
    'intrinsic-mode',    # Para compatibilidade com versões antigas
    'extrinsic-mode',    # Para compatibilidade com versões antigas
    'subkind',
    'phase',
    'role',
    'historicalRole',
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

SYMBOLS = [
    "{",
    "}",
    "(",
    ")",
    "[",
    "]",
    "..",
    "<>--",
    "--<>",
    "*",
    "@",
    ":",
    '--',
]

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
Convenção para nomes de classes: iniciando com letra maiúscula, seguida por qualquer
combinação de letras, ou tendo sublinhado como subcadeia própria, sem números. Exemplos:
Person, Child, Church, University, Second_Baptist_Church.
"""
t_CLASS_IDENTIFIER = r'[A-Z][_A-Za-z]*'

"""
Convenção para nomes de relações: começando com letra minúscula, seguida por qualquer
combinação de letras, ou tendo sublinhado como subcadeia própria, sem números. Exemplos:
has, hasParent, has_parent, isPartOf, is_part_of.
"""
t_RELATION_IDENTIFIER = r'[a-z]+[_a-z]*'

"""
Convenção para nomes de instâncias: iniciando com qualquer letra, podendo ter o sublinhado
como subcadeia própria e terminando com algum número inteiro. Exemplos: Planeta1, Planeta2,
pizza03, pizza123
"""
t_INSTANCE_IDENTIFIER = r'[a-zA-Z][a-zA-Z_]*\d+'


t_KEYWORD = r'\b({})\b'.format('|'.join(KEYWORDS))
t_SYMBOL = r'|'.join([r'\{}'.format(sym) for sym in SYMBOLS])
t_CLASS_STEREOTYPE = r'|'.join(CLASS_STEREOTYPES)
t_RELATION_STEREOTYPE = r'|'.join(RELATION_STEREOTYPES)
t_META_ATTRIBUTES = r'|'.join(META_ATTRIBUTES)
t_NATIVE_TYPE = r'|'.join(NATIVE_TYPES)

t_NUMBER = r'\d+'
t_COMMA = r','

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()
