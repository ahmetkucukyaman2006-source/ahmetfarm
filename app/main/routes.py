"""
AhmetFarm - Ana Oyun Rotaları (Main Blueprint)
===============================================
Bu modül, oyunun tüm iş mantığını (game logic) içeren HTTP rotalarını tanımlar.
Blueprint deseni ile auth modülünden ayrıştırılmıştır.

CRUD Karşılıkları:
  CREATE → /plant      : Tarlaya ekim (yeni kayıt: planted_at, crop_id)
  READ   → /           : Harita verisi (tüm Plot kayıtlarını okuma)
  UPDATE → /harvest    : Hasat (Plot.state güncelleme + Inventory artırma)
  DELETE → /sell       : Pazar satışı (Inventory.quantity = 0 ise kayıt silme)

Dinamik Güncelleme (AJAX/Fetch):
  Tüm POST rotaları JSON döner. Frontend, bu yanıtla sayfayı yenilemeden (no-reload)
  yalnızca ilgili DOM öğesini (Leaflet poligonu veya HTML kartı) günceller.

Güvenlik:
  @login_required  → Oturumu olmayan kullanıcı /auth/login'e yönlendirilir.
  plot.user_id != current_user.id  → Başka kullanıcının verisine erişim engellenir.
  Flask-WTF CSRF  → Tüm POST isteklerinde X-CSRFToken header zorunludur.
"""

from flask import render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from app.main import main_bp
from app.models import db, Crop, Plot, Inventory
from datetime import datetime, timezone
import random


# ==============================================================================
# DİL DEĞİŞTİRME ROTASI
# ==============================================================================
@main_bp.route('/set_lang/<lang>')
def set_lang(lang):
    """
    Kullanıcının dil tercihini oturuma (session) kaydeder.

    session['lang'] → get_locale() fonksiyonu tarafından her istekte okunur.
    Flask-Babel bu değere göre aktif çeviri dilini seçer.

    Desteklenen diller: 'tr' (Türkçe), 'en' (İngilizce)
    Kullanım: <a href="/set_lang/en">EN</a>
    """
    if lang in ('tr', 'en'):
        session['lang'] = lang
        session.permanent = True  # Tarayıcı kapansa da dil tercihini koru
    # Kullanıcıyı geldiği sayfaya geri gönder; referrer yoksa ana sayfaya
    return redirect(request.referrer or url_for('main.index'))


