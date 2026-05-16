from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user, login_required
from app.models import db, User
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.utils import generate_reset_token, verify_reset_token
from flask_mail import Message
from app.extensions import mail

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Geçersiz kullanıcı adı veya şifre', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Giriş Yap', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Tebrikler, başarıyla kayıt oldunuz! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Kayıt Ol', form=form)

@auth_bp.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        # Kullanıcıyı e-posta veya kullanıcı adına göre ara
        user = db.session.scalar(
            db.select(User).where(
                (User.email == form.email_or_username.data) | 
                (User.username == form.email_or_username.data)
            )
        )
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            # Gerçek e-posta gönderme mantığı
            msg = Message('AhmetFarm Şifre Sıfırlama Bağlantısı',
                          recipients=[user.email])
            msg.body = f'''Merhaba {user.username},

AhmetFarm hesabınız için şifre sıfırlama isteğinde bulundunuz. 
Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:

{reset_url}

Bu bağlantı 30 dakika boyunca geçerlidir.
Eğer bu isteği siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.
'''
            mail.send(msg)
            flash('Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.', 'success')
        else:
            # Güvenlik için kullanıcı bulunmasa bile aynı mesajı vermek daha iyidir
            # ama ödev/test kolaylığı için bulunamadı diyelim
            flash('Bu e-posta veya kullanıcı adı ile kayıtlı bir hesap bulunamadı.', 'error')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', title='Şifre Sıfırla', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    email = verify_reset_token(token)
    if email is None:
        flash('Şifre sıfırlama bağlantısı geçersiz veya süresi dolmuş.', 'error')
        return redirect(url_for('auth.login'))
        
    user = db.session.scalar(db.select(User).where(User.email == email))
    if user is None:
        flash('Kullanıcı bulunamadı.', 'error')
        return redirect(url_for('auth.login'))
        
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Şifreniz başarıyla güncellendi! Yeni şifrenizle giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', title='Yeni Şifre Belirle', form=form)
