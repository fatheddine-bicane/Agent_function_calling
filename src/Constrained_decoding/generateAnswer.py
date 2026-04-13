from llm_sdk import Small_LLM_Model
from State_preparation.ContextWindow import ContextWindow
from Exceptions.constrained_decoding_exceptions import ModelExceedTokensLimitException

MAX_NEW_TOKENS = 300

def greedySearch(tokens_ids: list[int], llm: Small_LLM_Model) -> int:
    logits = llm.get_logits_from_input_ids(tokens_ids)
    expected_token = logits.index(max(logits))
    tokens_ids.append(expected_token)

    return expected_token


def generateAnswer(
    llm: Small_LLM_Model,
    context_window: ContextWindow
) -> str:
    # tokenize context window
    tokens_ids = context_window.tokenizeContextWindow(llm)

    tool_call_token_id = llm._tokenizer.convert_tokens_to_ids("<tool_call>")
    end_of_thinking_token_id = llm._tokenizer.convert_tokens_to_ids("</think>")
    stop_token = llm._tokenizer.eos_token_id

    generated_answer = []
    for _ in range(MAX_NEW_TOKENS):
        expected_token = greedySearch(tokens_ids, llm)

        if expected_token == stop_token:
            break

        elif expected_token == tool_call_token_id:
            # call fms function takes {generated_answer, tokens_ids}
            pass

        generated_answer.append(expected_token)

    else:
        raise ModelExceedTokensLimitException(MAX_NEW_TOKENS)

    return llm.decode(generated_answer)