# ==============================================================================
# DASHBOARD / HARITA ROTASI (READ)
# ==============================================================================
@main_bp.route('/')
@main_bp.route('/index')
@login_required  # Oturum yoksa /auth/login'e yönlendir
def index():
    """
    Ana harita sayfasını yükler ve kullanıcının tüm arazi verilerini hazırlar.

    İlk Giriş (Seeding):
      - Veritabanında hiç ürün yoksa temel ürünler ve tarifler oluşturulur.
      - Kullanıcının hiç tarlası yoksa Aydın/Söke haritası şablonuna göre
        parseller oluşturulur: 4 adet ücretsiz (is_owned=True) başlangıç tarlası
        ve satın alınabilir büyük araziler (is_owned=False).

    Sayfa Yüklenirken Durum Güncelleme:
      Sayfa yenilendiğinde, büyüme süresi dolmuş tüm 'planted' tarlalar
      anlık olarak 'ready' durumuna geçirilir. Bu sayede kullanıcı sayfayı
      açar açmaz 'Hasat Et' butonu hazır görünür.

    Returns:
        Rendered HTML: index.html + plots ve crops verisi
    """
    from app.models import Recipe, Machine

    # --- VERİTABANI BAŞLANGIÇ VERİSİ (Seed Data) ---
    # Uygulama ilk çalıştığında ürün tablosu boşsa temel ürünler eklenir.
    if Crop.query.count() == 0:
        c1 = Crop(name='Domates', grow_time=60, seed_cost=10, harvest_value=25, unlock_level=2)
        c2 = Crop(name='Buğday', grow_time=120, seed_cost=5, harvest_value=15, unlock_level=1)
        c3 = Crop(name='Çilek', grow_time=180, seed_cost=25, harvest_value=70, unlock_level=5)
        c4 = Crop(name='Altın Kakao', grow_time=600, seed_cost=5000, harvest_value=15000, unlock_level=20)
        db.session.add_all([c1, c2, c3, c4])
        db.session.commit()

    # Fabrika tarifleri ve işlenmiş ürünler ilk girişte oluşturulur.
    if Recipe.query.count() == 0:
        bugday = Crop.query.filter_by(name='Buğday').first()
        domates = Crop.query.filter_by(name='Domates').first()
        cilek = Crop.query.filter_by(name='Çilek').first()
        # İşlenmiş ürünler (seed_cost=0 → tarlaya ekilemez, yalnızca fabrika çıktısı)
        un = Crop(name='Un', grow_time=0, seed_cost=0, harvest_value=50, unlock_level=1)
        salca = Crop(name='Salça', grow_time=0, seed_cost=0, harvest_value=90, unlock_level=2)
        recel = Crop(name='Çilek Reçeli', grow_time=0, seed_cost=0, harvest_value=180, unlock_level=5)
        ciko = Crop(name='Kraliyet Çikolatası', grow_time=0, seed_cost=0, harvest_value=50000, unlock_level=25)
        db.session.add_all([un, salca, recel, ciko])
        db.session.commit()
        kakao = Crop.query.filter_by(name='Altın Kakao').first()
        r1 = Recipe(name='Un Üretimi', result_item_id=un.id, ingredient_item_id=bugday.id, req_amount=2, craft_time=30, unlock_level=1, required_machine_type='basic')
        r2 = Recipe(name='Salça Üretimi', result_item_id=salca.id, ingredient_item_id=domates.id, req_amount=3, craft_time=45, unlock_level=2, required_machine_type='basic')
        r3 = Recipe(name='Çilek Reçeli', result_item_id=recel.id, ingredient_item_id=cilek.id, req_amount=2, craft_time=60, unlock_level=5, required_machine_type='basic')
        db.session.add_all([r1, r2, r3])
        if kakao:
            r4 = Recipe(name='Kraliyet Çikolatası Üretimi', result_item_id=ciko.id, ingredient_item_id=kakao.id, req_amount=3, craft_time=1800, unlock_level=25, required_machine_type='royal')
            db.session.add(r4)
        db.session.commit()

    # Kullanıcının hiç tarlası yoksa Söke Ovası harita şablonu oluşturulur.
    # Format: (x_coord, y_coord, width, height, is_owned)
    if len(current_user.plots) == 0:
        map_template = [
            (0, 0, 2, 2, False), # Sol üst devasa orman (4 dönüm)
            (2, 0, 3, 1, False), # Sağ üst uzun tarla (3 dönüm)
            (0, 2, 1, 3, False), # Sol alt nehir/sera (3 dönüm)
            (1, 2, 1, 1, False),
            (2, 1, 3, 1, False),
            (2, 2, 1, 1, True),  # Merkez başlangıç (1 dönüm - ücretsiz)
            (3, 2, 1, 1, True),  # Merkez başlangıç (1 dönüm - ücretsiz)
            (2, 3, 1, 1, True),  # Merkez başlangıç (1 dönüm - ücretsiz)
            (3, 3, 1, 1, True),  # Merkez başlangıç (1 dönüm - ücretsiz)
            (4, 2, 1, 2, False), # Sağ dikey tarla
            (1, 3, 1, 2, False),
            (2, 4, 2, 1, False),
            (4, 4, 1, 1, False)
        ]
        for x, y, w, h, owned in map_template:
            new_plot = Plot(user_id=current_user.id, state='empty', x_coord=x, y_coord=y, width=w, height=h, is_owned=owned)
            db.session.add(new_plot)
        db.session.commit()

    # Yeni kullanıcıya 2 adet temel üretim makinesi verilir.
    if len(current_user.machines) == 0:
        for _ in range(2):
            new_machine = Machine(user_id=current_user.id, state='idle')
            db.session.add(new_machine)
        db.session.commit()

    # --- SAYFA YÜKLENİRKEN DURUM GÜNCELLEME ---
    # Kullanıcı sayfayı kapattıktan sonra ekin büyümüş olabilir.
    # Her yüklemede tüm 'planted' tarlalar kontrol edilip gerekirse 'ready' yapılır.
    plots = Plot.query.filter_by(user_id=current_user.id).all()
    needs_commit = False
    for plot in plots:
        if plot.state == 'planted' and plot.is_ready:
            plot.update_state()
            needs_commit = True
    if needs_commit:
        db.session.commit()

    # seed_cost > 0 → Yalnızca tarlaya ekilebilir ürünler listelenir (fabrika çıktıları hariç)
    crops = Crop.query.filter(Crop.seed_cost > 0).all()
    return render_template('index.html', title='Dashboard', plots=plots, crops=crops)


