from pathlib import Path
import itertools
import json
from .schema_validation import validateFunctionsDefinitions
from src.Exceptions.state_preparation_exceptions import MultipleFunctionDefinitionException
from jsonschema import ValidationError
from colorama import Fore


def loadFunctions() -> list[dict]:
    folder_path = Path("./config/tools/definitions")

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
                print(Fore.RED + f"Error: file \"{json_file}\"\n    JSON syntax: {e.msg}.")
                print(Fore.YELLOW  + "    Warning: Function not loaded!" + Fore.RESET)
            except ValidationError as e:
                print(Fore.RED + f"Error: file \"{json_file}\"\n    Schema : {e.message}.")
                print(Fore.YELLOW + "    Warning: Function not loaded!" + Fore.RESET)
            except MultipleFunctionDefinitionException as e:
                print(Fore.RED + f"Error: file \"{json_file}\"\n    Multiple function definitions : {e.message}.")
                print(Fore.YELLOW + "    Warning: Functions not loaded!" + Fore.RESET)

    return functions_definitions
