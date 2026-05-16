"""
AhmetFarm - API Rotaları (v1)
==============================
Tüm rotalar '/api/v1' ön eki altında çalışır ve yalnızca JSON döner.
HTML şablonu render etmez; bu yüzden hem web hem de gelecekteki mobil
uygulamalar tarafından tüketilebilir.

Mevcut Uç Noktalar (Endpoints):
  GET  /api/v1/me              → Oturum açık kullanıcının profil özeti
  GET  /api/v1/plots           → Kullanıcının tüm tarla verisi (harita için)
  GET  /api/v1/inventory       → Kullanıcının envanter listesi
  POST /api/v1/avatar          → Avatar yükleme (multipart/form-data)

Güvenlik:
  @login_required  → Oturumu olmayan istekler 401 JSON hatası alır.
  CSRF             → POST isteklerinde X-CSRFToken header veya form field zorunludur.
"""

import os
from flask import jsonify, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.api import api_bp
from app.models import db, Plot, Inventory


# ==============================================================================
# KULLANICI İSTATİSTİKLERİ
# ==============================================================================

# API Endpoint - Dış sistemlere JSON veri sağlar
# Bu rota, oturum açık kullanıcının oyun istatistiklerini saf JSON formatında döner.
# HTML render etmez; doğrudan tarayıcıdan, mobil uygulamadan veya dış servislerden çağrılabilir.
# Örnek kullanım: GET /api/v1/stats → { "status": 200, "data": { ... } }
@api_bp.route('/stats')
def stats():
    """
    Oturum açık kullanıcının özet istatistiklerini döner.

    Kullanım: GET /api/v1/stats
    Yanıt (200): { "status": 200, "data": { username, level, xp, coins, sahip_olunan_tarla_sayisi, ... } }
    Yanıt (401): { "status": 401, "error": "Oturum açık değil." }
    """
    # Manuel oturum kontrolü — @login_required aksine JSON 401 döner (AJAX dostu)
    if not current_user.is_authenticated:
        return jsonify({
            'status': 401,
            'error': 'Oturum açık değil.'
        }), 401

    # Veritabanından is_owned=True olan tarla sayısını çek
    sahip_olunan_tarla_sayisi = Plot.query.filter_by(
        user_id=current_user.id,
        is_owned=True
    ).count()

    xp_required = current_user.level * 100
    xp_percent = round((current_user.xp / xp_required) * 100, 1) if xp_required else 0

    inventory_items = [i for i in current_user.inventory if i.quantity > 0]
    total_crops = sum(i.quantity for i in inventory_items)

    return jsonify({
        'status': 200,
        'data': {
            'username': current_user.username,
            'level': current_user.level,
            'xp': current_user.xp,
            'xp_required': xp_required,
            'xp_percent': xp_percent,
            'coins': current_user.coins,
            'sahip_olunan_tarla_sayisi': sahip_olunan_tarla_sayisi,
            'envanter_tur_sayisi': len(inventory_items),
            'toplam_urun_adedi': total_crops
        }
    }), 200


# ==============================================================================
# KULLANICI PROFİL ÖZETİ
# ==============================================================================
@api_bp.route('/me')
@login_required
def me():
    """
    Oturum açık kullanıcının profil bilgilerini döner.

    Kullanım: GET /api/v1/me
    Yanıt   : { id, username, level, xp, coins, avatar_url, plot_count }
    """
    plot_count = Plot.query.filter_by(user_id=current_user.id, is_owned=True).count()

    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'level': current_user.level,
        'xp': current_user.xp,
        'required_xp': current_user.level * 100,
        'coins': current_user.coins,
        'avatar_url': f'/static/uploads/avatars/{current_user.avatar_file}',
        'plot_count': plot_count
    })


# ==============================================================================
# TARLA LİSTESİ (Harita Verisi)
# ==============================================================================
@api_bp.route('/plots')
@login_required
def plots():
    """
    Kullanıcıya ait tüm parselleri (arazileri) JSON olarak döner.
    Leaflet.js haritasını beslemek için kullanılabilir.

    Kullanım: GET /api/v1/plots
    Yanıt   : { plots: [ { id, x, y, w, h, is_owned, state, ... } ] }
    """
    user_plots = Plot.query.filter_by(user_id=current_user.id).all()
    owned_count = sum(1 for p in user_plots if p.is_owned)

    plot_list = []
    for plot in user_plots:
        area = plot.width * plot.height
        plot_list.append({
            'id': plot.id,
            'x': plot.x_coord,
            'y': plot.y_coord,
            'w': plot.width,
            'h': plot.height,
            'is_owned': plot.is_owned,
            'state': plot.state,
            'crop_name': plot.crop.name if plot.crop else None,
            'time_remaining': plot.time_remaining,
            'grow_time': plot.crop.grow_time if plot.crop else 0,
            'cost': owned_count * 500 * area  # Dinamik satın alma fiyatı
        })

    return jsonify({'plots': plot_list})


# ==============================================================================
# ENVANTER LİSTESİ
# ==============================================================================
@api_bp.route('/inventory')
@login_required
def inventory():
    """
    Kullanıcının sahip olduğu ürünleri ve miktarlarını döner.

    Kullanım: GET /api/v1/inventory
    Yanıt   : { inventory: [ { crop_id, crop_name, quantity, sell_value } ] }
    """
    items = [item for item in current_user.inventory if item.quantity > 0]

    inventory_list = [{
        'id': item.id,
        'crop_id': item.crop_id,
        'crop_name': item.crop.name,
        'quantity': item.quantity,
        'sell_value': item.crop.harvest_value
    } for item in items]

    return jsonify({'inventory': inventory_list})


# ==============================================================================
# AVATAR YÜKLEME
# ==============================================================================
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'avatars')


@api_bp.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """
    Kullanıcının profil fotoğrafını yükler ve veritabanını günceller.

    Kullanım: POST /api/v1/avatar  (multipart/form-data, field adı: 'avatar')
    Yanıt   : { success, new_avatar_url }

    Güvenlik:
      - secure_filename() ile dizin geçişi (path traversal) saldırıları önlenir.
      - Yalnızca beyaz listedeki uzantılar kabul edilir.
      - Eski avatar (varsayılan değilse) diskten silinir.
    """
    if 'avatar' not in request.files:
        return jsonify({'error': 'Dosya bulunamadı.'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi.'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'error': f'Desteklenmeyen format. İzin verilenler: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    # Benzersiz ve güvenli dosya adı: user_5_avatar.jpg gibi
    filename = secure_filename(f'user_{current_user.id}_avatar.{ext}')
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    # Eski avatarı diskten temizle
    if current_user.avatar_file != 'default_avatar.png':
        old_path = os.path.join(UPLOAD_FOLDER, current_user.avatar_file)
        if os.path.exists(old_path):
            os.remove(old_path)

    file.save(save_path)
    current_user.avatar_file = filename
    db.session.commit()

    return jsonify({
        'success': True,
        'new_avatar_url': f'/static/uploads/avatars/{filename}'
    })
