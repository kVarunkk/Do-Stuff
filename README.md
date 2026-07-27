# Do-Stuff

## This is an opensource agent (wip)

- reAct tool calling
- opentelemetry tracing
- In memory store: short term memory
- long term memory (coming soon)
- context management (coming soon)

## Setup

- create a `.env` in the root and refer `.env.example` for the variables
- create and activate a `venv`
- run `pip install -r requirements.txt`
- run `python app.py`

## Guidelines

- reAct loop is present in `agent/run_tool.py`
- to create a new tool:
  - add a new file in the `tools` directory with name matching that of the tool func
  - update `tools/definitions.py`
  - update the `TOOL_MAP` in `helpers/agent/constants.py`
