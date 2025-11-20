from ply import yacc
from lexer.lexer import tokens, TontoLexer
import json


def p_ontology(p):
    '''ontology : importlist package_definition classlist'''
    p[0] = {
        'imports': p[1],
        'package_name': p[2],
        'classes': p[3]
    }


def p_importlist(p):
    '''
    importlist : importlist import
               | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_import(p):
    '''import : IMPORT_KW IDENTIFIER'''
    p[0] = p[2]


def p_package_definition(p):
    '''package_definition : PACKAGE_KW IDENTIFIER'''
    p[0] = p[2]


def p_classlist(p):
    '''
    classlist : classlist class
              | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_class(p):
    '''class : CLASS_STEREOTYPE IDENTIFIER OPEN_BRACE class_body CLOSE_BRACE'''
    p[0] = {
        'class_type': p[1],
        'name': p[2],
        'content': p[4],
    }


def p_class_body(p):
    '''class_body : attr_list relation_list'''
    p[0] = {
        'attributes': p[1],
        'relations': p[2],
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
    attribute : IDENTIFIER COLON NATIVE_TYPE
              | IDENTIFIER COLON NATIVE_TYPE cardinality 
              | IDENTIFIER COLON NATIVE_TYPE cardinality meta_attributes
              | IDENTIFIER COLON NATIVE_TYPE meta_attributes
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
