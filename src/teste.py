from parser.parser import parse_ontology
from semantic.analyzer import analyze, print_analysis_results


if __name__ == "__main__":
    with open("exemplos/unidade-3/Hospital_Mono.tonto", "r") as f:
        teste1 = f.read()
    ast = parse_ontology(teste1)
    st, err = analyze(ast)
    print_analysis_results(st, err)
