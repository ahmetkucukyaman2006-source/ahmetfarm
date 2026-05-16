"""
AhmetFarm - Uygulama Fabrikası (Application Factory)
=====================================================
Bu modül, Flask uygulamasını "Application Factory" (Uygulama Fabrikası) deseniyle
başlatır. Bu desen, uygulamanın farklı konfigürasyonlarla (geliştirme, test, üretim)
kolayca çalıştırılabilmesini sağlar ve dairesel import (circular import) sorunlarını
önler.

Mimari: Blueprint tabanlı modüler yapı
  - app.auth   → Kullanıcı kimlik doğrulama rotaları (kayıt, giriş, çıkış)
  - app.main   → Oyun mantığı rotaları (harita, ekim, hasat, pazar, tesisler)
"""

from flask import Flask
from flask_migrate import Migrate
from config import Config
from app.models import db
from app.extensions import login_manager, csrf, babel, mail

# Flask-Migrate, veritabanı şema değişikliklerini yönetmek için kullanılır.
# 'flask db migrate' ve 'flask db upgrade' komutlarını etkinleştirir.
migrate = Migrate()


def create_app(config_class=Config):
    """
    Flask uygulama örneğini oluşturan ve yapılandıran fabrika fonksiyonu.

    Bu fonksiyon:
    1. Flask uygulamasını başlatır ve konfigürasyonu yükler.
    2. Veritabanı (SQLAlchemy), migration (Migrate), oturum yönetimi (LoginManager)
       ve CSRF korumasını (CSRFProtect) uygulamaya bağlar.
    3. Blueprint'leri URL ön ekleriyle kaydeder.

    Args:
        config_class: Kullanılacak konfigürasyon sınıfı. Varsayılan: Config.

    Returns:
        Yapılandırılmış Flask uygulama örneği (app).
    """
    app = Flask(__name__)

    # Config sınıfından uygulama ayarlarını yükle (SECRET_KEY, SQLALCHEMY_DATABASE_URI vb.)
    app.config.from_object(config_class)

    # --- Eklenti Başlatma (Extension Initialization) ---
    # Her eklenti, uygulama örneğine bağlanmadan önce bağımsız olarak oluşturulmuştur.
    # Bu, Application Factory deseninin temel gereksinimidir.

    db.init_app(app)              # SQLAlchemy ORM - veritabanı bağlantısı
    migrate.init_app(app, db)     # Flask-Migrate - şema versiyonlama
    login_manager.init_app(app)   # Flask-Login - oturum yönetimi ve @login_required koruması
    csrf.init_app(app)            # Flask-WTF CSRFProtect - tüm POST isteklerine CSRF token doğrulaması

    # Flask-Babel 4.x'te @babel.localeselector kaldırıldı.
    # Bunun yerine locale_selector= parametresi ile fonksiyon doğrudan verilir.
    # Öncelik sırası: 1) session['lang']  2) Tarayıcı Accept-Language  3) Varsayılan 'tr'
    def get_locale():
        """
        Her istekte çağrılarak aktif dili belirler.

        Dil seçim önceliği:
          1. session['lang'] → Kullanıcı /set_lang rotasıyla dil seçtiyse
          2. request.accept_languages → Tarayıcının tercih ettiği dil (örn: 'en-US')
          3. 'tr' → Hiçbiri yoksa Türkçe varsayılan olarak döner
        """
        from flask import session, request as req
        # 1. Oturum tabanlı dil tercihi (kalıcı seçim)
        lang = session.get('lang')
        if lang in ('tr', 'en'):
            return lang
        # 2. Tarayıcı Accept-Language başlığından en iyi eşleşme
        return req.accept_languages.best_match(['tr', 'en']) or 'tr'

    babel.init_app(app, locale_selector=get_locale)  # Flask-Babel - i18n
    mail.init_app(app)                               # Flask-Mail - e-posta gönderme

    # --- Blueprint Kaydı ---
    # Blueprint'ler, uygulamayı mantıksal modüllere ayırmamızı sağlar.
    # Bu sayede her modülün kendi route, template ve static dosyaları olabilir.

    # Kimlik doğrulama modülü: /auth/login, /auth/register, /auth/logout
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Ana oyun modülü: /, /plant, /harvest, /market, /factory vb.
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)

    # API modülü: /api/v1/me, /api/v1/plots, /api/v1/inventory, /api/v1/avatar
    # JSON dönen saf API rotaları; web ve gelecekteki mobil uygulamalar için
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app
