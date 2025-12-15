from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SemanticError:
    """Representa um erro semântico encontrado durante a análise"""
    message: str
    line: Optional[int] = None
    context: Optional[str] = None

    def __str__(self):
        if self.line:
            return f"Semantic Error (Line {self.line}): {self.message}"
        return f"Semantic Error: {self.message}"


@dataclass
class TontoClass:
    """Representa uma classe na ontologia"""
    name: str
    stereotype: str
    specializes: Optional[list[str]] = None
    category: Optional[str] = None
    attributes: list[dict] = field(default_factory=list)
    relations: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if self.specializes is None:
            self.specializes = []
        elif isinstance(self.specializes, str):
            self.specializes = [self.specializes]


@dataclass
class Genset:
    """Representa um genset (conjunto de generalização)"""
    name: str
    general: str
    specifics: list[str]
    restrictions: list[str] = field(default_factory=list)

    def is_disjoint(self) -> bool:
        return 'disjoint' in self.restrictions

    def is_complete(self) -> bool:
        return 'complete' in self.restrictions

    def is_incomplete(self) -> bool:
        return 'incomplete' in self.restrictions

    def is_overlapping(self) -> bool:
        return 'overlapping' in self.restrictions


@dataclass
class TontoRelation:
    """Representa uma relação externa"""
    stereotype: str
    domain: str
    domain_cardinality: str
    image: str
    image_cardinality: str
    connector: dict
    name: Optional[str] = None