# ==============================================================================
# TESİSLER ROTASI (READ)
# ==============================================================================
@main_bp.route('/factory')
@login_required
def factory():
    """Kullanıcının fabrika makinelerini ve mevcut tarifleri listeler."""
    from app.models import Machine, Recipe
    machines = Machine.query.filter_by(user_id=current_user.id).all()
    recipes = Recipe.query.all()
    # Kraliyet Atölyesi var mı? Şablonda özel bölüm göstermek için kullanılır.
    has_royal = any(m.machine_type == 'royal' for m in machines)
    return render_template('factory.html', title='Tesisler', machines=machines, recipes=recipes, has_royal=has_royal)


# ==============================================================================
# EKİM ROTASI (CREATE - AJAX)
# ==============================================================================
@main_bp.route('/plant/<int:plot_id>', methods=['POST'])
@login_required
def plant(plot_id):
    """
    Belirtilen tarlaya tohum eker. (CRUD: CREATE işlemi)

    Frontend, JavaScript Fetch API ile bu rotaya JSON body gönderir.
    Başarılı yanıt alındığında sayfa yenilenmez; Leaflet poligonu anlık
    olarak sarıya (ekili) dönüştürülür ve geri sayım başlatılır.

    Dönüm Çarpanı:
      Geniş arazilerde (örn: 2x2=4 dönüm) tohum maliyeti 4 katına çıkar.
      Bu, büyük arazi yatırımını dengeler.

    Doğrulama:
      - Tarla boş (empty) olmalı
      - Kullanıcı yeterli bakiyeye sahip olmalı
      - Ürün seviye kilidini aşmış olmalı
      - Tarla kullanıcıya ait olmalı (yetkilendirme kontrolü)
    """
    plot = Plot.query.get_or_404(plot_id)

    # Yetkilendirme: Başka kullanıcının tarlasına ekim engellenir
    if plot.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    if plot.state != 'empty':
        return jsonify({'error': 'Tarla boş değil'}), 400

    data = request.get_json()
    crop_id = data.get('crop_id')
    if not crop_id:
        return jsonify({'error': 'Geçersiz tohum'}), 400

    crop = Crop.query.get_or_404(crop_id)

    # Dönüm bazlı maliyet hesabı: küçük arazi ucuz, büyük arazi pahalı
    area = plot.width * plot.height
    total_cost = crop.seed_cost * area

    if current_user.coins < total_cost:
        return jsonify({'error': f'Yetersiz bakiye! Bu geniş arazi ({area}x) için {total_cost} 🪙 gerekiyor.'}), 400
    if current_user.level < crop.unlock_level:
        return jsonify({'error': f'Bu tohum için Seviye {crop.unlock_level} gerekiyor.'}), 400

    # --- VERİTABANI YAZMA (UPDATE) ---
    current_user.coins -= total_cost
    plot.crop_id = crop.id
    plot.state = 'planted'
    plot.planted_at = datetime.now(timezone.utc)  # UTC zaman damgası; büyüme hesaplaması için
    db.session.commit()

    # JSON yanıtı: Frontend bu verilerle sayfayı yenilemeden haritayı günceller
    return jsonify({
        'success': True,
        'message': f'{crop.name} başarıyla ekildi!',
        'state': plot.state,
        'crop_name': crop.name,
        'grow_time': crop.grow_time,
        'time_remaining': plot.time_remaining,
        'new_coins': current_user.coins
    })


