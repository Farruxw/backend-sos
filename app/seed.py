"""Baza bo'sh bo'lsa, namunaviy brigadalarni qo'shadi (ismlar va raqamlar o'ylab topilgan)."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Unit

UNITS = [
    ("FVV 4-qism", "101", 41.3050, 69.2500, "Brigadir: Jasur Akbarov; O't o'chiruvchi: Sardor Aliyev; Haydovchi: Akmal Nazarov", "01 B 101 AA"),
    ("FVV 9-qism", "101", 41.2750, 69.2000, "Brigadir: Rustam Karimov; O't o'chiruvchi: Otabek Ergashev; Haydovchi: Sherzod Umarov", "01 B 102 AA"),
    ("Patrul PM-12", "102", 41.3000, 69.2450, "Inspektor: Bekzod Rahmonov; Haydovchi: Dilshod Saidov", "01 P 102 PM"),
    ("Patrul PM-5", "102", 41.3200, 69.2800, "Inspektor: Aziz Hamidov; Haydovchi: Javlon Tursunov", "01 P 105 PM"),
    ("Tez yordam 3-brigada", "103", 41.2990, 69.2480, "Brigadir: Abdulla Qosimov; Shifokor: Dilshod Karimov; Feldsher: Malika Yusupova; Haydovchi: Bobur Rahimov", "01 A 103 AB"),
    ("Tez yordam 7-brigada", "103", 41.3300, 69.2700, "Brigadir: Nodira Hasanova; Shifokor: Anvar Mirzaev; Haydovchi: Ulug'bek Sodiqov", "01 A 107 AB"),
    ("Gaz brigadasi 1", "104", 41.3100, 69.2300, "Brigadir: Farhod Yo'ldoshev; Usta: Qodir Ismoilov; Haydovchi: Ravshan Aminov", "01 G 104 AA"),
    ("Gaz brigadasi 2", "104", 41.2800, 69.2600, "Brigadir: Murod Abdullaev; Usta: Hasan Olimov; Haydovchi: Timur Qurbonov", "01 G 105 AA"),
]


def seed_units(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Unit)):
        return
    for name, service, lat, lng, crew, plate in UNITS:
        db.add(Unit(name=name, service=service, lat=lat, lng=lng, busy=False, crew=crew, plate=plate))
    db.commit()
