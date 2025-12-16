from dataclasses import dataclass
from typing import Any, Dict, List

from ply import yacc

from lexer.lexer import (
    Token,
    TontoLexer,
    tokens,
)
from parser.utils import find_similar_token, generate_smart_suggestion

_ = Token, tokens

errors = []
warnings = []

@dataclass
class ParseError:
    """Representa um erro léxico ou sintático encontrado durante o parsing"""
    line: int
    column: int
    message: str
    error_type: str  # 'LEXICAL' ou 'SYNTACTIC'
    suggestion: str = ""

    def __str__(self):
        error_label = "ERRO LÉXICO" if self.error_type == "LEXICAL" else "ERRO SINTÁTICO"
        result = f"[{error_label} - Linha {self.line}, Coluna {self.column}]\n"
        result += f"  Mensagem: {self.message}"
        if self.suggestion:
            result += f"\n  Sugestão: {self.suggestion}"
        return result


class OntologySummary:
    """Coleta estatísticas sobre os construtos da ontologia"""
    def __init__(self):
        self.package_name: str = None
        self.imports: List[str] = []
        self.classes: Dict[str, Dict] = {}  # {nome: {stereotype, attributes, relations, specializes}}
        self.datatypes: List[str] = []
        self.enums: Dict[str, List[str]] = {}  # {nome: [valores]}
        self.gensets: List[Dict] = []
        self.external_relations: List[Dict] = []

    def add_class(self, name: str, stereotype: str, specializes=None, category=None):
        if name not in self.classes:
            self.classes[name] = {
                'stereotype': stereotype,
                'category': category,
                'attributes': [],
                'relations': [],
                'specializes': specializes
            }

    def add_attribute_to_class(self, class_name: str, attr_name: str, attr_type: str):
        if class_name in self.classes:
            self.classes[class_name]['attributes'].append({'name': attr_name, 'type': attr_type})

    def add_relation_to_class(self, class_name: str, relation: Dict):
        if class_name in self.classes:
            self.classes[class_name]['relations'].append(relation)

    def get_summary_table(self) -> str:
        """Gera tabela de síntese formatada"""
        lines = []
        lines.append("="*80)
        lines.append("TABELA DE SÍNTESE DA ONTOLOGIA")
        lines.append("="*80)

        # Pacote
        if self.package_name:
            lines.append(f"\nPACOTE: {self.package_name}")
        else:
            lines.append("\nPACOTE: (não declarado)")

        # Imports
        lines.append(f"\nIMPORTS ({len(self.imports)}):")
        if self.imports:
            for imp in self.imports:
                lines.append(f"  - {imp}")
        else:
            lines.append("  (nenhum)")

        # Classes
        lines.append(f"\nCLASSES ({len(self.classes)}):")
        if self.classes:
            for class_name, class_info in self.classes.items():
                stereotype_str = class_info['stereotype']
                if class_info.get('category'):
                    stereotype_str += f" of {class_info['category']}"
                lines.append(f"\n  • {class_name} [{stereotype_str}]")
                if class_info['specializes']:
                    lines.append(f"    Especializa: {class_info['specializes']}")
                lines.append(f"    Atributos ({len(class_info['attributes'])}):")
                for attr in class_info['attributes']:
                    lines.append(f"      - {attr['name']}: {attr['type']}")
                lines.append(f"    Relações internas ({len(class_info['relations'])}):")
                for rel in class_info['relations']:
                    lines.append(f"      - {rel['relation_stereotype']} -> {rel['image']}")
        else:
            lines.append("  (nenhuma)")

        # Datatypes
        lines.append(f"\nDATATYPES ({len(self.datatypes)}):")
        if self.datatypes:
            for dt in self.datatypes:
                lines.append(f"  - {dt}")
        else:
            lines.append("  (nenhum)")

        # Enums
        lines.append(f"\nENUMS ({len(self.enums)}):")
        if self.enums:
            for enum_name, values in self.enums.items():
                lines.append(f"  • {enum_name}: {', '.join(values)}")
        else:
            lines.append("  (nenhum)")

        # Gensets
        lines.append(f"\nGENERALIZATION SETS ({len(self.gensets)}):")
        if self.gensets:
            for genset in self.gensets:
                restrictions = ', '.join(genset['genset_restrictions']) if genset['genset_restrictions'] else 'nenhuma'
                lines.append(f"  • {genset['name']}: {genset['general']} -> {', '.join(genset['specifics'])}")
                lines.append(f"    Restrições: {restrictions}")
        else:
            lines.append("  (nenhum)")

        # Relações externas
        lines.append(f"\nRELAÇÕES EXTERNAS ({len(self.external_relations)}):")
        if self.external_relations:
            for rel in self.external_relations:
                lines.append(f"  • {rel['relation_stereotype']}: {rel['domain']} -> {rel['image']}")
        else:
            lines.append("  (nenhuma)")

        lines.append("\n" + "="*80)
        return "\n".join(lines)


