from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from flask_mail import Mail

# Flask-Login: Oturum yönetimi ve @login_required koruması
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Lütfen bu sayfaya erişmek için giriş yapın.'
login_manager.login_message_category = 'warning'

# Flask-WTF: Tüm POST isteklerine CSRF token koruması
csrf = CSRFProtect()

# Flask-Babel: Çok dilli destek (i18n) ve yerel tarih/sayı biçimlendirme
babel = Babel()

# Flask-Mail: E-posta gönderme
mail = Mail()
