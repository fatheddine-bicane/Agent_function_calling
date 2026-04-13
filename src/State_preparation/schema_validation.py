from jsonschema import validate
from Exceptions.state_preparation_exceptions import MultipleFunctionDefinitionException


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


def validateFunctionsDefinitions(function: dict) -> None:
    if isinstance(function, list):
        raise MultipleFunctionDefinitionException()
    validate(instance=function, schema=schema)
