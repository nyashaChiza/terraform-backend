from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base
from app.models.enums import EquipmentCategory


class Equipment(Base):
    __tablename__ = "equipment"

    id          = Column(Integer, primary_key=True)
    name        = Column(String(255), nullable=False, unique=True)
    category    = Column(Enum(EquipmentCategory, native_enum=False), nullable=False)
    is_bodyweight = Column(Boolean, default=False, nullable=False)
    created     = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_equipment = relationship("UserEquipment", back_populates="equipment")


class UserEquipment(Base):
    __tablename__ = "user_equipment"

    id           = Column(Integer, primary_key=True)
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False)
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    equipment = relationship("Equipment", back_populates="user_equipment")
