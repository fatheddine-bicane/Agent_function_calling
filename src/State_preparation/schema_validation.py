from jsonschema import validate


schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "parameters": {"type": "object"},
        "return": {"type": "object"},
    },
    "required": ["name", "description", "parameters", "return"]
}


def validate_functions(functions: list[dict]) -> None:
    for function in functions:
        validate(instance=function, schema=schema)
