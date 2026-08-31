from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Inspector, Inspection, RefreshToken, AuditLog, RoleEnum
from ..schemas import InspectorOut, InspectorRegister
from ..security import hash_password

router = APIRouter(prefix='/inspectors', tags=['inspectors'])

class DeleteRequest(BaseModel):
    id: Optional[int] = None
    email: Optional[str] = None

@router.get('', response_model=list[InspectorOut])
@router.get('/', response_model=list[InspectorOut])
def list_inspectors(db: Session = Depends(get_db)):
    return list(db.scalars(select(Inspector).order_by(Inspector.id.asc())))

@router.post('', response_model=InspectorOut, status_code=status.HTTP_201_CREATED)
@router.post('/', response_model=InspectorOut, status_code=status.HTTP_201_CREATED)
def create_inspector(payload: InspectorRegister, db: Session = Depends(get_db)):
    clean_email = payload.email.strip().lower()
    role = payload.role
    if role == RoleEnum.admin and payload.admin_code not in ['MCHS-ADMIN-2026', 'ADMIN2026', 'MCHS-SUPER-ADMIN']:
        raise HTTPException(status_code=403, detail='Неверный служебный код допуска для роли Администратора')

    existing = db.scalar(select(Inspector).where(Inspector.email == clean_email))
    if existing:
        existing.full_name = payload.full_name
        existing.rank = payload.rank
        existing.phone = payload.phone
        existing.role = role
        existing.password_hash = hash_password(payload.password)
        db.commit()
        db.refresh(existing)
        return existing

    user = Inspector(
        full_name=payload.full_name,
        rank=payload.rank,
        phone=payload.phone,
        email=clean_email,
        role=role,
        password_hash=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def _execute_full_delete(db: Session, item: Inspector):
    # Каскадно удаляем все связанные записи, чтобы PostgreSQL не ругался на RESTRICT
    db.execute(delete(RefreshToken).where(RefreshToken.inspector_id == item.id))
    db.execute(delete(AuditLog).where(AuditLog.user_id == item.id))
    db.execute(delete(Inspection).where(Inspection.inspector_id == item.id))
    db.delete(item)
    db.commit()
    return {'status': 'deleted', 'id': item.id, 'email': item.email}

@router.delete('/{inspector_id}')
@router.delete('/{inspector_id}/')
def delete_inspector_by_id(inspector_id: int, db: Session = Depends(get_db)):
    item = db.get(Inspector, inspector_id)
    if item:
        return _execute_full_delete(db, item)
    return {'status': 'not_found', 'id': inspector_id}

@router.delete('/by-email/{email}')
def delete_inspector_by_email(email: str, db: Session = Depends(get_db)):
    clean_email = email.strip().lower()
    item = db.scalar(select(Inspector).where(Inspector.email == clean_email))
    if item:
        return _execute_full_delete(db, item)
    return {'status': 'not_found', 'email': clean_email}

@router.post('/delete')
def delete_inspector_post(payload: DeleteRequest, db: Session = Depends(get_db)):
    conditions = []
    if payload.id:
        conditions.append(Inspector.id == payload.id)
    if payload.email:
        conditions.append(Inspector.email == payload.email.strip().lower())

    if not conditions:
        raise HTTPException(status_code=400, detail='Укажите id или email')

    item = db.scalar(select(Inspector).where(or_(*conditions)))
    if item:
        return _execute_full_delete(db, item)
    return {'status': 'not_found'}
