"""
AhmetFarm - Güvenlik Yardımcı Fonksiyonları (Security Utilities)
=================================================================
Bu modül, kullanıcı kimlik doğrulamasıyla ilgili güvenlik araçlarını içerir.

itsdangerous Kütüphanesi:
  Flask ile birlikte kurulan bu kütüphane, verileri SECRET_KEY ile imzalar.
  İmzalanmış veriler değiştirilemez; değiştirilirse doğrulama başarısız olur.
  URLSafeTimedSerializer ek olarak zaman damgası ekler — token belirli bir
  süre sonra otomatik olarak geçersiz hale gelir.

Kullanım Akışı (Şifre Sıfırlama):
  1. generate_reset_token(user.email)  → Güvenli token üretilir
  2. Token e-posta ile kullanıcıya gönderilir (link içinde)
  3. Kullanıcı linke tıklar → verify_reset_token(token) çağrılır
  4. Token geçerliyse e-posta döner → kullanıcı bulunur → şifre sıfırlanır
  5. Token süresi dolmuşsa (varsayılan 30 dk) → hata mesajı gösterilir
"""

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app


# Token'ın içinde hangi veri saklanacak (salt: imzayı özelleştirir)
# Aynı SECRET_KEY ile farklı amaçlar için aynı serializer kullanılsa bile
# farklı salt değerleri token'ların birbirinin yerine geçmesini engeller.
_SALT = 'ahmetfarm-password-reset-salt'


def generate_reset_token(email: str) -> str:
    """
    Verilen e-posta adresi için zaman aşımına sahip güvenli bir token üretir.

    Nasıl Çalışır:
      - E-posta adresi, uygulamanın SECRET_KEY'i ile HMAC-SHA1 algoritması
        kullanılarak imzalanır.
      - İmzanın içine otomatik olarak oluşturulma zamanı (timestamp) gömülür.
      - Üretilen token URL-güvenli Base64 formatındadır (URL'de kullanılabilir).

    Args:
        email: Token'a gömülecek kullanıcı e-posta adresi.

    Returns:
        str: URL-güvenli, imzalı token string'i.

    Örnek:
        token = generate_reset_token('ahmet@example.com')
        # → 'eyJlbWFpbCI6ImFobWV0QGV4YW1wbGUuY29tIn0...'
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=_SALT)


def verify_reset_token(token: str, max_age_seconds: int = 1800) -> str | None:
    """
    Token'ı doğrular ve içindeki e-posta adresini döner.

    Doğrulama Kontrolleri:
      1. İmza bütünlüğü: Token değiştirilmiş mi? (BadSignature → None)
      2. Zaman aşımı: Token max_age_seconds'dan daha eski mi? (SignatureExpired → None)

    Args:
        token:           Doğrulanacak token string'i.
        max_age_seconds: Token'ın geçerli olduğu maksimum süre (saniye).
                         Varsayılan: 1800 saniye = 30 dakika.

    Returns:
        str | None: Token geçerliyse içindeki e-posta adresi,
                    geçersiz veya süresi dolmuşsa None.

    Örnek:
        email = verify_reset_token(token)
        if email is None:
            flash('Link geçersiz veya süresi dolmuş.', 'error')
        else:
            user = User.query.filter_by(email=email).first()
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        # loads() hem imzayı doğrular hem de zaman aşımını kontrol eder
        email = serializer.loads(token, salt=_SALT, max_age=max_age_seconds)
        return email
    except SignatureExpired:
        # Token geçerliydi ama süresi doldu
        return None
    except BadSignature:
        # Token bozuk veya değiştirilmiş
        return None
