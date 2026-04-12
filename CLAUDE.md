# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CS Agent** -- Self-hosted customer success agent for a Poland-based accounting firm. Qwen 3.6 Plus via OpenRouter API. Compact system prompt (behavioral rules) + wiki articles (domain knowledge).

**Language:** Turkish (code comments, wiki, user-facing text). English for accounting/legal team communication.

**Current State (2026-04-09):** Phase 0-3 complete, Phase 4 partial. 2,648 lines agent.py, 8 tools, 10 CLI modes, 13 API endpoints, 24 wiki articles, 142 firms, 100 benchmarks, chat UI, Docker ready. Overall production-readiness: ~%73.

## Key Source Files

- `kaynak_system_prompt.md` — Original 15-section system prompt to be decomposed
- `genel_plan.md` — Full project plan (Faz 0a → Faz 1 → Faz 2)
- `docs/master_architecture.md` — Birlesik mimari vizyonu (Karpathy + Ng + LeCun). Phase 0-5 roadmap, kontrol listesi, modul oncelikleri. Tum faz gecislerinde bu dokumanin kontrol listesi referans alinir.
- `docs/task_list.md` — Master architecture'in basit ve etkili uygulama plani. Oncelik sirali task listesi.

## Development Commands

```bash
# Run agent (CLI single query)
python cs-agent/agent.py "ZUS beyanı nasıl yapılır?"

# Run agent (REPL mode)
python cs-agent/agent.py

# Run benchmarks
python cs-agent/run_benchmark.py

# Docker
docker-compose build
docker-compose up -d
docker-compose exec agent python agent.py "query here"
docker-compose exec agent python run_benchmark.py
```

## Architecture

Single-file harness (`agent.py`) with OpenAI-compatible function calling:

```
User query → classify_query (intent) → classify_tier (1/2/3)
           → build_messages(system_prompt + wiki_index + history)
           → model_call (Qwen 3.6 via OpenRouter)
           → tool calls loop (max 10 per turn)
           → grounding_check → final response + trace log
```

**8 Tools (current):**
- `wiki_read(article_path)` — SOP document retrieval, truncates at 2500*4 chars, flags `draft/`
- `wiki_write(filename, content)` — SOP document creation/update
- `mastersheet_read(query)` — client lookup by company name or NIP (fuzzy matching)
- `exa_search(query)` — web search via Exa API
- `krs_lookup(krs_number)` — Polish company registry lookup
- `_create_pdf(title, content)` — branded PDF generation (orange theme)
- `_create_docx(title, content)` — DOCX generation with branding
- `_create_xlsx(title, content)` — XLSX generation

**9 CLI Modes:** `--serve`, `--stats`, `--report`, `--deadlines`, `--silent`, `--gaps`, `--promotions`, `--optimize`, interactive REPL

**11 API Endpoints:** `/chat`, `/feedback`, `/health`, `/`, `/favicon.ico`, `/files/{filename}`, `/admin/stats`, `/admin/report`, `/admin/deadlines`, `/admin/silent`, `/admin/gaps`

**No wiki_search tool** — INDEX.md is injected into system prompt; the LLM decides which article to read.

## Design Constraints (Mandatory)

1. **Single-file harness** — ALL logic in `agent.py`. No separate modules. Refactor threshold: 2,500 lines.
2. **Tools = pure I/O** — No LLM calls inside tools, no business logic, no chaining tools.
3. **Errors = strings, not exceptions** — Tools return error strings so the agent can explain to users.
4. **NIP float conversion** — Mastersheet stores NIP as float. Always use `str(int(float(x)))`.
5. **[KAYNAK:] tag** — Agent must cite sources in every response (wiki article, genel bilgi, or draft).
6. **Config in config.py** — API settings, paths, limits in a single CONFIG dict.
7. **Simplicity principle** — Extend existing infrastructure, don't build new systems. (Karpathy)

## Security & GDPR Requirements (Mandatory — Pre-Production)

> Ng: "Bir muhasebe firmasının müşteri verileri GDPR altında. Güvenlik 'nice to have' değil, 'must have'."

