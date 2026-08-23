from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Facility, Inspection, Inspector, RoleEnum
from ..schemas import InspectionCreate, InspectionOut, InspectionUpdate
from ..utils.audit import add_audit_log

router = APIRouter(prefix='/inspections', tags=['inspections'])

@router.get('/', response_model=list[InspectionOut])
def list_inspections(_: Inspector = Depends(get_current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Inspection).order_by(Inspection.date.desc())))

@router.post('/', response_model=InspectionOut, status_code=status.HTTP_201_CREATED)
def create_inspection(
    payload: InspectionCreate,
    request: Request,
    current_user: Inspector = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    facility = db.get(Facility, payload.facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail='Объект не найден')

    inspection = Inspection(
        facility_id=payload.facility_id,
        inspector_id=current_user.id,
        date=payload.date,
        result=payload.result,
        violations=payload.violations,
    )
    db.add(inspection)
    db.flush()

    add_audit_log(
        db,
        user_id=current_user.id,
        action='inspection_create',
        entity='inspection',
        entity_id=inspection.id,
        ip_address=request.client.host if request.client else None,
        payload={'facility_id': payload.facility_id, 'result': payload.result.value},
    )

    db.commit()
    db.refresh(inspection)
    return inspection

@router.put('/{inspection_id}', response_model=InspectionOut)
def update_inspection(
    inspection_id: int,
    payload: InspectionUpdate,
    request: Request,
    current_user: Inspector = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    inspection = db.get(Inspection, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail='Проверка не найдена')

    is_admin_or_senior = current_user.role in {RoleEnum.admin, RoleEnum.senior}
    if not is_admin_or_senior and inspection.inspector_id != current_user.id:
        raise HTTPException(status_code=403, detail='Недостаточно прав для редактирования проверки')

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(inspection, key, value)

    add_audit_log(
        db,
        user_id=current_user.id,
        action='inspection_update',
        entity='inspection',
        entity_id=inspection.id,
        ip_address=request.client.host if request.client else None,
        payload=update_data,
    )

    db.commit()
    db.refresh(inspection)
    return inspection

@router.delete('/{inspection_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_inspection(
    inspection_id: int,
    request: Request,
    current_user: Inspector = Depends(require_roles(RoleEnum.admin, RoleEnum.senior)),
    db: Session = Depends(get_db),
):
    inspection = db.get(Inspection, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail='Проверка не найдена')

    db.delete(inspection)
    add_audit_log(
        db,
        user_id=current_user.id,
        action='inspection_delete',
        entity='inspection',
        entity_id=inspection_id,
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return None
