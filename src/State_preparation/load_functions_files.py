from pathlib import Path
import itertools
import json
from .schema_validation import validateFunctionsDefinitions
from Exceptions.StatePreparationExceptions import MultipleFunctionDefinitionException
from jsonschema import ValidationError


def load_functions() -> list[dict]:
    folder_path = Path("src/Functions_deffinition")

    lowercase_json = folder_path.glob("*.json")
    uppercase_json = folder_path.glob("*.JSON")
    all_json_files = itertools.chain(lowercase_json, uppercase_json)

    functions_definitions = []
    for json_file in all_json_files:
        with json_file.open() as function_definition_file:
            try:
                function_definition = json.load(function_definition_file)
                validateFunctionsDefinitions(function_definition)
                functions_definitions.append(function_definition)
            except json.JSONDecodeError as e:
                print(f"Error: file \"{json_file}\"\n    JSON syntax: {e.msg}.")
                print("    Warning: Function not loaded!")
            except ValidationError as e:
                print(f"Error: file \"{json_file}\"\n    Schema : {e.message}.")
                print("    Warning: Function not loaded!")
            except MultipleFunctionDefinitionException as e:
                print(f"Error: file \"{json_file}\"\n    Multiple function definitions : {e.message}.")
                print("    Warning: Functions not loaded!")

    return functions_definitions