class ErrorReport:
    """Gerencia o relatório de erros léxicos e sintáticos"""
    def __init__(self):
        self.lexical_errors: List[ParseError] = []
        self.syntactic_errors: List[ParseError] = []

    def add_lexical_error(self, line: int, column: int, message: str, suggestion: str = ""):
        self.lexical_errors.append(ParseError(line, column, message, "LEXICAL", suggestion))

    def add_syntactic_error(self, line: int, column: int, message: str, suggestion: str = ""):
        self.syntactic_errors.append(ParseError(line, column, message, "SYNTACTIC", suggestion))

    def has_errors(self) -> bool:
        return len(self.lexical_errors) > 0 or len(self.syntactic_errors) > 0

    def get_error_report(self) -> str:
        """Gera relatório de erros formatado"""
        lines = []
        lines.append("="*80)
        lines.append("RELATÓRIO DE ERROS DA ONTOLOGIA")
        lines.append("="*80)

        # Erros léxicos
        if self.lexical_errors:
            lines.append(f"\nERROS LÉXICOS ({len(self.lexical_errors)}):")
            lines.append("-" * 80)
            for error in self.lexical_errors:
                lines.append("\n" + str(error))
        else:
            lines.append("\nERROS LÉXICOS: Nenhum erro léxico encontrado.")

        # Erros sintáticos
        if self.syntactic_errors:
            lines.append(f"\n\nERROS SINTÁTICOS ({len(self.syntactic_errors)}):")
            lines.append("-" * 80)
            for error in self.syntactic_errors:
                lines.append("\n" + str(error))
        else:
            lines.append("\n\nERROS SINTÁTICOS: Nenhum erro sintático encontrado.")

        lines.append("\n" + "="*80)

        if not self.has_errors():
            lines.append("\n✓ Análise léxica e sintática concluída sem erros!")
            lines.append("="*80)

        return "\n".join(lines)

# Instâncias globais
summary = OntologySummary()
error_report = ErrorReport()

# Regra principal que define a estrutura de uma ontologia
def p_ontology(p):
    """ontology : package imports declarations"""
    package_name = None
    imports = []
    declarations = []

    if len(p) == 4:
        package_name = p[1]
        imports = p[2]
        declarations = p[3]
    elif len(p) == 3:
        imports = p[1]
        declarations = p[2]

    # Preencher sumário
    summary.package_name = package_name
    summary.imports = imports

    # Processar declarações para coleta de estatísticas
    current_class = None
    for decl in declarations:
        if decl['type'] in ['kind', 'category', 'subkind', 'role', 'phase', 'mixin',
                            'roleMixin', 'phaseMixin', 'mode', 'quality', 'collective',
                            'quantity', 'event', 'situation', 'process', 'historicalRole',
                            'historicalRoleMixin', 'intrinsicMode', 'extrinsicMode', 'relator']:
            # É uma classe
            current_class = decl['name']
            summary.add_class(decl['name'], decl['type'], decl.get('specializes'), decl.get('category'))

            if decl.get('content'):
                for attr in decl['content'].get('attributes', []):
                    summary.add_attribute_to_class(current_class, attr['name'], attr['datatype'])
                for rel in decl['content'].get('relations', []):
                    summary.add_relation_to_class(current_class, rel)

        elif decl['type'] == 'datatype':
            summary.datatypes.append(decl['name'])

        elif decl['type'] == 'enum':
            summary.enums[decl['name']] = decl['values']

        elif decl['type'] == 'genset':
            summary.gensets.append(decl)

        elif decl['type'] == 'relation_external':
            summary.external_relations.append(decl)

    p[0] = {
        'package': package_name,
        'imports': imports,
        'declarations': declarations,
        'summary': summary.get_summary_table(),
        'error_report': error_report.get_error_report(),
        'has_errors': error_report.has_errors(),
    }


