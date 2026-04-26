from llm_sdk import Small_LLM_Model
from State_preparation.ContextWindow import ContextWindow
from Exceptions.constrained_decoding_exceptions import ModelExceedTokensLimitException
from Constrained_decoding.FiniteStateMachine import FiniteStateMachine
from interegular.fsm import State
import re
import json
from Constrained_decoding.tools import tools
from typing import Any

MAX_NEW_TOKENS = 600

def buildArrayOfDict(tools: str) -> list[dict]:
    """
    Build a list of dictionary out a provided json objects wrapped in
    '<tool_call></tool_call>' XML tags by matching them with a regular
    expression.
    """
    pattern: str = r'<tool_call>(.*?)</tool_call>'
    raw_jsons_strings: list[Any] = re.findall(pattern, tools, flags=re.DOTALL)

    tools_dict_list: list[dict] = []
    for raw_json_string in raw_jsons_strings:
        try:
            json_dictionary: dict = json.loads(raw_json_string)
            tools_dict_list.append(json_dictionary)

        except json.JSONDecodeError:
            pass

    return tools_dict_list


def executeFunctions(tools_dict_list: list[dict]) -> list[Any]:
    """
    Loop through the given list of dictionarys executing the functions
    and return the results.
    """
    functions_results: list[Any] = []
    for tool in tools_dict_list:
        result: Any = tools[tool["name"]](**tool["arguments"])
        functions_results.append(result)

    return functions_results


def generateToolsCallAsJson(
    llm: Small_LLM_Model,
    fsm: FiniteStateMachine,
    tokens_ids: list[int],
    context_window: ContextWindow,
    generated_answer: list[int]
) -> list[dict]:
    """
    Generate a list of parsable dictionarys to execute the correct tools by 
    guiding the models output token by token to avoid any chance of hallucination
    using a pre compiled state machine for the available tools.
    """
    current_state: State = fsm.fsm.initial
    # generated_answer: list[int] = []
    stop_token: int = llm._tokenizer.eos_token_id #type: ignore

    for _ in range(MAX_NEW_TOKENS):
        # calculate logits score
        logits_array: list[float] = llm.get_logits_from_input_ids(tokens_ids)
        # retrieve the allowed tokens at the current state
        allowed_tokens_ids: list[int] = list(fsm.token_fsm_index[current_state].keys())

        # check if the current state can be an accept state, if so allow the end of generation token
        if current_state in fsm.fsm.finals:
            allowed_tokens_ids.append(llm._tokenizer.eos_token_id) #type: ignore

        # debug
        allowed_tokens_strings = [llm._tokenizer.decode(token) for token in allowed_tokens_ids]

        # ban every none allowed token and chose the one with the highest score
        mask: list[float] = [float('-inf')] * len(logits_array)
        for token_id in allowed_tokens_ids:
            mask[token_id] = logits_array[token_id]
        expected_token: int = mask.index(max(mask))

        # debug
        expected_token_string = llm._tokenizer.decode(expected_token, skip_special_tokens=False)

        # break out of the loop is the curent state is the final state
        if expected_token == stop_token:
            break

        # update the current state after chosing the token with highest score
        current_state = fsm.token_fsm_index[current_state].get(expected_token)

        #append token to answer and 
        tokens_ids.append(expected_token)
        generated_answer.append(expected_token)

        # debug
        print(expected_token_string, end="", flush=True)

    else:
        raise ModelExceedTokensLimitException(MAX_NEW_TOKENS)

    generated_answer_string: str = llm._tokenizer.decode(generated_answer, skip_special_tokens=False) #type: ignore
    context_window.appendMessage(role="assistant", content=generated_answer_string)
    tools_list: list[dict] = buildArrayOfDict(generated_answer_string) #type: ignore
    return tools_list



def generateAnswerAndUpdateContextWindow(
    llm: Small_LLM_Model,
    context_window: ContextWindow,
    fsm: FiniteStateMachine
) -> None:
    """
    Generate answer, detect if there is a functions call, if so execute it and answer
    based on the functions output, and update the context window.
    """
    # transform context window text to token ids--numbers--
    tokens_ids: list[int] = context_window.tokenizeContextWindow(llm)

    tool_call_token_id: int = llm._tokenizer.convert_tokens_to_ids("<tool_call>") #type: ignore
    end_of_thinking_token_id: int = llm._tokenizer.convert_tokens_to_ids("</think>") #type: ignore
    start_of_thinking_token_id: int = llm._tokenizer.convert_tokens_to_ids("<think>") #type: ignore
    stop_token: int = llm._tokenizer.eos_token_id #type: ignore

    start_printing: bool = False
    generated_answer: list[int] = []
    for _ in range(MAX_NEW_TOKENS):
        # calculate logits score
        logits: list[float] = llm.get_logits_from_input_ids(tokens_ids)
        # chose the token with the highest score
        expected_token: int = logits.index(max(logits))

        # debug
        expected_token_string = llm._tokenizer.decode(expected_token)

        # if the llm decided the end of generation update the context window and break of the loop
        if expected_token == stop_token:
            generated_answer_string = llm.decode(generated_answer)
            context_window.appendMessage("assistant", generated_answer_string)
            break

        elif expected_token == tool_call_token_id:
            #get the parsable tools list
            tools_list: list[dict] = generateToolsCallAsJson(llm, fsm, tokens_ids, context_window, generated_answer)

            # execute the tools and add the result to the history
            results: list[Any] = executeFunctions(tools_list)
            for result in results:
                context_window.appendMessage(role="tool", content=str(result))

            # tokenize the new context window
            tokens_ids = context_window.tokenizeContextWindow(llm)
            generated_answer = []
            continue

        tokens_ids.append(expected_token)
        generated_answer.append(expected_token)

        if start_printing:
            print(expected_token_string, end="", flush=True)

        # check if the model is in reasoning state then dont print generated tokens
        if expected_token == end_of_thinking_token_id:
            start_printing = True
        elif expected_token == start_of_thinking_token_id:
            start_printing = False


    else:
        raise ModelExceedTokensLimitException(MAX_NEW_TOKENS)
