"""/api/chat/{specialty} — mutaxassis chati (javoblarni AI beradi, haqiqiy shifokor emas)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ChatMessage
from ..schemas import ChatIn, ChatOut
from ..services import ai_triage

router = APIRouter(prefix="/api/chat/{specialty}", tags=["chat"])


@router.get("", response_model=list[ChatOut])
def history(specialty: str, db: Session = Depends(get_db)):
    """Chat tarixi: oxirgi 50 xabar, eskisidan yangisiga."""
    q = (select(ChatMessage).where(ChatMessage.specialty == specialty)
         .order_by(ChatMessage.id.desc()).limit(50))
    return list(reversed(db.scalars(q).all()))


@router.post("", response_model=ChatOut)
def send(specialty: str, body: ChatIn, db: Session = Depends(get_db)):
    """Bemor xabarini saqlaydi, AI javobini saqlab qaytaradi."""
    db.add(ChatMessage(specialty=specialty, sender="PATIENT", text=body.text))
    reply = ChatMessage(specialty=specialty, sender="AI",
                        text=ai_triage.chat_reply(specialty, body.text))
    db.add(reply)
    db.commit()
    return reply
