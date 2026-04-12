# Customer Success AI Agent — Architecture Report

_Self-hosted, domain-compiled, tool-augmented LLM agent for accounting firm operations_

---

## 1. Executive Summary

A single-harness AI agent that transforms reactive customer support into proactive client management. Unlike generic chatbots, this agent operates on **compiled domain knowledge** (not RAG), maintains a **persistent client world model**, and follows a **tiered autonomy framework** where it handles routine queries autonomously while escalating complex decisions to humans.

```
                    WHAT IT IS                          WHAT IT IS NOT
            ┌─────────────────────┐            ┌─────────────────────────┐
            │ Domain-specific     │            │ Generic chatbot         │
            │ Compiled knowledge  │            │ Vector search / RAG     │
            │ Tool-augmented      │            │ Standalone LLM          │
            │ Tiered autonomy     │            │ Fully autonomous        │
            │ Self-monitoring     │            │ Black box               │
            │ GDPR-aware          │            │ Unregulated             │
            └─────────────────────┘            └─────────────────────────┘
```

**Key Metrics:**
- 2,827 lines single-file harness | 51 functions | 8 tools
- 100 benchmark questions | 92% accuracy | regression testing
- 142 active client profiles | persistent world model
- 13 API endpoints | 12 CLI modes | real-time dashboard
- PII masking | rate limiting | HTTPS-ready | GDPR documented

---

## 2. System Architecture

### 2.1 High-Level Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                                                                  │
│   ┌──────────┐    ┌──────────┐    ┌───────────┐                 │
│   │ Chat UI  │    │ CLI/REPL │    │ REST API  │                 │
│   │ (Web)    │    │ (Ops)    │    │ (Integr.) │                 │
│   └────┬─────┘    └────┬─────┘    └─────┬─────┘                 │
│        │               │                │                        │
│        └───────────────┼────────────────┘                        │
│                        │                                         │
│                        v                                         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   AGENT HARNESS                          │   │
│   │                                                          │   │
│   │  ┌──────────┐  ┌───────────┐  ┌──────────────────────┐  │   │
│   │  │ Input    │  │ Intent    │  │ Tier Classification  │  │   │
│   │  │ Sanitize │→ │ Classify  │→ │                      │  │   │
│   │  │ (S4)     │  │ (5 types) │  │ T1: Autonomous       │  │   │
│   │  └──────────┘  └───────────┘  │ T2: Human-Approved   │  │   │
│   │                               │ T3: Human-Only       │  │   │
│   │                               └──────────┬───────────┘  │   │
│   │                                          │               │   │
│   │                                          v               │   │
│   │  ┌──────────────────────────────────────────────────┐   │   │
│   │  │              LLM INFERENCE LOOP                   │   │
│   │  │                                                   │   │
│   │  │  System Prompt ──→ Model Call ──→ Tool Router     │   │
│   │  │       +                  │            │           │   │
│   │  │  Wiki Index              │        ┌───┴───┐       │   │
│   │  │       +                  │        │ Tools │       │   │
│   │  │  History                 │        │ (x8)  │       │   │
│   │  │                         │        └───┬───┘       │   │
│   │  │                         │            │           │   │
│   │  │               ┌─────────v────────────v──┐        │   │
│   │  │               │   Grounding Check       │        │   │
│   │  │               │   Source Attribution     │        │   │
│   │  │               └────────────┬────────────┘        │   │
│   │  └────────────────────────────┼─────────────────────┘   │   │
│   │                               │                          │   │
│   │                               v                          │   │
│   │  ┌──────────────────────────────────────────────────┐   │   │
│   │  │            OBSERVABILITY LAYER                    │   │
│   │  │                                                   │   │
│   │  │  PII Mask ──→ Trace Log ──→ Alert Check           │   │
│   │  │                  │              │                  │   │
│   │  │           Client State     Dashboard              │   │
│   │  │            Update          /Alerts                 │   │
│   │  └──────────────────────────────────────────────────┘   │   │
│   └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Compiled Knowledge Architecture

