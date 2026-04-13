from llm_sdk import Small_LLM_Model
from .load_functions_files import load_functions
from typing import cast, Any, Callable
from torch import Tensor

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


    def tokenizeContextWindow(self, llm: Small_LLM_Model) -> list[int]:
        functions: list[dict] = load_functions()

        initial_prompt = llm._tokenizer.apply_chat_template(
            conversation=self._messages_lists,
            tools=cast(list[dict[str, Any] | Callable[..., Any]], functions),
            add_generation_prompt=True,
            tokenize=False
        )

        return llm.encode(cast(str, initial_prompt))[0].tolist()
