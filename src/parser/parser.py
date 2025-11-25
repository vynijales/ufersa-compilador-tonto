from ply import yacc
from lexer.lexer import tokens, TontoLexer

# =========== Ontology ===========

# Regra principal que define a estrutura de uma ontologia
def p_ontology(p):
    '''ontology : package imports declarations'''
    p[0] = {
        'package_name': p[1],
        'imports': p[2],
        'declarations': p[3],
    }


# Lista de declarações (classes, enums, gensets, etc.)
def p_declarations(p):
    '''
    declarations : declarations declaration
                 | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# Define os tipos de declaração válidos na linguagem
def p_declaration(p):
    '''declaration : datatype_declaration
                   | class_declaration
                   | enum_declaration
                   | genset_declaration
                   | relation_external
    '''
    p[0] = p[1]


# Declaração de tipo de dados personalizado
def p_datatype_declarion(p):
    '''datatype_declaration : DATATYPE_KW USER_TYPE OPEN_BRACE attr_list CLOSE_BRACE'''
    p[0] = {
        'type': 'datatype',
        'name': p[2],
        'attributes': p[4],
    }


# Tipos de dados (nativos ou definidos pelo usuário)
def p_datatype(p):
    '''datatype : NATIVE_TYPE
                | USER_TYPE
    '''
    p[0] = p[1]


# Lista de imports de outros pacotes
def p_imports(p):
    '''
    imports : imports import
            | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# Declaração de import de um pacote
def p_import(p):
    '''import : IMPORT_KW IDENTIFIER'''
    p[0] = p[2]


# Declaração do nome do pacote
def p_package(p):
    '''package : PACKAGE_KW IDENTIFIER'''
    p[0] = p[2]

# ============== Class ==============

# Declaração de classe
def p_class_declaration(p):
    '''class_declaration : CLASS_STEREOTYPE IDENTIFIER optional_class_body'''
    p[0] = {
        'type': p[1],
        'name': p[2],
        'content': p[3],
    }


# Declaração de classe com herança/especialização
def p_class_specialization(p):
    '''class_declaration : CLASS_STEREOTYPE IDENTIFIER SPECIALIZES_KW IDENTIFIER optional_class_body'''
    p[0] = {
        'type': p[1],
        'name': p[2],
        'specializes': p[4],
        'content': p[5],
    }


# Corpo opcional da classe com atributos e relações
def p_optional_class_body(p):
    '''optional_class_body : OPEN_BRACE attr_list relation_list CLOSE_BRACE
                           | empty
    '''
    if len(p) == 5:
        p[0] = {
            'atributes': p[2],
            'relations': p[3],
        }
    else:
        p[0] = {
            'atributes': [],
            'relations': [],
        }


# Lista de atributos de uma classe
def p_attr_list(p):
    '''
    attr_list : attr_list attribute
              | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# Declaração de atributo em uma classe com tipo e metadados opcionais
def p_attribute(p):
    '''
    attribute : IDENTIFIER COLON datatype
              | IDENTIFIER COLON datatype cardinality
              | IDENTIFIER COLON datatype cardinality meta_attributes
              | IDENTIFIER COLON datatype meta_attributes
    '''
    p[0] = {
        'name': p[1],
        'type': p[3],
    }


# Metaatributos como ordered, const, derived, etc.
def p_meta_attributes(p):
    '''meta_attributes : OPEN_BRACE META_ATTRIBUTES CLOSE_BRACE'''
    p[0] = p[2]


# Lista de relações internas de uma classe
def p_relation_list(p):
    '''
    relation_list : relation_list relation_internal
                  | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_relation(p):
    '''relation : cardinality DOUBLE_DASH cardinality IDENTIFIER'''
    p[0] = {
        'name': p[4],
        'cardinality_from': p[1],
        'cardinality_to': p[3],
    }


# Define cardinalidade de atributos e relações
def p_cardinality(p):
    '''cardinality : OPEN_BRACKET MULTIPLICATION CLOSE_BRACKET
                   | OPEN_BRACKET NUMBER CLOSE_BRACKET
                   | OPEN_BRACKET NUMBER RANGE NUMBER CLOSE_BRACKET
                   | OPEN_BRACKET NUMBER RANGE MULTIPLICATION CLOSE_BRACKET
    '''
    # Retorna uma representação de string ou objeto da cardinalidade
    p[0] = ''.join(p[1:])

# =============== Enum ===============

# Declaração de enumeração
def p_enum_declaration(p):
    '''enum_declaration : ENUM_KW IDENTIFIER OPEN_BRACE enum_values CLOSE_BRACE'''
    p[0] = {
        'type': 'enum',
        'name': p[2],
        'values': p[4],
    }


# Valor individual de uma enumeração
def p_enum_value(p):
    '''enum_value : IDENTIFIER'''
    p[0] = p[1]


# Lista de valores de enumeração separados por vírgula
def p_enum_values(p):
    '''
    enum_values : enum_values COMMA enum_value
                | enum_value
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# ============== Genset ==============


# Declaração de genset (conjunto de generalização)
def p_genset_declaration(p):
    '''genset_declaration : GENSET_KW IDENTIFIER OPEN_BRACE GENERAL_KW IDENTIFIER SPECIFICS_KW comma_separated_identifiers CLOSE_BRACE'''
    p[0] = {
        'type': 'genset',
        'genset_restrictions': [],
        'name': p[2],
        'specifics': p[7],
        'general': p[5],
    }


# Declaração de genset na forma inline com restrições
def p_genset_declaration_inline(p):
    '''genset_declaration : optional_genset_restrictions GENSET_KW IDENTIFIER WHERE_KW comma_separated_identifiers SPECIALIZES_KW IDENTIFIER'''
    p[0] = {
        'type': 'genset',
        'genset_restrictions': p[1],
        'name': p[3],
        'specifics': p[5],
        'general': p[7],
    }


# Lista opcional de restrições de genset (disjoint, complete, etc.)
def p_optional_genset_restrictions(p):
    '''
    optional_genset_restrictions : optional_genset_restrictions genset_restriction
                                 | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# Restrições aplicáveis a gensets
def p_genset_restriction(p):
    '''
    genset_restriction : DISJOINT_KW
                       | COMPLETE_KW
                       | INCOMPLETE_KW
                       | OVERLAPPING_KW
    '''
    p[0] = p[1]


# Descrição: Essa regra define uma produção em que deve haver ao menos um
# identificador. Se houver mais que um, devem estar separados por vírgula
def p_comma_separated_identifiers(p):
    '''
    comma_separated_identifiers : comma_separated_identifiers COMMA IDENTIFIER
                                | IDENTIFIER
    '''

    if len(p) == 4:
        # Regra -> comma_separated_identifiers : comma_separated_identifiers COMMA IDENTIFIER
        p[0] = p[1] + [p[3]]
    else:
        # Regra -> comma_separated_identifiers : IDENTIFIER
        p[0] = [p[1]]


def p_empty(p):
    '''empty :'''
    pass


# Trata erros sintáticos durante o parsing
def p_error(p):
    if p:
        print(f"Syntax error at {p.value!r} in line {p.lineno}")
        print(f'Token type: {p.type}')
    else:
        print("Syntax error: Unexpected end of input")


lexer = TontoLexer()
parser = yacc.yacc()