```
┌─────────────────────────────────────────────────────┐
│              KNOWLEDGE LAYER                         │
│                                                      │
│  ┌─────────────┐     ┌──────────────────────────┐   │
│  │ SYSTEM      │     │ WIKI (24 articles)        │   │
│  │ PROMPT      │     │                           │   │
│  │             │     │  onboarding/  (2)         │   │
│  │ - Behavior  │     │  bordro/      (1)         │   │
│  │ - Org chart │     │  vergi/       (6)         │   │
│  │ - Routing   │     │  operasyon/   (6)         │   │
│  │ - Scope     │     │  goc/         (4)         │   │
│  │ - Format    │     │  sozlesme/    (1)         │   │
│  └──────┬──────┘     │  iletisim/    (1)         │   │
│         │            │  referans/    (2)         │   │
│         │            │  draft/       (staging)   │   │
│         │            └──────────┬───────────────┘   │
│         │                       │                    │
│         v                       v                    │
│  ┌──────────────────────────────────────────────┐   │
│  │         INDEX.md (Article Router)             │   │
│  │                                               │   │
│  │  Injected into system prompt at runtime.      │   │
│  │  LLM reads index → selects article →          │   │
│  │  calls wiki_read(path)                        │   │
│  │                                               │   │
│  │  No vector DB. No embeddings. No RAG.         │   │
│  │  Pure compiled context + LLM selection.        │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  WHY: 150 clients, ~25 topic clusters.               │
│  At this scale, compiled .md > vector search.        │
│  Faster, cheaper, more deterministic, auditable.     │
└─────────────────────────────────────────────────────┘
```

