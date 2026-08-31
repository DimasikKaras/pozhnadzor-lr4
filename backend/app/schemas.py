import re
from datetime import date as date_type
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from .models import EquipmentStatusEnum, InspectionResultEnum, RiskLevelEnum, RoleEnum

class TokenPairResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class InspectorBase(BaseModel):
    full_name: str
    rank: str
    phone: str | None = None
    email: EmailStr
    role: RoleEnum = RoleEnum.inspector

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        cleaned = v.strip()
        parts = cleaned.split()
        if len(parts) < 2:
            raise ValueError('Укажите как минимум Фамилию и Имя')
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', cleaned):
            raise ValueError('ФИО должно содержать только русские буквы и дефис')
        return cleaned

class InspectorRegister(InspectorBase):
    password: str = Field(min_length=8)
    admin_code: str | None = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Пароль должен быть не менее 8 символов')
        if not re.search(r'[A-ZА-ЯЁ]', v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r'[0-9]', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v

class InspectorOut(InspectorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class InspectionBase(BaseModel):
    facility_id: int
    date: date_type
    result: InspectionResultEnum
    violations: str | None = None

class InspectionCreate(InspectionBase):
    pass

class InspectionUpdate(BaseModel):
    date: date_type | None = None
    result: InspectionResultEnum | None = None
    violations: str | None = None

class InspectionOut(InspectionBase):
    id: int
    inspector_id: int
    model_config = ConfigDict(from_attributes=True)

class FacilityBase(BaseModel):
    name: str
    address: str
    risk_level: RiskLevelEnum
    cadastral_number: str | None = None
    responsible_person: str | None = None

class FacilityCreate(FacilityBase):
    pass

class FacilityUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    risk_level: RiskLevelEnum | None = None
    cadastral_number: str | None = None
    responsible_person: str | None = None

class FacilityOut(FacilityBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EquipmentBase(BaseModel):
    facility_id: int
    name: str | None = None
    type: str
    serial_number: str | None = None
    status: EquipmentStatusEnum = EquipmentStatusEnum.active
    last_check_date: date_type
    next_check_date: date_type | None = None

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    facility_id: int | None = None
    name: str | None = None
    type: str | None = None
    serial_number: str | None = None
    status: EquipmentStatusEnum | None = None
    last_check_date: date_type | None = None
    next_check_date: date_type | None = None

class EquipmentOut(EquipmentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
