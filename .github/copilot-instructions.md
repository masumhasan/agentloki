## Purpose
Short, actionable guidance for AI coding agents working in this repo (agentloki). Focus: where to look, conventions to follow, and quick run/debug steps.

## Quick start (developer)
- Create and activate a Python venv, then install dependencies:
  - See `requirements.txt` for required packages (LiveKit agents & plugins, mem0, duckduckgo, langchain_community, python-dotenv).
- Copy your secrets into a `.ENV` file (or set env vars):
  - LIVEKIT_URL, LIVEKIT_SECRET (LiveKit)
  - GMAIL_USER, GMAIL_APP_PASSWORD (for `send_email`)
  - N8N_MCP_SERVER_URL (if using `agent2.py` MCP integration)
- Run the agent with: `python agent.py` or `python agent2.py` (both call `agents.cli.run_app`).

## Big-picture architecture
- Entry points: `agent.py` and `agent2.py` — both create a LiveKit `Agent` subclass and start an `AgentSession`.
- Tools: `tools.py` contains helper functions decorated with `@function_tool()` (LiveKit pattern). Example: `get_weather(context, city)` returns a string.
- Prompts and behavior: `prompts.py` (and `prompts2.py`) define `AGENT_INSTRUCTION` and `SESSION_INSTRUCTION` used as agent instructions/persona.
- MCP integration: `mcp_client/` contains:
  - `server.py` — MCPServer abstractions (SSE and stdio examples) and caching behavior.
  - `util.py` — converts MCP tools into repo-local FunctionTool wrappers.
  - `agent_tools.py` — `MCPToolsIntegration` which fetches tools and registers them on LiveKit agents.
- Memory: `agent2.py` shows usage of `mem0` (`AsyncMemoryClient`) to load/save chat context.

## Project-specific conventions (important to follow)
- Tool functions must use LiveKit's `@function_tool()` and accept a `context` first argument (see `tools.py`). Return values should be strings; the codebase expects stringified tool outputs.
- Dynamic MCP tools are converted to `FunctionTool` objects by `mcp_client.util.MCPUtil.to_function_tool` and then decorated via `livekit.agents.llm.function_tool()` in `mcp_client.agent_tools._create_decorated_tool`.
  - When adding or testing MCP flows, prefer `MCPServerSse` (see `mcp_client/server.py`) and set `cache_tools_list=True` when server tools are stable.
- Agents extend `livekit.agents.Agent` and pass `instructions` and an `llm` instance in the constructor (see `Assistant` in `agent.py`/`agent2.py`).
- When registering tools dynamically, code uses `agent._tools` (list) — tests and code assume this attribute exists.

## Useful examples to copy from
- Registering MCP tools + creating agent: see `agent2.py` lines where `MCPToolsIntegration.create_agent_with_tools` is used to instantiate `Assistant` with MCP tools.
- Tool signature example (from `tools.py`):
  - async def get_weather(context: RunContext, city: str) -> str
- MCP tool invocation flow: `MCPUtil.invoke_tool` serializes kwargs to JSON and expects server responses with `content` list; conversion to string happens in `mcp_client/util.py`.

## Developer workflows & debugging
- Install: `python -m pip install -r requirements.txt` (use your venv's python executable).
- Run an agent for local debugging: `python agent2.py` — watch logs. Enable verbose logging by adding `import logging; logging.basicConfig(level=logging.DEBUG)` near entrypoint or set environment-driven logging in your runner.
- Test mem0 client: `python test_mem0.py` to validate memory reads/writes.
- Common failures:
  - Missing env vars (LiveKit, Gmail, N8N_MCP_SERVER_URL) — check `.ENV`.
  - Gmail auth: use an App Password and set `GMAIL_APP_PASSWORD`.
  - MCP server connectivity: verify `N8N_MCP_SERVER_URL` and inspect `mcp_client/server.py` logs.

## When modifying or adding tools
- Follow `tools.py` patterns: decorate with `@function_tool()`, first arg `context`, return a string (or something JSON-serializable that the agent expects).
- If adding MCP-exported tools, ensure JSON schema in the MCP tool is accurate. The conversion code maps JSON schema types to Python types (`mcp_client/agent_tools.py` type_map).

## What to look at first when you arrive
- `agent2.py` — shows the most complete integration: memory + MCP + dynamic tools.
- `mcp_client/` — essential for understanding cross-component tool discovery and invocation.
- `tools.py` and `prompts.py` — examples of tool implementations and persona instructions.

If anything in this document is unclear or missing examples you need (run commands, env var names, or a sample `.ENV`), tell me which area to expand and I'll iterate.
