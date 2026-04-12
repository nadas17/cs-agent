# CS Agent

A self-hosted AI agent for customer success operations at accounting firms. Built as a single-file harness with function calling, wiki-based knowledge management, and MCP-ready extensibility.

Designed for firms operating in Poland — handling tax compliance, payroll coordination, onboarding, immigration support, and client communication across Turkish, Polish, and English.

---

## Design Philosophy

This project applies ideas from three perspectives in AI agent design:

**Compiled Context over RAG** — Instead of vector search, the agent uses a wiki of 24 markdown SOP articles injected into the system prompt via an index. The LLM reads the index and decides which article to fetch. This eliminates embedding pipelines and retrieval latency while keeping knowledge grounded and editable.

**Human-in-the-Loop Tiers** — Every query is classified into one of three tiers: Tier 1 (autonomous — the agent responds directly), Tier 2 (approval required — drafts, documents, wiki writes), Tier 3 (human only — legal, complaints, contract changes). The tier boundary shifts over time based on trace analysis.

**Decision Traces as Institutional Memory** — Every agent interaction produces a structured trace: query type, tier classification, tools called, wiki articles used, routing decisions, grounding results, latency. These traces feed the admin dashboard, gap detection, and benchmark regression system.

---

## Architecture

```
User query → classify_query (intent) → classify_tier (1/2/3)
           → build_messages (system_prompt + wiki_index + history)
           → model_call (LLM via OpenRouter / Anthropic / local)
           → tool calls loop (max 10 per turn)
           → grounding_check → final response + trace log
```

Single-file harness: all logic lives in `agent.py` (~2,900 lines). No framework, no separate modules. Configuration in `config.py`. This is a deliberate design choice — the entire agent is readable, debuggable, and deployable as one unit.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| LLM | OpenAI-compatible API (OpenRouter, Anthropic, LM Studio) | Dual-API support with automatic detection |
| Function Calling | OpenAI tool format | 8 built-in tools + MCP fallback |
| Knowledge Base | Markdown wiki (24 SOPs) | Compiled context, no vector DB |
| Client Data | CSV mastersheet | Fuzzy search by name, NIP, type, accountant |
| HTTP API | FastAPI + Uvicorn | 13 endpoints including admin dashboard |
| Rate Limiting | slowapi | IP-based, per-endpoint configuration |
| Documents | fpdf2, python-docx, openpyxl | Branded PDF, DOCX, XLSX generation |
| Web Search | Exa API | Current regulations and procedures |
| Registry Lookup | KRS API | Polish company registry (KRS/NIP/REGON) |
| Extensibility | MCP (Model Context Protocol) | Pre-configured Gmail + Supabase integration points |
| Deployment | Docker + Docker Compose | Single-command deployment |
| Evaluation | LLM-as-judge | 100-question benchmark with separate judge model |

---

## Tools

| Tool | Type | Description |
|------|------|-------------|
| `wiki_read` | Knowledge | Read SOP articles with auto-truncation and draft warnings |
| `wiki_write` | Knowledge | Create/update articles with automatic version history |
| `mastersheet_read` | Data | Query clients by name, NIP, type, or accountant (fuzzy match) |
| `exa_search` | External | Web search for current tax/legal information |
| `krs_lookup` | External | Polish company registry lookup |
| `create_pdf` | Output | Generate branded PDF documents |
| `create_docx` | Output | Generate Word documents |
| `create_xlsx` | Output | Generate Excel spreadsheets |

---

## Quick Start

### Prerequisites

- Python 3.12+
- An LLM API key ([OpenRouter](https://openrouter.ai), [Anthropic](https://console.anthropic.com), or local via [LM Studio](https://lmstudio.ai))

### Setup

```bash
git clone https://github.com/nadas17/cs-agent.git
cd cs-agent
pip install -r cs-agent/requirements.txt
cp cs-agent/.env.example cs-agent/.env
# Edit .env with your API keys
```

### Run

```bash
# Interactive REPL
python cs-agent/agent.py

# Single query
python cs-agent/agent.py "What documents are needed for VAT registration?"

# HTTP API server
python cs-agent/agent.py --serve
```

### Docker

```bash
cd cs-agent
docker-compose build && docker-compose up -d
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Main agent endpoint (rate limited: 30/min) |
| `/feedback` | POST | User feedback on responses |
| `/health` | GET | Service health check |
| `/files/{filename}` | GET | Download generated documents |
| `/admin/dashboard` | GET | Real-time monitoring dashboard |
| `/admin/stats` | GET | Query statistics and tier distribution |
| `/admin/report` | GET | Weekly performance report |
| `/admin/deadlines` | GET | Upcoming tax/compliance deadlines |
| `/admin/silent` | GET | Inactive clients requiring follow-up |
| `/admin/gaps` | GET | SOP coverage gaps |
| `/admin/alerts` | GET | Recent errors and anomalies |

---

## CLI Modes

```bash
python agent.py --serve [port]     # HTTP API server (default: 8000)
python agent.py --stats            # Tier distribution from traces
python agent.py --report           # Weekly summary report
python agent.py --deadlines [days] # Upcoming tax deadlines
python agent.py --silent [days]    # Inactive clients
python agent.py --gaps             # SOP coverage gaps
python agent.py --trends [days]    # Trace trend analysis
python agent.py --promotions       # Tier promotion candidates
python agent.py --optimize         # Daily optimization run
python agent.py --remind [days]    # Generate deadline reminder drafts
python agent.py --purge-old-traces # GDPR: delete traces older than N days
```

---

## MCP Integration

The agent supports optional [Model Context Protocol](https://modelcontextprotocol.io) server integrations, pre-configured for:

- **Gmail** — Email operations (read, draft, send)
- **Supabase** — Database operations (replace CSV, store sessions)

MCP servers run as stdio subprocesses. Tools are discovered at startup and routed via a tool-to-server registry. Enable by setting environment flags:

```bash
MCP_GMAIL_ENABLED=true
MCP_SUPABASE_ENABLED=true
```

See [docs/mcp-setup.md](docs/mcp-setup.md) for full setup instructions.

---

## Benchmarks

100 Q&A pairs across 7 categories: procedure, routing, deadline, customer, constraint, edge-case, and multi-tool scenarios.

```bash
python cs-agent/run_benchmark.py
```

Uses LLM-as-judge evaluation with a separate model (default: Llama 3.3 70B) to reduce self-evaluation bias. Supports regression diffing, hill climbing, and feedback-to-QA generation.

---

## Project Structure

```
cs-agent/
├── README.md
├── docs/
│   ├── master_architecture.md    # Architectural vision document
│   ├── gdpr_policy.md            # RODO/GDPR data handling policy
│   └── mcp-setup.md              # MCP integration guide
└── cs-agent/
    ├── agent.py                  # Single-file harness (~2,900 lines)
    ├── config.py                 # Configuration + MCP server definitions
    ├── run_benchmark.py          # Benchmark runner with LLM-as-judge
    ├── chat.html                 # Web UI (dark theme)
    ├── .env.example              # Environment template
    ├── Dockerfile / docker-compose.yml
    ├── wiki/                     # 24 SOP articles (8 categories)
    ├── mastersheet/              # Client data (CSV)
    ├── benchmarks/               # 100 Q&A pairs
    ├── outputs/                  # Generated documents
    └── traces/                   # Decision traces + sessions
```

---

## License

MIT
