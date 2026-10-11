from ..memory import Memory


class MemorySelector:
    """
    Seleziona i ricordi da inviare all'AI.
    """

    def select(
        self,
        memories: list[Memory],
    ) -> list[Memory]:

        memories.sort(
            key=lambda memory: (
                memory.importance,
                memory.updated_at,
            ),
            reverse=True,
        )

        return memories[:20]