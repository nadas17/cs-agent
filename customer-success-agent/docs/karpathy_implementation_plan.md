# Karpathy Implementation Plan — CS Agent

_Oluşturma: 2026-04-18 | Hedef model: Claude Sonnet 4.6 | Toplam efor: ~7 gün, 12 task_

---

## 🎯 Genel İlkeler (Karpathy Felsefesi Özeti)

Her task bu dört ilkeden en az birine hizmet eder:

1. **Thin tools, fat skills** — Tool'lar saf I/O, karar verme ve iş mantığı skill'lerde.
2. **Information architecture > prompt quality** — Reliability context scope'undan gelir, daha iyi prompt yazmaktan değil.
3. **Eval-driven development** — Ölçülmeyen iyileştirme yoktur. Baseline → değişiklik → yeniden ölçüm.
4. **Progressive disclosure** — System prompt'ta sadece index; LLM ihtiyaca göre derinlik yükler.

## 🏗️ Karar Çerçevesi (Onaylanan)

| Karar | Değer | Gerekçe |
|-------|-------|---------|
| LLM modeli | **Claude Sonnet 4.6** | Tool calling güvenilirliği, TR/PL desteği, AB GDPR uyumu |
| API path | **Direkt Anthropic API** (fallback: OpenRouter) | Markup yok, telemetry net, EU bölgesi kolay |
| Skill sistemi | **B2 — CS Agent içi runtime** | Tek sistem, karmaşıklık yok |
| Prompt caching | **Faz 2'de aktif** | Maliyet ~%70 düşer |
| Refactor (monolitik bölme) | **Ertelenir** | 2972 satır hâlâ yönetilebilir |
| Autonomy slider full | **Ertelenir** | Mevcut onay mekanizması minimal slider |

---

## 📅 Faz-by-Faz Plan

### ⚡ FAZ 0 — Model Migration (~0.5 gün)

Claude Sonnet 4.6'ya geçiş + smoke test.

#### T0.1 — Model konfigürasyonu
- **Amaç:** `config.py`'de model `anthropic/claude-sonnet-4.6` olsun; Anthropic direkt endpoint kullanılsın.
- **Hedef dosya:** `config.py`
- **Acceptance:**
  - `CONFIG["model"] == "claude-sonnet-4.6"`
  - `CONFIG["api_base"] == "https://api.anthropic.com"`
  - `.env`'de `ANTHROPIC_API_KEY` tanımlı
- **Rollback:** Tek satır — önceki model string'ine geri dön.

#### T0.2 — API client detection
- **Amaç:** `agent.py`'deki model_call fonksiyonu Anthropic SDK'yı kullansın (halihazırda auto-detect var; sağlamlaştır).
- **Hedef:** `agent.py` içinde `_get_client()` veya benzeri
- **Acceptance:**
  - `claude-*` prefix → Anthropic SDK
  - `qwen-*` / `gpt-*` → OpenAI-compat SDK
  - Fallback env var: `FORCE_OPENROUTER=true`
- **Rollback:** Env var ile OpenRouter fallback.

#### T0.3 — CLAUDE.md güncelle
- **Amaç:** Dokümantasyon tutarlılığı.
- **Değişiklik:** "Qwen 3.6 Plus via OpenRouter" → "Claude Sonnet 4.6 via Anthropic API"
- **Acceptance:** `grep -i "qwen"` CLAUDE.md'de model referansı kalmamalı (tarihsel not dışında).

#### T0.4 — Smoke test
- **Amaç:** Regresyon yok olduğunu doğrula.
- **Prosedür:** 10 mevcut benchmark sorusunu çalıştır, cevap formatı ve `[KAYNAK:]` etiketi var mı kontrol et.
- **Acceptance:** 10/10 cevap üretildi, 9/10 `[KAYNAK:]` içeriyor.
- **Rollback:** Model kararı geri al.

---

### 🔧 FAZ 1 — Thin Tools + Skills (~5 gün)

Karpathy'nin "thin harness, fat skills" ilkesinin gövdesi.

#### T1.1 — `mastersheet_read` thin'leştir
- **Amaç:** Fuzzy matching + top-5 limit'i tool'dan çıkar; LLM ham satır seçsin.
- **Mevcut:** `mastersheet_read()` agent.py:506 civarı — query içi lower-match, `results[:5]` kesim.
- **Yeni davranış:** Tool parametresi `{query, limit?}` — default limit 20, format yalın JSON listesi.
- **Acceptance:**
  - 3 benchmark sorusunda LLM hangi satırı seçtiğini açıklayabilmeli
  - Top-5 kesim kaldırıldı
  - Fuzzy logic azaltıldı (sadece exact + contains)