# ==============================================================================
# HASAT ROTASI (UPDATE - AJAX)
# ==============================================================================
@main_bp.route('/harvest/<int:plot_id>', methods=['POST'])
@login_required
def harvest(plot_id):
    """
    Olgunlaşmış ürünü hasat eder. (CRUD: UPDATE işlemi)

    Dönüm Çarpanı ile Hasat Hesabı:
      Her 1 dönümden 8-15 arası rastgele ürün çıkar. Tarlanın alanıyla çarpılır.
      Örnek: 4 dönüm × 12 = 48 adet Domates

    Sonuçlar:
      - Envanter güncellenir (CREATE veya UPDATE)
      - Tarla boşaltılır: state='empty', crop_id=None, planted_at=None
      - Kullanıcıya XP eklenir; seviye atlanabilir
    """
    plot = Plot.query.get_or_404(plot_id)
    if plot.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Sunucu tarafında da durum kontrolü yapılır (AJAX çağrısı atlanmış olabilir)
    plot.update_state()
    if plot.state != 'ready':
        return jsonify({'error': 'Bu tarla henüz hasada hazır değil.'}), 400

    crop = plot.crop
    if not crop:
        return jsonify({'error': 'Tarlada ürün bulunamadı.'}), 400

    # Dönüm bazlı verim hesabı
    area = plot.width * plot.height
    base_yield = random.randint(8, 15)   # 1 dönüm için taban verim
    yield_amount = base_yield * area     # Toplam verim = taban × alan

    # Envanter güncelleme: Zaten varsa quantity artır, yoksa yeni kayıt oluştur
    inventory_item = Inventory.query.filter_by(user_id=current_user.id, crop_id=crop.id).first()
    if inventory_item:
        inventory_item.quantity += yield_amount   # UPDATE
    else:
        inventory_item = Inventory(user_id=current_user.id, crop_id=crop.id, quantity=yield_amount)
        db.session.add(inventory_item)            # CREATE

    # Tarlayı sıfırla (boş duruma getir)
    plot.state = 'empty'
    plot.crop_id = None
    plot.planted_at = None

    # XP hesabı: ürün değeri × alan (büyük tarla → daha çok XP)
    xp_gained = crop.harvest_value * area
    leveled_up = current_user.add_xp(xp_gained)
    db.session.commit()

    msg = f'{yield_amount}x {crop.name} envantere eklendi! (+{xp_gained} XP)'
    if leveled_up:
        msg += f' 🎉 TEBRİKLER! Seviye {current_user.level} oldun!'

    return jsonify({
        'success': True,
        'message': msg,
        'state': plot.state,
        'new_xp': current_user.xp,
        'new_level': current_user.level,
        'required_xp': current_user.level * 100
    })


# ==============================================================================
# PAZAR / SATIŞ ROTASI (DELETE - AJAX)
# ==============================================================================
@main_bp.route('/market')
@login_required
def market():
    """Kullanıcının satılabilir envanter kalemlerini listeler."""
    inventory_items = [item for item in current_user.inventory if item.quantity > 0]
    return render_template('market.html', title='Pazar', inventory=inventory_items)


@main_bp.route('/sell/<int:inventory_id>', methods=['POST'])
@login_required
def sell(inventory_id):
    """
    Envanterdeki 1 adet ürünü pazar fiyatından satar. (CRUD: DELETE işlemi)

    Miktar 0'a düştüğünde envanter kaydı veritabanından tamamen silinir.
    Bu, veritabanını gereksiz sıfır-miktarlı kayıtlardan temiz tutar.
    """
    item = Inventory.query.get_or_404(inventory_id)
    if item.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    if item.quantity <= 0:
        return jsonify({'error': 'Yetersiz miktar'}), 400

    sell_price = item.crop.harvest_value
    item.quantity -= 1
    current_user.coins += sell_price

    # Miktar 0 ise kayıt silinir (DELETE)
    if item.quantity == 0:
        db.session.delete(item)

    db.session.commit()
    return jsonify({
        'success': True,
        'message': f'1x {item.crop.name} satıldı!',
        'new_coins': current_user.coins,
        'new_quantity': item.quantity
    })


