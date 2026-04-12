from State_preparation.initial_prompt import initial_message
from llm_sdk import Small_LLM_Model


def main():
    llm = Small_LLM_Model(model_name="Qwen/Qwen3-0.6B")
    string: str = initial_message(llm)
    print(string)



if __name__ == "__main__":
    main()