- **Rollback:** Git revert.

#### T1.2 — `wiki_read` thin'leştir
- **Amaç:** Truncation (2500*4) ve draft warning logic'ini kaldır.
- **Mevcut:** `wiki_read()` agent.py:491 — truncate + draft flag ekliyor.
- **Yeni davranış:** Sadece dosya oku; draft/ path kontrolü LLM'de.
- **Acceptance:**
  - `wiki_read` <30 satır
  - Truncation yok; uzun makaleler için **system prompt'a token budget uyarısı eklenir**
- **Rollback:** Git revert.

#### T1.3 — Tool error format uniform
- **Amaç:** Tüm tool'lar `{"error": str, "code": str}` ya da başarı değeri döndürsün.
- **Acceptance:**
  - `execute_tool` dispatch dönüşü tek standart
  - LLM kullanıcıya hata açıklarken `code` field'ına bakabilsin

#### T2.1 — `skills/` dizin + 3 başlangıç skill
- **Amaç:** Wiki makalelerini SKILL formatına genişletmek.
- **Dosyalar:**
  - `skills/new_client_onboarding/SKILL.md`
  - `skills/zus_declaration/SKILL.md`
  - `skills/vat_declaration/SKILL.md`
- **Frontmatter:** `name`, `description`, opsiyonel `allowed-tools`
- **İçerik:** Mevcut `wiki/onboarding/checklist.md`, `wiki/vergi/*` içeriğinden türet.
- **Acceptance:**
  - 3 skill'in description'ı 80-150 token arası
  - Her skill <5000 kelime
  - Her skill'de `# Adımlar` ve `# İlişkili Wiki` bölümleri

#### T2.2 — `skill_loader.py`
- **Amaç:** Skill'leri yükle + YAML frontmatter parse et.
- **Hedef:** ~50 satır yeni dosya. **Tek işlev:**
  - `list_skills()` → tüm skill'lerin `{name, description, path}` listesi
  - `load_skill(name)` → YAML frontmatter dışındaki markdown içeriği döner
- **Acceptance:** Pytest olmadan manual test: 3 skill listelenir, `load_skill("zus_declaration")` body döner.
- **Rollback:** Dosyayı sil, `skill_registry` entegrasyonu geri al.

#### T2.3 — Skill registry'yi system prompt'a inject
- **Amaç:** Progressive disclosure. System prompt'a INDEX.md gibi skill listesi eklensin (sadece name+description).
- **Hedef:** `build_messages()` içinde.
- **Acceptance:**
  - `messages[0]["content"]` içinde `[SKILLS]` bölümü var
  - Her skill için satır: `- skill_name: one-line description`
  - Toplam skill index <500 token

#### T2.4 — `load_skill(name)` tool ekle
- **Amaç:** LLM bir skill seçip body'sini yüklesin.
- **Hedef:** `TOOLS` listesine yeni entry, `execute_tool` dispatch'ine case.
- **Acceptance:**
  - 1 benchmark sorusunda LLM `load_skill` çağırır
  - Tool sonucu `[SKILL: zus_declaration]` prefix ile döner
  - `wiki_read` pattern'ine birebir benzer kod

---

### 📊 FAZ 2 — Eval + Observability (~2 gün)

March of Nines için minimum metric seti + prompt caching.

#### T4.1 — Token telemetry
- **Amaç:** Her trace'e token sayıları yaz.
- **Yeni trace alanları:** `prompt_tokens`, `completion_tokens`, `tool_result_tokens`, `cache_read_tokens` (Sonnet 4.6 prompt caching ile birlikte).
- **Kaynak:** Anthropic response'unda `usage` objesi built-in.
- **Acceptance:** 10 query trace'inde 4 alan da dolu, `total_tokens` hesaplanabiliyor.

#### T4.2 — P95 latency + tool accuracy benchmark
- **Amaç:** `run_benchmark.py` çıktısına iki metric daha ekle.
- **Acceptance:**
  - Her query_type için P95 latency raporlanır (simple <1s, complex <4s hedefi)
  - Her soru için `tool_call_accuracy` (beklenen tool çağrıldı mı) judge sonucuna dahil

