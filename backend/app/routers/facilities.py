from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Facility, Inspector, RoleEnum
from ..schemas import FacilityCreate, FacilityOut, FacilityUpdate
from ..utils.audit import add_audit_log

router = APIRouter(prefix='/facilities', tags=['facilities'])

@router.get('/', response_model=list[FacilityOut])
def list_facilities(_: Inspector = Depends(get_current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Facility).order_by(Facility.id.asc())))

@router.post('/', response_model=FacilityOut, status_code=status.HTTP_201_CREATED)
def create_facility(
    payload: FacilityCreate,
    request: Request,
    current_user: Inspector = Depends(require_roles(RoleEnum.admin, RoleEnum.senior)),
    db: Session = Depends(get_db),
):
    facility = Facility(**payload.model_dump())
    db.add(facility)
    db.flush()
    add_audit_log(
        db,
        user_id=current_user.id,
        action='facility_create',
        entity='facility',
        entity_id=facility.id,
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(facility)
    return facility

@router.put('/{facility_id}', response_model=FacilityOut)
def update_facility(
    facility_id: int,
    payload: FacilityUpdate,
    request: Request,
    current_user: Inspector = Depends(require_roles(RoleEnum.admin, RoleEnum.senior)),
    db: Session = Depends(get_db),
):
    facility = db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail='Объект не найден')

    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(facility, key, value)

    add_audit_log(
        db,
        user_id=current_user.id,
        action='facility_update',
        entity='facility',
        entity_id=facility.id,
        ip_address=request.client.host if request.client else None,
        payload=changes,
    )
    db.commit()
    db.refresh(facility)
    return facility

@router.delete('/{facility_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_facility(
    facility_id: int,
    request: Request,
    current_user: Inspector = Depends(require_roles(RoleEnum.admin, RoleEnum.senior)),
    db: Session = Depends(get_db),
):
    facility = db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail='Объект не найден')

    add_audit_log(
        db,
        user_id=current_user.id,
        action='facility_delete',
        entity='facility',
        entity_id=facility.id,
        ip_address=request.client.host if request.client else None,
    )
    db.delete(facility)
    db.commit()
    return None
