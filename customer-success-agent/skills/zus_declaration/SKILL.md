---
name: zus_declaration
description: ZUS (Polish social security) monthly declaration process. Determines the correct filing deadline based on firm headcount category (7th, 10th, or 15th of each month), handles employee lifecycle events (ZUA/ZZA/ZWUA within 7 days), and routes payroll queries to the Payroll Specialist role. Use when the user asks about ZUS filings, deadlines, DRA/RCA forms, A1 certificates, or ZUS PEL authorization.
---

# ZUS Declaration

## Adımlar

1. **Identify the firm's ZUS filing category** (use mastersheet_read to find the firm; employee count typically inferred from TYP and context):
   - **JDG, no employees** → deadline: **10th of each month**
   - **Small firms (≤ 9 employees)** → deadline: **7th of each month**
   - **Medium/large firms (10+ employees)** → deadline: **15th of each month**

2. **Weekend/holiday rule:** if the deadline falls on a weekend or an official Polish holiday, it automatically extends to the next business day. State this explicitly in the answer so the user does not assume a hard date.

3. **Employee lifecycle events (all within 7 days of the event):**
   - **New hire** — **ZUA** (full ZUS coverage: retirement, health, accident) or **ZZA** (health insurance only, e.g. board members without employment contract)
   - **Termination** — **ZWUA**
   - **Monthly aggregate** — **DRA** (firm-level) + **RCA** (per-employee breakdown)

4. **ZUS PEL authorization:** mandatory if the firm has employees. Collected during onboarding (see `new_client_onboarding` skill). If missing, filing cannot be submitted electronically.

5. **Routing for domain questions:**
   - Payroll calculation, gross-to-net, A1 certificates, ZUS form questions → **Payroll Specialist** (English communication)
   - Missing ZUS PEL or vekâletname → **Document Specialist**
   - Penalties, audit response, disputes → **General Manager**

6. **Firm-specific ZUS account:** check the mastersheet **ZUS Account** column for the unique sub-account number when drafting payment references.

## İlişkili Wiki
- [vergi/beyanname_takvimi.md](../../wiki/vergi/beyanname_takvimi.md) — tüm beyanname tarihleri
- [bordro/aylik_akis.md](../../wiki/bordro/aylik_akis.md) — aylık bordro döngüsü
- [referans/mastersheet_yapisi.md](../../wiki/referans/mastersheet_yapisi.md) — ZUS Account kolon referansı