#### T4.3 — Prompt caching aktif
- **Amaç:** System prompt + INDEX.md + skill registry'yi cache'le.
- **Hedef:** Anthropic API çağrısında `cache_control: {"type": "ephemeral"}` ekle.
- **Acceptance:**
  - Trace'te `cache_read_tokens > 0` (ikinci çağrıdan itibaren)
  - Maliyet simülasyonu: 100 query → önceki vs cache'li karşılaştırması
  - Hedef: %50+ input token maliyet düşüşü
- **Rollback:** `cache_control` parametresini kaldır.

#### T5.1 — Context adherence judge
- **Amaç:** Hallucination rate ölçümü.
- **Hedef:** `run_benchmark.py` içindeki `judge()` fonksiyonuna 2. soru.
- **Judge prompt'a eklenecek:**
  ```
  Ek kontrol: Agent'ın cevabı sadece wiki/skill'den gelen bilgiye mi dayanıyor,
  yoksa dış bilgi kullanmış mı? {"grounded": true/false, "extra_claims": [...]}
  ```
- **Acceptance:**
  - Her benchmark sonucunda `grounded` alanı bulunur
  - Özet: `grounding_rate = grounded_count / total` raporlanır

---

### 🧭 FAZ 3 — Routing Refinement (~1 gün)

Explicit matrix'i silme, **genişlet**.

#### T6.1 — Few-shot örnekler ekle
- **Amaç:** Mevcut routing matrix'in ÜSTÜNE 3-4 few-shot örnek ekle.
- **Hedef:** `SYSTEM_PROMPT` içinde routing matrix'in altına:
  ```
  Örnekler:
  - "Kasım bordro hesabı ne zaman?" → Payroll Specialist (bordro)
  - "Vekaletname hangi belgelerde gerekli?" → Lawyer (hukuk)
  - "Sözleşme iptal etmek istiyorum" → General Manager (strateji)
  - "Vergi kesinti oranları?" → REFUSE (vergi tavsiyesi)
  ```
- **Acceptance:**
  - System prompt sadece +~200 token büyür
  - 5 routing-specific benchmark'ta 5/5 doğru route

#### T6.2 — Routing trace alanı
- **Amaç:** Hangi routing kararı alındığı trace'e yazılsın.
- **Hedef:** `save_trace()` parametresine `routing_decision` ekle — LLM yanıtından regex ile route adı çıkar.
- **Acceptance:** 10 query trace'inde route adı doğru (manual check).

---

## 📊 Bağımlılık Grafiği

```
Faz 0 (T0.1-T0.4) → bağımsız, önce yapılır
    ↓
Faz 1:
  T1.1, T1.2, T1.3 → paralel (thin tools)
  T2.1 → T2.2 → T2.3 → T2.4 (sıralı, skills)

Faz 2:
  T4.1 → T4.2 → T4.3 (sıralı)
  T5.1 → paralel Faz 2 içinde

Faz 3:
  T6.1 → T6.2 (sıralı)
```

**Paralellik fırsatları:**
- Faz 1'de T1.1-T1.3 aynı gün yapılabilir
- T2.1 (skill yazımı) T1'lerle paralel yürüyebilir
- Faz 2'de T5.1 ayrı iş parçası

---

## 🎯 Sprint Breakdown (~7 gün)

| Gün | Faz | Task'lar |
|-----|-----|----------|
| **G1 (AM)** | Faz 0 | T0.1 + T0.2 + T0.3 + T0.4 |
| **G1 (PM)** | Faz 1 | T1.1 + T1.2 + T1.3 (thin tools) |
| **G2** | Faz 1 | T2.1 (3 skill yaz) |
| **G3** | Faz 1 | T2.2 + T2.3 (loader + registry) |
| **G4** | Faz 1 | T2.4 (tool entegrasyon) + regression test |
| **G5** | Faz 2 | T4.1 + T4.2 (token + latency telemetry) |
| **G6** | Faz 2 | T4.3 + T5.1 (caching + adherence) |
| **G7** | Faz 3 | T6.1 + T6.2 + final benchmark |

---

## ⚠️ Risk Matrisi

| Risk | İhtimal | Etki | Azaltma |
|------|---------|------|---------|
| Maliyet patlaması (cache çalışmazsa) | Orta | Yüksek | Rate limit sıkı, prompt caching öncelik |
| Thin tool sonrası LLM yanlış row seçer | Düşük | Orta | Benchmark T1 sonrası çalıştır; regresyon varsa geri al |
| Skill loader INDEX.md ile çakışır | Düşük | Düşük | İki index ayrı bölümde `[WIKI]` ve `[SKILLS]` |
| Anthropic API rate limit (EU bölge) | Düşük | Orta | Fallback: OpenRouter'a otomatik geçiş env var ile |
| Türkçe kalite regression (Qwen → Claude) | Çok düşük | Yüksek | T0.4 smoke test kaçırmayacak; en fazla prompt tweak gerek |

