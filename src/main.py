import os

from lexer import lexer

def parse(data):
    lexer.lineno = 1
    lexer.input(data)
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(tok)
    return tokens


def main():
    files = []

    for root, _, filenames in os.walk('exemplos'):
        for filename in filenames:
            if filename.endswith('.tonto'):
                files.append(os.path.join(root, filename))
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
            print(f'Parsing: {file_path}')

            tokens = parse(data)
            for token in tokens:
                print(token)
            
            print('-'*40 + '\n')

if __name__ == '__main__':
    main()
