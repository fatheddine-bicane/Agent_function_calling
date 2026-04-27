from typing import Callable
from .implementations.fn_extract_webpage_content import fn_extract_webpage_content
from .implementations.fn_get_current_time import fn_get_current_time
from .implementations.fn_get_internet_snippet import fn_get_internet_snippet
from .implementations.fn_substitute_string_with_regex import fn_substitute_string_with_regex
from .implementations.fn_write_to_file import fn_write_to_file


tools_map: dict[str, Callable] = {
    "fn_extract_webpage_content": fn_extract_webpage_content,
    "fn_get_current_time": fn_get_current_time,
    "fn_get_internet_snippet": fn_get_internet_snippet,
    "fn_substitute_string_with_regex": fn_substitute_string_with_regex,
    "fn_write_to_file": fn_write_to_file
}
