import pytest
from app.models import User
from app.extensions import db

def test_register_flow(client, app):
    """Kullanıcı kayıt akışının (Register) başarıyla çalıştığını doğrular."""
    response = client.post('/auth/register', data={
        'username': 'yeni_oyuncu',
        'email': 'oyuncu@farm.com',
        'password': 'Sifre123_test!',
        'confirm_password': 'Sifre123_test!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    with app.app_context():
        user = User.query.filter_by(username='yeni_oyuncu').first()
        assert user is not None
