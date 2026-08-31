from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Equipment, Facility
from ..schemas import EquipmentCreate, EquipmentOut, EquipmentUpdate

router = APIRouter(prefix='/equipment', tags=['equipment'])

@router.get('', response_model=list[EquipmentOut])
@router.get('/', response_model=list[EquipmentOut])
def list_equipment(db: Session = Depends(get_db)):
    return list(db.scalars(select(Equipment).order_by(Equipment.id.asc())))

@router.post('', response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
@router.post('/', response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
def create_equipment(payload: EquipmentCreate, db: Session = Depends(get_db)):
    facility = db.get(Facility, payload.facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail='Объект не найден')
    item = Equipment(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put('/{equipment_id}', response_model=EquipmentOut)
def update_equipment(equipment_id: int, payload: EquipmentUpdate, db: Session = Depends(get_db)):
    item = db.get(Equipment, equipment_id)
    if not item:
        raise HTTPException(status_code=404, detail='Оборудование не найдено')
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@router.delete('/{equipment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    item = db.get(Equipment, equipment_id)
    if item:
        db.delete(item)
        db.commit()
