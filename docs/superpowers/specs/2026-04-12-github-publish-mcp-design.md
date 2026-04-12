# Design Spec: GitHub Publication + MCP Integration Readiness

**Date:** 2026-04-12
**Author:** Dogukan + Claude
**Status:** Draft — awaiting approval

---

## 1. Goal

Sanitize, internationalize, and prepare the CS Agent project for public GitHub release. Add MCP (Model Context Protocol) integration readiness for Gmail and Supabase without active connections.

**Priority order:**
1. Sanitization (PII, API keys, real client data removal)
2. MCP infrastructure (config templates + minimal dispatch hook)
3. README + documentation (English)
4. 3-Expert AI Engineer Feedback Simulation (final gate before commit)
5. GitHub commit + publish

**Non-goal:** Production deployment for the company (secondary, maybe later).

---

## 2. Language Policy

| Layer | Language | Examples |
|-------|----------|----------|
| Project code | English | Variable names, comments, docstrings, error messages |
| Documentation | English | README.md, docs/, .env.example, CLAUDE.md |
| Config | English | config.py keys, CLI output |
| System prompt | English | Agent behavioral rules, routing matrix (output language rules define PL/TR/EN) |
| Wiki SOPs | Turkish/Polish (as-is) | Domain content — tax calendars, payroll procedures. File content stays as-is. |
| Wiki INDEX.md | English | Category headers and article descriptions translated to English |
| Wiki mechanism docs | English | Architecture explanation, how wiki_read works |
| Agent output | Polish/Turkish/English | User-facing responses, message drafts |

---

## 3. Sanitization

### 3.1 Files to clean

| Target | Action |
|--------|--------|
| `.env` | Delete. Replace with `.env.example` (English placeholders, empty values) |
| `clients.csv` | Replace 142 real firms with 10 real large Polish companies (real NIP from public records, fake operational data) |
| `traces/` | Delete all `.jsonl` files, keep `.gitkeep` |
| `outputs/` | Delete all generated PDF/DOCX/XLSX, keep `.gitkeep` |
| `traces/sessions/` | Delete all session files, keep `.gitkeep` |
| `settings.local.json` | Add to `.gitignore` (contains API keys) |
| `benchmarks/results_*` | Delete result files, keep `qa_pairs.json` |
| `agent.py` | Scan for hardcoded NIP, firm names, API keys |

### 3.2 Code internationalization

| Target | Action |
|--------|--------|
| `agent.py` comments (~200 lines) | Translate Turkish comments to English |
| `SYSTEM_PROMPT` string | Translate to English (preserve output language rules for PL/TR/EN) |
| `config.py` comments | Translate to English |
| Error messages (`"Hata: ..."`) | Translate to English (`"Error: ..."`) |
| CLI output (`"Cikmak icin 'q' yazin"`) | Translate to English |
| Tool descriptions in TOOLS list | Translate to English |
| Function docstrings | Translate to English |

### 3.3 Sample mastersheet companies

10 large Polish companies with real NIP (publicly available from KRS):

| Company | Real NIP | Fake operational data |
|---------|----------|----------------------|
| PKN Orlen | (from KRS) | Fake accountant, VAT date, tax office |
| KGHM Polska Miedz | (from KRS) | " |
| PZU | (from KRS) | " |
| Allegro | (from KRS) | " |
| CD Projekt | (from KRS) | " |
| LPP | (from KRS) | " |
| Dino Polska | (from KRS) | " |
| CCC | (from KRS) | " |
| Zabka | (from KRS) | " |
| InPost | (from KRS) | " |

NIP values will be looked up from public KRS/CEIDG records during implementation.

### 3.4 .env.example

