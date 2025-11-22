from parser.parser import parser

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

"""

def test_parser():
    result = parser.parse(teste1)

    print ("Parser Result:", result)
    
    result_expected = {
    'package_name': 'teste',
    'imports': [],
    'declarations': [
        {
            'type': 'enum',
            'name': 'Color',
            'values': ['RED', 'GREEN', 'BLUE'],
        },
        {
            'type': 'enum',
            'name': 'Size',
            'values': ['SMALL'],
        },
        {
            'type': 'datatype',
            'name': 'AddressDataType',
            'attributes': [
                {'name': 'street', 'type': 'string'},
                {'name': 'city', 'type': 'number'},
            ],
        },
        {
            'type': 'kind',
            'name': 'Person',
            'content': {
                'atributes': [
                    {'name': 'name', 'type': 'string'},
                    {'name': 'age', 'type': 'number'},
                    {'name': 'address', 'type': 'AddressDataType'},
                ],
                'relations': [],
            },
        },
        {
            'type': 'datatype',
            'name': 'CompanyDataType',
            'attributes': [
                {'name': 'name', 'type': 'string'},
            ],
        },
    ]}

    assert result == result_expected

if __name__ == "__main__":
    test_parser()
    print("All tests passed.")
