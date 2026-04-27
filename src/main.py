from llm_sdk import Small_LLM_Model
from src.Constrained_decoding.generateAnswerAndUpdateContextWindow import generateAnswerAndUpdateContextWindow
from src.State_preparation.ContextWindow import ContextWindow
from src.Constrained_decoding.FiniteStateMachine import FiniteStateMachine
from colorama import Fore, Back
import sys, getopt
import src.Constrained_decoding.generateAnswerAndUpdateContextWindow
from src.Exceptions.constrained_decoding_exceptions import ModelExceedTokensLimitException


def printHelp():
    help_text = """
    LOW-PARAM AGENT v1.0 - Tool-Execution Framework

    USAGE:
        uv run agent [FLAGS]

    FLAGS:
        -h, --help        Show this help message and exit.
        -r, --reasoning   Enable "Internal Monologue" mode. Prints the model's
                          step-by-step reasoning process before tool execution.

    INTERACTIVE COMMANDS:
        exit              Type 'exit' or 'quit' at the prompt to safely
                          terminate the agent and stop execution.
        help              Show this help message and exit.

    TOOL CONFIGURATION:
        The agent dynamically loads tools from the 'config/tools/' directory.
        To expand the agent's capabilities, you must populate two sub-directories:

        1. config/tools/definitions/
           Place your [tool_name].json files here (JSON schemas).

        2. config/tools/implementations/
           Place your [tool_name].py files here (Python logic).

        3. config/tools/tools_map.py
           CRITICAL: You must update the mapping registry in this file
           to link the definition to the implementation. The agent
           will not execute a tool unless it is registered here.

        4. config/tools/fsm_schema.json
           CRITICAL: Update the FSM schema. This guides the model's 
           constrained decoding to ensure the output remains 
           syntactically valid for the newly added tools.

    NOTE:
        Ensure that the filename in 'definitions/' matches the filename in
        'implementations/' for successful auto-linking.
    """
    print(Fore.LIGHTGREEN_EX + help_text + Fore.RESET)


def getOptions():
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hr", ["help", "reasoning"])
    except getopt.GetoptError as e:
        print(Fore.RED + "Error:")
        print(f"    {e}", end="")
        print(Fore.RESET)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printHelp()
            sys.exit()

        elif opt in ("-r", "--reasoning"):
            src.Constrained_decoding.generateAnswerAndUpdateContextWindow.SHOW_REASONING = True
            print(Fore.LIGHTGREEN_EX + "thinking enabled")


def main():
    # handle options
    getOptions()

    print(Fore.LIGHTGREEN_EX + "Loading the agent...")
    llm = Small_LLM_Model(model_name="Qwen/Qwen3-0.6B")
    context_window = ContextWindow()
    fsm = FiniteStateMachine(llm)

    while True:
        prompt = input(Back.LIGHTBLUE_EX + Fore.BLACK + 'ask agent >' + Back.RESET + Fore.BLUE + ' ')
        print(Fore.RESET)

        if prompt == "exit":
            sys.exit()
        elif prompt == "help":
            printHelp()
            continue

        context_window.appendMessage("user", prompt)
        try:
            generateAnswerAndUpdateContextWindow(llm, context_window, fsm)
        except ModelExceedTokensLimitException as e:
            print(Fore.RED + "Error:")
            print(f"    {e.message}", end="")
            print(Fore.RESET)


if __name__ == "__main__":
    main()
