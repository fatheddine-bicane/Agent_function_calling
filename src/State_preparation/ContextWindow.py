from llm_sdk import Small_LLM_Model
from .loadFunctions import loadFunctions
from typing import cast, Any, Callable

class ContextWindow:
    def __init__(self, *, messages_limit: int=50) -> None:
        self._messages_lists: list[dict[str, str]] = []
        self._index = 0
        self._messages_limit = messages_limit


    def appendMessage(self, role: str, content: str, name: str | None = None) -> None:
        # 1. Build the base dictionary
        message_dict = {"role": role, "content": content}

        # 2. Inject the name key strictly for tool executions
        if name is not None:
            message_dict["name"] = name

        # 3. Context Window Management (Sliding Window)
        if len(self._messages_lists) < self._messages_limit:
            self._messages_lists.append(message_dict)
        else:
            self._messages_lists.append(message_dict)

            cut_index: int = 2
            for i in range(1, len(self._messages_lists)):
                if self._messages_lists[i]["role"] == "user":
                    cut_index = i
                    break

            self._messages_lists = self._messages_lists[cut_index:]


    def tokenizeContextWindow(self, llm: Small_LLM_Model) -> list[int]:
        functions: list[dict] = loadFunctions()

        initial_prompt = llm._tokenizer.apply_chat_template(
            conversation=self._messages_lists,
            tools=cast(list[dict[str, Any] | Callable[..., Any]], functions),
            add_generation_prompt=True,
            tokenize=False
        )

        return llm.encode(cast(str, initial_prompt))[0].tolist()
