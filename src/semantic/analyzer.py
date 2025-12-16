from typing import List, Optional, Tuple

from semantic.dataclasses import Genset, SemanticError, TontoClass, TontoRelation
from semantic.pattern_validator import PatternValidator
from semantic.symbol_table import SymbolTable


class SemanticAnalyzer:
    """Analisador semântico principal"""

    # Estereótipos que são ultimate sortals
    ULTIMATE_SORTALS = {
        'kind', 'collective', 'quantity', 'relator',
        'quality', 'mode', 'intrinsicMode', 'extrinsicMode',
        'type', 'powertype'
    }

    # Estereótipos que DEVEM especializar um ultimate sortal
    NON_ULTIMATE_SORTALS = {
        'subkind', 'phase', 'role', 'historicalRole'
    }

    # Classificação por rigidez
    RIGID_STEREOTYPES = {
        'kind', 'collective', 'quantity', 'subkind', 'category'
    }

    ANTI_RIGID_STEREOTYPES = {
        'role', 'phase', 'historicalRole', 'roleMixin'
    }

    SEMI_RIGID_STEREOTYPES = {
        'mixin', 'phaseMixin'
    }

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.package_name: Optional[str] = None
        self.imports: List[str] = []

    def analyze(self, ast: dict) -> Tuple[SymbolTable, List[SemanticError]]:
        """
        Analisa a AST e retorna a tabela de símbolos e lista de erros
        """
        self.errors = []

        # Fase 1: Construir tabela de símbolos
        self._build_symbol_table(ast)

        # Fase 2: Validar referências
        self._validate_references()

        # Fase 3: Validar padrões ontológicos
        validator = PatternValidator(self.symbol_table)
        validator.validate_all_patterns()
        self.errors.extend(validator.errors)

        return self.symbol_table, self.errors

    def _build_symbol_table(self, ast: dict):
        """Primeira passada: constrói a tabela de símbolos"""

        self.package_name = ast.get('package')
        self.imports = ast.get('imports', [])

        for declaration in ast.get('declarations', []):
            decl_type = declaration.get('type')

            if decl_type == 'class':
                self._process_class_declaration(declaration)
            elif decl_type == 'datatype':
                self._process_datatype_declaration(declaration)
            elif decl_type == 'enum':
                self._process_enum_declaration(declaration)
            elif decl_type == 'genset':
                self._process_genset_declaration(declaration)
            elif decl_type == 'relation_external':
                self._process_relation_external(declaration)

    def _process_class_declaration(self, declaration: dict):
        """Processa declaração de classe"""
        stereotype = declaration.get('stereotype', '')
        name = declaration.get('name', '')
        specializes = declaration.get('specializes')
        category = declaration.get('category')
        content = declaration.get('content')

        # Validação básica
        if not name or not stereotype:
            return

        # Verifica se já existe
        if name and self.symbol_table.get_class(name):
            self.errors.append(SemanticError(
                f"Class '{name}' is already defined."
            ))
            return

        # Valida estereótipo
        if stereotype == 'kind' and specializes:
            self.errors.append(SemanticError(
                f"Kind '{name}' cannot specialize another class. "
                f"Kinds are the top-level sortals."
            ))

        # Valida que non-ultimate sortals DEVEM especializar um ultimate sortal
        if stereotype in self.NON_ULTIMATE_SORTALS:
            if not specializes or len(specializes) == 0:
                ultimate_list = ', '.join(sorted(self.ULTIMATE_SORTALS))
                self.errors.append(SemanticError(
                    f"This class does not specialize a Ultimate Sortal. "
                    f"Every sortal class must specialize a unique Ultimate Sortal "
                    f"({ultimate_list})"
                ))

        # Cria classe
        attributes = []
        relations = []

        if content:
            attributes = content.get('attributes', [])
            relations = content.get('relations', [])

        tonto_class = TontoClass(
            name=str(name),
            stereotype=str(stereotype),
            specializes=specializes,
            category=category,
            attributes=attributes,
            relations=relations
        )

        self.symbol_table.add_class(tonto_class)

    def _process_datatype_declaration(self, declaration: dict):
        """Processa declaração de datatype"""
        name = declaration.get('name', '')
        if name:
            self.symbol_table.datatypes.append(str(name))

    def _process_enum_declaration(self, declaration: dict):
        """Processa declaração de enum"""
        name = declaration.get('name', '')
        values = declaration.get('values', [])
        if name:
            self.symbol_table.enums[str(name)] = values

    def _process_genset_declaration(self, declaration: dict):
        """Processa declaração de genset"""
        name = declaration.get('name', '')
        general = declaration.get('general', '')
        specifics = declaration.get('specifics', [])
        restrictions = declaration.get('genset_restrictions', [])

        # Validação básica
        if not name or not general:
            return

        genset = Genset(
            name=str(name),
            general=str(general),
            specifics=specifics,
            restrictions=restrictions
        )

        self.symbol_table.add_genset(genset)

    def _process_relation_external(self, declaration: dict):
        """Processa declaração de relação externa"""
        stereotype = declaration.get('relation_stereotype', '')
        domain = declaration.get('domain', '')
        domain_card = declaration.get('domain_cardinality', '')
        image = declaration.get('image', '')
        image_card = declaration.get('image_cardinality', '')
        connector = declaration.get('connector', {})

        # Validação básica
        if not stereotype or not domain or not image:
            return

        relation = TontoRelation(
            stereotype=str(stereotype),
            domain=str(domain),
            domain_cardinality=str(domain_card),
            image=str(image),
            image_cardinality=str(image_card),
            connector=dict(connector) if connector else {}
        )

        self.symbol_table.add_relation(relation)

    def _validate_references(self):
        """Segunda passada: valida referências entre símbolos"""

        # Valida especializações
        for class_name, tonto_class in self.symbol_table.classes.items():
            if tonto_class.specializes:
                for parent in tonto_class.specializes:
                    if parent and not self.symbol_table.get_class(parent):
                        self.errors.append(SemanticError(
                            f"Class '{class_name}' specializes undefined class '{parent}'."
                        ))

        # Valida hierarquia de rigidez: rigid não pode especializar anti-rigid
        self._validate_rigidity_hierarchy()

        # Valida gensets
        for genset in self.symbol_table.gensets:
            # Verifica se o general existe
            if not self.symbol_table.get_class(genset.general):
                self.errors.append(SemanticError(
                    f"Genset '{genset.name}' references undefined general class '{genset.general}'."
                ))

            # Verifica se os specifics existem
            for specific in genset.specifics:
                if not self.symbol_table.get_class(specific):
                    self.errors.append(SemanticError(
                        f"Genset '{genset.name}' references undefined specific class '{specific}'."
                    ))

        # Valida relações externas
        for relation in self.symbol_table.relations:
            if relation.domain and not self.symbol_table.get_class(relation.domain):
                self.errors.append(SemanticError(
                    f"Relation references undefined domain class '{relation.domain}'."
                ))

            if relation.image and not self.symbol_table.get_class(relation.image):
                self.errors.append(SemanticError(
                    f"Relation references undefined image class '{relation.image}'."
                ))

        # Valida relações internas
        for class_name, tonto_class in self.symbol_table.classes.items():
            for relation in tonto_class.relations:
                image = relation.get('image')
                if image and not self.symbol_table.get_class(image):
                    self.errors.append(SemanticError(
                        f"Class '{class_name}' has relation to undefined class '{image}'."
                    ))

    def _validate_rigidity_hierarchy(self):
        """
        Valida que rigid universals não podem especializar anti-rigid universals.

        Exemplos de erros:
        - subkind especializando role
        - kind especializando phase
        - category especializando roleMixin
        """
        for class_name, tonto_class in self.symbol_table.classes.items():
            stereotype = tonto_class.stereotype

            # Verifica se é um estereótipo rigid
            if stereotype not in self.RIGID_STEREOTYPES:
                continue

            # Verifica todos os parents (diretos e indiretos)
            visited = set()
            to_visit = list(tonto_class.specializes) if tonto_class.specializes else []

            while to_visit:
                parent_name = to_visit.pop(0)

                if parent_name in visited:
                    continue
                visited.add(parent_name)

                parent_class = self.symbol_table.get_class(parent_name)
                if not parent_class:
                    continue

                parent_stereotype = parent_class.stereotype

                # ERRO: rigid especializando anti-rigid
                if parent_stereotype in self.ANTI_RIGID_STEREOTYPES:
                    self.errors.append(SemanticError(
                        f"Rigid universal '{class_name}' ({stereotype}) cannot specialize "
                        f"anti-rigid universal '{parent_name}' ({parent_stereotype}). "
                    ))
                    break

                if parent_class.specializes:
                    to_visit.extend(parent_class.specializes)


