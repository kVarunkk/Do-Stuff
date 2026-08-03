# Do-Stuff

## This is an opensource agent (wip)

- reAct tool calling
- opentelemetry tracing
- short term memory
- long term memory
- context management
- skill support
- mcp servers support (stdio and http (Dynamic Client Registration support only))

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

- Add mcp servers in the `mcp_config.json`. Sample remote and local servers present.

### Observability

- Use this command to spin up a Jaeger container:
  ``docker run -d --name jaeger `
-e SPAN_STORAGE_TYPE=badger `
-e BADGER_EPHEMERAL=false `
-e BADGER_DIRECTORY_VALUE=/badger/data `
-e BADGER_DIRECTORY_KEY=/badger/key `
-v ${PWD}/jaeger_data:/badger `
-p 16686:16686 `
-p 4317:4317 `
-p 4318:4318 `
jaegertracing/all-in-one:latest``
- Open `http://localhost:16686` on your browser to view live traces.
