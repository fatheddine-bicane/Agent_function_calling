class ContextWindow:
    def __init__(self, *, messages_limit: int=50) -> None:
        self._messages_lists: list[dict[str, str]] = []
        self._index = 0
        self._messages_limit = messages_limit


    def appendMessage(self, role: str, content: str) -> None:
        if (len(self._messages_lists) < self._messages_limit):
            self._messages_lists.append({
                "role": role, "content": content
            })

        else:
            if self._index == self._messages_limit:
                self._index = 0

            self._messages_lists[self._index] = {"role": role, "content": content}
            self._index += 1
