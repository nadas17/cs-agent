# CS Agent — RODO/GDPR Veri Isleme Politikasi

_Son guncelleme: 2026-04-09_
_Referans: Polonya UODO (Urzad Ochrony Danych Osobowych) standartlari_

---

## 1. Veri Sorumlusu

The accounting firm is the data controller for this CS Agent system. The agent is used as an internal operational tool and processes client data.

## 2. Islenen Veri Turleri

| Veri Tipi | Ornek | Saklama Suresi | Maskeleme |
|-----------|-------|----------------|-----------|
| Firma adi | PKN Orlen S.A. | Aktif musteri suresi | Trace'lerde maskelenmez* |
| NIP (Vergi No) | 7740001454 | Aktif musteri suresi | Trace'lerde maskelenir (774***454) |
| PESEL | 92071314567 | Aktif musteri suresi | Trace'lerde maskelenir (92*******67) |
| IBAN | PL61109010140000071219812874 | Aktif musteri suresi | Trace'lerde maskelenir |
| Sorgu gecmisi | "ZUS beyani nasil yapilir?" | 90 gun | PII iceren kisimlar maskelenir |
| Session verileri | Konusma gecmisi | 24 saat inaktivite | Otomatik arsivlenir |
| Feedback | Rating + yorum | 90 gun | PII maskelenir |

*Not: Firma adlari trace loglarinda maskelenmez cunku operasyonel raporlama icin gereklidir. Ancak /admin API'lari uzerinden disariya acilmaz.

## 3. Veri Maskeleme (S1)

Agent su PII turlerini otomatik maskeler:
- NIP: 10 haneli -> `676***841` formati
- PESEL: 11 haneli -> `92*******67` formati
- IBAN: 26 haneli -> `PL**************************` formati

Maskeleme su noktalarda uygulanir:
- `save_trace()` — her trace kaydinda otomatik
- `feedback.jsonl` — linked_query alaninda
- `/admin/*` endpoint'leri — ham veri donmeden once

## 4. Veri Saklama Sureleri

| Veri | Saklama | Otomatik Temizleme |
|------|---------|-------------------|
| Trace loglari (traces/*.jsonl) | 90 gun | `--purge-old-traces 90` CLI komutu |
| Session dosyalari (traces/sessions/) | 24 saat inaktivite | `_load_sessions()` otomatik arsivleme |
| Feedback (feedback.jsonl) | 90 gun | `--purge-old-traces` ile birlikte |
| Alert loglari (alerts.jsonl) | 90 gun | `--purge-old-traces` ile birlikte |
| Client state (client_state.json) | Aktif musteri suresi | Manuel temizleme |
| Uretilen belgeler (outputs/) | 30 gun | Manuel temizleme |

## 5. Veri Sahibi Haklari (RODO Madde 15-20)

| Hak | Uygulama |
|-----|----------|
| Erisim hakki (Madde 15) | Musteri verilerini `/admin/stats` ve mastersheet uzerinden goruntuleme |
| Duzeltme hakki (Madde 16) | Mastersheet'te firma bilgisi duzeltme (manuel) |
| Silme hakki (Madde 17) | `--purge-old-traces` ile trace verisini temizleme |
| Tasima hakki (Madde 20) | Mastersheet CSV olarak disari aktarilabilir |
| Itiraz hakki (Madde 21) | Agent kullanimi hakkinda itiraz Kaan Bey'e iletilir |

## 6. Teknik Guvenlik Onlemleri

| Onlem | Durum | Aciklama |
|-------|-------|----------|
| PII maskeleme | AKTIF | mask_pii() fonksiyonu, NIP/PESEL/IBAN |
| Rate limiting | AKTIF | IP bazli, /chat 30/dk, /admin 10/dk |
| Input sanitization | AKTIF | Max 2000 karakter, path traversal korumal |
| HTTPS/TLS | BEKLIYOR | Production'da Caddy reverse proxy ile |
| Disk sifreleme | BEKLIYOR | OS duzeyi sifreleme onerilir |
| Erisim kontrolu | KISMI | /admin endpoint'leri icin auth planlanmakta |

## 7. Veri Isleme Kaydi (RODO Madde 30)

Bu agent su veri isleme faaliyetlerini gerceklestirir:

1. **Musteri bilgisi sorgulama** — mastersheet_read tool'u ile firma adi/NIP araması
2. **SOP dokumani okuma** — wiki_read ile islem prosedurlerini getirme
3. **Belge uretimi** — create_pdf/docx/xlsx ile musteri raporlari
4. **KRS sorgulama** — krs_lookup ile Polonya sirket sicil bilgisi
5. **Web arama** — exa_search ile guncel mevzuat bilgisi
6. **Konusma kaydi** — session verileri ve trace loglari

## 8. Ucuncu Taraf Veri Transferi

| Servis | Transferin Amaci | Veri Tipi | Koruma |
|--------|-----------------|-----------|--------|
| OpenRouter API | LLM cagrilari | Sorgu metni (PII maskelenMEMIS) | API key auth, HTTPS |
| Exa API | Web arama | Arama sorgusu | API key auth, HTTPS |
| KRS API | Sirket sicil | KRS numarasi | Public API |

**ONEMLI:** OpenRouter API'ye gonderilen mesajlarda PII maskelenmez cunku LLM'in dogru cevap vermesi icin tam bilgi gerekir. OpenRouter'in kendi veri isleme politikasi gecerlidir.

## 9. Ihlal Bildirimi (RODO Madde 33-34)

Veri ihlali durumunda:
1. 72 saat icinde UODO'ya bildirim
2. Etkilenen musterilere bilgilendirme
3. Ihlal raporu hazirlama
4. Duzeltici onlemler uygulama

Ihlal tespiti icin:
- `/admin/alerts` endpoint'i anormal aktivite tespiti yapar
- Trace loglarinda beklenmeyen veri erisim kaliplari izlenir

## 10. Kullanici Bilgilendirmesi

Chat UI'da asagidaki bilgilendirme metni goruntulenir:
> "Bu konusma firma tarafindan islem takibi amacli kaydedilmektedir."

---

_Bu politika firmanin RODO uyumluluk cabalari cercevesinde hazirlanmistir. Yillik gozden gecirme gereklidir._
