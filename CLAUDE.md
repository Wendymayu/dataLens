# DataLens Project Guide

## Overview

Natural language database query system using Claude AI to translate queries into SQL. Four-layer architecture: Frontend (Vue 3) → API (FastAPI) → Agent (NL2SQL) → MCP Server (database access).

## Architecture

- **Frontend** (`frontend/`): Vue 3 + TypeScript + Naive UI, entry: `src/main.ts`
- **API** (`api/`): FastAPI REST API, entry: `main.py`
- **Agent** (`agent/`): NL2SQL translation, files: `agent.py`, `mcp_client.py`
- **MCP Server** (`mcp_server/`): Database connection pool + tools, runs as subprocess

## Tech Stack

**Backend**: Python 3.13, FastAPI, Anthropic Claude, MCP, MySQL, Uvicorn  
**Frontend**: Vue 3, TypeScript, Vite, Naive UI, Pinia, Axios, Tailwind CSS

## Quick Start

```bash
# Backend (port 8000)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (port 5173, proxies /api to backend)
cd frontend && npm install && npm run dev

# CLI mode
python main.py
```

## Critical Conventions

### MCP Server
- **Runs as subprocess** - does NOT auto-reload with `--reload`
- **Must restart API server** to pick up MCP server code changes
- Logs to `mcp_server.log`

### Database Safety
- **Read-only queries only**: SELECT, SHOW, DESCRIBE, EXPLAIN
- Results limited to 100 rows
- All queries validated by MCP server

### JSON Serialization
- Handle non-serializable types: `date`, `datetime`, `Decimal`, `bytes`
- Use `default=str` in `json.dumps()` or convert explicitly
- Dates → ISO format strings

### Code Style
- Use async/await for I/O operations
- Add type hints to function signatures

## File Structure

```
dataLens/
├── frontend/          # Vue 3 SPA
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── stores/      # Pinia stores
│   │   ├── services/    # API client
│   │   └── main.ts
│   └── vite.config.ts
├── agent/             # Agent layer
│   ├── agent.py       # NL2SQL agent
│   ├── mcp_client.py  # MCP client wrapper
│   └── config.py
├── api/               # API layer
│   ├── main.py        # FastAPI app
│   ├── routers/       # API routes
│   └── services/      # Business logic
├── mcp_server/        # MCP server
│   ├── server.py      # MCP server
│   ├── connection_pool.py  # Connection pool
│   └── tools/         # Database tools
├── data/conversations/  # Chat history
├── config.json        # DB config
└── main.py           # CLI entry
```

## Common Tasks

**Add database**: Edit `config.json`, restart API server

**Add MCP tool**: 
1. Define in `mcp_server/server.py` (`list_tools()`, `call_tool()`)
2. Implement in `mcp_server/tools/database_tools.py`
3. Add method in `agent/mcp_client.py`
4. Restart API server

**Debug**: Check `mcp_server.log`, test MCP client directly before API

## Known Issues

- MCP server subprocess doesn't auto-reload
- Network timeout pushing to GitHub (may need proxy)
- Windows CRLF warnings (can ignore)

## Config

**Environment**: `ANTHROPIC_API_KEY` (required), `DATALENS_DB_CONFIG` (internal)

**Git**: Main branch `master`, dev branch `develop`