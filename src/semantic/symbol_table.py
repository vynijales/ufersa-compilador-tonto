from dataclasses import dataclass, field
from typing import Optional

from semantic.dataclasses import Genset, TontoClass, TontoRelation


@dataclass
class SymbolTable:
    """Tabela de símbolos para análise semântica"""
    classes: dict[str, TontoClass] = field(default_factory=dict)
    gensets: list[Genset] = field(default_factory=list)
    relations: list[TontoRelation] = field(default_factory=list)
    datatypes: list[str] = field(default_factory=list)
    enums: dict[str, list[str]] = field(default_factory=dict)

    def add_class(self, tonto_class: TontoClass):
        self.classes[tonto_class.name] = tonto_class

    def get_class(self, name: str) -> Optional[TontoClass]:
        return self.classes.get(name)

    def add_genset(self, genset: Genset):
        self.gensets.append(genset)

    def add_relation(self, relation: TontoRelation):
        self.relations.append(relation)

    def get_gensets_for_general(self, general_name: str) -> list[Genset]:
        """Retorna todos os gensets que têm a classe como general"""
        return [g for g in self.gensets if g.general == general_name]

    def get_specializations(self, class_name: str) -> list[TontoClass]:
        """Retorna todas as classes que especializam a classe dada"""
        return [c for c in self.classes.values() if c.specializes and class_name in c.specializes]
