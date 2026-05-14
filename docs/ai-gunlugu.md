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

