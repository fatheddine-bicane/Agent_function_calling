import re

def fn_substitute_string_with_regex(source_string: str, regex: str, replacement: str) -> str:
    """
    Replaces all occurrences matching a regex pattern in a string 
    with a specified replacement string.
    """
    try:
        # re.sub finds all non-overlapping matches of the pattern and replaces them
        result = re.sub(regex, replacement, source_string)
        return result
    except re.error as e:
        # Catches invalid regular expression syntax provided in the 'regex' parameter
        return f"Regex compilation error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# Example usage:
# modified_string = fn_substitute_string_with_regex("The price is 100 dollars", r"\d+", "XX")
# print(modified_string) # Output: The price is XX dollars
