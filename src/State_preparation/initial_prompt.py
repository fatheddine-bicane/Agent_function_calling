from .load_functions_files import load_functions
from typing import cast, Any, Callable
from llm_sdk import Small_LLM_Model


def initial_message(llm: Small_LLM_Model) -> str:
    functions: list[dict] = load_functions()
    user_input: str = input("ask agent> ")

    messages_list = [
        {"role": "user", "content": f"{user_input}"}
    ]

    initial_prompt = llm._tokenizer.apply_chat_template(
        messages_list,
        tools=cast(list[dict[str, Any] | Callable[..., Any]], functions),
        add_generation_prompt=True,
        tokenize=False
    )

    return cast(str, initial_prompt)
