from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from app.models import db, User

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    submit = SubmitField('Giriş Yap')

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[
        DataRequired(),
        Length(min=8, message="Şifre en az 8 karakter uzunluğunda olmalıdır."),
        Regexp(r'(?=.*[a-z])', message="Şifre en az bir küçük harf içermelidir."),
        Regexp(r'(?=.*[A-Z])', message="Şifre en az bir büyük harf içermelidir."),
        Regexp(r'(?=.*\d)', message="Şifre en az bir rakam içermelidir."),
        Regexp(r'(?=.*[@$!%*?&._-])', message="Şifre en az bir özel karakter (@$!%*?&._-) içermelidir.")
    ])
    confirm_password = PasswordField('Şifreyi Onayla', validators=[
        DataRequired(),
        EqualTo('password', message="Şifreler eşleşmiyor.")
    ])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        user = db.session.scalar(db.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Bu kullanıcı adı zaten alınmış. Lütfen farklı bir tane seçin.')

    def validate_email(self, email):
        user = db.session.scalar(db.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Bu e-posta adresi ile kayıtlı bir hesap zaten var.')
