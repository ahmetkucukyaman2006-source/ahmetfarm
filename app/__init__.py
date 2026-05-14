from flask import Flask
from flask_migrate import Migrate
from config import Config
from app.models import db
from app.extensions import login_manager, csrf

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main.routes import main_bp
    app.register_blueprint(main_bp)

    return app
