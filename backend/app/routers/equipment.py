from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Equipment, Facility, Inspector, RoleEnum
from ..schemas import EquipmentCreate, EquipmentOut, EquipmentUpdate
from ..utils.audit import add_audit_log

router = APIRouter(prefix='/equipment', tags=['equipment'])

@router.get('/', response_model=list[EquipmentOut])
def list_equipment(_: Inspector = Depends(get_current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Equipment).order_by(Equipment.id.asc())))

@router.post('/', response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
def create_equipment(
    payload: EquipmentCreate,
    request: Request,
    current_user: Inspector = Depends(require_roles(RoleEnum.admin, RoleEnum.senior, RoleEnum.inspector)),
    db: Session = Depends(get_db),
):
    facility = db.get(Facility, payload.facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail='Указанный объект не найден')

    equipment = Equipment(**payload.model_dump())
    db.add(equipment)
    db.flush()
    add_audit_log(
        db,
        user_id=current_user.id,
        action='equipment_create',
        entity='equipment',
        entity_id=equipment.id,
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(equipment)
    return equipment

@router.put('/{equipment_id}', response_model=EquipmentOut)
def update_equipment(
    equipment_id: int,
    payload: EquipmentUpdate,
    request: Request,
    current_user: Inspector = Depends(require_roles(RoleEnum.admin, RoleEnum.senior, RoleEnum.inspector)),
    db: Session = Depends(get_db),
):
    equipment = db.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail='Оборудование не найдено')

    changes = payload.model_dump(exclude_unset=True)
    if 'facility_id' in changes and changes['facility_id'] is not None:
        facility = db.get(Facility, changes['facility_id'])
        if not facility:
            raise HTTPException(status_code=404, detail='Указанный объект не найден')

    for key, value in changes.items():
        setattr(equipment, key, value)

    add_audit_log(
        db,
        user_id=current_user.id,
        action='equipment_update',
        entity='equipment',
        entity_id=equipment.id,
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(equipment)
    return equipment

@router.delete('/{equipment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(
    equipment_id: int,
    request: Request,
    current_user: Inspector = Depends(require_roles(RoleEnum.admin, RoleEnum.senior)),
    db: Session = Depends(get_db),
):
    equipment = db.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail='Оборудование не найдено')

    add_audit_log(
        db,
        user_id=current_user.id,
        action='equipment_delete',
        entity='equipment',
        entity_id=equipment.id,
        ip_address=request.client.host if request.client else None,
    )
    db.delete(equipment)
    db.commit()
    return None
