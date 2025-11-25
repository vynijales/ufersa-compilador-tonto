import json

from parser.parser import parser

# Código de teste para verificar o parser da linguagem Tonto
teste1 = """
package teste

enum Color {
    RED,
    GREEN,
    BLUE
}

enum Size { SMALL }

datatype AddressDataType {
    street: string
    city: number
}

kind Person {
    name: string
    age: number
    address: AddressDataType
}

datatype CompanyDataType {
    name: string
}

disjoint complete genset PersonAgeGroup where Child, Adult specializes Person

genset PersonAgeGroup {
    general Person
    specifics Child, Adult
}


kind House {
    color: string
}

@componentOf
relation Person [0..*] <>-- possui -- [0..*] House
"""


if __name__ == "__main__":
    # Executa o parser com o código de teste e exibe o resultado
    result = parser.parse(teste1)
    print("Parser Result:", json.dumps(result, indent=4))
