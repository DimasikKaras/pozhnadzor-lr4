from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Facility, Inspection, Inspector
from ..schemas import InspectionCreate, InspectionOut, InspectionUpdate

router = APIRouter(prefix='/inspections', tags=['inspections'])

@router.get('', response_model=list[InspectionOut])
@router.get('/', response_model=list[InspectionOut])
def list_inspections(db: Session = Depends(get_db)):
    return list(db.scalars(select(Inspection).order_by(Inspection.date.desc())))

@router.post('', response_model=InspectionOut, status_code=status.HTTP_201_CREATED)
@router.post('/', response_model=InspectionOut, status_code=status.HTTP_201_CREATED)
def create_inspection(payload: InspectionCreate, db: Session = Depends(get_db)):
    facility = db.get(Facility, payload.facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail='Объект не найден')
    
    # Ищем инспектора или берем первого доступного
    inspector = db.scalar(select(Inspector))
    insp_id = inspector.id if inspector else 1

    item = Inspection(
        facility_id=payload.facility_id,
        inspector_id=insp_id,
        date=payload.date,
        result=payload.result,
        violations=payload.violations
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete('/{inspection_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_inspection(inspection_id: int, db: Session = Depends(get_db)):
    item = db.get(Inspection, inspection_id)
    if item:
        db.delete(item)
        db.commit()
