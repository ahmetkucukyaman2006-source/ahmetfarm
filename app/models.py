from datetime import datetime, timezone
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    coins: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    inventory: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="user", cascade="all, delete-orphan")
    plots: Mapped[List["FarmPlot"]] = relationship("FarmPlot", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password, method='scrypt')

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Crop(db.Model):
    __tablename__ = 'crop'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    grow_time: Mapped[int] = mapped_column(Integer, nullable=False)  # In seconds
    seed_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    harvest_value: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    inventory_items: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="crop", cascade="all, delete-orphan")
    farm_plots: Mapped[List["FarmPlot"]] = relationship("FarmPlot", back_populates="crop", cascade="all, delete-orphan")


class Inventory(db.Model):
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    crop_id: Mapped[int] = mapped_column(ForeignKey('crop.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="inventory")
    crop: Mapped["Crop"] = relationship("Crop", back_populates="inventory_items")


class FarmPlot(db.Model):
    __tablename__ = 'farm_plot'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    crop_id: Mapped[Optional[int]] = mapped_column(ForeignKey('crop.id'), nullable=True)
    planted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_empty: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="plots")
    crop: Mapped[Optional["Crop"]] = relationship("Crop", back_populates="farm_plots")

from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
