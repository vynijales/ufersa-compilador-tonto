
from dataclasses import dataclass

@dataclass
class OntologyError:
    line: int
    column: int
    message: str

@dataclass
class OntologyWarning:
    line: int
    column: int
    message: str
