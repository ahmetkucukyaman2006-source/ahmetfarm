from flask import render_template
from flask_login import login_required, current_user
from app.main import main_bp

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Dashboard')
