# Customer Success AI Agent — Master Architecture

## Uc Uzmanin Birlesik Vizyonu

> **Simulasyon:** Andrej Karpathy, Andrew Ng ve Yann LeCun'un tasarim felsefelerinin bir CS AI Agent mimarisine uygulanmasi.

---

## 1. Karpathy'nin Gozunden: "The General Harness"

*"Don't build features, build action spaces. Let the agent discover the optimal workflow."*

Karpathy'nin AutoAgent felsefesi: Agent kendi prompt'unu, tool setini ve orkestrasyon mantigi optimize etmeli. CS agenti bir "compiled knowledge base" uzerine oturmali — RAG degil, baglami derlenmis `.md` dosyalari.

### Modul: Harness Core

```
+------------------------------------------+
|            HARNESS CORE                  |
|                                          |
|  Goal Parser --> Tool Router --> Loop    |
|       |              |            |      |
|  "Musteri X'in      Tool        Sonuc   |
|   VAT durumu?"    Registry    Degerlendir|
|                                          |
|  +-------------+  +--------------+       |
|  | Compiled    |  | Decision     |       |
|  | Knowledge   |  | Trace Logger |       |
|  | (.md files) |  | (ogrenme)    |       |
|  +-------------+  +--------------+       |
+------------------------------------------+
```

**Karpathy'nin 4 temel prensibi:**

1. **Compiled Context > RAG** — Firmanin tum SOP'lari, vergi takvimleri, musteri kurallari `.md` dosyalarina derlenmeli. Her sorgu icin vektor aramasi yapmak yerine, dogru `.md` dosyasini secen bir router yeterli.

2. **Action Space = Tool Registry** — Agent'in yapabilecegi her sey bir tool. `check_vat_status`, `send_reminder_email`, `create_task`, `lookup_client_history`. Baslangicta 10 tool, agent kullanim verisine gore yenileri eklenir.

3. **Decision Traces** — Her agent karari loglanir. "Musteri X sordu -> Tool Y cagirdim -> Sonuc Z" Bu trace'ler kurumsal hafiza olur.

4. **Self-Optimizing Loop** — Agent kendi prompt'unu, SOP dokumanlarindaki bosluklara gore guncelleme onerileri uretir.

---

## 2. Andrew Ng'nin Gozunden: "Systematic Deployment"

*"The gap between a demo and production is where most AI projects die. Start with the workflow, not the model."*

Ng'nin yaklasimi: Once mevcut CS workflow'unu tam olarak dokumante et, darbogazi bul, en yuksek ROI olan noktadan basla.

### Modul: Data Flywheel & Evaluation

```
+----------------------------------------------+
|          DATA FLYWHEEL                       |
|                                              |
|  +----------+    +-----------+    +--------+ |
|  | Human    |--->| AI Agent  |--->| Human  | |
|  | Handoff  |    | Response  |    | Review | |
|  | Trigger  |    | Generator |    | & Rate | |
|  +----------+    +-----------+    +--------+ |
|       ^                               |      |
|       +------- Feedback Loop <--------+      |
|                                              |
|  +--------------------------------------+    |
|  | Evaluation Pipeline                  |    |
|  |  - Accuracy (dogru cevap %)          |    |
|  |  - Latency (yanit suresi)            |    |
|  |  - Escalation Rate (insana devir %)  |    |
|  |  - Client Satisfaction (NPS delta)   |    |
|  +--------------------------------------+    |
+----------------------------------------------+
```

**Ng'nin 4 temel prensibi:**

1. **Error Analysis First** — Lansmandan once 100 gercek musteri sorusu toplanir. Agent bunlara cevap verir. Hatalar kategorize edilir: "Yanlis bilgi", "Eksik baglam", "Yanlis tool secimi", "Ton hatasi". En buyuk kategori once duzeltilir.

2. **Human-in-the-Loop Tiers** — Uc seviye:
   - **Tier 1 (Otonom):** Bilgi sorulari, durum sorgulari, standart hatirlatmalar
   - **Tier 2 (Onayli):** Email gonderimi, task olusturma, dokuman hazirlama
   - **Tier 3 (Yalnizca Insan):** Sikayetler, sozlesme degisiklikleri, hukuki konular

3. **Data Flywheel** — Her insan mudahalesi yeni egitim verisi olur. Agent zamanla Tier 2'deki isleri Tier 1'e tasir.

