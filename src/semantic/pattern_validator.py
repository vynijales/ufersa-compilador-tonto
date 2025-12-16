from semantic.dataclasses import SemanticError
from semantic.symbol_table import SymbolTable


class PatternValidator:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.errors: list[SemanticError] = []

    def validate_all_patterns(self):
        self.validate_subkind_pattern()
        self.validate_role_pattern()
        self.validate_phase_pattern()
        self.validate_relator_pattern()
        self.validate_mode_pattern()
        self.validate_rolemixin_pattern()
        self.validate_genset_homogeneity()

    # Pattern 1: Subkind Pattern
    def validate_subkind_pattern(self):
        """
        Valida o padrão Subkind:
        - kind ClassName
        - subkind SubclassName specializes ClassName
        - Deve ter genset com general=ClassName
        - Genset deve ter 'disjoint'
        """
        for class_name, tonto_class in self.symbol_table.classes.items():
            if tonto_class.stereotype == 'kind':
                # Verifica se há subkinds que especializam este kind
                subkinds = [
                    c for c in self.symbol_table.get_specializations(class_name)
                    if c.stereotype == 'subkind' and c.specializes and class_name in c.specializes
                ]

                # Genset só é necessário quando há 2 ou mais subkinds
                if len(subkinds) >= 2:
                    gensets = self.symbol_table.get_gensets_for_general(class_name)

                    if not gensets:
                        self.errors.append(SemanticError(
                            f"Subkind Pattern violation: Kind '{class_name}' has multiple subkinds "
                            f"({', '.join([s.name for s in subkinds])}) but no genset is defined. "
                            f"A genset with 'disjoint' restriction is required."
                        ))
                        continue

                    # Verifica se pelo menos um genset tem 'disjoint'
                    has_disjoint = any(g.is_disjoint() for g in gensets)
                    if not has_disjoint:
                        self.errors.append(SemanticError(
                            f"Subkind Pattern violation: Kind '{class_name}' with subkinds "
                            f"requires a genset with 'disjoint' restriction."
                        ))

                    # Verifica se todos os subkinds estão no genset
                    for genset in gensets:
                        subkind_names = {s.name for s in subkinds}
                        genset_specifics = set(genset.specifics)

                        if not subkind_names.issubset(genset_specifics):
                            missing = subkind_names - genset_specifics
                            self.errors.append(SemanticError(
                                f"Subkind Pattern warning: Genset '{genset.name}' for kind '{class_name}' "
                                f"does not include all subkinds. Missing: {', '.join(missing)}"
                            ))

    # Pattern 2: Role Pattern
    def validate_role_pattern(self):
        """
        Valida o padrão Role:
        - kind ClassName
        - role RoleName specializes ClassName
        - Deve ter genset com general=ClassName
        - Genset NÃO deve ter 'disjoint' (roles podem se sobrepor)
        """
        for class_name, tonto_class in self.symbol_table.classes.items():
            if tonto_class.stereotype == 'kind':
                # Verifica se há roles que especializam este kind
                roles = [
                    c for c in self.symbol_table.get_specializations(class_name)
                    if c.stereotype == 'role'
                ]

                # Genset só é necessário quando há 2 ou mais roles
                if len(roles) >= 2:
                    # Deve existir um genset
                    gensets = self.symbol_table.get_gensets_for_general(class_name)

                    if not gensets:
                        self.errors.append(SemanticError(
                            f"Role Pattern violation: Kind '{class_name}' has multiple roles "
                            f"({', '.join([r.name for r in roles])}) but no genset is defined."
                        ))
                        continue

                    # Verifica se algum genset tem 'disjoint' (não deveria ter)
                    for genset in gensets:
                        if genset.is_disjoint():
                            self.errors.append(SemanticError(
                                f"Role Pattern violation: Genset '{genset.name}' for kind '{class_name}' "
                                f"with roles should NOT have 'disjoint' restriction. "
                                f"Roles can overlap."
                            ))

                    # Verifica se todos os roles estão no genset
                    for genset in gensets:
                        role_names = {r.name for r in roles}
                        genset_specifics = set(genset.specifics)

                        if not role_names.issubset(genset_specifics):
                            missing = role_names - genset_specifics
                            self.errors.append(SemanticError(
                                f"Role Pattern warning: Genset '{genset.name}' for kind '{class_name}' "
                                f"does not include all roles. Missing: {', '.join(missing)}"
                            ))

    # Pattern 3: Phase Pattern
    def validate_phase_pattern(self):
        """
        Valida o padrão Phase:
        - kind ClassName
        - phase PhaseName specializes ClassName
        - Deve ter pelo menos 2 phases (não faz sentido ter apenas 1)
        - Deve ter genset com general=ClassName
        - Genset DEVE ter 'disjoint' (obrigatório)
        """
        for class_name, tonto_class in self.symbol_table.classes.items():
            if tonto_class.stereotype == 'kind':
                # Verifica se há phases que especializam este kind
                phases = [
                    c for c in self.symbol_table.get_specializations(class_name)
                    if c.stereotype == 'phase'
                ]

                # Se há apenas 1 phase, isso é um erro
                if len(phases) == 1:
                    self.errors.append(SemanticError(
                        f"Phase Pattern violation: Kind '{class_name}' has only one phase "
                        f"('{phases[0].name}')."
                    ))

                # Genset só é necessário quando há 2 ou mais phases
                if len(phases) >= 2:
                    # Deve existir um genset
                    gensets = self.symbol_table.get_gensets_for_general(class_name)

                    if not gensets:
                        self.errors.append(SemanticError(
                            f"Phase Pattern violation: Kind '{class_name}' has multiple phases "
                            f"({', '.join([p.name for p in phases])}) but no genset is defined. "
                            f"A genset with 'disjoint' restriction is MANDATORY."
                        ))
                        continue

                    # Verifica se pelo menos um genset tem 'disjoint' (obrigatório)
                    has_disjoint = any(g.is_disjoint() for g in gensets)
                    if not has_disjoint:
                        self.errors.append(SemanticError(
                            f"Phase Pattern violation: Kind '{class_name}' with phases "
                            f"MUST have a genset with 'disjoint' restriction. This is MANDATORY."
                        ))

                    # Verifica se todos os phases estão no genset
                    for genset in gensets:
                        phase_names = {p.name for p in phases}
                        genset_specifics = set(genset.specifics)

                        if not phase_names.issubset(genset_specifics):
                            missing = phase_names - genset_specifics
                            self.errors.append(SemanticError(
                                f"Phase Pattern warning: Genset '{genset.name}' for kind '{class_name}' "
                                f"does not include all phases. Missing: {', '.join(missing)}"
                            ))

    # Pattern 4: Relator Pattern
    def validate_relator_pattern(self):
        """
        Valida o padrão Relator:
        - kind ClassName
        - role RoleName1, RoleName2 specializes ClassName
        - relator RelatorName {
              @mediation [1..*] -- [1..*] RoleName1
              @mediation [1..*] -- [1..*] RoleName2
          }
        - @material relation RoleName1 [1..*] -- [1..*] RoleName2
        """
        # Encontra todos os relators
        relators = [c for c in self.symbol_table.classes.values() if c.stereotype == 'relator']

        for relator in relators:
            # Verifica se o relator tem pelo menos 2 mediations
            mediations = [r for r in relator.relations if r.get('relation_stereotype') == 'mediation']

            if len(mediations) < 2:
                self.errors.append(SemanticError(
                    f"Relator Pattern violation: Relator '{relator.name}' must have at least "
                    f"2 @mediation relations."
                ))
                continue

            # Coleta os roles mediados
            mediated_roles = [m.get('image') for m in mediations if m.get('image')]

            # Verifica se as classes mediadas existem
            for role_name in mediated_roles:
                if not role_name:
                    continue
                role_class = self.symbol_table.get_class(str(role_name))
                if not role_class:
                    self.errors.append(SemanticError(
                        f"Relator Pattern violation: Relator '{relator.name}' mediates "
                        f"'{role_name}' which is not defined."
                    ))

            # Verifica se existe uma relação @material entre os roles
            material_relations = [
                r for r in self.symbol_table.relations
                if r.stereotype == 'material'
            ]

            # Verifica se há relação material entre pares de roles mediados
            if len(mediated_roles) >= 2:
                found_material = False
                for relation in material_relations:
                    if (relation.domain in mediated_roles and relation.image in mediated_roles):
                        found_material = True
                        break

                if not found_material and len(mediated_roles) >= 2:
                    role_list = ', '.join(str(r) for r in mediated_roles if r)
                    self.errors.append(SemanticError(
                        f"Relator Pattern violation: Missing @material relation between roles "
                        f"mediated by relator '{relator.name}'. "
                        f"Expected relation between: {role_list}"
                    ))

    # Pattern 5: Mode Pattern
    def validate_mode_pattern(self):
        """
        Valida o padrão Mode:
        - kind ClassName1, ClassName2
        - mode ModeName {
              @characterization [1..*] -- [1] ClassName1
              @externalDependence [1..*] -- [1] ClassName2
          }
        """
        modes = [c for c in self.symbol_table.classes.values()
                 if c.stereotype in ['mode', 'intrinsicMode', 'extrinsicMode']]

        for mode in modes:
            # Verifica se tem @characterization
            characterizations = [
                r for r in mode.relations
                if r.get('relation_stereotype') == 'characterization'
            ]

            if not characterizations:
                self.errors.append(SemanticError(
                    f"Mode Pattern violation: Mode '{mode.name}' must have at least one "
                    f"@characterization relation."
                ))

            # Se for extrinsicMode, deve ter @externalDependence
            if mode.stereotype in ['extrinsicMode', 'mode']:
                external_deps = [
                    r for r in mode.relations
                    if r.get('relation_stereotype') == 'externalDependence'
                ]

                if mode.stereotype == 'extrinsicMode' and not external_deps:
                    self.errors.append(SemanticError(
                        f"Mode Pattern violation: Extrinsic mode '{mode.name}' must have at least one "
                        f"@externalDependence relation."
                    ))

            # Verifica se as classes alvo existem
            for relation in mode.relations:
                target_class = relation.get('image')
                if target_class and not self.symbol_table.get_class(target_class):
                    self.errors.append(SemanticError(
                        f"Mode Pattern violation: Mode '{mode.name}' references undefined class "
                        f"'{target_class}' in relation."
                    ))

    # Pattern 6: RoleMixin Pattern
    def validate_rolemixin_pattern(self):
        """
        Valida o padrão RoleMixin:
        - kind ClassName1, ClassName2
        - roleMixin RoleMixinName
        - role RoleName1 specializes ClassName1, RoleMixinName
        - role RoleName2 specializes ClassName2, RoleMixinName
        - Deve ter genset com general=RoleMixinName e specifics=[RoleName1, RoleName2]
        - Genset deve ter 'disjoint' e 'complete'
        """
        rolemixins = [c for c in self.symbol_table.classes.values() if c.stereotype == 'roleMixin']

        for rolemixin in rolemixins:
            # Verifica se há roles que especializam este roleMixin
            roles = []
            for c in self.symbol_table.classes.values():
                if c.stereotype == 'role' and c.specializes and rolemixin.name in c.specializes:
                    roles.append(c)

            if len(roles) < 2:
                self.errors.append(SemanticError(
                    f"RoleMixin Pattern warning: RoleMixin '{rolemixin.name}' should be specialized "
                    f"by at least 2 roles (found {len(roles)})."
                ))

            if len(roles) > 0:
                # Deve existir um genset
                gensets = self.symbol_table.get_gensets_for_general(rolemixin.name)

                if not gensets:
                    self.errors.append(SemanticError(
                        f"RoleMixin Pattern violation: RoleMixin '{rolemixin.name}' has roles "
                        f"({', '.join([r.name for r in roles])}) but no genset is defined."
                    ))
                    continue

                # Verifica se o genset tem 'disjoint' e 'complete'
                for genset in gensets:
                    if not genset.is_disjoint():
                        self.errors.append(SemanticError(
                            f"RoleMixin Pattern violation: Genset '{genset.name}' for roleMixin "
                            f"'{rolemixin.name}' should have 'disjoint' restriction."
                        ))

                    if not genset.is_complete():
                        self.errors.append(SemanticError(
                            f"RoleMixin Pattern warning: Genset '{genset.name}' for roleMixin "
                            f"'{rolemixin.name}' should typically have 'complete' restriction."
                        ))

                # Verifica se os roles especializam diferentes kinds
                parent_kinds = set()
                for role in roles:
                    if not role.specializes:
                        continue
                    for parent in (role.specializes or []):
                        if parent != rolemixin.name:
                            parent_class = self.symbol_table.get_class(parent)
                            if parent_class and parent_class.stereotype == 'kind':
                                parent_kinds.add(parent)

                if len(parent_kinds) < 2:
                    self.errors.append(SemanticError(
                        f"RoleMixin Pattern warning: RoleMixin '{rolemixin.name}' roles should "
                        f"specialize different kinds (found {len(parent_kinds)} kind(s))."
                    ))

    # Pattern 7: Genset Homogeneity
    def validate_genset_homogeneity(self):
        """
        Valida que um genset não mistura esteriótipos incompatíveis.

        Regras:
        - Rigid sortals (subkind, category) não podem ser misturados com
          anti-rigid sortals (role, phase, historicalRole) no mesmo genset
        - Isso garante que o genset mantenha coerência ontológica
        """
        for genset in self.symbol_table.gensets:
            stereotypes = {}

            # Coleta os estereótipos de cada specific
            for specific_name in genset.specifics:
                specific_class = self.symbol_table.get_class(specific_name)
                if specific_class:
                    stereotypes[specific_name] = specific_class.stereotype

            if not stereotypes:
                continue

            # Define grupos de categorias ontológicas
            rigid_sortals = {'subkind', 'category'}
            anti_rigid_sortals = {'role', 'phase', 'historicalRole'}
            semi_rigid_sortals = {'roleMixin', 'phaseMixin'}

            # Verifica quais categorias estão presentes
            stereotype_set = set(stereotypes.values())
            has_rigid = bool(stereotype_set & rigid_sortals)
            has_anti_rigid = bool(stereotype_set & anti_rigid_sortals)

            # Erro: mistura de rigid com anti-rigid
            if has_rigid and has_anti_rigid:
                rigid_classes = [name for name, st in stereotypes.items() if st in rigid_sortals]
                anti_rigid_classes = [name for name, st in stereotypes.items() if st in anti_rigid_sortals]

                self.errors.append(SemanticError(
                    f"Genset '{genset.name}' mixes incompatible ontological categories. "
                    f"Rigid sortals ({', '.join(rigid_classes)}) cannot be mixed with "
                    f"anti-rigid sortals ({', '.join(anti_rigid_classes)}) in the same genset. "
                ))

            # Aviso: mistura de diferentes tipos de anti-rigid
            roles_and_phases = {'role', 'historicalRole', 'phase'}
            mixed_anti_rigid = stereotype_set & roles_and_phases
            if len(mixed_anti_rigid) > 1:
                has_role = bool(stereotype_set & {'role', 'historicalRole'})
                has_phase = 'phase' in stereotype_set

                if has_role and has_phase:
                    role_classes = [name for name, st in stereotypes.items()
                                   if st in {'role', 'historicalRole'}]
                    phase_classes = [name for name, st in stereotypes.items() if st == 'phase']

                    self.errors.append(SemanticError(
                        f"Genset '{genset.name}' mixes roles ({', '.join(role_classes)}) "
                        f"with phases ({', '.join(phase_classes)}). "
                    ))