```
# Required
OPENROUTER_API_KEY=your_openrouter_key_here
EXA_API_KEY=your_exa_key_here

# Optional: Model override
# API_BASE=https://openrouter.ai/api/v1
# MODEL=claude-sonnet-4-6-20250217

# MCP Integrations (optional)
MCP_GMAIL_ENABLED=false
MCP_SUPABASE_ENABLED=false
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Benchmark judge model
# JUDGE_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

### 3.5 .gitignore additions

```
.env
traces/*.jsonl
traces/sessions/*
outputs/*
benchmarks/results_*.json
.claude/settings.local.json
__pycache__/
*.pyc
```

---

## 4. MCP Integration Readiness

### 4.1 Approach

Lightweight MCP client infrastructure inside the existing single-file architecture. No active connections — everything disabled by default behind environment flags.

### 4.2 config.py additions

```python
# MCP Servers (optional integrations)
"mcp_servers": {
    "gmail": {
        "enabled": os.getenv("MCP_GMAIL_ENABLED", "false").lower() == "true",
        "transport": "stdio",
        "command": ["npx", "@anthropic/mcp-gmail"],
    },
    "supabase": {
        "enabled": os.getenv("MCP_SUPABASE_ENABLED", "false").lower() == "true",
        "transport": "stdio",
        "command": ["npx", "supabase-mcp-server"],
        "env": {
            "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
            "SUPABASE_KEY": os.getenv("SUPABASE_KEY", ""),
        },
    },
},
```

### 4.3 agent.py additions (~40 lines)

Four functions added to agent.py:

1. **`_init_mcp_servers()`** — Start enabled MCP servers as subprocesses at agent startup
2. **`_discover_mcp_tools(server_name)`** — Query an MCP server for its available tools via stdio JSON-RPC
3. **`_call_mcp_tool(server_name, tool_name, args)`** — Execute a tool call on an MCP server
4. **`execute_tool` modification** — Add MCP fallback: if tool not found in local registry, check MCP servers

### 4.4 Dispatch flow

```
execute_tool("gmail_send", args)
  -> local tool dict lookup -> not found
  -> MCP registry lookup -> "gmail" server enabled?
     -> yes -> _call_mcp_tool("gmail", "send", args)
     -> no  -> "Error: unknown tool 'gmail_send'"
```

### 4.5 What this does NOT include

- No active MCP connections at startup (all disabled by default)
- No MCP tool definitions in the TOOLS list (discovered at runtime when enabled)
- No subprocess management (graceful shutdown, health checks) — kept simple
- No MCP server implementation (agent is client only)

---

## 5. Documentation

### 5.1 README.md (English)

Structure:
```
# CS Agent
> Self-hosted customer success AI agent for accounting firms operating in Poland.

## Features
## Quick Start
## Configuration
## Architecture
## MCP Integration (Optional)
## API Endpoints
## CLI Modes
## Benchmarks
## License
```

### 5.2 docs/mcp-setup.md (English)

Gmail and Supabase MCP setup guide:
- Prerequisites (Node.js, npx)
- Environment variables
- Enabling each server
- Verifying connection
- Available tools per server

### 5.3 Existing docs

- `docs/master_architecture.md` — stays as-is (internal reference)
- `docs/gdpr_policy.md` — stays as-is
- `docs/task_list.md` — stays as-is

---

## 6. Expert Simulation Gate (Pre-Commit)

### 6.1 Timing

After ALL sanitization, MCP infrastructure, and documentation is complete. Final gate before `git commit`.

### 6.2 Three experts

| Expert | Perspective | Focus |
|--------|-------------|-------|
| **Karpathy** | Harness & Tools | Code quality, tool design, agent loop, MCP architecture, single-file discipline |
| **Ng** | Deployment & Ops | Sanitization completeness, security, .env, Docker, GitHub-readiness, docs quality |
| **LeCun** | World Model & Extensibility | Architectural extensibility, MCP integration points, data model, scalability |

### 6.3 Evaluation criteria (GitHub-showcase focused)

- PII zero-tolerance (no real client data anywhere in tracked files)
- Code quality and readability
- Documentation completeness
- MCP readiness (clean config, clear setup path)
- Docker-readiness
- Benchmark presence
- License

### 6.4 Pass criteria

All 3 experts give **go** for GitHub publication. Any blocker → fix → re-evaluate.

---

## 7. Out of Scope

- Active MCP server connections
- Supabase migration of mastersheet
- Gmail send/receive implementation
- Production HTTPS/TLS setup
- CI/CD pipeline
- Automated testing beyond existing benchmarks