# Lista de declarações (classes, enums, gensets, etc.)
# Retorna lista com declarações ou lista vazia
def p_declarations(p):
    """
    declarations : declarations declaration
                 | empty
    """
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# Define os tipos de declaração válidos na linguagem
def p_declaration(p):
    """declaration : datatype_declaration
                   | class_declaration
                   | enum_declaration
                   | genset_declaration
                   | relation_external
    """
    p[0] = p[1]


# Declaração de tipo de dados personalizado
def p_datatype_declarion(p):
    """datatype_declaration : DATATYPE_KW USER_TYPE OPEN_BRACE attr_list CLOSE_BRACE"""
    p[0] = {
        "type": "datatype",
        "name": p[2],
        "attributes": p[4],
    }


# Tipos de dados (nativos ou definidos pelo usuário)
def p_datatype(p):
    """datatype : NATIVE_TYPE
                | USER_TYPE
    """
    p[0] = p[1]


# Lista de imports de outros pacotes
# Retorna uma lista com nome dos imports
# Caso nenhum import seja encontrado, retorna lista vazia
def p_imports(p):
    """
    imports : imports import
            | empty
    """
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# Declaração de import de um pacote
def p_import(p):
    """import : IMPORT_KW IDENTIFIER"""
    p[0] = p[2]


# Declaração do nome do pacote
def p_package(p):
    """package : PACKAGE_KW IDENTIFIER"""
    p[0] = p[2]


# ============== Class ==============


def p_class_declaration(p):
    '''class_declaration : CLASS_STEREOTYPE IDENTIFIER class_body
                         | CLASS_STEREOTYPE IDENTIFIER
                         | CLASS_STEREOTYPE IDENTIFIER OF_KW ONTOLOGICAL_CATEGORY class_body
                         | CLASS_STEREOTYPE IDENTIFIER OF_KW ONTOLOGICAL_CATEGORY
    '''

    if len(p) == 4:
        p[0] = {
            "type": "class",
            "stereotype": p[1],
            "name": p[2],
            "content": p[3],
        }
    elif len(p) == 3:
        p[0] = {
            "type": "class",
            "stereotype": p[1],
            "name": p[2],
            "content": None,
        }
    elif len(p) == 6:
        p[0] = {
            "type": "class",
            "stereotype": p[1],
            'name': p[2],
            'category': p[4],
            'content': p[5],
        }
    else:  # len(p) == 5
        p[0] = {
            "type": "class",
            "stereotype": p[1],
            'name': p[2],
            'category': p[4],
            'content': None,
        }


def p_class_body(p):
    '''class_body : OPEN_BRACE class_attribute_and_relation_list CLOSE_BRACE'''

    attributes = []
    relations = []

    for item in p[2]:
        if item is None:
            continue
        if item["type"] == "attribute":
            attributes.append(item)
        elif item["type"] == "relation_internal":
            relations.append(item)

    p[0] = {
        "attributes": attributes,
        "relations": relations,
    }


