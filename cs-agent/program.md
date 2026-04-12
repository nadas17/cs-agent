# CS Agent — Meta-Agent Direktifleri

## Amaç
Bu dosyayı okuyan meta-agent, agent.py'deki SYSTEM_PROMPT ve TOOLS tanımlarını
iyileştirerek benchmark skorunu artırmaya çalışır.

## Değiştirilebilir Alanlar
- SYSTEM_PROMPT string'indeki talimatlar, format örnekleri, routing kuralları
- TOOLS listesindeki tool description'ları
- classify_query keyword listeleri

## Değiştirilemez Alanlar (Dokunma)
- agent_loop fonksiyonunun yapısı
- model_call, build_messages, save_trace fonksiyonları
- Güvenlik kontrolleri (path traversal, API key validation)
- config.py parametreleri
- Docker konfigürasyonu
- wiki_read, mastersheet_read, wiki_write fonksiyon implementasyonları

## Kısıtlamalar
- Tek seferde maksimum 1 değişiklik öner
- Her değişiklik geri alınabilir olmalı (önceki versiyonu sakla)
- Değişiklik sonrası benchmark çalıştır, skor düşerse geri al

## Skor Hedefi
Mevcut baseline: %92 (Faz 1 sonucu)
Hedef: > %95 composite skor
