# Agent_function_calling

## Overview
This project is mainly a constrained decoding engine designed to guide a low-parameter Language Model (LLM) to output correct, schema-based JSON syntax for function calls. The primary goal is to build a constrained decoding engine leveraging the chosen model's token-level finite state machine (FSM). 

**Note:** Because the framework relies on low-parameter models, the main loop and the LLM might hallucinate. The main focus here is demonstrating how the constrained decoding engine enforces strict topological structure and correct JSON syntax for agentic tool use, rather than perfect logical reasoning from the model itself.

## How to Run

To start the agentic loop, you can use `uv` to run the project:

```bash
uv run agent [FLAGS]
```

### Flags
- `-h`, `--help`: Show the help message and exit.
- `-r`, `--reasoning`: Enable "Internal Monologue" mode. This prints the model's step-by-step reasoning process before tool execution.

### Interactive Commands
While the agent is running, you can use the following commands at the prompt:
- `exit` or `quit`: Safely terminate the agent and stop execution.
- `help`: Show the help message and exit.

## Tool Configuration
The agent dynamically loads tools from the `config/tools/` directory. To expand the agent's capabilities, you must populate the following:

1. **`config/tools/definitions/`**
   Place your tool JSON schemas (`[tool_name].json`) here.
2. **`config/tools/implementations/`**
   Place your tool Python logic (`[tool_name].py`) here. Ensures the filename matches the definition.
3. **`config/tools/tools_map.py`**
   **CRITICAL**: You must update the mapping registry in this file to link the definition to the implementation. The agent will not execute a tool unless it is registered here.
4. **`config/tools/fsm_schema.json`**
   **CRITICAL**: Update the FSM schema. This guides the model's constrained decoding to ensure the output remains syntactically valid for the newly added tools.
