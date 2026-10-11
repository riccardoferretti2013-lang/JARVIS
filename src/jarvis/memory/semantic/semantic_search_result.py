from dataclasses import dataclass

from ..memory import Memory


@dataclass(frozen=True, slots=True)
class SemanticSearchResult:
    """
    Risultato di una ricerca semantica.
    """

    memory: Memory
    similarity: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.similarity <= 1.0:
            raise ValueError(
                "La similarità deve essere compresa tra 0 e 1."
            )