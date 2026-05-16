"""
AhmetFarm - Veritabanı Modelleri (Database Models)
===================================================
Bu modül, SQLAlchemy ORM kullanılarak tanımlanmış tüm veritabanı tablolarını içerir.
Her Python sınıfı, veritabanındaki bir tabloya karşılık gelir. Flask-Login entegrasyonu
ile kullanıcı oturum yönetimi de bu katmanda gerçekleştirilir.

Veri Modeli İlişkileri:
  User  ──< Plot      : Bir kullanıcının birden fazla tarlası olabilir.
  User  ──< Inventory : Bir kullanıcının birden fazla envanter kalemi olabilir.
  User  ──< Machine   : Bir kullanıcının birden fazla üretim makinesi olabilir.
  Crop  ──< Plot      : Bir ürün türü birçok tarlada ekilmiş olabilir.
  Crop  ──< Inventory : Bir ürün türü birçok kullanıcının envanterinde olabilir.
  Recipe ──< Machine  : Bir tarif birçok makinede üretilebilir.
"""

from datetime import datetime, timezone
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy nesnesi; uygulamaya __init__.py içinde db.init_app(app) ile bağlanır.
db = SQLAlchemy()


# ==============================================================================
# KULLANICI MODELİ (Authentication & Authorization)
# ==============================================================================
class User(UserMixin, db.Model):
    """
    Kullanıcı tablosu. Flask-Login entegrasyonu için UserMixin miras alınmıştır.

    UserMixin, Flask-Login'in beklediği is_authenticated, is_active, get_id()
    gibi metotları otomatik olarak sağlar. Bu sayede @login_required dekoratörü
    ile korunan rotalara yalnızca giriş yapmış kullanıcılar erişebilir.

    Güvenlik Notu:
      Kullanıcı şifreleri veritabanına asla düz metin (plain-text) olarak
      kaydedilmez. Werkzeug kütüphanesinin 'scrypt' algoritmasıyla hash'lenerek
      saklanır. Giriş sırasında check_password_hash() ile doğrulama yapılır.
    """
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    # Şifre düz metin olarak değil, hash'lenmiş hali olarak saklanır.
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    coins: Mapped[int] = mapped_column(Integer, default=50, nullable=False)   # Başlangıç parası
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, server_default='0', nullable=False)
    # Kullanıcının profil fotoğrafı dosya adı. Dosyalar static/avatars/ klasöründe saklanır.
    avatar_file: Mapped[str] = mapped_column(String(128), default='default_avatar.png', server_default='default_avatar.png', nullable=False)

    # İlişkiler: cascade="all, delete-orphan" → Kullanıcı silinirse ilişkili kayıtlar da silinir.
    inventory: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="user", cascade="all, delete-orphan")
    plots: Mapped[List["Plot"]] = relationship("Plot", back_populates="user", cascade="all, delete-orphan")
    machines: Mapped[List["Machine"]] = relationship("Machine", back_populates="user", cascade="all, delete-orphan")

    def add_xp(self, amount: int) -> bool:
        """
        Kullanıcıya XP ekler ve seviye atlanıp atlanmadığını kontrol eder.

        Seviye atlama formülü: Her seviye için gereken XP = mevcut_seviye * 100
        Birden fazla seviye aynı anda atlanabilir (while döngüsü ile).

        Args:
            amount: Eklenecek XP miktarı.

        Returns:
            bool: Seviye atlandıysa True, atlanmadıysa False.
        """
        self.xp += amount
        leveled_up = False
        while True:
            required_xp = self.level * 100  # Örn: Seviye 3 için 300 XP gerekir
            if self.xp >= required_xp:
                self.xp -= required_xp       # Fazla XP bir sonraki seviyeye aktarılır
                self.level += 1
                leveled_up = True
            else:
                break
        return leveled_up

    def set_password(self, password: str) -> None:
        """
        Verilen şifreyi 'scrypt' algoritmasıyla hash'leyerek veritabanına kaydeder.
        Hiçbir zaman şifrenin kendisi saklanmaz.
        """
        self.password_hash = generate_password_hash(password, method='scrypt')

    def check_password(self, password: str) -> bool:
        """
        Giriş sırasında kullanıcının girdiği şifreyi, veritabanındaki hash ile karşılaştırır.
        Doğruysa True, yanlışsa False döner.
        """
        return check_password_hash(self.password_hash, password)