1. **PII masking in traces** — NIP, firma adı, kişisel veriler trace loglarında maskelenmeli. `NIP: 676***841` formatı.
2. **HTTPS zorunlu** — Production'da reverse proxy (nginx/caddy) ile TLS. Localhost:8000 yalnızca dev.
3. **Rate limiting** — `/chat` endpoint'ine IP bazlı rate limit (ör: 30 req/min). Free tier API kotası koruması.
4. **Session encryption** — Session verileri disk'e yazılırken şifrelenmeli (T3 ile birlikte).
5. **RODO/GDPR uyumu** — Polonya UODO standartları. Veri saklama süresi, silme hakkı, erişim log'u.
6. **API key rotation** — .env'deki anahtarlar periyodik rotate edilmeli.
7. **Input sanitization** — User query'lerinde injection önleme (prompt injection, path traversal).

## Production Readiness Gates

Her faz geçişinde bu kontrol listesi referans alınır:

| Gate | Durum | Blocker? |
|------|-------|----------|
| GDPR/PII maskeleme | ✅ | **mask_pii + _mask_trace_fields** |
| HTTPS/TLS | ❌ | **EVET — production öncesi zorunlu** |
| Rate limiting | ✅ | **slowapi IP bazlı** |
| Error handling (500→mesaj) | ✅ | _friendly_error + try/except |
| Session persistence | ✅ | _save_session + _load_sessions |
| Monitoring dashboard | ✅ | /admin/dashboard HTML |
| Alerting (hata artışı) | ❌ | Hayır ama önerilir |
| Benchmark ≥100 soru | ✅ | 100 soru, 5 tip, difficulty alanı |
| Regression test diff | ✅ | --diff + --strict + baseline |

## Expert Assessment Summary (2026-04-08)

Üç AI uzmanı simülasyonu sonuçları (referans: conversation log):

| Uzman | Perspektif | Skor | En Kritik Bulgu |
|-------|-----------|------|-----------------|
| Karpathy | Harness & Tools | %67 → %80 | Trace reasoning eklendi, dashboard ve regression aktif |
| Ng | Deployment & Ops | %52 → %82 | PII, rate limit, session, monitoring, alerting, GDPR doc |
| LeCun | World Model | %22 → %45 | Client state 142 firma, proaktif deadline, alert pattern |
| **Ağırlıklı Toplam** | | **%73** | Production threshold (%75) yakininda |

**Katman olgunlukları:** Core %85, Wiki %75, UI %80, Tools %65, Eval %80, DevOps %70, Güvenlik %65, World Model %45

## Wiki Structure

Articles are decomposed from `kaynak_system_prompt.md` sections:

| Section | → Wiki Article |
|---------|---------------|
| Bölüm 4 | `onboarding/checklist.md` + `onboarding/vekaletname_seti.md` |
| Bölüm 5.1-5.2 | `operasyon/aylik_dongu.md` |
| Bölüm 5.3 | `bordro/aylik_akis.md` |
| Bölüm 5.4 | `operasyon/belge_toplama.md` |
| Bölüm 6 | `vergi/beyanname_takvimi.md` |
| Bölüm 7 | `operasyon/sla_yanitsureleri.md` |
| Bölüm 8 | `iletisim/kanallar.md` |
| Bölüm 9 | `sozlesme/genel_kurallar.md` |
| Bölüm 11 | `referans/mastersheet_yapisi.md` |
| Bölüm 12 | `referans/yasal_terimler.md` |

Sections 1, 2, 3, 10, 14 stay in SYSTEM_PROMPT string inside `agent.py`.

Wiki article format:
```markdown
# [Title]
_Kaynak: System prompt Bölüm X | Son güncelleme: 2026-04-05_
## Özet
## İçerik
## İlişkili Makaleler
```

## Implementation Steps

Follow these 7 steps **sequentially**. Complete each step, show results, then proceed.

### Adım 1: Proje İskeleti

Create directory structure under `cs-agent/`:

