import enum
from datetime import date, datetime
from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .database import Base

class RoleEnum(str, enum.Enum):
    admin = 'Администратор'
    senior = 'Старший инспектор'
    inspector = 'Инспектор'

class RiskLevelEnum(str, enum.Enum):
    high = 'Высокий'
    significant = 'Значительный'
    medium = 'Средний'
    moderate = 'Умеренный'
    low = 'Низкий'

class EquipmentStatusEnum(str, enum.Enum):
    active = 'Исправен'
    repair = 'Требует ремонта'
    written_off = 'Списан'
    inspecting = 'На проверке'

class InspectionResultEnum(str, enum.Enum):
    passed = 'Пройдена'
    failed = 'Не пройдена'

class Inspector(Base):
    __tablename__ = 'inspectors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rank: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, name='role_enum'), nullable=False, default=RoleEnum.inspector)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inspections: Mapped[list['Inspection']] = relationship(back_populates='inspector', cascade='all,delete-orphan')
    refresh_tokens: Mapped[list['RefreshToken']] = relationship(back_populates='inspector', cascade='all,delete-orphan')
    audit_logs: Mapped[list['AuditLog']] = relationship(back_populates='inspector')

class Facility(Base):
    __tablename__ = 'facilities'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    risk_level: Mapped[RiskLevelEnum] = mapped_column(Enum(RiskLevelEnum, name='risk_level_enum'), nullable=False)
    cadastral_number: Mapped[str | None] = mapped_column(String(100))
    responsible_person: Mapped[str | None] = mapped_column(String(255))

    equipment: Mapped[list['Equipment']] = relationship(back_populates='facility', cascade='all,delete-orphan')
    inspections: Mapped[list['Inspection']] = relationship(back_populates='facility', cascade='all,delete-orphan')

class Equipment(Base):
    __tablename__ = 'equipment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    facility_id: Mapped[int] = mapped_column(ForeignKey('facilities.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[EquipmentStatusEnum] = mapped_column(Enum(EquipmentStatusEnum, name='equipment_status_enum'), nullable=False)
    last_check_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_check_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    facility: Mapped['Facility'] = relationship(back_populates='equipment')

class Inspection(Base):
    __tablename__ = 'inspections'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    facility_id: Mapped[int] = mapped_column(ForeignKey('facilities.id', ondelete='CASCADE'), nullable=False, index=True)
    inspector_id: Mapped[int] = mapped_column(ForeignKey('inspectors.id', ondelete='RESTRICT'), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    result: Mapped[InspectionResultEnum] = mapped_column(Enum(InspectionResultEnum, name='inspection_result_enum'), nullable=False)
    violations: Mapped[str | None] = mapped_column(Text)
    prescription_number: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    facility: Mapped['Facility'] = relationship(back_populates='inspections')
    inspector: Mapped['Inspector'] = relationship(back_populates='inspections')

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    __table_args__ = (UniqueConstraint('token_hash', name='uq_refresh_token_hash'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspector_id: Mapped[int] = mapped_column(ForeignKey('inspectors.id', ondelete='CASCADE'), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_agent: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inspector: Mapped['Inspector'] = relationship(back_populates='refresh_tokens')

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('inspectors.id', ondelete='SET NULL'), index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inspector: Mapped[Inspector | None] = relationship(back_populates='audit_logs')
