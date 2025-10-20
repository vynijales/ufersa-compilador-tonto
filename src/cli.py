import os

from lexer.lexer import tokenize


def tokenize_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    tokens = tokenize(content)

    print(f'\nProcessando arquivo: {file_path}:\n')
    for token in tokens:
        print(token)
    print('\n')


def main():
    while True:
        user_input = input('Digite o caminho do arquivo (.tonto) ou "sair" para encerrar: ')
        if user_input.lower() == 'sair':
            return
        elif os.path.isfile(user_input) and user_input.endswith('.tonto'):
            tokenize_file(user_input)
        else:
            print('Caminho inválido ou arquivo não é .tonto. Tente novamente.\n')
        print('-' * 40 + '\n')


if __name__ == '__main__':
    main()