```
cs-agent/
├── agent.py               ← Single-file harness
├── config.py              ← Configuration
├── run_benchmark.py       ← Benchmark runner
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── wiki/
│   ├── INDEX.md
│   ├── onboarding/
│   ├── bordro/
│   ├── vergi/
│   ├── operasyon/
│   ├── sozlesme/
│   ├── iletisim/
│   ├── referans/
│   └── draft/
├── mastersheet/
├── outputs/
├── traces/
└── benchmarks/
    └── qa_pairs.json
```

**config.py:**
```python
import os

CONFIG = {
    "api_base": "https://openrouter.ai/api/v1",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "qwen/qwen3.6-plus-preview:free",
    "temperature": 0.2,
    "max_tokens": 4096,

    "wiki_dir": "./wiki",
    "index_file": "./wiki/INDEX.md",
    "mastersheet_file": "./mastersheet/clients.csv",

    "output_dir": "./outputs",
    "trace_dir": "./traces",

    "max_tool_calls_per_turn": 5,
    "max_wiki_article_tokens": 3000,
    "wiki_truncate_at": 2500,
    "max_history_messages": 10,
}
```

**requirements.txt:**
```
openai>=1.0
fastapi
uvicorn
```

**Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent.py config.py run_benchmark.py ./
EXPOSE 8000
CMD ["python", "agent.py"]
```

**docker-compose.yml:**
```yaml
version: "3.8"
services:
  agent:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./wiki:/app/wiki:ro
      - ./mastersheet:/app/mastersheet:ro
      - ./outputs:/app/outputs
      - ./traces:/app/traces
      - ./benchmarks:/app/benchmarks
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    restart: unless-stopped
```

### Adım 2: System Prompt Ayrıştırma

Read `kaynak_system_prompt.md`. Split 15 sections into two groups:

**Stays in SYSTEM_PROMPT (agent.py):** Bölüm 1 (behavior rules, approval mechanism, "Ne Anladığını Yaz" format), Bölüm 2 (org structure, routing matrix), Bölüm 3 (service scope), Bölüm 10 (message draft rules), Bölüm 14 (constraints).

Append self-check rule to system prompt:
```
SELF-CHECK KURALI:
Her yanıtın sonunda kaynak belirt:
- Wiki'den bilgi kullandıysan → [KAYNAK: makale_adı.md]
- Wiki'de bulamadığın bilgi için → [KAYNAK: genel bilgi]
- draft/ kaynağı kullandıysan → [KAYNAK: draft/makale_adı.md — doğrulanmamış]
- Bilmiyorsan → "Bu konuda kesin bilgi veremiyorum"
Kaynak gösteremediğin bilgiyi yanıta ekleme.
```

**Becomes wiki articles:** See Wiki Structure table above. Bölüm 15 is parked for Faz 2.

**INDEX.md** — single file listing all articles with one-line descriptions per category (Onboarding, Bordro, Vergi, Operasyon, Sözleşme, İletişim, Referans).

Run linting: check date/term consistency across articles.

### Adım 3: Tools

Two tools in `agent.py` using OpenAI function calling format:

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "wiki_read",
            "description": "Wiki makalesinin içeriğini okur. INDEX.md'deki listeden makale yolunu seç.",
            "parameters": {
                "type": "object",
                "properties": {
                    "article_path": {
                        "type": "string",
                        "description": "Makale yolu, örn: onboarding/checklist.md"
                    }
                },
                "required": ["article_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mastersheet_read",
            "description": "Mastersheet'ten müşteri bilgisi sorgular. Firma adı veya NIP ile arama.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Firma adı veya NIP numarası"
                    }
                },
                "required": ["query"]
            }
        }
    }
]
```

**Implementations:**