---

## 🛑 Rollback Noktaları

- **Faz 0 sonunda:** Model kararı geri alınabilir, tek satır config.
- **Faz 1 sonunda:** Thin tools + skills commit'leri git revert edilebilir; sistem eski haline döner.
- **Faz 2 sonunda:** Trace field'ları ek, zararsız — rollback pratik ihtiyaç yok.
- **Faz 3 sonunda:** Few-shot örnekler kaldırılabilir, matrix saf haliyle kalır.

---

## 📏 Başarı Ölçütü (Plan sonunda)

| Metrik | Şu anki | Hedef |
|--------|---------|-------|
| Benchmark pass rate | ~%73 (tahmin) | **≥%85** |
| P95 latency (simple queries) | bilinmiyor | **<1.5s** |
| P95 latency (complex) | bilinmiyor | **<5s** |
| Tool call accuracy | bilinmiyor | **≥%85** |
| Grounding rate | bilinmiyor | **≥%95** |
| Token cost per query (median) | bilinmiyor | **<$0.01** (caching ile) |
| Skill sistemi | yok | **3 skill çalışır** |
| Trace telemetry completeness | %60 | **%95** |

Baseline Faz 0 T0.4 smoke test sonrasında dondurulur; sonuç bu dokümana "Baseline Log" bölümü olarak eklenir.

---

## 📊 Baseline Log (2026-04-18, Faz 0 sonrası)

**Test kapsamı:** İlk 20 soru qa_pairs.json (5 onboarding + 10 routing + 5 deadline). 0 error, 290 saniye toplam.

| Metrik | Değer | Hedef | Gap |
|--------|-------|-------|-----|
| Gerçek başarı oranı (manual re-score) | **~80%** (16/20) | ≥85% | -5pp |
| Heuristic match ≥30% | 45% (9/20) | - | heuristic zayıf |
| Source coverage `[SOURCE:]` | 75% (15/20) | ≥95% | **-20pp** |
| Ortalama latency | 14.5s | - | - |
| P95 latency | **35.4s** | <5s complex | **-30s** ❌ |
| Tool call discipline | **Zayıf** (test 2: mastersheet çağırmadı, hallucination) | ≥85% | kritik |
| Routing disambiguation | 7/10 direct, 3 clarify-first | - | clarify aşırı |
| Error rate | 0/20 | 0 | ✓ |

**Kategori bazında:**
- **Onboarding (5 soru):** 4-5/5 ✓ (doc-list match mükemmel, source var)
- **Routing (10 soru):** 7/10 ✓ (routing-003/005/006/007: agent clarification-first davranıyor, direkt route etmiyor)
- **Deadline (5 soru):** 5/5 ✓ (doğru tarihler, source var, ama latency >15s)

**Kritik bulgular:**
1. **Sonnet 4.6 domain uyumu güçlü** — Türkçe + muhasebe terminolojisi OK
2. **Tool call discipline bozuk** — agent mastersheet'i çağırmak yerine hafızadan cevaplıyor → hallucination riski
3. **P95 latency ~7x hedef** — Tool loop ve model düşünme süresi birlikte yavaşlatıyor
4. **Routing "önce netlik iste" davranışı** — CLAUDE.md'deki direkt routing kuralına aykırı

**Plan etkisi:**
- **T1.1 motivasyonu artt**ı — sadece thin'leştirme değil, tool description'a **"Always call — do not rely on memory"** cümlesi eklenmeli
- **T6.1 öne çekilsin** — Routing few-shot'ları Faz 1'den önce girmek daha yüksek ROI
- **Latency ayrı bir task** olmalı — T4.4 (yeni): tool loop optimizasyonu, muhtemelen early-exit logic

---

## 🔜 Ertelenen Task'lar (Sonraki Faz)

- F (Single-file refactor) → `agent.py` 4000+ satır olunca
- D4 (OpenTelemetry migration) → Enterprise ihtiyacı doğunca
- E (Full autonomy slider) → Kullanıcı talebi gelince
- H4 (Adversarial eval suite) → Temel eval stabilleşince
- G4 (Qwen-Agent framework) → Model değişimi gerekmeden tartışmayalım

---

_Son güncelleme: 2026-04-18 | Karar onayları: model (Sonnet 4.6), skill sistemi (B2), prompt caching (Faz 2), direct API (Anthropic)_