# ==============================================================================
# FABRİKA ÜRETİM ROTALARI (CREATE / UPDATE - AJAX)
# ==============================================================================
@main_bp.route('/craft/<int:machine_id>', methods=['POST'])
@login_required
def craft(machine_id):
    """
    Fabrika makinesinde yeni bir üretim başlatır.

    Ön Koşullar:
      - Makine boşta (idle) olmalı
      - Tarif makine tipine uygun olmalı (basic / royal)
      - Yeterli ham madde envanterde bulunmalı
      - Seviye kilidi aşılmış olmalı
    """
    from app.models import Machine, Recipe
    machine = Machine.query.get_or_404(machine_id)
    if machine.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    if machine.state != 'idle':
        return jsonify({'error': 'Makine şu an meşgul.'}), 400

    data = request.get_json()
    recipe_id = data.get('recipe_id')
    recipe = Recipe.query.get_or_404(recipe_id)

    if recipe.required_machine_type != machine.machine_type:
        return jsonify({'error': 'Bu tarif bu makinede üretilemez!'}), 400
    if current_user.level < recipe.unlock_level:
        return jsonify({'error': f'Bu tarif için Seviye {recipe.unlock_level} gerekiyor.'}), 400

    # Envanterdeki ham madde kontrolü
    inv_item = Inventory.query.filter_by(user_id=current_user.id, crop_id=recipe.ingredient_item_id).first()
    if not inv_item or inv_item.quantity < recipe.req_amount:
        return jsonify({'error': f'Yetersiz malzeme! {recipe.req_amount}x {recipe.ingredient_item.name} gerekiyor.'}), 400

    # Ham maddeyi düş, üretimi başlat
    inv_item.quantity -= recipe.req_amount
    machine.recipe_id = recipe.id
    machine.state = 'crafting'
    machine.started_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'{recipe.name} başladı!',
        'state': machine.state,
        'recipe_name': recipe.name,
        'craft_time': recipe.craft_time,
        'time_remaining': machine.time_remaining
    })


@main_bp.route('/collect/<int:machine_id>', methods=['POST'])
@login_required
def collect(machine_id):
    """Üretimi tamamlanan ürünü makineden alır ve envantere ekler."""
    from app.models import Machine
    machine = Machine.query.get_or_404(machine_id)
    if machine.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    machine.update_state()
    if machine.state != 'ready':
        return jsonify({'error': 'Üretim henüz tamamlanmadı.'}), 400

    recipe = machine.recipe
    inv_item = Inventory.query.filter_by(user_id=current_user.id, crop_id=recipe.result_item_id).first()
    if inv_item:
        inv_item.quantity += 1
    else:
        inv_item = Inventory(user_id=current_user.id, crop_id=recipe.result_item_id, quantity=1)
        db.session.add(inv_item)

    # Makineyi sıfırla
    machine.state = 'idle'
    machine.recipe_id = None
    machine.started_at = None

    xp_gained = max(1, recipe.result_item.harvest_value // 2)
    leveled_up = current_user.add_xp(xp_gained)
    db.session.commit()

    msg = f'1x {recipe.result_item.name} toplandı! (+{xp_gained} XP)'
    if leveled_up:
        msg += f' 🎉 TEBRİKLER! Seviye {current_user.level} oldun!'

    return jsonify({
        'success': True,
        'message': msg,
        'state': machine.state,
        'new_xp': current_user.xp,
        'new_level': current_user.level,
        'required_xp': current_user.level * 100
    })


# ==============================================================================
# KRALİYET ATÖLYESİ İNŞASI (CREATE - AJAX)
# ==============================================================================
@main_bp.route('/build_factory', methods=['POST'])
@login_required
def build_factory():
    """
    Seviye 25 ve 10.000 coin karşılığında Kraliyet Çikolata Atölyesi inşa eder.
    Başarı durumunda yeni makinenin ID'si döner; frontend sayfa yenilemeden
    dinamik olarak yeni makine kartını DOM'a ekler.
    """
    from app.models import Machine
    if current_user.level < 25:
        return jsonify({'error': 'Bu tesis için Seviye 25 gerekiyor!'}), 400
    if current_user.coins < 10000:
        return jsonify({'error': 'Yetersiz bakiye! 10.000 🪙 gerekiyor.'}), 400

    existing = Machine.query.filter_by(user_id=current_user.id, machine_type='royal').first()
    if existing:
        return jsonify({'error': 'Bu tesis zaten inşa edilmiş!'}), 400

    current_user.coins -= 10000
    royal_machine = Machine(user_id=current_user.id, machine_type='royal')
    db.session.add(royal_machine)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Kraliyet Çikolata Atölyesi inşa edildi! 🏰',
        'new_coins': current_user.coins,
        'machine_id': royal_machine.id  # Frontend'in DOM'a kart eklemesi için gerekli
    })