4. **Deployment as Iteration** — v0.1'de sadece "bilgi sorgulama" calisir. v0.2'de "hatirlatma gonderme" eklenir. Her modul ayri degerlendirilir, ayri deploy edilir.

---

## 3. Yann LeCun'un Gozunden: "World Model"

*"An intelligent agent needs an internal model of its world to plan and predict outcomes."*

LeCun'un JEPA-ilhamli yaklasimi: Agent musteri dunyasinin bir "world model"ine sahip olmali — sadece react etmek degil, predict etmek.

### Modul: Predictive Client Model

```
+----------------------------------------------+
|          WORLD MODEL LAYER                   |
|                                              |
|  +----------------+   +-------------------+  |
|  | Client State   |   | Prediction        |  |
|  | Representation |-->| Engine            |  |
|  |                |   |                   |  |
|  | - Firma tipi   |   | - Churn riski     |  |
|  | - Vergi takvim |   | - Odeme gecikmesi |  |
|  | - Iletisim     |   | - Soru paterni    |  |
|  |   gecmisi      |   | - Buyume sinyali  |  |
|  | - Uyum durumu  |   |                   |  |
|  +----------------+   +-------------------+  |
|                                              |
|  +----------------------------------------+  |
|  | Proactive Action Planner              |   |
|  |                                        |  |
|  | IF churn_risk > 0.7 -> alert CS team   |  |
|  | IF deadline - 5 days -> auto remind    |  |
|  | IF growth_signal -> upsell suggestion  |  |
|  | IF silence > 30 days -> check-in email |  |
|  +----------------------------------------+  |
+----------------------------------------------+
```

**LeCun'un 4 temel prensibi:**

1. **State Representation** — Her musteri bir "state vector" ile temsil edilir. Sirket tipi, sektor, risk seviyesi, iletisim sikligi, odeme gecmisi. Bu sadece veri degil, agent'in dunyayi "anlamasini" saglayan yapi.

2. **Prediction over Reaction** — Agent "musteri ne sordu" yerine "musteri ne soracak" uzerine calisir. Vergi beyanname takvimi yaklasiyorsa, musteri sormadan hatirlatma hazirlar.

3. **Hierarchical Planning** — Gunluk (bugun kimlere ulasmali), haftalik (hangi musteriler risk altinda), aylik (trend analizi) planlar. Agent sadece ticket cozmez, stratejik CS plani onerir.

4. **Energy-Based Filtering** — Her olasi aksiyon bir "energy score" alir. Dusuk enerjili (yuksek degerli, dusuk riskli) aksiyonlar otomatik calisir, yuksek enerjili olanlar insana yonlendirilir.

---

## 4. BIRLESIK MIMARI

```
+===========================================================+
|                CS AI AGENT — UNIFIED                       |
+===========================================================+
|                                                            |
|  +-----------------------------------------------------+  |
|  |            LAYER 4: INTERFACE                        |  |
|  |  Slack / Email / Dashboard / WhatsApp                 |  |
|  +---------------------------+-------------------------+   |
|                              |                             |
|  +---------------------------v-------------------------+   |
|  |     LAYER 3: HARNESS (Karpathy)                     |  |
|  |  Goal Parser -> Tool Router -> Execution Loop       |  |
|  |  Compiled Knowledge (.md) | Decision Traces         |  |
|  +---------------------------+-------------------------+   |
|                              |                             |
|  +---------------------------v-------------------------+   |
|  |     LAYER 2: WORLD MODEL (LeCun)                    |  |
|  |  Client State Vectors | Prediction Engine           |  |
|  |  Proactive Planner | Energy-Based Filter            |  |
|  +---------------------------+-------------------------+   |
|                              |                             |
|  +---------------------------v-------------------------+   |
|  |     LAYER 1: DATA FLYWHEEL (Ng)                     |  |
|  |  Evaluation Pipeline | Human-in-the-Loop Tiers      |  |
|  |  Error Analysis | Feedback Loop                     |  |
|  +-----------------------------------------------------+  |
|                                                            |
+============================================================+
```

### Modul Bazinda Ozet