# ==============================================================================
# ÜRÜN MODELİ (Ekilebilir ve İşlenebilir Ürünler)
# ==============================================================================
class Crop(db.Model):
    """
    Oyundaki tüm ürün türlerini tanımlar. Hem tarla ürünleri (Domates, Buğday)
    hem de fabrika çıktıları (Un, Salça) bu tabloda saklanır.

    Fabrika çıktıları için seed_cost=0 ve grow_time=0 değerleri kullanılır;
    bu sayede tarlaya ekilemezler, yalnızca envanterde taşınırlar.
    """
    __tablename__ = 'crop'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    grow_time: Mapped[int] = mapped_column(Integer, nullable=False)      # Büyüme süresi (saniye cinsinden)
    seed_cost: Mapped[int] = mapped_column(Integer, nullable=False)      # Tohum maliyeti (coin)
    harvest_value: Mapped[int] = mapped_column(Integer, nullable=False)  # Pazar satış değeri (coin)
    unlock_level: Mapped[int] = mapped_column(Integer, default=1, server_default='1', nullable=False)  # Kilit açma seviyesi

    inventory_items: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="crop", cascade="all, delete-orphan")
    plots: Mapped[List["Plot"]] = relationship("Plot", back_populates="crop", cascade="all, delete-orphan")


