from llm_sdk import Small_LLM_Model
from src.State_preparation.ContextWindow import ContextWindow
from src.Exceptions.constrained_decoding_exceptions import ModelExceedTokensLimitException
from src.Constrained_decoding.FiniteStateMachine import FiniteStateMachine
from interegular.fsm import State
import re
import json
from src.Constrained_decoding.tools import tools
from typing import Any
from colorama import Style

MAX_NEW_TOKENS = 1000
SHOW_REASONING: bool = True

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

        # ban every none allowed token and chose the one with the highest score
        mask: list[float] = [float('-inf')] * len(logits_array)
        for token_id in allowed_tokens_ids:
            mask[token_id] = logits_array[token_id]
        expected_token: int = mask.index(max(mask))

        exp_str = llm._tokenizer.decode(expected_token)
        print(exp_str, end="", flush=True)

        # break out of the loop is the curent state is the final state
        if expected_token == stop_token:
            break

        # update the current state after chosing the token with highest score
        current_state = fsm.token_fsm_index[current_state].get(expected_token)

        #append token to answer and 
        tokens_ids.append(expected_token)
        generated_answer.append(expected_token)

    else:
        raise ModelExceedTokensLimitException(MAX_NEW_TOKENS)

    generated_answer_string: str = llm._tokenizer.decode(generated_answer, skip_special_tokens=False) #type: ignore
    context_window.appendMessage(role="assistant", content=generated_answer_string)
    tools_list: list[dict] = buildArrayOfDict(generated_answer_string) #type: ignore
    return tools_list



def printToken(llm: Small_LLM_Model, token_id: int, model_is_reasoning: bool) -> bool:
    """
    Print given token, and apply terminal style for reasoning
    """
    if not SHOW_REASONING:
        if token_id == START_OF_THINKING_TOKEN_ID:
            return False
        elif token_id == END_OF_THINKING_TOKEN_ID:
            return True
        elif not model_is_reasoning:
            print(llm._tokenizer.decode(token_id), end="", flush=True)

    elif SHOW_REASONING:
        if token_id == START_OF_THINKING_TOKEN_ID:
            print(Style.DIM, "Reasoning:", end="", flush=True)
        elif token_id == END_OF_THINKING_TOKEN_ID:
            print(Style.NORMAL, end="", flush=True)
            return True
        else:
            print(llm._tokenizer.decode(token_id), end="", flush=True)

    return model_is_reasoning


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

    global START_OF_THINKING_TOKEN_ID
    global END_OF_THINKING_TOKEN_ID 

    tool_call_token_id: int = llm._tokenizer.convert_tokens_to_ids("<tool_call>") #type: ignore
    START_OF_THINKING_TOKEN_ID = llm._tokenizer.convert_tokens_to_ids("<think>") #type: ignore
    END_OF_THINKING_TOKEN_ID = llm._tokenizer.convert_tokens_to_ids("</think>") #type: ignore
    stop_token: int = llm._tokenizer.eos_token_id #type: ignore

    generated_answer: list[int] = []
    model_is_reasoning: bool = False
    for _ in range(MAX_NEW_TOKENS):
        # calculate logits score
        logits: list[float] = llm.get_logits_from_input_ids(tokens_ids)
        # chose the token with the highest score
        expected_token: int = logits.index(max(logits))

        # if the llm decided the end of generation update the context window and break of the loop
        if expected_token == stop_token:
            generated_answer_string = llm.decode(generated_answer)
            context_window.appendMessage("assistant", generated_answer_string)
            printToken(llm, llm._tokenizer.convert_tokens_to_ids('/n'), model_is_reasoning) #type: ignore
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

            # reset the token limit count
            _ = 0
            continue

        tokens_ids.append(expected_token)
        generated_answer.append(expected_token)

        # print the token
        model_is_reasoning = printToken(llm, expected_token, model_is_reasoning)

    else:
        raise ModelExceedTokensLimitException(MAX_NEW_TOKENS)
