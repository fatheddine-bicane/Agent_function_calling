class ContextWindow:
    def __init__(self, *, messages_limit: int=50) -> None:
        self._messages_lists: list[dict[str, str]] = []
        self._index = 0
        self._messages_limit = messages_limit
