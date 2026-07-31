# Do-Stuff

## This is an opensource agent (wip)

- reAct tool calling
- opentelemetry tracing
- short term memory
- long term memory
- context management
- skill support
- mcp servers support (stdio)

## Setup

- create a `.env` in the root and refer `.env.example` for the variables
- create and activate a `venv`
- run `pip install -r requirements.txt`
- run `python app.py`

## Tools

- `write_file`
- `read_file`
- `list_files`
- `delete_file`
- `read_skill`

## Guidelines

- Main agent code is present in `agent/run_agent.py`
- To create a new tool:
  - add a new file in the `tools` directory with name matching that of the tool func
  - update `tools/definitions.py`
- New files will be created in the `agent_workspace` directory
- Add skills in the `skill` directory. Sample skills present. Refer [this](https://agentskills.io/home) for more info.

### Long Term Memory

- Long term memories are saved on exit.

### MCP Servers

- Add mcp servers in the `mcp_config.json`
