# DÖNEM PROJESİ RESMİ GELİŞTİRME RAPORU

**Proje Adı:** AhmetFarm (Söke Ovası Çiftlik Simülasyonu)  
**Ders:** BLG106 İnternet Programcılığı  
**Geliştirici:** Ahmet Küçükyaman  
**Geliştirme Metodolojisi:** Vibe Coding (AI-Assisted Agentic Development)  
**Kullanılan Model:** Gemini 3.1 Pro / Claude Sonnet 4.6  
**Geliştirme Ortamı:** Antigravity IDE  

---

## 1. Projenin Amacı ve Ne İşe Yaradığı
AhmetFarm, geleneksel yazılım ödevlerinin monoton yapısını kırarak veritabanı ilişkileri (CRUD), kullanıcı yetkilendirmesi, asenkron veri iletişimi ve çoklu dil desteği gibi modern web teknolojisi bileşenlerini interaktif bir oyun simülasyonu potasında eritmeyi amaçlamaktadır. Proje, Aydın Söke Ovası’nın coğrafi yapısını temel alarak oyunculara dinamik bir çiftlik yönetimi deneyimi sunar. Kullanıcılar sisteme güvenli bir şekilde kayıt olup giriş yaptıktan sonra, harita üzerinde farklı dönüm büyüklüklerine sahip tarlaları satın alabilir, tohum ekebilir, büyüme sürelerini asenkron sayaçlar üzerinden takip edebilir, hasat ettikleri ürünleri ambarlarında depolayabilir ve pazar alanında satarak ekonomik bir döngü oluşturabilirler.

## 2. Mimari Özet: Klasör Yapısı ve Ana Akışlar
Proje, Flask topluluğu tarafından kabul görmüş en sürdürülebilir mimari olan **Application Factory Pattern** ve modüler **Blueprint** yapısı üzerine inşa edilmiştir. Bu mimari, uygulamanın ölçeklenebilir olmasını sağlarken spagetti kod oluşumunu tamamen engeller.

## 3. Vibe Coding Deneyiminiz: Ne İşe Yaradı, Nerede Zorlandınız?
"Vibe Coding" metodolojisi, satır satır kod yazma yükünü tamamen ortadan kaldırarak geliştiriciyi spagetti kod detaylarında boğulmaktan kurtarmış ve bir "Yazılım Mimarı" konumuna yükseltmiştir. Bu süreçte yapay zeka ajanları, sadece basit kod tamamlayıcılar olarak değil; sistem bileşenlerini planlayan, mimariyi kurgulayan ve hata ayıklama süreçlerinde hipotezler üreten otonom iş ortakları olarak görev almıştır. 

Ancak, Vibe Coding disiplini kendi içinde ciddi zorluklar da barındırmaktadır. Ajanların en büyük zaafı, projenin mevcut bağlamını (context) zaman zaman kaybetmeleri ve bir özelliği eklerken daha önce yazılmış çalışan bir kodu bozma eğilimleridir. Özellikle asenkron JavaScript entegrasyonu sırasında ajan, Flask rotasının döndürdüğü JSON formatını unutup HTML render etmeye kalkışmıştır. Burada "Mimar" olarak devreye girmek ve prompt kısıtlarını çok sıkı tutmak gerekmiştir.

## 4. Antigravity IDE'de En Faydalı Bulunan İki Özellik ve Nedenleri
1. **Artifact Yapısı ve Canlı Önizleme Sistemi:** Antigravity bünyesindeki Artifact mimarisi, ajanın ürettiği frontend çıktılarını ana projeye enjekte etmeden önce izole bir sandbox alanında test etmeye imkan tanımıştır. 
2. **Gelişmiş Ajan Yönetim Paneli (Agent Manager View) ve Plan Modu:** Antigravity'nin kod yazmadan önce zorunlu kıldığı "Plan Modu", projenin kaderini değiştirmiştir. Bu sayede ajanın mimariyle çelişen, gereksiz kütüphaneler ekleyen veya güvensiz yöntemler öneren planları daha kod aşamasına geçmeden reddedilmiş ve kontrol daima geliştiricide kalmıştır.

## 5. Ajanın Yakalayıp Düzelttiğim En Kritik Üç Hata
1. **API Tasarımında JSON Yerine HTML Döndürme Hatası (Oturum 6):** Ajan, `/api/v1/stats` uç noktasını tasarlarken, verileri frontend tarafına saf bir JSON objesi olarak geçirmek yerine yanlışlıkla bir Jinja2 şablonu render etmeye (`render_template`) çalışmıştır. Ajana müdahale edilerek `jsonify` kullanması sağlanmıştır.
2. **Şifre Sıfırlama Akışında Süre Sınırı İhmali (Oturum 7):** Ajan, şifremi unuttum sistemi için ürettiği sıfırlama token'larını zaman aşımı parametresi olmadan üretmiştir. Kod reddedilmiş, `URLSafeTimedSerializer` sınıfı projeye dikte ettirilerek token'lara 30 dakikalık ömür (expiration) sınırı getirilmiştir.
3. **Canlı Sunucu Entegrasyonunda Gönderici Eksikliği (Oturum 9):** Mock sistemden gerçek e-posta gönderimine geçildiğinde, ajan e-posta objesine bir gönderici tanımlamamıştır. Bu durum `AssertionError` hatasına yol açmıştır. Çözüm olarak `config.py` içine `MAIL_DEFAULT_SENDER` parametresi eklenmiştir.

## 6. Proje Yapay Zeka Olmadan Sıfırdan Yapılsaydı Ne Kadar Sürerdi?
Eğer bu proje yapay zeka ajanları olmadan, tamamen geleneksel el kodlaması ve manuel hata ayıklama yöntemleriyle yapılsaydı, geliştirme süresi en az 4 ila 5 kat daha uzun sürerdi. Geleneksel yöntemlerle yaklaşık 3 ila 4 hafta sürebilecek olan bu web uygulaması, Vibe Coding disiplini sayesinde 3-4 günlük bir zaman diliminde tamamen üretime hazır hale getirilmiştir.

## 7. Proje Sürdürülseydi Bir Sonraki Adım Ne Olurdu?
Bir sonraki geliştirme fazında atılacak en stratejik adım, veritabanını SQLite'dan tamamen kopararak PostgreSQL ilişkisel veritabanına geçirmek olurdu. Ayrıca WebSocket teknolojisini kullanarak oyuncuların birbirleriyle anlık olarak ürün ticareti yapabildiği gerçek zamanlı bir Canlı Pazar mekanizması eklenebilirdi.
