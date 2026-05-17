# 🌾 AhmetFarm - Söke Ovası Çiftlik Simülasyonu

AhmetFarm, Flask web çatısı kullanılarak geliştirilmiş, oyuncuların Aydın Söke Ovası'nda kendi tarlalarını ekip biçebildiği, ürünlerini depolayıp pazarda satabildiği ve seviye atlayarak yeni tesisler kurabildiği interaktif bir web tabanlı çiftlik simülasyonudur.

Bu proje, BLG106 İnternet Programcılığı dersi dönem projesi kapsamında, "Vibe Coding" disiplini ve Yapay Zeka destekli geliştirme süreçleri takip edilerek inşa edilmiştir.

## 🚀 Özellikler (Zorunlu ve Bonuslar)
- **Güvenli Kimlik Doğrulama:** Flask-Login ve werkzeug.security ile güvenli kayıt, giriş ve şifreleme.
- **Gerçek Zamanlı Mail Entegrasyonu:** Flask-Mail ve Google SMTP üzerinden şifre sıfırlama akışı.
- **Asenkron Oyun Döngüsü:** JavaScript Fetch API ile sayfa yenilenmeden çalışan hasat ve bekleme süreleri.
- **Dinamik Coğrafi Harita:** Absolute positioning kullanılarak oluşturulan gerçekçi Söke Ovası haritası ve dönüm hesaplaması.
- **Oyunlaştırma (Gamification):** Seviye atlama (Level Up), deneyim puanı (XP) ve Boss tesisleri.
- **Çoklu Dil Desteği:** Flask-Babel ile anında geçiş yapılabilen Türkçe (TR) ve İngilizce (EN) arayüz.
- **Gelişmiş Profil ve Avatar:** Multipart form data ile güvenli resim yükleme ve sergileme.
- **JSON API & Arama:** `/api/v1/stats` uç noktası ve pazar araması.

## 🛠️ Kullanılan Teknolojiler
* **Backend:** Python 3.12, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Babel, Flask-Mail
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API), Jinja2
* **Dağıtım:** Docker, docker-compose, PostgreSQL
* **Mimari:** Application Factory Pattern, Blueprints

## 🤖 AI Geliştirme Günlüğü ve Raporu
Projenin yapay zeka ile geliştirilme sürecindeki tüm detaylar için [docs/ai-gunlugu.md](docs/ai-gunlugu.md) dosyasına, detaylı mimari rapor için [docs/rapor.md](docs/rapor.md) dosyasına göz atabilirsiniz.

---
*Geliştirici: Ahmet Küçükyaman - 2026*