# ==============================================================================
# ENVANTER MODELİ (CRUD: Create/Update/Delete)
# ==============================================================================
class Inventory(db.Model):
    """
    Kullanıcı-Ürün arasındaki N:N ilişkiyi çözen ara tablo (junction table).
    Her kayıt; hangi kullanıcının, hangi üründen, kaç adet sahip olduğunu tutar.

    CRUD İşlemleri:
      - CREATE: Hasat sırasında yeni ürün ilk defa elde edildiğinde oluşturulur.
      - READ  : Pazar ve envanter sayfasında listelenir.
      - UPDATE: Hasat veya fabrika toplamasında quantity artırılır; satışta azaltılır.
      - DELETE: Miktar 0'a düştüğünde kayıt veritabanından silinir (Pazar satışı).
    """
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    crop_id: Mapped[int] = mapped_column(ForeignKey('crop.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="inventory")
    crop: Mapped["Crop"] = relationship("Crop", back_populates="inventory_items")


# ==============================================================================
# TARLA MODELİ (Coğrafi Harita Sistemi)
# ==============================================================================
class Plot(db.Model):
    """
    Aydın/Söke haritasında her bir arazi parselini temsil eder.

    Koordinat ve Boyut Sistemi:
      - x_coord, y_coord: Harita üzerindeki ızgara konumu (0'dan başlar).
      - width, height   : Tarlanın kaç hücre kapladığı (dönüm çarpanı = width * height).
      - is_owned        : Kullanıcının bu araziyi satın alıp almadığı.

    Durum Makinesi (State Machine):
      empty → planted → ready → empty (hasat sonrası sıfırlanır)

    Dinamik Hesaplama:
      time_remaining ve is_ready özellikleri veritabanına kaydedilmez.
      Her çağrıda UTC zaman damgasına göre gerçek zamanlı hesaplanır.
      Bu sayede sunucu yeniden başlasa bile sayaçlar doğru çalışmaya devam eder.
    """
    __tablename__ = 'plot'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    crop_id: Mapped[Optional[int]] = mapped_column(ForeignKey('crop.id'), nullable=True)  # Ekim yapılmamışsa None
    planted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)       # UTC zaman damgası
    state: Mapped[str] = mapped_column(String(20), default='empty', nullable=False)       # 'empty' | 'planted' | 'ready'
    x_coord: Mapped[int] = mapped_column(Integer, default=0, server_default='0', nullable=False)
    y_coord: Mapped[int] = mapped_column(Integer, default=0, server_default='0', nullable=False)
    width: Mapped[int] = mapped_column(Integer, default=1, server_default='1', nullable=False)
    height: Mapped[int] = mapped_column(Integer, default=1, server_default='1', nullable=False)
    is_owned: Mapped[bool] = mapped_column(Boolean, default=False, server_default='0', nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="plots")
    crop: Mapped[Optional["Crop"]] = relationship("Crop", back_populates="plots")

    @property
    def is_ready(self) -> bool:
        """
        Tarlada büyüme süresinin dolup dolmadığını anlık olarak hesaplar.
        UTC zaman farkı, ekin büyüme süresine (crop.grow_time) ulaştıysa True döner.
        """
        if self.state != 'planted' or not self.planted_at or not self.crop:
            return False
        planted_utc = self.planted_at.replace(tzinfo=timezone.utc)
        time_passed = (datetime.now(timezone.utc) - planted_utc).total_seconds()
        return time_passed >= self.crop.grow_time

    @property
    def time_remaining(self) -> int:
        """
        Frontend'e gönderilecek kalan saniyeyi anlık hesaplar.
        Süre dolduysa 0 döner (negatif değer olmaz).
        """
        if self.state != 'planted' or not self.planted_at or not self.crop:
            return 0
        planted_utc = self.planted_at.replace(tzinfo=timezone.utc)
        time_passed = (datetime.now(timezone.utc) - planted_utc).total_seconds()
        remaining = self.crop.grow_time - time_passed
        return int(max(0, remaining))

    def update_state(self):
        """
        Tarlanın durumunu kontrol edip gerekirse 'ready' olarak günceller.
        Sayfa yüklenirken ve hasat öncesinde çağrılarak veri tutarsızlığı önlenir.
        """
        if self.state == 'planted' and self.is_ready:
            self.state = 'ready'


# ==============================================================================
# TARİF MODELİ (Fabrika Üretim Tarifleri)
# ==============================================================================
class Recipe(db.Model):
    """
    Fabrika tesislerinde hangi ham maddenin hangi ürüne dönüştürüleceğini tanımlar.

    Örnek: 'Salça Üretimi' → 3x Domates (malzeme) → 1x Salça (çıktı), 45 saniyede
    required_machine_type: 'basic' (standart tesis) veya 'royal' (Kraliyet Atölyesi)
    """
    __tablename__ = 'recipe'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    result_item_id: Mapped[int] = mapped_column(ForeignKey('crop.id'), nullable=False)      # Üretilen ürün
    ingredient_item_id: Mapped[int] = mapped_column(ForeignKey('crop.id'), nullable=False)  # Gereken ham madde
    req_amount: Mapped[int] = mapped_column(Integer, nullable=False)        # Gereken ham madde miktarı
    craft_time: Mapped[int] = mapped_column(Integer, nullable=False)        # Üretim süresi (saniye)
    unlock_level: Mapped[int] = mapped_column(Integer, default=1, server_default='1', nullable=False)
    required_machine_type: Mapped[str] = mapped_column(String(50), default='basic', server_default='basic', nullable=False)

    result_item: Mapped["Crop"] = relationship("Crop", foreign_keys=[result_item_id])
    ingredient_item: Mapped["Crop"] = relationship("Crop", foreign_keys=[ingredient_item_id])
    machines: Mapped[List["Machine"]] = relationship("Machine", back_populates="recipe")


# ==============================================================================
# MAKİNE MODELİ (Fabrika Tesisleri)
# ==============================================================================
class Machine(db.Model):
    """
    Kullanıcıya ait üretim makinelerini temsil eder.

    Durum Makinesi:
      idle → crafting → ready → idle (ürün toplandıktan sonra sıfırlanır)

    machine_type:
      'basic' → Standart üretim tesisi (Un, Salça, Reçel)
      'royal' → Kraliyet Çikolata Atölyesi (Lvl 25 kilit, 10.000 coin maliyet)
    """
    __tablename__ = 'machine'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    recipe_id: Mapped[Optional[int]] = mapped_column(ForeignKey('recipe.id'), nullable=True)  # Aktif tarif; boştayken None
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)           # UTC başlangıç zamanı
    state: Mapped[str] = mapped_column(String(20), default='idle', nullable=False)            # 'idle' | 'crafting' | 'ready'
    machine_type: Mapped[str] = mapped_column(String(50), default='basic', server_default='basic', nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="machines")
    recipe: Mapped[Optional["Recipe"]] = relationship("Recipe", back_populates="machines")

    @property
    def is_ready(self) -> bool:
        """Makinenin üretim süresinin dolup dolmadığını anlık hesaplar."""
        if self.state != 'crafting' or not self.started_at or not self.recipe:
            return False
        started_utc = self.started_at.replace(tzinfo=timezone.utc)
        time_passed = (datetime.now(timezone.utc) - started_utc).total_seconds()
        return time_passed >= self.recipe.craft_time

    @property
    def time_remaining(self) -> int:
        """Frontend'e gönderilecek kalan üretim süresini (saniye) hesaplar."""
        if self.state != 'crafting' or not self.started_at or not self.recipe:
            return 0
        started_utc = self.started_at.replace(tzinfo=timezone.utc)
        time_passed = (datetime.now(timezone.utc) - started_utc).total_seconds()
        remaining = self.recipe.craft_time - time_passed
        return int(max(0, remaining))

    def update_state(self):
        """Makine durumunu kontrol edip gerekirse 'ready' olarak günceller."""
        if self.state == 'crafting' and self.is_ready:
            self.state = 'ready'


# ==============================================================================
# FLASK-LOGIN: KULLANICI YÜKLEYİCİ
# ==============================================================================
# Flask-Login, oturum çerezinde yalnızca user_id saklar.
# Her istekte bu fonksiyon çağrılarak ilgili User nesnesi veritabanından yüklenir.
# @login_required dekoratörü, bu yükleyiciyi kullanarak kullanıcının kim olduğunu doğrular.
from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
