import json
from llm_sdk import Small_LLM_Model
from interegular import Pattern, parse_pattern
from interegular.fsm import anything_else, FSM, State


class FiniteStateMachine:
    def __init__(self, llm: Small_LLM_Model) -> None:
        with open("./src/Constrained_decoding/fsm_schema.json") as f:
            schema = json.load(f)
            regex: str = self.__schemaToRegex(schema)
            parsed_regex: Pattern = parse_pattern(regex)
            self.fsm: FSM = parsed_regex.to_fsm()

        return


    def __schemaToRegex(self, schema: dict) -> str:

        if "anyOf" in schema:
            elements = schema.get("anyOf", {})
            options = [self.__schemaToRegex(element) for element in elements]

            joined_options = "|".join(options)
            return r'(<tool_call>\n?' + f'({joined_options})' + r'\n?</tool_call>\n?)+'

        elif "const" in schema:
            const_value = schema.get("const", {})
            if isinstance(const_value, str):
                return f'"{const_value}"'
            else:
                return f'{const_value}'

        schema_type = schema.get("type")

        if schema_type == "string":
            return r'"[^"]*"'

        elif schema_type == "number":
            return r'-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?'

        elif schema_type == "object":
            properties = schema.get("properties", {})

            properties_regexes = []
            for key, value in properties.items():
                key_regex = f'"{key}"'
                value_regex = self.__schemaToRegex(value)
                properties_regexes.append(f'{key_regex}: ?{value_regex}')

            joined_properties_regexes = ", ?".join(properties_regexes)
            return r'\{' + joined_properties_regexes + r'\}'

        elif schema_type == "array":
            array_items = schema.get("items", {})
            items_regex = self.__schemaToRegex(array_items)
            return r'\[(' + items_regex + r'(, ?' + items_regex + r')*)?\]'

        raise ValueError(f"Unsupported schema type: {schema}")
