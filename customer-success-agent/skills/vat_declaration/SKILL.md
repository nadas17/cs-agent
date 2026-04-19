---
name: vat_declaration
description: VAT (KDV / Podatek od towarów i usług) monthly declaration and JPK_V7 submission process. Covers the 25th-of-month filing deadline, registration threshold (PLN 240,000 from 2026), standard rates (23/8/5/0%), and role routing for JPK_V7 preparation. Use when the user asks about VAT, JPK, tax returns, becoming an active VAT payer, or VAT-R form.
---

# VAT Declaration (JPK_V7)

## Adımlar

1. **Verify VAT status** via `mastersheet_read` — check the **VAT Aktiflik Tarihi** column. If the firm is not yet registered, route the user to the VAT registration flow (`wiki/vergi/vat_kaydi_rehberi.md`) instead of filing.

2. **Monthly deadline: 25th of each month** — form is JPK_V7M (monthly filer, default) or JPK_V7K (quarterly, rare). Same weekend/holiday extension rule applies.

3. **Rates to verify against invoices when the user asks "which rate applies":**
   - **23%** — standard (most goods and services)
   - **8%** — some food, accommodation, construction
   - **5%** — basic foodstuffs, books, newspapers
   - **0%** — EU intra-community + international shipments (conditional on evidence)

4. **Registration threshold (from 1 January 2026):** annual turnover **PLN 240,000** (raised from PLN 200,000). **Foreign (non-Polish) firms** must register from the first taxable transaction regardless of turnover.

5. **Route JPK_V7 preparation to the assigned accountant** (check mastersheet **RA** column): Head Accountant or Accountant. Do not answer the user with a calculation; confirm who is responsible.

6. **Escalation scenarios:**
   - VAT application refusal, appeal — **General Manager** + **Lawyer**
   - Exemption eligibility question — **General Manager** (do NOT give tax advice yourself)
   - Late filing penalty — **General Manager**

7. **When drafting a client message** about VAT status change: always state both the Polish and Turkish term in the first mention ("KDV kaydı / rejestracja VAT").

## İlişkili Wiki
- [vergi/vat_kaydi_rehberi.md](../../wiki/vergi/vat_kaydi_rehberi.md) — VAT kayıt rehberi
- [vergi/beyanname_takvimi.md](../../wiki/vergi/beyanname_takvimi.md) — beyanname takvimi
- [vergi/efatura_ksef.md](../../wiki/vergi/efatura_ksef.md) — KSeF e-fatura entegrasyonu
- [vergi/vat_kaydi_belgeler.md](../../wiki/vergi/vat_kaydi_belgeler.md) — VAT kayıt belgeleri
