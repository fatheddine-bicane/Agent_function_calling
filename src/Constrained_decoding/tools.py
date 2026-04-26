from typing import Callable


def fn_add_numbers(a, b) -> int:
    return a + b

def fn_greet(name: str) -> str:
    return f"Greetings {name}, how are you today?"


tools: dict[str, Callable] = {
    "fn_add_numbers": fn_add_numbers,
    "fn_greet": fn_greet
}
