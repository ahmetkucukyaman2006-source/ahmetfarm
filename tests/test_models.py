from app.models import User
from app.extensions import db

def test_user_password_hashing(app):
    """Kullanıcı şifrelerinin düz metin yerine güvenli şekilde hash'lendiğini doğrular."""
    user = User(username="ahmet_test", email="test@ahmetfarm.com")
    user.set_password("SokeOvası123!")
    
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        
        # Şifrenin düz metin olarak saklanmadığını doğrula
        assert user.password_hash != "SokeOvası123!"
        # Şifre doğrulama metodunun çalıştığını kontrol et
        assert user.check_password("SokeOvası123!") is True
        assert user.check_password("yanlis_sifre") is False
