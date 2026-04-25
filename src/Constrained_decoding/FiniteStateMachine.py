import json
from llm_sdk import Small_LLM_Model
from interegular import Pattern, parse_pattern
from interegular.fsm import anything_else, FSM, State, TransitionKey, _AnythingElseCls
from typing import Any, Union


class FiniteStateMachine:
    def __init__(self, llm: Small_LLM_Model) -> None:
        with open("./src/Constrained_decoding/fsm_schema.json") as f:
            schema: dict = json.load(f)
            regex: str = self.__schemaToRegex(schema)
            parsed_regex: Pattern = parse_pattern(regex)
            self.fsm: FSM = parsed_regex.to_fsm()
            self.token_fsm_index: dict = self.__tokenFsmIndex(llm, self.fsm)

        return


    def __schemaToRegex(self, schema: dict) -> str:
        """
        Build a regular expression string out of a python dictionary.
        """
        if "anyOf" in schema:
            elements: dict = schema.get("anyOf", {})
            options: list[str] = [self.__schemaToRegex(element) for element in elements]

            joined_options: str = "|".join(options)
            return r'(<tool_call>\n?' + f'({joined_options})' + r'\n?</tool_call>\n?)+'

        elif "const" in schema:
            const_value: Any = schema.get("const", {})
            if isinstance(const_value, str):
                return f'"{const_value}"'
            else:
                return f'{const_value}'

        schema_type: str = schema.get("type") #type: ignore

        if schema_type == "string":
            return r'"[^"]*"'

        elif schema_type == "number":
            return r'-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?'

        elif schema_type == "object":
            properties: dict = schema.get("properties", {})

            properties_regexes: list[str] = []
            for key, value in properties.items():
                key_regex: str = f'"{key}"'
                value_regex: str = self.__schemaToRegex(value)
                properties_regexes.append(f'{key_regex}: ?{value_regex}')

            joined_properties_regexes: str = ", ?".join(properties_regexes)
            return r'\{' + joined_properties_regexes + r'\}'

        elif schema_type == "array":
            array_items: dict = schema.get("items", {})
            items_regex: str = self.__schemaToRegex(array_items)
            return r'\[(' + items_regex + r'(, ?' + items_regex + r')*)?\]'

        raise ValueError(f"Unsupported schema type: {schema}")


    def __tokenFsmIndex(self, llm: Small_LLM_Model, fsm: FSM) -> dict:
        """
        Build a token level fsm by going through every token in the models vocabulary,
        and try to move char by char checking if the token can walk an fsm state chain
        starting from its first character till the end of a token.
        """
        tokens_vocabulary: dict[str, int] = llm._tokenizer.get_vocab()
        fsm_map: dict[State, dict[TransitionKey, State]] = fsm.map
        symbol_mapping: dict[Union[str, _AnythingElseCls], TransitionKey] = fsm.alphabet._symbol_mapping

        token_fsm_index: dict[State, dict[int, State]] = {}
        for state in fsm.states:
            token_fsm_index[state] = {}

            for token_string, token_id in tokens_vocabulary.items():
                current_state: State = state
                is_valid_token: bool = True

                for char in token_string:
                    # characters at the fsm level translate to numberIds--TransitionKey-- for fast look up
                    fsm_symbol_id: TransitionKey | _AnythingElseCls = symbol_mapping.get(char, anything_else)
                    # possible next states and the numberIds that can move to based on the current_state
                    state_transitions: dict[TransitionKey, State] = fsm_map.get(current_state, {})

                    if fsm_symbol_id not in state_transitions:
                        is_valid_token = False
                        break

                    current_state = state_transitions[fsm_symbol_id] #type: ignore

                if is_valid_token:
                    token_fsm_index[state][token_id] = current_state

        return token_fsm_index
