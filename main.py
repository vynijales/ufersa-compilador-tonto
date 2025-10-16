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
    'intrisicMode',
    'extrinsicMode',
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
    ":"
]

META_ATTRIBUTES = [
    "ordered",
    "const",
    "derived",
    "subsets",
    "redefines"
]

"""
Convenção para nomes de classes: iniciando com letra maiúscula, seguida por qualquer
combinação de letras, ou tendo sublinhado como subcadeia própria, sem números. Exemplos:
Person, Child, Church, University, Second_Baptist_Church.
"""
t_CLASS_IDENTIFIER = r'[A-Z][a-z]+(_[A-Z][a-z]+)*'

"""
Convenção para nomes de relações: começando com letra minúscula, seguida por qualquer
combinação de letras, ou tendo sublinhado como subcadeia própria, sem números. Exemplos:
has, hasParent, has_parent, isPartOf, is_part_of.
"""
t_RELATION_IDENTIFIER = r'[a-z][a-z]*(_[a-z][a-z]*)*'

"""
Convenção para nomes de instâncias: iniciando com qualquer letra, podendo ter o sublinhado
como subcadeia própria e terminando com algum número inteiro. Exemplos: Planeta1, Planeta2,
pizza03, pizza123
"""
t_INSTANCE_IDENTIFIER = r'[A-Za-z][A-Za-z]*(_[A-Za-z][A-Za-z]*)*\d+'
