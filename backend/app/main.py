from datetime import date
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, SessionLocal, engine
from .models import (
    Equipment,
    EquipmentStatusEnum,
    Facility,
    Inspection,
    InspectionResultEnum,
    Inspector,
    RiskLevelEnum,
    RoleEnum,
)
from .routers import auth, equipment, facilities, inspections, inspectors, users
from .security import hash_password

app = FastAPI(
    title='ПожНадзор.pro API',
    description='Информационная система Государственного пожарного надзора МЧС России',
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(inspectors.router)
app.include_router(facilities.router)
app.include_router(equipment.router)
app.include_router(inspections.router)

def seed_initial_data(db: Session):
    if db.scalar(select(Inspector)):
        return

    admin_user = Inspector(
        full_name='Иванов Петр Сергеевич',
        rank='Капитан внутренней службы',
        phone='+7 (999) 123-45-67',
        email='ivanov@mchs.gov.ru',
        role=RoleEnum.admin,
        password_hash=hash_password('password123'),
    )
    senior_user = Inspector(
        full_name='Смирнова Елена Александровна',
        rank='Майор внутренней службы',
        phone='+7 (999) 234-56-78',
        email='smirnova@mchs.gov.ru',
        role=RoleEnum.senior,
        password_hash=hash_password('password123'),
    )
    inspector_user = Inspector(
        full_name='Кузнецов Дмитрий Олегович',
        rank='Лейтенант внутренней службы',
        phone='+7 (999) 345-67-89',
        email='kuznetsov@mchs.gov.ru',
        role=RoleEnum.inspector,
        password_hash=hash_password('password123'),
    )
    db.add_all([admin_user, senior_user, inspector_user])
    db.flush()

    f1 = Facility(
        name='ТРЦ «Галактика»',
        address='г. Москва, пр-т Мира, д. 112',
        risk_level=RiskLevelEnum.high,
        cadastral_number='77:01:0001001:1024',
        responsible_person='Соколов В.В.',
    )
    f2 = Facility(
        name='ГБОУ СОШ № 1502',
        address='г. Москва, ул. Молостовых, д. 10А',
        risk_level=RiskLevelEnum.significant,
        cadastral_number='77:03:0002005:4012',
        responsible_person='Михайлова О.Н.',
    )
    f3 = Facility(
        name='Складской комплекс «Северный»',
        address='г. Москва, Дмитровское ш., д. 157',
        risk_level=RiskLevelEnum.medium,
        cadastral_number='77:09:0004010:8831',
        responsible_person='Григорьев А.И.',
    )
    f4 = Facility(
        name='БЦ «Арма»',
        address='г. Москва, Нижний Сусальный пер., д. 5',
        risk_level=RiskLevelEnum.moderate,
        cadastral_number='77:01:0001045:1902',
        responsible_person='Романов С.Д.',
    )
    db.add_all([f1, f2, f3, f4])
    db.flush()

    eq1 = Equipment(
        facility_id=f1.id,
        name='Огнетушитель порошковый ОП-5',
        type='ОП-5',
        serial_number='SN-9941-A',
        status=EquipmentStatusEnum.active,
        last_check_date=date(2025, 1, 15),
    )
    eq2 = Equipment(
        facility_id=f1.id,
        name='Пожарный кран ПК-2',
        type='ПК-2',
        serial_number='SN-1049-C',
        status=EquipmentStatusEnum.repair,
        last_check_date=date(2024, 11, 20),
    )
    eq3 = Equipment(
        facility_id=f2.id,
        name='Огнетушитель углекислотный ОУ-3',
        type='ОУ-3',
        serial_number='SN-5520-E',
        status=EquipmentStatusEnum.active,
        last_check_date=date(2025, 2, 1),
    )
    eq4 = Equipment(
        facility_id=f3.id,
        name='Мотопомпа МП-800',
        type='МП-800',
        serial_number='SN-0094-X',
        status=EquipmentStatusEnum.inspecting,
        last_check_date=date(2024, 12, 10),
    )
    db.add_all([eq1, eq2, eq3, eq4])
    db.flush()

    insp1 = Inspection(
        facility_id=f1.id,
        inspector_id=admin_user.id,
        date=date(2025, 2, 10),
        result=InspectionResultEnum.failed,
        violations='Загромождение путей эвакуации на 3 этаже, неисправность пожарного крана ПК-2.',
    )
    insp2 = Inspection(
        facility_id=f2.id,
        inspector_id=senior_user.id,
        date=date(2025, 1, 22),
        result=InspectionResultEnum.passed,
        violations=None,
    )
    insp3 = Inspection(
        facility_id=f3.id,
        inspector_id=inspector_user.id,
        date=date(2024, 12, 15),
        result=InspectionResultEnum.passed,
        violations=None,
    )
    db.add_all([insp1, insp2, insp3])
    db.commit()

@app.on_event('startup')
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            seed_initial_data(db)
    except Exception as e:
        print(f'Database startup warning: {e}')

@app.get('/health')
def health_check():
    return {'status': 'ok', 'app': 'ПожНадзор.pro'}
