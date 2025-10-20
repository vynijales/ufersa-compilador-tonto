from .token_types import Token

# Estereótipos de classe
STEREOTYPES_CLASSES = {
    'event': Token.EVENT,
    'situation': Token.SITUATION, 
    'process': Token.PROCESS,
    'category': Token.CATEGORY,
    'mixin': Token.MIXIN,
    'phasemixin': Token.PHASE_MIXIN,
    'rolemixin': Token.ROLE_MIXIN,
    'historicalrolemixin': Token.HISTORICAL_ROLE_MIXIN,
    'kind': Token.KIND,
    'collective': Token.COLLECTIVE,
    'quantity': Token.QUANTITY,
    'quality': Token.QUALITY,
    'mode': Token.MODE,
    'intrinsicmode': Token.INTRINSIC_MODE,
    'extrinsicmode': Token.EXTRINSIC_MODE,
    'subkind': Token.SUBCLASS_KIND,
    'phase': Token.PHASE,
    'role': Token.ROLE,
    'historicalrole': Token.HISTORICAL_ROLE
}

# Estereótipos de relações
STEREOTYPES_RELATIONS = {
    'material': Token.MATERIAL,
    'derivation': Token.DERIVATION,
    'comparative': Token.COMPARATIVE,
    'mediation': Token.MEDIATION,
    'characterization': Token.CHARACTERIZATION,
    'externaldependence': Token.EXTERNAL_DEPENDENCE,
    'componentof': Token.COMPONENT_OF,
    'memberof': Token.MEMBER_OF,
    'subcollectionof': Token.SUBCOLLECTION_OF,
    'subqualityof': Token.SUBQUALITY_OF,
    'instantiation': Token.INSTANTIATION,
    'termination': Token.TERMINATION,
    'participational': Token.PARTICIPATIONAL,
    'participation': Token.PARTICIPATION,
    'historicaldependence': Token.HISTORICAL_DEPENDENCE,
    'creation': Token.CREATION,
    'manifestation': Token.MANIFESTATION,
    'bringsabout': Token.BRINGS_ABOUT,
    'triggers': Token.TRIGGERS,
    'composition': Token.COMPOSITION,
    'aggregation': Token.AGGREGATION,
    'inherence': Token.INHERENCE,
    'value': Token.VALUE,
    'formal': Token.FORMAL,
    'constitution': Token.CONSTITUTION
}

# Palavras reservadas
RESERVED_WORDS = {
    'genset': Token.GENSET,
    'disjoint': Token.DISJOINT,
    'complete': Token.COMPLETE,
    'general': Token.GENERAL,
    'specifics': Token.SPECIFICS,
    'where': Token.WHERE,
    'package': Token.PACKAGE
}

# Tipos de dados nativos
DATA_TYPES = {
    'number': Token.NUMBER_TYPE,
    'string': Token.STRING_TYPE,
    'boolean': Token.BOOLEAN_TYPE,
    'date': Token.DATE_TYPE,
    'time': Token.TIME_TYPE,
    'datetime': Token.DATETIME_TYPE
}

# Meta-atributos
META_ATTRIBUTES = {
    'ordered': Token.ORDERED,
    'const': Token.CONST,
    'derived': Token.DERIVED,
    'subsets': Token.SUBSETS,
    'redefines': Token.REDEFINES
}

# Combinar todos os dicionários de palavras-chave
KEYWORDS = {}
KEYWORDS.update(STEREOTYPES_CLASSES)
KEYWORDS.update(STEREOTYPES_RELATIONS)
KEYWORDS.update(RESERVED_WORDS)
KEYWORDS.update(DATA_TYPES)
KEYWORDS.update(META_ATTRIBUTES)
