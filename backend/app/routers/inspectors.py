from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Inspector, RoleEnum
from ..schemas import InspectorOut

router = APIRouter(prefix='/inspectors', tags=['inspectors'])

@router.get('/', response_model=list[InspectorOut])
def list_inspectors(_: Inspector = Depends(get_current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Inspector).order_by(Inspector.id.asc())))

@router.get('/admin-only', response_model=list[InspectorOut])
def list_inspectors_admin(_: Inspector = Depends(require_roles(RoleEnum.admin)), db: Session = Depends(get_db)):
    return list(db.scalars(select(Inspector).order_by(Inspector.id.asc())))
