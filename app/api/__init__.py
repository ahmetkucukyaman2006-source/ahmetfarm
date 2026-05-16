"""
AhmetFarm - API Blueprint Başlatıcısı
======================================
Bu modül, '/api/v1' ön eki altındaki tüm JSON API rotalarını gruplar.
Saf HTML döndüren main Blueprint'ten ayrılmıştır; bu sayede:
  - Frontend geliştirme (React, Vue vb.) kolaylaşır.
  - Mobil uygulama entegrasyonu mümkün olur.
  - API versiyonlaması (v1, v2) desteklenir.
"""

from flask import Blueprint

# Blueprint nesnesi: URL'ler '__init__.py' içindeki url_prefix ile birleşir.
# Kayıt: app/__init__.py → app.register_blueprint(api_bp, url_prefix='/api/v1')
api_bp = Blueprint('api', __name__)

# Rotalar ayrı dosyada tanımlıdır; dairesel import'u önlemek için en sona import edilir.
from app.api import routes  # noqa: F401, E402
