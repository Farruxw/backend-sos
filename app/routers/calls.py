"""/api/calls — SOS qabul qilish va chaqiruv hayot siklini boshqarish."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Call, Status
from ..schemas import CallDetail, CallOut, NewCall
from ..services import ai_triage, dispatch

router = APIRouter(prefix="/api/calls", tags=["calls"])


@router.post("", response_model=CallOut)
def create(body: NewCall, db: Session = Depends(get_db)):
    """SOS yuborish: AI saralaydi, chaqiruv NEW holatida saqlanadi."""
    r = ai_triage.triage(body.text)
    call = Call(full_name=body.full_name, phone=body.phone, address=body.address,
                lat=body.lat, lng=body.lng, accuracy=body.accuracy, text=body.text,
                services=r.services, severity=r.severity, ai_summary=r.summary)
    db.add(call)
    db.commit()
    return call


@router.get("/active", response_model=list[CallOut])
def active(db: Session = Depends(get_db)):
    """Operator uchun faol chaqiruvlar (NEW va ENROUTE), yangisi birinchi."""
    q = select(Call).where(Call.status.in_([Status.NEW, Status.ENROUTE])).order_by(Call.created_at.desc())
    return db.scalars(q).all()


@router.get("/{call_id}", response_model=CallDetail)
def get(call_id: int, db: Session = Depends(get_db)):
    """Chaqiruv holati, brigada va yetib kelish vaqti."""
    call = dispatch.get_call(db, call_id)
    return CallDetail(call=call, unit=dispatch.get_unit(db, call),
                      eta_minutes=dispatch.eta_minutes(db, call))


@router.post("/{call_id}/assign", response_model=CallOut)
def assign(call_id: int, db: Session = Depends(get_db)):
    return dispatch.assign_nearest(db, call_id)


@router.post("/{call_id}/reassign", response_model=CallOut)
def reassign(call_id: int, db: Session = Depends(get_db)):
    return dispatch.reassign(db, call_id)


@router.post("/{call_id}/arrive", response_model=CallOut)
def arrive(call_id: int, db: Session = Depends(get_db)):
    return dispatch.arrive(db, call_id)


@router.post("/{call_id}/done", response_model=CallOut)
def done(call_id: int, db: Session = Depends(get_db)):
    return dispatch.done(db, call_id)


@router.post("/{call_id}/cancel", response_model=CallOut)
def cancel(call_id: int, db: Session = Depends(get_db)):
    """Fuqaro chaqiruvni bekor qiladi."""
    return dispatch.cancel(db, call_id)