def analyze(ast: dict) -> Tuple[SymbolTable, List[SemanticError]]:
    """
    Interface principal do analisador semântico

    Args:
        ast: Árvore sintática abstrata do parser

    Returns:
        Tupla contendo (tabela_de_símbolos, lista_de_erros)
    """
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)


def print_analysis_results(symbol_table: SymbolTable, errors: List[SemanticError]):
    """Imprime os resultados da análise semântica"""

    print("\n" + "=" * 60)
    print("SEMANTIC ANALYSIS RESULTS")
    print("=" * 60)

    # Tabela de Símbolos
    print("\n--- Symbol Table ---")

    print(f"\nClasses ({len(symbol_table.classes)}):")
    for name, tonto_class in symbol_table.classes.items():
        specializes_str = f" specializes {', '.join(tonto_class.specializes)}" if tonto_class.specializes else ""
        print(f"  - {tonto_class.stereotype} {name}{specializes_str}")

    print(f"\nGensets ({len(symbol_table.gensets)}):")
    for genset in symbol_table.gensets:
        restrictions = ' '.join(genset.restrictions) if genset.restrictions else 'none'
        print(f"  - {genset.name}: {genset.general} -> [{', '.join(genset.specifics)}] ({restrictions})")

    print(f"\nExternal Relations ({len(symbol_table.relations)}):")
    for relation in symbol_table.relations:
        print(f"  - @{relation.stereotype}: {relation.domain} {relation.domain_cardinality} -- "
              f"{relation.image_cardinality} {relation.image}")

    print(f"\nDatatypes ({len(symbol_table.datatypes)}):")
    for dt in symbol_table.datatypes:
        print(f"  - {dt}")

    print(f"\nEnums ({len(symbol_table.enums)}):")
    for name, values in symbol_table.enums.items():
        print(f"  - {name}: [{', '.join(values)}]")

    # Erros
    print("\n--- Semantic Errors ---")
    if errors:
        print(f"\nFound {len(errors)} error(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
    else:
        print("\n✓ No semantic errors found!")

    print("\n" + "=" * 60)