# ==============================================================================
# ARAZİ SATIN ALMA ROTASI (UPDATE - AJAX)
# ==============================================================================
@main_bp.route('/buy_plot/<int:plot_id>', methods=['POST'])
@login_required
def buy_plot(plot_id):
    """
    Sahiplenilmemiş (is_owned=False) bir araziyi satın alır.

    Dinamik Fiyatlandırma:
      Fiyat = sahip_olunan_tarla_sayısı × 500 × arazi_alanı
      Daha fazla arazi satın aldıkça yeni araziler daha pahalı olur.

    Başarı durumunda frontend, sayfayı yenilemeden araziyi anlık yeşile çevirir.
    """
    plot = Plot.query.get_or_404(plot_id)
    if plot.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    if plot.is_owned:
        return jsonify({'error': 'Bu arazi zaten sizin.'}), 400

    owned_count = Plot.query.filter_by(user_id=current_user.id, is_owned=True).count()
    area = plot.width * plot.height
    cost = owned_count * 500 * area

    if current_user.coins < cost:
        return jsonify({'error': f'Yetersiz bakiye! Bu devasa arazi için {cost} 🪙 gerekiyor.'}), 400

    current_user.coins -= cost
    plot.is_owned = True
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Yeni arazi satın alındı!',
        'new_coins': current_user.coins
    })


# ==============================================================================
# PROFİL SAYFASI (READ)
# ==============================================================================
@main_bp.route('/profile')
@login_required
def profile():
    """
    Kullanıcı profil sayfasını gösterir.
    İstatistikler (seviye, para, tarla sayısı) şablona aktarılır.
    """
    # Kullanıcıya ait sahiplenilmiş tarla sayısı
    plot_count = Plot.query.filter_by(user_id=current_user.id, is_owned=True).count()
    return render_template('profile.html', title='Profil', plot_count=plot_count)


# ==============================================================================
# AVATAR YÜKLEME ROTASI (UPDATE - AJAX / multipart form)
# ==============================================================================
@main_bp.route('/profile/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    """
    Kullanıcının profil fotoğrafını yükler ve User.avatar_file sütununu günceller.

    Güvenlik Kontrolleri:
      - Yalnızca izin verilen uzantılar kabul edilir (png, jpg, jpeg, gif, webp).
      - Dosya adı güvenli hale getirilir (werkzeug.secure_filename).
      - Eski avatar (default değilse) diskten silinir.

    Dosya adı: user_{id}_avatar.{uzantı} formatında kaydedilir.
    Konum   : static/uploads/avatars/
    """
    import os
    from werkzeug.utils import secure_filename

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'avatars')

    if 'avatar' not in request.files:
        return jsonify({'error': 'Dosya bulunamadı.'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi.'}), 400

    # Uzantı kontrolü
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'error': f'Desteklenmeyen format. İzin verilenler: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    # Güvenli, benzersiz dosya adı oluştur
    filename = secure_filename(f'user_{current_user.id}_avatar.{ext}')
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    # Eski avatarı sil (varsayılan değilse)
    if current_user.avatar_file != 'default_avatar.png':
        old_path = os.path.join(UPLOAD_FOLDER, current_user.avatar_file)
        if os.path.exists(old_path):
            os.remove(old_path)

    # Yeni dosyayı kaydet ve veritabanını güncelle
    file.save(save_path)
    current_user.avatar_file = filename
    db.session.commit()

    # Frontend'e yeni avatar URL'ini döndür (sayfayı yenilemeden güncellemek için)
    new_avatar_url = f'/static/uploads/avatars/{filename}'
    return jsonify({
        'success': True,
        'message': 'Avatar güncellendi!',
        'new_avatar_url': new_avatar_url
    })
