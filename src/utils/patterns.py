import re
from ..tokens.token_types import Token

class PATTERNS:
    # Padrões regex para identificadores
    CLASS_NAME = re.compile(r'[A-Z][a-zA-Z]*(_[a-zA-Z]+)*[a-zA-Z]*')
    RELATION_NAME = re.compile(r'[a-z][a-zA-Z]*(_[a-zA-Z]+)*[a-zA-Z]*')
    INSTANCE_NAME = re.compile(r'[a-zA-Z][a-zA-Z_]*(_[a-zA-Z]+)*\d+')
    DATATYPE_NAME = re.compile(r'[a-zA-Z]+DataType')
    IDENTIFIER = re.compile(r'[a-zA-Z_][a-zA-Z_0-9]*')
    NUMBER = re.compile(r'\d+')
    STRING = re.compile(r'\"([^\\\n]|(\\.))*?\"')
    COMMENT = re.compile(r'\#.*')
    
    # Símbolos especiais
    SYMBOLS = {
        '{': Token.LBRACE,
        '}': Token.RBRACE, 
        '(': Token.LPAREN,
        ')': Token.RPAREN,
        '[': Token.LBRACKET,
        ']': Token.RBRACKET,
        '..': Token.DOUBLE_DOT,
        '<>--': Token.DIAMOND_LEFT,
        '--<>': Token.DIAMOND_RIGHT,
        '*': Token.ASTERISK,
        '@': Token.AT,
        ':': Token.COLON
    }
