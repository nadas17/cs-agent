**Amaç**
========

Bu SOP'nin amacı:

-   tüm işlerin tek ve merkezi sistemde yönetilmesini sağlamak

-   sorumluluk, durum ve ilerlemeyi görünür hale getirmek

-   ekipler arası koordinasyonu standartlaştırmak

-   SLA, gecikme ve riskleri kontrol altına almak

Bu SOP, tüm operasyonel süreçlerin temel kontrol mekanizmasıdır.

**Temel İlkeler (Bağlayıcı Kurallar)**
======================================

Task yoksa → iş yoktur\
Owner yoksa → sorumluluk yoktur\
Status yoksa → kontrol yoktur\
Kanıt yoksa → iş tamamlanmamıştır

**3. Sistem Mimarisi**
======================

**3.1 Sistem Rol Dağılımı**
---------------------------

  **Sistem**   **Amaç**
  ------------ ----------------------------
  Zoho Desk    Müşteri iletişimi
  Zoho CRM     Task ve operasyon yönetimi
  Zoho Phone   Telefon kayıtları

**4. Task Türleri (Zorunlu Sınıflandırma)**
===========================================

Her task aşağıdaki tiplerden biri olmak zorundadır:

-   DOCUMENT

-   APPROVAL

-   ACTION

-   CLIENT RESPONSE

-   COMPLIANCE

-   RISK / ESCALATION

**5. Task Status Sistemi**
==========================

**5.1 Standart Statusler**
--------------------------

-   NEW → Task oluşturuldu

-   IN PROGRESS → Aktif çalışma var

-   WAITING -- CLIENT → Müşteri yanıtı bekleniyor

-   WAITING -- INTERNAL → İç ekip aksiyonu bekleniyor

-   BLOCKED → İş yapılamıyor

-   DONE → İş tamamlandı

-   CANCELLED → Geçersiz

**5.2 Status Kuralları**
------------------------

Status değişmeden ilerleme yoktur\
DONE = kanıt + müşteri bilgilendirmesi

**6. Ownership**
================

**6.1 Tek Sahip Kuralı**
------------------------

Her task'ın sadece 1 owner'ı vardır

**7. Task Açma Kuralları**
==========================

Her task aşağıdaki bilgileri içermek zorundadır:

-   Client ID

-   Task Type

-   Açıklama (net ve yorumsuz)

-   Deadline

-   Owner

-   İlgili SOP referansı

**8. Deadline Kuralları**
=========================

**8.1 Default Deadline (Zorunlu)**
----------------------------------

Müşteri deadline vermediyse:

**Deadline = ertesi iş günü mesai bitimi**

**8.2 Override Kuralları**
--------------------------

-   Müşteri deadline verdiyse → geçerlidir

-   Yasal deadline varsa → geçerlidir

**9. Desk Merkezli Müşteri Yönetimi**
=====================================

**9.1 Ana Kural**
-----------------

Müşteriden gelen tüm konular SADECE Zoho Desk üzerinden yönetilir
-----------------------------------------------------------------

**9.2 Süreç Akışı**
-------------------

1.  Müşteri → Desk ticket

2.  Destek → değerlendirme

3.  CRM task açılır

4.  İç ekip koordinasyonu

5.  Müşteriye Desk üzerinden dönüş

**9.3 Rol Ayrımı**
------------------

  **Rol**   **Sorumluluk**
  --------- ----------------------------------
  Destek    Koordinasyon + müşteri iletişimi
  İç ekip   İşin yapılması

❌ İç ekip müşteriye cevap vermez

**10. İç İletişim Dili**
========================

👉 Tüm diğer departmanlar ile olan iç iletişim İNGİLİZCE yapılır

Kapsam:

-   CRM notları

-   Desk iç yorumları

-   Internal e-mailler

-   Task açıklamaları

❌ Türkçe veya karışık dil yasaktır, Support ekibinin iç yazışması Türkçe olabilir.

**11. Waiting Status Kuralları**
================================

**11.1 Waiting -- Client**
--------------------------

👉 Maksimum süre: **1 iş günü**

-   süre dolarsa → follow-up zorunlu

-   devam ederse → Non-response süreci

**11.2 Waiting -- Internal**
----------------------------

👉 Maksimum süre: **1 iş günü**

-   süre aşımı → escalation

**11.3 Temel İlke**
-------------------

👉 Waiting = pasif bekleme değil, aktif kontrol statüsüdür

**12. Handover (Devir Yönetimi)**
=================================

**12.1 Kural**
--------------

👉 Task devredilmez → yeni task açılır, ilk Task'in içerisine diğer taskın numarası yazılır ve bağlanır.

**12.2 Standart Flow**
----------------------

Destek işi tamamlar → DONE\
↓\
Yeni task açılır → Muhasebe

Takip yine Support'tadır.

**12.3 Yasaklar**
-----------------

❌ Sözlü devir\
❌ WhatsApp devir\
❌ "bakar mısın" yaklaşımı

**13. Telefon Kullanımı (Zoho Phone)**
======================================

Telefon:

-   karar aracı değildir

-   destekleyici araçtır

-   Her görüşme kaydedilmek zorundadır

**13.1 Zorunlu Kural**
----------------------

👉 Her telefon görüşmesi CRM'e loglanır

**14. SLA & Status İlişkisi**
=============================

  **Status**    **SLA**
  ------------- --------------------
  NEW           Başladı
  IN PROGRESS   Devam
  WAITING       Durur
  BLOCKED       Durur + escalation
  DONE          Kapanır

**15. İş Kapanış & Kanıt Kuralı**
=================================

👉 Kanıt olmadan task DONE olamaz

**15.1 Zorunlu Kapanış**
------------------------

-   Müşteriye e-posta gönderilir

-   Yapılan işlem açıklanır

-   Çıktı / belge paylaşılır

**15.2 Geçerli Kanıtlar**
-------------------------

-   e-posta

-   resmi belge

-   sistem çıktısı

-   dosya

**15.3 Temel İlke**
-------------------

👉 "Yaptık" geçersiz\
👉 "Kanıtladık" geçerli

**16. Escalation Kuralları**
============================

Escalation tetikleyicileri:

-   deadline aşımı

-   BLOCKED \> 24 saat

-   WAITING \> 1 iş günü

**17. Kayıt & Audit**
=====================

Loglanması zorunlu:

-   task creation

-   status değişimi

-   owner değişimi

-   timestamp

-   completion proof

**18. Kesin Yasaklar**
======================

❌ Task açmadan iş yapmak\
❌ Owner'sız task\
❌ Status güncellemeden ilerlemek\
❌ Desk içinde iş yönetmek\
❌ WhatsApp üzerinden karar almak\
❌ Kanıtsız "DONE"