### 2.3 Tool Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      TOOL REGISTRY                            │
│                                                               │
│  ┌─────────── READ TOOLS ────────────┐  ┌── WRITE TOOLS ──┐ │
│  │                                    │  │                  │ │
│  │  wiki_read       SOP lookup        │  │  wiki_write      │ │
│  │  mastersheet_read Client search    │  │  create_pdf      │ │
│  │  krs_lookup       Registry API     │  │  create_docx     │ │
│  │  exa_search       Web search       │  │  create_xlsx     │ │
│  │                                    │  │                  │ │
│  │  → Tier 1 (Autonomous)            │  │  → Tier 2        │ │
│  │  → No side effects                │  │  → Human review  │ │
│  └────────────────────────────────────┘  └──────────────────┘ │
│                                                               │
│  DESIGN PRINCIPLES:                                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 1. Pure I/O — no LLM calls inside tools                 │ │
│  │ 2. Errors = strings — agent explains to user             │ │
│  │ 3. No tool chaining — each tool is independent           │ │
│  │ 4. Path traversal protection — realpath validation        │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Tiered Autonomy Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    HUMAN-IN-THE-LOOP TIERS                       │
│                                                                  │
│   TIER 1: AUTONOMOUS                                             │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ Info queries, status checks, SOP lookup, client search     │ │
│   │ → Agent responds directly. No human approval needed.       │ │
│   │ → ~70% of all queries                                      │ │
│   └───────────────────────────────────────────────────────────┘ │
│                           │                                      │
│   TIER 2: HUMAN-APPROVED                                         │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ Document generation, wiki updates, message drafts          │ │
│   │ → Agent creates, human reviews before sending/publishing.  │ │
│   │ → ~20% of all queries                                      │ │
│   └───────────────────────────────────────────────────────────┘ │
│                           │                                      │
│   TIER 3: HUMAN-ONLY                                             │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ Complaints, legal matters, pricing, tax advice             │ │
│   │ → Agent routes to correct team member. Does not respond.   │ │
│   │ → ~10% of all queries                                      │ │
│   └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│   PROMOTION PATH:                                                │
│   ┌──────────┐    data accumulates    ┌──────────┐              │
│   │  Tier 2  │ ─────────────────────→ │  Tier 1  │              │
│   │ (Manual) │    90%+ success rate   │  (Auto)  │              │
│   └──────────┘    10+ operations      └──────────┘              │
│                                                                  │
│   → Promotion is SUGGESTED, never automatic.                     │
│   → Human always makes the final decision.                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. World Model & Proactive Intelligence

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT WORLD MODEL                           │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  CLIENT STATE (JSON)                      │   │
│   │                                                           │   │
│   │  For each of 142 clients:                                 │   │
│   │  ┌─────────────────────────────────────────────────────┐ │   │
│   │  │ company       │ "Acme Corp Sp. z o.o."              │ │   │
│   │  │ type          │ "SP" / "JDG"                        │ │   │
│   │  │ last_contact  │ "2026-04-09T14:30:00"               │ │   │
│   │  │ total_queries │ 12                                   │ │   │
│   │  │ last_topic    │ "VAT"                                │ │   │
│   │  │ risk_flags    │ []                                   │ │   │
│   │  └─────────────────────────────────────────────────────┘ │   │
│   │                                                           │   │
│   │  Updated automatically after every query.                 │   │
│   │  Persisted to disk. Survives server restart.              │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                              v                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              PROACTIVE ACTION ENGINE                      │   │
│   │                                                           │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│   │  │  Deadline    │  │  Silent     │  │  Alert          │  │   │
│   │  │  Reminder    │  │  Client     │  │  System         │  │   │
│   │  │             │  │  Detection  │  │                 │  │   │
│   │  │ --remind    │  │ --silent    │  │ _check_alerts   │  │   │
│   │  │             │  │ --action    │  │                 │  │   │
│   │  │ Filters by  │  │ 30d: soft  │  │ 4 conditions:   │  │   │
│   │  │ firm type   │  │ 60d: firm  │  │ - error spike   │  │   │
│   │  │ (JDG/SP)    │  │ 90d: churn │  │ - high latency  │  │   │
│   │  │             │  │   alert    │  │ - tool failure   │  │   │
│   │  │ Generates   │  │            │  │ - grounding     │  │   │
│   │  │ per-client  │  │ Generates  │  │   degradation   │  │   │
│   │  │ reminders   │  │ check-in   │  │                 │  │   │
│   │  │ (drafts)    │  │ drafts     │  │ Logs to         │  │   │
│   │  │             │  │            │  │ alerts.jsonl    │  │   │
│   │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│   │                                                           │   │
│   │  ALL drafts require human approval. No auto-send.         │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Security & Compliance Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   SECURITY LAYERS                                │
│                                                                  │
│  LAYER 1: PERIMETER                                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Caddy Reverse Proxy                                        │  │
│  │ ├── Automatic HTTPS (Let's Encrypt)                        │  │
│  │ ├── X-Content-Type-Options: nosniff                        │  │
│  │ ├── X-Frame-Options: DENY                                  │  │
│  │ └── Agent port NOT exposed externally                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  LAYER 2: APPLICATION                                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Rate Limiting (slowapi)                                    │  │
│  │ ├── /chat:  30 req/min per IP                              │  │
│  │ ├── /admin: 10 req/min per IP                              │  │
│  │ └── 429 → localized error message                          │  │
│  │                                                            │  │
│  │ Input Sanitization                                         │  │
│  │ ├── Max query: 2,000 chars                                 │  │
│  │ ├── Path traversal: realpath validation                    │  │
│  │ └── Empty message rejection                                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  LAYER 3: DATA PROTECTION                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ PII Masking (mask_pii)                                     │  │
│  │ ├── Tax ID:    1234567890  →  123***890                    │  │
│  │ ├── PESEL:     92071314567 →  92*******67                  │  │
│  │ └── IBAN:      PL61...874  →  PL*****...****               │  │
│  │                                                            │  │
│  │ Applied at: trace logs, feedback, admin API responses       │  │
│  │ NOT applied at: LLM calls (full data needed for accuracy)  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  LAYER 4: DATA LIFECYCLE                                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Session: 24h auto-archive │ Traces: 90d purge             │  │
│  │ Wiki: versioned backups   │ GDPR: documented policy        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Observability & Self-Improvement

```
┌─────────────────────────────────────────────────────────────────┐
│                OBSERVABILITY PIPELINE                             │
│                                                                  │
│  Every query produces a TRACE record:                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ {                                                          │  │
│  │   timestamp, query (PII-masked),                           │  │
│  │   query_type, tier, tier_reason,                           │  │
│  │   tool_calls, tool_reasoning,                              │  │
│  │   wiki_articles_used, routing_decision,                    │  │
│  │   self_check_result, grounding_result,                     │  │
│  │   error_category, duration_ms                              │  │
│  │ }                                                          │  │
│  └────────────────────────┬──────────────────────────────────┘  │
│                           │                                      │
│              ┌────────────┼────────────┐                         │
│              v            v            v                          │
│  ┌──────────────┐ ┌────────────┐ ┌──────────────┐               │
│  │  Dashboard   │ │  Alerting  │ │  Trends      │               │
│  │              │ │            │ │              │               │
│  │ /admin/      │ │ 4 auto     │ │ --trends     │               │
│  │  dashboard   │ │ conditions │ │              │               │
│  │              │ │            │ │ Daily volume │               │
│  │ Queries/24h  │ │ Error      │ │ Topic dist.  │               │
│  │ Avg latency  │ │ spike      │ │ Tool usage   │               │
│  │ Error rate   │ │ Latency    │ │ Anomaly      │               │
│  │ Tier dist.   │ │ Tool fail  │ │ detection    │               │
│  │ Wiki usage   │ │ Grounding  │ │              │               │
│  │              │ │ decay      │ │              │               │
│  │ Auto-refresh │ │            │ │              │               │
│  │ 30 seconds   │ │ /admin/    │ │              │               │
│  └──────────────┘ │  alerts    │ └──────────────┘               │
│                   └────────────┘                                 │
│                                                                  │
│  SELF-IMPROVEMENT LOOP:                                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  Feedback ──→ QA Generation ──→ Benchmark ──→ Hill-Climb   │  │
│  │  (user)       (auto)            (100 Q&A)    (subprocess)  │  │
│  │                                     │                      │  │
│  │                              ┌──────┴──────┐               │  │
│  │                              │  Regression │               │  │
│  │                              │  --diff     │               │  │
│  │                              │  --strict   │               │  │
│  │                              └─────────────┘               │  │
│  │                                                            │  │
│  │  Score improves → keep change                              │  │
│  │  Score drops    → auto-rollback                            │  │
│  │  Max 3 iterations/day (safety limit)                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Production Scenarios — What Can This Agent Do?

### Scenario 1: Instant Knowledge Access

```
  USER                          AGENT                         TOOLS
   │                              │                              │
   │  "What documents are         │                              │
   │   needed for VAT             │                              │
   │   registration?"             │                              │
   │ ────────────────────────→    │                              │
   │                              │  classify: procedure, T1     │
   │                              │  select: vergi/vat_kaydi     │
   │                              │ ─────────────────────────→   │
   │                              │                   wiki_read  │
   │                              │ ←─────────────────────────   │
   │                              │  grounding_check: passed     │
   │  Complete answer with        │                              │
   │  source attribution          │                              │
   │ ←────────────────────────    │                              │
   │  [SOURCE: vat_kaydi.md]      │                              │
   │                              │                              │
   │  Total time: 2-4 seconds     │                              │
```

**Value:** Support team doesn't need to search SOPs manually. Agent finds the right document, extracts the answer, and cites its source. 24/7 availability.

---

### Scenario 2: Client Lookup & Document Generation

```
  USER                          AGENT                         TOOLS
   │                              │                              │
   │  "Pull info on client        │                              │
   │   #5252678381 and            │                              │
   │   create a PDF report"       │                              │
   │ ────────────────────────→    │                              │
   │                              │  classify: customer, T2      │
   │                              │ ─────────────────────────→   │
   │                              │              mastersheet_read │
   │                              │ ←─────────────────────────   │
   │                              │ ─────────────────────────→   │
   │                              │                  create_pdf  │
   │                              │ ←─────────────────────────   │
   │  "Report generated:          │                              │
   │   client_report.pdf"         │                              │
   │ ←────────────────────────    │                              │
   │                              │                              │
   │  Download: /files/report.pdf │  Branded PDF with            │
   │                              │  Key: Value formatting       │
```

**Value:** Client info retrieval + branded document creation in a single interaction. No copy-paste between systems.

---

### Scenario 3: Smart Routing

```
  USER                          AGENT                     TEAM MEMBER
   │                              │                              │
   │  "Client asking about        │                              │
   │   payroll calculation"        │                              │
   │ ────────────────────────→    │                              │
   │                              │  classify: routing, T1       │
   │                              │  routing_map → Payroll Spec. │
   │  "Route to Payroll           │                              │
   │   Specialist. She handles    │                              │
   │   ZUS filings and salary     │                              │
   │   calculations."             │                              │
   │ ←────────────────────────    │                              │
   │                              │                              │

   OUT OF SCOPE queries (tax advice, pricing, legal):
   │  "Client wants tax advice"   │                              │
   │ ────────────────────────→    │                              │
   │                              │  classify: constraint, T3    │
   │  "This is outside our        │                              │
   │   scope. Please refer to     │                              │
   │   a licensed tax advisor."   │                              │
   │ ←────────────────────────    │                              │
```

**Value:** Consistent routing decisions based on organizational matrix. Constraint enforcement prevents scope creep.

---

### Scenario 4: Proactive Deadline Management

```
  OPERATIONS TEAM                AGENT                    OUTPUT
   │                              │                          │
   │  python agent.py --remind 5  │                          │
   │ ────────────────────────→    │                          │
   │                              │  Scan upcoming deadlines │
   │                              │  Filter by firm type:    │
   │                              │  ├── JDG → specific set  │
   │                              │  └── SP  → different set │
   │                              │                          │
   │                              │  Generate per-client     │
   │                              │  reminder drafts         │
   │                              │ ────────────────────→    │
   │                              │            outputs/      │
   │  "47 reminders generated     │            reminders/    │
   │   for 3 deadlines.           │            2026-04-15/   │
   │   Review before sending."    │                          │
   │ ←────────────────────────    │                          │
   │                              │                          │
   │  NO auto-send.               │                          │
   │  Human reviews + sends.      │                          │
```

**Value:** Instead of manually checking which clients need reminders for which deadlines, the agent generates personalized drafts filtered by firm type. Human reviews and sends.

---

### Scenario 5: Silent Client Detection & Re-engagement

```
  OPERATIONS TEAM                AGENT                    MANAGEMENT
   │                              │                          │
   │  --silent 30 --action        │                          │
   │ ────────────────────────→    │                          │
   │                              │  Scan client_state.json  │
   │                              │  Find: 12 silent clients │
   │                              │                          │
   │                              │  Classify by severity:   │
   │                              │  ├── 30d (8) → soft msg  │
   │                              │  ├── 60d (3) → firm msg  │
   │                              │  └── 90d (1) → ALERT ──→ │
   │                              │                          │
   │  Check-in drafts generated   │            Churn risk    │
   │  with tone-appropriate       │            notification  │
   │  messages per client         │            for review    │
   │ ←────────────────────────    │                          │
```

**Value:** Prevents client churn by detecting silence patterns. Escalates high-risk cases to management automatically.

---

### Scenario 6: Self-Monitoring & Quality Assurance

```
  ┌──────────────────────────────────────────────────────────┐
  │                  CONTINUOUS QUALITY LOOP                   │
  │                                                           │
  │   ┌─────────┐    ┌──────────┐    ┌───────────────────┐   │
  │   │ Users   │    │ Feedback │    │ Benchmark         │   │
  │   │ interact│───→│ with     │───→│ 100 Q&A pairs     │   │
  │   │ via chat│    │ context  │    │ + regression test  │   │
  │   └─────────┘    └──────────┘    └─────────┬─────────┘   │
  │                                            │              │
  │                                            v              │
  │   ┌──────────────┐    ┌───────────────────────────────┐  │
  │   │  Dashboard   │    │  Hill-Climb Optimization       │  │
  │   │              │    │                                │  │
  │   │  Real-time   │    │  Meta-agent suggests prompt    │  │
  │   │  metrics:    │    │  improvements. Subprocess      │  │
  │   │              │    │  runs benchmark. Auto-rollback │  │
  │   │  - Queries   │    │  if score drops.               │  │
  │   │  - Latency   │    │                                │  │
  │   │  - Errors    │    │  Max 3/day safety limit.       │  │
  │   │  - Alerts    │    │                                │  │
  │   └──────────────┘    └───────────────────────────────┘  │
  │                                                           │
  │   The agent monitors itself and improves its own          │
  │   system prompt based on measured performance.            │
  └──────────────────────────────────────────────────────────┘
```

**Value:** The system doesn't just serve queries — it measures its own performance, detects degradation, and iteratively improves.

---

## 8. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    DOCKER HOST                           │    │
│  │                                                          │    │
│  │   :443 ┌──────────┐        ┌──────────────────────┐     │    │
│  │ ──────→│  Caddy   │───────→│  Agent Container     │     │    │
│  │   :80  │  (HTTPS) │ :8000  │                      │     │    │
│  │        │  TLS     │        │  Python 3.12-slim    │     │    │
│  │        │  Headers │        │  FastAPI + Uvicorn   │     │    │
│  │        └──────────┘        │                      │     │    │
│  │                            │  Volumes:            │     │    │
│  │                            │  ├── wiki/ (RO)      │     │    │
│  │                            │  ├── mastersheet/    │     │    │
│  │                            │  │   (RO)            │     │    │
│  │                            │  ├── outputs/ (RW)   │     │    │
│  │                            │  └── traces/ (RW)    │     │    │
│  │                            └──────────────────────┘     │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  EXTERNAL DEPENDENCIES:                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LLM Provider (OpenRouter / Direct API)  ←── API Key     │   │
│  │  Web Search API                          ←── API Key     │   │
│  │  Company Registry API                    ←── Public      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ZERO external databases. ZERO cloud storage.                    │
│  All state is local files (JSON, CSV, JSONL).                    │
│  Fully self-contained. Air-gappable.                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Capability Matrix

| Capability | Status | How It Works |
|-----------|--------|-------------|
| Knowledge Q&A | Production | 24 compiled articles + LLM selection |
| Client Lookup | Production | CSV fuzzy search by name/tax ID |
| Document Generation | Production | Branded PDF/DOCX/XLSX with field formatting |
| Smart Routing | Production | Organization matrix + 6 routing targets |
| Scope Enforcement | Production | Constraint classification + refusal patterns |
| Deadline Reminders | Production | Tax calendar + firm type filtering + draft generation |
| Silent Client Detection | Production | World model state + tiered re-engagement |
| Real-time Monitoring | Production | Dashboard + 4-condition alerting |
| Self-Improvement | Beta | Hill-climb optimization + regression testing |
| Trend Analysis | Beta | Daily/weekly aggregation + anomaly detection |
| Session Persistence | Production | Disk-backed + auto-archive + restart survival |
| PII Protection | Production | NIP/PESEL/IBAN masking in all logs |
| Web Search | Production | External API integration for current information |
| Registry Lookup | Production | National company registry API |

---

## 10. Technical Stack Summary

```
┌─────────────────────────────────────────────────────────────┐
│  Language    │  Python 3.12                                  │
│  LLM        │  OpenAI-compatible API (model-agnostic)       │
│  Framework  │  FastAPI + Uvicorn                             │
│  Frontend   │  Vanilla HTML/CSS/JS (no framework)           │
│  Documents  │  fpdf2, python-docx, openpyxl                 │
│  Security   │  slowapi (rate limit), Caddy (TLS)            │
│  Storage    │  Local files (JSON, CSV, JSONL, Markdown)     │
│  Container  │  Docker + Docker Compose                      │
│  Eval       │  LLM-as-judge + deterministic checks          │
│  LOC        │  2,827 (agent) + 655 (benchmark) + 56 (conf)  │
└─────────────────────────────────────────────────────────────┘

  Design philosophy: "Extend existing infrastructure,
  don't build new systems." — Single-file harness,
  compiled knowledge, local storage, no external DB.
```

---

_This architecture serves 150 clients with 8 tools, 100 benchmark questions, and a self-improving feedback loop — all in a single deployable container with zero external database dependencies._