```python
def wiki_read(article_path: str) -> str:
    full_path = f"{CONFIG['wiki_dir']}/{article_path}"
    if not os.path.exists(full_path):
        return f"Hata: '{article_path}' bulunamadı."
    content = read_file(full_path)
    if len(content) > CONFIG["wiki_truncate_at"] * 4:
        content = content[:CONFIG["wiki_truncate_at"] * 4] + "\n\n... [kırpıldı]"
    if "draft/" in article_path:
        return "[⚠ DOĞRULANMAMIŞ KAYNAK]\n\n" + content
    return content

def mastersheet_read(query: str) -> str:
    import csv
    results = []
    with open(CONFIG["mastersheet_file"], "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nip = safe_nip(row.get("NIP/PESEL", ""))
            company = row.get("Company Name", "")
            if query.lower() in company.lower() or query in nip:
                results.append(format_client_row(row))
    if not results:
        return f"'{query}' ile eşleşen firma bulunamadı."
    return "\n---\n".join(results[:5])

def safe_nip(raw):
    """NIP float→int dönüşümü. Mastersheet'te NIP float olarak saklanıyor."""
    try:
        return str(int(float(raw)))
    except (ValueError, TypeError):
        return str(raw).strip()

def format_client_row(row):
    nip = safe_nip(row.get("NIP/PESEL", ""))
    return (
        f"Firma: {row.get('Company Name', '?')}\n"
        f"NIP: {nip}\n"
        f"Tür: {row.get('TYP', '?')}\n"
        f"Muhasebeci: {row.get('RA', '?')}\n"
        f"VAT: {row.get('VAT Aktiflik Tarihi', '?')}\n"
        f"Vergi Dairesi: {row.get('US', '?')}\n"
        f"Mikrorachunek: {row.get('Mikrorachunek', '?')}"
    )

def execute_tool(name, args):
    tools = {
        "wiki_read": lambda a: wiki_read(a["article_path"]),
        "mastersheet_read": lambda a: mastersheet_read(a["query"]),
    }
    fn = tools.get(name)
    if not fn:
        return f"Hata: '{name}' tanınmayan tool."
    try:
        return fn(args)
    except Exception as e:
        return f"Hata: {str(e)}"
```

### Adım 4: Agent Loop

```python
import json, os, time
from datetime import datetime
from openai import OpenAI
from config import CONFIG

def agent_loop(user_message: str, session: dict) -> str:
    """think → call → observe → respond → trace"""
    start = time.time()

    session["messages"].append({"role": "user", "content": user_message})
    messages = build_messages(session)

    tool_calls_log = []
    tool_call_count = 0

    while tool_call_count < CONFIG["max_tool_calls_per_turn"]:
        response = model_call(messages, tools=TOOLS)

        if response.tool_calls:
            for tc in response.tool_calls:
                tool_call_count += 1
                args = json.loads(tc.function.arguments)
                result = execute_tool(tc.function.name, args)
                tool_calls_log.append({"name": tc.function.name, "args": args})

                messages.append({"role": "assistant", "content": None, "tool_calls": [tc]})
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            continue

        final = response.content
        session["messages"].append({"role": "assistant", "content": final})

        save_trace({
            "timestamp": datetime.now().isoformat(),
            "query": user_message,
            "tool_calls": tool_calls_log,
            "duration_ms": int((time.time() - start) * 1000),
        })
        return final

    return "⚠ Çok fazla adım gerekti. Lütfen soruyu daha spesifik sorun."


def model_call(messages, tools=None):
    client = OpenAI(api_key=CONFIG["api_key"], base_url=CONFIG["api_base"])
    return client.chat.completions.create(
        model=CONFIG["model"],
        messages=messages,
        tools=tools,
        temperature=CONFIG["temperature"],
        max_tokens=CONFIG["max_tokens"],
    ).choices[0].message


def build_messages(session):
    index_content = read_file(CONFIG["index_file"])
    system = SYSTEM_PROMPT + f"\n\n[WİKİ İNDEKSİ — Hangi makaleyi okuman gerektiğine bu listeye bakarak karar ver]\n{index_content}"
    messages = [{"role": "system", "content": system}]
    messages.extend(session["messages"][-CONFIG["max_history_messages"]:])
    return messages


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_trace(trace):
    os.makedirs(CONFIG["trace_dir"], exist_ok=True)
    filepath = f"{CONFIG['trace_dir']}/{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    with open(filepath, "a") as f:
        f.write(json.dumps(trace, ensure_ascii=False) + "\n")
```

SYSTEM_PROMPT is the string built in Adım 2 from sections 1, 2, 3, 10, 14.

### Adım 5: CLI

Append to `agent.py`:

```python
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        session = {"messages": []}
        print(agent_loop(query, session))
    else:
        print("CS Agent v1 — Cikmak icin 'q' yazin")
        session = {"messages": []}
        while True:
            try:
                query = input("\n> ")
            except (EOFError, KeyboardInterrupt):
                break
            if query.lower() in ("exit", "quit", "q"):
                break
            print(agent_loop(query, session))
```

**Manual test scenarios (run all 10):**

| # | Query | Expected |
|---|-------|----------|
| 1 | "ZUS beyanı nasıl yapılır?" | wiki_read → procedure + [KAYNAK:] |
| 2 | "PKN Orlen NIP?" | mastersheet_read → "7740001454" |
| 3 | "Bordro hesaplaması hakkında bilgi lazım" | Route to Gosia |
| 4 | "Yeni müşteri onboarding checklist" | wiki_read → checklist |
| 5 | "Kasım VAT beyanname tarihi?" | wiki_read → "Her ayın 25'i" |
| 6 | "Müşteriye hatırlatma mesajı yaz" | Draft message → ask approval |
| 7 | "Wiki'de olmayan bir konu" | [KAYNAK: genel bilgi] or "bilgi yok" |
| 8 | "Sözleşme iptal talebi" | Route to Kaan Bey + standard response |
| 9 | "Vergi tavsiyesi ver" | Refuse |
| 10 | "Varolmayan makale oku" | Handle error |

### Adım 6: Benchmark

Create `benchmarks/qa_pairs.json` with 12 Q&A pairs covering: procedure (onboard-001, onboard-002, edge-001, sla-001), routing (routing-001 through routing-003), deadline (deadline-001, deadline-002), customer (customer-001), constraint (constraint-001, constraint-002).

**run_benchmark.py** — loads qa_pairs.json, runs each through agent_loop with fresh session, uses LLM-as-judge to compare response vs expected answer, outputs pass/fail per question and final baseline score. Saves results to `benchmarks/results_YYYYMMDD.json`.

```python
"""Benchmark runner: Q&A çiftlerini agent'a sor, LLM-as-judge ile değerlendir."""
import json
from datetime import datetime
from agent import agent_loop, model_call
from config import CONFIG

def run():
    with open("benchmarks/qa_pairs.json") as f:
        pairs = json.load(f)

    results = []
    for pair in pairs:
        session = {"messages": []}
        response = agent_loop(pair["question"], session)

        judgment = judge(pair["question"], pair["expected_answer"], response)
        results.append({
            "id": pair["id"],
            "type": pair["type"],
            "correct": judgment["correct"],
            "reasoning": judgment["reasoning"],
        })
        print(f"  {pair['id']}: {'✓' if judgment['correct'] else '✗'}")

    correct = sum(1 for r in results if r["correct"])
    total = len(results)
    print(f"\nBaseline: {correct}/{total} ({correct/total:.0%})")

    with open(f"benchmarks/results_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def judge(question, expected, actual):
    prompt = f"""Soru: {question}
Beklenen cevap: {expected}
Agent'ın cevabı: {actual}

Agent'ın cevabı beklenen cevapla örtüşüyor mu?
Sadece JSON döndür: {{"correct": true/false, "reasoning": "kısa açıklama"}}"""

    response = model_call(
        [{"role": "user", "content": prompt}],
        tools=None
    )
    try:
        return json.loads(response.content.strip().replace("```json", "").replace("```", ""))
    except:
        return {"correct": False, "reasoning": "Parse hatası"}

if __name__ == "__main__":
    run()
```

### Adım 7: Docker Test

```bash
docker-compose build
docker-compose up -d
docker-compose exec agent python agent.py "ZUS beyanı nasıl yapılır?"
docker-compose exec agent python run_benchmark.py
```

## Routing Rules (Quick Reference)

| Topic | Route to |
|-------|----------|
| Bordro (payroll) | Gosia |
| Muhasebe (accounting) | Kasia / Liudmila |
| Hukuk (legal) / şirket kuruluşu | Jakub |
| Strateji / sözleşme iptal | Kaan Bey |
| Vergi tavsiyesi | REFUSE — redirect to professional advisor |
| Fiyat bilgisi | REFUSE — management will contact |
