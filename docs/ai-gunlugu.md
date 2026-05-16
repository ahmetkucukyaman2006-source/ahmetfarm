# AI Günlüğü
Oturum 1 — 14/05/2026 — 00:30
## Hedef
Proje iskeletini "Application Factory" ve "Blueprint" yapısına uygun şekilde kurmak ve veritabanı modellerini (User, Crop, Inventory, FarmPlot) tasarlamak.

## Mod/Model
- Mod: Plan Modu
- Model: Gemini 3.1 Pro (High)
- Görünüm: Manager View

## Promptlar
"Application factory pattern kullanan, blueprint yapısına sahip temel proje iskeletini kur. (ahmetfarm)"

"docs/ klasörü ve içinde ai-gunlugu.md şablonu oluştur."

"SQLAlchemy 2.x stili (Mapped ve mapped_column) kullanarak User, Crop, Inventory ve FarmPlot modellerini oluştur."
## Plan
Proje klasörlerini mkdir komutlarıyla oluşturma.

requirements.txt dosyasına gerekli Flask kütüphanelerini ekleme.

Modelleri yazmadan önce relationship (ilişki) tanımları ve UTC zaman dilimi standardı için onay isteme.
## Sorgulama
Proje klasörlerini mkdir komutlarıyla oluşturma.

requirements.txt dosyasına gerekli Flask kütüphanelerini ekleme.

Modelleri yazmadan önce relationship (ilişki) tanımları ve UTC zaman dilimi standardı için onay isteme.

## Hatalar
- **Ajan Kesintisi:** "Our servers are experiencing high traffic" hatası alındı. `Retry` butonu ile aşıldı.
- **Git Eksikliği:** Sistemde Git yüklü olmadığı için komutlar çalışmadı. `winget` aracılığıyla terminalden kurulum yapıldı.
- **Kimlik Hatası:** Git commit sırasında isim/eposta hatası alındı. `git config` komutlarıyla kullanıcı tanımlandı.
- **Yanlış Dosya Yazımı:** Git komutları yanlışlıkla `.gitignore` içine yazıldı, fark edilip terminale taşındı.

## Öğrenilenler
- Flask 3.x ve SQLAlchemy 2.x arasındaki yeni sözdizimi (Mapped) farklarını kavradım.
- AI ile "Vibe Coding" yaparken sadece komut vermenin yetmediğini, AI'nın sorduğu detaylı sorulara (ilişkiler, zaman dilimi) bilinçli cevap vermenin kod kalitesini artırdığını öğrendim.
- Git'in sadece bir yükleme aracı değil, projenin her aşamasını mühürleyen bir "zaman makinesi" olduğunu deneyimledim.

!Oturum 1 Planı ve Onay Anı](img/oturum1-plan.png)

------------------------
Tarih: 15 Mayıs 2026 20:37

Hedef: Kullanıcı kayıt/giriş sistemini kurmak, güvenliği maksimize etmek ve projeyi GitHub'a yedeklemek.

 1. Teknik Altyapı ve Auth Sistemi

 Flask-Login Entegrasyonu: Uygulamaya Flask-Login kütüphanesi dahil edilerek oturum yönetimi (session management) sağlandı.

 User Modeli ve Veritabanı: app/models.py içerisinde kullanıcıların id, username ve password_hash bilgilerini tutan SQL tablosu oluşturuldu.
 
 Blueprint Yapısı: Kimlik doğrulama işlemleri için app/auth adında yeni bir Blueprint oluşturularak kodun modüler kalması sağlandı.

2. Güvenlik Protokolleri (Sıfır Taviz)
Password Hashing: Şifreler veritabanına asla açık metin olarak kaydedilmedi. werkzeug.security paketindeki generate_password_hash ve check_password_hash fonksiyonları kullanılarak tek yönlü şifreleme uygulandı.
  
  Erişim Kısıtlaması: Dashboard gibi özel sayfalar @login_required dekoratörü ile koruma altına alındı. Giriş yapmayan kullanıcıların bu sayfalara erişimi engellenerek login sayfasına yönlendirilmesi sağlandı.
  
  Form Güvenliği: Tüm Flask-WTF formlarına CSRF (Cross-Site Request Forgery) koruması eklenerek dışarıdan gelecek sahte isteklere karşı önlem alındı.

   3. Frontend ve Kullanıcı Deneyimi 
   
Modern Tasarım: login.html ve register.html sayfaları, 1. gündeki tasarıma sadık kalınarak "Glassmorphism" (cam efekti) ve koyu tema (dark mode) ile geliştirildi.
   
   Dinamik Karşılama: Dashboard ekranına, giriş yapan kullanıcının veritabanındaki ismini çeken "Hoş Geldin, [Kullanıcı Adı]!" mesajı eklendi.

    4. GitHub ve Versiyon Kontrolü Süreci
    
    Depo (Repo) Kurulumu: GitHub üzerinde ahmetkucukyaman2006-source/ahmetfarm adıyla uzak depo oluşturuldu.
    
    Remote Güncelleme: git remote add origin komutuyla yerel projenin GitHub ile bağlantısı kuruldu.
    
    İlk Büyük Push: Toplam 13 dosyadaki değişiklikler "Kullanıcı Kayıt ve Giriş sistemi tamamlandı" mesajıyla buluta başarıyla gönderildi.

  5. Karşılaşılan Zorluklar ve Çözüm Yolları
     
Sorun:Authentication Error

    Neden:GitHub bağlantısı sırasında kimlik doğrulanamadı.

    Çözüm:Tarayıcı üzerinden GitCredential Manager onayı verilerek erişim sağlandı.
    
    Sorun:Repository Not Found

    Neden:Yanlış veya henüz oluşturulmamış depo adresine push denemesi.

    Çözüm:GitHub'da manuel olarak depo açıldı ve git remote remove/add ile adres güncellendi.

   Sorun:Server High Traffic
   Neden:Antigravity sunucularındaki yoğunluk nedeniyle ajan hata verdi.

   Çözüm:Manuel kontrollerle işlemin GitHub tarafında tamamlandığı teyit edildi.
