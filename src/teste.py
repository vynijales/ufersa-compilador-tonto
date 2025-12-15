from parser.parser import parse_ontology
from semantic.analyzer import analyze, print_analysis_results

teste1 = """
package teste

enum Color {
    RED,
    GREEN,
    BLUE
}

enum Size { SMALL }

subkind Child specializes Person
kind Adult

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

//disjoint complete genset PersonAgeGroup where Child, Adult specializes Person
//
//genset PersonAgeGroup {
//    general Person
//    specifics Child, Adult
//}


kind House {
    color: string
}

@componentOf
relation Person [0..*] <>-- possui -- [0..*] House
"""


if __name__ == "__main__":
    ast = parse_ontology(teste1)
    st, err = analyze(ast)
    print_analysis_results(st, err)
