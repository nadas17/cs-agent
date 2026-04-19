# MasterSheet Veri Yapısı
_Kaynak: Mastersheet 2026 - Master Client | Son güncelleme: 2026-04-06_

## Özet
MasterSheet Excel dosyası iki ana sayfadan oluşur: "Master Client" (firma bilgileri) ve "Data" (aylık belge durumu). 142 aktif firma kaydı mevcut. Firma bilgileri, muhasebeci ataması ve VAT durumu bu dosyada takip edilir.

## İçerik

### "Master Client" Sayfası Kolonları

Nr | Responsible | RA (Muhasebeci) | Company Name | NIP/PESEL | TYP | KRS | REGON | KRS Kayıt Tarihi | VAT Aktiflik Tarihi | Adres | US (Vergi Dairesi) | Mikrorachunek | ZUS Account | Soyad | Ad

### Partner Dağılımı (Responsible sütunu)

| Responsible | Firma Sayısı | Açıklama |
|------------|-------------|----------|
| Firm | ~57 | Directly managed firms |
| Partner (Partner C) | ~54 | Partner C / Partner C Contact partneri |
| Partner B | ~14 | Partner B / Partner B Contact partneri |
| Partner A | ~13 | Partner A / Partner A Contact partneri |

### Önemli Kolon Notları

**RA (Muhasebeci ataması):**
- "Head Accountant" = Head Accountant (Baş Muhasebeci)
- "Accountant" = Accountant
- "nowy pracownik" = Henüz atanmamış (yeni çalışan bekliyor)
- "nieokreszlony" = Belirlenmemiş
- "nie obsligujemy" = Hizmet verilmiyor
- "2025" veya "2026 / O" = Yıl bazlı atama notu

**VAT Durumları:**
- Tarih (örn. "04.06.2025") = VAT aktif, o tarihten itibaren
- "nie" = VAT yok / tescil edilmemiş
- "Zwolniony" = VAT muaf
- "wykreślony" = VAT silindi (Art. 96)
- "ODMOWA" = VAT başvurusu reddedildi
- "tak" = VAT aktif (tarih belirtilmemiş)

**Firma Türleri (TYP):**
- "sp z o o" = Sp. z o.o. (Limited şirket) — çoğunluk
- "JDG" = Jednoosobowa Działalność Gospodarcza (şahıs firması)
- "sp akcyjna" = Spółka akcyjna (anonim şirket)

### "Data" Sayfası
- Satırlar = firmalar
- Sütunlar = aylık belge kategorileri
- Hücre değerleri: "Added" (yeşil), "NO DOC..." (kırmızı), "NO INF..." (turuncu), boş (kontrol edilmedi)

## İlişkili Makaleler
- [[operasyon/belge_toplama.md]]
