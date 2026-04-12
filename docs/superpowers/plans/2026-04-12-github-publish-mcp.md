# GitHub Publication + MCP Readiness — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sanitize, internationalize, and add MCP readiness to the CS Agent for public GitHub release.

**Architecture:** Single-file harness stays intact. All changes are in-place edits to existing files (agent.py, config.py) plus new config/doc files. No new Python modules. MCP client code lives inside agent.py behind feature flags.

**Tech Stack:** Python 3.12, OpenAI SDK, FastAPI, MCP protocol (stdio/JSON-RPC)

**Spec:** `docs/superpowers/specs/2026-04-12-github-publish-mcp-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `cs-agent/agent.py` | Modify | Translate comments/errors/docstrings/SYSTEM_PROMPT to English, add MCP client functions |
| `cs-agent/config.py` | Modify | Translate comments to English, add MCP server configs |
| `cs-agent/.env` | Delete | Contains real API keys |
| `cs-agent/.env.example` | Create | English template with all env vars |
| `cs-agent/.gitignore` | Create | Exclude sensitive/generated files |
| `cs-agent/mastersheet/clients.csv` | Rewrite | Replace 142 real firms with 10 Polish companies |
| `cs-agent/wiki/INDEX.md` | Modify | Translate category headers and descriptions to English |
| `README.md` (project root) | Create | English project documentation |
| `docs/mcp-setup.md` | Create | MCP integration guide (English) |
| `cs-agent/traces/*.jsonl` | Delete | Real trace data with PII |
| `cs-agent/traces/sessions/*.json` | Delete | Real session data |
| `cs-agent/traces/client_state.json` | Delete | Real client state |
| `cs-agent/outputs/*` | Delete | Generated documents with real data |
| `cs-agent/benchmarks/results_*.json` | Delete | Real benchmark results |
| `cs-agent/benchmarks/baseline.json` | Delete | Real baseline data |

---

## Task 1: File Cleanup — Delete Sensitive Data

**Files:**
- Delete: `cs-agent/.env`
- Delete: `cs-agent/traces/*.jsonl` (all)
- Delete: `cs-agent/traces/client_state.json`
- Delete: `cs-agent/traces/sessions/*.json` (all)
- Delete: `cs-agent/outputs/*` (all PDFs, DOCXs)
- Delete: `cs-agent/benchmarks/results_*.json`
- Delete: `cs-agent/benchmarks/baseline.json`

- [ ] **Step 1: Delete .env file**

```bash
rm cs-agent/.env
```

- [ ] **Step 2: Clean traces directory**

```bash
rm -f cs-agent/traces/*.jsonl
rm -f cs-agent/traces/client_state.json
rm -f cs-agent/traces/sessions/*.json
```

- [ ] **Step 3: Clean outputs directory**

```bash
rm -f cs-agent/outputs/*
```

- [ ] **Step 4: Clean benchmark results**

```bash
rm -f cs-agent/benchmarks/results_*.json
rm -f cs-agent/benchmarks/baseline.json
```

- [ ] **Step 5: Add .gitkeep files to empty directories**

```bash
touch cs-agent/traces/.gitkeep
touch cs-agent/traces/sessions/.gitkeep
touch cs-agent/outputs/.gitkeep
```

- [ ] **Step 6: Verify no sensitive files remain**

```bash
# Should show only .gitkeep files in traces/, outputs/
ls -la cs-agent/traces/
ls -la cs-agent/traces/sessions/
ls -la cs-agent/outputs/
# Should show only qa_pairs.json in benchmarks/
ls -la cs-agent/benchmarks/
# .env should not exist
ls cs-agent/.env 2>&1  # Expected: No such file
```

---

## Task 2: Create .gitignore and .env.example

**Files:**
- Create: `cs-agent/.gitignore`
- Create: `cs-agent/.env.example`

- [ ] **Step 1: Create .gitignore**

```
# Environment
.env

# Traces and sessions (contain PII)
traces/*.jsonl
traces/client_state.json
traces/sessions/*.json

# Generated documents
outputs/*
!outputs/.gitkeep

# Benchmark results (keep qa_pairs.json)
benchmarks/results_*.json
benchmarks/baseline.json

# Claude Code local settings
.claude/settings.local.json

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

Write this to `cs-agent/.gitignore`.

- [ ] **Step 2: Create .env.example**

```
# =============================================================================
# CS Agent — Environment Configuration
# =============================================================================

# Required: LLM API
OPENROUTER_API_KEY=your_openrouter_key_here
EXA_API_KEY=your_exa_key_here

# Optional: Model override (defaults to claude-sonnet-4-6-20250217 via OpenRouter)
# API_BASE=https://openrouter.ai/api/v1
# MODEL=claude-sonnet-4-6-20250217

# Optional: Local model (e.g., LM Studio)
# API_BASE=http://localhost:1234/v1
# MODEL=local-model-name

# MCP Integrations (optional — see docs/mcp-setup.md)
MCP_GMAIL_ENABLED=false
MCP_SUPABASE_ENABLED=false
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Benchmark judge model (should differ from agent model to reduce bias)
# JUDGE_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

Write this to `cs-agent/.env.example`.

- [ ] **Step 3: Verify .gitignore catches sensitive files**

```bash
cd cs-agent && git init --quiet 2>/dev/null; git status --short
# .env should NOT appear, .env.example SHOULD appear
```

---

## Task 3: Replace Mastersheet with Sample Polish Companies

**Files:**
- Rewrite: `cs-agent/mastersheet/clients.csv`

The current mastersheet has 142 real client firms with real NIP, PESEL, addresses, and bank accounts. Replace with 10 large, publicly-known Polish companies using their real NIP (public KRS data) but fake operational fields.

- [ ] **Step 1: Look up real NIP values for 10 Polish companies**

Search public KRS/CEIDG records for these companies:
1. PKN Orlen
2. KGHM Polska Miedz
3. PZU
4. Allegro
5. CD Projekt
6. LPP
7. Dino Polska
8. CCC
9. Zabka
10. InPost

Use web search or KRS API to find their real NIP and KRS numbers.

- [ ] **Step 2: Write new clients.csv**

Preserve the exact CSV header from the original file:
```
Nr,Responsible,RA,Company Name,NIP/PESEL,TYP,KRS,REGON,KRS Kayit Tarihi,VAT Aktiflik Tarihi,Adres,US,Mikrorachunek,ZUS Account,Soyad,Ad
```

Create 10 rows with:
- **Real:** Company Name, NIP/PESEL, KRS (from public records)
- **Fake:** RA (assign to Katarzyna, Liudmila, or nowy pracownik), VAT Aktiflik Tarihi, Adres (use company's real city but simplified), US (plausible tax office), Mikrorachunek (fake PL00 format), ZUS Account (fake), Soyad/Ad (fake Polish contact names)
- **TYP:** "sp z o o" for all (these are all sp. z o.o. or S.A. — use realistic type)

Write to `cs-agent/mastersheet/clients.csv`.

- [ ] **Step 3: Verify mastersheet_read works with new data**

```bash
cd cs-agent && python -c "
from agent import mastersheet_read
print(mastersheet_read('Orlen'))
print(mastersheet_read('say'))
print(mastersheet_read('rastgele'))
"
```

Expected: Orlen found, count=10, random returns subset.

---

## Task 4: Internationalize config.py

**Files:**
- Modify: `cs-agent/config.py`

- [ ] **Step 1: Translate all Turkish comments to English and add MCP config**

Read `cs-agent/config.py` and rewrite with:

```python
import os

# All paths relative to the directory containing config.py
_BASE = os.path.dirname(os.path.abspath(__file__))

# Load .env file (no python-dotenv dependency)
_env_file = os.path.join(_BASE, ".env")
if os.path.exists(_env_file):
    with open(_env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                k, v = key.strip(), val.strip()
                if v:
                    os.environ[k] = v  # .env always takes precedence

CONFIG = {
    # LLM API
    "api_base": os.getenv("API_BASE", "https://openrouter.ai/api/v1"),
    "api_key": os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENROUTER_API_KEY", ""),
    "model": os.getenv("MODEL", "claude-sonnet-4-6-20250217"),
    "temperature": 0.2,
    "max_tokens": 4096,

    # Wiki knowledge base
    "wiki_dir": os.path.join(_BASE, "wiki"),
    "index_file": os.path.join(_BASE, "wiki", "INDEX.md"),
    "mastersheet_file": os.path.join(_BASE, "mastersheet", "clients.csv"),

    # External APIs
    "exa_api_key": os.getenv("EXA_API_KEY", ""),

    # Output and trace directories
    "output_dir": os.path.join(_BASE, "outputs"),
    "trace_dir": os.path.join(_BASE, "traces"),

    # Agent behavior limits
    "max_tool_calls_per_turn": 10,
    "max_wiki_article_tokens": 3000,
    "wiki_truncate_at": 2500,
    "max_index_chars": 4000,
    "max_history_messages": 10,

    # Rate limiting
    "rate_limit_chat": "30/minute",
    "rate_limit_feedback": "60/minute",
    "rate_limit_admin": "10/minute",

    # Input sanitization
    "max_query_length": 2000,
    "max_feedback_comment_length": 500,

    # Session persistence
    "session_dir": os.path.join(_BASE, "traces", "sessions"),
    "max_active_sessions": 50,
    "session_expire_hours": 24,

    # Benchmark judge model (different from agent model to reduce bias)
    "judge_model": os.getenv("JUDGE_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),

    # MCP Servers (optional integrations — see docs/mcp-setup.md)
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
}
```

Write this to `cs-agent/config.py`, replacing the entire file.

- [ ] **Step 2: Verify config loads correctly**

```bash
cd cs-agent && python -c "
from config import CONFIG
print('API base:', CONFIG['api_base'])
print('MCP Gmail enabled:', CONFIG['mcp_servers']['gmail']['enabled'])
print('MCP Supabase enabled:', CONFIG['mcp_servers']['supabase']['enabled'])
print('Wiki dir:', CONFIG['wiki_dir'])
"
```

Expected: API base = openrouter URL, both MCP servers disabled, wiki dir = absolute path.

---

## Task 5: Internationalize agent.py — SYSTEM_PROMPT

**Files:**
- Modify: `cs-agent/agent.py` (lines 23-209)

This is the largest translation task. The SYSTEM_PROMPT (~187 lines) must be translated to English while preserving the agent's output language rules (Turkish/Polish/English based on context).

- [ ] **Step 1: Translate SYSTEM_PROMPT to English**

Replace the entire `SYSTEM_PROMPT = """..."""` block (lines 23-209) with an English version. Key rules:

- All behavioral instructions in English
- Section headers in English (e.g., "## 1. CORE BEHAVIORAL RULES")
- Team member names stay as-is (Kaan, Dogukan, Rana, Mehtap, Kasia, etc.)
- Output language rules preserved: agent responds in Turkish to internal team, English to accounting/legal team, Turkish/Polish for client message drafts
- Polish legal terms stay with translations: e.g., "VAT registration (rejestracja VAT)", "payroll (lista plac)"
- The self-check rule tags stay as `[SOURCE: article_name.md]`, `[SOURCE: general knowledge]`, `[SOURCE: draft/article_name.md — unverified]`

The translated SYSTEM_PROMPT should maintain the exact same structure: sections 1, 2, 3, 10, 14, Proactive Learning Rule, Self-Check Rule.

- [ ] **Step 2: Verify SYSTEM_PROMPT loads without syntax errors**

```bash
cd cs-agent && python -c "
from agent import SYSTEM_PROMPT
print(f'SYSTEM_PROMPT length: {len(SYSTEM_PROMPT)} chars')
print(SYSTEM_PROMPT[:200])
"
```

Expected: No import errors, prompt loads, first 200 chars show English text.

---

## Task 6: Internationalize agent.py — Comments, Errors, Docstrings

**Files:**
- Modify: `cs-agent/agent.py` (throughout, ~60 edits)

- [ ] **Step 1: Translate section header comments**

Replace all `# =====...` section headers and inline comments. Major sections:

```python
# Before:
# =============================================================================
# TOOLS — wiki_read + mastersheet_read
# =============================================================================

# After:
# =============================================================================
# TOOLS — wiki_read + mastersheet_read
# =============================================================================
# (headers are already English — translate inline Turkish comments)
```

Scan the full file for Turkish comments (lines containing Turkish characters or Turkish words like "dosya", "hata", "bilgi", "silindi", "bulunamadi", etc.) and translate each to English.

- [ ] **Step 2: Translate TOOLS list descriptions**

Replace all 8 tool `description` fields in the TOOLS list (lines 215-355) from Turkish to English. Example:

```python
# Before:
"description": "Wiki makalesinin icerigini okur. INDEX.md'deki listeden makale yolunu sec.",

# After:
"description": "Reads a wiki article's content. Choose the article path from the INDEX.md listing.",
```

Do this for all 8 tools: wiki_read, mastersheet_read, wiki_write, create_pdf, create_docx, create_xlsx, exa_search, krs_lookup.

- [ ] **Step 3: Translate error messages**

Replace all Turkish error/status strings in tool implementations and agent loop. There are ~40 instances (see grep results from exploration). Examples:

```python
# Before:
return f"Hata: '{article_path}' bulunamadi."
# After:
return f"Error: '{article_path}' not found."

# Before:
return f"'{query}' ile eslesen firma bulunamadi."
# After:
return f"No matching firm found for '{query}'."

# Before:
return "API limiti asildi. Lutfen 1-2 dakika sonra tekrar deneyin."
# After:
return "API rate limit exceeded. Please try again in 1-2 minutes."

# Before:
return "Bir hata olustu. Lutfen tekrar deneyin."
# After:
return "An error occurred. Please try again."
```

- [ ] **Step 4: Translate CLI output strings**

```python
# Before:
print("CS Agent v1 — Cikmak icin 'q' yazin")
# After:
print("CS Agent v1 — Type 'q' to quit")

# Before:
print(f"\n{removed} dosya temizlendi ({days} gunden eski).")
# After:
print(f"\n{removed} files cleaned ({days} days old).")

# Before:
print("Trace verisi bulunamadi.")
# After:
print("No trace data found.")
```

Translate all `print()` calls in the CLI section (lines 2190-2866).

- [ ] **Step 5: Translate function docstrings**

Replace Turkish docstrings with English. Example:

```python
# Before:
def classify_tier(query_type, tool_calls, routing_decision):
    """HiTL tier siniflandirmasi. (tier, reason) tuple dondurur."""
# After:
def classify_tier(query_type, tool_calls, routing_decision):
    """HiTL tier classification. Returns (tier, reason) tuple."""
```

- [ ] **Step 6: Translate FastAPI response messages**

```python
# Before:
content={"error": True, "message": "Cok fazla istek gonderdiniz. Lutfen biraz bekleyin."}
# After:
content={"error": True, "message": "Too many requests. Please wait a moment."}

# Before:
return {"error": "Mastersheet bulunamadi"}
# After:
return {"error": "Mastersheet not found"}
```

- [ ] **Step 7: Full verification — import and basic run**

```bash
cd cs-agent && python -c "
from agent import SYSTEM_PROMPT, TOOLS, execute_tool
print('SYSTEM_PROMPT loaded:', len(SYSTEM_PROMPT), 'chars')
print('TOOLS count:', len(TOOLS))
print('wiki_read test:', execute_tool('wiki_read', {'article_path': 'nonexistent.md'}))
"
```

Expected: No import errors. wiki_read returns English error message "Error: 'nonexistent.md' not found."

---

## Task 7: Internationalize wiki/INDEX.md

**Files:**
- Modify: `cs-agent/wiki/INDEX.md`

- [ ] **Step 1: Translate INDEX.md headers and descriptions to English**

Keep article paths unchanged (Turkish filenames stay). Translate only the category headers and one-line descriptions.

```markdown
# Wiki Index
_Last updated: 2026-04-07_

## Onboarding
- onboarding/checklist.md — New client intake steps, required documents, employee onboarding checklist
- onboarding/vekaletname_seti.md — Power of attorney types and requirements for Sp. z o.o. and JDG

## Payroll
- bordro/aylik_akis.md — Monthly payroll workflow, ZUS deadlines, salary calculation process

## Tax
- vergi/beyanname_takvimi.md — ZUS/PIT/CIT/VAT/JPK filing and payment deadlines
- vergi/vat_kaydi_belgeler.md — VAT registration (rejestracja VAT) required documents, process flow, control notes
- vergi/vat_kaydi_rehberi.md — Comprehensive VAT registration guide: VAT-R form, exemption thresholds, intra-EU transactions, Biala Lista
- vergi/efatura_ksef.md — KSeF e-invoice system access and integration steps
- vergi/vergi_borcu_sorgulama.md — ZAS-W certificate inquiry via e-Tax Office (internal use)
- vergi/vergi_borcu_musteri_kilavuzu.md — Client guide for obtaining tax clearance certificate

## Operations
- operasyon/aylik_dongu.md — Monthly accounting workflow, document collection cycle and calendar
- operasyon/belge_toplama.md — Document management, MasterSheet Data page usage
- operasyon/sla_yanitsureleri.md — SLA response times, working hours, emergency rules
- operasyon/fis_fatura_kurallari.md — Company purchases, NIP requirements, receipt/invoice rules
- operasyon/faaliyet_durum_raporu.md — Partner activity status report example (EPIK Poland)
- operasyon/task_management_crm.md — Task management and CRM status SOP

## Immigration
- goc/calisma_izni_rehberi.md — Work permit application: passport scan, fee payment, application steps
- goc/profil_zaufany.md — Polish e-Government account (Profil Zaufany) setup guide
- goc/pesel_alma.md — PESEL number application process and required documents
- goc/banka_hesabi_acma.md — Opening a bank account in Poland: steps and required documents

## Contracts
- sozlesme/genel_kurallar.md — Payment terms, termination, suspension, client obligations, RODO/GDPR

## Communication
- iletisim/kanallar.md — Official communication channels, email addresses, prohibited channels

## Reference
- referans/yasal_terimler.md — Polish legal concepts (KRS, NIP, ZUS, KSeF, etc.)
- referans/mastersheet_yapisi.md — Master Client and Data sheet structure and columns
```

Write this to `cs-agent/wiki/INDEX.md`, replacing the entire file.

- [ ] **Step 2: Verify INDEX.md loads correctly in agent**

```bash
cd cs-agent && python -c "
from agent import build_messages
session = {'messages': [{'role': 'user', 'content': 'test'}]}
msgs = build_messages(session)
system_content = msgs[0]['content']
print('INDEX found in system:', 'Wiki Index' in system_content)
print('Onboarding found:', 'onboarding/checklist.md' in system_content)
"
```

Expected: Both True.

---

## Task 8: Add MCP Client Infrastructure to agent.py

**Files:**
- Modify: `cs-agent/agent.py` (add ~50 lines, modify execute_tool)

- [ ] **Step 1: Add MCP client functions after the TOOLS list**

Insert these functions after the `TOOLS = [...]` block and before the helper functions section. Place them in a new section:

```python
# =============================================================================
# MCP CLIENT — Optional external tool integrations (Gmail, Supabase, etc.)
# =============================================================================

_mcp_processes = {}  # server_name -> subprocess.Popen
_mcp_request_id = 0


def _init_mcp_servers():
    """Start enabled MCP servers as subprocesses. Called once at agent startup."""
    import subprocess
    for name, cfg in CONFIG.get("mcp_servers", {}).items():
        if not cfg.get("enabled"):
            continue
        env = {**os.environ, **cfg.get("env", {})}
        try:
            proc = subprocess.Popen(
                cfg["command"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            _mcp_processes[name] = proc
            print(f"MCP server '{name}' started (pid={proc.pid})")
        except FileNotFoundError:
            print(f"MCP server '{name}' failed to start — command not found: {cfg['command'][0]}")
        except Exception as e:
            print(f"MCP server '{name}' failed to start — {e}")


def _mcp_request(server_name, method, params=None):
    """Send a JSON-RPC request to an MCP server and return the result."""
    global _mcp_request_id
    proc = _mcp_processes.get(server_name)
    if not proc or proc.poll() is not None:
        return {"error": f"MCP server '{server_name}' is not running"}

    _mcp_request_id += 1
    request = {
        "jsonrpc": "2.0",
        "id": _mcp_request_id,
        "method": method,
        "params": params or {},
    }
    try:
        request_line = json.dumps(request) + "\n"
        proc.stdin.write(request_line.encode())
        proc.stdin.flush()
        response_line = proc.stdout.readline().decode()
        return json.loads(response_line)
    except Exception as e:
        return {"error": f"MCP communication error: {e}"}


def _discover_mcp_tools(server_name):
    """Query an MCP server for its available tools. Returns list of tool definitions."""
    result = _mcp_request(server_name, "tools/list")
    if "error" in result:
        return []
    return result.get("result", {}).get("tools", [])


def _call_mcp_tool(server_name, tool_name, args):
    """Execute a tool call on an MCP server. Returns result string."""
    result = _mcp_request(server_name, "tools/call", {
        "name": tool_name,
        "arguments": args,
    })
    if "error" in result:
        return f"Error: MCP tool call failed — {result['error']}"
    content = result.get("result", {}).get("content", [])
    if content and isinstance(content, list):
        return "\n".join(c.get("text", str(c)) for c in content)
    return str(result.get("result", ""))


def _shutdown_mcp_servers():
    """Gracefully terminate all running MCP server subprocesses."""
    for name, proc in _mcp_processes.items():
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
    _mcp_processes.clear()
```

- [ ] **Step 2: Modify execute_tool to include MCP fallback**

Find the existing `execute_tool` function and add MCP fallback after the local tool lookup:

```python
def execute_tool(name, args):
    tools = {
        "wiki_read": lambda a: wiki_read(a["article_path"]),
        "mastersheet_read": lambda a: mastersheet_read(a["query"]),
        "wiki_write": lambda a: wiki_write(a["filename"], a["content"]),
        "create_pdf": lambda a: _create_pdf(a["title"], a["content"], a["filename"], a.get("preview", False)),
        "create_docx": lambda a: _create_docx(a["title"], a["content"], a["filename"], a.get("preview", False)),
        "create_xlsx": lambda a: _create_xlsx(a["title"], a["content"], a["filename"]),
        "krs_lookup": lambda a: krs_lookup(a["krs_number"]),
        "exa_search": lambda a: exa_search(a["query"]),
    }
    fn = tools.get(name)
    if fn:
        try:
            return fn(args)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"

    # MCP fallback — check if any enabled MCP server provides this tool
    for server_name, proc in _mcp_processes.items():
        if proc.poll() is None:
            return _call_mcp_tool(server_name, name, args)

    return f"Error: unknown tool '{name}'."
```

- [ ] **Step 3: Add MCP init call to server startup**

In the `--serve` CLI block (around line 2839), add `_init_mcp_servers()` after `_init_client_state()`:

```python
    elif len(sys.argv) > 1 and sys.argv[1] == "--serve":
        import uvicorn
        _load_sessions()
        _init_client_state()
        _init_mcp_servers()  # Start enabled MCP servers
        app = create_api()
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        print(f"CS Agent API — http://0.0.0.0:{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
```

- [ ] **Step 4: Verify MCP code loads without errors (servers disabled)**

```bash
cd cs-agent && python -c "
from agent import _init_mcp_servers, _mcp_processes, _shutdown_mcp_servers
_init_mcp_servers()
print('MCP processes (should be empty):', dict(_mcp_processes))
_shutdown_mcp_servers()
print('MCP shutdown OK')
"
```

Expected: Empty dict (no servers enabled), no errors.

---

## Task 9: Create README.md

**Files:**
- Create: `README.md` (project root)

- [ ] **Step 1: Write README.md**

Write a comprehensive English README to the project root (`C:\Users\dogkn\Desktop\CS AGENT\README.md`). Structure:

```markdown
# CS Agent

> Self-hosted customer success AI agent for accounting firms operating in Poland. Built with OpenAI-compatible function calling, wiki-based knowledge management, and MCP-ready architecture.

## Features

- **8 Built-in Tools** — Wiki read/write, client mastersheet lookup, web search (Exa), KRS company registry, PDF/DOCX/XLSX document generation
- **Wiki-Based Knowledge** — 24 SOP articles covering onboarding, tax, payroll, immigration, and operations. No vector database needed — the LLM selects relevant articles from an index.
- **Human-in-the-Loop Tiers** — Tier 1 (autonomous), Tier 2 (requires approval), Tier 3 (escalate to human)
- **Admin Dashboard** — Real-time monitoring with query stats, latency tracking, error rates, and SLA compliance
- **MCP-Ready** — Pre-configured integration points for Gmail and Supabase via Model Context Protocol
- **Docker-Ready** — Single-command deployment with docker-compose
- **Multilingual Output** — Agent responds in Turkish, Polish, or English based on context

## Quick Start

### Prerequisites

- Python 3.12+
- OpenRouter API key ([get one here](https://openrouter.ai))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cs-agent.git
   cd cs-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r cs-agent/requirements.txt
   ```

3. Configure environment:
   ```bash
   cp cs-agent/.env.example cs-agent/.env
   # Edit .env with your API keys
   ```

4. Run the agent:
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
docker-compose build
docker-compose up -d

# Test
docker-compose exec agent python agent.py "Hello"
```

## Architecture

```
User query -> classify_query (intent) -> classify_tier (1/2/3)
           -> build_messages(system_prompt + wiki_index + history)
           -> model_call (LLM via OpenRouter)
           -> tool calls loop (max 10 per turn)
           -> grounding_check -> final response + trace log
```

Single-file harness design: all logic lives in `agent.py` (~2800 lines). No framework, no separate modules. Configuration in `config.py`.

### Tools

| Tool | Purpose |
|------|---------|
| `wiki_read` | Read SOP articles from internal knowledge base |
| `wiki_write` | Create or update wiki articles with version history |
| `mastersheet_read` | Query client database by company name, NIP, type, or accountant |
| `exa_search` | Web search via Exa API for current regulations |
| `krs_lookup` | Polish company registry (KRS) lookup |
| `create_pdf` | Generate branded PDF documents |
| `create_docx` | Generate DOCX documents |
| `create_xlsx` | Generate Excel spreadsheets |

## Configuration

See `.env.example` for all available options. Key settings:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | LLM API key |
| `EXA_API_KEY` | Yes | Web search API key |
| `API_BASE` | No | Override API endpoint (default: OpenRouter) |
| `MODEL` | No | Override model (default: claude-sonnet-4-6-20250217) |

## MCP Integration (Optional)

The agent supports optional MCP (Model Context Protocol) server integrations. Currently pre-configured for:

- **Gmail** — Email reading, drafting, and sending
- **Supabase** — Database operations (can replace CSV mastersheet)

See [docs/mcp-setup.md](docs/mcp-setup.md) for setup instructions.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Main agent endpoint |
| `/feedback` | POST | Submit feedback on responses |
| `/health` | GET | Health check |
| `/files/{filename}` | GET | Download generated documents |
| `/admin/dashboard` | GET | Monitoring dashboard (HTML) |
| `/admin/stats` | GET | Query statistics |
| `/admin/report` | GET | Weekly report |
| `/admin/deadlines` | GET | Upcoming tax deadlines |
| `/admin/silent` | GET | Inactive clients |
| `/admin/gaps` | GET | SOP coverage gaps |
| `/admin/alerts` | GET | Recent errors/alerts |

## CLI Modes

```bash
python agent.py                    # Interactive REPL
python agent.py "query"            # Single query
python agent.py --serve [port]     # HTTP API server (default: 8000)
python agent.py --stats            # Tier distribution from traces
python agent.py --report           # Weekly summary report
python agent.py --deadlines [days] # Upcoming tax deadlines
python agent.py --silent [days]    # Inactive clients
python agent.py --gaps             # SOP coverage gaps
python agent.py --trends [days]    # Trace trend analysis
python agent.py --promotions       # Tier promotion candidates
python agent.py --optimize         # Daily optimization run
```

## Benchmarks

12 Q&A pairs covering procedure, routing, deadline, customer, and constraint scenarios:

```bash
python cs-agent/run_benchmark.py
```

Uses LLM-as-judge evaluation with a separate model to reduce bias.

## License

MIT
```

Write this to `C:\Users\dogkn\Desktop\CS AGENT\README.md`.

---

## Task 10: Create docs/mcp-setup.md

**Files:**
- Create: `C:\Users\dogkn\Desktop\CS AGENT\docs\mcp-setup.md`

- [ ] **Step 1: Write MCP setup guide**

```markdown
# MCP Integration Setup

The CS Agent supports optional [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server integrations. MCP servers run as subprocesses and expose their tools to the agent via JSON-RPC over stdio.

## Prerequisites

- Node.js 18+ and npx (for running MCP servers)
- The MCP server packages are downloaded automatically via npx on first run

## Gmail Integration

### Setup

1. Add to your `.env`:
   ```
   MCP_GMAIL_ENABLED=true
   ```

2. On first run, the Gmail MCP server will prompt for OAuth authentication in your browser.

3. Start the agent with `--serve` or in REPL mode — the Gmail MCP server starts automatically.

### Available Tools

When enabled, the Gmail MCP server provides tools for:
- Searching emails
- Reading email content
- Creating drafts
- Sending emails
- Managing labels

### Use Cases

- Automated deadline reminder emails to clients
- Reading incoming client emails for context
- Drafting response emails based on wiki SOPs

## Supabase Integration

### Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)

2. Add to your `.env`:
   ```
   MCP_SUPABASE_ENABLED=true
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   ```

3. Start the agent — the Supabase MCP server connects automatically.

### Available Tools

When enabled, the Supabase MCP server provides tools for:
- Querying database tables
- Inserting/updating records
- Running SQL queries
- Managing database schema

### Use Cases

- Replace CSV mastersheet with a Supabase table for real-time multi-user access
- Store session data and trace logs in a database
- Build dashboards with live data queries

## Architecture

```
Agent (agent.py)
  |
  |-- execute_tool("wiki_read", args)  --> Local tool (direct function call)
  |-- execute_tool("gmail_send", args) --> MCP fallback
        |
        +-- _call_mcp_tool("gmail", "gmail_send", args)
              |
              +-- JSON-RPC over stdio --> Gmail MCP Server (subprocess)
```

MCP servers are started as child processes when the agent launches (if enabled). The agent sends JSON-RPC requests over stdin/stdout. If a tool name is not found in the local tool registry, the agent falls back to checking running MCP servers.

## Troubleshooting

- **"command not found: npx"** — Install Node.js 18+
- **MCP server fails to start** — Check stderr output in the agent logs
- **Tool calls return errors** — Verify your API keys and permissions in `.env`
- **Gmail OAuth fails** — Ensure your browser can open for the OAuth flow
```

Write this to `C:\Users\dogkn\Desktop\CS AGENT\docs\mcp-setup.md`.

---

## Task 11: PII Scan and Final Verification

**Files:**
- Scan: All tracked files in the project

- [ ] **Step 1: Scan agent.py for hardcoded PII**

```bash
cd "C:/Users/dogkn/Desktop/CS AGENT"
# Search for real NIP patterns (10-digit numbers that could be NIP)
grep -n "5833\|5892\|6762\|AKTAŞ\|BACAK\|DOGAN\|BELEK\|Mine Food\|Aldona\|Agsay\|Aliyze\|Desbuild\|HEWELIUSZA" cs-agent/agent.py
```

Expected: No matches (these are real client data patterns from the original mastersheet).

- [ ] **Step 2: Scan all Python files for API keys**

```bash
grep -rn "sk-\|eyJ\|OPENROUTER_API_KEY=" cs-agent/*.py
```

Expected: No real API key values (only references to env vars).

- [ ] **Step 3: Scan .env.example for real values**

```bash
cat cs-agent/.env.example | grep -v "^#" | grep -v "^$" | grep -v "your_\|false\|https://your"
```

Expected: No output (all values should be placeholders).

- [ ] **Step 4: Verify .gitignore catches sensitive files**

```bash
# Create a test .env to verify .gitignore works
echo "TEST=1" > cs-agent/.env
cd cs-agent && git status --short 2>/dev/null | grep ".env"
# Should NOT show .env (it's gitignored)
rm cs-agent/.env
```

- [ ] **Step 5: Full agent import test**

```bash
cd cs-agent && python -c "
from agent import agent_loop, SYSTEM_PROMPT, TOOLS, execute_tool
from config import CONFIG

# Verify English
assert 'Error' in execute_tool('wiki_read', {'article_path': 'nonexistent.md'})
assert 'Hata' not in execute_tool('wiki_read', {'article_path': 'nonexistent.md'})

# Verify tools count
assert len(TOOLS) == 8

# Verify MCP config present
assert 'mcp_servers' in CONFIG
assert 'gmail' in CONFIG['mcp_servers']
assert 'supabase' in CONFIG['mcp_servers']

# Verify mastersheet sample data
result = execute_tool('mastersheet_read', {'query': 'say'})
assert '10' in result

print('All checks passed.')
"
```

Expected: "All checks passed."

---

## Task 12: Expert Simulation Gate

**No code changes.** This is the final review step before commit.

- [ ] **Step 1: Run 3-Expert AI Engineer Feedback Simulation**

Simulate evaluation from three expert perspectives (Karpathy, Ng, LeCun) focused on **GitHub showcase readiness**:

Evaluation criteria:
- PII zero-tolerance — no real client data in tracked files
- Code quality — English comments, clean structure, single-file discipline
- Documentation — README completeness, MCP setup guide clarity
- Security — .gitignore coverage, no hardcoded secrets
- Extensibility — MCP integration points, config-driven architecture
- Docker-readiness — Dockerfile and docker-compose work

Each expert provides: score (0-100%), critical findings, go/no-go decision.

- [ ] **Step 2: Address any blockers found by experts**

If any expert finds a blocker, fix it and re-run verification.

- [ ] **Step 3: Final go/no-go decision**

All 3 experts must give **go** before proceeding to commit.