| Modul | Ilham | Islev | Oncelik |
|-------|-------|-------|---------|
| Compiled Knowledge Base | Karpathy | SOP, vergi takvimi, kurallar -> `.md` | P0 |
| Tool Registry | Karpathy | Cagrilabilir aksiyonlar katalogu | P0 |
| Goal Parser | Karpathy | Dogal dil -> yapilandirilmis intent | P0 |
| Decision Trace Logger | Karpathy | Her karar loglanir, kurumsal hafiza | P1 |
| Evaluation Pipeline | Ng | Accuracy, latency, escalation metrikleri | P0 |
| Human-in-the-Loop Tiers | Ng | Otonom / Onayli / Yalnizca Insan | P0 |
| Error Analysis System | Ng | Hata kategorileme ve onceliklendirme | P1 |
| Data Flywheel | Ng | Feedback -> model iyilestirme dongusu | P2 |
| Client State Vectors | LeCun | Her musterinin temsili | P1 |
| Prediction Engine | LeCun | Churn, gecikme, buyume tahmini | P2 |
| Proactive Planner | LeCun | Otomatik check-in ve hatirlatmalar | P2 |
| Energy-Based Filter | LeCun | Aksiyon risk/deger skorlamasi | P3 |

---

## 5. ROADMAP

### Phase 0 — Temel (Hafta 1-2)
**"Ng: Walk before you run"**

- [ ] 100 gercek musteri sorusu toplanir ve kategorize edilir
- [ ] Mevcut CS workflow'u bastan sona dokumante edilir
- [ ] Basari metrikleri tanimlanir (accuracy target: %90, escalation target: <%15)
- [ ] Tool listesi cikarilir (ilk 10 tool belirlenir)

### Phase 1 — Compiled Core (Hafta 3-4)
**"Karpathy: Build the harness"**

- [ ] SOP dokumanlari `.md` formatina derlenir
- [ ] Vergi takvimi ve deadline veritabani olusturulur
- [ ] System prompt yazilir (mevcut 14 bolumlu yapi temel alinir)
- [ ] Goal Parser prototipi: intent classification (bilgi/aksiyon/sikayet)
- [ ] Ilk 5 tool implement edilir:
  - `query_client_info` — musteri bilgisi sorgulama
  - `check_tax_deadline` — vergi takvimi kontrolu
  - `lookup_sop` — SOP dokumani getirme
  - `draft_email` — email taslagi olusturma
  - `create_task` — gorev olusturma
- [ ] "Anladigimi onayliyorum" confirmation pattern uygulanir

### Phase 2 — Evaluation & Tiers (Hafta 5-6)
**"Ng: Measure everything"**

- [ ] Evaluation pipeline kurulur (100 test case ile)
- [ ] Human-in-the-Loop tier'lari implement edilir:
  - Tier 1: Bilgi sorgulari -> otonom
  - Tier 2: Email/task -> onay gerekli
  - Tier 3: Sikayet/hukuk -> direkt insan
- [ ] Error analysis: Ilk 100 cevap analiz edilir, hata kategorileri belirlenir
- [ ] Decision Trace Logger aktif edilir
- [ ] Rana ve Mehtap ile pilot test baslar (ic kullanim)

### Phase 3 — World Model (Hafta 7-10)
**"LeCun: Understand, don't just react"**

- [ ] Client State Vector tasarimi (Supabase tablosu):
  - `risk_score`, `last_contact`, `payment_pattern`, `query_frequency`
- [ ] Proactive Planner — kural tabanli baslangic:
  - Deadline 5 gun kala -> otomatik hatirlatma kuyrugu
  - 30 gun sessizlik -> check-in onerisi
  - Odeme gecikmesi pattern'i -> risk uyarisi
- [ ] Haftalik CS ozet raporu (hangi musteriler risk altinda)
- [ ] Energy-Based Filter: aksiyonlari risk/deger matrisinde skorlama

### Phase 4 — Flywheel & Self-Optimization (Hafta 11-16)
**"Ucunun birlesimi: Otonom ogrenme dongusu"**

- [ ] Data Flywheel aktif: Her insan duzeltmesi -> training data
- [ ] Tier promosyonu: Yeterli veri biriken Tier 2 isler -> Tier 1'e gecer
- [ ] Self-optimization: Agent, SOP bosluklarini tespit eder ve guncelleme onerir
- [ ] Prediction Engine: Basit ML modeli (logistic regression) ile churn tahmini
- [ ] Dashboard: Real-time agent performansi (accuracy, escalation, CSAT)
- [ ] Musterilere yonelik self-service portal (SSS, durum sorgulama)