def p_class_attribute_and_relation_list(p):
    """class_attribute_and_relation_list : class_attribute_and_relation class_attribute_and_relation_list
                                         | class_attribute_and_relation
    """
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]


def p_class_attribute_and_relation(p):
    """class_attribute_and_relation : attribute
                                    | relation_internal
    """
    p[0] = p[1]


# Declaração de classe com herança/especialização
def p_class_specialization(p):
    """class_declaration : CLASS_STEREOTYPE IDENTIFIER SPECIALIZES_KW identifier_list class_body
                         | CLASS_STEREOTYPE IDENTIFIER SPECIALIZES_KW identifier_list
                         | CLASS_STEREOTYPE IDENTIFIER OF_KW ONTOLOGICAL_CATEGORY SPECIALIZES_KW identifier_list class_body
                         | CLASS_STEREOTYPE IDENTIFIER OF_KW ONTOLOGICAL_CATEGORY SPECIALIZES_KW identifier_list
    """

    if len(p) == 6:
        p[0] = {
            "type": "class",
            "stereotype": p[1],
            "name": p[2],
            "specializes": p[4],
            "content": p[5],
        }
    elif len(p) == 5:
        p[0] = {
            "type": "class",
            "stereotype": p[1],
            "name": p[2],
            "specializes": p[4],
            "content": None,
        }
    elif len(p) == 8:
        p[0] = {
            "type": "class",
            "stereotype": p[1],
            'name': p[2],
            'category': p[4],
            'specializes': p[6],
            'content': p[7],
        }
    else:  # len(p) == 7
        p[0] = {
            "type": "class",
            "stereotype": p[1],
            'name': p[2],
            'category': p[4],
            'specializes': p[6],
            'content': None,
        }

# Retorna uma lista não vazia de identificadores
def p_identifier_list(p):
    """identifier_list : identifier_list COMMA IDENTIFIER
                       | IDENTIFIER
    """

    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


# Lista de atributos de uma classe
def p_attr_list(p):
    """
    attr_list : attr_list attribute
              | empty
    """
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# Declaração de atributo em uma classe com tipo e metadados opcionais
def p_attribute(p):
    """
    attribute : IDENTIFIER COLON datatype
              | IDENTIFIER COLON datatype cardinality
              | IDENTIFIER COLON datatype cardinality meta_attributes
              | IDENTIFIER COLON datatype meta_attributes
              | IDENTIFIER COLON IDENTIFIER
              | IDENTIFIER COLON IDENTIFIER cardinality
              | IDENTIFIER COLON IDENTIFIER cardinality meta_attributes
              | IDENTIFIER COLON IDENTIFIER meta_attributes
    """
    p[0] = {
        'type': 'attribute',
        'name': p[1],
        'datatype': p[3],
    }


# Metaatributos como ordered, const, derived, etc.
def p_meta_attributes(p):
    """meta_attributes : OPEN_BRACE META_ATTRIBUTES CLOSE_BRACE"""
    p[0] = p[2]


# Lista de relações internas de uma classe
def p_relation_list(p):
    """
    relation_list : relation_list relation_internal
                  | empty
    """
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# Define cardinalidade de atributos e relações
def p_cardinality(p):
    """cardinality : OPEN_BRACKET MULTIPLICATION CLOSE_BRACKET
                   | OPEN_BRACKET NUMBER CLOSE_BRACKET
                   | OPEN_BRACKET NUMBER RANGE NUMBER CLOSE_BRACKET
                   | OPEN_BRACKET NUMBER RANGE MULTIPLICATION CLOSE_BRACKET
    """
    p[0] = "".join(p[1:])


# =============== Enum ===============


# Declaração de enumeração
def p_enum_declaration(p):
    """enum_declaration : ENUM_KW IDENTIFIER OPEN_BRACE enum_values CLOSE_BRACE"""
    # TODO: o identificador de instancia deve terminar com um número

    p[0] = {
        "type": "enum",
        "name": p[2],
        "values": p[4],
    }


