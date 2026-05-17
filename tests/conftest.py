import pytest
from app import create_app
from app.extensions import db
from app.models import User

@pytest.fixture
def app():
    """Testler için Flask uygulamasını ve in-memory SQLite veritabanını izole şekilde kurar."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """HTTP istekleri simüle etmek için test client'ı döndürür."""
    return app.test_client()