### Phase 5 — Scale & Autonomy (Hafta 17+)
**"Production-grade CS AI"**

- [ ] Multi-channel: Email + Slack + WhatsApp + Dashboard
- [ ] Coklu dil destegi: TR / EN / PL otomatik algilama
- [ ] Advanced prediction: Buyume sinyalleri -> upsell onerileri
- [ ] Cross-client pattern detection: "Sektor X'teki musteriler ayni soruyu soruyor"
- [ ] Agent-to-agent: CS agent <-> Muhasebe agent koordinasyonu
- [ ] Tam otonom Tier 1 operasyonu (insan sadece Tier 2-3)

---

## 6. KONTROL LISTESI — Lansman Oncesi

### Mimari Kontrol

- [ ] Compiled knowledge base tum SOP'lari kapsiyor mu?
- [ ] Tool registry'deki her tool hata yonetimi iceriyor mu?
- [ ] Decision trace'ler loglaniyor ve erisilebilir mi?
- [ ] Confirmation pattern tum write/modify/send islemlerinde aktif mi?
- [ ] Fallback: Tool cagrisi basarisiz olursa graceful degradation var mi?

### Veri & Guvenlik Kontrol

- [ ] Musteri verisi sifreleme (at rest + in transit) var mi?
- [ ] PII maskeleme: Agent loglarinda kisisel veri maskelenmis mi?
- [ ] RODO/GDPR uyumlulugu kontrol edildi mi?
- [ ] API anahtarlari environment variable'da mi?
- [ ] Rate limiting aktif mi?

### Kalite Kontrol

- [ ] 100 test case'de accuracy >= %90 mi?
- [ ] Escalation rate <= %15 mi?
- [ ] Ortalama yanit suresi <= 5 saniye mi?
- [ ] Yanlis bilgi verme orani <= %2 mi?
- [ ] Ton ve dil kalitesi Rana/Mehtap tarafindan onaylandi mi?

### Operasyonel Kontrol

- [ ] Monitoring dashboard canli mi?
- [ ] Alert sistemi: Agent hata orani artarsa bildirim gider mi?
- [ ] Rollback plani: Agent kapatilabilir, insan devralabilir mi?
- [ ] Kaan'dan go/no-go onayi alindi mi?
- [ ] Musterilere AI asistan kullanimi bildirildi mi?

### Surekli Iyilestirme Kontrol

- [ ] Haftalik error analysis toplantisi takvime eklendi mi?
- [ ] Feedback loop mekanizmasi calisiyor mu?
- [ ] Tier promosyon kriterleri yazili mi?
- [ ] Aylik metric review sureci tanimli mi?
- [ ] SOP guncelleme -> knowledge base guncelleme sureci otomatik mi?

---

## 7. HER UZMANDAN FIRMAYA OZEL TAVSIYE

### Karpathy -> Dogukan'a:
> "225 musteriniz var, hepsinin sorulari benzer pattern'ler izliyor. RAG ile her sorguda vektor aramasi yapmak yerine, 'Vergi Takvimi', 'Sirket Kurulus', 'Calisma Izni', 'Muhasebe Dongusu' gibi 8-10 compiled `.md` dosyasi yaz. Agent dogru dosyayi secsin, icinde arasin. Daha hizli, daha guvenilir, daha ucuz."

### Ng -> Dogukan'a:
> "Ilk versiyonu 2 haftada yayinla, ama sadece Rana ve Mehtap kullansin. Onlarin duzeltmeleri senin en degerli verin. 100 duzeltme topladiginda agent %80'den %95'e ziplar. Mukemmel urunu bekleyerek 3 ay harcama."

### LeCun -> Dogukan'a:
> "Musterilerinin vergi beyanname takvimini biliyorsun. Agent'in musteriden once hatirlatma gondermesi tek basina devasa deger yaratir. Reactive'den proactive'e gecis, CS'in en buyuk level-up'i."

---

*Bu dokuman uc farkli AI vizyonunun sentezini icerir. Temel ilke: Basit basla (Phase 0), olc (Phase 2), tahmin et (Phase 3), ogren (Phase 4).*