# Valor individual de uma enumeração
def p_enum_value(p):
    """enum_value : IDENTIFIER"""
    p[0] = p[1]


# Lista de valores de enumeração separados por vírgula
def p_enum_values(p):
    """
    enum_values : enum_values COMMA enum_value
                | enum_value
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


# ============== Genset ==============


# Declaração de genset (conjunto de generalização)
def p_genset_declaration(p):
    """genset_declaration : optional_genset_restrictions GENSET_KW IDENTIFIER OPEN_BRACE GENERAL_KW IDENTIFIER SPECIFICS_KW comma_separated_identifiers CLOSE_BRACE"""
    p[0] = {
        "type": "genset",
        "genset_restrictions": p[1],
        "name": p[3],
        "specifics": p[8],
        "general": p[6],
    }


# Declaração de genset na forma inline com restrições
def p_genset_declaration_inline(p):
    """genset_declaration : optional_genset_restrictions GENSET_KW IDENTIFIER WHERE_KW comma_separated_identifiers SPECIALIZES_KW IDENTIFIER"""
    p[0] = {
        "type": "genset",
        "genset_restrictions": p[1],
        "name": p[3],
        "specifics": p[5],
        "general": p[7],
    }


# Lista opcional de restrições de genset (disjoint, complete, etc.)
def p_optional_genset_restrictions(p):
    """
    optional_genset_restrictions : optional_genset_restrictions genset_restriction
                                 | empty
    """
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# Restrições aplicáveis a gensets
def p_genset_restriction(p):
    """
    genset_restriction : DISJOINT_KW
                       | COMPLETE_KW
                       | INCOMPLETE_KW
                       | OVERLAPPING_KW
    """
    p[0] = p[1]


# Descrição: Essa regra define uma produção em que deve haver ao menos um
# identificador. Se houver mais que um, devem estar separados por vírgula
def p_comma_separated_identifiers(p):
    """
    comma_separated_identifiers : comma_separated_identifiers COMMA IDENTIFIER
                                | IDENTIFIER
    """

    if len(p) == 4:
        # Regra -> comma_separated_identifiers : comma_separated_identifiers COMMA IDENTIFIER
        p[0] = p[1] + [p[3]]
    else:
        # Regra -> comma_separated_identifiers : IDENTIFIER
        p[0] = [p[1]]


# ============== Relations ==============


# Declaração de relação interna (dentro de uma classe)
def p_relation_internal(p):
    """
    relation_internal : AT RELATION_STEREOTYPE cardinality relation_connector cardinality IDENTIFIER
    """
    p[0] = {
        "type": "relation_internal",
        "relation_stereotype": p[2],
        "connector": p[4],
        "domain": None,
        "domain_cardinality": p[3],
        "image": p[6],
        "image_cardinality": p[5],
    }


# Declaração de relações externa (fora do corpo das classes)
def p_relation_external(p):
    """
    relation_external : AT RELATION_STEREOTYPE RELATION_KW IDENTIFIER cardinality relation_connector cardinality IDENTIFIER
    """
    p[0] = {
        "type": "relation_external",
        "relation_stereotype": p[2],
        "connector": p[6],
        "domain": p[4],
        "domain_cardinality": p[5],
        "image": p[8],
        "image_cardinality": p[7],
    }


# Conector de relação sem rótulo
def p_relation_connector_unlabeled(p):
    """
    relation_connector : relation_connector_start
                       | relation_connector_end
                       | DOUBLE_DASH
    """
    p[0] = {"type": "relation_connector", "label": None, "connector": p[1]}


# Conector de relação com rótulo à esquerda (agregação/composição).
# "<>-- rel_name --"   (agregação)
# "<o>-- rel_name --"  (composição)
def p_relation_connector_labeled_left(p):
    """
    relation_connector : relation_connector_start IDENTIFIER DOUBLE_DASH
    """

    p[0] = {"type": "relation_connector", "label": p[2], "connector": p[1]}


# Conector de relação à direita com rótulo.
# "-- name --<>"   (agregação)
# "-- name --<o>"  (composição)
# "-- name --"     (associação)
def p_relation_connector_labeled_right(p):
    """
    relation_connector : DOUBLE_DASH IDENTIFIER relation_connector_end
                       | DOUBLE_DASH IDENTIFIER DOUBLE_DASH
    """
    p[0] = {"type": "relation_connector", "label": p[2], "connector": p[3]}


# Conectores de início de relação (agregação/composição)
def p_relation_connector_symbol(p):
    """
    relation_connector_start : AGGREGATION
                             | COMPOSITION
    """
    p[0] = p[1]


# Conectores de fim de relação (agregação/composição inversa)
def p_relation_connector_symbol_inverse(p):
    """
    relation_connector_end : AGGREGATION_INVERSE
                           | COMPOSITION_INVERSE
    """
    p[0] = p[1]


# ============= Parser Utils ==============


def p_catch_error(p):
    """
    catch : error
    """
    print(p[1])


# Regra para produções vazias
def p_empty(p):
    """empty :"""
    pass


# Trata erros sintáticos durante o parsing
def p_error(p):
    if p:
        # Gerar sugestão inteligente baseada no token
        suggestion = generate_smart_suggestion(str(p.value), p.type)

        error_report.add_syntactic_error(
            line=p.lineno,
            column=0,
            message=f"Token inesperado '{p.value}' do tipo {p.type}",
            suggestion=suggestion
        )
        parser.errok()
    else:
        error_report.add_syntactic_error(
            line=0,
            column=0,
            message="Fim de arquivo inesperado",
            suggestion="Verifique se todos os blocos foram fechados corretamente com '}' e se a sintaxe está completa."
        )


lexer = TontoLexer()
parser = yacc.yacc()

def parse_ontology(data: str) -> Dict[str, Any]:
    """
    Realiza o parsing de uma ontologia Tonto e retorna a árvore sintática,
    tabela de síntese e relatório de erros.

    Args:
        data: Código fonte da ontologia em formato string

    Returns:
        Dicionário contendo:
        - ast: Árvore sintática abstrata
        - summary: Tabela de síntese formatada
        - error_report: Relatório de erros formatado
        - has_errors: Boolean indicando se há erros
    """
    # Resetar estado global
    global summary, error_report
    summary = OntologySummary()
    error_report = ErrorReport()

    # Processar erros léxicos
    lexer_instance = TontoLexer()
    list(lexer_instance.tokenize(data))  # Força tokenização para coletar erros

    for lex_error in lexer_instance.errors:
        # Gerar sugestão inteligente para erros léxicos
        suggestion = f"Caractere ilegal '{lex_error.character}'."

        # Tentar identificar se é uma palavra-chave escrita errada
        if hasattr(lex_error, 'value') and len(lex_error.character) > 1:
            similar = find_similar_token(lex_error.character)
            if similar:
                suggestion += f" {similar}"
            else:
                suggestion += " Verifique se este caractere é válido na linguagem Tonto."
        else:
            suggestion += " Verifique se este caractere é válido na linguagem Tonto."

        error_report.add_lexical_error(
            line=lex_error.line,
            column=lex_error.column,
            message=lex_error.message,
            suggestion=suggestion
        )

    # Parsing
    lexer_instance.lexer.lineno = 1
    lexer_instance.lexer.input(data)
    result = parser.parse(lexer=lexer_instance.lexer)

    if result is None:
        result = {
            'package': None,
            'imports': [],
            'declarations': [],
            'summary': summary.get_summary_table(),
            'error_report': error_report.get_error_report(),
            'has_errors': True,
        }

    return result

def print_parse_results(result: Dict[str, Any]):
    """
    Imprime os resultados do parsing de forma formatada.

    Args:
        result: Resultado retornado por parse_ontology()
    """
    print("\n")
    print(result['summary'])
    print("\n")
    print(result['error_report'])
    print("\n")
