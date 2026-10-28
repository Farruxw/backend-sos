"""Biznes mantiq: eng yaqin bo'sh brigadani tanlash, qayta biriktirish, yetib kelish vaqti."""
from math import asin, cos, radians, sin, sqrt

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import AVG_SPEED_KMH
from ..models import Call, Status, Unit, now


def km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Ikki nuqta orasidagi masofa (km) — Haversine formulasi."""
    r = 6371.0
    d_lat, d_lng = radians(lat2 - lat1), radians(lng2 - lng1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    return 2 * r * asin(sqrt(a))


def get_call(db: Session, call_id: int) -> Call:
    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(404, f"Chaqiruv topilmadi: {call_id}")
    return call


def get_unit(db: Session, call: Call) -> Unit | None:
    return db.get(Unit, call.unit_id) if call.unit_id else None


def _assign(db: Session, call: Call, exclude_unit_id: int | None = None) -> Call:
    service = ((call.services or "103").split(",")[0]).strip() or "103"
    free = db.scalars(select(Unit).where(Unit.service == service, Unit.busy.is_(False))).all()
    free = [u for u in free if u.id != exclude_unit_id]
    if not free:
        raise HTTPException(409, f"Bo'sh brigada yo'q: {service}")
    best = min(free, key=lambda u: km(call.lat, call.lng, u.lat, u.lng))
    best.busy = True
    call.unit_id = best.id
    call.status = Status.ENROUTE
    db.commit()
    return call


def _free_unit(db: Session, call: Call) -> None:
    unit = get_unit(db, call)
    if unit:
        unit.busy = False


def assign_nearest(db: Session, call_id: int) -> Call:
    """Xizmat bo'yicha eng yaqin bo'sh brigadani biriktiradi."""
    return _assign(db, get_call(db, call_id))


def reassign(db: Session, call_id: int) -> Call:
    """Brigada kechiksa: eskisini bo'shatib, keyingi eng yaqinini yuboradi."""
    call = get_call(db, call_id)
    old = call.unit_id
    _free_unit(db, call)
    return _assign(db, call, exclude_unit_id=old)   # xato bo'lsa, o'zgarish saqlanmaydi


def arrive(db: Session, call_id: int) -> Call:
    call = get_call(db, call_id)
    call.status = Status.ARRIVED
    call.arrived_at = now()
    db.commit()
    return call


def done(db: Session, call_id: int) -> Call:
    call = get_call(db, call_id)
    _free_unit(db, call)
    call.status = Status.DONE
    db.commit()
    return call


def cancel(db: Session, call_id: int) -> Call:
    call = get_call(db, call_id)
    _free_unit(db, call)
    call.status = Status.CANCELLED
    db.commit()
    return call


def eta_minutes(db: Session, call: Call) -> int:
    """Taxminiy yetib kelish vaqti (daqiqa). Brigada yo'q bo'lsa 0."""
    unit = get_unit(db, call)
    if unit is None:
        return 0
    return max(1, round(km(call.lat, call.lng, unit.lat, unit.lng) / AVG_SPEED_KMH * 60))
