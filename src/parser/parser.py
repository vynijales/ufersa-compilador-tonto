from ply import yacc
from lexer.lexer import tokens, TontoLexer
import json


def p_ontology(p):
    '''ontology : package imports declarations'''

    p[0] = {
        'package_name': p[1],
        'imports': p[2],
        'declarations': p[3],
    }


def p_declarations(p):
    '''
    declarations : declarations declaration
                 | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_declaration(p):
    '''declaration : datatype_declaration
                   | class_declaration
                   | enum_declaration
    '''
    p[0] = p[1]

def p_datatype_declarion(p):
    '''datatype_declaration : DATATYPE_KW USER_TYPE OPEN_BRACE attr_list CLOSE_BRACE'''
    p[0] = {
        'type': 'datatype',
        'name': p[2],
        'attributes': p[4],
    }

def p_datatype(p):
    '''datatype : NATIVE_TYPE
                | USER_TYPE
    '''
    p[0] = p[1]

def p_imports(p):
    '''
    imports : imports import
            | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_import(p):
    '''import : IMPORT_KW IDENTIFIER'''
    p[0] = p[2]


def p_package(p):
    '''package : PACKAGE_KW IDENTIFIER'''
    p[0] = p[2]

def p_class_declaration(p):
    '''class_declaration : CLASS_STEREOTYPE IDENTIFIER optional_class_body'''
    p[0] = {
        'type': p[1],
        'name': p[2],
        'content': p[3],
    }

def p_class_specialization(p):
    '''class_declaration : CLASS_STEREOTYPE IDENTIFIER SPECIALIZES_KW IDENTIFIER optional_class_body'''
    p[0] = {
        'type': p[1],
        'name': p[2],
        'specializes': p[4],
        'content': p[5],
    }


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

def p_attr_list(p):
    '''
    attr_list : attr_list attribute
              | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


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


def p_meta_attributes(p):
    '''meta_attributes : OPEN_BRACE META_ATTRIBUTES CLOSE_BRACE'''
    p[0] = p[2]


def p_relation_list(p):
    '''
    relation_list : relation_list relation
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


def p_cardinality(p):
    '''cardinality : OPEN_BRACKET MULTIPLICATION CLOSE_BRACKET
                   | OPEN_BRACKET NUMBER CLOSE_BRACKET
                   | OPEN_BRACKET NUMBER RANGE NUMBER CLOSE_BRACKET
                   | OPEN_BRACKET NUMBER RANGE MULTIPLICATION CLOSE_BRACKET
    '''
    # Retorna uma representação de string ou objeto da cardinalidade
    p[0] = ''.join(p[1:])


def p_enum_declaration(p):
    '''enum_declaration : ENUM_KW IDENTIFIER OPEN_BRACE enum_values CLOSE_BRACE'''
    p[0] = {
        'type': 'enum',
        'name': p[2],
        'values': p[4],
    }

def p_enum_value(p):
    '''enum_value : IDENTIFIER'''
    p[0] = p[1]

def p_enum_values(p):
    '''
    enum_values : enum_values COMMA enum_value
                | enum_value
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]
    

def p_empty(p):
    '''empty :'''
    pass


def p_error(p):
    if p:
        print(f"Syntax error at {p.value!r} in line {p.lineno}")
        print(f'Token type: {p.type}')
    else:
        print("Syntax error: Unexpected end of input")
    

lexer = TontoLexer()
parser = yacc.yacc()
